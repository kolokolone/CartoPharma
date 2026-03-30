# CartoPharma - référentiel d'importation des données métier

## 1. Objet du document

Ce document décrit le comportement attendu du pipeline d'import métier de CartoPharma.

Il sert de référence pour :
- comprendre comment les CSV sont lus et transformés ;
- expliquer comment les données sont importées dans `data/poi.sqlite` ;
- documenter le rôle du bouton de réindexation dans `/settings` ;
- fournir une méthode stable pour ajouter d'autres familles métier à l'avenir (`medecins`, `infirmiers`, etc.).

Ce document doit être suivi pour toute nouvelle catégorie métier importée dans le projet.

---

## 2. Vue d'ensemble du flux

### 2.1 Déclenchement fonctionnel

Le point d'entrée utilisateur est le bouton **"Réindexer les données"** dans la page `frontend/src/app/settings/page.tsx`.

Flux complet :

1. le frontend appelle `POST /api/v1/indexing/rebuild-poi` ;
2. la route backend lance `rebuild_poi_database()` ;
3. le backend vide la projection POI existante ;
4. le backend importe les catégories métier spécialisées (actuellement `pharmacies`) ;
5. le backend importe ensuite les CSV génériques restants à la racine de `data/csv/` ;
6. les statuts de géocodage sont recalculés ;
7. l'index spatial `poi_rtree` est reconstruit ;
8. le frontend affiche le rapport de réindexation.

### 2.2 Fichiers et modules impliqués

- frontend :
  - `frontend/src/app/settings/page.tsx`
  - `frontend/src/hooks/useIndexing.ts`
  - `frontend/src/lib/api.ts`
- backend :
  - `backend/app/api/routes/indexing.py`
  - `backend/app/services/poi_rebuild.py`
  - `backend/app/services/pharmacy_directory_import.py`
  - `backend/app/services/poi_import.py`
  - `backend/app/services/poi_geocoding.py`
  - `backend/app/db/poi_database.py`

---

## 3. Arborescence de données attendue

### 3.1 Répertoire racine des imports

Le backend lit les fichiers depuis :

- `data/csv/` pour les imports génériques ;
- `data/csv/pharmacies/` pour l'import métier pharmacie.

### 3.2 Convention actuelle pour `pharmacies`

Le lot pharmacie repose sur quatre fichiers spécialisés :

- `etablissements_*.csv`
- `pharmaciens_*.csv`
- `activites_*.csv`
- `diplomes_*.csv`

La sélection se fait par le nom du fichier, après normalisation ASCII/snake_case.

### 3.3 Règle importante sur `pharmacies.csv`

Le fichier racine `data/csv/pharmacies.csv` est désormais considéré comme **legacy**.

Il ne doit plus être utilisé comme source métier pharmacie :
- il n'est plus utilisé pour injecter des coordonnées de secours ;
- il est exclu du chemin d'import générique pendant un rebuild ;
- le lot métier de référence est `data/csv/pharmacies/`.

---

## 4. Lecture des CSV

### 4.1 Objectif de robustesse

Les exports métier ne sont pas toujours homogènes. Le lecteur doit donc absorber :

- UTF-16 avec BOM ;
- UTF-16 little-endian sans BOM ;
- UTF-16 big-endian ;
- UTF-8 / UTF-8 BOM ;
- `cp1252` en dernier recours.

### 4.2 Décodage

Le lecteur spécialisé pharmacie :

1. lit le fichier en binaire ;
2. détecte si le contenu ressemble à de l'UTF-16 ;
3. essaie plusieurs encodages dans un ordre contrôlé ;
4. nettoie les caractères parasites (`\ufeff`, `\x00`) ;
5. ne poursuit que si le texte décodé est exploitable.

### 4.3 Délimiteur

Le lecteur :

- respecte une éventuelle première ligne du type `sep=;` ;
- sinon utilise `csv.Sniffer()` ;
- sinon retombe sur `;` par défaut.

### 4.4 Normalisation des en-têtes

Chaque en-tête est normalisé pour produire une clé stable :

- suppression des accents ;
- passage en minuscules ;
- remplacement des séparateurs par `_` ;
- suppression des caractères nuls ;
- nettoyage des variantes pathologiques via recherche canonique sans `_`.

