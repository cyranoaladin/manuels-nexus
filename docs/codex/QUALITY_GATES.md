# QUALITY GATES — Manuel 1SPE

## Gate G0 — Dépôt

- [ ] branche dédiée
- [ ] HEAD consigné
- [ ] WIP audité
- [ ] aucun diff non expliqué
- [ ] `git diff --check` vert

## Gate G1 — Modèle

- [ ] JSON valide
- [ ] YAML valide
- [ ] schémas valides
- [ ] IDs uniques
- [ ] références résolues
- [ ] corrections liées
- [ ] manifests cohérents
- [ ] provenance complète

### Qualification et baseline de dette

- `disposition_coverage` contrôle la politique approuvée, son empreinte, le
  registre matérialisé, les propriétaires, les dispositions et les rapports
  `UNQUALIFIED_ANOMALIES.{json,md}` ; il n’existe pas de précondition parallèle
  contournable.
- Le `qualification_digest` canonique couvre propriétaire, justification,
  cause, approbateur, décision, preuve, règle et empreinte de politique. Sa
  modification à fingerprint brut inchangé est une régression pour
  `--fail-on-new`.
- La matérialisation est une opération locale explicite et ponctuelle. La CI
  n’exécute ni `--materialize-baseline-qualifications` ni
  `--update-baseline`; une anomalie future reste non qualifiée et bloquante.
- Après le gel, une disparition est une amélioration non bloquante et reste
  dans l’historique ; une réapparition `fixed` ou une substitution à total
  constant échoue.

## Gate G2 — Mathématiques

- [ ] zéro P0
- [ ] assertions symboliques
- [ ] valeurs numériques vérifiées
- [ ] QCM/corrigés cohérents
- [ ] démonstrations revues
- [ ] résolution aveugle
- [ ] seconde revue indépendante
- [ ] mutations détectées

## Gate G3 — Programme

- [ ] matrice officielle complète
- [ ] édition 2026-2027 explicite
- [ ] aucune notion future exigible
- [ ] approfondissements signalés
- [ ] listes Python couvertes
- [ ] statistiques/simulations couvertes
- [ ] épreuve anticipée couverte
- [ ] validation humaine

## Gate G4 — Pédagogie Nexus

Pour chaque capacité :

- [ ] diagnostic
- [ ] orientation
- [ ] cours essentiel
- [ ] exemple expert
- [ ] guidage estompé
- [ ] entraînement
- [ ] preuve de maîtrise
- [ ] remédiation
- [ ] re-test
- [ ] réactivation
- [ ] transfert

## Gate G5 — Python

- [ ] source `.py`
- [ ] `ast.parse`
- [ ] exécution
- [ ] sorties comparées
- [ ] aucun caractère invalide
- [ ] cas limites
- [ ] terminaison
- [ ] lint

## Gate G6 — Variantes

- [ ] élève sans corrigé
- [ ] professeur complet
- [ ] aucun ID interne élève
- [ ] aucun placeholder
- [ ] diff d’inclusion archivé

## Gate G7 — LaTeX et visuel

- [ ] zéro référence indéfinie
- [ ] zéro overflow non approuvé
- [ ] zéro collision
- [ ] ouvertures robustes
- [ ] en-têtes corrects
- [ ] taille minimale
- [ ] planche-contact
- [ ] revue visuelle 100 %

## Gate G8 — PDF

- [ ] métadonnées
- [ ] signets
- [ ] liens
- [ ] sommaire cliquable
- [ ] polices incorporées
- [ ] aucun glyphe manquant
- [ ] ordre de lecture contrôlé
- [ ] préflight numérique
- [ ] préflight imprimeur
- [ ] épreuve papier

## Gate G9 — Reproductibilité

- [ ] clone propre
- [ ] environnement figé
- [ ] deux builds
- [ ] manifests observés
- [ ] checksums
- [ ] artefacts CI

## Gate G10 — Release

- [ ] `--validate-model` vert
- [ ] `--fail-on-new` vert
- [ ] `--release-strict` vert
- [ ] approbations humaines
- [ ] PR relue
- [ ] SHA figé
- [ ] tag immuable
- [ ] notes de release
