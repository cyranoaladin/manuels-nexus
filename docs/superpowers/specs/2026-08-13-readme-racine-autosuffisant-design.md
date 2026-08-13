# Conception — README racine autosuffisant pour audit

**Date :** 13 août 2026  
**Statut :** conception approuvée par l'utilisateur  
**Branche :** `integration/1spe-bo2026-traceability`  
**Point de départ :** `b5c6f9f113dc7be0b33765bb6229b6d4e6611467`  
**Approche retenue :** manuel d'audit en couches

## 1. Objectif

Créer à la racine du dépôt un `README.md` suffisamment complet pour qu'un
auditeur découvrant le projet puisse comprendre, sans autre préalable :

- la mission et la logique métier de la collection Nexus Réussite ;
- le périmètre des six manuels 2026-2027 ;
- le cahier des charges et la hiérarchie d'autorité ;
- le modèle pédagogique Nexus ;
- l'architecture éditoriale et technique ;
- l'arborescence du dépôt ;
- la chaîne de production LaTeX/PDF ;
- les variantes élève et professeur ;
- les sources réglementaires ;
- les workflows de développement, de validation et de release ;
- l'état d'avancement observé ;
- les gates verts et rouges ;
- les risques, P0 et décisions humaines ;
- la procédure permettant de reproduire l'audit.

Le README doit être autosuffisant pour la compréhension, sans remplacer les
documents qui font juridiquement ou techniquement autorité.

## 2. Décision éditoriale

L'utilisateur a approuvé l'approche A « manuel d'audit en couches » :

1. un résumé opérationnel lisible en quelques minutes ;
2. une description durable et exhaustive du projet ;
3. un instantané daté de l'état réel avec preuves et commandes de reproduction.

Le document peut être long si la longueur sert l'autonomie de l'auditeur. La
cible indicative est de 600 à 800 lignes, sans obligation artificielle : la
complétude et l'absence de répétition priment.

Les alternatives suivantes sont explicitement écartées pour cette tranche :

- README court reposant principalement sur des renvois ;
- copie intégrale du cahier des charges de 1 141 lignes ;
- générateur automatique du bloc d'état ;
- refonte simultanée des README disciplinaires ;
- correction des défauts métier, réglementaires, LaTeX ou de gouvernance
  signalés dans le README.

## 3. Rôle documentaire

Le README est un portail et un document de passation. Il ne devient pas une
nouvelle source contractuelle concurrente.

Il affiche l'ordre d'autorité suivant :

1. textes officiels en vigueur ;
2. `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md` ;
3. `AGENTS.md` applicable au fichier ;
4. schémas, contrats et gates machine ;
5. décisions humaines approuvées ;
6. rapports recalculés depuis les sources et builds ;
7. documents historiques.

Si un chiffre ou une affirmation du README contredit une source d'autorité, un
build ou un test observé, le README est faux et doit être corrigé.

## 4. Public cible

Le document s'adresse en priorité à :

- un auditeur externe technique, pédagogique ou disciplinaire ;
- un mainteneur découvrant le dépôt ;
- un relecteur programme ;
- un relecteur LaTeX/PDF ;
- un agent de développement ou d'audit ;
- le responsable humain appelé à approuver un manuel.

Le lecteur est supposé maîtriser Git et les principes généraux d'une chaîne de
build, mais pas le vocabulaire Nexus ni l'histoire du dépôt.

## 5. Architecture d'information

### 5.1 En-tête et alerte immédiate

Le document commence par :

- le nom de la collection ;
- une phrase de mission ;
- un avertissement visible `NO-GO publication` ;
- la date, le SHA et la branche de l'état présenté ;
- la distinction entre PDF présent, build observé et release ;
- un lien vers `audit/AUDIT_ETAT_PROJET_2026-08-13.md`.

Aucun badge vert ou formulation « prêt » ne doit apparaître si les preuves
correspondantes sont rouges ou absentes.

### 5.2 Le projet en 90 secondes

Cette synthèse affiche les valeurs observées :

- 6 manuels ;
- 51 chapitres ;
- 2 860 objets ;
- 12 PDF canoniques ;
- 2 026 pages ;
- 0 chapitre `READY` ;
- 2 911 entrées objet/contrat non publiables ;
- 67 bloqueurs `release-strict` ;
- 0 build observé.

Elle résume également le modèle : sources officielles, capacités, contrats,
objets, assemblage, preuves de build, gates, revues, approbation humaine.

### 5.3 Mission et définition du produit

Le README explique que la collection vise simultanément :

