from __future__ import annotations

from contextlib import closing
import re
import unicodedata
from typing import Literal

from app.db.poi_database import connect_poi
from app.models.schemas import SearchResponse, SearchResultResponse


SearchKind = Literal['suggestions', 'results']


def search_catalog(*, query: str, kind: str = 'results', limit: int = 20) -> SearchResponse:
    normalized_query = _normalize_search_text(query)
    safe_limit = max(1, min(limit, 50))

    if len(normalized_query) < 2:
        return SearchResponse(query=query, kind=_normalize_kind(kind), total_count=0, results=[])

    with closing(connect_poi()) as connection:
        poi_rows = connection.execute(
            """
            SELECT
                poi.id,
                poi.layer_id,
                poi.display_name,
                poi.name,
                poi.city,
                poi.postal_code,
                poi.source_record_id,
                poi.pharmacy_establishment_id,
                poi_layer.label AS layer_label,
                poi_layer.category AS layer_category
            FROM poi
            INNER JOIN poi_layer ON poi_layer.id = poi.layer_id
            WHERE poi.is_active = 1
              AND poi_layer.is_active = 1
            ORDER BY poi_layer.priority ASC, poi.display_name ASC, poi.name ASC
            """
        ).fetchall()
        city_rows = connection.execute(
            """
            SELECT city, postal_code, COUNT(*) AS poi_count
            FROM poi
            WHERE is_active = 1
              AND city IS NOT NULL
              AND city != ''
            GROUP BY city, postal_code
            ORDER BY city ASC, postal_code ASC
            """
        ).fetchall()
        layer_rows = connection.execute(
            """
            SELECT id, label, category
            FROM poi_layer
            WHERE is_active = 1
            ORDER BY priority ASC, label ASC
            """
        ).fetchall()

    scored_results: list[tuple[int, int, SearchResultResponse]] = []
    seen_keys: set[tuple[str, str]] = set()

    for row in poi_rows:
        result_type = 'pharmacy' if row['pharmacy_establishment_id'] else 'poi'
        label = row['display_name'] or row['name'] or row['source_record_id'] or row['layer_label']
        secondary_label = _join_parts(row['postal_code'], row['city'], row['layer_label'])
        score = _score_match(
            normalized_query,
            primary=label,
            exact_id=row['pharmacy_establishment_id'] or row['source_record_id'],
            alternates=[row['city'], row['layer_label'], row['layer_category']],
            result_type=result_type,
        )
        if score is None:
            continue

        item = SearchResultResponse(
            id=f"{result_type}:{row['id']}",
            result_type=result_type,
            label=label,
            secondary_label=secondary_label,
            target_href=_build_target_href(result_type, row['pharmacy_establishment_id'], row['layer_id'], row['city']),
            pharmacy_establishment_id=row['pharmacy_establishment_id'],
            layer_id=row['layer_id'],
            layer_label=row['layer_label'],
            city=row['city'],
        )
        result_key = (item.result_type, item.id)
        if result_key in seen_keys:
            continue
        seen_keys.add(result_key)
        scored_results.append((score, _result_type_priority(result_type), item))

    for row in city_rows:
        score = _score_match(
            normalized_query,
            primary=row['city'],
            exact_id=None,
            alternates=[row['postal_code']],
            result_type='city',
        )
        if score is None:
            continue

        item = SearchResultResponse(
            id=f"city:{row['city']}:{row['postal_code'] or ''}",
            result_type='city',
            label=row['city'],
            secondary_label=_join_parts(row['postal_code'], f"{row['poi_count']} point(s)"),
            target_href=f"/map?city={row['city']}",
            city=row['city'],
        )
        result_key = (item.result_type, item.id)
        if result_key in seen_keys:
            continue
        seen_keys.add(result_key)
        scored_results.append((score, _result_type_priority('city'), item))

    for row in layer_rows:
        score = _score_match(
            normalized_query,
            primary=row['label'],
            exact_id=row['id'],
            alternates=[row['category']],
            result_type='layer',
        )
        if score is None:
            continue

        item = SearchResultResponse(
            id=f"layer:{row['id']}",
            result_type='layer',
            label=row['label'],
            secondary_label=row['category'],
            target_href=f"/map?layer={row['id']}",
            layer_id=row['id'],
            layer_label=row['label'],
        )
        result_key = (item.result_type, item.id)
        if result_key in seen_keys:
            continue
        seen_keys.add(result_key)
        scored_results.append((score, _result_type_priority('layer'), item))

    scored_results.sort(key=lambda item: (item[0], item[1], _normalize_search_text(item[2].label), item[2].secondary_label or ''))
    results = [item for _, _, item in scored_results[:safe_limit]]
    return SearchResponse(
        query=query,
        kind=_normalize_kind(kind),
        total_count=len(scored_results),
        results=results,
    )


def _normalize_kind(kind: str) -> SearchKind:
    return 'suggestions' if kind == 'suggestions' else 'results'


def _normalize_search_text(value: str | None) -> str:
    if not value:
        return ''

    normalized = unicodedata.normalize('NFKD', value)
    without_accents = ''.join(char for char in normalized if not unicodedata.combining(char))
    lowered = without_accents.lower()
    return re.sub(r'\s+', ' ', lowered).strip()


def _score_match(
    query: str,
    *,
    primary: str | None,
    exact_id: str | None,
    alternates: list[str | None],
    result_type: str,
) -> int | None:
    primary_value = _normalize_search_text(primary)
    exact_id_value = _normalize_search_text(exact_id)
    alternate_values = [_normalize_search_text(value) for value in alternates if _normalize_search_text(value)]

    if exact_id_value and query == exact_id_value:
        return 0 if result_type == 'pharmacy' else 5
    if primary_value == query:
        return 10
    if primary_value.startswith(query):
        return 20 + _result_type_priority(result_type)
    if any(value.startswith(query) for value in alternate_values):
        return 30 + _result_type_priority(result_type)
    if query in primary_value:
        return 40 + _result_type_priority(result_type)
    if any(query in value for value in alternate_values):
        return 50 + _result_type_priority(result_type)
    return None


def _result_type_priority(result_type: str) -> int:
    return {
        'pharmacy': 0,
        'poi': 1,
        'city': 2,
        'layer': 3,
    }[result_type]


def _join_parts(*parts: str | None) -> str | None:
    values = [part for part in parts if part]
    return ' · '.join(values) if values else None


def _build_target_href(result_type: str, establishment_id: str | None, layer_id: str | None, city: str | None) -> str:
    if result_type == 'pharmacy' and establishment_id:
        return f'/pharmacie/{establishment_id}'
    if result_type == 'layer' and layer_id:
        return f'/map?layer={layer_id}'
    if result_type == 'city' and city:
        return f'/map?city={city}'
    return '/map'
