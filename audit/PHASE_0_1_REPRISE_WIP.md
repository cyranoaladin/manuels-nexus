# Audit de reprise du WIP — Phase 0.1

Date de l'audit : 2026-07-21
Branche : `finalisation/collection-v1`
HEAD de départ : `f500166605d0891e148511a9c124fda9769c5f85`

## Périmètre et règles de conservation

L'audit porte sur les deux modifications locales héritées suivantes, laissées
intactes et non stagées pendant l'analyse :

- `scripts/inventory_collection.py` : 1 184 ajouts, 51 suppressions ;
- `scripts/inventory_graph.py` : 7 ajouts, 1 suppression.

Aucune restauration, suppression, substitution, mise au stash ou opération de
réécriture Git n'a été effectuée.

## Contrôles de démarrage

Les commandes imposées ont été exécutées avant toute modification :

```text
git status --short --branch
git diff --stat
git diff -- scripts/inventory_collection.py
git diff -- scripts/inventory_graph.py
git diff --check
```

Constats :

- seuls les deux fichiers annoncés étaient modifiés ;
- `git diff --check` ne signalait aucune erreur d'espacement ;
- les deux modules compilaient avec `python -m py_compile` ;
- Ruff signalait deux imports inutilisés (`PurePath`, `Callable`) ;
- la CLI exposait encore uniquement `--strict`, pas les cinq gates demandées.

Référence comportementale : un export du HEAD, placé dans un dépôt Git
temporaire, passe les 73 tests de `tests/test_inventory_collection.py`. Le WIP
hérité n'en passe que 37 sur 73 : 36 régressions sont donc imputables aux
modifications locales.

### Liste exhaustive des 36 tests cassés

#### Groupe A — ingestion, métadonnées et contrats (11)

Ces tests échouent directement parce que `content_sources` est vide lorsque le
fichier de rôles est absent :

1. `test_non_string_subtype_is_reported_as_invalid_metadata_without_crashing`
2. `test_subtype_priority_changes_counts_but_preserves_source_taxonomy`
3. `test_build_inventory_aggregates_objects_and_keeps_four_manuals`
4. `test_build_inventory_reports_metadata_ids_and_blocking_statuses`
5. `test_only_explicitly_approved_status_is_publishable`
6. `test_all_math_and_nsi_object_schema_statuses_are_recognized_but_only_approved_publishes`
7. `test_contract_status_vocabulary_is_separate_and_requires_explicit_approval`
8. `test_only_well_formed_contract_capacities_are_counted_and_each_error_is_reported`
9. `test_path_meta_and_contract_context_mismatches_are_explicit`
10. `test_duplicate_capacity_references_are_detected_across_chapters`
11. `test_unknown_chapter_prefix_is_never_silently_ignored`

#### Groupe B — graphes, références et digest (4)

La même absence d'objets vide les index et la fermeture du graphe :

12. `test_reference_graph_reports_missing_correction_and_broken_meta_and_latex_targets`
13. `test_reverse_and_conventional_correction_links_prevent_false_missing_reports`
14. `test_meta_capacity_references_resolve_local_codes_and_report_unknown_ids`
15. `test_source_digest_includes_tracked_targets_reached_by_meta_graph`

#### Groupe C — assemblages, dépendances et PDF (14)

Les assemblages sont analysés, mais ne peuvent plus relier les sources aux
objets de chapitre supprimés en amont :

16. `test_assemblies_follow_ast_globs_and_expose_duplicates_exclusions_and_orphans`
17. `test_manual_assembler_gaps_and_chapters_outside_manual_are_explicit`
18. `test_recursive_static_latex_assembly_counts_duplicates_and_assembles_correction`
19. `test_missing_declared_manual_chapter_is_broken_and_never_covered`
20. `test_exercise_glob_order_places_all_hints_after_primary_exercises`
21. `test_chapter_pdf_attribution_aggregates_pages_and_variants`
22. `test_meta_graph_resolves_capacity_prerequisite_method_and_hint_families`
23. `test_meta_graph_reports_unknown_and_invalid_reference_forms_by_family`
24. `test_method_aliases_use_meta_then_verified_id_suffix_without_positional_fallback`
25. `test_missing_and_duplicate_method_aliases_are_reported`
26. `test_physical_chapter_drives_assembly_even_when_meta_chapter_mismatches`
27. `test_dynamic_assembler_dependencies_are_included_and_missing_ones_are_broken`
28. `test_fstring_documentclass_is_a_dynamic_assembly_dependency`
29. `test_duplicate_chapter_declaration_preserves_multiple_inclusion_and_reports_it`

