# NOT_PUBLISH_READY

Rapport de consolidation — 9/10 septembre 2026. Constat, non approbation.

## A. Git final

| | |
|---|---|
| `main` | `d2f677fd2fc8f089300575f9fef259b2d520f829` |
| `origin/main` | `d2f677fd2fc8f089300575f9fef259b2d520f829` |
| ahead / behind | **0 / 0** |
| `git status` | propre, 0 modification |
| worktrees | **1** — la racine, sur `main` |
| stashs | **0** |
| branches locales | **1** — `main` |
| tags d'archive | 18 locaux, 18 sur `origin` |

Au départ : 1 526 commits sur aucune ref distante, `main` 1 443 commits en
retard, la production dans un worktree sur une branche jamais poussée, la
racine sur une branche de sauvetage. **Aucun commit projet n'est resté non
sauvegardé** — vérifié par SHA distants, jamais par code de retour.

## B. Branches réconciliées

Disposition complète dans `audit/RECONCILIATION_BRANCHES_2026_09_09.md`.
14 branches contenues dans `main`, supprimées par `git branch -d` qui refuse
toute branche non fusionnée ; 18 archivées par tag immuable poussé avant
suppression locale ; le tronc d'intégration temporaire supprimé après
fast-forward.

| Branche | Repris | Écarté |
|---|---|---|
| `codex/t3-publish-readiness-current` | tout — c'est le tronc | — |
| `codex/urgent-1nsi-content` | 32 remédiations rédigées ; INT-005 | ses retraits de clones (le tronc a **réécrit** les 16 restants en exercices distincts, meilleur que supprimer) ; ses 28 fiches méthode (série concurrente, voir §D) |
| `rescue/t2-legacy-wip-…` (88bbc) | 14 fichiers sur 122, dont le registre des autorités 2027 et la matrice de couverture | paquets de revue déjà présents sous `superseded/` ; 2 producteurs contredisant une décision humaine |
| `feature/1spe-bat-2026` | le contrôle de chaîne de fabrication | son référentiel programme concurrent |
| `codex/shared-infra-integration` | INT-005 et son test | INT-006 — vise une API que le tronc a fait évoluer |
| WIP du 8/9 septembre | intégralement | — |
| les 12 autres | — | superseded, déjà présent, ou dispositionné le 31 août |

## C. Programmes — session 2027

Registre récupéré : `audit/OFFICIAL_AUTHORITIES_2026_2027.json`, absent du tronc.

| Manuel | Texte | Applicable |
|---|---|---|
| 1SPE | **MENE2602917A**, BO n°14 du 2 avril 2026 | rentrée 2026-2027 |
| TSPE | MENE1921246A (2019) | 2026-2027 ; MENE2602919A classé **`WRONG_YEAR`** |
| TCOMPL / TEXPERTES | régime optionnel | — |
| 1NSI / TNSI | programmes 2019 ; TNSI **MENE2516123N** | épreuve session 2026, écrit 0,75 / pratique 0,25 |

Migration BO 2026 visible : le chapitre second degré porte les atomes
`-2026-C1..C4`, `D1` ; trois capacités de trigonométrie sont sorties du
programme ; les deux atomes `TNSI-PROJET` sont présents.

**Trou restant** : la matrice se déclare elle-même
`REJECTED_AS_PROGRAMME_COVERAGE_MATRIX` — les atomes officiels ne sont pas
inventoriés, un référentiel interne ne vaut pas autorité officielle.
`PROGRAM_EVIDENCE_MISSING_SOURCE` **n'est pas à 0**.

## D. Contenu

**52 chapitres, 3 477 objets, 6 manuels.** Identifiants : 3 477 objets,
3 477 identifiants distincts, **0 doublon** — désormais gardé par un test.

Les **cinq défauts scientifiques** du 8 septembre sont **fermés**. Quatre
l'étaient déjà par le tronc et je l'ai vérifié pièce par pièce ; j'ai fermé le
cinquième : l'ouverture du second degré présentait le développement exact
`4x³−100x²+600x` comme une « version simplifiée ≈ » et affirmait que forme
canonique et discriminant résolvent cette optimisation, alors que son propre
bloc de vérification employait une dérivée.

Clones : 5 groupes near-clones, 11 objets excédentaires — identiques avant et
après consolidation. Contamination inter-manuels : 0.

**Arbitrage éditorial laissé ouvert** : deux séries de fiches méthode
concurrentes existent pour huit chapitres 1NSI. Celle du tronc couvre 3
capacités sur 5 pour ARCHITECTURE-OS, celle de `urgent-1nsi` les couvre toutes.
J'ai restauré la série du tronc — celle sur laquelle toutes ses preuves sont
bâties — et l'autre reste sous son tag d'archive. **Ce choix appartient à un
humain.**

## E. Revue

