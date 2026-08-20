# PRE-A6 — forensique de `--validate-model`

## Conclusion

Au SHA A5 autoritaire
`761508d923d74fd3d93fc055b3f3b1857fb251e1`, la commande
`python scripts/inventory_collection.py --validate-model` retourne `rc=6` et
exactement neuf blockers. Les neuf failures appartiennent exclusivement à
`ID_MIGRATION_FINGERPRINT_DRIFT`.

Il ne manque aucune décision humaine : chacun des neuf objets possède une
qualification historique `open_debt`, humaine, individuelle et toujours
bloquante sous son fingerprint AGT. Le commit
`2c100f0dab1a9cf67fb1a553f5fb501664e68cf7` (`[FIX] resolve all 132 genuinely
new anomalies (A0 complete)`) a migré les chemins AGT vers APT sans fournir au
validateur une bijection d'identité versionnée. Sept sources sont
byte-identiques ; deux autres sont le résultat exact et exclusif de la
substitution d'identifiants `1NSI-AGT-` vers `1NSI-APT-`.

L'action autorisée est donc la déclaration mécanique des neuf bijections,
avec vérification fail-closed de leurs preuves. L'ancien record reste l'unique
qualification humaine persistée. Aucune approbation, signature, décision,
baseline, disposition, promotion ou dette métier n'est créée ou modifiée par
cette forensique.

## Autorités scellées

- Baseline : `audit/ANOMALIES_BASELINE.json`, SHA-256
  `3e9225668121a67c2fdea1248ec420ff16bd3910c8557e3a98df8bb7997250e1`.
- Dispositions : `audit/ANOMALY_DISPOSITIONS.yaml`, SHA-256
  `49595a0f28745eee0b8f080a4cbeb2fa7265a798455f2747a93d9d532635cda6`.
- Politique : `audit/BASELINE_QUALIFICATION_POLICY.yaml`, SHA-256 fichier
  `07d95c5073da77944ab07a3312483fdfda0f43d6f412ee023f3269c770b282d2`,
  `control_digest`
  `sha256:34341425e865bb72129064438631fe3ae9af3a78dd0b647b5b7276bdabee77a9`.
- Décision : `audit/BASELINE_QUALIFICATION_DECISION.md`, SHA-256
  `7266e523a20ed1ca8df6a1f4f21a6bc20a359600a83ad6e616d34b5311946e7b`.
- `policy_id` : `baseline-status-governance-1nsi-2026-08-10`.
- `decision_ref` :
  `audit/BASELINE_QUALIFICATION_DECISION.md#decision-baseline-status-governance-1nsi-2026-08-10`.

La qualification de 2026-08-10 ne comportait pas de liaison à un SHA source :
`source_sha_bound=null` signifie donc « champ absent du record historique »,
et non une valeur inconnue. Les SHA courants complets sont consignés
individuellement dans le JSON.

Pour éviter toute reconstruction implicite, chaque champ JSON
`qualification_record.record` est une copie structurelle verbatim complète du
record YAML historique correspondant, sans ajout ni omission. Le fait
`qualified_in_baseline=true` n'appartient pas à ce record de dispositions : il
est dérivé séparément de `audit/ANOMALIES_BASELINE.json` et se trouve donc dans
`qualification_evidence`, avec sa référence de preuve.

## Neuf failures

### `3352c285c8971a9a`

- Contexte : `1NSI` / `1NSI-ALGO-PARCOURS-TRIS`, objet
  `1NSI-AGT-EVAL-B`, statut `verified`, catégorie `blocking_statuses`.
- Source :
  `NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/evaluations/1NSI-APT-EVAL-B.tex`.
- Qualification : record historique `4686bd1f406b8183`, règle
  `blocking-scientific-object`, owner `direction_scientifique_programme`,
  qualification digest
  `sha256:978ae8e9f8da8d123669f722609eab0f527dbdcf814e80addc1cafa0b371da52`.
- Preuve : ancien et nouveau SHA source
  `sha256:adfec3634e458eb09ba1f0a1cd144b6c2456a3d20907163d46dbb397c5b1ad9c` ;
  renommage de chemin byte-identique.
- Erreur exacte : `policy_gate:qualification active incomplète fp=3352c285c8971a9a: owner/justification/qualification_digest/qualified requis; owner logique inconnu ou absent`.

### `3a8ff3c7649eebf4`

- Contexte : `1NSI` / `1NSI-ALGO-PARCOURS-TRIS`, objet
  `1NSI-AGT-COURS-C2`, statut `verified`, catégorie `blocking_statuses`.