- exactitude disciplinaire ;
- conformité aux programmes applicables ;
- pédagogie différenciée Nexus ;
- séparation élève/professeur ;
- code Python exécuté et sorties prouvées ;
- qualité graphique, LaTeX et PDF ;
- reproductibilité depuis un clone propre ;
- traçabilité des décisions et preuves ;
- publication numérique et imprimée ;
- validation humaine finale.

La définition de « terminé » condense les critères contractuels sans recopier
mot pour mot l'intégralité du cahier des charges.

### 5.4 Périmètre des six manuels

Un tableau donne pour chaque manuel : identifiant, niveau, discipline,
chapitres, objets et pages des variantes élève/professeur.

| Manuel | Chapitres | Objets | Pages élève/professeur |
|---|---:|---:|---:|
| `1SPE` | 10 | 1 401 | 361 / 601 |
| `TSPE_2026_2027` | 11 | 768 | 179 / 250 |
| `TCOMPL` | 9 | 150 | 66 / 80 |
| `TEXPERTES` | 5 | 93 | 42 / 52 |
| `1NSI` | 10 | 339 | 109 / 171 |
| `TNSI` | 6 | 109 | 48 / 67 |

Les ressources annexes sont distinguées des éditions canoniques.

### 5.5 Logique métier

Le flux métier est rendu visible :

```text
texte officiel
  -> capacité atomique et référentiel
  -> contrat de chapitre
  -> objets pédagogiques identifiés et statutés
  -> assemblage élève/professeur
  -> compilation LaTeX et préflight PDF
  -> reçu et manifeste observé
  -> inventaire, gates et revues indépendantes
  -> approbation humaine
  -> release
```

Le document définit les termes : capacité, objet, contrat, statut, assemblage
déclaré, build observé, manifeste, gate, baseline, disposition, `READY` et
release candidate.

### 5.6 Pédagogie Nexus

Les onze étapes obligatoires sont expliquées : diagnostic, orientation, cours
essentiel, exemple expert, guidage estompé, entraînement, preuve de maîtrise,
remédiation, re-test, réactivation et transfert.

Le document décrit les parcours Consolidation, Maîtrise et Approfondissement,
les évaluations A/B et la cible d'exercices :

`min(50, max(24, 6 × nombre_de_capacités))`.

Cette cible est présentée comme une exigence de la conception approuvée, pas
comme une preuve qu'elle est déjà atteinte.

### 5.7 Architecture éditoriale d'un chapitre

Le README décrit la structure cible complète : ouverture, contrat, diagnostic,
orientation, cours, démonstrations, méthodes, exercices, TD ou fil rouge,
auto-évaluation, diagnostic d'erreurs, remédiation, re-test, évaluations A/B,
réactivation, transfert et ressources professeur.

Il distingue explicitement la cible contractuelle de l'état observé.

### 5.8 Programmes officiels

Un tableau présente par manuel : texte applicable, référence, année d'effet,
source déposée ou non et réserve actuelle.

Le README utilise les références vérifiées :

- 1SPE 2026 : `MENE2602917A` ;
- épreuve anticipée 2027 : `MENE2515469N` ;
- TSPE 2019 : `MENE1921246A` ;
- TCOMPL 2019 : `MENE1921265A` ;
- TEXPERTES 2019 : `MENE1921264A` ;
- 1NSI 2019 : `MENE1901633A` ;
- TNSI 2019 : `MENE1921247A`.

Il indique que le registre courant contient encore par erreur `MENE1921262A`
pour TSPE et que cette référence correspond à STMG. Il ne masque donc pas le
P0 réglementaire.

Il signale aussi que le registre courant ne porte encore ni NOR ni URL pour la
source 1NSI, bien que le BO officiel soit identifié. Cette tranche documente
l'écart sans modifier le registre.

Les modalités d'épreuve dont `source_deposee` vaut `false` ne sont pas
présentées comme officiellement prouvées.

### 5.9 Variantes et ressources

Deux éditions canoniques assemblées sont décrites pour chaque manuel : élève et
professeur.

La variante élève exclut corrigés, barèmes, notes professeur, identifiants
internes, placeholders et renvois provisoires. La variante professeur porte
les corrigés détaillés, diagnostics, barèmes et conseils de différenciation.

Les livrets, banques, sujets et ressources sont des artefacts séparés. Les 22
assemblages encore déclarés dans `audit/BUILD_PRODUCERS.yaml` sont présentés
comme une contradiction de gouvernance à résoudre, non comme la surface
canonique acceptée.

### 5.10 Arborescence commentée

Le README montre une arborescence courte et stable. Il ne liste pas
l'ensemble exhaustif des fichiers suivis. Il explique le rôle des chemins
structurants :