#### Groupe D — réconciliation et matrice de livraison (7)

Sans chapitres, la résolution des assertions retombe au manuel, les comptes
calculés valent zéro et la matrice annonce `chapter_count=0` :

30. `test_report_claims_reconcile_chapter_table_and_keep_unknown_pages_open`
31. `test_report_claims_flag_numeric_and_completeness_contradictions`
32. `test_report_claim_spanning_multiple_chapters_stays_open`
33. `test_deliverable_matrix_covers_all_mission_variants_and_blocks_publication`
34. `test_deliverable_matrix_blocks_needs_review_and_checks_model_coherence`
35. `test_report_continuation_scope_does_not_leak_after_a_blank_line`
36. `test_real_reports_expose_known_exercise_contradictions`

### Cause racine commune et modifications responsables

La cause immédiate commune aux 36 échecs est l'association de deux changements
dans `scripts/inventory_collection.py` :

1. `_collect_role_patterns()` appelle `_load_yaml_payload(..., default={})`, puis
   n'utilise le fallback historique que si le résultat n'est pas un mapping ;
   `{}` étant un mapping valide, la fonction retourne `patterns={}` et
   `role_order=[]` quand `audit/SOURCE_ROLES.yaml` n'existe pas ;
2. `build_inventory()` filtre désormais chaque source pertinente par
   `_is_production()`. Avec une configuration vide, aucune source n'est retenue.

La vérification locale reproduit précisément cet état :

```text
patterns= {}
default= transversal
order= []
```

Le plus petit correctif restaurant le maximum de tests est donc de faire du
fallback de rôles une constante canonique utilisée lorsque le fichier est absent
ou vide. Ajouter artificiellement le fichier aux fixtures de tests est rejeté :
cela masquerait la rupture de compatibilité du contrat public existant.

### Défauts secondaires actuellement masqués

Après restauration de l'ingestion, les contrôles doivent rechercher en priorité :

- l'ajout inconditionnel de `source` dans les anomalies brutes, susceptible de
  casser les assertions exactes et contraire à leur immutabilité ;
- les signatures incompatibles des trois renderers, déjà reproduites par un
  `TypeError` direct ;
- la validation erronée des fichiers Markdown comme YAML ;
- l'asymétrie de `skipped_path` entre META absent et META invalide ;
- les changements de bloqueurs induits par `missing_corrections` et les
  dispositions ;
- les nouveaux compteurs et la sémantique structure/publication.

### Revue Chutes indépendante

Une revue indépendante a été demandée le 2026-07-22 au modèle Chutes attesté
`unsloth/Mistral-Nemo-Instruct-2407-TEE`, avec température 0, à partir des
extraits de classification, rendu, verrouillage et du résumé des tests, sans
contenu sensible.

La revue confirme :

- la configuration de rôles absente comme cause dominante des 36 échecs ;
- les renderers et la CLI comme défauts secondaires à vérifier ensuite ;
- l'ordre local « classification, tests ciblés, suite historique, autres
  fonctionnalités ».

Elle proposait de créer `SOURCE_ROLES.yaml` dans chaque dépôt temporaire. Cette
recommandation n'est pas retenue après vérification locale, car les 73 tests
historiques spécifient que le générateur fonctionne sans cette nouvelle
configuration. Le correctif doit préserver ce comportement par défaut.

## `scripts/inventory_collection.py`

### 1. Objectif de la modification

Le WIP tente de couvrir une grande partie de la Phase 0.1 en une seule
modification :

