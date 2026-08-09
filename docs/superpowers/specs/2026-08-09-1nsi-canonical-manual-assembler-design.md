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
les utilise aussi à l'exécution. Il réemploie les primitives sûres de
chargement, rendu, compilation, préflight et promotion déjà éprouvées dans
`NSI/scripts/assemble.py`.

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

L'alias historique `complet` reste accepté par `assemble.py` pour ne pas casser
les usages existants, mais n'est pas une variante déclarée par l'assembleur
canonique.

## Inventaire et traçabilité

L'inventaire ajoute explicitement `NSI/scripts/assemble_manuel.py` à
l'allowlist des assembleurs suivis. Son analyse statique doit lire :

- un littéral `CHAPITRES` contenant exactement les dix chapitres du manifeste ;
- un littéral `ORDER` couvrant tous les répertoires métier ;
- un littéral `VARIANTS` contenant exactement les sept variantes canoniques ;
- les filtres élève fail-closed exigés par le modèle.

Les sélections spécialisées `evaluations` et `projets` sont reconnues à la fois
par l'assembleur réel et par `inventory_assembly.select_items`, afin que la
déclaration auditée corresponde à la construction exécutée.

## Sécurité et erreurs

- Les validations de manifeste et de chemins existantes restent obligatoires.
- Une variante inconnue échoue avant toute écriture.
- Une variante sans aucun objet éligible échoue explicitement.
- Les sorties sont construites en staging, préflightées puis promues ; un échec
  ne laisse pas de PDF canonique périmé.
- Les variantes élèves filtrent les chemins et types professeur avant rendu.
- Aucun manifeste, chapitre, source ou sortie TNSI n'est créé ou modifié.

## Vérification

- tests rouges puis verts des sept sélections et du dispatch CLI ;
- test d'inventaire prouvant sept variantes manuelles, dix chapitres couverts,
  zéro chapitre 1NSI hors manuel et zéro objet 1NSI non assemblé ;
- tests d'étanchéité élève et de couverture des 109 corrigés professeur ;
- compilation réelle des sept variantes 1NSI et préflight PDF ;
- régénération contrôlée de l'inventaire et comparaison de baseline ;
- `--validate-model`, `--fail-on-new` et `--release-strict` ;
- diff TNSI vide sur `NSI/chapitres/TNSI-*` et absence de manifeste TNSI.

## Hors périmètre

- validation disciplinaire ou changement de statut des contenus 1NSI ;
- publication de la collection ;
- assemblage TNSI ;
- modification du contenu pédagogique des chapitres.
