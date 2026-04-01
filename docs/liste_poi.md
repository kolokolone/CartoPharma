# Référentiel POI CartoPharma

## 1. Objectif

Ce document est la source de vérité documentaire pour les couches POI de CartoPharma.

Il définit :
- les domaines racine côté produit ;
- les couches techniques (`layer_id`) à exposer dans la base et dans l'interface ;
- les libellés métier attendus ;
- la famille couleur associée à chaque domaine.

## 2. Règles de structuration

Le référentiel doit rester stable sur deux niveaux uniquement :

1. **domaine racine** : regroupement produit lisible par l'utilisateur ;
2. **couche technique** : identifiant stable utilisé par l'import, la base et le frontend.

Règles à respecter :
- un `layer_id` est en `snake_case` ;
- une couche appartient à un seul domaine racine ;
- les variantes métier trop fines ne deviennent pas automatiquement de nouvelles couches ;
- la couleur est définie au niveau de la couche et doit rester cohérente avec la famille de son domaine ;
- une même famille couleur peut admettre des variantes de teinte par couche tant que la hiérarchie métier reste lisible ;
- le même référentiel doit piloter l'import, le panneau de couches, la carte et les popups.

## 3. Domaines racine

- **Santé — concurrence** : vert santé ;
- **Santé — prescripteurs** : bleu médical ;
- **Santé — paramédical** : turquoise ;
- **Santé — structures** : rouge santé ;
- **Médico-social** : prune ;
- **Santé annexe** : cyan doux ;
- **Mobilité** : violet ;
- **Flux commercial** : orange ;
- **Services publics et vie locale** : gris bleuté.

## 4. Référentiel consolidé des couches

### Santé — concurrence

Famille couleur : **vert santé**

- `pharmacies` — Pharmacies d'officine
- `parapharmacies` — Parapharmacies

Notes :
- les notions de pharmacie de garde, de gare ou de centre commercial doivent d'abord être traitées comme des attributs ou des sous-catégories de `pharmacies` ;
- on évite de multiplier les couches tant qu'une source distincte et un usage produit clair ne le justifient pas.

### Santé — prescripteurs

Famille couleur : **bleu médical**

- `medecins_generalistes` — Médecins généralistes
- `medecins_specialistes` — Médecins spécialistes
- `dentistes` — Chirurgiens-dentistes
- `sages_femmes` — Sages-femmes

### Santé — paramédical

Famille couleur : **turquoise**

- `infirmiers` — Infirmiers et cabinets infirmiers
- `kinesitherapeutes` — Masseurs-kinésithérapeutes
- `orthophonistes` — Orthophonistes
- `orthoptistes` — Orthoptistes
- `podologues` — Pédicures-podologues
- `ergotherapeutes` — Ergothérapeutes
- `psychomotriciens` — Psychomotriciens

### Santé — structures

Famille couleur : **rouge santé**

- `hopitaux` — Hôpitaux
- `cliniques` — Cliniques
- `urgences` — Services d'urgences
- `centres_de_sante` — Centres de santé
- `maisons_de_sante` — Maisons de santé pluriprofessionnelles
- `laboratoires` — Laboratoires d'analyses médicales
- `radiologie_imagerie` — Radiologie et imagerie
- `centres_de_dialyse` — Centres de dialyse
- `centres_de_cancerologie` — Centres de cancérologie
- `maternite` — Maternités
- `ssr` — Soins de suite et de réadaptation
- `had` — Hospitalisation à domicile

### Médico-social

Famille couleur : **prune**

- `ehpad` — EHPAD
- `residences_seniors` — Résidences seniors
- `ssiad` — SSIAD
- `saad` — SAAD
- `foyers_handicap` — Foyers et structures handicap
- `centres_reeducation` — Centres de rééducation

### Santé annexe

Famille couleur : **cyan doux**

- `opticiens` — Opticiens
- `audioprothesistes` — Audioprothésistes
- `materiel_medical` — Matériel médical
- `orthopedie` — Orthopédie

### Mobilité

Famille couleur : **violet**

- `arrets_bus` — Arrêts de bus
- `stations_tram` — Stations de tram
- `stations_metro` — Stations de métro
- `gares` — Gares
- `parkings` — Parkings
- `stations_velo` — Stations de vélo en libre-service
- `taxis` — Stations de taxi

### Flux commercial

Famille couleur : **orange**

- `supermarches` — Supermarchés et hypermarchés
- `centres_commerciaux` — Centres commerciaux
- `boulangeries` — Boulangeries à fort trafic
- `tabac_presse` — Tabac et presse
- `poste` — La Poste
- `banques` — Banques
- `marches` — Marchés
- `stations_service` — Stations-service

### Services publics et vie locale

Famille couleur : **gris bleuté**

- `mairies` — Mairies
- `cpam_caf_france_services` — CPAM, CAF et France Services
- `ecoles` — Écoles
- `colleges` — Collèges
- `lycees` — Lycées
- `universites` — Universités
- `creches` — Crèches
- `equipements_sportifs` — Équipements sportifs

## 5. Conséquences d'implémentation

Ce référentiel doit piloter directement :
- les `layer_id` importés en base ;
- les libellés visibles dans le panneau de couches ;
- les couleurs portées par `poi_layer.color` ;
- la documentation d'indexation et de parsing des sources ;
- les badges et repères visuels de la carte.

## 6. Cas particuliers à traiter comme attributs

Sauf décision produit explicite contraire, les cas suivants ne doivent pas créer une nouvelle couche dédiée :

- pharmacie de garde ;
- pharmacie en gare ;
- pharmacie en centre commercial ;
- activité principale ou secondaire d'un professionnel ;
- établissement public ou privé quand l'information peut vivre comme attribut.

La règle générale est de conserver des couches lisibles, stables et réutilisables, puis de porter la granularité fine dans les attributs métier.