But : faire correspondre des variantes comme :

- `Numéro d'établissement`
- `Numero d etablissement`
- `n° RPPS`
- ou même des clés dégradées après mauvais décodage

avec les clés métier attendues par l'importeur.

---

## 5. Traitement métier par catégorie de données

## 5.1 Catégorie `etablissements`

### Rôle

Source maîtresse des officines à projeter.

### Champs métier recherchés

- identifiant établissement : `numero_d_etablissement`, `numero_etablissement`, `establishment_id`
- type : `type_etablissement`
- nom affiché : `denomination_commerciale`, sinon `raison_sociale`
- adresse : `adresse`
- code postal : `code_postal`
- commune : `commune` ou `ville`
- département : `departement` ou `department`
- région : `region`
- téléphone : `telephone` ou `phone`
- fax : `fax`

### Champs optionnels supportés

- `latitude`, `lat`, `y`
- `longitude`, `lon`, `lng`, `x`
- `site_web`, `website`, `url`
- `horaires`, `opening_hours`
- `siret`

### Règles métier

- sans identifiant établissement, la ligne est rejetée ;
- chaque établissement valide alimente :
  - la table `pharmacy_establishment`
  - puis une projection `poi` de couche `pharmacies`.

---

## 5.2 Catégorie `pharmaciens`

### Rôle

Référentiel des professionnels rattachables aux établissements.

### Champs métier recherchés

- identifiant pharmacien : `n_rpps`, `n_rpps_pharmacien`, `rpps`
- titre : `titre`, `title`
- nom : `nom_d_exercice`, `nom`, `last_name`
- prénom : `prenom`, `first_name`
- date de première inscription : `date_de_premiere_inscription`, `first_registration_date`

### Règles métier

- sans RPPS, la ligne est rejetée ;
- chaque pharmacien valide alimente la table `pharmacist`.

---

## 5.3 Catégorie `activites`

### Rôle

Table de liaison entre pharmacien et établissement, avec nature d'exercice.

### Champs métier recherchés

- établissement : `numero_d_etablissement`, `numero_etablissement`, `establishment_id`
- pharmacien : `n_rpps_pharmacien`, `n_rpps`, `rpps`
- fonction : `fonction`, `function_label`
- date : `date_d_inscription`, `registration_date`
- section : `section`, `section_code`
- activité principale : `activite_principale`, `is_primary_activity`

### Règles métier

- sans identifiant établissement ou RPPS, la ligne est rejetée ;
- si l'établissement n'existe pas dans `etablissements`, la ligne est rejetée ;
- si le pharmacien n'existe pas dans `pharmaciens`, la ligne est rejetée ;
- les lignes valides alimentent `pharmacist_activity`.

---

## 5.4 Catégorie `diplomes`

### Rôle

Historique de diplômes rattaché aux pharmaciens.

### Champs métier recherchés

- pharmacien : `n_rpps_pharmacien`, `n_rpps`, `rpps`
- diplôme : `diplome`, `degree_label`
- date : `date_d_obtention`, `degree_date`
- université : `universite`, `university`
- région : `region`

### Règles métier

- sans RPPS, la ligne est rejetée ;
- si le pharmacien n'existe pas dans `pharmaciens`, la ligne est rejetée ;
- les lignes valides alimentent `pharmacist_degree`.

---

## 6. Import en base SQLite

### 6.1 Tables métier spécialisées

Le pipeline pharmacie alimente les tables suivantes dans `data/poi.sqlite` :

- `pharmacy_establishment`
- `pharmacist`
- `pharmacist_activity`
- `pharmacist_degree`

### 6.2 Projection cartographique

Chaque établissement valide génère une ligne dans `poi` avec :

- `layer_id = 'pharmacies'`
- `pharmacy_establishment_id`
- `pharmacist_count`
- `pharmacy_type`
- les champs adresse/ville/région/téléphone
- des coordonnées soit présentes dans l'export source, soit calculées ensuite par géocodage batch

### 6.3 Géocodage

Le pipeline déclenche un géocodage batch via le service public de géocodage de la Géoplateforme.

Conséquence :