- chargement sûr JSON/YAML et validation d'artefacts ;
- classification des sources et dispositions d'anomalies ;
- baseline d'anomalies et empreintes ;
- provenance Git et empreinte du générateur ;
- sécurisation des chemins, verrou, écritures groupées avec sauvegardes ;
- ajout de `missing_corrections` aux catégories bloquantes ;
- distinction entre éligibilité structurelle et publication ;
- exposition des sept dimensions de gates ;
- correction amorcée du nombre d'objets ;
- rendu centralisé des artefacts et préparation de `--check`, de la validation
  du modèle, du contrôle de baseline et de `--require-clean`.

### 2. Degré d'achèvement

État : **partiel, non exécutable de bout en bout et non committable en l'état**.

Les briques suivantes sont présentes et récupérables :

- commentaire généré `# ...`, valide en YAML ;
- appels à `yaml.safe_load` et `json.loads` dans les nouveaux validateurs ;
- ajout de `missing_corrections` aux anomalies bloquantes ;
- champs `phase0_structural_eligible`, `publication_eligible` et matrice des sept
  dimensions ;
- provenance Git, liste des fichiers modifiés/non suivis et empreinte du
  générateur ;
- préparation en mémoire des sorties avant remplacement ;
- sauvegarde et restauration des anciens fichiers si un remplacement échoue ;
- calcul séparé de `object_count` à partir des objets de contenu.

Les éléments suivants sont absents ou inopérants :

- aucun des flags `--check`, `--validate-model`, `--release-strict`,
  `--fail-on-new`, `--require-clean` n'est déclaré par `argparse` ;
- aucun schéma versionné n'existe encore et l'absence du schéma JSON est traitée
  comme un succès ; aucun schéma YAML n'est appliqué ;
- `SOURCE_ROLES.yaml`, `ANOMALY_DISPOSITIONS.yaml` et
  `ANOMALIES_BASELINE.json` ne sont pas créés ;
- le manifeste de build réel, `observed_builds` et la distinction explicite avec
  `declared_assemblies` ne sont pas implémentés ;
- la CI Phase 0.1 n'est pas créée ;
- les helpers de synthèse des anomalies et de baseline sont inutilisés ;
- la CLI conserve l'ancien comportement `--strict`.

### 3. Compatibilité avec la mission Phase 0.1

La direction générale est compatible, mais l'implémentation actuelle ne répond
pas aux critères d'acceptation. Les points à conserver sont les chargeurs sûrs,
la séparation structure/publication, les dimensions de gates, la provenance et
le principe d'écriture transactionnelle. Ils doivent être complétés sous tests
avant activation.

La modification concentre toutefois trop de responsabilités dans un fichier qui
dépasse désormais 3 400 lignes. Les gates, schémas et opérations d'écriture
doivent garder des interfaces testables et explicites, même si une extraction en
modules séparés reste limitée au strict nécessaire pour cette phase corrective.

### 4. Tests manquants

Il manque au minimum des tests pour :

- le fallback de classification lorsque `SOURCE_ROLES.yaml` est absent ;
- la priorité des rôles spécifiques sur les racines de production, notamment
  `_harvest`, `build/maquette-v5/renvois.tex`, fixtures, validations, archives et
  dépendances générées ;
- les schémas versionnés de chaque JSON/YAML et l'échec si un schéma manque ;
- l'égalité du digest exposé par tous les artefacts ;
- les signatures et codes de sortie des cinq gates CLI ;
- les cas sans HEAD, HEAD détaché, dépôt sale et fichiers non suivis pertinents ;
- les chemins absolus, traversées, symlinks de sortie et sorties hors dépôt ;
- deux générations concurrentes, verrou obsolète et timeout ;
- l'échec au milieu d'un lot d'écritures et la restauration byte à byte ;
- la reproductibilité de deux générations ;
- les empreintes d'anomalies lorsque seul le champ `source` distingue deux cas ;
- la baseline : anomalie nouvelle, croissance, disparition, réapparition et
  disposition ;
- le nombre réel d'objets, distinct des capacités et des agrégats de métriques ;
- l'absence de lignes humaines `id=—, detail=—, code=—` ;
- la taille synthétique de `ETAT_COLLECTION.md` ;
- le manifeste d'un build réellement observé et l'absence de déduction abusive
  du contenu final d'un PDF à partir de l'AST ou d'expressions régulières.

