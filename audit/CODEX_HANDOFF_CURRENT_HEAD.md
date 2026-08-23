# Codex side-car handoff — jalon PROGRAMME + QCM

## Provenance

- Integration branch (lecture seule): `audit/adversarial-reconciliation-2026`
- Integration base SHA: `10cb5f07772842d6630d2a2f78531f6900371023`
- Codex branch: `codex/t2-current-10cb5f0`
- Source SHA soumise aux builds isolés: `75492cf05bcae6c7319e9ec91709e4cc7166e22b`
- Push: aucun
- Merge: aucun
- Baseline/oracle/receipt promu: aucun

## Résultat PROGRAMME

Le dénominateur historique de 333 atoms obligatoires a été rejeté après
réextraction directe et double contrôle des documents officiels. Il omettait des
segments obligatoires et ne pouvait pas servir de preuve publish-ready.

- Segments officiels analysés: 985
- Atoms officiels: 919
- Atoms obligatoires: 596
- Atoms obligatoires structurellement mappés: 596/596
- Atoms `FULL`: 0/596
- `CONTENT_REVIEW_PENDING`: 322
- `STRUCTURALLY_MAPPED`: 274
- Mandatory unmapped: 0
- Wrong year: 0
- Unsupported claims: 0
- Segments obligatoires non parsés: 0
- Duplicates / ambiguïtés d'atoms: 0 / 0

Répartition mandatory mapped:

- 1SPE: 133/133
- TSPE: 155/155
- TCOMPL: 69/69
- TEXPERTES: 74/74
- 1NSI: 87/87
- TNSI: 78/78

Les 274 mappings purement structurels restent explicitement non couverts. Les
contrats transversaux d'audit 1SPE/TSPE qui n'ont pas de source éditoriale portent
`source_content_state: MISSING` et `coverage_claim: NONE`; aucun chemin existant
n'a été assimilé à une validation scientifique ou pédagogique.

Preuves principales:

- `audit/OFFICIAL_SOURCE_SEGMENTS_2026_2027.*`
- `audit/OFFICIAL_PROGRAM_ATOMS_2026_2027.*`
- `audit/OFFICIAL_SOURCE_ATOM_CROSSWALK_2026_2027.*`
- `audit/OFFICIAL_PROGRAM_COVERAGE_2026_2027.*`
- `audit/MANDATORY_UNMAPPED_ATOMS_CLOSURE.*`

## Résultat QCM

- Sources QCM Math: 35
- Questions recomputées indépendamment: 330/330
- Wrong answer key: 0
- Multiple correct options: 0
- No correct option / no unique answer: 0 / 0
- Invalid or generic unjustified diagnostic: 0 / 0
- Wrong capacity / wrong programme year: 0 / 0
- Variant visibility failure: 0
- Unresolved: 0
- État de gouvernance: `HUMAN_APPROVAL_PENDING_NO_AUTO_APPROVAL`

La dette de couverture demeure distincte de cette validation:

- 49 capacités de contrat sans QCM;
- 117 champs de renvoi de remédiation absents dans les distracteurs TSPE.

## Corrections source supplémentaires du jalon

- Reclassification explicite des approfondissements trigonométriques et de la
  loi binomiale 1SPE selon l'arbitrage fourni.
- Correction des faux verts QCM et des diagnostics causaux, avec tests de
  régression indépendants.
- Correction de la définition de l'écart-type et des périmètres probabilités /
  exponentielle.
- Correction de commandes LaTeX tronquées, d'une commande `\attention` non
  définie, d'un diagnostic QCM au mode mathématique non fermé et du libellé
  exponentielle `e^{at}` injecté hors mode mathématique.
- Les 35 clés QCM et les deux barèmes TSPE restent absents des variantes élèves
  et présents dans les variantes professeur par gardes structurelles.

## Science et pédagogie

- Chapitres canoniques actuels: 52 (1SPE 10, TSPE 11, TCOMPL 9,
  TEXPERTES 5, 1NSI 10, TNSI 7).
- Audit scientifique exhaustif de chapitre: 0/52.
- Audit pédagogique exhaustif de chapitre: 0/52.
- Couche QCM Math examinée: 35/35 chapitres Math.

