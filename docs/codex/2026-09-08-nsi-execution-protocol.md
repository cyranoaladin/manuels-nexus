# Vérificateur NSI : preuves d’exécution bornées

Observation de développement du 2026-09-08, base Git
`31ccdf5585faac52701f8faafa60e949412045a0`, avec modifications de travail.
Cette note n’est ni une certification du HEAD, ni une revue scientifique du
corpus, ni une approbation humaine. Aucun receipt du corpus NSI n’a été réécrit.

Le protocole `NSI_EXECUTED_CLAIMS_V1` remplace le crédit fondé sur un code retour
nul ou sur Ruff seul. Chaque bloc VERIFY doit effectivement atteindre une
assertion et terminer normalement ; une assertion fausse absorbée reste un
échec. Chaque TRACE doit terminer normalement et reproduire exactement les
espaces imprimés ; seul le dernier terminateur de ligne absent du bloc TeX est
admis. Les blocs mal formés ne disparaissent pas du périmètre. Un chapitre absent ou
vide renvoie un échec explicite ; le test de syntaxe CLI utilise `--help` et ne
confond plus acceptation de `--check` avec vérification d’un corpus inexistant.
La liste des sources est triée et figée avant exécution ; le set final doit
être identique. Une source ajoutée ou retirée pendant l’exécution donne un échec
de périmètre explicite.

Les listings doivent correspondre par AST à une source `.py` explicitement
référencée dans leur objet. Les sources sont résolues localement, confinées à
NSI, sans accès réseau ; absence, ambiguïté, référence mal formée et différence
restent visibles. La position d’un marqueur ne décide pas de la liaison : un
encadré `codereference` peut séparer la référence du listing. Chaque listing est
vérifié individuellement. Les dépendances Python et les listings doivent aussi
être liés par AST à un programme VERIFY/TRACE effectivement exécuté, faute de
quoi le verdict reste `manual_review`.

Cette liaison prouve la présence des mêmes instructions dans le programme
chargé. Elle ne prouve pas qu’un corps de fonction a été appelé, que toutes les
branches ont été parcourues, ni que l’algorithme est généralement correct. Les
assertions choisies, les cas frontières, les explications et les affirmations
historiques nécessitent leurs revues distinctes. Les receipts déclarent
`certifies_documentary_claims=false` et
`certifies_complete_program_correctness=false`.

Le sandbox existant de `review_1nsi_content.py` est réutilisé : bwrap sans réseau,
interpréteur isolé, ressources et durée bornées par systemd. Aucun fallback
moins confiné n’est ajouté. Les reçus enregistrent les empreintes du vérificateur,
du helper, de common, du sandbox et des sources Python. Le consumer reconstruit
ces ensembles et refuse les anciennes méthodes, les entrées manquantes et les
empreintes périmées. Une source identique peut rester `CURRENT_BOUND` avec une
méthode non fiable ; elle ne reçoit alors aucun crédit scientifique courant.
La source observée n’est pas remplacée dans le receipt par le digest d’un texte
modifié après exécution. Les receipts JSON illisibles du dashboard sont visibles.

Périmètre de code :

- `NSI/scripts/verify_python.py` et `NSI/scripts/execution_protocol.py` ;
- `scripts/scientific_receipt_binding.py` ;
- `scripts/review_1nsi_content.py` (chargement isolé et cache invalidé par le helper) ;
- `scripts/chapter_readiness.py` (receipt illisible explicite) ;
- tests `NSI/tests/test_verify_python_protocol.py`,
  `NSI/tests/test_1nsi_content_reviews.py`, `NSI/tests/test_verify_python.py`,
  `tests/test_current_scientific_receipt_binding.py`.

L’inventaire statique des fichiers effectivement parcourus par ce vérificateur
compte 520 TeX, 542 blocs VERIFY, 43 TRACE, 448 listings et 15 références Python
explicites. Il observe 436 listings sans source Python explicite identique,
répartis sur 309 objets, zéro marqueur mal formé et zéro revue scientifique
réalisée par cet inventaire. Ce sont des observations de liaison à réconcilier,
pas 309 défauts scientifiques démontrés, ni un décompte des objets canoniques.
Les sources `.py` éventuellement présentes mais non référencées ne sont pas
inférées à partir de leur nom. Rapport local avec digests des 520 entrées :
`/tmp/nexus_nsi_execution_scope.json`, SHA256
`cf5647d4ab6bd0d7b7c7908a558ff54f44fbeaf40b71cf6f3c3144eb6715a26f`.
Le script de capture local est `/tmp/nexus_nsi_execution_scope.py` ; il ne lance
aucun code du corpus. Ces chemins temporaires ne sont pas des preuves de release.

Validation ciblée : 64 + 7 = 71 tests passés ; aucun skip ou xfail dans ces deux
sélections. Les 173 tests désélectionnés par `-k` ne sont pas déclarés exécutés.
Les mutations ont d’abord reproduit les défauts (import seul, assertion non
atteinte, exception absorbée, fin anticipée, espaces TRACE, absence de fichier
publié, référence mal formée, dépendance modifiée, digest de méthode périmé,
source modifiée après exécution, bloc ignoré, chapitre absent ou vide, ajout ou retrait de source pendant la vérification). Les tests de confinement vérifient
réseau absent, dépôt hôte inaccessible et collecte des processus après timeout.
Commandes depuis la racine du dépôt, Python 3.12.3 :

```bash
python -m pytest NSI/tests/test_verify_python_protocol.py NSI/tests/test_verify_python.py tests/test_current_scientific_receipt_binding.py tests/test_manual_assembler_import_isolation.py -q
python -m pytest NSI/tests/test_1nsi_content_reviews.py -q -k 'verifier_and_receipt_schema_are_loaded or verifier_cache_is_invalidated or check_object_uses_confined_ruff or execution_observation_reruns or confined_python_cannot_write_outside or confined_python_has_no_network or confined_python_timeout_collects'
ruff check --select F,E9 NSI/scripts/execution_protocol.py NSI/scripts/verify_python.py scripts/scientific_receipt_binding.py scripts/review_1nsi_content.py NSI/tests/test_verify_python_protocol.py NSI/tests/test_verify_python.py tests/test_current_scientific_receipt_binding.py
git diff --check
```

Les anciennes files signées, les validations historiques et les corpus NSI
restent inchangés. La réexécution du corpus doit suivre sa lecture et ses revues,
avec les ressources requises, et ne peut hériter automatiquement de ces tests
du vérificateur.

Contre-revue indépendante du parent `/root` : les dix fichiers du lot ont
été lus, y compris les mutations de dépendances et de population. Les deux
commandes ciblées ci-dessus ont été exécutées par le parent : 64 tests passent
en 5,46 s, puis 7 contrôles de confinement et de consumers passent en 1,44 s
(173 désélectionnés). Ruff et le contrôle du diff passent. Les limites sur
les corps de fonctions, les branches et les affirmations documentaires sont
conservées ; aucun résultat de corpus ni accord humain n’en est déduit.
