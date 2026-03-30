from __future__ import annotations

from contextlib import closing
from pathlib import Path

from app.db.poi_database import connect_poi
from app.models.schemas import (
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
        pharmacist_count=int(pharmacist_count),
        pharmacists=list(pharmacists.values()),
    )