| | |
|---|---|
| `machine_review_complete` | **52 / 52** |
| `human_closed` | **0 / 52** |
| nouvelles rédactions en attente | 262 |
| non formalisables en attente | 207 / 417 |
| `release-strict` | 127 raisons, dont **52 `HUMAN_REVIEW_PENDING`** |

52 pour 52 chapitres : **chaque chapitre attend sa revue humaine.** Aucune
opération machine ne la remplace, et aucune n'a été fabriquée.

## F. Tests

Mesure comparative, suite complète, même commande, deux exécutions d'environ
1 h 06 :

| | origine `274a7b811` | final `d2f677fd2` |
|---|---:|---:|
| échecs | 257 | **251** |
| succès | 9 283 | **9 698** |
| ignorés | 8 | 8 |

**8 échecs résolus, 2 introduits.** Les deux introduits sont :
`test_all_12_targets_candidate_ready`, rouge **délibéré** (voir §G), et
`test_programme_coverage_artifacts_match_generator`, qui passe seul et rejoint
une famille pré-existante de 27 cas identiques dus à la mutation d'artefacts
pendant la suite.

`ruff` : 190 erreurs résiduelles, aucune dans un fichier dont je suis l'auteur.
`mypy` : 1 erreur, pré-existante. **Couverture non mesurée** — elle exige une
exécution complète sous instrumentation, non faite.

Gates rejoués depuis un clone propre : `require-clean` **vert** ; `check`
rouge sur **une** qualification périmée exigeant un `approved_by` humain ;
`validate-model` 628 raisons ; `fail-on-new` 1 263 ; `release-strict` sort en 7,
son code **attendu**.

**CI** : la CI d'audit ne surveillait en push que `finalisation/collection-v1`.
Elle est restée muette sur trois semaines de production. Elle surveille `main`.

## G. PDF

**Aucun PDF n'a été reconstruit pour la publication, et c'est un blocage.**

`scripts/check_toolchain.py` : **3 blocages sur 10 contrôles** — TeX Live 2023
contre 2026 exigé, `verapdf` absent, balisage Tagged PDF non prouvable.

Trois artefacts distincts portent le même nom pour la seule édition élève 1SPE :

| Artefact | Pages | SHA-256 |
|---|---:|---|
| recompilé depuis les sources | **381** | `0ea2e23abdeb5b44…` |
| `build/`, **versionné dans Git** | 371 | `f3b8ec66584bda2a…` |
| `MANUELS_PDF_PUBLICATION/` | 371 | `c23140a53c25c584…` |

Les deux périmés ont le même nombre de pages et des empreintes différentes.
La reproductibilité et le préflight sont désormais déclarés
**`STALE_EVIDENCE_NOT_REOBSERVED`** : observés au commit `6c8b4b5b`, pas au
HEAD. Ils ne peuvent plus rendre une cible candidate.

Ce que la compilation depuis le clone propre établit tout de même :
**0 overfull, 0 glyphe manquant, 0 avertissement LaTeX**, polices incorporées,
`qpdf` sans erreur, couvertures avant et arrière correctes.

## H. Reproductibilité

Détail dans `audit/CLEAN_CLONE_REPRODUCIBILITY_2026_09_09.md`.

Un clone `git clone` depuis `origin`, environnement bâti du seul
`requirements-ci-audit.txt`, **aucun fichier copié de la machine** :
inventorie, assemble et compile un manuel complet. **Déterminisme prouvé** —
deux exécutions donnent des artefacts identiques au bit près, et deux
compilations le même PDF.

La reproductibilité **du dispositif** est acquise ; celle de la **release** ne
l'est pas, faute de la chaîne d'outillage déclarée.

## I. Dette finale

```
OPEN_RELEASE_BLOCKERS = 6
```

1. **Revue humaine** — 0/52 chapitres fermés, 52 `HUMAN_REVIEW_PENDING`.
2. **Chaîne de fabrication** — TeX Live 2023 < 2026, veraPDF absent,
   PDF/UA-1 non prouvable.
3. **Livrables** — 24/24 sans reçu de build courant, `RELEASE_READY` 0/24.
4. **Preuves de release périmées** — reproductibilité et préflight observés à
   un autre commit.
5. **Qualification périmée** — une fiche méthode exige un `approved_by` parmi
   trois rôles humains.
6. **Couverture programme** — la matrice se déclare rejetée ; les atomes
   officiels ne sont pas inventoriés.

À arbitrer par un humain, hors compteur : la série de fiches méthode 1NSI, et
49 liens Google Drive publics depuis le 11 août dont le partage n'a pas été
testé (`audit/IP_AND_PERSONAL_DATA_2026_09_09.md`).

Aucun seuil n'a été abaissé, aucun contrôle retiré, aucune anomalie reclassée,
aucune validation humaine inventée.
