# Registre des avertissements de dépendances et de l'état d'épinglage

Généré par `scripts/build_dependency_warning_ledger.py` à partir d'une exécution
réelle de la suite complète. Données : `audit/DEPENDENCY_WARNING_AND_PINNING_LEDGER.json`.
Capture brute de la section *warnings summary* :
`audit/DEPENDENCY_WARNING_CAPTURE.txt`.

**Rien n'est modifié.** Conformément à la décision de gouvernance, aucune version
n'est changée pendant la wave de contenu ; la fermeture est planifiée **avant
`FINAL_SOURCE_SHA`**.

## 1. Les 5 avertissements observés

Exécution : point d'entrée `root_umbrella` sur l'arbre canonique — **9039 passés,
2 échoués, 0 erreur**, **4 warnings + 1 warning post-summary**, en 45 min 27 s.
Voir `audit/TEST_EXECUTION_MATRIX.md`.

Les cinq sont déclenchés par un seul test :
`Mathematiques/manuel-maths/tests/test_retrieval.py::test_topk_contains_type`.

| # | Phase | Catégorie | Origine | Message | Propriétaire | Impact | Résolution |
|---|---|---|---|---|---|---|---|
| 1 | summary | `UserWarning` | `~/.local/.../pandas/core/computation/expressions.py:22` | Pandas requiert `numexpr` ≥ 2.10.2, 2.9.0 installé | **amont** (pandas / numexpr) | pandas retombe sur son évaluateur lent ; aucun effet sur les résultats | épingler `pandas` **et** `numexpr` dans le fichier de contraintes |
| 2 | summary | `UserWarning` | `~/.local/.../pandas/core/arrays/masked.py:56` | Pandas requiert `bottleneck` ≥ 1.4.2, 1.3.5 installé | **amont** (pandas / bottleneck) | accélérations désactivées ; aucun effet sur les résultats | épingler `pandas` **et** `bottleneck` |
| 3 | summary | `DeprecationWarning` | `<frozen importlib._bootstrap>:488` | `SwigPyPacked` n'a pas d'attribut `__module__` | **amont** (extension SWIG) | aucun aujourd'hui ; deviendra une erreur d'import sur une version future de Python | identifier le paquet SWIG et l'épingler à une version corrigée |
| 4 | summary | `DeprecationWarning` | `<frozen importlib._bootstrap>:488` | `SwigPyObject` n'a pas d'attribut `__module__` | **amont** (extension SWIG) | idem | idem |
| 5 | **post-summary** | `DeprecationWarning` | `sys:1` | `swigvarlink` n'a pas d'attribut `__module__` | **amont** (extension SWIG) | émis après le résumé, pendant la finalisation de l'interpréteur ; échappe donc au filtrage pytest | idem |

**Aucun des cinq n'appartient au projet.** `project_owned = 0`,
`upstream_owned = 5`.

### Le vrai constat

Les quatre paquets impliqués — `pandas`, `numexpr`, `bottleneck` et l'extension
SWIG — **ne figurent dans aucun fichier de dépendances du dépôt**. Ils viennent
de `~/.local/lib/python3.12/site-packages`, c'est-à-dire du *user site* du poste
de développement, entièrement hors contrôle.

C'est la dette réelle : ce n'est pas que ces avertissements soient bruyants,
c'est que le code qui les déclenche s'exécute depuis un environnement que le
dépôt ne décrit pas.

## 2. État de l'épinglage

`requirements-ci-audit.txt` épingle **30 paquets**, tous en `==`. Face à
l'environnement local :

| État | Nombre |
|---|---:|
| `MATCH` | 21 |
| `DRIFT` | 8 |
| `ABSENT` | 1 |

| Paquet | Épinglé | Installé localement | État |
|---|---|---|---|
| `Deprecated` | 1.3.1 | 1.2.18 | DRIFT |
| `PyYAML` | 6.0.3 | 6.0.1 | DRIFT |
| `attrs` | 25.4.0 | 23.2.0 | DRIFT |
| `librt` | 0.13.0 | 0.12.0 | DRIFT |
| `python-dotenv` | 1.2.1 | 1.2.2 | DRIFT |
| `types-PyYAML` | 6.0.12.20260724 | 6.0.12.20260518 | DRIFT |
| `typing_extensions` | 4.15.0 | 4.16.0 | DRIFT |
| `wrapt` | 2.3.0 | 1.17.2 | DRIFT |
| `types-jsonschema` | 4.26.0.20260518 | — | ABSENT |

**La suite de tests exécutée localement ne tourne donc pas sur l'ensemble de
versions que la CI installe.** Un résultat vert local ne prouve rien sur la CI,
et réciproquement.

## 3. Déclarations non bornées

`NSI/requirements.txt` porte **14 déclarations à borne inférieure seule**
(`>=`), sans borne supérieure ni verrou :

`httpx`, `trafilatura`, `pymupdf`, `beautifulsoup4`, `lxml`,
`sentence-transformers`, `anthropic`, `fastmcp`, `pyyaml`, `jsonschema`,
`python-dotenv`, `rich`, `pytest`, `ruff`.

Cinq d'entre elles — `pyyaml`, `jsonschema`, `python-dotenv`, `pytest`, `ruff` —
sont **aussi** épinglées dans `requirements-ci-audit.txt`, à des versions qui
peuvent diverger. Deux sources de vérité contradictoires pour le même paquet.

## 4. Politique d'installation en CI

| Workflow | Installe le fichier épinglé | `--no-deps` | `pip check` | `--require-hashes` |
|---|---|---|---|---|
| `ci-audit-collection.yml` | oui | oui | oui | **non** |
| `ci-mathematiques.yml` | oui | oui | oui | **non** |
| `ci-nsi.yml` | oui | oui | oui | **non** |

La CI est déjà correcte sur l'essentiel : installation `--no-deps` depuis un
fichier entièrement épinglé, puis `pip check`. Il manque le verrouillage par
empreinte : sans `--require-hashes`, une version republiée sous le même numéro
change l'environnement sans changer le fichier.

`pip check` local échoue par ailleurs sur des paquets système sans rapport avec
le projet (`tables`, `uno`, `flask-limiter`, `opencv-python-headless`,
`ocrmypdf`), ce qui confirme que le poste n'est pas un environnement isolé.

## 5. Conditions de fermeture avant `FINAL_SOURCE_SHA`

1. Un fichier de contraintes reproductible **couvrant aussi l'environnement de
   test local**, incluant `pandas`, `numexpr`, `bottleneck` et l'extension SWIG
   aujourd'hui invisibles du dépôt.
2. `pip check` vert dans l'environnement réellement utilisé, et non seulement en
   CI.
3. La CI et le poste de développement résolvant le **même** ensemble de versions
   — les 9 écarts ci-dessus ramenés à zéro.
4. `--require-hashes` en CI.
5. Une source de vérité unique par paquet : arbitrer entre
   `requirements-ci-audit.txt` et `NSI/requirements.txt` pour les 5 paquets
   déclarés deux fois.
6. Chaque avertissement soit corrigé, soit tracé ici comme dette amont assumée.

Aucun de ces points ne bloque la wave de contenu en cours ; tous bloquent
`FINAL_SOURCE_SHA`.
