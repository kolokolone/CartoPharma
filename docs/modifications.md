# CartoPharma - liste des modifications a preparer

## Objet du fichier

Ce fichier sert a noter simplement les idees de modifications avant implementation.

Le but n est pas d ecrire une specification lourde. Le but est d avoir une liste claire, ordonnee et assez precise pour qu un humain ou un agent comprenne vite ce qu il faut faire.

## Principe

- une ligne = une idee ou une modification ;
- la ligne doit contenir directement le detail utile ;
- si une idee devient trop grosse, on la decoupe en sous-points ;
- on reste concret, lisible et exploitable.

## Comment rediger une bonne ligne

Chaque ligne doit, si possible, contenir en une seule phrase :
- ce qu il faut changer ;
- pourquoi c est utile ou necessaire ;
- le resultat attendu ;
- la contrainte importante s il y en a une.

Exemple trop vague :

- ameliorer la page map

Exemple mieux defini :

- ameliorer la page `/map` pour rendre le panneau de couches plus lisible sur mobile, sans changer le comportement actuel des couches.

## Format conseille

Format simple recommande :

```md
- [ ] Titre court - detail clair de la modification, du probleme et du resultat attendu.
```

Exemples :

```md
- [ ] Clarifier la reindexation POI dans `/settings` - expliquer a quoi sert l action, quand l utiliser et ce qu elle met a jour, sans modifier la logique backend existante.
- [ ] Ameliorer la lisibilite du panneau de couches sur `/map` - mieux gerer les petits ecrans pour eviter les blocs trop serres et garder une interface sobre.
- [ ] Mieux expliquer les donnees pharmacies dans la documentation - preciser ce qui est reel, ce qui est mocke et ce qui reste a brancher.
```

## Quand utiliser des sous-points

Si une ligne devient trop longue ou contient plusieurs morceaux importants, garder une ligne principale puis ajouter 2 a 5 sous-points.

Exemple :

```md
- [ ] Revoir l experience de reindexation POI dans `/settings`.
  - expliquer clairement le role de l action ;
  - indiquer quand il faut la lancer ;
  - preciser ce que l utilisateur peut attendre apres execution ;
  - ne pas changer le mecanisme backend sans besoin explicite.
```

## Ordre recommande

Pour que le fichier reste gerable humainement, classer les idees dans cet ordre :

1. urgent / bloquant ;
2. important a faire ensuite ;
3. ameliorations de confort ;
4. idees a clarifier plus tard.

## Statuts simples

Utiliser de preference :

- `[ ]` a faire ;
- `[-]` en cours ;
- `[x]` fait ;
- `[?]` a clarifier.

## Lien avec le workflow d agents

Si tu utilises un workflow avec des agents :

- `docs/modifications.md` = liste source, ecrite simplement ;
- agent de brainstorming / cadrage = reprend la liste et la developpe si besoin ;
- agent de dev = implemente a partir de la version enrichie.

L idee est donc de garder ici un document humain, rapide a maintenir, sans perdre les details utiles.

## Regles a garder en tete

- une idee par ligne principale ;
- rester factuel ;
- eviter les formules vagues ;
- ne pas melanger trop de sujets differents dans une seule ligne ;
- noter les contraintes importantes directement dans la ligne ou juste en dessous ;
- si une idee depend d une autre, le preciser.

## Zone de travail

### Urgent / bloquant

- [ ]

### Important / a faire ensuite

- [ ] '/search' page de recherche :
- créer cette nouvelle page
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

- [ ] '/pharmacie/[id]' page d'une pharmacie en particulier :
- créer cette nouvelle page
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

### Ameliorations de confort

- [ ]

### A clarifier plus tard

- [?]
