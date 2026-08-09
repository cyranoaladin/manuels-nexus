# Design - Assembleur canonique du manuel 1NSI

Date : 2026-08-09

## Objectif

Brancher les dix chapitres 1NSI sur un assembleur de manuel suivi et réellement
exécutable, avec les sept variantes canoniques attendues par la matrice des
livrables, sans créer ni modifier un assemblage TNSI.

## Contexte observé

- `NSI/scripts/assemble.py` sait déjà construire un livre 1NSI à partir de
  `NSI/manifests/books/1NSI.json`.
- Le mode livre existant expose `complet`, `methodes`, `remediation` et
  `amenagee`, mais l'inventaire ne reconnaît un assembleur de manuel que sous le
  nom `scripts/assemble_manuel.py`.
- Les dix chapitres 1NSI sont donc signalés hors manuel.
- Les 109 objets 1NSI non assemblés sont tous situés sous `corriges/`.
- La matrice contractuelle exige `eleve`, `professeur`, `methodes`,
  `remediation`, `amenagee`, `evaluations` et `projets`.
- TNSI reste gelé à 6 chapitres sur 12 et demeure hors périmètre.

## Approche retenue

Créer `NSI/scripts/assemble_manuel.py` comme adaptateur canonique dédié. Ce
module porte les déclarations littérales consommées par l'analyse statique et
les utilise aussi à l'exécution. En particulier, un littéral fermé
`VARIANT_ORDERS` associe chaque variante à ses règles de sélection ; l'inventaire
lit ce même littéral par AST au lieu de maintenir une seconde table implicite.
Il réemploie les primitives sûres de chargement, rendu, compilation, préflight
et promotion déjà éprouvées dans `NSI/scripts/assemble.py`.

Cette approche évite de renommer l'assembleur historique de chapitre et évite
d'introduire dans l'inventaire une exception qui interpréterait directement le
manifeste JSON NSI.

## Contrat des variantes

- `eleve` : cours, méthodes, exercices, coups de pouce, TD, projets, QCM et ECE,
  sans évaluations barémées, remédiations corrigées, corrigés ni contenu
  professeur.
- `professeur` : les dix chapitres et tous leurs objets publiables, notamment
  les 109 objets sous `corriges/` actuellement hors assemblage.
- `methodes` : uniquement les objets du répertoire `methodes/`.
- `remediation` : uniquement les objets élèves du répertoire `remediation/` ;
  les corrigés séparés restent réservés à `professeur`.
- `amenagee` : uniquement les objets du répertoire `amenagee/`.
- `evaluations` : les évaluations et leurs corrigés ou barèmes associés ; cette
  banque est rendue en mode professeur.
- `projets` : uniquement les objets du répertoire `projet/`, en mode élève.

Le gabarit de livre reçoit un emplacement fermé de configuration de variante.
Les cinq variantes élèves y injectent `\nxVersionProfesseurfalse` et la
neutralisation du corps de `corrige`. `professeur` et `evaluations` injectent
`\nxVersionProfesseurtrue` sans neutraliser `corrige`. Aucun choix de rôle ne
repose sur une recherche textuelle dans le nom de sortie.

L'alias historique `complet` reste accepté par `assemble.py` pour ne pas casser
les usages existants, mais n'est pas une variante déclarée par l'assembleur
canonique.

## Inventaire et traçabilité

L'inventaire ajoute explicitement `NSI/scripts/assemble_manuel.py` à
l'allowlist des assembleurs suivis. Son analyse statique doit lire :

- un littéral `CHAPITRES` contenant exactement les dix chapitres du manifeste ;
- un littéral `ORDER` couvrant tous les répertoires métier ;
- un littéral `VARIANTS` contenant exactement les sept variantes canoniques ;
- un littéral `VARIANT_ORDERS` donnant les règles effectives des sept variantes ;
- les filtres élève fail-closed exigés par le modèle.

