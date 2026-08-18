# PROVENANCE CORRECTION — SHA 1361cf37

Correction formelle de la contradiction « même SHA, deux arbres » entre les deux
rapports A1/A2 successifs qui citaient tous deux
`HEAD = 1361cf3771317bb5d1b86d72a1f5a38ea80fd464`.

Date du diagnostic : 2026-08-18.
Diagnostic exécuté depuis des environnements hermétiques (clones frais +
worktrees frais), sans cache partagé, sans fichier local du worktree principal.

## 1. Cause racine

**Les deux rapports ont cité un SHA périmé.** Aucun des deux jeux de métriques
n'a été produit à partir de l'arbre committé `1361cf37` :

1. `1361cf37` n'est PAS le HEAD scellé. Le travail A1-final/A2 a produit
   **145 commits locaux supplémentaires** au-dessus de `1361cf37`. Le HEAD réel
   scellé au moment du second rapport était
   `9ddcffee6a341981feed95e54bc641e17cdc0732`
   (branche `audit/adversarial-reconciliation-2026`, worktree propre,
   tree `db8c215c1a3c110b2f51e40d347dd41b5a587a6c`).
2. Les métriques des deux rapports provenaient du worktree de travail
   (fichiers modifiés non committés au fil des étapes), pas de l'arbre du SHA
   cité. La citation `HEAD=1361cf37` était un instantané mémorisé et jamais
   revérifié par `git rev-parse HEAD` au moment de la mesure.
3. À `1361cf37`, la reproduction est **impossible par construction** :
   le `model_digest` de `audit/BUILD_MANIFEST.json` committé à ce SHA est
   incohérent avec le digest calculé par les scripts committés au même SHA.
   Tout run frais échoue avec
   `InventoryError: model_digest du manifeste de build incohérent`
   (render, fail-on-new et release-strict). Ni « RAW 5615 / P0 10 » ni
   « RAW 5605 / P0 0 » ne sont donc attribuables à `1361cf37`.

## 2. Mesures hermétiques

### À 1361cf37 (2 clones frais indépendants, branche exacte, arbre propre)

| Mesure | CLONE A | CLONE B |
| --- | --- | --- |
| render pipeline | FAIL (`model_digest` incohérent) | FAIL (identique) |
| fail-on-new | FAIL exit 5 (même raison) | FAIL exit 5 |
| release-strict | FAIL exit 7 (même raison) | FAIL exit 7 |
| pytest gouvernance | 13 failed / 709 passed | 13 failed / 709 passed |
| Ensembles d'échecs | identiques A == B | identiques A == B |

### À 9ddcffee (HEAD scellé, 2 worktrees frais indépendants)

| Mesure | FRESH A | FRESH B |
| --- | --- | --- |
| render pipeline | PASS | PASS |
| RAW | 5615 | 5615 |
| broken_latex_references | 0 | 0 |
| latex_cycles (graphe complet) | 0 | 0 |
| P0 (broken_latex + cycles) | 0 | 0 |
| fail-on-new | PASS exit 0, failures=[] | PASS exit 0, failures=[] |
| release-strict | FAIL exit 7 (dette ouverte 1NSI, attendu NO-GO) | identique |
| pytest gouvernance | 4 failed / 720 passed | 4 failed / 720 passed |
| INVENTAIRE_COLLECTION.json régénéré | sha256 `de146656…505a0c` | sha256 identique |

Le render à 9ddcffee est **déterministe et hermétique** : les artefacts
régénérés sont byte-identiques entre les deux worktrees frais.

Ventilation du RAW=5615 reproduit :
`broken_meta_references 2730, blocking_statuses 2133, unclassified_types 660,
unassembled_objects 52, unattributed_pdfs 22, orphan_files 12,
context_mismatches 3, duplicate_assembly_objects 3` (A3 non entamé).

## 3. Corrections apportées aux rapports scellés

