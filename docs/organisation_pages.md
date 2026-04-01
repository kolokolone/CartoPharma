# Organisation des pages

Ce document sert de base pour decrire le comportement des pages de l'application.

Pour chaque page, l'idee est de decrire :
- son utilite ;
- ses fonctions principales ;
- ses dependances frontend/backend ;
- les donnees affichees ;
- les points UX importants.

## Principes transverses

- les pages applicatives standard restent dans le shell global (`AppShell`) ;
- les titres, sous-titres et variantes de container restent centralises dans `frontend/src/components/layout/page-metadata.tsx` ;
- la navigation globale doit rester geree dans `frontend/src/components/layout/nav.ts` ;
- chaque page doit avoir un parcours principal clair ;
- privilegier des sections courtes, lisibles et faciles a faire evoluer.

## '/' accueil :

- utilite :
    - premiere page sur laquelle on tombe ;
    - poser rapidement le cadre de CartoPharma ;
    - orienter vers les actions principales : consulter la carte, lancer une recherche et regler l'application.
- fonctions :
    - presenter la proposition de valeur du produit ;
    - mettre en avant les grands blocs de l'application ;
    - proposer des CTA visibles vers `/map`, `/search` et `/settings`.
- dependances :
    - `frontend/src/app/page.tsx` ;
    - composants UI simples de type `Card` et `Button` ;
    - metadonnees de page centralisees via `frontend/src/components/layout/page-metadata.tsx`.
- idees d'evolution douce :
    - garder une page volontairement courte ;
    - ajouter plus tard un petit bloc de contexte utile (etat des donnees, derniere reindexation, resume rapide) ;
    - conserver un ton sobre et orienter clairement vers l'ouverture de la carte.

## '/map' map :

- utilite :
    - page centrale du produit ;
    - afficher la carte avec les points d'interet ;
    - permettre une lecture territoriale simple et immediate.
- fonctions :
    - afficher la map avec tous les points d'interet ;
    - activer / desactiver les couches ;
    - filtrer les points d'interet, d'abord par couches puis progressivement par zone visible et par criteres metier ;
    - afficher un etat lisible de la carte : nombre de couches actives, nombre de points, statut des donnees ;
    - servir de point d'entree vers une fiche detail de POI quand cela a du sens.
- dependances :
    - `frontend/src/app/map/page.tsx` ;
    - `CartoMap`, `LayerTogglePanel`, `useLayersCatalog`, `useLayerPoints` ;
    - API `/api/v1/layers` et `/api/v1/layers/points`.
- idees d'evolution douce :
    - reserver un emplacement naturel pour une future recherche rapide ;
    - faciliter le passage carte -> detail d'un POI ;
    - garder le panneau lateral simple pour ne pas concurrencer visuellement la carte.

## '/settings' parametres :

- utilite :
    - page qui permet de regler les parametres de l'application ;
    - centraliser les preferences utilisateur et les actions techniques utiles.
- fonctions :
    - regler le theme ;
    - regler l'affichage des labels et le mode de controles compacts ;
    - enregistrer les preferences ;
    - relancer la reindexation des donnees avec un retour de statut ;
    - afficher la version applicative.
- dependances :
    - `frontend/src/app/settings/page.tsx` ;
    - `useSettings`, `usePatchSettings`, `useRebuildPoi`, `APP_VERSION` ;
    - API `/api/v1/settings` et `/api/v1/indexing/rebuild-poi`.
- idees d'evolution douce :
    - bien separer ce qui releve des preferences utilisateur et ce qui releve des operations de maintenance ;
    - garder des messages de retour tres clairs apres sauvegarde ou reindexation ;
    - prevoir plus tard une petite zone de diagnostic ou de resume systeme si besoin.

## '/search' page de recherche :

- utilite :
    - page qui permet de chercher dans la base de donnees un certain POI ;
    - offrir un acces rapide a une pharmacie, une ville, une categorie ou un identifiant.
- fonctions :
    - en tapant dans la barre de recherche, la liste defile au fur et a mesure qu'on tape des mots ;
    - apres avoir tape ce qu'on veut dans la barre de recherche, on peut soit cliquer dans la liste qui deroule, soit faire Entrer, soit utiliser un bouton `Rechercher` pour obtenir une liste de resultats ;
    - on a la possibilite de cliquer sur un resultat qui nous envoie vers la page du POI ;
    - la liste de resultats peut etre classee par type ou categorie pour rester lisible ;
    - la requete de recherche peut idealement rester visible dans l'URL pour permettre le partage et le retour arriere.
- dependances a prevoir :
    - un endpoint backend dedie a la recherche ;
    - des composants de liste/resultat reutilisables ;
    - une bonne articulation avec la page `/map` et la page `/pharmacie/[id]`.
- points UX importants :
    - reponse rapide ;
    - surbrillance des mots trouves ;
    - message clair si aucun resultat ;
    - ordre de pertinence simple a comprendre ;
    - priorite visible aux pharmacies si c'est le cas d'usage principal.

## '/pharmacie/[id]' page d'une pharmacie en particulier :

- utilite :
    - page d'information complete de la pharmacie ;
    - page de reference pour consulter a la fois l'identite, le contexte geographique et l'equipe.
- contenu principal :
    - referencement de toutes les informations connues a son sujet (mettre un `/` si info manquante) ;
    - commencer par les donnees deja solides, puis enrichir progressivement l'affichage.
- informations a afficher :
    - adresse complete ;
    - telephone ;
    - horaires ;
    - site internet ;
    - lien Pappers si disponible ;
    - type d'etablissement ;
    - nombre de pharmaciens rattaches ;
    - autres informations a definir et completer dans cette liste selon ce qu'on a dans la base de donnees.
- blocs de page a conserver :
    - un encadre pour une petite map centree sur la pharmacie avec affichage des autres POI autour d'elle, dans une logique proche de `/map` ;
    - un encadre pour la composition de l'equipe avec la liste des pharmaciens qui y travaillent ;
    - un encadre pour une liste des POI autour de la pharmacie ;
    - un bloc favori facilement accessible.
- composition de l'equipe :
    - tableau avec :
        - nom ;
        - prenom ;
        - RPPS ;
        - diplome ;
        - annee d'inscription ;
        - fonction principale ;
        - etc.
- POI autour de la pharmacie :
    - liste categorisee en fonction de `docs/liste_poi.md` ;
    - ajout de la distance ;
    - affichage du nombre ;
    - rayon autour de la pharmacie de 1 km par defaut, avec changement possible.
- mise en favori :
    - bouton favori place de maniere visible mais discrete ;
    - tracage de cette mise en favori dans `cartopharma.sqlite` via une structure dediee ;
    - bouton vide si pas en favori, bouton plein et jaune si en favori.
- dependances :
    - API `/api/v1/pharmacies/{establishment_id}` ;
    - donnees cartographiques contenant `pharmacy_establishment_id` pour faire le lien entre carte et fiche ;
    - page `/pharmacie/[id]` ou id est Numéro d'établissement (ou mieux avec ce qu'il y a dans la base de donnée)
    - reutilisation possible de la logique cartographique existante pour le bloc map.
- idees d'evolution douce :
    - ajouter un retour rapide vers la recherche et la carte ;
    - decouper la page en cartes claires : identite, map, equipe, environnement proche ;
    - garder la page utile meme si certaines informations sont absentes.