- `Mathematiques/manuel-maths/` ;
- `NSI/` ;
- `scripts/` et `tests/` racine ;
- `audit/` ;
- `docs/programmes/` ;
- `docs/codex/` ;
- `docs/superpowers/` ;
- `.github/workflows/`.

`NSI/corpus_nsi/` est qualifié de matière première importée par subtree, jamais
de contenu approuvé par défaut.

### 5.11 Architecture technique

Le document explique :

- les métadonnées `% META:` des objets `.tex` ;
- les contrats YAML et schémas JSON ;
- l'assembleur Mathématiques piloté par des listes Python ;
- l'assembleur NSI piloté par `NSI/manifests/books/*.json` ;
- les scripts transversaux d'inventaire et de gouvernance ;
- les PDF canoniques sous `build/` ;
- la différence entre analyse statique et preuve de build.

### 5.12 Charte graphique v5/v6

La pile réelle est décrite sans surévaluer la migration :

```text
nexus-manuel.cls historique
  -> nexus-manuel-v5.cls
    -> nexus-charte-v6.sty et modules v6
      -> nexus-pont-v6.sty
```

Le README explique le pont, la nécessité d'au moins trois passes LuaLaTeX, les
neuf modules v5/v6 identiques mais physiquement dupliqués, les divergences
disciplinaires, le gate `check_charte_sync.py` rouge et incomplet et la cible
future d'un noyau commun avec surcharges explicites.

### 5.13 Installation et commandes de build

Les prérequis actuels sont listés : Python 3.12, LuaLaTeX/TeX Live, polices,
Poppler, qpdf et Pandoc lorsque nécessaire côté NSI.

Seules les commandes existantes et vérifiées par `--help`, Makefile ou CI sont
documentées. Les commandes cibles encore absentes du cahier des charges ne sont
pas présentées comme disponibles.

Les builds locaux sont séparés des builds `--record-observed`. Le README avertit
que ce dernier mode écrit des preuves et le manifeste global et doit être lancé
intentionnellement sur un arbre propre.

### 5.14 Tests, gates et CI

Le document couvre les familles structure, discipline, programme, pédagogie,
Python, variantes, LaTeX/visuel, PDF, reproductibilité et release.

Il explique :

- `--fail-on-new` contrôle la non-régression de dette ;
- une baseline n'est pas une acceptation de qualité ;
- `--release-strict` contrôle la publiabilité ;
- les codes non nuls actuels sont des faits à conserver.

Les trois workflows CI sont présentés avec leurs limites actuelles : ancienne
branche de push pour l'audit, filtres incomplets de charte et absence de build
des douze manuels complets.

### 5.15 Workflow de contribution

La procédure comprend : lecture des règles, état Git, préservation du WIP,
diagnostic, conception approuvée, plan détaillé en étapes de 2 à 5 minutes,
validation humaine du plan, TDD lorsqu'il s'agit de code ou d'un défaut,
correction minimale, parallélisation par sous-agents des tâches réellement
indépendantes, tests ciblés, gates affectés, revue indépendante, points de
validation utilisateur, commit atomique et compte rendu.

Les interdictions Git et les préfixes de commit contractuels sont résumés.

### 5.16 État courant audité

Le bloc d'état est encadré par :

```text
<!-- BEGIN CURRENT AUDITED STATE -->
<!-- END CURRENT AUDITED STATE -->
```

Il reste manuel dans cette tranche. Les marqueurs préparent une automatisation
future sans créer de générateur.

Le bloc porte la date, l'état métier audité `1d0c3fda`, le commit de rapport
`b5c6f9f1`, la branche et les faits : 0 `READY`, 2 911 entrées bloquantes, 67
bloqueurs release, 119 nouvelles empreintes, 119 qualifications manquantes,
manifeste vide, P0, tests rouges et limites PDF.

### 5.17 Roadmap, décisions et questions ouvertes

Les vagues approuvées 0 à 4 sont décrites. L'état est « Wave 0 incomplète et à
restabiliser », sans pourcentage inventé.

Les décisions humaines approuvées sont listées avec leurs identifiants. Elles
ne sont pas présentées comme des validations scientifiques ou de release.

Les questions ouvertes couvrent l'architecture physique de charte, la surface
canonique des variantes, la qualification de baseline, les sources d'épreuve
et la revue visuelle v6 par manuel.

### 5.18 Carte documentaire et procédure d'audit

Les documents sont classés en contractuels, réglementaires, décisions
approuvées, état généré, audit courant et historiques/supplantés.

