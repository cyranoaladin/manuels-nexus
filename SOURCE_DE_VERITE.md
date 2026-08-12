# SOURCE DE VÉRITÉ — Collection Manuels Nexus Réussite

Consolidation du 11 août 2026. Ce fichier recense **tout** ce qui a été produit
pour la collection et où cela se trouve. Il prévaut sur tout rapport antérieur
décrivant l'emplacement des contenus.

## Règle

`/home/alaeddine/Documents/Manuels_Nexus`, branche `main`, est l'unique source
de vérité. Miroir distant : `github.com/cyranoaladin/manuels-nexus`,
**public**.

Historique de visibilité du 11 août 2026 : le dépôt était public, a été basculé
en privé au titre de la propriété intellectuelle commerciale, puis remis en
public le même jour sur instruction explicite. Aucune donnée d'élève ne doit
donc y figurer — voir le contrôle PII ci-dessous.

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

## Recherche exhaustive de contenus manquants — 2026-08-11 (seconde passe)

**Sur disque.** Recherche de `contrat.yaml`, marqueur du pipeline de chapitre,
sur l'integralite de `/home/alaeddine` hors depot : **zero resultat**. Aucun
chapitre produit par le pipeline ne vit ailleurs. Les fichiers `.tex` employant
les macros du gabarit (`exercice`, `corrige`, `fichemethode`) trouves hors
depot sont des documents de seance : stages, sujets blancs, tests d'entree,
DS. Ce sont des supports ponctuels, pas des manuels.

**Sur GitHub.** Les 40 depots du compte ont ete inventories. `manuels-nexus`
est le seul a contenir des manuels. Ses refs distantes sont completes : 6
branches, 18 tags, une pull request fusionnee.

**Trouvaille : le corpus NSI n'etait pas perdu.** Le depot
`github.com/cyranoaladin/NSI` est le `corpus_nsi` reference par les
metadonnees du chapitre pilote `1NSI-TYPES-CONSTRUITS`. Les 15 anomalies
`unavailable_inspiration_sources` de l'audit portaient sur 10 cibles
distinctes : **les 10 s'y resolvent, chemin pour chemin**.

Volume : 44 fiches de cours, 370 supports (TD, TP, cours, evaluations,
corriges, baremes, remediation, versions amenagees), 45 sequences, 14 banques,
pour les deux niveaux — Premiere P00 a P21, Terminale T00 a T22. Environ
440 000 mots.

Reserve : la totalite des 370 supports porte `status: needs_review` et
`source_creation: generated_from_program`. La qualite est inegale, certaines
fiches de cours restant generiques la ou plusieurs TD sont directement
exploitables. Cette matiere premiere reste soumise aux memes gates que toute
autre. Voir `NSI/sources/SOURCES.md` pour l'enregistrement complet, avec le
commit epingle `52bcfdea`.

Point ouvert : ce depot est **public** alors que `manuels-nexus` est passe en
prive le meme jour.

## Consolidation finale — 2026-08-11

**Le corpus NSI est desormais dans le depot.** Importe par `git subtree` sous
`NSI/corpus_nsi/`, c'est-a-dire exactement le chemin que les metadonnees du
chapitre pilote `1NSI-TYPES-CONSTRUITS` referencaient depuis l'origine. Les 10
cibles `sources_inspiration` se resolvent maintenant en local, sans acces
reseau : l'anomalie `unavailable_inspiration_sources` (15 references) est
fermee a la source.

1 235 fichiers, importes en un commit unique (`--squash`) pour ne pas gonfler
l'historique, la provenance restant tracee dans le message de fusion et dans
`NSI/sources/SOURCES.md`.

Le depot `github.com/cyranoaladin/NSI` reste en place comme amont du corpus.
Toute evolution ulterieure se reporte par `git subtree pull`.

**Une seule branche porte tout.** `main` a ete avance par fast-forward sur
`production/collection-v2` : elle contient desormais la production du chapitre
TSPE-CONTINUITE, les correctifs de conformite programme, la reparation de la
suite de tests et le corpus. Local et distant sont identiques.

