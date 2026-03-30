from __future__ import annotations

from app.db.database import connect, utc_now_iso
from app.models.schemas import SettingsPatchRequest, SettingsResponse


def get_settings() -> SettingsResponse:
    with connect() as connection:
        row = connection.execute(
            "SELECT theme, show_labels, compact_controls FROM app_settings WHERE id = 1"
        ).fetchone()

    if row is None:
        return SettingsResponse()

    return SettingsResponse(
        theme=row["theme"],
        show_labels=bool(row["show_labels"]),
        compact_controls=bool(row["compact_controls"]),
    )


def update_settings(payload: SettingsPatchRequest) -> SettingsResponse:
    current = get_settings()
    patch = payload.model_dump(exclude_unset=True)

    updated = current.model_copy(update=patch)

    with connect() as connection:
        connection.execute(
            """
            UPDATE app_settings
            SET theme = ?, show_labels = ?, compact_controls = ?, updated_at_utc = ?
            WHERE id = 1
            """,
            (
                updated.theme,
                int(updated.show_labels),
                int(updated.compact_controls),
                utc_now_iso(),
            ),
        )
        connection.commit()

    return updated
