# Conformite BO 2026 — Manuel 1SPE Mathematiques

> **BLOQUANT POUR COMMERCIALISATION** : la validation humaine des referentiels
> contre le BO n 14 du 2 avril 2026 est une gate de sortie non automatisable.
> Chaque ligne A_VALIDER_HUMAIN dans ce tableau doit etre resolue avant mise
> en production des variantes eleve/professeur.

## Source reglementaire attendue

BO special n 14 du 2 avril 2026 — Programme de specialite mathematiques,
classe de premiere generale.

**Statut du texte dans le depot** : ABSENT de `sources/`.
Regle R7 appliquee : aucune supposition sur le contenu du BO 2026.

## Tableau de conformite par chapitre

| Chapitre | Referentiel actuel | BO ref. | Verdict | Detail |
|---|---|---|---|---|
| 1SPE-SUITES | BO 2019 | BO 2026 | **A_VALIDER_HUMAIN** | Capacites C1-C7 a confronter |
| 1SPE-SECOND-DEGRE | BO 2019 | BO 2026 | **A_VALIDER_HUMAIN** | Capacites C1-C6 a confronter |
| 1SPE-DERIVATION-LOCAL | BO 2019/2026 | BO 2026 | **A_VALIDER_HUMAIN** | Capacites C1-C5 a confronter |
| 1SPE-DERIVATION-GLOBAL | BO 2019/2026 | BO 2026 | **A_VALIDER_HUMAIN** | Capacites C1-C5 a confronter |
| 1SPE-EXPONENTIELLE | BO 2026 | BO 2026 | **A_VALIDER_HUMAIN** | Capacites C1-C5, formulations a verifier mot a mot |
| 1SPE-TRIGONOMETRIE | BO 2026 | BO 2026 | **A_VALIDER_HUMAIN** | Capacites C1-C5, formulations a verifier |
| 1SPE-PRODUIT-SCALAIRE | BO 2026 | BO 2026 | **A_VALIDER_HUMAIN** | Capacites C1-C5, formulations a verifier |
| 1SPE-GEOMETRIE-REPEREE | BO 2026 | BO 2026 | **A_VALIDER_HUMAIN** | Capacites C1-C5, formulations a verifier |
| 1SPE-PROBA-COND | BO 2026 | BO 2026 | **A_VALIDER_HUMAIN** | Capacites C1-C5, formulations a verifier |
| 1SPE-VARIABLES-ALEATOIRES | BO 2026 | BO 2026 | **A_VALIDER_HUMAIN** | Capacites C1-C5, formulations a verifier |

## Points critiques identifies sans le texte

### Chapitres ancres BO 2019 (Suites, Second degre)
- Les programmes 2019 et 2026 peuvent differer sur :
  - Notions ajoutees/retirees/deplacees entre niveaux
  - Demonstrations exigibles modifiees
  - Algorithmique : evolution du perimetre Python
- **Action requise** : fournir le texte BO 2026, confronter capacite par capacite,
  corriger les JSON + cours/exos/QCM si ecart de contenu, VERIFY re-execute.

### Chapitres ancres BO 2026 (Exponentielle et suivants)
- Produits directement sur le programme 2026 mais les `libelle_bo` sont des
  formulations agent, pas des citations verbatim du BO.
- **Action requise** : verification mot a mot des `libelle_bo` contre le texte officiel.

## Procedure de mise a jour (quand le BO sera fourni)

1. Ajouter le texte dans `sources/bo_2026_maths_1spe.pdf` ou `.md`
2. Pour chaque chapitre : comparer capacite par capacite
3. Ecarts de contenu : correctifs cours/exos/QCM, commits par chapitre, VERIFY re-execute
4. Ecarts de formulation seule : mise a jour JSON + libelles eleve
5. Mettre a jour ce tableau avec verdict CONFORME ou CORRIGE
6. Validation humaine finale signee
