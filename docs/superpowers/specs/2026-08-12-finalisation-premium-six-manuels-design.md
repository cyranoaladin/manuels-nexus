# Conception — Finalisation premium des six manuels Nexus 2026-2027

**Date :** 12 août 2026  
**Statut :** conception approuvée par l'utilisateur  
**Branche :** `integration/1spe-bo2026-traceability`  
**Point de départ :** `a21ff532750cebd156b4a77666f434c40ae9ee20`

## 1. Objectif

Finaliser et rendre publiables les six manuels de la collection Nexus Réussite
2026-2027 :

1. Mathématiques Première spécialité (`1SPE`) ;
2. Mathématiques Terminale spécialité (`TSPE_2026_2027`) ;
3. Mathématiques complémentaires Terminale (`TCOMPL`) ;
4. Mathématiques expertes Terminale (`TEXPERTES`) ;
5. NSI Première spécialité (`1NSI`) ;
6. NSI Terminale spécialité (`TNSI`).

Le niveau « premium » signifie simultanément : exactitude disciplinaire
prouvée, conformité traçable aux programmes applicables en 2026-2027,
progression pédagogique Nexus complète, séparation élève/professeur, code
exécuté, PDF stable sans collision, contrôle visuel, reproductibilité depuis un
clone propre et approbation humaine finale.

## 2. Décisions humaines enregistrées

L'utilisateur a explicitement approuvé les décisions suivantes :

- `HUM-2026-08-11-WAVES` : produire la collection par vagues avec gates
  communs ;
- `HUM-2026-08-11-VISUAL-MAIN` : conserver la maquette actuelle de `main`,
  incluant les correctifs
  anti-collision, comme référence visuelle ;
- `HUM-2026-08-11-1SPE-INTEGRATION` : porter sélectivement les apports programme
  et traçabilité de
  `feature/1spe-bat-2026`, sans fusion automatique de cette branche ;
- `HUM-2026-08-11-ENRICHMENTS` : conserver les enrichissements hors programme
  uniquement lorsqu'ils sont
  clairement signalés « Pour aller plus loin », non exigibles, non nécessaires
  à la maîtrise et exclus des évaluations obligatoires ;
- `HUM-2026-08-11-BASELINE-WAVE0` : autoriser la mise à jour de la baseline
  d'anomalies pendant Wave 0 uniquement selon le protocole fingerprint par
  fingerprint décrit en section 12, sans suppression destinée à obtenir du
  vert ;
- `HUM-2026-08-12-FINAL-APPROVER` : soumettre chaque manuel séparément à
  l'utilisateur pour l'approbation humaine
  finale, après remise des preuves scientifiques, programme, éditoriales et PDF.

Ces identifiants décrivent des décisions de cadrage. Ils ne valent ni revue
scientifique d'un chapitre ni approbation de release d'un manuel. Les preuves
de ces revues seront enregistrées séparément dans le registre canonique des
approbations humaines.

## 3. Approches examinées

### 3.1 Production par vagues avec gates communs — retenue

Terminer d'abord l'infrastructure et les invariants communs, puis finaliser les
manuels selon leur priorité et leur distance réelle à `READY`. Un candidat
validé est gelé pendant la finalisation des autres manuels.

Avantages : cohérence de collection, prévention des régressions, outils communs
réutilisés, dette de revue traitée avec la production.

### 3.2 Finalisation immédiate de 1SPE — non retenue

Cette approche donnerait un résultat visible plus vite, mais risquerait de
dupliquer ou de réécrire les outils de traçabilité, d'assemblage et de revue
nécessaires aux cinq autres manuels.

### 3.3 Six flux parallèles — non retenue

Cette approche maximise le volume apparent, mais augmente fortement le risque
de divergences de schéma, d'auto-validation, de dette `generated` et de
régressions visuelles.

## 4. Gouvernance et source de vérité

La source locale unique est :

`/home/alaeddine/Documents/Manuels_Nexus`

Le dépôt distant unique est :

`github.com/cyranoaladin/manuels-nexus`

La branche canonique est `main`. Le travail de Wave 0 est réalisé sur
`integration/1spe-bo2026-traceability`, créée depuis le SHA synchronisé
`a21ff532`.

Aucun contenu retenu ne doit subsister durablement dans un dossier externe, un
worktree oublié, une branche abandonnée, `/tmp` ou un scratchpad. Tout contenu
accepté doit finir dans `main` par une intégration contrôlée et prouvée.

Les statuts sont factuels. Aucun objet `generated`, `draft` ou
`review_required` ne peut être présenté comme validé ou publié. Les rapports de
pilotage sont recalculés depuis l'arbre, les manifests et les builds observés.

