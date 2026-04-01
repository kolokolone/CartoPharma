from __future__ import annotations

from contextlib import closing
from pathlib import Path

from app.db.favorites_repository import is_pharmacy_favorite
from app.db.poi_repository import list_poi_nearby_pharmacy
from app.db.poi_database import connect_poi
from app.models.schemas import (
    PharmacyNearbyPoiItemResponse,
    PharmacyNearbyPoiResponse,
    PharmacistDetailResponse,
    PharmacyActivityResponse,
    PharmacyDegreeResponse,
    PharmacyDetailResponse,
)


def get_pharmacy_details(establishment_id: str, database_path: Path | None = None) -> PharmacyDetailResponse | None:
    with closing(connect_poi(database_path)) as connection:
        establishment = connection.execute(
            """
            SELECT establishment_id, establishment_type, display_name, legal_name, address_line_1,
                   postal_code, city, department, region, phone, fax
            FROM pharmacy_establishment
            WHERE establishment_id = ?
            """,
            (establishment_id,),
        ).fetchone()
        if establishment is None:
            return None

        pharmacist_count = connection.execute(
            """
            SELECT COUNT(DISTINCT rpps) AS count
            FROM pharmacist_activity
            WHERE establishment_id = ?
            """,
            (establishment_id,),
        ).fetchone()["count"]

        pharmacist_rows = connection.execute(
            """
            SELECT DISTINCT pharmacist.rpps, pharmacist.title, pharmacist.last_name, pharmacist.first_name, pharmacist.first_registration_date
            FROM pharmacist
            INNER JOIN pharmacist_activity ON pharmacist_activity.rpps = pharmacist.rpps
            WHERE pharmacist_activity.establishment_id = ?
            ORDER BY pharmacist.last_name ASC, pharmacist.first_name ASC, pharmacist.rpps ASC
            """,
            (establishment_id,),
        ).fetchall()

        activity_rows = connection.execute(
            """
            SELECT rpps, function_label, registration_date, section_code, is_primary_activity
            FROM pharmacist_activity
            WHERE establishment_id = ?
            ORDER BY is_primary_activity DESC, function_label ASC, registration_date ASC
            """,
            (establishment_id,),
        ).fetchall()

        degree_rows = connection.execute(
            """
            SELECT rpps, degree_label, degree_date, university, region
            FROM pharmacist_degree
            WHERE rpps IN (
                SELECT DISTINCT rpps
                FROM pharmacist_activity
                WHERE establishment_id = ?
            )
            ORDER BY degree_date ASC, degree_label ASC
            """,
            (establishment_id,),
        ).fetchall()

        poi_row = connection.execute(
            """
            SELECT website, opening_hours, siret, latitude, longitude, updated_at_utc
            FROM poi
            WHERE pharmacy_establishment_id = ?
              AND is_active = 1
            ORDER BY updated_at_utc DESC
            LIMIT 1
            """,
            (establishment_id,),
        ).fetchone()

    pharmacists: dict[str, PharmacistDetailResponse] = {
        row["rpps"]: PharmacistDetailResponse(
            rpps=row["rpps"],
            title=row["title"],
            last_name=row["last_name"],
            first_name=row["first_name"],
            first_registration_date=row["first_registration_date"],
            activities=[],
            degrees=[],
        )
        for row in pharmacist_rows
    }

    for row in activity_rows:
        pharmacist = pharmacists.get(row["rpps"])
        if pharmacist is None:
            continue
        pharmacist.activities.append(
            PharmacyActivityResponse(
                function_label=row["function_label"],
                registration_date=row["registration_date"],
                section_code=row["section_code"],
                is_primary_activity=bool(row["is_primary_activity"]),
            )
        )

    for row in degree_rows:
        pharmacist = pharmacists.get(row["rpps"])
        if pharmacist is None:
            continue
        pharmacist.degrees.append(
            PharmacyDegreeResponse(
                degree_label=row["degree_label"],
                degree_date=row["degree_date"],
                university=row["university"],
                region=row["region"],
            )
        )

    return PharmacyDetailResponse(
        establishment_id=establishment["establishment_id"],
        establishment_type=establishment["establishment_type"],
        display_name=establishment["display_name"],
        legal_name=establishment["legal_name"],
        address_line_1=establishment["address_line_1"],
        postal_code=establishment["postal_code"],
        city=establishment["city"],
        department=establishment["department"],
        region=establishment["region"],
        phone=establishment["phone"],
        fax=establishment["fax"],
        website=poi_row["website"] if poi_row is not None else None,
        opening_hours=poi_row["opening_hours"] if poi_row is not None else None,
        siret=poi_row["siret"] if poi_row is not None else None,
        latitude=float(poi_row["latitude"]) if poi_row is not None and poi_row["latitude"] is not None else None,
        longitude=float(poi_row["longitude"]) if poi_row is not None and poi_row["longitude"] is not None else None,
        last_updated_at=poi_row["updated_at_utc"] if poi_row is not None else None,
        is_favorite=is_pharmacy_favorite(establishment_id),
        pharmacist_count=int(pharmacist_count),
        pharmacists=list(pharmacists.values()),
    )


def get_pharmacy_nearby_poi(
    establishment_id: str,
    *,
    radius_m: int = 1000,
    database_path: Path | None = None,
) -> PharmacyNearbyPoiResponse | None:
    pharmacy = get_pharmacy_details(establishment_id, database_path=database_path)
    if pharmacy is None:
        return None

    if pharmacy.latitude is None or pharmacy.longitude is None:
        return PharmacyNearbyPoiResponse(
            establishment_id=establishment_id,
            radius_m=radius_m,
            total_count=0,
            items=[],
        )

    items = [
        PharmacyNearbyPoiItemResponse(
            id=str(row["id"]),
            label=str(row["label"]),
            secondary_label=row["secondary_label"] if isinstance(row["secondary_label"], str) else None,
            layer_id=str(row["layer_id"]),
            layer_label=str(row["layer_label"]),
            category=str(row["category"]),
            city=row["city"] if isinstance(row["city"], str) else None,
            distance_m=row["distance_m"] if isinstance(row["distance_m"], int) else 0,
            latitude=float(row["latitude"]) if isinstance(row["latitude"], (int, float)) else 0.0,
            longitude=float(row["longitude"]) if isinstance(row["longitude"], (int, float)) else 0.0,
            target_href=str(row["target_href"]),
            pharmacy_establishment_id=(
                row["pharmacy_establishment_id"]
                if isinstance(row["pharmacy_establishment_id"], str)
                else None
            ),
        )
        for row in list_poi_nearby_pharmacy(
            establishment_id,
            radius_m=radius_m,
            database_path=database_path,
        )
    ]
    return PharmacyNearbyPoiResponse(
        establishment_id=establishment_id,
        radius_m=radius_m,
        total_count=len(items),
        items=items,
    )