- Source :
  `NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/cours/1NSI-APT-COURS-C2.tex`.
- Qualification : record historique `a4d85ea8ddf56111`, règle
  `blocking-scientific-object`, owner `direction_scientifique_programme`, même
  décision et digest scientifique ci-dessus.
- Preuve : ancien et nouveau SHA source
  `sha256:0d16b34f49524a4a111da74764033e471f7ecbbdec86ed5d9026c710468f4d7d` ;
  renommage de chemin byte-identique.
- Erreur exacte : `policy_gate:qualification active incomplète fp=3a8ff3c7649eebf4: owner/justification/qualification_digest/qualified requis; owner logique inconnu ou absent`.

### `4efbac4c9cd5b38e`

- Contexte : `1NSI` / `1NSI-ALGO-PARCOURS-TRIS`, objet
  `1NSI-AGT-COURS-C1`, statut `verified`, catégorie `blocking_statuses`.
- Source :
  `NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/cours/1NSI-APT-COURS-C1.tex`.
- Qualification : record historique `b1b11f28b3c73674`, règle
  `blocking-scientific-object`, owner `direction_scientifique_programme`, même
  décision et digest scientifique ci-dessus.
- Preuve : ancien et nouveau SHA source
  `sha256:f0735348410aab8f6243d724873a313abe6b001eab6fd497ebaec0359002f44c` ;
  renommage de chemin byte-identique.
- Erreur exacte : `policy_gate:qualification active incomplète fp=4efbac4c9cd5b38e: owner/justification/qualification_digest/qualified requis; owner logique inconnu ou absent`.

### `5dd488a33d09ff85`

- Contexte : `1NSI` / `1NSI-ALGO-PARCOURS-TRIS`, objet
  `1NSI-AGT-COURS-C3`, statut `verified`, catégorie `blocking_statuses`.
- Source :
  `NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/cours/1NSI-APT-COURS-C3.tex`.
- Qualification : record historique `e3f94eee205675b2`, règle
  `blocking-scientific-object`, owner `direction_scientifique_programme`, même
  décision et digest scientifique ci-dessus.
- Preuve : ancien et nouveau SHA source
  `sha256:c9c390760e1ab5fbdf83b3957a2ba8a620ed878a6543944c3d090f55562eb257` ;
  renommage de chemin byte-identique.
- Erreur exacte : `policy_gate:qualification active incomplète fp=5dd488a33d09ff85: owner/justification/qualification_digest/qualified requis; owner logique inconnu ou absent`.

### `64d302027bb8d49d`

- Contexte : `1NSI` / `1NSI-ALGO-PARCOURS-TRIS`, objet
  `1NSI-AGT-EVAL-A-corrige`, statut `verified`, catégorie `blocking_statuses`.
- Source :
  `NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/evaluations/1NSI-APT-EVAL-A-corrige.tex`.
- Qualification : record historique `760dd470d22f772c`, règle
  `blocking-scientific-object`, owner `direction_scientifique_programme`, même
  décision et digest scientifique ci-dessus.
- Preuve : ancien et nouveau SHA source
  `sha256:5c6f12a93f6582b8b3bd44d8335dbdb9b8e0c91b3d4d87acfee1c734f59a4f37` ;
  renommage de chemin byte-identique.
- Erreur exacte : `policy_gate:qualification active incomplète fp=64d302027bb8d49d: owner/justification/qualification_digest/qualified requis; owner logique inconnu ou absent`.

### `685b5345a7a14d3a`

- Contexte : `1NSI` / `1NSI-ALGO-PARCOURS-TRIS`, objet
  `1NSI-AGT-EVAL-A`, statut `verified`, catégorie `blocking_statuses`.
- Source :
  `NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/evaluations/1NSI-APT-EVAL-A.tex`.
- Qualification : record historique `0af04017fed4737f`, règle
  `blocking-scientific-object`, owner `direction_scientifique_programme`, même
  décision et digest scientifique ci-dessus.
- Preuve : ancien et nouveau SHA source
  `sha256:0c216601ab2a8d9cebb4ef09aec707f5073185e27a4fbd26931fd37596b5db03` ;
  renommage de chemin byte-identique.
- Erreur exacte : `policy_gate:qualification active incomplète fp=685b5345a7a14d3a: owner/justification/qualification_digest/qualified requis; owner logique inconnu ou absent`.

### `6dbdcc7ea0c5b104`

