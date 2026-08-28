# Autorités officielles — édition 2026-2027

Les trois namespaces sont disjoints :

- `PROGRAMME_D_ENSEIGNEMENT` détermine exclusivement la couverture à enseigner ;
- `DEFINITION_D_EPREUVE` décrit le régime, la durée, la structure, la pondération et la calculatrice ;
- `SUJETS_D_EXAMEN` constitue une preuve empirique de mise en œuvre, jamais une autorité de programme.

Les autorités programme sont établies pour les six manuels dans
`audit/OFFICIAL_AUTHORITIES_2026_2027.json`.

## Décisions sensibles

- 1SPE : MENE2602917A est applicable dès la rentrée 2026-2027. L’épreuve anticipée est écrite, 2 h, coefficient 2, sans calculatrice, avec 6 points d’automatismes/QCM et 14 points pour deux à trois exercices. Les sujets de juin 2026 relèvent de la cohorte 2025-2026 : `SUBJECT_2026_PROGRAM_AUTHORITY=false`.
- TSPE : le programme 2019 MENE1921246A reste applicable en 2026-2027 ; MENE2602919A est `WRONG_YEAR` car applicable seulement en 2027-2028. L’épreuve applicable dure 4 h, comporte quatre exercices, coefficient 16 ; le sujet fixe l’usage de la calculatrice.
- TCOMPL et TEXPERTES : régime optionnel. Pour les scolaires, contrôle continu ; pour les candidats individuels/hors contrat, oral ponctuel selon MENE2533572N. Ce ne sont pas des épreuves terminales nationales scolaires.
- 1NSI : contrôle continu si la spécialité n’est pas poursuivie ; épreuve ponctuelle prévue pour les catégories concernées, sans créer une autorité de programme distincte.
- TNSI : MENE2516123N. Écrit 3 h 30 et pratique 1 h, chacun noté sur 20, pondérés respectivement 0,75 et 0,25. Les contributions pédagogiques 15/20 + 5/20 ne sont pas stockées comme barèmes bruts.

Deux coquilles de NOR sont tracées dans le JSON et résolues par la source canonique JO/BO. Aucun sujet zéro explicitement rattaché à MENE2602917A n’a été identifié au 23 août 2026.