`inventory_assembly.select_items` consomme `VARIANT_ORDERS`, comme l'assembleur
réel. Un test d'intégration compare, variante par variante, la liste ordonnée des
objets META sélectionnés au runtime avec `included_objects` calculé par
l'inventaire. Toute divergence de chemins est bloquante.

## Preflight sensible au rôle

Le préflight commun continue de contrôler journaux LaTeX, métadonnées, outline,
liens et lisibilité pour les sept variantes. Le détecteur de fuite élève est
activé uniquement pour `eleve`, `methodes`, `remediation`, `amenagee` et
`projets`. Il est désactivé explicitement pour `professeur` et `evaluations`, où
les corrigés et barèmes sont contractuels. Cette décision est portée par une
valeur de rôle fermée, jamais déduite du nom du fichier de sortie.

## Builds observés

`audit/BUILD_PRODUCERS.yaml` déclare un producteur 1NSI couvrant exactement les
sept identifiants `nsi:manual:1NSI:<variant>`. Après compilation et préflight,
l'assembleur peut émettre un receipt fermé puis appeler
`scripts/build_manifest.py --receipt`, selon le même contrat de défiance que
l'assembleur mathématique.

Le receipt contient la variante canonique, l'assembly ID, les objets inclus et
exclus, la trace ordonnée, les dépendances générées, les preuves de compilation,
préflight, séparation élève lorsque applicable et reproductibilité. Une
compilation locale sans `--record-observed` reste possible ; elle ne rend pas le
livrable visible dans la matrice.

Les sorties canoniques vivent sous `NSI/build/MANUEL_1NSI/` et sont nommées
`MANUEL_1NSI_<variante>.pdf`, avec une variante parmi les sept valeurs
contractuelles. Le chemin et le champ `variant` du receipt portent donc la même
identité interprétable par l'inventaire. Les anciennes sorties
`NSI/build/books/MANUEL_1NSI_v1*.pdf`, ignorées par Git, restent des sorties de
compatibilité non observées et ne sont jamais utilisées comme preuve canonique.

## Sécurité et erreurs

- Les validations de manifeste et de chemins existantes restent obligatoires.
- Une variante inconnue échoue avant toute écriture.
- Une variante sans aucun objet éligible échoue explicitement.
- Les sorties sont construites en staging, préflightées puis promues ; un échec
  ne laisse pas de PDF canonique périmé.
- Les variantes élèves filtrent les chemins et types professeur avant rendu.
- Un build professeur ou évaluations ne peut pas contourner les contrôles PDF
  communs ; seule la recherche de fuite élève est inapplicable à ces rôles.
- Aucun manifeste, chapitre, source ou sortie TNSI n'est créé ou modifié.

## Vérification

- tests rouges puis verts des sept sélections et du dispatch CLI ;
- test d'inventaire prouvant sept variantes manuelles, dix chapitres couverts,
  zéro chapitre 1NSI hors manuel et zéro objet 1NSI non assemblé ;
- tests d'étanchéité élève et de couverture des 109 corrigés professeur ;
- test de parité exacte entre sélections runtime et inventaire ;
- compilation réelle des sept variantes 1NSI, préflight PDF puis enregistrement
  des sept reçus observés sur un arbre propre ;
- régénération contrôlée de l'inventaire et comparaison de baseline ;
- `--validate-model` et `--fail-on-new` verts ; `--release-strict` reste rouge
  attendu tant que les statuts 1NSI et les autres dimensions de publication ne
  sont pas approuvés ;
- diff TNSI vide sur `NSI/chapitres/TNSI-*`, absence de manifeste TNSI et test
  statique garantissant que TNSI conserve ses seules variantes de chapitre,
  sans assemblage manuel déclaré.

La baseline de dette n'est pas réécrite dans cette passe : les anomalies
résolues sont constatées par comparaison avec la baseline approuvée existante.

## Hors périmètre

- validation disciplinaire ou changement de statut des contenus 1NSI ;
- publication de la collection ;
- assemblage TNSI ;
- modification du contenu pédagogique des chapitres.