- si l'export fournit `latitude`/`longitude`, l'établissement est `resolved` ;
- sinon, si l'adresse est exploitable (`address_line_1`, `postal_code`, `city`), la ligne est envoyée à `https://data.geopf.fr/geocodage/search/csv` ;
- si la Géoplateforme retourne des coordonnées, elles sont écrites dans `poi.latitude` / `poi.longitude` avec `geocode_provider = geoplateforme_search_csv` ;
- sinon la ligne reste `pending` ;
- un établissement sans coordonnées est bien importé métier, mais n'entre pas dans `poi_rtree`.

### 6.3.1 Paramètres de géocodage

- `CARTOPHARMA_ENABLE_BATCH_GEOCODING` : active/désactive le géocodage batch (`1` par défaut)
- `CARTOPHARMA_GEOCODING_API_URL` : URL de base du service (`https://data.geopf.fr/geocodage` par défaut)
- `CARTOPHARMA_GEOCODING_BATCH_SIZE` : taille des lots envoyés à l'API (`5000` par défaut)

### 6.4 Index spatial

`poi_rtree` ne contient que les lignes `poi` avec :

- `is_active = 1`
- `latitude IS NOT NULL`
- `longitude IS NOT NULL`

Donc :
- import métier réussi ≠ point cartographique indexé ;
- les comptes "importé" et "indexé" sont volontairement distincts.

---

## 7. Sémantique du bouton de réindexation

Le bouton dans `/settings` réalise un **rebuild complet de projection**.

Cela signifie :

1. purge des erreurs d'import précédentes ;
2. purge des fichiers source historisés ;
3. purge des lignes `poi` existantes ;
4. mise en `stale` des couches existantes ;
5. purge du domaine pharmacie ;
6. réimport du lot spécialisé pharmacie ;
7. réimport des CSV génériques restants ;
8. géocodage batch des lignes sans coordonnées puis recalcul des statuts de géocodage ;
9. reconstruction de `poi_rtree`.

Le rapport renvoyé au frontend sépare :

- `pharmacies_imported`, `pharmacists_imported`, `activities_imported`, `degrees_imported`
- `generic_files_processed`, `generic_rows_imported`
- `rows_rejected`
- `poi_rows_rebuilt`
- `geocoded_resolved`, `geocoded_pending`

---

## 8. Stratégie d'extension vers d'autres catégories métier

Pour ajouter `medecins`, `infirmiers`, etc., suivre le même modèle.

### 8.1 Convention recommandée

Créer un sous-répertoire dédié :

- `data/csv/medecins/`
- `data/csv/infirmiers/`

### 8.2 Fichiers attendus

Définir explicitement les catégories internes nécessaires, par exemple :

- `praticiens`
- `structures`
- `activites`
- `specialites`

### 8.3 Module d'import dédié

Créer un module spécialisé du type :

- `backend/app/services/medecin_directory_import.py`

Ce module doit :

1. découvrir les bons fichiers ;
2. décoder les CSV de façon robuste ;
3. normaliser les en-têtes ;
4. construire des dictionnaires métier cohérents ;
5. insérer dans des tables spécialisées ;
6. projeter ce qui doit l'être dans `poi`.

### 8.4 Règles à conserver

- ne jamais dépendre d'un CSV legacy racine pour compléter une catégorie spécialisée ;
- distinguer clairement les tables métier et la projection `poi` ;
- séparer les compteurs d'import et d'indexation ;
- documenter les clés attendues par catégorie ;
- ajouter des tests avec encodages réalistes et variantes d'en-têtes.

---

## 9. Validation attendue à chaque évolution

Pour toute nouvelle famille importée :

1. ajouter ou adapter des tests backend ;
2. vérifier `lsp_diagnostics` côté backend ;
3. exécuter les tests Python pertinents ;
4. vérifier les impacts frontend si le rapport d'import change ;
5. mettre à jour cette documentation et le `README` si le comportement observé change.

---

## 10. Résumé normatif

À retenir pour le futur :

- une catégorie métier = un importeur spécialisé ;
- les CSV doivent être lus de façon tolérante aux vrais exports, pas aux seuls fichiers idéaux ;
- les identifiants métier priment sur les insertions SQL ;
- `poi` est une projection cartographique, pas la source métier ;
- le bouton de `/settings` reconstruit la projection entière ;
- les catégories futures doivent suivre cette même discipline.
