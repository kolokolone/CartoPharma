from __future__ import annotations

from app.models.schemas import GeoPointFeature, GeoPointProperties, LayerDefinition


LAYER_CATALOG: list[LayerDefinition] = [
    LayerDefinition(
        id="pharmacies",
        label="Pharmacies",
        category="Sante",
        color="#1d4ed8",
        priority=1,
        visible_by_default=True,
    ),
    LayerDefinition(
        id="health_professionals",
        label="Autres professionnels de sante",
        category="Sante",
        color="#0f766e",
        priority=2,
        visible_by_default=True,
    ),
    LayerDefinition(
        id="public_transport",
        label="Transports publics",
        category="Mobilite",
        color="#7c3aed",
        priority=3,
        visible_by_default=True,
    ),
    LayerDefinition(
        id="shops",
        label="Commerces utiles",
        category="Services",
        color="#c2410c",
        priority=4,
        visible_by_default=False,
    ),
    LayerDefinition(
        id="points_of_interest",
        label="Points d'interet",
        category="Services",
        color="#be123c",
        priority=5,
        visible_by_default=False,
    ),
]


MOCK_POINTS: list[GeoPointFeature] = [
    GeoPointFeature(
        geometry={"type": "Point", "coordinates": [2.3522, 48.8566]},
        properties=GeoPointProperties(id="pharm-1", layer="pharmacies", name="Pharmacie Centrale", city="Paris"),
    ),
    GeoPointFeature(
        geometry={"type": "Point", "coordinates": [4.8357, 45.764]},
        properties=GeoPointProperties(id="pharm-2", layer="pharmacies", name="Pharmacie des Terreaux", city="Lyon"),
    ),
    GeoPointFeature(
        geometry={"type": "Point", "coordinates": [5.3698, 43.2965]},
        properties=GeoPointProperties(id="health-1", layer="health_professionals", name="Cabinet Infirmier Vieux-Port", city="Marseille"),
    ),
    GeoPointFeature(
        geometry={"type": "Point", "coordinates": [1.4442, 43.6047]},
        properties=GeoPointProperties(id="transport-1", layer="public_transport", name="Station Jean Jaures", city="Toulouse"),
    ),
    GeoPointFeature(
        geometry={"type": "Point", "coordinates": [-1.5536, 47.2184]},
        properties=GeoPointProperties(id="shop-1", layer="shops", name="Supermarche Centre", city="Nantes"),
    ),
    GeoPointFeature(
        geometry={"type": "Point", "coordinates": [7.2619, 43.7102]},
        properties=GeoPointProperties(id="poi-1", layer="points_of_interest", name="Point d'accueil Riviera", city="Nice"),
    ),
]
