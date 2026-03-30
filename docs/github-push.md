Vérifie le code local actuel de mon projet et compare-le au dépôt GitHub suivant :
https://github.com/kolokolone/CartoPharma

Ensuite, exécute directement cette procédure :
- vérifier l’état du dépôt local
- comparer le code local avec le dépôt GitHub
- récupérer les éventuelles différences utiles si nécessaire
- vérifier qu’il n’y a pas de problème bloquant avant publication
- incrémenter la version du projet de +0.0.1
- mettre à jour tous les fichiers de version concernés
- préparer un commit propre et cohérent
- commit les changements
- push sur la branche main

Après le push :
- lancer l’analyse CI
- s’assurer que la pipeline CI passe correctement
- créer ou mettre à jour ce qu’il faut pour que la création de l’image Docker se fasse automatiquement sur GitHub après validation CI
- utiliser GitHub Actions pour le workflow CI/CD
- utiliser Docker Image (GHCR) comme registre cible
- publier automatiquement l’image Docker sur GitHub Container Registry (ghcr.io)
- si le workflow CI/CD ou Docker n’existe pas encore, le créer proprement et l’intégrer au projet
- si le workflow existe déjà, le corriger ou l’adapter si nécessaire

Exigences spécifiques pour le workflow :
- le workflow doit construire l’image Docker
- le workflow doit taguer l’image proprement
- le workflow doit pousser l’image sur GHCR
- le workflow doit être compatible avec la branche main
- le workflow doit utiliser les mécanismes standard GitHub Actions pour Docker et GHCR
- le workflow doit rester cohérent avec la version du projet
- le workflow doit éviter toute configuration inutilement complexe

Contraintes :
- ne pas faire de modification inutile
- conserver la cohérence du projet
- ne pas inclure de fichiers temporaires, locaux ou parasites dans le commit
- travailler proprement et de façon idempotente
- pousser uniquement sur main
- ne pas me faire de compte-rendu final
- n’afficher quelque chose que s’il y a une erreur bloquante ou une information indispensable pour terminer l’opération

Objectif final :
le code est vérifié, la version est augmentée de +0.0.1, les changements sont commit et push sur main, la CI est lancée, et l’image Docker est automatiquement construite et publiée sur GHCR.