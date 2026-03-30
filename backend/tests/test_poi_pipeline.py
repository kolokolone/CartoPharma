from __future__ import annotations

import asyncio
from contextlib import closing
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fastapi import HTTPException

from app.api.routes.layers import get_layer_points
from app.db.poi_database import connect_poi, init_poi_database
from app.db.poi_repository import PoiBoundingBox, list_poi_layers, list_poi_points
from app.services.poi_geocoding import synchronize_geocode_statuses
from app.services.poi_import import import_csv_directory


class PoiPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.data_dir = Path(self.temp_dir.name)
        os.environ["CARTOPHARMA_DATA_DIR"] = str(self.data_dir)
        self.addCleanup(lambda: os.environ.pop("CARTOPHARMA_DATA_DIR", None))
        csv_dir = self.data_dir / "csv"
        csv_dir.mkdir(parents=True, exist_ok=True)
        (csv_dir / "pharmacies.csv").write_text(
            "source_record_id,name,address_line_1,postal_code,city,latitude,longitude,phone\n"
            "pharm-1,Pharmacie Test,1 rue de Paris,75001,Paris,48.8566,2.3522,0102030405\n"
            "pharm-2,Pharmacie Lille,2 place du Theatre,59000,Lille,50.6292,3.0573,0203040506\n",
            encoding="utf-8",
        )

    def test_builds_catalog_and_bbox_filtered_points(self) -> None:
        init_poi_database()
        summary = import_csv_directory()
        geocode_report = synchronize_geocode_statuses()

        self.assertEqual(summary.files_processed, 1)
        self.assertEqual(summary.rows_imported, 2)
        self.assertEqual(summary.rows_rejected, 0)
        self.assertEqual(geocode_report["resolved"], 2)

        layers = list_poi_layers()
        self.assertEqual(len(layers), 1)
        self.assertEqual(layers[0]["id"], "pharmacies")

        all_points = list_poi_points(layers=["pharmacies"])
        self.assertEqual(len(all_points), 2)

        bbox_points = list_poi_points(
            layers=["pharmacies"],
            bbox=PoiBoundingBox(min_lon=2.0, min_lat=48.0, max_lon=2.5, max_lat=49.0),
        )
        self.assertEqual(len(bbox_points), 1)
        self.assertEqual(bbox_points[0]["city"], "Paris")

        with closing(connect_poi()) as connection:
            indexed = connection.execute("SELECT COUNT(*) AS count FROM poi_rtree").fetchone()["count"]
        self.assertEqual(indexed, 2)

    def test_layers_points_route_validates_bbox_and_filters_results(self) -> None:
        init_poi_database()
        import_csv_directory()
        synchronize_geocode_statuses()

        response = asyncio.run(get_layer_points(layers=['pharmacies'], bbox='2.0,48.0,2.5,49.0'))
        self.assertEqual(len(response.features), 1)
        self.assertEqual(response.features[0].properties.city, 'Paris')

        with self.assertRaises(HTTPException) as context:
            asyncio.run(get_layer_points(layers=['pharmacies'], bbox='oops'))
        self.assertEqual(context.exception.status_code, 422)


if __name__ == "__main__":
    unittest.main()
