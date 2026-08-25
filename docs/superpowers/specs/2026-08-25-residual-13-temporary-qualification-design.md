# Qualification temporaire exacte des 13 dettes résiduelles — Conception

## Autorité et portée

La décision humaine du 25 août 2026 autorise uniquement la qualification de
non-régression des treize fingerprints listés dans
`audit/RESIDUAL_TRUE_NEW_FORENSICS.json`. Le SHA source autorisé est
`0543df60f4931f0e9e24ce23a9635f203f3a3a53` et le digest du set est
`sha256:1abe51ad406752b1e09996020c1afb2db3982ac2741cf98ed7b2118f302ace98`.

La qualification conserve `disposition=open_debt`, `qualified=true`,
`blocking=true`, `release_blocking=true` et `release_acceptance=false`, ainsi
que les statuts sources non approuvés et les propriétaires canoniques. Elle ne
modifie aucun contenu, aucun oracle D7 et aucune sévérité.

## Architecture

Le workflow existant reste l'unique producteur : politique de qualification,
matérialisation canonique des dispositions, inventaire, puis
`--update-baseline --allow-approved-baseline-extension`. Le jeu
`approved_set` représente uniquement les treize vraies nouvelles dettes. Les
neuf changements d'identité déjà approuvés restent décrits séparément par
`approved_transition`; ils ne sont pas ré-approuvés par cette décision.

Le contrôle impose donc `approved_set == comparison.new`, exactement. Le jeu
brut des fingerprints courants absents de la baseline se partitionne sans
intersection : `111 = 9 migrations + 89 expected review debt + 13 true new`.
Les neuf côtés nouveaux des migrations restent vérifiés par la liste et le
digest exacts de `approved_transition`.

L'algèbre historique reste elle aussi explicite : 4411 résolutions hors
transitions, plus les neuf anciens côtés des migrations, donnent 4420 entrées
archivées. Les 89 dettes de review et les 4411 résolutions hors transitions
portent chacune leur nombre et leur digest exacts dans la politique.

## Verrous

- État source observé à l'autorisation : HEAD exact, worktree propre,
  `CURRENT_ACTIVE=2232`, set vrai nouveau exact de treize éléments. La
  matérialisation s'effectue sur un descendant ne contenant que la gouvernance
  et les garde-fous, avec le même `source_digest` métier.
- La politique porte la liste nominative triée, son nombre et son digest.
- Le `source_digest` autorisé est revalidé après matérialisation, au probe puis
  sous verrou, immédiatement avant l'écriture de baseline.
- Toute wildcard, duplication, omission, quatorzième empreinte ou dérive de
  source/modèle avant matérialisation est refusée. Après matérialisation, le
  source reste exact et l'algèbre verrouille le modèle, dont le digest change
  légitimement avec les qualifications.
- La baseline finale contient toujours 2232 dettes actives : la gouvernance
  change, pas l'existence métier.
- `release-strict` doit continuer à compter les treize objets comme bloqueurs.

## Artefacts

- décision et politique canoniques ;
- registre canonique `audit/ANOMALY_DISPOSITIONS.yaml` et rapports générés ;
- baseline générée par le workflow autorisé ;
- `audit/BASELINE_RESIDUAL_13_EXACT_DIFF.{json,md}` ;
- `audit/RESIDUAL_13_SUNSET_LEDGER.{json,md}`.

## Tests

Les mutations couvrent le set exact, un quatorzième fingerprint, une
qualification manquante, une mutation de source, `release_acceptance=true`, un
statut `approved` sans reçu, une anomalie structurelle et une wildcard. Après
l'extension canonique : `validate-model=0`, `fail-on-new=0` et
`release-strict` reste rouge avec une relation de blocage explicite pour les
treize objets.
