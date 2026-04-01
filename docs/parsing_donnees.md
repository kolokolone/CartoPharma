# Référentiel de parsing des données POI

## 1. Objectif

Ce document définit comment les sources POI doivent être récupérées, normalisées et préparées avant import dans CartoPharma.

Il s'agit d'un référentiel interne de structuration des données, pas d'une note exploratoire.

Les règles ci-dessous pilotent :
- le stockage des fichiers sources dans `data/csv/` ;
- la détection des lots métier ;
- la normalisation des colonnes ;
- la projection finale dans `data/poi.sqlite` ;
- l'alignement avec `docs/liste_poi.md`.

## 2. Règles générales obligatoires

### Emplacements cibles

- les sources CSV simples vivent dans `data/csv/` ;
- les lots métier composés de plusieurs fichiers vivent dans `data/csv/<domaine>/` ;
- la première spécialisation à supporter est `data/csv/pharmacies/` ;
- la base cible d'import cartographique reste `data/poi.sqlite`.

### Alignement avec le référentiel POI

Toute source importée doit produire une couche technique conforme à `docs/liste_poi.md` :
- même `layer_id` ;
- même périmètre métier ;
- même logique de regroupement ;
- pas de duplication d'une même couche sous plusieurs noms.

### Détection des fichiers

La détection doit être robuste et ne jamais dépendre d'un nom de fichier unique figé.

Règles obligatoires :
- détection par motif de nom ;
- tolérance aux suffixes horodatés ;
- tolérance au singulier/pluriel ;
- tolérance aux accents présents ou absents ;
- sélection d'un seul fichier retenu par catégorie métier.

### Règle de précédence

Quand plusieurs exports d'une même catégorie existent :
- on retient le fichier le plus récent ;
- on rejette les situations ambiguës si deux fichiers ne peuvent pas être départagés proprement ;
- on n'importe jamais deux variantes concurrentes de la même couche dans `poi`.

### Normalisation minimale avant import

Avant toute jointure ou projection, le pipeline doit :
- normaliser les noms de colonnes ;
- trim les espaces parasites ;
- conserver les identifiants métier sous forme de chaînes ;
- préserver les zéros significatifs ;
- documenter explicitement l'encodage et le séparateur ;
- distinguer les champs source des champs projetés pour la carte.

## 3. Référentiel pharmacie

### Source officielle

- URL de référence : `https://www.ordre.pharmacien.fr/je-suis/patient-grand-public/l-annuaire-des-pharmaciens-etablissements`
- téléchargement attendu : une archive contenant plusieurs CSV métier

### Stockage cible

Le lot pharmacie normalisé doit vivre dans `data/csv/pharmacies/`.

Catégories attendues :
- fichier établissements ;
- fichier pharmaciens ;
- fichier activités ;
- fichier diplômes.

Exemples de motifs acceptés :
- `*etablissement*.csv`
- `*pharmacien*.csv`
- `*activite*.csv`
- `*diplome*.csv`

### Précédence vis-à-vis de `data/csv/pharmacies.csv`

Règle normative :
- si le lot spécialisé `data/csv/pharmacies/` est complet, il est prioritaire ;
- `data/csv/pharmacies.csv` ne sert que de fallback historique ;
- il est interdit d'importer à la fois le lot spécialisé et `pharmacies.csv` pour reconstruire deux versions concurrentes de la couche `pharmacies`.

### Format attendu

Les fichiers pharmacie doivent être lus avec les hypothèses suivantes :
- encodage cible : UTF-16, avec fallback explicite si la source évolue ;
- séparateur : `;` ;
- clés de jointure manipulées comme des chaînes.

### Colonnes métier minimales

#### Établissements

Colonnes minimales à exploiter :
- `Numéro d'établissement`
- `Type établissement`
- `Dénomination commerciale`
- `Raison sociale`
- `Adresse`
- `Code postal`
- `Commune`
- `Département`
- `Région`
- `Téléphone`
- `Fax`

#### Pharmaciens

Colonnes minimales à exploiter :
- `n° RPPS`
- `Titre`
- `Nom d'exercice`
- `Prénom`
- `Date de première inscription`

#### Activités

Colonnes minimales à exploiter :
- `n° RPPS pharmacien`
- `Numéro d'établissement`
- `Fonction`
- `Date d'inscription`
- `Section`
- `Activité principale`

#### Diplômes

Colonnes minimales à exploiter :
- `n° RPPS pharmacien`
- `Diplôme`
- `Date d'obtention`
- `Université`
- `Region`

### Clés de jointure obligatoires

Les rapprochements métier reposent sur :
- `Numéro d'établissement` pour relier établissements et activités ;
- `RPPS` pour relier pharmaciens, activités et diplômes.

Normalisation obligatoire :
- trim des espaces ;
- conservation stricte des zéros ;
- homogénéisation des variantes de nom de colonne liées au RPPS ;
- aucune conversion en entier ou en flottant.

### Pipeline de transformation attendu

1. charger les 4 fichiers bruts ;
2. normaliser les noms de colonnes et les clés métier ;
3. construire le référentiel établissement ;
4. construire le référentiel pharmacien ;
5. rattacher les pharmaciens aux établissements via `activites` ;
6. enrichir les pharmaciens avec `diplomes` ;
7. projeter une couche `pharmacies` prête pour l'affichage carte.

### Projection minimale attendue dans `poi`

Chaque pharmacie projetée dans `poi` doit fournir au minimum :
- un identifiant métier stable d'établissement ;
- un nom affichable ;
- une adresse exploitable ;
- des coordonnées cartographiques ;
- un compteur de pharmaciens distincts ;
- les métadonnées minimales utiles au popup.

Règle de calcul du compteur :
- le nombre de pharmaciens doit être calculé à partir des `RPPS` distincts rattachés à l'établissement ;
- plusieurs lignes d'activité pour un même RPPS ne doivent pas gonfler artificiellement le total.

## 4. Fiche standard pour les autres sources

Toute nouvelle source documentée dans ce fichier doit suivre la même structure :

1. source officielle ;
2. emplacement de stockage dans `data/csv/` ;
3. `layer_id` cible conforme à `docs/liste_poi.md` ;
4. format de fichier attendu ;
5. colonnes minimales à parser ;
6. règles de déduplication ;
7. règles de géocodage ou d'utilisation des coordonnées ;
8. projection minimale attendue dans `poi`.

## 5. Priorités documentaires suivantes

Les prochaines fiches à formaliser sur ce modèle sont :
- `medecins_generalistes` et `medecins_specialistes` ;
- `infirmiers` ;
- `dentistes`.

Règle de rédaction :
- documenter une couche ou une famille cohérente ;
- ne pas mélanger description métier, source brute et projection cartographique dans une section floue ;
- conserver une rédaction prescriptive permettant une implémentation directe.