## 5. Autorité des programmes 2026-2027

Le registre canonique `docs/programmes/PROGRAMMES_2026_2027.yaml` fait autorité
pour les six manuels, sous réserve de cohérence avec les textes officiels
archivés et empreintés.

- `1SPE` utilise le programme 2026 applicable dès la rentrée 2026-2027 et
  prépare l'épreuve anticipée 2027 pendant toute l'année.
- `TSPE_2026_2027` conserve le programme en vigueur pour 2026-2027. Le nouveau
  programme Terminale publié en 2026, applicable seulement en 2027-2028, ne doit
  pas entrer dans le parcours exigible.
- `TCOMPL` suit la même règle temporelle que `TSPE_2026_2027`.
- `TEXPERTES` utilise le programme du BO spécial du 25 juillet 2019.
- `1NSI` utilise le BO spécial n° 1 du 22 janvier 2019.
- `TNSI` utilise le BO spécial n° 8 du 25 juillet 2019 et les modalités
  d'épreuve applicables depuis la session 2026 : écrit 3 h 30 et pratique 1 h.

Toute capacité obligatoire doit être reliée à une source officielle, un
chapitre, des objets pédagogiques, des évaluations, des remédiations et des
preuves de validation.

## 6. Architecture pédagogique canonique

Chaque chapitre est une unité éditoriale complète et possède un contrat
canonique précisant : capacités officielles, prérequis, objets associés,
évaluations, remédiations, preuves et statuts de revue.

Chaque capacité met en œuvre la boucle Nexus :

1. diagnostic ;
2. orientation ;
3. cours essentiel ;
4. exemple expert ;
5. guidage estompé ;
6. entraînement ;
7. preuve de maîtrise ;
8. remédiation ciblée ;
9. re-test isomorphe ;
10. réactivation ;
11. transfert.

Le seuil des exercices E5 est :

`TARGET_EXERCISES = min(50, max(24, 6 × C))`

où `C` est le nombre de capacités atomiques du chapitre. Chaque capacité doit
posséder au moins trois exercices dédiés et apparaître dans au moins deux
parcours. Les QCM, diagnostics, automatismes, projets, oraux et évaluations ne
gonflent pas artificiellement ce seuil.

Chaque chapitre doit posséder deux évaluations comparables A/B, des corrigés
détaillés réservés au professeur, des barèmes, un diagnostic par distracteur,
une remédiation ciblée, un re-test et des tâches de transfert.

## 7. Enrichissements hors programme

Les enrichissements sont autorisés uniquement si toutes les conditions
suivantes sont réunies :

- étiquette visible « Pour aller plus loin » ;
- classement machine `mandatory_or_enrichment: enrichment` ou équivalent ;
- absence du parcours obligatoire et des prérequis de maîtrise ;
- exclusion des évaluations A/B et des épreuves d'entraînement obligatoires ;
- impossibilité de les interpréter comme exigibles en 2026-2027 ;
- vérification scientifique et éditoriale identique aux autres contenus.

## 8. Exigences spécifiques NSI

Toute source Python publiée provient d'un fichier `.py` canonique. Le pipeline
doit parser, tester, exécuter et capturer la sortie avant l'insertion générée
dans LaTeX. Les sorties inventées et les blocs de code saisis manuellement dans
LaTeX sont interdits.

Les gates NSI couvrent : syntaxe, tests unitaires, sortie attendue, cas limites,
complexité avec modèle explicite, mutations et cas adversariaux pertinents.

Le corpus importé sous `NSI/corpus_nsi` reste une matière première. Chaque objet
retenu doit être inventorié, attribué à des capacités, relu, exécuté si
nécessaire, adapté au style Nexus et validé séparément pour les variantes élève
et professeur.

## 9. Chaîne de revue indépendante

La chaîne obligatoire est :

Writer → Scientific Reviewer → Programme Reviewer → Editorial et
Student/Professor Reviewer → Build/PDF Reviewer → approbation humaine.

Les reviewers recherchent activement les erreurs et ne recopient pas le verdict
du Writer. Une revue indépendante automatisée ou par modèle peut fournir un
avis contradictoire, mais ne vaut jamais preuve à elle seule.

L'utilisateur est l'approbateur humain final de chaque manuel. Aucun manuel ne
peut recevoir un statut final de release sans cette décision.

## 10. Intégration contrôlée de `feature/1spe-bat-2026`

La branche n'est pas fusionnée automatiquement. Les apports sont portés par
lots atomiques :

