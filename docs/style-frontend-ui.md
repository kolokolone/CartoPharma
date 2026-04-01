# CartoPharma - Guide de style Frontend UI

## 1) Objectif

Ce document est la reference UI normative de CartoPharma pour la phase fondation.

Il definit :
- le shell global obligatoire
- les regles de navigation
- les conventions de header et de container
- les principes de composition des pages `/`, `/map`, `/settings`
- les tokens visuels et le rythme d interface

En cas de doute, ce document prime sur l implementation locale d une page.

---

## 2) Architecture UI cible

Fichiers structurants :
- `frontend/src/components/layout/AppShell.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/layout/NavItem.tsx`
- `frontend/src/components/layout/TopHeader.tsx`
- `frontend/src/components/layout/PageContainer.tsx`
- `frontend/src/components/map/PoiFeaturePopup.tsx`
- `frontend/src/components/layout/nav.ts`
- `frontend/src/components/layout/page-metadata.tsx`
- `frontend/src/components/layout/HeaderActions.tsx`
- `frontend/src/lib/app-version.ts`
- `frontend/src/app/globals.css`
- `frontend/src/app/layout.tsx`

Contrat technique :

```tsx
<Providers>
  <AppShell>{children}</AppShell>
</Providers>
```

Interdictions :
- ne pas contourner `AppShell` pour les pages applicatives standards
- ne pas recreer de header global local
- ne pas recreer de container root local

---

## 3) Navigation - source unique

Fichier unique : `frontend/src/components/layout/nav.ts`

Ordre courant :
1. `Accueil` -> `/`
2. `Carte` -> `/map`
3. `Paramètres` -> `/settings` (footer)

Regles :
- ne jamais hardcoder une navigation globale dans une page
- ne jamais dupliquer l ordre de navigation ailleurs
- toute evolution de navigation passe par `nav.ts`

---

## 4) Header metadata - source unique

Fichier unique : `frontend/src/components/layout/page-metadata.tsx`

Chaque route declare :
- `title`
- `subtitle`
- `container`
- eventuellement des `HeaderActions`

Regles :
- les titres ne viennent pas des pages
- les actions specifiques vivent dans le slot du header global
- `/map` utilise un container `wide`

---

## 5) Shell global

Structure :
- colonne gauche : sidebar fixe sur desktop
- colonne droite : header sticky + contenu scrollable

Valeurs retenues :
- largeur sidebar desktop ouverte : `220px`
- largeur sidebar desktop reduite : `3.5rem`
- hauteur shell : `h-screen`
- scroll principal : `main`
- scroll sidebar : interne

Sidebar :
- branding simple
- nav principale
- nav footer
- item actif lisible avec fond accent + indicateur vertical primaire
- bouton de reduction en haut a droite sur desktop
- mode reduit desktop :
  - aucun bloc branding texte
  - bouton de reouverture en haut
  - navigation principale et secondaire conservees en dessous
  - items affiches en icones seules avec `title` / `aria-label`

TopHeader :
- sticky unique
- `h1` + subtitle a gauche
- actions compactes a droite
- bouton menu en mobile uniquement

Drawer mobile :
- largeur `18rem`
- max largeur `88vw`
- fermeture par overlay, `Escape` et changement de route

---

## 6) Container et rythme vertical

Le container global est gere uniquement par `PageContainer`.

Variants :
- `default`: `max-w-6xl`
- `wide`: `max-w-[88rem]`

Padding standard :
- x : `px-4 sm:px-6 lg:px-8`
- y : `py-6`

Rythme :
- sections : `space-y-4`
- grilles : `gap-4`

---

## 7) Tokens visuels

Les tokens sont definis dans `frontend/src/app/globals.css`.

Palette utilisee :
- `background`, `foreground`
- `card`, `card-foreground`
- `muted`, `muted-foreground`
- `accent`, `accent-foreground`
- `primary`, `primary-foreground`
- `border`, `input`, `ring`, `destructive`

Regles :
- utiliser les tokens pour l UI structurelle
- eviter les couleurs hardcodees sauf visualisation metier cartographique
- pour la cartographie metier, la source de verite de la couleur doit etre `poi_layer.color`
- une meme couleur de couche doit etre reutilisee pour le point carte, la pastille du panneau de couches, le badge de popup et les futurs reperes de detail
- les couleurs hardcodees frontend ne sont autorisees qu en fallback de securite si la couleur backend manque

---

## 8) Composition des pages

### `/`
- page d accueil sobre
- cartes de presentation produit
- CTA principal vers `/map`

### `/map`
- carte interactive au centre de l experience
- panneau de couches dans une `Card`
- architecture prete pour pharmacies, professionnels de sante, transports, commerces, points d interet
- aucune zone de chalandise dans cette phase
- la hierarchie couleur des couches doit rester coherente entre panneau, carte et popup
- recommandation initiale de familles couleur : `pharmacies` en vert sante fort, `parapharmacies` en vert secondaire, `medecins_*` en bleu medical, les couches paramedicales en turquoise, `hopitaux` / `cliniques` / `urgences` en rouge, les couches medico-sociales en prune, les couches de sante annexe en cyan doux, les couches de mobilite en violet, les couches de flux commercial en orange, les couches de services publics et vie locale en gris bleute
- le detail complet du rattachement couche -> famille couleur doit rester centralise dans `docs/liste_poi.md`
- popup pharmacie :
  - `Pharmaciens` affiche le total sur une ligne de metadonnees au meme format que `Telephone`
  - `Type` pharmacie affiche sur une ligne de metadonnees simple
  - `Site` ne doit rendre qu un lien `http/https`

### `/settings`
- reglages d affichage et de comportement cartographique
- champs simples, lisibles, coherents avec les primitives UI
- version applicative visible tout en haut a gauche, au-dessus des cartes de reglage

Regles communes :
- wrapper metier `div.space-y-4`
- sections en `Card`
- pas de header local duplique

---

## 9) Accessibilite et UX

Checklist minimale :
- focus visible sur boutons et items de nav
- `aria-label` sur bouton menu mobile
- `aria-label="Navigation"` sur le drawer mobile en mode dialogue
- structure semantique `header`, `main`, `nav`
- navigation clavier possible
- pas de zoom horizontal impose
- en mode sidebar reduite, les icones restent navigables sans texte visible grace a `title` et `aria-label`

---

## 10) Checklist de verification UI

- [ ] Le shell global encapsule toutes les pages
- [ ] Navigation centralisee via `nav.ts`
- [ ] Titre/subtitle centralises via `page-metadata.tsx`
- [ ] Pas de duplication header/container
- [ ] La sidebar desktop peut se reduire et se reouvrir proprement
- [ ] La sidebar reduite conserve les icones de navigation sous le bouton d ouverture
- [ ] La carte `/map` est fonctionnelle
- [ ] Les couches peuvent etre activees/desactivees
- [ ] Le popup pharmacie affiche les metadonnees cles avec le meme rythme visuel que les autres lignes
- [ ] Le rendu reste sobre, lisible, reactif et professionnel
