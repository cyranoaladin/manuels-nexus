# DIRECTIVES COLLECTION — 4 manuels Nexus Réussite

Ce fichier est lu au début de chaque session, **avant** les directives du projet actif.
`PROMPT_MISSION_COLLECTION.md` prévaut sur les directives d'un projet, puis viennent les
cahiers des charges et les documents de projet.

## Règle de flux

- Reprendre la première tâche non cochée de la check-list, sans redemander d'autorisation.
- Ne jamais refaire un travail déjà livré : contrôler le journal, les rapports et les tags.
- Les pauses de validation pilote sont non bloquantes : basculer immédiatement sur le front
  suivant. À chaque frontière de chapitre, lire `VALIDATION_PILOTE.md` ou le message humain,
  appliquer les retours puis reprendre.
- Une tâche cochée indique le commit qui la prouve. Un arrêt total n'est admis que lorsque les
  quatre fronts dépendent d'une validation humaine, ou après trois contournements documentés.
- Exécuter les gates, compiler et inspecter les livrables avant chaque commit ; conserver les
  rapports de LOT et les preuves de validation.

## Check-list ordonnée

- [x] **J1 — NSI : installation et bootstrap.** Commit `2bca1c2`.
- [x] **J2 — NSI Première : pilote Types construits LOT 0–7, PDF et dossier de validation.**
  Commits `233c39b` et `9da092e` (charte v3.2 et spécimen de contrôle) ; validation humaine
  conjointe en attente, non bloquante.
- [ ] **J3 — Mathématiques Première : achever le chapitre actif puis les chapitres restants
  jusqu'à Variables aléatoires ; exécuter les lots finaux du manuel.**
- [ ] **J4 — Mathématiques Terminale : bootstrap, référentiel, production complète.**
- [ ] **J5 — NSI Première : chapitres 2 à 10 après validation du pilote ; sinon poursuivre J4.**
- [ ] **J6 — NSI Terminale : chapitres 1 à 12 et blocs d'épreuve.**
- [ ] **J7 — Lots finaux des quatre manuels : assemblages, livrets professeur et gates.**
- [ ] **J8 — Cohérence collection : identité, progressions, terminologie et rapports finaux.**

Les tâches J3/J4 et J5/J6 peuvent s'intercaler selon les validations humaines ; l'ordre
interne des chapitres d'un même manuel reste fixe.

## Garde-fous collection

- Respecter les référentiels officiels et les règles de propriété intellectuelle de chaque
  dépôt ; toute donnée réglementaire actuelle est vérifiée auprès d'une source officielle.
- Conserver les interfaces communes (charte, gabarits, gates et conventions) cohérentes entre
  les quatre manuels.
- Mettre à jour `ETAT_COLLECTION.md` après chaque état des lieux et après chaque changement de
  phase significatif.
