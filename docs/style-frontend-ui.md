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
- `frontend/src/components/layout/nav.ts`
- `frontend/src/components/layout/page-metadata.tsx`
- `frontend/src/components/layout/HeaderActions.tsx`
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
- largeur sidebar desktop : `260px`
- hauteur shell : `h-screen`
- scroll principal : `main`
- scroll sidebar : interne

Sidebar :
- branding simple
- nav principale
- nav footer
- item actif lisible avec fond accent + indicateur vertical primaire

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

### `/settings`
- reglages d affichage et de comportement cartographique
- champs simples, lisibles, coherents avec les primitives UI

Regles communes :
- wrapper metier `div.space-y-4`
- sections en `Card`
- pas de header local duplique

---

## 9) Accessibilite et UX

Checklist minimale :
- focus visible sur boutons et items de nav
- `aria-label` sur bouton menu mobile
- structure semantique `header`, `main`, `nav`
- navigation clavier possible
- pas de zoom horizontal impose

---

## 10) Checklist de verification UI

- [ ] Le shell global encapsule toutes les pages
- [ ] Navigation centralisee via `nav.ts`
- [ ] Titre/subtitle centralises via `page-metadata.tsx`
- [ ] Pas de duplication header/container
- [ ] La carte `/map` est fonctionnelle
- [ ] Les couches peuvent etre activees/desactivees
- [ ] Le rendu reste sobre, lisible, reactif et professionnel
