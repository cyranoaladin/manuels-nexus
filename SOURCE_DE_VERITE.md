# SOURCE DE VÉRITÉ — Collection Manuels Nexus Réussite

Consolidation du 11 août 2026. Ce fichier recense **tout** ce qui a été produit
pour la collection et où cela se trouve. Il prévaut sur tout rapport antérieur
décrivant l'emplacement des contenus.

## Règle

`/home/alaeddine/Documents/Manuels_Nexus`, branche `main`, est l'unique source
de vérité. Miroir distant : `github.com/cyranoaladin/manuels-nexus` (**privé**
depuis le 11 août 2026 — il était public jusque-là).

Aucun contenu de la collection ne doit vivre ailleurs : ni dans un worktree, ni
dans une branche non fusionnée, ni dans un dossier externe.

## Ce que contient la source de vérité

| Manuel | Identifiant | Chapitres | Objets | PDF assemblés |
|---|---|---:|---:|---|
| Mathématiques Première spécialité | `1SPE` | 10 | 1 401 | élève, professeur, méthodes, remédiation, évaluations |
| Mathématiques Terminale spécialité | `TSPE_2026_2027` | 11 | 659 | élève, professeur |
| Mathématiques Terminale complémentaires | `TCOMPL` | 9 | 150 | élève, professeur |
| Mathématiques Terminale expertes | `TEXPERTES` | 5 | 93 | élève, professeur |
| NSI Première spécialité | `1NSI` | 10 | 339 | élève, professeur, méthodes, remédiation, évaluations, projets, aménagée |
| NSI Terminale spécialité | `TNSI` | 6 | 109 | aucun (assembleur manquant) |

Total : **51 chapitres, 2 751 objets de contenu, 20 PDF, 6 994 fichiers suivis,
739 commits, 16 tags.**

S'y ajoutent : les référentiels de capacités extraits des BO, les BO officiels
empreintés dans `sources/txt/`, les gabarits et la charte LaTeX, les serveurs
MCP, les scripts de gates, les suites de tests et l'appareil d'audit
(`audit/`).

## Contenu mis de côté volontairement

- `Mathematiques/manuel-maths/backlog_tspe_v2/1SPE-TRIGONOMETRIE/` — 86 fichiers.
  Capacités C3/C4/C5 de trigonométrie retirées de Première par le BO 2026
  (commit `8ecd58e0`, 18 juillet 2026) et conservées pour le programme de
  Terminale 2027. **Ce n'est pas du contenu perdu.**

## Ce qui reste hors de `main` — une seule chose

**Branche `feature/1spe-bat-2026`** (dernier commit `0d6ebd79`, 29 juillet 2026,
présente sur `origin`). 34 commits, 75 fichiers, non fusionnés.

Elle contient du travail réel absent de `main` :

- `referentiel/programme_1SPE_2026.json` — programme officiel 2026 canonisé ;
- `scripts/check_programme_1spe_2026.py` — gate de conformité au programme 2026 ;
- `scripts/extract_official_source.py`, `inventory_1spe.py`,
  `capture_initial_state_1spe.py`, `run_baseline_build.py`, `check_toolchain.py` ;
- 4 schémas JSON (contrat de chapitre 2026, programme, attestation, baseline) ;
- 8 fichiers de tests ;
- `validations/release-1spe/` — baseline de release, attestation programme,
  épinglage de la chaîne d'outils, preuve Tagged PDF ;
- `validations/v5-it1/` et `v5-it2/` — preuves visuelles de la maquette ;
- une migration des `contrat.yaml` vers un schéma enrichi portant les
  identifiants officiels du BO (`ANA-TRIG-CAP-001`), une `obligation_class` et
  les `proof_object_ids` par capacité — soit la matrice de traçabilité exigée
  par PROG-001 du cahier des charges.

**Pourquoi elle n'est pas fusionnée.** La fusion produit 7 conflits réels :
4 `contrat.yaml` (1SPE-PROBA-COND, SECOND-DEGRE, TRIGONOMETRIE,
VARIABLES-ALEATOIRES), `requirements.txt`, `scripts/check_maquette_v5.py` et
`tests/test_maquette_v5.py`. Les deux derniers ont divergé des deux côtés
— itération V5.B-it2 des onglets sur la branche, correctifs anti-collision des
notes de marge sur `main` — et `AGENTS.md` exige une approbation humaine
explicite pour toute modification de baseline visuelle.

L'intégration partielle a été testée et **écartée** : déposer les seuls
44 fichiers purement additifs sur `main` fait échouer 47 tests, car ils
dépendent des contrats migrés. La branche est indivisible.

**Décision attendue.** Trancher la baseline visuelle (V5.B-it2 contre
anti-collision), puis fusionner en reprenant la version de la branche pour les
4 contrats et en y réappliquant les corrections d'accentuation et
l'échappement `\%` faits sur `main`.

## Branches distantes

| Branche | État |
|---|---|
| `main` | source de vérité, à jour |
| `finalisation/collection-v1` | identique à `main` au contenu près des 2 commits de rangement ; conservée comme référence historique |
| `feature/1spe-bat-2026` | **non fusionnée** — voir ci-dessus |
| `codex/integrite-1spe` | entièrement contenue dans `main`, supprimable |
| `charte/v5-b-it2` | entièrement contenue dans `main`, supprimable |

## Ce qui a été vérifié le 11 août 2026

- Recherche exhaustive de `/home/alaeddine/Documents` : **aucun manuel de la
  collection n'existe hors du dépôt**. `01_Maths` ne contient que des stages,
  annales, séances et plateformes.
- Historique git complet : la **seule** suppression de contenu jamais commise
  est le retrait de trigonométrie du 18 juillet, archivé dans le backlog.
- Commits orphelins (`git fsck`) : aucun ne contient plus de contenu que `main`.
- Le worktree `.worktrees/finalisation-collection-v1` pointait sur le même
  commit que `main` ; il a été supprimé après consolidation (133 Mo de doublon).

## État de publication

**Aucun manuel n'est publiable.** Gate `release-strict` : ROUGE, 63 bloqueurs.
2 402 des 2 751 objets portent encore le statut `generated`. Voir
`ETAT_COLLECTION.md`, `audit/AUDIT_CONSOLIDE.md` et
`CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md`.
