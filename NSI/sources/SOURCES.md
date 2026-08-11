# Sources reglementaires — NSI

## Fichiers

| Fichier | Reference BO | Application | SHA-256 |
|---|---|---|---|
| `BO2019_NSI_premiere.pdf` | BO special n 1 du 22-01-2019 | Rentree 2019 | `7ca9a32e1823be6c1120cb0417324c3cb01688d1d194c7614a88ea851ccc60b0` |
| `BO2019_NSI_terminale.pdf` | BO special n 8 du 25-07-2019 | Rentree 2020 | `10ce34666edd722a3d8d86642a9f1ac205c7a9d128d6142a17effcba2fb85e69` |

## Note

Les programmes NSI ne sont pas modifies par la reforme 2026.

## Extraits texte

`sources/txt/BO2019_NSI_terminale.txt` — extrait `pdftotext -layout` depose le 5 aout 2026,
recupere depuis `https://eduscol.education.gouv.fr/sites/default/files/document/spe247annexe1158933pdf-89502.pdf`
(arrete MENE1921247A). SHA-256 verifie identique a `BO2019_NSI_terminale.pdf` deja
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
