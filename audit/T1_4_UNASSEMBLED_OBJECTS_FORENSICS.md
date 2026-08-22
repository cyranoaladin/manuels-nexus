# T1.4 — forensique des 52 `unassembled_objects`

## Statut

`unassembled_objects` est passé de **52 → 0** en deux lots distincts, tous
deux avec cause racine identifiée et preuve, sans allowlist opaque et sans
suppression de contenu pédagogique unique.

## Lot 1 — 5 objets `1SPE-VARIABLES-ALEATOIRES` : companions `\input`

`Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/cours/15_experimentations.tex`
(id `1SPE-VARALEA-ALG-001`) est sélectionné par les globs `ORDER` déclarés de
l'assembleur du chapitre. Son propre corps `\input` directement les cinq
fichiers de `cours/experimentations/` :

```text
\input{chapitres/1SPE-VARIABLES-ALEATOIRES/cours/experimentations/02_frequences_lettres.tex}
\input{chapitres/1SPE-VARIABLES-ALEATOIRES/cours/experimentations/03_simuler_variable.tex}
\input{chapitres/1SPE-VARIABLES-ALEATOIRES/cours/experimentations/04_fonction_moyenne.tex}
\input{chapitres/1SPE-VARIABLES-ALEATOIRES/cours/experimentations/05_distance_moyenne_esperance.tex}
\input{chapitres/1SPE-VARIABLES-ALEATOIRES/cours/experimentations/06_proportion_2sigma.tex}
```

Ces cinq fichiers portent chacun leur propre `% META` (leur propre `id`,
`type_objet: algorithme`, `status: verified`), donc le scanner d'objets les
traitait comme cinq candidats indépendants, chacun devant apparaître par lui
même dans `included_objects` d'un assemblage déclaré — alors que leur
contenu est déjà réellement présent dans le livre compilé via l'inclusion de
leur parent. `inventory["reference_graph"]` contenait déjà les cinq arêtes
`\input` résolues correspondantes ; seul `add_unassembled_objects()` ne les
consultait pas.

Correctif : `add_unassembled_objects()` (dans `scripts/inventory_assembly.py`)
ferme désormais la clôture des arêtes `\input`/`\include` résolues du graphe
de référence existant depuis chaque `included_objects`, avant de vérifier
l'appartenance. Aucun fichier déplacé ni renommé ; aucun contenu modifié.

RED/GREEN : `tests/test_inventory_collection.py::test_unassembled_objects_excludes_companions_input_by_an_assembled_object`.

## Lot 2 — 47 objets TSPE : doublons obsolètes pré-consolidation

Les 47 objets restants sont tous des fichiers `<CHAPITRE>-COURS-NN.tex`
répartis sur 6 chapitres TSPE (`TSPE-CALCUL-INTEGRAL`, `TSPE-COMBINATOIRE`,
`TSPE-GEOMETRIE-ESPACE`, `TSPE-LOGARITHME`, `TSPE-PRIMITIVES-EQDIFF`,
`TSPE-PROBABILITES`). Chacun coexiste, dans le même dossier `cours/`, avec un
fichier nommé de façon descriptive (`10_definition_integrale.tex`,
`11_C7_fonction_integrale.tex`, etc.) qui, lui, est réellement sélectionné
par l'assembleur.

Vérification automatisée (corps après la ligne `% META`, comparaison
octet-à-octet) : **47/47** fichiers `COURS-NN.tex` ont un corps strictement
identique à celui d'un fichier frère nommé de façon descriptive et
effectivement assemblé dans le même chapitre. Seul le `% META` diffère (id
legacy `<CHAPITRE>-COURS-NN`, champs `capacites`/`statut` legacy en plus de
`capacites_codes`/`status`).

Recherche de toute référence externe à chacun des 47 id legacy
(`git grep`, hors le fichier lui-même) : **0** référence dans tout contenu
pédagogique, contrat, corrigé, exercice, prérequis ou alias de méthode. Les
seules occurrences hors de leur propre fichier sont dans les artefacts
d'audit générés par le pipeline lui-même (`ANOMALIES_BASELINE.json`,
`ANOMALY_DISPOSITIONS.yaml`, `INVENTAIRE_COLLECTION.json`, etc.), qui se
régénèrent automatiquement.

Classification : **OBSOLETE_DUPLICATE**. Ce sont des artefacts d'une
convention de nommage antérieure (numérotation `COURS-NN`), remplacée par le
nommage descriptif actuel, jamais nettoyés du dépôt. Le contenu réel et
unique reste entièrement présent dans les 47 fichiers descriptifs assemblés
— aucun contenu pédagogique unique n'est supprimé en retirant les doublons.

