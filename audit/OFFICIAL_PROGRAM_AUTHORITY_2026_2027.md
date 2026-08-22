# Autorité programme officiel — édition 2026-2027

Vérifié le 2026-08-22. Sources exclusives : Bulletin officiel
(education.gouv.fr), Légifrance (JORF), Éduscol. Détail complet et URLs
dans `audit/OFFICIAL_PROGRAM_AUTHORITY_2026_2027.yaml`, structuré en trois
namespaces jamais mélangés : `programme_d_enseignement` (ce qui doit être
enseigné), `definition_d_epreuve` (durée/structure/pondération),
`sujets_d_examen` (preuves empiriques, jamais une autorité de contenu).

## A. Programme d'enseignement — synthèse

| Manuel | Programme applicable 2026-2027 | Texte | BO | Entrée en vigueur | Changement 2026-2027 ? |
|---|---|---|---|---|---|
| **1SPE** | Nouveau (2026) | MENE2602917A | n°14 du 02-04-2026 | rentrée 2026-2027 | **OUI** — seul manuel concerné |
| **TSPE** | 2019, inchangé | MENE1921246A | spécial 8 du 25-07-2019 | rentrée 2020 | NON (nouveau texte MENE2602919A différé à 2027-2028) |
| **TCOMPL** | 2019, inchangé | MENE1921265A | spécial 8 du 25-07-2019 | rentrée 2020 | NON (nouveau texte MENE2902920A différé à 2027-2028) |
| **TEXPERTES** | 2019, inchangé | MENE1921264A | spécial 8 du 25-07-2019 | rentrée 2020 | NON — aucun nouveau texte trouvé |
| **1NSI** | 2019, inchangé | MENE1901633A | spécial 1 du 22-01-2019 | rentrée 2019 | NON — aucun nouveau texte trouvé |
| **TNSI** | 2019, inchangé | MENE1921247A | spécial 8 du 25-07-2019 | rentrée 2020 | NON pour le programme |

Seul 1SPE change de programme. Confirmé texte à l'appui (article 2 des
arrêtés) : les nouveaux textes Terminale/complémentaires 2026 n'entrent en
application qu'à la rentrée **2027-2028**, pas 2026-2027.

## B. Définition d'épreuve — synthèse

| Manuel | Épreuve | Statut | Détail |
|---|---|---|---|
| **1SPE** | Épreuve anticipée maths | Structure confirmée, session 2028 non nommément trouvée | 2h, coeff 2, sans calculatrice, QCM 6pts + 2-3 exercices 14pts. Texte session 2027 confirmé (MENE2515469N) ; continuité vers 2028 = inférence raisonnable, pas confirmation positive. |
| **TSPE** | Épreuve spécialité Terminale | Partiellement confirmée | Note /20, barème par exercice 4-8 pts (MENE2001796N). Durée, calculatrice, nombre d'exercices, coefficient 16 : non re-confirmés cette passe (fetch 403, pas de miroir trouvé). |
| **TCOMPL** | — | Confirmé : **contrôle continu** | MENE2215445N, coefficient 2. Pas d'épreuve terminale — ne pas en inventer une. |
| **TEXPERTES** | — | Confirmé : **contrôle continu** | Même autorité et régime que TCOMPL. |
| **TNSI** | Épreuve spécialité | Confirmé, avec correction | MENE2516123N. Écrit 3h30 (poids 0,75, note /20) + pratique 1h (poids 0,25, note /20) → moyenne pondérée, PAS deux notes littéralement sur 15 et 5. |
| **1NSI** | — | N/A | Pas d'épreuve terminale en Première pour la spécialité NSI (évaluée en Terminale uniquement). |

### Correction importante — pondération TNSI

Le stockage initial (`written_points=15`, `practical_points=5`) était
incorrect : il suggérait deux épreuves notées directement sur 15 et 5. Le
texte réel définit deux épreuves notées chacune **sur 20**, combinées par
une **pondération** 0,75 (écrit) / 0,25 (pratique). La formulation "15/20 +
5/20" reste utilisable comme *explication pédagogique* de la contribution
équivalente, jamais comme échelle de stockage.

### Ambiguïté réelle non fermée — 1SPE session 2028

Le mandat identifie correctement 1SPE comme le manuel changeant de
programme, mais les élèves de Première 2026-2027 (cohorte de cette édition)
passeront l'épreuve anticipée au titre de la **session 2028**, pas 2027.
Seul un texte "session 2027" (MENE2515469N, cohorte Première 2025-2026) a
été trouvé et confirmé. La continuité de la structure d'épreuve
(2h/coeff2/QCM6+14) au-delà de 2027 est une inférence raisonnable (page
évergreen education.gouv.fr décrivant la réforme structurellement, pas
annuellement) mais pas une confirmation positive par un texte "session
2028" nommément daté — ce texte n'existe peut-être simplement pas encore
(généralement publié l'année précédente). **Signalé, non bloquant pour la
suite** : à revérifier avant publication finale.

## C. Sujets d'examen — règle stricte

`SUBJECT_2026_PROGRAM_AUTHORITY = FALSE`. Les sujets de juin 2026
correspondent à l'année scolaire 2025-2026 (ancien programme 1SPE 2019),
pas au nouveau programme MENE2602917A (entrée en vigueur septembre 2026).
Usage autorisé : format, durée, style, organisation — jamais preuve de
couverture de contenu du nouveau programme.

## Corrections apportées à ce lot

- NOR du futur programme TCOMPL 2026 (hors périmètre 2026-2027) corrigé de
  `MENE2602920A` à **`MENE2902920A`** (URL réellement servie par
  education.gouv.fr).
- Pondération TNSI corrigée (poids 0,75/0,25 sur échelles /20, pas deux
  notes littérales sur 15 et 5).
- Régime d'évaluation TCOMPL/TEXPERTES confirmé : contrôle continu
  (MENE2215445N), pas d'épreuve terminale inventée.

## Cohérence avec le registre opérationnel

Aucune contradiction trouvée avec `docs/programmes/PROGRAMMES_2026_2027.yaml`
sur les points qu'il couvre déjà. Ce fichier d'audit ajoute la séparation
programme/épreuve/sujets et les trouvailles ci-dessus ; il ne remplace pas
le registre opérationnel, qui reste la source consommée par le pipeline
d'inventaire.

## Prochaine étape

Construire la matrice programme ↔ manuel exhaustive et atomisée
(classification MANDATORY_KNOWLEDGE / MANDATORY_SKILL /
MANDATORY_ALGORITHM_OR_PROCEDURE / MANDATORY_EXPECTED_CAPACITY /
IMPLEMENTATION_GUIDANCE / HISTORY_CONTEXT / OPTIONAL_EXTENSION /
EXPLICIT_LIMITATION / OTHER_OFFICIAL, avec `mandatory_for_coverage`
justifié) pour 1SPE en premier, recalculée directement contre le texte
MENE2602917A (`Mathematiques/manuel-maths/sources/txt/BO2026_1SPE_specialite.txt`,
déjà déposé et empreinté) — pas réutilisée depuis `CONFORMITE_BO2026.md`
comme preuve intrinsèque. Puis les cinq autres manuels.
