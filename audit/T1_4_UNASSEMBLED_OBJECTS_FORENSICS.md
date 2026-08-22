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

## Ledger complet et invariants (preuve par fichier)

Le ledger machine complet des 47 suppressions — `deleted_path`,
`deleted_blob_sha`, `canonical_survivor_path`, `canonical_survivor_blob_sha`,
`byte_identical`, `deleted_inbound_refs`, `deleted_outbound_unique_refs`,
`deleted_unique_META`, `deleted_receipt_or_review`,
`deleted_historical_authority`, `deleted_manifest_entry`,
`canonical_survivor_assembled` — est dans
`audit/T1_4_DELETION_LEDGER.json` (47 entrées). Résumé vérifié :

```text
byte_identical            = 47/47 YES
canonical_survivor_assembled = 47/47 YES
deleted_inbound_refs       = 0/47 (git grep sur le chemin exact, hors
                              artefacts d'audit auto-générés)
deleted_outbound_unique_refs = 0/47 (corps identique => mêmes cibles)
deleted_historical_authority = 0/47
deleted_manifest_entry     = 0/47 (aucun chemin supprimé dans
                              audit/BUILD_MANIFEST.json)
```

### `deleted_unique_META` : ce qui diffère réellement, et pourquoi ce n'est pas une perte

Seuls quatre champs META divergent jamais entre un fichier supprimé et son
canonique : `id`, `capacites` (legacy), `capacites_codes`, `statut`
(legacy). Trois preuves ferment ce point :

1. **`statut` legacy** : **47/47** fichiers supprimés portent
   `"statut": "structure"` (stade de structure/brouillon). **47/47**
   canoniques survivants portent `"status": "approved"`. Le contenu
   supprimé n'a jamais dépassé le stade de brouillon structurel ; le
   contenu réellement approuvé et publié est entièrement dans les
   canoniques.
2. **`capacites_codes`** diverge sur **40/47** paires. Dans ces 40 cas,
   le code legacy est systématiquement `["C<N>"]` où `N` est le numéro
   extrait du nom de fichier supprimé lui-même
   (`...-COURS-07.tex` → `["C7"]`) — un placeholder séquentiel 1-pour-1
   posé au moment du brouillon, indépendant du contenu réel. Le fichier
   canonique, lui, porte le ou les codes de capacité effectivement
   présents dans son nom descriptif
   (`13_C8_integration_par_parties.tex` → `["C8"]` ou
   `["C8","C2"]`) — cohérent avec son propre contenu. Aucune capacité
   n'est donc perdue : la classification exacte est celle du canonique ;
   celle du brouillon était un espace réservé, jamais une classification
   réelle.
3. **`capacites` legacy** (7/47 seulement, ancien format à préfixe
   `<CHAPITRE>-C<N>`) : même conclusion, préfixe redondant du chapitre déjà
   porté par `chapitre` et par le chemin.

`CONTENT_LOSS = 0` (corps octet-identique), `PROVENANCE_LOSS = 0` (aucune
autorité/committment historique unique dans les 47 fichiers supprimés).

### `deleted_receipt_or_review` : trouvaille et disposition

Contrairement à une hypothèse initiale de zéro absolu, **80** entrées de
`audit/BASELINE_QUALIFICATION_REGISTRY.yaml` référencent l'un des 47 chemins
supprimés comme `source` (`disposition: open_debt`,
`approved_by: Alaeddine Ben Rhouma`, catégories `unassembled_objects` et
`broken_meta_references`). Ce ne sont **pas** des revues de contenu
pédagogique : ce sont des qualifications de **dette de release** —
l'acceptation gouvernée du fait que l'anomalie existait et ne bloquait pas
la release dans l'intervalle. Rien n'y atteste une lecture ou une
approbation du contenu pédagogique lui-même.

Supprimer la source qui causait l'anomalie est précisément la résolution
attendue de ce type de dette : l'anomalie qualifiée devient obsolète parce
que sa cause a été traitée, pas parce qu'elle a été masquée. Après
suppression :

- `--check --validate-model --require-clean` : **rc 0** ;
- `--check --fail-on-new --require-clean` : **rc 0**, `new=0`,
  `regressions=0`, `failures=0`.

Aucun des deux gates ne signale les 80 entrées désormais orphelines comme
une incohérence détectée. `REVIEW_LOSS = 0` au sens où aucune revue de
contenu n'est perdue ; mais ces 80 entrées de
`BASELINE_QUALIFICATION_REGISTRY.yaml` restent, elles, désormais orphelines
(leur `source` n'existe plus) et n'ont pas été nettoyées dans ce lot — ce
nettoyage relève de l'hygiène de gouvernance (proche de T7, dette de
statut/reviews), pas de la fermeture technique de `unassembled_objects`.
Signalé explicitement plutôt que silencieusement laissé de côté.

## Gouvernance

Aucune modification de statut, qualification ou baseline effectuée dans ce
lot. Les fingerprints d'anomalie `unassembled_objects` associés se
retirent mécaniquement à la régénération de l'inventaire qui suit chaque
lot. Les 80 entrées de dette désormais orphelines dans
`BASELINE_QUALIFICATION_REGISTRY.yaml` sont documentées ci-dessus comme
reste à traiter (T7), non promues, non supprimées. Aucun push, aucun
merge.
