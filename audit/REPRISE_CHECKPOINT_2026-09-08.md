# Checkpoint de reprise — 8 septembre 2026

Observation initiale, antérieure aux mutations de cette reprise. Aucun verdict
de publication ni approbation humaine. Les preuves recalculées se rapportent à
`6da7f7637e34a3f7f4aba91eb765ee92ce7fc1d9`, pas au commit portant ce rapport.

```text
HEAD_SHA = 6da7f7637e34a3f7f4aba91eb765ee92ce7fc1d9
BRANCH = codex/t3-publish-readiness-current
UPSTREAM = absent
WORKTREE_STATUS = clean (tracked et untracked)
UNPUSHED_COMMITS = 1341 absents des refs distantes locales connues ; aucun fetch
CONCURRENT_PROJECT_PROCESSES = aucun build/test préexistant identifié
STASHES = 2, conservés
WORKTREES = 2, conservés
DISK_AVAILABLE = 99 GiB environ

CURRENT_CANONICAL_CHAPTERS = 52
CURRENT_PEDAGOGICAL_OBJECTS = 3445 (inventaire suivi : 3441)
ASTRA_CHAPTER_DIRS = 51
CHAPTER_SET_DELTA = uniquement NSI/chapitres/TNSI-PROJET dans HEAD courant
CURRENT_REQUIRED_DELIVERABLES = 24 (12 éditions + 12 auxiliaires ; 4 optionnels exclus)

PROGRAM_EVIDENCE_MISSING_SOURCE = 23 occurrences / 20 atomes / 12 chemins
PROGRAM_EVIDENCE_FALSE_MISSING_FRAGMENT = 2 références #Q3
CURRENT_RECEIPTS_REFERENCING_RETIRED_OBJECTS = 0 pour les 4 reçus signalés ; périmètre global en qualification
HISTORICAL_RECEIPTS_FOR_RETIRED_OBJECTS = 4 reçus SymPy signalés, conservés dans Git
RECEIPT_EVIDENCE_REUSED_FOR_REPLACEMENT_CONTENT = 0 pour ces 4 empreintes
OTHER_RETIRED_SOURCE_RECEIPTS = 3 similarity, historique prouvé ; consommation courante à contrôler

SECOND_DEGREE_CONTRACT_CAPACITIES = 8
SECOND_DEGREE_OFFICIAL_ATOMS = 5
SECOND_DEGREE_MAPPING_STATUS = 5 alias + 3 facettes ; jointure entre espaces d'identité défectueuse
SECOND_DEGREE_OFFICIAL_ARBITRATION_REQUIRED = non établi, aucune modification d'atome nécessaire identifiée

CURRENT_REVIEW_INDEX_STATUS = absent ; partition antérieure échoue sur divergence d'inventaire
NEW_AUTHORING_REVIEW_PENDING = 294 (artefact suivi : 290)
NON_FORMALIZABLE_REVIEW_PENDING = 207 sur 417 objets
REVIEW_QUEUE_PATH_INTERSECTION = 0
REVIEW_QUEUE_PATH_UNION = 501
DISTINCT_TEXTS_TO_REVIEW = 488 corps normalisés candidats ; 13 rapprochements à vérifier, aucun héritage accordé

CURRENT_CROSS_MANUAL_CONTAMINATION = 0 selon détecteur exécuté
RETIRED_SYNTHETIC_BODIES_STILL_IN_CURRENT_CHAPTER_SOURCES = 0
REUSED_RETIRED_IDS_WITH_DIFFERENT_CONTENT = 218 (212 anciens chemins réutilisés)
UNRESOLVED_CLONE_GROUPS = 5 near-clones ; 6 groupes de satellites déjà qualifiés à recontrôler

VALIDATION_ARTIFACTS_TOTAL = 4788 JSON sous validations des chapitres
VALIDATION_BOUND_CURRENT = 3354
VALIDATION_STALE = 1431 (dont 1430 sans empreinte source suffisante et 1 empreinte modifiée)
VALIDATION_HISTORICAL = 3
VALIDATION_UNBOUND = 0 après liaison forensique, sans convertir les preuves périmées en courantes

ASTRA_CONTROLS_TOTAL = 273 IDs uniques (120 transversaux + 153 ciblés)
ASTRA_CONTROLS_MAPPED = NON_VERIFIE ; delta détaillé en construction
ASTRA_CONTROLS_OBSOLETE = NON_VERIFIE
ASTRA_CONTROLS_PARTIAL = NON_VERIFIE
ASTRA_CONTROLS_NOT_COVERED = NON_VERIFIE
ASTRA_CONTROLS_DEFERRED_RELEASE_PHASE = NON_VERIFIE

PEDAGOGICAL_VERDICT_RECALCULATED = 50 ADEQUATE + 2 STRONG
PEDAGOGICAL_SEMANTIC_CERTIFICATION = non acquise par ce calcul
METHOD_ORACLES_EXPECTED = 100 fichiers / 100 blocs (98 annoncé antérieurement)
METHOD_ORACLES_OUTSIDE_VERIFIER_DIRECTORIES = 0
TARGETED_INITIAL_TESTS = 13 passed / 5 failed / 0 skipped
FULL_SUITE = non lancée ; sources à corriger avant cette phase
PUBLISH_READY = false
```