La couverture structurelle et le zéro QCM ne sont donc pas une déclaration de
qualité intégrale ni de publication.

## Charte et runtime

- Registre déterministe courant: PASS.
- Fichiers physiques: 63; contenus uniques: 42.
- Duplicatas exacts: 21 fichiers dans 18 groupes.
- Implémentation canonique classe/style identifiée: oui / oui.
- Runtime sans wrapper de compatibilité: non.
- Wrappers observés: `nexus-charte-v6.sty`, `nexus-manuel-v5.cls` côté Math.
- Chemins non canoniques potentiellement runtime: 16.

## Structure et gouvernance

Le scan structurel courant, avec neutralisation explicite et uniquement
diagnostique du receipt A4 stale et du manifeste de builds stale, donne les neuf
invariants source suivants à zéro:

- context mismatches
- unattributed PDFs
- orphan files
- unassembled objects
- unclassified types
- broken meta references
- broken LaTeX references
- LaTeX cycles
- duplicate assembly objects

Cette mesure ne contourne pas les gates de gouvernance. Ceux-ci restent rouges
sur le receipt A4 obsolète de
`1SPE-TRIGONOMETRIE/methodes/1SPE-TRIGO-ME-005.tex` (fingerprint
`70dfcb9ea3d7e1ec`). Le statut `needs_review` du projet TNSI reste lui aussi
préservé; aucune promotion administrative n'a été faite.

## Tests et gates

- Builders déterministes atoms/crosswalk/coverage/closure/QCM/style: PASS.
- Suite ciblée programme + QCM au source SHA: 81 passed.
- Suite NSI complète au SHA source précédent sans changement NSI: 2203 passed.
- Suite Math complète avant le dernier correctif LaTeX: 4844 passed, 22 failed;
  les échecs restants sont 2 inventaires observés stale et 20 oracles D7/maquette
  volontairement non mis à jour.
- Suite racine: 1336 passed, 24 failed, 16 errors; échecs dominés par le receipt
  A4 stale et l'audit PDF suivi stale.
- `validate-model`: rc 6, rouge honnête (receipt A4 stale).
- `fail-on-new`: rc 5, rouge honnête (même receipt stale).
- `release-strict`: non exécuté à ce jalon; il doit rester rouge tant que la
  dette réelle n'est pas fermée.

## Builds et séparation

Les preuves A/B au SHA source exact sont produites hors dépôt dans des
worktrees propres; aucun ancien PDF de `MANUELS_PDF_PUBLICATION` n'est autorité.

- Math run A: 6/8 PASS au dernier relevé; 1SPE professeur et TSPE professeur
  encore actifs. Les quatre variantes élève ont déjà compilé, notamment 1SPE
  après correction des deux bloqueurs LaTeX.
- Math run B: 5/8 PASS au dernier relevé; trois variantes professeur actives.
- NSI 1NSI élève: A/B PASS; 1NSI professeur A/B actifs.
- NSI TNSI: élève et professeur échouent symétriquement A/B au préflight
  pour `Overfull \\hbox` et `Underfull \\hbox`; le diagnostic de lignes exactes
  est ouvert et aucun PDF staging n'a été promu.

La garde source structurée des 35 clés QCM et des deux barèmes reste verte;
le gate PDF global 12/12 reste volontairement non acquis tant que TNSI ne
compile pas et que les comparaisons finales A/B ne sont pas closes.

## Ordre de reprise / dépendances

Le lot contient des changements source, tests et rapports de preuve. Les commits
PDF, inventaire et manifest historiques (`e53365c4`, `a92e46b2`, `abb5eab0`)
ne doivent pas être repris comme artefacts courants: régénérer après intégration
des sources. L'intégrateur doit revalider les changements sémantiques au nouveau
HEAD et appliquer les commits sources/tests dans leur ordre historique.

## État du handoff

Le side-car est prêt pour revue sélective des sources et tests, mais il n'est ni
publish-ready, ni print-ready, ni distribution-ready. Les campagnes science,
pédagogie, langue, fermeture des statuses/receipts, nettoyage runtime, 12 PDF
finaux, visual QA, prépresse, reproductibilité, D7 et métadonnées administratives
restent à exécuter ou à fermer.
