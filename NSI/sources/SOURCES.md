# Sources reglementaires — NSI

## Fichiers

| Fichier suivi | Arrete | Page BO | Annexe officielle | SHA-256 |
|---|---|---|---|---|
| `NSI/corpus_nsi/00_programmes_officiels/programme_nsi_premiere.pdf` | `MENE1901633A` | `https://www.education.gouv.fr/bo/19/Special1/MENE1901633A.htm` | `https://cache.media.education.gouv.fr/file/SP1-MEN-22-1-2019/26/8/spe633_annexe_1063268.pdf` | `7ca9a32e1823be6c1120cb0417324c3cb01688d1d194c7614a88ea851ccc60b0` |
| `NSI/corpus_nsi/00_programmes_officiels/programme_nsi_terminale.pdf` | `MENE1921247A` | `https://www.education.gouv.fr/bo/19/Special8/MENE1921247A.htm` | `https://cache.media.education.gouv.fr/file/SPE8_MENJ_25_7_2019/93/3/spe247_annexe_1158933.pdf` | `10ce34666edd722a3d8d86642a9f1ac205c7a9d128d6142a17effcba2fb85e69` |

## Note

Ces lignes attestent uniquement l'identite et l'authenticite des deux copies
locales. Elles ne concluent ni leur applicabilite a l'edition 2026-2027, ni la
couverture des manuels ; ces decisions relevent de l'audit de programme T2.

## Extraits texte

`sources/txt/BO2019_NSI_terminale.txt` — extrait `pdftotext -layout` depose le 5 aout 2026,
recupere depuis `https://eduscol.education.gouv.fr/sites/default/files/document/spe247annexe1158933pdf-89502.pdf`
(arrete MENE1921247A). SHA-256 verifie identique a
`NSI/corpus_nsi/00_programmes_officiels/programme_nsi_terminale.pdf` deja
enregistre ci-dessus (`10ce34666edd722a3d8d86642a9f1ac205c7a9d128d6142a17effcba2fb85e69`).
Confirme les 6 themes deja extraits dans `referentiel/capacites_TNSI_*.json` (Histoire de
l'informatique, Structures de donnees, Bases de donnees, Architectures materielles/OS/reseaux,
Langages et programmation, Algorithmique).

**Point ouvert (A_VALIDER_HUMAIN)** : le champ `bo_reference` des 6 fichiers
`referentiel/capacites_TNSI_*.json` cite a tort "BO special n1 du 22 janvier 2019 -- a
re-verifier" (copie du gabarit 1NSI). La bonne reference est "BO special n8 du 25-07-2019,
arrete MENE1921247A" (deja correcte dans ce fichier SOURCES.md). Correction non appliquee
ici : modification de `referentiel/*.json` interdite sans instruction explicite (regle CLAUDE.md
NSI). A corriger sur validation humaine.

## Corpus pedagogique NSI — source d'inspiration retrouvee (2026-08-11)

Les objets du chapitre pilote `1NSI-TYPES-CONSTRUITS` declarent dans leurs
metadonnees des `sources_inspiration` pointant vers `NSI/corpus_nsi/...`.
L'inventaire de la collection classait ces 15 references en anomalie
`unavailable_inspiration_sources` : les fichiers etaient absents des sources
suivies, et le corpus etait repute perdu.

Il ne l'etait pas. Ce corpus est le depot **`github.com/cyranoaladin/NSI`**.
Les 10 cibles distinctes des 15 references s'y resolvent toutes, chemin pour
chemin, sous `03_progressions/`.

| | |
|---|---|
| Depot | `https://github.com/cyranoaladin/NSI` |
| Commit epingle | `52bcfdea46be5a0225003b59f2d2333e84bf19bd` (2026-07-15) |
| Correspondance | `NSI/corpus_nsi/X` designe `X` a la racine de ce depot |
| Volume | 44 fiches de cours, 370 supports, 45 sequences, 14 banques |
| Niveaux | Premiere (P00 a P21) et Terminale (T00 a T22) |
| Statut des documents | `needs_review` sur la totalite des 370 supports |
| Visibilite | **public** au 2026-08-11 |

Types de supports disponibles : td (43), evaluation (43), corrige (43),
bareme (43), trace (41), cours (41), tp (39), version amenagee (35),
remediation (35), tp papier (7).

**Politique d'usage.** Contenu produit par le meme auteur, donc reutilisable
sans restriction de droits. Il reste soumis aux memes gates que toute autre
matiere premiere : aucun document n'est publiable en l'etat, tous portant
`status: needs_review` et `source_creation: generated_from_program`. La
qualite est inegale — certaines fiches de cours sont generiques, plusieurs TD
sont substantiels et directement exploitables.

**Point ouvert.** Ce corpus est public alors que `manuels-nexus` est passe en
prive le 2026-08-11. Si la matiere premiere doit suivre le meme regime que les
manuels qu'elle alimente, la visibilite du depot `NSI` est a trancher.

## Recuperation — passe TD-normalisation P00 non commitee (2026-08-12)

L'audit du 2026-08-12 a retrouve, dans le worktree externe
`/home/alaeddine/Documents/NSI-recovery-t10-p08-t17` (clone du depot corpus
`cyranoaladin/NSI`), une passe de normalisation du TD diagnostic P00 datee du
2026-07-15, restee **non commitee** sur la branche locale
`td-normalisation/p00-diagnostic-python`. Les passes equivalentes P08, P12 et
T13 ont, elles, ete fusionnees en amont via les PR `td-normalisation/*`.

| | |
|---|---|
| Perimetre | 8 fichiers, +451/-354 : `P00_contract.yml`, TD et corrige diagnostic Python, manifestes, registre de dette TD, revue de substance P-LANG-01 |
| Sauvegarde amont locale | commit `cb48096` sur `td-normalisation/p00-diagnostic-python` du clone de recuperation (non pousse) |
| Copie dans ce depot | `NSI/sources/recuperation/2026-07-15-p00-td-normalisation.patch` |
| Base d'application | commit corpus `52bcfdea` (le commit epingle du subtree) |

**Statut.** Matiere premiere non revue, au meme regime que le reste du corpus :
la passe n'est ni appliquee a `NSI/corpus_nsi/` ni poussee en amont. Pour
l'integrer : la faire aboutir dans le depot `cyranoaladin/NSI` (revue puis PR,
comme P08/P12/T13), puis `git subtree pull`.
