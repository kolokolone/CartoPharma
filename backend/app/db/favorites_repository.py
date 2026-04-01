from __future__ import annotations

from app.db.database import connect, init_database, utc_now_iso
from app.models.schemas import FavoriteStatusResponse


def is_pharmacy_favorite(establishment_id: str) -> bool:
    init_database()

    with connect() as connection:
        row = connection.execute(
            "SELECT 1 FROM favorite_pharmacy WHERE establishment_id = ?",
            (establishment_id,),
        ).fetchone()

    return row is not None


def get_favorite_pharmacy_status(establishment_id: str) -> FavoriteStatusResponse:
    return FavoriteStatusResponse(
        establishment_id=establishment_id,
        is_favorite=is_pharmacy_favorite(establishment_id),
    )


def put_favorite_pharmacy(establishment_id: str) -> FavoriteStatusResponse:
    init_database()

    with connect() as connection:
        connection.execute(
            """
            INSERT INTO favorite_pharmacy (establishment_id, created_at_utc)
            VALUES (?, ?)
            ON CONFLICT(establishment_id) DO NOTHING
            """,
            (establishment_id, utc_now_iso()),
        )
        connection.commit()

    return FavoriteStatusResponse(establishment_id=establishment_id, is_favorite=True)


def delete_favorite_pharmacy(establishment_id: str) -> FavoriteStatusResponse:
    init_database()

    with connect() as connection:
        connection.execute(
            "DELETE FROM favorite_pharmacy WHERE establishment_id = ?",
            (establishment_id,),
        )
        connection.commit()

    return FavoriteStatusResponse(establishment_id=establishment_id, is_favorite=False)
