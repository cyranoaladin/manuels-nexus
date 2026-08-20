# Ontologie canonique de `% META.type_objet`

## Portée

`CANONICAL_OBJECT_TYPE_ONTOLOGY.yaml` est l’autorité exécutable du champ
source `% META.type_objet`. Elle ne gouverne ni `chunk_type`, ni le rôle source,
ni la section documentaire, ni le sous-type : ces dimensions sont séparées et
seulement croisées par des contraintes explicites.

Ordre d’autorité : conception approuvée, contrats/schémas canoniques, structure
éditoriale officielle, assembleurs/producteurs, usages cohérents, puis audits
historiques.

## Types canoniques au cluster `correction`

| Type | Définition courte | Section(s) | Compteur | Variantes | Assemblage/revue | Alias autorisés | Autorité |
|---|---|---|---|---|---|---|---|
| `amenagee` | version adaptée explicite | `amenagee` | aucun | `amenagee`, professeur | chemin adapté ; statuts inchangés | aucun | corpus, assembleurs |
| `algorithme` | investigation ou implémentation algorithmique exigible | `cours` | `sections_cours` | complet, élève, parcours 1, professeur | explicitement accepté par l’assembleur Math ; statuts inchangés | aucun | conception, assembleur, corpus |
| `cours` | exposition d’un concept | `cours` | `sections_cours` | cours déclarés | politique cours ; statuts inchangés | aucun | structure, assembleurs |
| `methode` | procédure réutilisable | `methodes` | `methodes` | méthodes déclarées | dette A4 inchangée | aucun | conception, structure |
| `exercice` | entraînement élève | `exercices` | `exercices_principaux` | exercices déclarés | sélection élève/prof ; statuts inchangés | aucun | structure, assembleurs |
| `corrige` | correction professeur | `corriges` | `corriges` | professeur, maquette | exclu élève ; statuts inchangés | `correction` | 1386 pairs live, structure |
| `corrige_evaluation` | correction d’évaluation | `evaluations` | `corriges` | évaluations déclarées | politique évaluation | aucun | corpus, assembleurs |
| `evaluation_corrige` | ordre historique corrigé-évaluation | `evaluations` | `corriges` | évaluations déclarées | politique évaluation | aucun | corpus, assembleurs |
| `coup_de_pouce` | indice gradué | `coups_de_pouce`, `exercices` | `coups_de_pouce` | parcours déclarés | visible selon parcours | aucun | conception, corpus |
| `qcm` | QCM d’évaluation/positionnement | `qcm` | `qcm` | QCM déclarés | réponses sous gate | aucun | conception, structure |
| `diagnostic` | diagnostic pédagogique | `cours`, `diagnostics`, `qcm` | `diagnostics` | diagnostic | routage diagnostic | aucun | conception, contrat |
| `diagnostics` | forme plurielle historique | mêmes sections | `diagnostics` | diagnostic | comportement conservé | aucun | contrat existant |
| `qcm_diagnostics` | diagnostic au format QCM | `qcm` | `diagnostics` | QCM déclarés | conserve la forme QCM | aucun | corpus, contrat |
| `remediation` | remédiation ciblée | `remediation` | `remediations` | remédiation/parcours | sélection de parcours | aucun | conception, structure |
| `td` | activité dirigée étendue | `cours` | `td` | cours déclarés | ordre de chapitre | aucun | structure, corpus |
| `evaluation` | évaluation formelle | `evaluations` | `evaluations` | évaluations déclarées | sélection de variante | aucun | conception, structure |
| `projet` | production en mode projet | `projet` | `projets` | projets déclarés | variantes projet | aucun | conception, corpus |

Tous autorisent uniquement le rôle source `production_object`. La représentation
schema est la valeur exacte `META.type_objet=<nom>` ; les détails exhaustifs de
variantes, sous-types, comportement de revue et autorités sont dans le YAML.

## Alias A5

`correction -> corrige` est exact, non ambigu et déprécié. Il n’est valable que
sous `corriges/`, en rôle `production_object`, sans `sous_type`. Les 653 sources
restent inchangées. Le `chunk_type=corrige` des schémas d’ingestion est une
corroboration d’une dimension différente, pas l’autorité de ce champ.

## Sous-types

`diagnostic`, `ouverture`, `td_contextualise` et `td_fil_rouge` restent des
sous-types de `cours`. `ouverture` est explicitement hors compteur ; les trois
autres conservent leurs compteurs existants.

## Valeurs non décidées en A5

`activite`, `methode_guidee` et `auto_evaluation` n’ont aucune occurrence active
dans le snapshot A5. Elles ne sont ni ajoutées ni déclarées définitivement
invalides : une autorité future devra d’abord lever leur dimension et leur
éventuelle ambiguïté.
