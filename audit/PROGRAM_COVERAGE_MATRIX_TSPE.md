# Matrice programme ↔ manuel — TSPE_2026_2027 (édition 2026-2027)

Recalculée directement contre le texte officiel `MENE1921246A` (BO spécial
n°8 du 25 juillet 2019, toujours en vigueur pour cette édition), déposé et
empreinté sous
`Mathematiques/manuel-maths/sources/txt/BO2019_TSPE_specialite.txt`
(`sha256:65eb5a55df14a2b3025a96db72fbcb1d917b55e8da7feb13669e28b903712210`,
vérifié contre `docs/programmes/PROGRAMMES_2026_2027.yaml`). Le texte du
NOUVEAU programme Terminale 2026 (`BO2026_TSPE_specialite_r2027.txt`,
applicable seulement à la rentrée 2027-2028) a été explicitement exclu de
cette atomisation. Détail complet ligne par ligne dans
`audit/PROGRAM_COVERAGE_MATRIX_TSPE.json` (89 lignes).

## Chiffres finaux

```
TOTAL_MANDATORY_ATOMS      = 75
STRUCTURALLY_MAPPED        = 73
TRANSVERSAL (hors grille)  = 2   (algorithmique de consolidation, vocabulaire ensembliste/logique - non scopés à un seul chapitre)
FULL                       = 0   (aucun audit scientifique/pédagogique fait sur ce manuel)
PARTIAL                    = 0
MISSING                    = 0
WRONG_YEAR                 = 0
UNSUPPORTED_CLAIM          = 0

Non obligatoire (mandatory=false), 14 lignes :
  OUT_OF_SCOPE_WITH_PROOF  = 14  (approfondissements/exemples d'algorithme explicitement facultatifs du BO)
```

Contrairement à 1SPE (programme changé, référentiel non encore resynchronisé
sur plusieurs points), TSPE 2019 n'a montré **aucune trouvaille de type
WRONG_YEAR ou UNSUPPORTED_CLAIM** : le référentiel local
(`referentiel/capacites_TSPE_*.json`, 12 thèmes, ~70 capacités) est très
fidèlement fondé sur le texte officiel — souvent au mot près.

## Trouvaille structurelle réelle (pas T1, mais à signaler)

`chapitres/TSPE-CONCENTRATION-LGN/cours/` est **vide** (aucun fichier
`.tex`). Le contenu réel de cette section BO ("Concentration, loi des
grands nombres" — inégalité de Bienaymé-Tchebychev, inégalité de
concentration, loi des grands nombres) existe bel et bien, mais est
physiquement rangé dans le chapitre voisin
`TSPE-PROBABILITES/cours/16_CONCLGN_bienayme_tchebychev.tex`. Le référentiel
garde `CONCENTRATION-LGN` comme thème séparé
(`capacites_TSPE_CONCENTRATION_LGN.json`, une seule capacité C1) alors que
le contenu a été consolidé dans un autre chapitre.

Pas une anomalie T1 (l'objet existe, est assemblé, structurellement mappé —
aucune des catégories `orphan_files`/`unassembled_objects` ne s'applique) :
c'est une question d'**organisation éditoriale**. Deux options pour
clarifier : fusionner formellement le thème `CONCENTRATION-LGN` dans
`PROBABILITES` (le BO lui-même présente cette section comme la suite
naturelle de la partie Probabilités), ou déplacer le fichier dans son
propre dossier de chapitre. Décision éditoriale, pas une correction
mécanique — signalé, non traité dans ce lot.

## Vérification spécifique — pas de confusion avec le programme 1SPE 2026

Deux points croisés explicitement avec les trouvailles 1SPE de ce même
audit T2 :

- **Loi binomiale** : confirmée présente et explicitement exigée dans le
  texte TSPE 2019 (schéma de Bernoulli, loi binomiale ℬ(n,p), espérance et
  variance de la loi binomiale — lignes 820, 827-833, 881, 892 du texte
  archivé). En 1SPE 2026, la formalisation nommée est désormais classée
  `OPTIONAL_EXTENSION`; ici c'est un attendu officiel réel du programme
  TSPE 2019 — aucune confusion.
- **Trigonométrie** : le chapitre `TSPE-TRIGONOMETRIE` (2019, en vigueur)
  couvre dérivées/variations/courbes de cosinus et sinus, et la résolution
  d'équations `cos(x)=a` — contenu **distinct** de ce qui a été retiré de
  1SPE 2026 (formules d'addition/duplication, étude complète des fonctions
  cos/sin) et qui rejoindra le futur programme Terminale 2027-2028
  (`backlog_tspe_v2`). Aucun chevauchement ni double-comptage trouvé.

## Ce que cette matrice ne couvre pas encore

Audit scientifique (T4) et pédagogique (T3) — non commencés pour TSPE.
`EXAM_ALIGNMENT` détaillé avec `definition_d_epreuve.TSPE_EPREUVE_SPECIALITE`
(MENE2001796N, partiellement vérifié seulement — durée/calculatrice/nombre
d'exercices non confirmés) — pas encore croisé avec le contenu réel du
manuel.

## Prochaine étape

TCOMPL, TEXPERTES, 1NSI, TNSI restent à construire pour compléter
`PROGRAMME_COVERAGE_MATRIX_COMPLETE_FOR_6_MANUALS`.
