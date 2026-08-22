# Classification de la dette de statut — 2222 `blocking_statuses`

Classification par **clusters** (pas une revue individuelle des 2222 —
c'est l'objectif explicite de ce lot : cartographier la dette pour pouvoir
la fermer méthodiquement, pas la fermer ici). Détail machine complet, une
ligne par objet, dans `audit/PUBLISH_STATUS_DEBT_CLASSIFICATION.json`.

Aucune promotion de statut effectuée. `UNKNOWN = 0` (2222/2222 classifiés).

## Répartition par cluster

| Cluster | Nombre | % | Signification |
|---|---:|---:|---|
| `GENERATED_NOT_REVIEWED` | 1756 | 79,0 % | `status=generated` — produit par le pipeline, jamais examiné (ni scientifique, ni pédagogique, ni éditorial). |
| `EDITORIAL_REVIEW_PENDING` | 164 | 7,4 % | `status=needs_review` (hors méthodes) — flag explicite de revue, type de revue non déductible sans inspection individuelle. |
| `PEDAGOGICAL_REVIEW_PENDING` | 161 | 7,2 % | `status=verified` — vérification scientifique/computationnelle (SymPy/Python) déjà passée ; reste la revue pédagogique/éditoriale avant `approved`. |
| `METHOD_REVIEW_DEBT_A4` | 94 | 4,2 % | `status=needs_review`, `type_objet=methode` — dette de revue des méthodes déjà identifiée (`A4_METHOD_REVIEW_DEBT_POLICY.md`, ~89 méthodes ; 94 mesurées ici, écart probablement dû à des méthodes ajoutées depuis A4 — à vérifier). |
| `HUMAN_APPROVAL_PENDING` | 23 | 1,0 % | Contrats `status=valide` (20) ou `status=complete` (3) — validation informelle déjà faite, transition formelle vers `approved` manquante. |
| `DRAFT_NOT_REVIEWED` | 17 | 0,8 % | `status=draft` — brouillon, structure/contrat non finalisé. |
| `SCIENTIFIC_REVIEW_PENDING` | 7 | 0,3 % | `status=manual_review` — SymPy n'a pas pu vérifier automatiquement (règle R2), revue scientifique humaine explicitement requise. |
| **Total** | **2222** | **100 %** | |

`UNKNOWN` = 0.

## Répartition par manuel × cluster

| Manuel | Clusters présents |
|---|---|
| **1SPE** (1414) | GENERATED_NOT_REVIEWED 1393, PEDAGOGICAL_REVIEW_PENDING 8, DRAFT_NOT_REVIEWED 7, HUMAN_APPROVAL_PENDING 3, METHOD_REVIEW_DEBT_A4 3 |
| **1NSI** (342) | EDITORIAL_REVIEW_PENDING 164, PEDAGOGICAL_REVIEW_PENDING 153, DRAFT_NOT_REVIEWED 10, METHOD_REVIEW_DEBT_A4 8, SCIENTIFIC_REVIEW_PENDING 7 |
| **TCOMPL** (209) | GENERATED_NOT_REVIEWED 150, METHOD_REVIEW_DEBT_A4 50, HUMAN_APPROVAL_PENDING 9 |
| **TEXPERTES** (131) | GENERATED_NOT_REVIEWED 93, METHOD_REVIEW_DEBT_A4 33, HUMAN_APPROVAL_PENDING 5 |
| **TNSI** (115) | GENERATED_NOT_REVIEWED 109, HUMAN_APPROVAL_PENDING 6 |
| **TSPE_2026_2027** (11) | GENERATED_NOT_REVIEWED 11 |

Observation : **1NSI concentre à lui seul 100 % des clusters
`EDITORIAL_REVIEW_PENDING` et `PEDAGOGICAL_REVIEW_PENDING`** — cohérent avec
la règle R2 du pipeline NSI (`verify_python.py`, exécution sandbox
systématique), qui fait davantage progresser les objets NSI vers
`verified`/`needs_review` plutôt que de les laisser à `generated`. Les
manuels de mathématiques (1SPE, TCOMPL, TEXPERTES, TSPE, TNSI) restent
massivement au stade `generated` — jamais passés par une étape de
vérification automatique équivalente à grande échelle.

## Ce que cette classification permet — et ne permet pas

**Permet** : prioriser. `GENERATED_NOT_REVIEWED` (79 %) est la masse
principale — closing ce cluster nécessite de faire passer chaque objet par
la vérification appropriée à son type (`verify_sympy.py`/`verify_python.py`
pour le contenu calculatoire, revue humaine pour le reste), pas une
promotion en masse. `METHOD_REVIEW_DEBT_A4` (94) est un cluster déjà
identifié et documenté par un lot antérieur (A4) — prioritaire pour
fermeture réelle (mandat T2 addendum §15).

**Ne permet pas** : conclure quoi que ce soit sur la conformité programme,
l'exactitude scientifique ou la qualité pédagogique d'un objet individuel.
`programme_state`, `scientific_state`, `pedagogical_state` sont enregistrés
comme `UNKNOWN_PENDING_AUDIT` pour tous les objets sauf
`PEDAGOGICAL_REVIEW_PENDING` (`scientific_state=AUTOMATED_CHECK_PASSED`,
seul signal disponible sans audit individuel). Aucune valeur `FULL`/
`approved` n'est déclarée par ce lot.

## Prochaine étape

Fermer réellement les 94 `METHOD_REVIEW_DEBT_A4` (programme, scientifique,
pédagogique, cross-reference, variante/rendu — mandat §15), en parallèle
des audits scientifique/pédagogique par chapitre (T3/T4) qui feront
progresser `GENERATED_NOT_REVIEWED` et `EDITORIAL_REVIEW_PENDING` vers des
statuts honnêtes. Aucune promotion tant que ces contrôles ne sont pas
réellement passés.