Correctif : suppression des 47 fichiers `<CHAPITRE>-COURS-NN.tex`
énumérés ci-dessous, dans un commit dédié, séparé du correctif de code du
lot 1.

| Fichier doublon (supprimé) | Fichier canonique conservé |
|---|---|
| `TSPE-CALCUL-INTEGRAL/cours/TSPE-CALCUL-INTEGRAL-COURS-01.tex` | `10_definition_integrale.tex` |
| `TSPE-CALCUL-INTEGRAL/cours/TSPE-CALCUL-INTEGRAL-COURS-02.tex` | `11_C7_fonction_integrale.tex` |
| `TSPE-CALCUL-INTEGRAL/cours/TSPE-CALCUL-INTEGRAL-COURS-03.tex` | `12_C2_proprietes_calcul.tex` |
| `TSPE-CALCUL-INTEGRAL/cours/TSPE-CALCUL-INTEGRAL-COURS-04.tex` | `13_C8_integration_par_parties.tex` |
| `TSPE-CALCUL-INTEGRAL/cours/TSPE-CALCUL-INTEGRAL-COURS-05.tex` | `14_C4_aire_entre_courbes.tex` |
| `TSPE-CALCUL-INTEGRAL/cours/TSPE-CALCUL-INTEGRAL-COURS-06.tex` | `15_C5_suites_integrales.tex` |
| `TSPE-CALCUL-INTEGRAL/cours/TSPE-CALCUL-INTEGRAL-COURS-07.tex` | `16_C6_applications.tex` |
| `TSPE-CALCUL-INTEGRAL/cours/TSPE-CALCUL-INTEGRAL-COURS-08.tex` | `10_definition_integrale.tex` |
| `TSPE-COMBINATOIRE/cours/TSPE-COMBINATOIRE-COURS-01.tex` | `10_C1_representations_denombrement.tex` |
| `TSPE-COMBINATOIRE/cours/TSPE-COMBINATOIRE-COURS-02.tex` | `11_C2_principes_permutations_combinaisons.tex` |
| `TSPE-COMBINATOIRE/cours/TSPE-COMBINATOIRE-COURS-03.tex` | `12_C3_somme_coefficients_binomiaux.tex` |
| `TSPE-COMBINATOIRE/cours/TSPE-COMBINATOIRE-COURS-04.tex` | `13_C4_relation_pascal.tex` |
| `TSPE-GEOMETRIE-ESPACE/cours/TSPE-GEOMETRIE-ESPACE-COURS-01.tex` | `10_C1_C2_C4_C5_vecteurs_espace.tex` |
| `TSPE-GEOMETRIE-ESPACE/cours/TSPE-GEOMETRIE-ESPACE-COURS-02.tex` | `11_C3_C6_positions_relatives.tex` |
| `TSPE-GEOMETRIE-ESPACE/cours/TSPE-GEOMETRIE-ESPACE-COURS-03.tex` | `12_C7_produit_scalaire.tex` |
| `TSPE-GEOMETRIE-ESPACE/cours/TSPE-GEOMETRIE-ESPACE-COURS-04.tex` | `13_C12_representation_parametrique_droite.tex` |
| `TSPE-GEOMETRIE-ESPACE/cours/TSPE-GEOMETRIE-ESPACE-COURS-05.tex` | `14_C13_C16_equation_cartesienne_plan.tex` |
| `TSPE-GEOMETRIE-ESPACE/cours/TSPE-GEOMETRIE-ESPACE-COURS-06.tex` | `15_C8_C11_C14_projection_orthogonale.tex` |
| `TSPE-GEOMETRIE-ESPACE/cours/TSPE-GEOMETRIE-ESPACE-COURS-07.tex` | `16_C10_C15_systemes_lieux.tex` |
| `TSPE-GEOMETRIE-ESPACE/cours/TSPE-GEOMETRIE-ESPACE-COURS-08.tex` | `17_C9_longueurs_angles_aires_volumes.tex` |
| `TSPE-GEOMETRIE-ESPACE/cours/TSPE-GEOMETRIE-ESPACE-COURS-09.tex` | `10_C1_C2_C4_C5_vecteurs_espace.tex` |
| `TSPE-GEOMETRIE-ESPACE/cours/TSPE-GEOMETRIE-ESPACE-COURS-10.tex` | `11_C3_C6_positions_relatives.tex` |
| `TSPE-GEOMETRIE-ESPACE/cours/TSPE-GEOMETRIE-ESPACE-COURS-11.tex` | `12_C7_produit_scalaire.tex` |
| `TSPE-GEOMETRIE-ESPACE/cours/TSPE-GEOMETRIE-ESPACE-COURS-12.tex` | `13_C12_representation_parametrique_droite.tex` |
| `TSPE-GEOMETRIE-ESPACE/cours/TSPE-GEOMETRIE-ESPACE-COURS-13.tex` | `14_C13_C16_equation_cartesienne_plan.tex` |
| `TSPE-GEOMETRIE-ESPACE/cours/TSPE-GEOMETRIE-ESPACE-COURS-14.tex` | `15_C8_C11_C14_projection_orthogonale.tex` |
| `TSPE-GEOMETRIE-ESPACE/cours/TSPE-GEOMETRIE-ESPACE-COURS-15.tex` | `16_C10_C15_systemes_lieux.tex` |
| `TSPE-GEOMETRIE-ESPACE/cours/TSPE-GEOMETRIE-ESPACE-COURS-16.tex` | `17_C9_longueurs_angles_aires_volumes.tex` |
| `TSPE-LOGARITHME/cours/TSPE-LOGARITHME-COURS-01.tex` | `10_definition_ln.tex` |
| `TSPE-LOGARITHME/cours/TSPE-LOGARITHME-COURS-02.tex` | `11_C3_derivee_ln.tex` |
| `TSPE-LOGARITHME/cours/TSPE-LOGARITHME-COURS-03.tex` | `12_variations_limites_ln.tex` |
| `TSPE-LOGARITHME/cours/TSPE-LOGARITHME-COURS-04.tex` | `13_C4_limite_xlnx.tex` |
| `TSPE-PRIMITIVES-EQDIFF/cours/TSPE-PRIMITIVES-EQDIFF-COURS-01.tex` | `10_C4_primitives_constante.tex` |
| `TSPE-PRIMITIVES-EQDIFF/cours/TSPE-PRIMITIVES-EQDIFF-COURS-02.tex` | `11_C1_calcul_primitives.tex` |
| `TSPE-PRIMITIVES-EQDIFF/cours/TSPE-PRIMITIVES-EQDIFF-COURS-03.tex` | `12_C5_equation_yprime_ay.tex` |
| `TSPE-PRIMITIVES-EQDIFF/cours/TSPE-PRIMITIVES-EQDIFF-COURS-04.tex` | `13_C2_equation_yprime_ay_b.tex` |
| `TSPE-PRIMITIVES-EQDIFF/cours/TSPE-PRIMITIVES-EQDIFF-COURS-05.tex` | `14_C3_equation_yprime_ay_f.tex` |
| `TSPE-PROBABILITES/cours/TSPE-PROBABILITES-COURS-01.tex` | `10_C1_epreuves_independantes.tex` |
| `TSPE-PROBABILITES/cours/TSPE-PROBABILITES-COURS-02.tex` | `11_C2_C5_schema_bernoulli_binomiale.tex` |
| `TSPE-PROBABILITES/cours/TSPE-PROBABILITES-COURS-03.tex` | `12_C3_C4_utilisation_binomiale.tex` |
| `TSPE-PROBABILITES/cours/TSPE-PROBABILITES-COURS-04.tex` | `13_C6_C7_esperance_linearite.tex` |
| `TSPE-PROBABILITES/cours/TSPE-PROBABILITES-COURS-05.tex` | `14_C8_variance.tex` |
| `TSPE-PROBABILITES/cours/TSPE-PROBABILITES-COURS-06.tex` | `15_C9_esperance_variance_binomiale.tex` |
| `TSPE-PROBABILITES/cours/TSPE-PROBABILITES-COURS-07.tex` | `16_CONCLGN_bienayme_tchebychev.tex` |
| `TSPE-PROBABILITES/cours/TSPE-PROBABILITES-COURS-08.tex` | `10_C1_epreuves_independantes.tex` |
| `TSPE-PROBABILITES/cours/TSPE-PROBABILITES-COURS-09.tex` | `11_C2_C5_schema_bernoulli_binomiale.tex` |
| `TSPE-PROBABILITES/cours/TSPE-PROBABILITES-COURS-10.tex` | `12_C3_C4_utilisation_binomiale.tex` |

(chemins relatifs à `Mathematiques/manuel-maths/chapitres/`)

## Gouvernance

Aucune modification de statut, qualification ou baseline. Les fingerprints
d'anomalie `unassembled_objects` associés se retirent mécaniquement à la
régénération de l'inventaire qui suit chaque lot. Aucun push, aucun merge.