Méthodes : `build_inventory(require_git_provenance=True)` exécuté depuis
l'arbre propre ; producteurs `build_chapter_pedagogical_verdict`,
`build_release_deliverable_scope_matrix`, `build_new_authoring_review_debt`,
`build_non_formalizable_review_closure` et `build_clone_disposition_ledger`
appelés sans remplacer leurs sorties suivies. Recalcul contamination et 19
fixtures de normalisation exécutés. Inventaires de validation liés par champs
internes, références et historique Git, pas par seul nom de fichier.

Le supplément de quatre objets est constitué de `1SPE-SECDEG-ME-007`,
`1SPE-SECDEG-ME-008`, `1SPE-SECOND-DEGRE-RE-C7` et
`1SPE-SECOND-DEGRE-RE-C8`. Les 488 condensés servent à préparer les lectures :
ils ne certifient ni équivalence contextuelle ni fermeture scientifique.

Le supplément de chapitre est prouvé par `NSI/manifests/books/TNSI.json`,
`NSI/chapitres/TNSI-PROJET/contrat.yaml` et l'introduction
`59ace02250cde120ac36911f453b0a3f0da3efaa`. Astra reste externe et inchangé.
Les 973 corps antérieurs au retrait ont été comparés aux sources actuelles ;
une réutilisation d'identifiant ne permet jamais de réutiliser leur revue.

Défauts scientifiques ouverts lors de cette lecture : accroche de boîte cubique
présentée comme quadratique dans le contrat du second degré ; preuve du
discriminant ne traitant pas correctement `a<0` ; frontière pédagogique de la
forme canonique à corriger ; condition `pgcd(a,n) | b` manquante en remédiation
des congruences ; domaine non précisé dans `PGCD(n,0)=n`. Ces constats
interdisent d'extrapoler une clôture produit depuis les compteurs structurels.

Tests initiaux : `python -m pytest -q --import-mode=importlib
tests/test_sympy_receipt_binds_its_source.py tests/test_human_review_kit.py`.
Les cinq échecs portent le kit humain. Leur qualification distingue la
nécessité de relire, les assertions anciennes et une possible perte de
décisions de barème ; aucun seuil, test ou verdict humain n'a été modifié.

Chutes : catalogue accessible ; smoke test sans donnée de corpus refusé
HTTP 402 (quota). Aucune expertise Chutes n'est revendiquée.

La suite poursuit la forensique manquante et les corrections déterminables.
Ce checkpoint ne constitue pas le rapport de convergence avant freeze.