### 5. Régressions et défauts observés

#### P0 — génération des artefacts cassée

`build_inventory_artifacts(..., check_only=True)` lève :

```text
TypeError: _render_inventory_markdown() got an unexpected keyword argument 'marker'
```

Le nouveau pipeline appelle les fonctions de rendu avec `marker` et `root`, mais
leurs définitions effectives ont conservé les anciennes signatures. Même après
ce premier défaut, la validation traiterait les fichiers Markdown comme du YAML.

#### P1 — inventaire vidé lorsque la configuration de rôles est absente

`_collect_role_patterns()` charge `{}` par défaut, puis ne déclenche son fallback
que pour une valeur non-mapping. Sans `audit/SOURCE_ROLES.yaml`, la liste des
rôles est donc vide et tous les contenus deviennent `transversal`. Cela explique
les 36 échecs : chapitres, objets, graphes, assemblages et réconciliation sont
vides ou faux.

#### P1 — priorité de classification incorrecte

Le rôle `production_object` est évalué avant les rôles spécifiques. Les fichiers
`NSI/chapitres/**/_harvest/**/*.candidate.tex`, les fixtures ou références sous
une racine de chapitre seraient donc capturés comme production avant d'atteindre
leur rôle spécialisé.

#### P1 — gates annoncées mais non implémentées

Des constantes et paramètres internes existent, mais `argparse` ne les expose
pas et aucun code de sortie ne les applique. `--check` ne peut donc pas protéger
les artefacts, `--release-strict` ne peut pas inventorier ses bloqueurs et
`--fail-on-new` ne peut pas comparer la baseline.

#### P1 — verrouillage incomplet

Le verrou est relâché avant la comparaison et avant `_apply_atomic_payloads`.
Deux processus peuvent ainsi rendre sous verrou puis écrire concurremment. Un
processus tué laisse en outre un verrou permanent, sans PID ni récupération
contrôlée.

#### P1 — reproductibilité non atteinte

La provenance inclut `generated_at_utc`, l'état sale et l'empreinte du fichier
générateur courant. Le WIP ne définit pas de représentation reproductible pour
les artefacts suivis et ne câble pas le helper de normalisation. Une seconde
génération peut donc différer sans changement des sources de contenu.

#### P1 — validation de modèle permissive

L'absence de `audit/inventory_collection.schema.json` retourne zéro erreur. Il
n'existe ni schéma YAML ni validation versionnée commune. Le code ne garantit
donc pas les contrats machine demandés.

#### P1 — empreintes d'anomalies ambiguës

`_anomaly_fingerprint()` exclut systématiquement `source`. Pour les anomalies où
la source est l'identité principale, deux anomalies distinctes peuvent partager
la même empreinte et fausser dispositions et baseline.

#### P1 — rapports humains encore erronés

`_sample_keys()` conserve le fallback `id/detail/code`, responsable des lignes
vides. `_render_inventory_markdown()` calcule encore `Objets` avec
`sum(manual["totals"].values())`. Les rendus de rapports restent exhaustifs et
les nouveaux helpers synthétiques ne sont jamais appelés.

#### P2 — provenance d'outils incorrecte

Le champ nommé `texlive` est alimenté par `git -C <repo> --version` ; il contient
donc la version de Git et non celle de TeX Live. Le champ `git` n'est qu'un
booléen de présence, pas une version.

#### P2 — contrôle `require-clean=head` incomplet

Si le dépôt est propre, `_ensure_clean_tree()` retourne avant de vérifier que le
dépôt est valide, que HEAD existe et qu'il n'est pas détaché. Les modes `head` et
`worktree` sont sinon équivalents sur un dépôt sale.

#### P2 — baseline sémantiquement trop stricte pour `--fail-on-new`

La disparition d'une anomalie non marquée `fixed` est considérée comme un échec.
Un gate nommé `--fail-on-new` doit échouer sur une nouveauté ou une croissance,
pas empêcher une correction ; les dispositions peuvent contrôler séparément les
réapparitions.

