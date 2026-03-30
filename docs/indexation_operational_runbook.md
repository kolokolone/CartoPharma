# Runbook - Initialisation des donnees cartographiques

Ce document garde le nom historique du corpus de reference mais, dans CartoPharma, il decrit la future initialisation des couches de donnees.

Etat actuel :
- aucune indexation metier lourde n est lancee
- la fondation s appuie sur des donnees mockees

Future procedure cible :
1. importer une source brute par couche
2. normaliser vers un schema commun GeoJSON/point
3. enregistrer un horodatage de mise a jour
4. publier via l API de couches
