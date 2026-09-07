# Origine de la cible « cinquante exercices par chapitre »

- `FIFTY_EXERCISES_POLICY_ORIGIN` : `EDITORIAL_GUIDELINE, EXPLICIT_RELEASE_OWNER_REQUIREMENT, GENERATOR_ASSUMPTION`
- `FIFTY_EXERCISES_RELEASE_REQUIREMENT` : `SUPERSEDED_EDITORIAL_VOLUME_TARGET`
- gates de release imposant cinquante : `0`

## Traces

### `PROMPT_MISSION_COLLECTION.md` — `EXPLICIT_RELEASE_OWNER_REQUIREMENT`

> matrice ≥2 ex/case et ≥50 ex/chapitre

Le prompt de mission ecrit par le release owner, dans une section intitulee « ce qui ne change pas » : c'est une directive humaine explicite, pas une convention d'outil.

### `scripts/chapter_readiness.py` — `GENERATOR_ASSUMPTION`

> TARGET_EXERCISES = min(50, max(24, 6 * C))

Un seuil interne a un tableau de bord que son propre en-tete declare « non autoritaire pour la release » ; il derive la cible du nombre de capacites au lieu de l'imposer.

### `Mathematiques/manuel-maths/chapitres/TSPE-CONTINUITE/LOT-4_addendum_seuil_E5.md` — `EDITORIAL_GUIDELINE`

> Ratio 40/40/20 exactement conforme à E5/F01

Un compte rendu de production qui atteint cinquante pour un chapitre donne ; il documente une realisation, il n'edicte rien.

## Supersession

- origine historique : PROMPT_MISSION_COLLECTION.md §3.4, 2026-07-16, « matrice >=2 ex/case et >=50 ex/chapitre »
- statut : `SUPERSEDED_EDITORIAL_VOLUME_TARGET`
- decidee le 2026-09-07 par abenrhouma
- motifs :
  - ce nombre n'est pas issu des programmes officiels
  - il ne mesure ni couverture, ni diversite, ni qualite
  - il a cree une incitation directe au remplissage synthetique
  - le commit 533d1919 demontre empiriquement le risque de satisfaire une metrique quantitative au detriment du fond
  - l'objectif est de produire des manuels complets et rigoureux, sans filler
- critere courant : completude pedagogique qualitative : programme, entrainement, variete, progressivite, corriges, evaluation, remediation

## Autorite courante

La decision humaine du 2026-09-07 ne fixe aucun nombre : « le volume est une consequence de la qualite, jamais la cible ». Elle est posterieure a la directive du 2026-07-16 et la remplace pour la reconstruction. La directive anterieure est donc remontee comme preuve, sans etre appliquee : aucun objet ne sera cree pour atteindre cinquante.