1. **`A0_A1_STATE_TRANSITIONS`** : S3 affichait `RAW 5605`. La valeur
   reproduite est **5615**. Le 5605 provenait d'une double soustraction
   arithmétique des 10 cycles (jamais mesuré) : les 10 `latex_cycles` avaient
   déjà disparu de toute analyse fraîche dès la correction des wrappers en A1
   (commit `fed6d28a`, antérieur à `1361cf37`) ; le S2=5615 mesuré les
   incluait déjà en tant que résolus.
2. **`A2_LATEX_SCC_ANALYSIS`** : le lot A2 ne contient **aucun changement de
   source LaTeX** (aucun `.tex/.sty/.cls` modifié entre `1361cf37` et
   `9ddcffee`). La résolution réelle des 10 cycles est un unique motif de
   défaut — le fallback auto-référentiel `\input{nexus-manuel.cls}` dans les
   2 wrappers (`Mathematiques/manuel-maths/gabarits/nexus-manuel.cls`,
   `NSI/gabarits/nexus-manuel.cls`) — supprimé par le commit **`fed6d28a`**
   (lot A1, 2026-08-16). Les « 10 cycles » du rapport précédent provenaient de
   l'inventaire committé stale (généré avant `fed6d28a`), pas d'une mesure.
3. **`BUILD_MANIFEST_SEMANTICS_A1`** : la sémantique « synchronized with
   current repository HEAD » était auto-référentielle et entretenait la boucle
   de commits `final head_sha alignment` (plusieurs dizaines dans
   l'historique). Remplacée par la sémantique effective du code :
   `provenance.head_sha` = **OBSERVED_BUILD_SOURCE_SHA**, ancêtre strict
   vérifié par `merge-base --is-ancestor`, jamais réaligné manuellement.

## 4. Prévention de la récidive

- Tout rapport de phase DOIT citer le SHA obtenu par `git rev-parse HEAD`
  exécuté **au moment de la mesure**, avec `git status --porcelain` vide ;
  sinon le rapport doit porter la mention `WORKTREE_DIRTY`.
- Les métriques d'un rapport de gate DOIVENT provenir d'un run frais dans un
  clone/worktree propre au SHA cité — jamais d'un JSON committé
  potentiellement stale (`INVENTAIRE_COLLECTION.json` committé était périmé
  de 2 jours au moment des deux rapports).
- Un commit ne peut sceller un verdict que si le pipeline s'exécute avec
  succès depuis ce commit seul. `1361cf37` (manifeste incohérent avec ses
  propres scripts) n'aurait jamais dû servir de référence.
- Interdiction de la boucle d'auto-attestation `head_sha` (voir
  `BUILD_MANIFEST_SEMANTICS_A1.md` corrigé).

## 5. Dettes d'hermétisme restantes (bloquantes pour l'acceptation A1/A2)

Reproduites à l'identique dans les deux worktrees frais à `9ddcffee` :

1. `test_a1_broken_latex_references_resolved` et
   `test_renvois_generated_dependency_architecture` exigent l'existence de
   `Mathematiques/manuel-maths/build/maquette-v5/renvois.tex` — fichier
   **ignoré, non suivi, non régénéré par le test** (producteur identifié :
   `build_maquette_v5.py`, mais non invoqué). Preuve de gouvernance dépendant
   d'un fichier local non reproductible — interdit par le contrat de
   provenance. À corriger (le test doit invoquer le producteur ou vérifier le
   contrat sans dépendre du disque).
2. `test_require_clean_uses_canonical_union_for_untracked_source_roles` et
   `test_source_roles_preserve_literal_backslash_git_path` échouent aussi dans
   le worktree principal : régressions introduites par `76eed5de`
   (`_load_source_roles` : ajout des chemins déclarés non suivis). Code et
   tests sont en désaccord ; l'arbitrage (comportement voulu) doit être validé
   avant toute correction.

Tant que ces 4 tests ne sont pas verts en environnement frais, la condition
« governance tests = 100% PASS » n'est pas remplie.
