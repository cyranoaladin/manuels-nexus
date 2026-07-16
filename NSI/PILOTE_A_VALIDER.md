# PILOTE A VALIDER --- 1NSI-TYPES-CONSTRUITS

PDF : `build/1NSI-TYPES-CONSTRUITS/1NSI-TYPES-CONSTRUITS_complet.pdf` (641 Ko)

## Contenu du chapitre pilote (complet)

| Composant | Quantite | Status |
|---|---|---|
| Cours 3 strates (C1-C5) | 5 sections, 40-70 lignes chacune | needs_review |
| Fiches methodes (M1-M5) | 5 (6 rubriques chacune) | needs_review |
| Exercices (3 parcours) | 55 (P1=24, P2=21, P3=10 -- ratio 44/38/18) | needs_review |
| Corriges copie-modele | 55/55 (100%) | needs_review |
| Coups de pouce | 24 (tous les P1) | needs_review |
| QCM diagnostique | 16 questions, C1-C5 couverts, 27 diagnostics | needs_review |
| Remediation | 5 fiches R1-R5 (1 par capacite) | needs_review |
| Evaluation A | 4 exercices, 55 min, contexte e-sport | needs_review |
| Evaluation B | 4 exercices, 55 min, inventaire/morpion/carnet | needs_review |
| TD 1 | Station meteo, 5 exercices, 50 min (C1/C2/C4) | needs_review |
| TD 2 | Classement tournoi, 5 exercices, 50 min (C2/C3/C4/C5) | needs_review |
| Mini-projet | E-sport, 4 jalons + extensions | needs_review |
| Version amenagee (F11) | Extrait 3 exercices (C1/C2/C5), format trous | needs_review |

## Gates passes (tous VERT en mode strict)

- `make accents` : OK
- `make test` : 165 passed
- `make gates-corpus-strict` :
  - eleve-no-corrige : 73 fichiers, 0 fuite
  - td-corrige alignment : 55/55
  - no placeholders : 0
  - differentiation : P1=44% P2=38% P3=18%
  - QCM : 16 questions, C1-C5

## Sources T0 utilisees

- Sequence P04 : 21 fichiers recoltes, 19 conversions pandoc
- 3 fiches de cours (tuples, listes, dictionnaires)
- Code : starter + corrige_professeur + tests_attendus (3/3 OK)
- Contrat P04_contract.yml
- Verdict substance P-DATA-CONSTR-02A : needs_review (human_review_required)

## Points de jugement humain

1. **Figures memoire (C3, C5)** : schemas TikZ alias/copie/grille. Clairs ?
   Faut-il plus de figures (representation memoire des dictionnaires) ?

2. **Densite des `\codereference`** : un bloc par section de cours, commente.
   Niveau de detail adapte a la Premiere ?

3. **Equilibre transposition/reecriture** : cours transpose du T0 avec
   enrichissement (contre-exemples, EF1-4, figures, "A la machine").
   Ton et progressivite adaptes ?

4. **Distinction code/console** : `python` (fond blanc, filet, numeros) vs
   `console` (fond gris, chevrons >>>). Visuellement suffisant ?

5. **QCM distracteurs** : chaque mauvaise reponse = diagnostic + renvoi
   Mn/Dn/EFn. Format utile ?

6. **Version amenagee** : extrait avec consignes sequencees, trous a completer,
   tableaux a remplir, mise en page aeree. Format adapte aux eleves
   a besoins particuliers ?

7. **Evaluations A/B** : deux sujets de 55 min, 4 exercices chacun, 5 capacites
   croisees. Niveau calibre ? Contextes varies (e-sport/inventaire/morpion) ?

8. **TD thematiques** : station meteo (C1/C2/C4) et classement tournoi
   (C2/C3/C4/C5). Pertinence et difficulte ?

9. **Mini-projet** : 4 jalons progressifs avec criteres testables.
   Extensions ◆◆◆ realistes ?

## Statuts herites (F08)

- P-DATA-CONSTR-02A : needs_review (human_review_required)
- Tous les objets : needs_review (herite du corpus)

## Apres validation

Appliquer les retours, puis enchainer sans arret sur :
Premiere ch. 2-10, Terminale ch. 1-12 + blocs ECE/ecrit, lots finaux.

## Addendum — Ré-attestation du 16/07/2026

PDF recompilé : 34 pages, 213 Ko (précédemment 641 Ko). Le maître
`build/1NSI-TYPES-CONSTRUITS/1NSI-TYPES-CONSTRUITS_complet.tex` est décompté par
occurrences de `\input` et `\include`, sans dépendre de l'indentation.

| Objet | Attendu | Constaté | Preuve |
|---|---:|---:|---|
| Exercices / corrigés / CDP | 55 / 55 / 24 | 55 / 55 / 24 | `exercices/`, `corriges/`, `coups_de_pouce/` |
| QCM / remédiations | 16 / 5 | 16 / 5 | `qcm/`, `remediation/` |
| Évaluations | 2 | 2 | `evaluations/` |
| TD / projet | 2 / 1 | 2 / 1 | maître lignes 94–96 ; `cours/07_td1_station_meteo.tex`, `cours/07_td2_classement_esport.tex`, `projet/1NSI-TC-PROJET.tex` |

Le précédent total « td 0 / projets 0 » était un artefact : son parcours de
répertoires ne comptait ni les TD stockés sous `cours/07_td*.tex` ni `projet/`.
L'inventaire est identique. `pdffonts` confirme des polices embarquées et en
sous-ensembles (`emb=yes`, `sub=yes`) ; cette sous-division explique
probablement la baisse 641 Ko → 213 Ko en l'absence de l'ancien PDF comparé.