- référentiel canonique du programme 1SPE 2026 ;
- gate de conformité programme ;
- extraction et registre des sources officielles ;
- schémas programme, contrat et attestation ;
- tests programme et toolchain utiles ;
- identifiants BO, `obligation_class` et `proof_object_ids` ;
- contrats enrichis, puis réapplication des corrections plus récentes de
  `main`.

La maquette et les gates visuels anti-collision de `main` prévalent. Les
anciennes baselines V5.B-it2 ne sont pas réintroduites. La trigonométrie retirée
du programme 1SPE 2026 et les anciens prérequis faux ne doivent pas revenir.

## 11. Assemblage, PDF et variantes

L'assembleur TNSI déjà ajouté doit être réconcilié avec l'inventaire, les
manifests observés et la documentation de source de vérité.

Pour chaque manuel :

- build élève et professeur ;
- comparaison des objets inclus et exclus ;
- recherche de corrigés, barèmes, notes professeur, identifiants internes et
  placeholders dans la variante élève ;
- préflight PDF ;
- inspection visuelle des ouvertures, notes marginales, figures, tableaux,
  code et pages denses ;
- métadonnées, signets, liens et polices ;
- reproductibilité depuis un clone propre.

## 12. Baseline d'anomalies

La baseline est recalculée fingerprint par fingerprint. Une anomalie ne peut en
sortir que si sa résolution est démontrée. Une anomalie encore réelle reste ;
une anomalie nouvelle est ajoutée explicitement. Aucun gate n'est affaibli pour
obtenir du vert.

Chaque mise à jour produit un rapport conservant la raison, le SHA, les
empreintes entrées et sorties et les preuves de fermeture.

## 13. Vagues de production

### Wave 0 — infrastructure commune

- réconciliation de la source de vérité ;
- vérification du registre officiel des six programmes ;
- intégration contrôlée du travail 1SPE 2026 ;
- généralisation de PROG-001 ;
- réconciliation de l'assembleur TNSI ;
- source unique QCM et statuts normalisés ;
- mise à jour gouvernée de la baseline ;
- dashboard recalculé ;
- tests complets, commits atomiques et push.

### Wave 1 — première période

Rendre réellement utilisables les premiers chapitres de `1SPE`, `1NSI`,
`TSPE_2026_2027` et `TNSI`.

### Wave 2 — quatre manuels principaux

Finaliser les quatre enseignements principaux et geler chaque candidat validé.

### Wave 3 — options Terminale

Finaliser `TCOMPL` puis `TEXPERTES`.

### Wave 4 — collection et releases

Audit transversal, builds finaux, préflights, contrôle visuel, reproductibilité,
manifests de release et approbations humaines manuel par manuel.

## 14. Définition de `READY` et de release

Un chapitre devient `READY` uniquement si son contrat, sa traçabilité, sa boucle
Nexus, ses exercices, ses évaluations A/B, ses remédiations, ses revues, ses
builds et son préflight sont prouvés et qu'aucun P0 n'est ouvert.

Un manuel devient candidat uniquement si :

- 100 % des capacités obligatoires sont tracées ;
- zéro P0 ;
- zéro contenu `generated` publié ;
- zéro fuite vers la variante élève ;
- zéro placeholder ou identifiant interne visible ;
- code et sorties exécutés ;
- tests, builds et préflight verts ;
- contrôle visuel vert ;
- source officielle figée ;
- manifeste de release généré ;
- approbation humaine finale obtenue.

## 15. Git et traçabilité des changements

Les commits sont atomiques et utilisent les préfixes contractuels :
`[PROGRAMME]`, `[MATH]`, `[NSI]`, `[PEDAGOGIE]`, `[TESTS]`, `[PDF]`, `[AUDIT]`
et `[DOCS]`.

Les changements de programme, de contenu, de baseline, de design et de tests ne
sont pas mélangés. Aucun force push, reset destructif, réécriture d'historique
ou remplacement silencieux de baseline n'est autorisé.

Avant chaque push sensible : scan de secrets, données personnelles, CSV et
bases SQLite. Le dépôt public ne doit contenir aucune donnée d'élève.

## 16. Pilotage

Le tableau interactif et les fichiers `ETAT_COLLECTION_2026_2027.json` et
`ETAT_COLLECTION_2026_2027.md` sont recalculés après chaque grande vague.

Le nombre d'exercices n'est pas le KPI principal. Les indicateurs de décision
sont : couverture des capacités, couverture de revue scientifique, traçabilité
programme, évaluations, remédiation, séparation des variantes, build et
préflight PDF.

## 17. Validation de la conception

Cette conception a été présentée en trois sections : gouvernance et source de
vérité, architecture pédagogique premium, puis chaîne technique et release.
L'utilisateur a répondu positivement à chaque section et a confirmé la stratégie
de production par vagues avec gates communs.