### 6. Décision

**Conserver puis corriger et compléter.** La modification ne doit ni être jetée
ni commitée en bloc. Les briques compatibles seront intégrées par cycles TDD,
avec restauration de la compatibilité des 73 tests comme premier jalon, puis
commits atomiques pour schémas/artefacts, rapports, gates, classification,
sécurité, assemblages/manifeste et CI.

## `scripts/inventory_graph.py`

### 1. Objectif de la modification

Le changement ajoute `skipped_path` à `add_orphan_files()` afin d'éviter qu'un
fichier déjà signalé pour erreur de métadonnées soit aussi classé comme orphelin.

### 2. Degré d'achèvement

État : **petit changement fonctionnel, mais intégration incomplète**. Seuls les
chemins ayant levé `MetadataMissingError` sont ajoutés à l'ensemble ignoré ; les
autres `MetadataError` ne le sont pas. Le comportement est donc asymétrique.

### 3. Compatibilité avec la mission Phase 0.1

Le principe est compatible si la politique d'anomalies décide qu'une cause
racine de métadonnées ne doit pas produire un second symptôme `orphan_files`.
Cette politique doit être explicite dans les dispositions et testée, car elle
modifie le nombre de bloqueurs inventoriés.

### 4. Tests manquants

Il manque des tests couvrant :

- un fichier sans META, un META invalide et un fichier réellement orphelin ;
- la présence d'une seule anomalie de cause racine selon la politique retenue ;
- le comportement par défaut lorsque `skipped_path` est omis ;
- l'absence de masquage d'un fichier valide mais non atteignable.

### 5. Régressions potentielles

Le changement peut réduire silencieusement les bloqueurs `orphan_files`. Dans le
WIP actuel, l'asymétrie entre META absent et META invalide produit des comptes
incohérents. La grande régression observée dans les tests provient toutefois de
la classification amont dans `inventory_collection.py`, pas de cette boucle.

### 6. Décision

**Conserver sous réserve de correction et de tests.** Il faut renommer le
paramètre au pluriel (`skipped_paths`), documenter la politique et alimenter
l'ensemble pour toutes les erreurs de métadonnées concernées, ou supprimer ce
filtrage si les tests de modèle établissent qu'un double signalement est requis.

## État des artefacts et rapports au moment de la reprise

- `audit/ECARTS_ET_CONTRADICTIONS.yaml` est invalide : le commentaire HTML de la
  première ligne est suivi d'un mapping et fait échouer `yaml.safe_load` ligne 2 ;
- `audit/MATRICE_LIVRABLES.yaml` se charge correctement ;
- `audit/INVENTAIRE_COLLECTION.json` se charge avec `json.loads` ;
- `ETAT_COLLECTION.md` contient 1 856 lignes et n'est pas synthétique ;
- `audit/AUDIT_CONSOLIDE.md` contient de nombreuses lignes
  `id=—, detail=—, code=—` ;
- aucun schéma versionné, baseline, disposition ou rôle de source demandé n'est
  encore présent ;
- le manifeste de build réel et la CI Phase 0.1 sont absents.

## Verdict de revue

**REQUEST CHANGES — confiance élevée.** Les intentions couvrent utilement la
mission Phase 0.1, mais les régressions P0/P1 empêchent toute génération fiable.
La reprise doit conserver les modifications, les stabiliser d'abord contre la
suite existante, puis compléter les exigences par petits commits testés.

## Stabilisation provenance et transactions — 2026-07-29

La Task 6 a été reprise par cycles RED/GREEN. La provenance emploie désormais le
statut Git NUL (`--porcelain=v1 -z`), conserve sans guillemets les chemins
Unicode ou contenant des espaces, et expose les deux chemins d'un renommage. Les
versions de Python, Git, TeX Live, Latexmk et pdfinfo proviennent chacune de son
exécutable réel. `SOURCE_DATE_EPOCH`, ou à défaut la date du commit, fixe
l'horodatage reproductible.

