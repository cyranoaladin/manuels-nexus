# Revue scientifique et pedagogique 1NSI

## Contexte

Le perimetre 1NSI contient 339 objets et 10 contrats de chapitre. La
gouvernance actuelle conserve 349 statuts bloquants : 163 objets `verified`,
169 objets `needs_review`, 7 objets `manual_review` et 10 contrats `draft`.
Le statut `verified` prouve seulement une execution technique lorsqu'un recu
Python existe. Il ne constitue ni une validation scientifique, ni une
validation pedagogique, ni une autorisation de publication.

Cette passe doit examiner exhaustivement ces 349 elements sans toucher a TNSI,
aux sept PDF canoniques 1NSI ni aux statuts des sources.

## Autorite et sources officielles

La conformite au programme est evaluee contre les sources primaires suivantes,
consultees le 10 aout 2026 :

- arrete du 17 janvier 2019 fixant le programme de NSI de premiere generale :
  <https://www.legifrance.gouv.fr/loda/id/LEGITEXT000038046340> ;
- programme officiel publie par le ministere, PDF de 9 pages, SHA-256
  `7ca9a32e1823be6c1120cb0417324c3cb01688d1d194c7614a88ea851ccc60b0` :
  <https://www.education.gouv.fr/sites/default/files/document/Programme%20de%20num%C3%A9rique%20et%20sciences%20informatiques%20de%20premi%C3%A8re%20g%C3%A9n%C3%A9rale-248139.pdf> ;
- page Eduscol des programmes et ressources NSI de la voie generale :
  <https://eduscol.education.gouv.fr/5823/programmes-et-ressources-en-numerique-et-sciences-informatiques-voie-g>.

Les documents contractuels locaux applicables sont
`NSI/docs/01_conception_manuel.md`, `NSI/docs/02_workflow_production.md`,
`NSI/docs/05_conventions_latex.md`, `docs/codex/QUALITY_GATES.md` et
`docs/codex/ISSUE_REGISTER_TEMPLATE.md`.

## Decision humaine

La decision du 10 aout 2026 autorise une revue probante scientifique et
pedagogique de 1NSI seulement. Elle n'autorise aucune transition vers
`approved`, `ready` ou `rejected`, aucune acceptation de release et aucune
auto-approbation par l'agent.

Un verdict de revue signifie uniquement que l'agent a examine l'element selon
le protocole et consigne ses preuves. La confirmation humaine independante
reste obligatoire avant toute approbation de publication.

## Livrables

La passe produit quatre surfaces distinctes :

1. `audit/1NSI_CONTENT_REVIEW_POLICY.yaml` decrit le protocole, les sources,
   les dimensions et les transitions interdites.
2. `audit/schemas/v1/1nsi-content-review.schema.json` contraint le registre.
3. `audit/1NSI_CONTENT_REVIEWS.json` contient exactement 349 entrees, avec un
   digest de la source revue et deux verdicts explicites.
4. `audit/1NSI_CONTENT_REVIEW_SUMMARY.md` expose les comptes, les anomalies et
   les decisions encore requises, sans declaration de completude editoriale.

Un generateur deterministe reconstruit le registre a partir des dix contrats,
de leurs objets et des constats de revue structures. Les tests echouent si un
objet ou un contrat manque, si un digest est obsolete, si une entree TNSI
apparait, si une approbation est inferee ou si les comptes ne correspondent
plus aux sources.

## Modele de preuve

Chaque entree enregistre :

- l'identite stable, le chapitre, le type, le chemin et le statut source ;
- le SHA-256 du fichier effectivement lu ;
- les capacites ou references officielles revendiquees ;
- le recu d'execution disponible, sans lui attribuer une portee scientifique ;
- un verdict scientifique, un verdict pedagogique et leurs constats ;
- les identifiants des anomalies ouvertes ;
- l'identite et la nature du relecteur ;
- `publication_approval: false` et
  `human_confirmation_required: true`.

Les verdicts admis sont :

- `pass` : aucun defaut n'a ete releve dans la dimension apres lecture ;
- `issue` : au moins une anomalie ouverte affecte la dimension ;
- `not_applicable` : la dimension ne s'applique pas, avec justification ;
- `human_confirmation_required` : la lecture agent ne suffit pas pour
  trancher un point disciplinaire ou pedagogique sensible.

`pass` n'est jamais synonyme de `approved`. Une entree ne peut etre consideree
comme revue que si les deux dimensions ont un verdict et une justification.

## Axes de revue

### Revue scientifique

La lecture verifie au minimum :

- conformite au programme officiel et etiquetage de tout approfondissement ;
- exactitude des definitions, affirmations et explications ;
- validite et terminaison des algorithmes ;
- coherence des exemples, jeux de donnees et sorties ;
- coherence exercice, aide, corrige et evaluation ;
- executabilite du Python lorsque l'objet contient du code ;
- absence d'hypothese technique trompeuse ou non explicitee.

### Revue pedagogique

La lecture verifie au minimum :

- objectif explicite et adequation de la tache a la capacite visee ;
- progressivite, guidage, charge cognitive et niveau Premiere ;
- clarte des consignes et possibilite de reponse avec les donnees fournies ;
- qualite des distracteurs, aides, remediations et re-tests ;
- coherence entre version eleve et elements reserves au professeur ;
- presence des etapes pertinentes de la boucle Nexus ou justification de leur
  absence ;
- absence d'identifiant interne, placeholder, bareme ou corrige complet dans
  une surface eleve.

## Organisation de la lecture

Les dix chapitres sont repartis entre relecteurs independants en lecture seule.
Chaque relecteur rend des constats structures et reproductibles. Le chapitre
`1NSI-TYPES-CONSTRUITS`, qui concentre 153 objets et des references locales
`1NSI-TYPES-CONSTRUITS-C1` a `C5`, fait l'objet d'un lot dedie. Une revue
transversale controle les dix contrats et le rattachement de leurs capacites au
programme officiel.

L'agent integrateur verifie les chemins, digests, comptes et invariants, mais ne
transforme pas les conclusions des relecteurs en approbation humaine.

## Gestion des anomalies

Chaque anomalie recoit un identifiant stable, une severite, une dimension, une
preuve localisee, une consequence et une action attendue. Une erreur
scientifique, une ambiguite disciplinaire, une capacite sans source officielle,
une fuite professeur vers eleve ou un code publie incoherent est P0 selon les
regles du depot.

Cette passe n'effectue pas de correction de contenu. Les corrections eventuelles
seront des lots atomiques ulterieurs avec tests de regression et seconde revue.
Elle ne modifie donc ni les fichiers de contenu, ni les contrats, ni
`audit/1NSI_STATUS_GOVERNANCE.yaml`.

## Validation

La validation comprend :

- tests cibles du schema et du registre ;
- reconstruction deterministe deux fois et comparaison ;
- controle des 339 objets et 10 contrats ;
- verification de l'absence de chemin ou d'identifiant TNSI ;
- verification que tous les champs d'approbation restent faux ;
- `git diff --check` ;
- gates collection `--check`, `--validate-model` et `--fail-on-new` ;
- execution de `--release-strict`, qui doit rester rouge tant que les 349
  statuts et les autres bloqueurs reels ne sont pas resolus.

## Hors perimetre

Sont explicitement exclus :

- toute modification TNSI ;
- toute transition de statut source ;
- toute correction scientifique ou pedagogique ;
- tout rebuild ou changement de PDF ;
- toute modification de baseline ;
- toute declaration de publication ou de completude.
