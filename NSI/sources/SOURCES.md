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