**Visibilite des depots.** Dix depots prives sont passes en public le
2026-08-11, dont `manuels-nexus` : le compte compte desormais 60 depots publics
et 2 prives. Ces deux-la restent prives sur decision explicite :

| Depot | Motif |
|---|---|
| `Interface_NSI` | listes nominatives d'eleves (nom, prenom, adresse mail scolaire, classe) dans cinq fichiers CSV |
| `qcm-eds-maths-terminale-amc` | bases AMC `capture.sqlite`, `scoring.sqlite`, `report.sqlite` : copies scannees et notes individuelles |

Ces deux depots pourront etre publies apres purge des donnees personnelles, y
compris dans l'historique git.

## Contrôle des données personnelles — dépôt public

Le dépôt étant public, aucun contenu ne doit comporter de donnée d'élève.
Contrôle du 2026-08-11 sur l'intégralité de l'arbre suivi, corpus inclus :

| Contrôle | Résultat |
|---|---|
| Fichiers `.env` réels, clés, certificats suivis | 0 (seuls deux `.env.example`) |
| Adresses mail scolaires | 0 |
| Noms d'élèves dans les chemins suivis | 0 |
| CSV / sqlite du corpus NSI | 6 fichiers, tous des manifestes techniques |
| Documents du corpus déclarant `private_data` | 467, tous à `false` |

Les correspondances « Prénom NOM » relevées dans le corpus sont des artefacts
d'exemples SQL (`Eleve JOIN`, `Note WHERE`) et non des données réelles.

Ce contrôle est à refaire avant chaque poussée sensible : recherche de secrets,
de données personnelles, de CSV et de bases sqlite.

## Audit de recolement — 2026-08-12

Nouvelle passe exhaustive : worktrees, dossiers externes, clones du corpus,
refs git, depot GitHub.

**Branche porteuse du travail en cours.** La branche
`integration/1spe-bo2026-traceability` (creee apres la consolidation du 11
aout) part de `main` et porte la mission « finalisation premium des six
manuels » : conception approuvee
(`docs/superpowers/specs/2026-08-12-finalisation-premium-six-manuels-design.md`)
et plan Wave 0
(`docs/superpowers/plans/2026-08-12-wave-0-collection-infrastructure.md`).
`main` reste la source de verite ; cette branche est la seule a contenir du
travail plus recent que `main`, et doit y etre fusionnee a l'issue des vagues.

**Production retrouvee hors depot — recuperee.** Passe TD-normalisation P00 du
corpus NSI, non commitee depuis le 2026-07-15 dans le worktree externe
`~/Documents/NSI-recovery-t10-p08-t17`. Sauvegardee en commit local `cb48096`
dans ce clone et copiee ici :
`NSI/sources/recuperation/2026-07-15-p00-td-normalisation.patch` (voir
`NSI/sources/SOURCES.md`). C'etait la seule production de la collection
retrouvee hors du depot.

**Clones externes du corpus `cyranoaladin/NSI`** (matiere premiere, pas des
manuels) :

| Chemin | Etat |
|---|---|
| `~/Documents/NSI-recovery-t10-p08-t17` | a jour de l'amont (`52bcfdea`) ; portait la passe P00 recuperee ci-dessus |
| `~/Documents/00_NSI/NSI` | perime (31 commits de retard) ; son commit local REM6 `36394a5` est deja en amont via la PR #111 — rien a recuperer ; fichier non suivi `reports/forensic_recovery_t10_p08_t17.md` (rapport, sans contenu pedagogique) |
| `~/Documents/00_NSI/NSI-recovery-t10-p08-t17` | worktree casse (son depot parent `~/Documents/NSI` n'existe plus) — supprimable |

**Nettoyages effectues.** Ref distante fantome
`baseline-final/finalisation-collection-v1` supprimee (le remote n'existait
plus). Squelette vide `chapitres/TSPE-SUITES-LIMITES/` a la racine supprime
(zero fichier, doublon d'arborescence du vrai chapitre sous
`Mathematiques/manuel-maths/chapitres/`).

**GitHub.** `manuels-nexus` public, 7 branches distantes conformes aux refs
locales. Amont corpus `cyranoaladin/NSI` : `main` = `52bcfdea` = commit epingle
du subtree — aucun ecart.
