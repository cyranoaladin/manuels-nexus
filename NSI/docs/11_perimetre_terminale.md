# Perimetre Terminale — NSI specialite (TNSI)

## Source reglementaire

Arrete MENE1921247A, BO special n 8 du 25 juillet 2019, application rentree 2020.
Texte depose : `sources/txt/BO2019_NSI_terminale.txt` (extrait `pdftotext -layout`,
depose le 5 aout 2026, SHA-256 verifie identique au `BO2019_NSI_terminale.pdf`
deja enregistre dans `sources/SOURCES.md`).

## Etat du referentiel

`referentiel/capacites_TNSI_*.json` — **deja extrait**, 6 fichiers, confirmes
conformes a l'ordre et aux intitules du texte BO (verification croisee 2026-08-05) :

| # | Chapitre propose | Fichier referentiel | Position dans le BO |
|---|---|---|---|
| 1 | TNSI-HISTOIRE-INFORMATIQUE | `capacites_TNSI_HISTOIRE-DE-L-INFORMATIQUE.json` | ligne 127 |
| 2 | TNSI-STRUCTURES-DONNEES | `capacites_TNSI_STRUCTURES-DE-DONNEES.json` | ligne 155 |
| 3 | TNSI-BASES-DONNEES | `capacites_TNSI_BASES-DE-DONNEES.json` | ligne 205 |
| 4 | TNSI-ARCHITECTURES-SYSTEMES | `capacites_TNSI_ARCHITECTURES-MATERIELLES-SY.json` | ligne 266 |
| 5 | TNSI-LANGAGES-PROGRAMMATION | `capacites_TNSI_LANGAGES-ET-PROGRAMMATION.json` | ligne 323 |
| 6 | TNSI-ALGORITHMIQUE | `capacites_TNSI_ALGORITHMIQUE.json` | ligne 375 |

**Point ouvert (A_VALIDER_HUMAIN)** : le champ `bo_reference` interne des 6
fichiers JSON cite a tort "BO special n1 du 22 janvier 2019" (copie du gabarit
1NSI, jamais mise a jour). La reference correcte est "BO special n8 du
25-07-2019, arrete MENE1921247A" — deja correcte dans `sources/SOURCES.md`.
Correction non appliquee : modification de `referentiel/*.json` interdite sans
instruction explicite (regle absolue du `CLAUDE.md` NSI). A corriger sur
validation humaine avant tout LOT 0.

## Granularite — A_VALIDER_HUMAIN

Deux themes sont plus volumineux que les 4 autres et pourraient etre scindes
(a verifier au moment du LOT 0 de chacun, apres lecture fine du referentiel) :
- **Structures de donnees** : piles, files, listes chaines, arbres (binaires,
  binaires de recherche) — potentiellement 2 chapitres (lineaire / arborescent).
- **Langages et programmation** : programmation orientee objet, recursivite,
  gestion d'exceptions — potentiellement 2 chapitres.

Decision par defaut proposee : 6 chapitres (1 par fichier referentiel deja
extrait), a l'image de 1NSI ou chaque theme = 1 chapitre. A ajuster au vu du
volume reel de capacites par fichier lors du LOT 0.

## Etat d'avancement

Aucun chapitre TNSI redige a ce jour (seul `1NSI-TYPES-CONSTRUITS` existe pour
la Premiere, 1/8 themes 1NSI). Ce document sert de cadrage prealable au LOT 0
du premier chapitre TNSI.

## Prerequis avant LOT 0 du premier chapitre

1. Texte BO depose et verifie : **fait**.
2. Referentiel capacites extrait : **fait** (sous reserve de la correction de
   metadonnee `bo_reference` ci-dessus).
3. Validation humaine de la liste de 6 chapitres (et de la granularite
   Structures de donnees / Langages et programmation) : **A_VALIDER_HUMAIN**.

## Workflow

Meme pipeline que 1NSI : voir `docs/02_workflow_production.md`.