Le verrou couvre maintenant rendu, validation, comparaison, second contrôle de
propreté et remplacement du lot. Son enregistrement JSON contient PID, jeton de
démarrage du processus et date UTC. Seul un propriétaire mort ou dont le jeton
ne correspond plus, âgé d'au moins 20 secondes, est mis en quarantaine ; un
verrou vivant, jeune ou illisible expire sans être supprimé. Les stages et
sauvegardes utilisent un répertoire privé sous la racine, les symlinks sortants
sont refusés, et un échec de remplacement restaure les cibles préexistantes
octet pour octet sans créer les nouvelles.

| Cause racine | Tests affectés | Fichier | Correction | Test de régression | Statut |
|---|---|---|---|---|---|
| Verrou relâché avant comparaison et écriture | concurrence, TOCTOU, lot partiel | `scripts/inventory_collection.py` | verrou unique sur toute la transaction et second contrôle sous verrou | `test_generation_lock_covers_render_compare_clean_and_apply`, `test_require_clean_generation_ignores_only_its_own_transaction_files` | Corrigé |
| Verrou sans propriétaire ni politique stale | timeout permanent après arrêt brutal | `scripts/inventory_collection.py` | record JSON PID/jeton/date, détection live, quarantaine atomique | `test_live_generation_lock_times_out_without_removing_owner_record`, `test_stale_dead_generation_lock_is_quarantined_once`, `test_malformed_or_young_generation_lock_times_out_unchanged` | Corrigé |
| Écriture et rollback insuffisamment confinés | perte d'anciens artefacts, sortie hors dépôt | `scripts/inventory_collection.py` | validation des cibles, répertoire privé, sauvegardes fsync, rollback typé | `test_generation_rejects_symlink_escape_before_any_write`, `test_atomic_batch_failure_restores_every_target_byte_for_byte`, `test_atomic_staging_failure_leaves_no_temporary_or_target`, `test_atomic_batch_rejects_transaction_directory_symlink_escape` | Corrigé |
| Statut Git textuel ambigu | chemins Unicode/espaces et renommages faux | `scripts/inventory_collection.py` | parsing NUL et représentation structurée des entrées | `test_git_status_preserves_unicode_spaces_and_both_rename_paths` | Corrigé |
| Provenance de `--check` trop largement réutilisée | nouveau source non suivi invisible | `scripts/inventory_collection.py` | réutilisation limitée au SHA et à l'horodatage attestés | `test_check_recomputes_untracked_provenance_instead_of_reusing_stored_status` | Corrigé |
| Versions d'outils et UTC incorrects | fausse preuve de toolchain, warnings | `scripts/inventory_collection.py` | interrogation de chaque exécutable et UTC aware | `test_tool_versions_come_from_each_real_executable`, `test_now_utc_is_timezone_aware_without_deprecation_warning` | Corrigé |

### Correctif de revue de conformité

- La génération d'artefacts exige désormais un dépôt Git exploitable : `HEAD`,
  branche attachée, statut, fichiers suivis et horodatage doivent être
  disponibles. Les inventaires en mémoire conservent leur compatibilité avec un
  dépôt non initialisé, mais déclarent explicitement `git_available: false` et
  des valeurs nulles au lieu d'une fausse propreté.
- Deux générations complètes, lancées dans deux dépôts Git isolés avec le même
  contenu et le même `SOURCE_DATE_EPOCH`, produisent des octets identiques.
- La libération d'un verrou après erreur revalide son inode. Chaque remplacement
  et chaque rollback revalident aussi le confinement des symlinks ; il s'agit
  d'une réduction déterministe de la fenêtre TOCTOU, pas d'une protection
  absolue contre un adversaire privilégié contrôlant le système de fichiers.
- Si un rollback échoue, la sauvegarde récupérable est conservée et son chemin
  est inclus dans l'`InventoryError`, au lieu d'être supprimée au nettoyage.

Tests de conformité ajoutés : échecs des commandes Git, dépôt non Git, dépôt
sans commit, reproductibilité inter-dépôts, remplacement d'inode du verrou,
courses symlink avant remplacement et rollback, sauvegarde après rollback
incomplet, et absence d'affectation morte dans la réutilisation de provenance.