Le README marque notamment comme historiques lorsqu'ils contredisent l'état
courant : `DIRECTIVES_COLLECTION.md`, `PROMPT_MISSION_COLLECTION.md`,
`ROADMAP_TERMINALE.md`, les README disciplinaires et les anciens états datés.

Une checklist de nouvel audit permet de confirmer SHA, branche, propreté,
gates, PDF, variantes, sources officielles, P0 et baseline.

### 5.19 Consultation externe Chutes

Le README documente le workflow consultatif lorsque le MCP Chutes est
disponible : smoke test, emploi exclusif des modèles réellement listés, aucune
transmission de secret ou donnée personnelle, avis indépendants, vérification
locale de chaque recommandation et consignation utile sous `audit/chutes/`.

Chutes ne constitue jamais une source d'autorité ni une approbation. Le README
mentionne aussi le fait observé lors de l'audit du 13 août : catalogue de
modèles accessible, puis consultation refusée avec HTTP 402 pour quota
insuffisant, donc aucune expertise externe exploitable pour cet audit.

### 5.20 Sécurité, propriété et glossaire

Le dépôt étant public et sans licence racine, le README précise que visibilité
publique ne signifie pas autorisation générale de réutilisation.

Aucune donnée d'élève, clé, secret ou `.env` réel ne doit être publié.

Un glossaire termine le document, suivi du format contractuel de compte rendu.

## 6. Sources de rédaction

Les sources principales sont :

- `AGENTS.md` ;
- `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md` ;
- `docs/superpowers/specs/2026-08-12-finalisation-premium-six-manuels-design.md` ;
- `audit/AUDIT_ETAT_PROJET_2026-08-13.md` ;
- `audit/INVENTAIRE_COLLECTION.json` et `.md` ;
- `audit/BUILD_MANIFEST.json` ;
- `audit/BUILD_PRODUCERS.yaml` ;
- `docs/programmes/PROGRAMMES_2026_2027.yaml` ;
- les assembleurs, Makefiles, `pyproject.toml` et workflows CI réels.

Les anciens README et directives peuvent servir à expliquer l'histoire, mais
pas à fixer un fait courant lorsqu'ils sont contredits.

## 7. Garde-fous factuels

Le README ne doit pas :

- annoncer quatre manuels au lieu de six ;
- reprendre 2 751 ou 2 782 objets comme total courant ;
- attribuer `MENE1921262A` au programme TSPE Mathématiques ;
- qualifier les douze PDF de reproductibles ;
- affirmer que la charte est physiquement centralisée ;
- transformer une baseline en acceptation de release ;
- présenter les modalités d'épreuve non déposées comme vérifiées ;
- déclarer TNSI complet parce que six chapitres existent ;
- affirmer que `main` contient déjà le dernier état ;
- présenter le dépôt public comme placé sous licence ouverte ;
- masquer les gates rouges ou les P0.

## 8. Fichiers modifiés dans cette tranche

- créer `README.md` ;
- créer la présente spécification ;
- créer `docs/superpowers/plans/2026-08-13-readme-racine-autosuffisant.md`.

Aucun autre fichier n'est modifié. En particulier, cette tranche ne corrige ni
le registre programme, ni la charte, ni les assembleurs, ni les inventaires, ni
les README disciplinaires.

## 9. Validation

La validation porte sur :

- existence de chaque lien local mentionné ;
- concordance des chiffres avec l'inventaire et le rapport d'audit ;
- concordance des commandes avec `--help`, Makefiles et CI ;
- présence de la hiérarchie d'autorité ;
- présence des marqueurs du bloc daté ;
- absence des contradictions interdites ;
- cohérence entre objectif, cible et état observé ;
- `git diff --check` ;
- `scripts/inventory_collection.py --check --require-clean` après commit ;
- relecture indépendante de conformité puis de qualité documentaire.

La suite de tests complète n'est pas relancée pour une modification Markdown
seule ; ses échecs actuels sont documentés et non modifiés par cette tranche.

## 10. Critères d'acceptation

Le travail est accepté si :

1. un auditeur peut identifier le projet, son périmètre et son statut sans lire
   un autre document ;
2. la logique métier et la pédagogie Nexus sont compréhensibles ;
3. l'arborescence et la chaîne de build sont explicites ;
4. les commandes réellement disponibles sont distinguées des cibles futures ;
5. les P0 et gates rouges ne sont pas minimisés ;
6. les sources d'autorité et les preuves sont accessibles ;
7. l'état daté ne peut pas être confondu avec une vérité intemporelle ;
8. le README ne crée aucune nouvelle contradiction connue ;
9. aucune modification hors des trois fichiers autorisés n'est présente ;
10. les revues indépendantes n'ont plus de constat bloquant.
