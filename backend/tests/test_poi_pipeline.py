from __future__ import annotations

import asyncio
from contextlib import closing
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

from fastapi import HTTPException

from app.api.routes.indexing import rebuild_poi_route
from app.api.routes.layers import get_layer_points
from app.api.routes.pharmacies import get_pharmacy_detail_route
from app.db.database import utc_now_iso
from app.db.poi_database import connect_poi, init_poi_database
from app.db.poi_repository import PoiBoundingBox, list_poi_layers, list_poi_points
from app.services.poi_geocoding import synchronize_geocode_statuses
from app.services.poi_rebuild import rebuild_poi_database


def write_utf16le_csv(path: Path, content: str) -> None:
    path.write_bytes(content.replace("\n", "\r\n").encode("utf-16-le"))


class PoiPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self.temp_dir.cleanup)
        self.data_dir = Path(self.temp_dir.name)
        os.environ["CARTOPHARMA_DATA_DIR"] = str(self.data_dir)
        self.addCleanup(lambda: os.environ.pop("CARTOPHARMA_DATA_DIR", None))
        csv_dir = self.data_dir / "csv"
        csv_dir.mkdir(parents=True, exist_ok=True)
        (csv_dir / "pharmacies.csv").write_text("legacy file that must be ignored\n", encoding="utf-8")
        (csv_dir / "shops.csv").write_text(
            "source_record_id,name,address_line_1,postal_code,city,latitude,longitude\n"
            "shop-1,Commerce Test,5 place du Marche,33000,Bordeaux,44.8378,-0.5792\n",
            encoding="utf-8",
        )

        pharmacy_dir = csv_dir / "pharmacies"
        pharmacy_dir.mkdir(parents=True, exist_ok=True)
        write_utf16le_csv(
            pharmacy_dir / "etablissements_2026-03-30_03-31-31.csv",
            "Numéro d'établissement;Type établissement;Dénomination commerciale;Raison sociale;Adresse;Code postal;Commune;Département;Région;Téléphone;Fax;Latitude;Longitude;Site web;Horaires;Siret\n"
            "ETAB-001;Officine;Pharmacie du Centre;Pharmacie du Centre SARL;1 rue de Paris;75001;Paris;75;Ile-de-France;0102030405;0102030406;48.8566;2.3522;https://example.org/pharm1;Mo-Sa 09:00-19:00;11111111111111\n"
            "ETAB-002;Officine;Pharmacie du Nord;Pharmacie du Nord SARL;2 place du Theatre;59000;Lille;59;Hauts-de-France;0203040506;0203040507;50.6292;3.0573;https://example.org/pharm2;Mo-Sa 08:30-19:30;22222222222222\n",
        )
        write_utf16le_csv(
            pharmacy_dir / "pharmaciens_2026-03-30_03-31-31.csv",
            "n° RPPS;Titre;Nom d'exercice;Prénom;Date de première inscription\n"
            "RPPS-001;Dr;Martin;Alice;2015-01-01\n"
            "RPPS-002;Dr;Durand;Bruno;2016-06-15\n"
            "RPPS-003;Dr;Petit;Claire;2018-09-20\n",
        )
        write_utf16le_csv(
            pharmacy_dir / "activites_2026-03-30_03-31-31.csv",
            "n° RPPS pharmacien;Numéro d'établissement;Fonction;Date d'inscription;Section;Activité principale\n"
            "RPPS-001;ETAB-001;Titulaire;2020-01-01;A;Oui\n"
            "RPPS-002;ETAB-001;Adjoint;2021-02-01;A;Non\n"
            "RPPS-002;ETAB-002;Titulaire;2022-03-01;B;Oui\n"
            "RPPS-003;ETAB-002;Adjoint;2023-04-01;B;Non\n",
        )
        write_utf16le_csv(
            pharmacy_dir / "diplomes_2026-03-30_03-31-31.csv",
            "n° RPPS pharmacien;Diplôme;Date d'obtention;Université;Region\n"
            "RPPS-001;Doctorat pharmacie;2014-01-01;Paris Cité;Ile-de-France\n"
            "RPPS-002;Doctorat pharmacie;2015-01-01;Lille;Hauts-de-France\n"
            "RPPS-003;DU Orthopedie;2019-01-01;Lille;Hauts-de-France\n",
        )

    def test_rebuilds_catalog_with_specialized_pharmacy_directory(self) -> None:
        init_poi_database()
        report = rebuild_poi_database()

        self.assertTrue(report.used_specialized_pharmacy_directory)
        self.assertEqual(report.pharmacy_files_detected, 4)
        self.assertEqual(report.generic_files_processed, 1)
        self.assertEqual(report.pharmacies_imported, 2)
        self.assertEqual(report.pharmacists_imported, 3)
        self.assertEqual(report.activities_imported, 4)
        self.assertEqual(report.degrees_imported, 3)
        self.assertEqual(report.rows_rejected, 0)
        self.assertEqual(report.geocoded_resolved, 3)

        layers = list_poi_layers()
        self.assertEqual([layer["id"] for layer in layers], ["pharmacies", "shops"])

        all_points = list_poi_points(layers=["pharmacies"])
        self.assertEqual(len(all_points), 2)
        self.assertEqual(all_points[0]["pharmacist_count"], 2)
        self.assertIsNotNone(all_points[0]["pharmacy_establishment_id"])

        bbox_points = list_poi_points(
            layers=["pharmacies"],
            bbox=PoiBoundingBox(min_lon=2.0, min_lat=48.0, max_lon=2.5, max_lat=49.0),
        )
        self.assertEqual(len(bbox_points), 1)
        self.assertEqual(bbox_points[0]["city"], "Paris")

        with closing(connect_poi()) as connection:
            indexed = connection.execute("SELECT COUNT(*) AS count FROM poi_rtree").fetchone()["count"]
        self.assertEqual(indexed, 3)

    def test_routes_expose_enriched_pharmacy_payloads(self) -> None:
        init_poi_database()
        rebuild_poi_database()

        response = asyncio.run(get_layer_points(layers=['pharmacies'], bbox='2.0,48.0,2.5,49.0'))
        self.assertEqual(len(response.features), 1)
        self.assertEqual(response.features[0].properties.city, 'Paris')
        self.assertEqual(response.features[0].properties.pharmacist_count, 2)
        self.assertEqual(response.features[0].properties.pharmacy_establishment_id, 'ETAB-001')

        with self.assertRaises(HTTPException) as context:
            asyncio.run(get_layer_points(layers=['pharmacies'], bbox='oops'))
        self.assertEqual(context.exception.status_code, 422)

        detail = asyncio.run(get_pharmacy_detail_route('ETAB-001'))
        self.assertEqual(detail.display_name, 'Pharmacie du Centre')
        self.assertEqual(detail.pharmacist_count, 2)
        self.assertEqual(len(detail.pharmacists), 2)
        self.assertEqual(detail.pharmacists[0].activities[0].function_label, 'Adjoint')

    def test_rebuild_endpoint_returns_structured_report(self) -> None:
        init_poi_database()

        response = asyncio.run(rebuild_poi_route())

        self.assertEqual(response.status, 'success')
        self.assertEqual(response.pharmacy_files_detected, 4)
        self.assertEqual(response.pharmacies_imported, 2)
        self.assertEqual(response.poi_rows_rebuilt, 3)

    def test_legacy_root_pharmacies_csv_is_ignored(self) -> None:
        init_poi_database()

        report = rebuild_poi_database()

        self.assertEqual(report.generic_files_processed, 1)
        layers = list_poi_layers()
        self.assertEqual([layer['id'] for layer in layers], ['pharmacies', 'shops'])

    def test_rebuild_removes_stale_layers_when_csv_disappears(self) -> None:
        init_poi_database()
        first_report = rebuild_poi_database()
        self.assertEqual(first_report.poi_rows_rebuilt, 3)

        (self.data_dir / 'csv' / 'shops.csv').unlink()

        second_report = rebuild_poi_database()

        self.assertEqual(second_report.generic_files_processed, 0)
        layers = list_poi_layers()
        self.assertEqual([layer['id'] for layer in layers], ['pharmacies'])
        all_points = list_poi_points(layers=['pharmacies'])
        self.assertEqual(len(all_points), 2)

    @patch('app.services.poi_geocoding.requests.post')
    def test_batch_geocoding_resolves_pending_points(self, requests_post: Mock) -> None:
        init_poi_database()
        timestamp = utc_now_iso()

        with closing(connect_poi()) as connection:
            connection.execute(
                """
                INSERT INTO poi_layer (id, label, category, priority, color, visible_by_default, is_active, source_status, updated_at_utc)
                VALUES ('pharmacies', 'Pharmacies', 'Sante', 1, '#15803d', 1, 1, 'imported', ?)
                """,
                (timestamp,),
            )
            cursor = connection.execute(
                """
                INSERT INTO poi (
                    source_name, source_record_id, layer_id, name, display_name, address_line_1, postal_code, city,
                    department_code, region, country_code, phone, website, opening_hours, pharmacy_establishment_id,
                    pharmacist_count, pharmacy_type, latitude, longitude, geocode_status, geocode_score,
                    geocode_provider, raw_address, normalized_address, is_active, last_seen_at_utc, created_at_utc, updated_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
                """,
                (
                    'pharmacy_directory',
                    'ETAB-XYZ',
                    'pharmacies',
                    'Pharmacie Test',
                    'Pharmacie Test',
                    '37 BIS RUE DE PENTHIEVRE',
                    '22120',
                    'YFFINIAC',
                    "COTES D'ARMOR",
                    'REGION BRETAGNE',
                    'FR',
                    '0296726692',
                    None,
                    None,
                    'ETAB-XYZ',
                    3,
                    'OFFICINE',
                    None,
                    None,
                    'pending',
                    None,
                    None,
                    '37 BIS RUE DE PENTHIEVRE, 22120 YFFINIAC',
                    '37 BIS RUE DE PENTHIEVRE, 22120 YFFINIAC',
                    timestamp,
                    timestamp,
                    timestamp,
                ),
            )
            poi_id = cursor.lastrowid
            connection.commit()

        requests_post.return_value = Mock(
            status_code=200,
            text=(
                'poi_id,address_line_1,postal_code,city,longitude,latitude,result_score,result_status\n'
                f'{poi_id},37 BIS RUE DE PENTHIEVRE,22120,YFFINIAC,-2.673841,48.481279,0.8476,ok\n'
            ),
        )
        requests_post.return_value.raise_for_status = Mock()

        report = synchronize_geocode_statuses()

        self.assertEqual(report['resolved'], 1)
        self.assertEqual(report['pending'], 0)
        self.assertEqual(report['indexed_rows'], 1)

        with closing(connect_poi()) as connection:
            row = connection.execute(
                "SELECT latitude, longitude, geocode_status, geocode_provider FROM poi WHERE id = ?",
                (poi_id,),
            ).fetchone()

        self.assertAlmostEqual(row['latitude'], 48.481279)
        self.assertAlmostEqual(row['longitude'], -2.673841)
        self.assertEqual(row['geocode_status'], 'resolved')
        self.assertEqual(row['geocode_provider'], 'geoplateforme_search_csv')


if __name__ == "__main__":
    unittest.main()