- Contexte : `1NSI` / `1NSI-ALGO-PARCOURS-TRIS`, objet
  `1NSI-APT-RE-C5-CORRIGE`, statut `needs_review`, catégorie
  `blocking_statuses`.
- Source :
  `NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/corriges/1NSI-APT-RE-C5-CORRIGE.tex`.
- Qualification : record historique `2e10a1fa5e61ca58`, règle
  `blocking-scientific-object`, owner `direction_scientifique_programme`, même
  décision et digest scientifique ci-dessus.
- Preuve : SHA historique
  `sha256:c15090d52c458d895c253ae000c98f1585bc54e2177152681c7c73142684fb14`,
  SHA courant
  `sha256:46187cd4cdb10b837f602044dc7c2dbc2cb1bd5b5e1a582b04e4e7ce9d464583` ;
  trois substitutions exactes du token `1NSI-AGT-` vers `1NSI-APT-`, aucune
  autre différence.
- Erreur exacte : `policy_gate:qualification active incomplète fp=6dbdcc7ea0c5b104: owner/justification/qualification_digest/qualified requis; owner logique inconnu ou absent`.

### `8c73d69a6c3f46c4`

- Contexte : `1NSI` / `1NSI-ALGO-PARCOURS-TRIS`, objet
  `1NSI-AGT-EVAL-B-corrige`, statut `verified`, catégorie `blocking_statuses`.
- Source :
  `NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/evaluations/1NSI-APT-EVAL-B-corrige.tex`.
- Qualification : record historique `e0ba62172b638934`, règle
  `blocking-scientific-object`, owner `direction_scientifique_programme`, même
  décision et digest scientifique ci-dessus.
- Preuve : ancien et nouveau SHA source
  `sha256:40bfda001c262c1dccdb5a1b44f6aafecc8b9177860c7a4d6fd5020255d8c85e` ;
  renommage de chemin byte-identique.
- Erreur exacte : `policy_gate:qualification active incomplète fp=8c73d69a6c3f46c4: owner/justification/qualification_digest/qualified requis; owner logique inconnu ou absent`.

### `9bc05524d4ef9a01`

- Contexte : `1NSI` / `1NSI-ALGO-PARCOURS-TRIS`, objet
  `1NSI-APT-RE-C5`, statut `verified`, catégorie `blocking_statuses`.
- Source :
  `NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/remediation/1NSI-APT-RE-C5.tex`.
- Qualification : record historique `ac9ea077ad841eeb`, règle
  `blocking-pedagogical-object`, owner
  `direction_editoriale_pedagogique`, qualification digest
  `sha256:2e2ab865f9b5141ca050e8e62a5df4327c7ef24f897f8d1c013feb2f49e45e57`.
- Preuve : SHA historique
  `sha256:40201779826e9d1f092ca6cb302a9b5f28bfc455dcf770c481678f1a04800c49`,
  SHA courant
  `sha256:1e5d23218d314c33f11c543ff6869dba51391b6582c6021a12cb6ab9d61c38e1` ;
  deux substitutions exactes du token `1NSI-AGT-` vers `1NSI-APT-`, aucune
  autre différence.
- Erreur exacte : `policy_gate:qualification active incomplète fp=9bc05524d4ef9a01: owner/justification/qualification_digest/qualified requis; owner logique inconnu ou absent`.

Pour les neuf cas : `qualification_type` vaut
`HUMAN_APPROVED_OPEN_DEBT_STATUS_GOVERNANCE`, `root_cause` vaut
`ID_MIGRATION_FINGERPRINT_DRIFT`, `first_known_bad_checkpoint` vaut
`2c100f0dab1a9cf67fb1a553f5fb501664e68cf7`, et l'action vaut
`REGISTER_EXACT_BIJECTIVE_IDENTITY_MIGRATION_WITHOUT_NEW_HUMAN_QUALIFICATION`.

## Invariants

- Somme des classes : `9`.
- Fingerprints historiques uniques : `9`.
- Fingerprints courants uniques : `9`.
- Bijection : `YES`.
- Décisions humaines requises : `0`.
- Nouvelle qualification humaine : `NO`.
- Baseline modifiée : `NO`.
- Dispositions modifiées par cette forensique : `NO`.
- Promotions de statut : `0`.
- Records historiques embarqués verbatim : `9/9`.
- Preuves de qualification baseline séparées des records : `9/9`.
- `UNKNOWN` : `0`.

Le détail machine exhaustif, y compris les champs demandés pour chaque
failure, est l'autorité de ce rapport :
`audit/PRE_A6_VALIDATE_MODEL_FORENSICS.json`.
