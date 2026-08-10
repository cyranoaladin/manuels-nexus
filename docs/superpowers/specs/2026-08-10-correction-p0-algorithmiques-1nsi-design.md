# Correction des trois P0 algorithmiques 1NSI

## Objectif

Corriger atomiquement les trois P0 algorithmiques identifies par la revue
scientifique et pedagogique 1NSI :

- `1NSI-REV-ADGK-C2-DOCSTRING-OPTIMALITE` ;
- `1NSI-REV-AGT-C2-BORNE-TERMINAISON` ;
- `1NSI-REV-AGT-QCM-Q2-AMBIGU`.

La passe ne modifie ni les statuts, ni TNSI, ni les sources associees aux
autres anomalies. La suppression de la contradiction gloutonne resout aussi,
par consequence directe, le P1 pedagogique
`1NSI-REV-ADGK-C2-CONTRADICTION`.

## Corrections

### Algorithme glouton

Conserver l'algorithme pedagogique actuel et retirer toute garantie generale de
minimalite. L'exemple d'introduction decrit l'objectif du rendu de monnaie et la
docstring decrit le choix glouton. La propriete et le contre-exemple existants
restent l'autorite sur l'absence d'optimalite generale.

### Terminaison du tri par insertion

Remplacer la borne incorrecte par une preuve explicite. La boucle externe
execute `max(n - 1, 0)` iterations et les cas `n <= 1` sont deja tries.
Pour `n >= 2`, `j` peut atteindre `-1`, tandis que le variant entier
`j + 1` reste positif avant chaque tour execute et decroit strictement. La
boucle interne termine donc apres un nombre fini de decalages.

### QCM du maximum

Conserver une seule reponse exacte : initialiser le maximum avec le premier
element d'un tableau non vide. Remplacer le dernier element, egalement valide
avec un parcours adapte, par le distracteur « le nombre d'elements du
tableau », incontestablement faux en general.

## Tests

Ajouter trois tests de regression ciblant les sources publiees. Les tests sont
observes rouges avant correction, puis verts apres correction. Ils verifient :

- l'absence de promesse generale de minimalite dans la docstring gloutonne ;
- la presence de `max(n - 1, 0)`, du variant `j + 1`, de la borne `-1`, du
  traitement de `n <= 1` et de la conclusion conditionnelle `n >= 2` dans la
  preuve ;
- les quatre options exactes et ordonnees du bloc Q2, dont « premier element »
  et « nombre d'elements du tableau », sans conserver « derniere valeur ».

Les tests de corpus et d'execution des deux chapitres sont ensuite rejoues.

## Revue et validation

Le commit source contient seulement les trois corrections et leurs tests. Une
seconde revue independante intervient ensuite sur ce commit immuable.

Le chemin canonique
`audit/reviews/1nsi/runs/2026-08-10-algorithms.yaml` est deja ferme dans le
protocole. Pour ne pas modifier l'allowlist ni invalider le digest du protocole,
le second relecteur reatteste les 40 objets du lot algorithmique dans une
nouvelle version complete de ce recu. Les 37 constats non affectes sont relus
et conserves seulement s'ils restent valides ; les trois constats corriges sont
remplaces par leurs verdicts et preuves courants.

Le nouveau recu est scelle dans un commit dedie. Un commit suivant met a jour
la provenance des 40 findings, retire les trois P0 et le P1 de contradiction
resolus, puis regenere le registre JSON et la synthese. Les anciens blobs
restent tracables dans l'historique Git. Ces deux commits forment une migration
ordonnee : le premier est volontairement rouge sur la seule provenance
historique devenue obsolete, et le second retablit le registre. Creer un
nouveau chemin de recu est exclu, car son ajout a l'allowlist changerait le
digest du protocole et invaliderait les 349 revues.

Le manifeste du recu scelle les octets des sources, leurs dependances et les
versions des verificateurs. Les faits `computed_result` consignent les
executions fraiches. Le relecteur doit differer du relecteur initial et de
l'integrateur. Le commit de scellement a pour parent direct le commit source,
ce qui rattache la reattestation a la correction immuable.

`--verify-scope` de la passe de revue initiale reste inchange et rouge pour
des modifications de sources, comme prevu par son contrat. Il n'est pas
affaibli pour cette correction. La validation finale utilise le schema, les
tests de revue, la reconstruction `--check`, les tests NSI et les gates
d'inventaire.

La seconde revue ne modifie aucun statut et ne vaut pas approbation de
publication.

Le commit de contenu reste atomique et utilise le prefixe `[PEDAGOGIE]`.
