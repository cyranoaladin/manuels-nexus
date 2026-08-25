# Qualification temporaire exacte des 13 dettes résiduelles — Conception

## Autorité et portée

La décision humaine du 25 août 2026 autorise uniquement la qualification de
non-régression des treize fingerprints listés dans
`audit/RESIDUAL_TRUE_NEW_FORENSICS.json`. Le SHA source autorisé est
`0543df60f4931f0e9e24ce23a9635f203f3a3a53` et le digest du set est
`sha256:1abe51ad406752b1e09996020c1afb2db3982ac2741cf98ed7b2118f302ace98`.

La qualification conserve `open_debt=true`, `release_acceptance=false`,
`publish_approved=false`, les statuts sources non approuvés et les propriétaires
canoniques. Elle ne modifie aucun contenu, aucun oracle D7 et aucune sévérité.

## Architecture

Le workflow existant reste l'unique producteur : politique de qualification,
matérialisation canonique des dispositions, inventaire, puis
`--update-baseline --allow-approved-baseline-extension`. Le jeu
`approved_set` représente uniquement les treize vraies nouvelles dettes. Les
neuf changements d'identité déjà approuvés restent décrits séparément par
`approved_transition`; ils ne sont pas ré-approuvés par cette décision.

Le contrôle de transition compare donc le jeu approuvé au sous-ensemble
`comparison.new`, après retrait des côtés nouveaux des paires de migration.
Les côtés nouveaux des migrations restent vérifiés par la liste et le digest
exacts de `approved_transition`.

## Verrous

- Précondition déjà observée avant toute écriture : HEAD exact, worktree propre,
  `CURRENT_ACTIVE=2232`, set vrai nouveau exact de treize éléments.
- La politique porte la liste nominative triée, son nombre et son digest.
- Toute wildcard, duplication, omission, quatorzième empreinte ou dérive de
  source/modèle est refusée.
- La baseline finale contient toujours 2232 dettes actives : la gouvernance
  change, pas l'existence métier.
- `release-strict` doit continuer à compter les treize objets comme bloqueurs.

## Artefacts

- décision et politique canoniques ;
- registre et dispositions générés ;
- baseline générée par le workflow autorisé ;
- `audit/BASELINE_RESIDUAL_13_EXACT_DIFF.{json,md}` ;
- `audit/RESIDUAL_13_SUNSET_LEDGER.{json,md}`.

## Tests

Les mutations couvrent le set exact, un quatorzième fingerprint, une
qualification manquante, une mutation de source, `release_acceptance=true`, un
statut `approved` sans reçu, une anomalie structurelle et une wildcard. Après
matérialisation : `validate-model=0`, `fail-on-new=0` et `release-strict` reste
rouge avec une relation de blocage explicite pour les treize objets.
