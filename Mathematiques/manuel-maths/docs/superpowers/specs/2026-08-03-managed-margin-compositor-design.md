# Compositeur déterministe des notes marginales — Design

**Date :** 3 août 2026  
**Branche :** `finalisation/collection-v1`  
**Référence observée :** `c0c39519ce50175b4bb13e3655727a1a23bfa630`  
**Statut :** approuvé pour planification  
**Décision humaine :** conserver toutes les annotations pédagogiques dans la
marge extérieure ; autoriser leur décalage vertical et leur report à la page
suivante ; retenir le compositeur LuaTeX multipasse.  
**Baseline visuelle :** aucune modification autorisée par cette décision.

## 1. Problème reproduit

Les masters complets élève et professeur utilisent encore
`gabarits/nexus-manuel.cls`. Les macros `\margeAppui`,
`\commentaireMarge`, `\vocab` ainsi que les métadonnées d'exercices et de
corrigés appellent directement `\marginnote`.

`\marginnote` positionne chaque annotation indépendamment à la hauteur de son
ancre. Il ne réserve pas une file verticale partagée. Lorsque plusieurs appels
sont proches, leurs boîtes se recouvrent. `\marginparpush=6pt` ne protège pas
ces annotations, car il ne pilote que les vrais `\marginpar`.

Le défaut est visuellement confirmé dans le manuel élève réattesté :

- page 18 : les trois méthodes de variation se superposent dans la marge ;
- page 19 : les trois rappels de modélisation se recouvrent ;
- page 20 : les rappels `range`, `while` et accumulateur sont presque
  entièrement illisibles ;
- page 21 : deux groupes de commentaires d'étapes se chevauchent.

L'analyse des sources dénombre 71 appels `\margeAppui` et 750 appels
`\commentaireMarge` dans les chapitres 1SPE. Au moins 132 commentaires sont
émis depuis des encadrés `tcolorbox` cassables. Le défaut est donc systémique et
ne peut pas être corrigé durablement par des décalages manuels page par page.

## 2. Objectifs

Le compositeur doit :

1. conserver chaque annotation dans la marge extérieure ;
2. préserver l'ordre sémantique des annotations ;
3. interdire tout chevauchement entre boîtes marginales ;
4. autoriser un décalage vertical lorsque l'ancre est encombrée ;
5. reporter les dernières annotations sur la page suivante lorsque la marge est
   saturée ;
6. fonctionner depuis le flux normal et depuis les encadrés cassables ;
7. fonctionner en recto-verso, à droite au recto et à gauche au verso ;
8. conserver des sorties déterministes avec la chaîne reproductible existante ;
9. échouer explicitement si une annotation ne peut pas être placée ;
10. fournir un gate automatique de collision marginale sur les deux PDF.

## 3. Hors périmètre

Cette tâche ne doit pas :

- réécrire les 821 appels pédagogiques existants ;
- déplacer une annotation dans le corps principal ;
- corriger ou réviser le contenu mathématique ;
- modifier la charte graphique générale ou la pagination métier à la main ;
- mettre à jour une baseline visuelle ;
- transformer le NO-GO actuel en acceptation de publication.

## 4. Approches examinées

### 4.1 `marginpar` avec `marginfix`

`marginfix` ordonne les vrais `\marginpar`, respecte un espacement minimal et
peut reporter du matériel marginal. Il est disponible dans le référentiel TeX
figé. Toutefois sa documentation exclut le multicolonnage et il ne couvre pas
nativement les annotations émises depuis les encadrés cassables. L'adopter
imposerait une refonte de ces composants ou des exceptions concurrentes.

### 4.2 Compositeur LuaTeX multipasse — retenu

Les annotations conservent une API LaTeX sémantique, mais leur mesure, leurs
ancres et leur placement deviennent des données explicites. LuaTeX résout les
positions au niveau de la page et rend les boîtes au `shipout`. Cette approche
fonctionne indépendamment du contexte d'appel, couvre les encadrés et offre un
contrat de validation machine.

### 4.3 Décalages manuels

Les offsets dans les sources corrigeraient rapidement quelques pages, mais
seraient invalidés par toute repagination. Cette approche est rejetée comme non
reproductible et non maintenable.

## 5. Architecture retenue

### 5.1 API sémantique unique

La commande interne `\nxMarginRailNote` devient l'unique voie vers la marge
du master complet. Les composants suivants lui
délèguent leur rendu :

- `\margeAppui` ;
- `\commentaireMarge` ;
- `\vocab` ;
- métadonnées d'exercices ;
- identifiants de corrigés réservés à la variante professeur.

Les signatures publiques et les fichiers de contenu restent inchangés.

Chaque appel reçoit un identifiant stable dérivé de l'ordre observé dans le
master et de son rôle. Le payload est construit après application des conditions
de variante : la version élève conserve le chrono d'un exercice, mais n'envoie
jamais son identifiant interne au compositeur ; la version professeur peut
capturer le chrono et l'identifiant. L'identifiant de contrôle du compositeur
n'est jamais rendu comme texte visible.

### 5.2 Passe de mesure

À chaque passe, le contenu de chaque annotation est composé immédiatement et
exactement une fois dans une `\vbox` de largeur `\marginparwidth`. Sa node-list
Lua est copiée dans un registre global de passe, indexé par identifiant, avant
la disparition d'un éventuel groupe local ou encadré `tcolorbox`. Cette copie,
et non les tokens TeX d'origine, est conservée jusqu'au `shipout`. Les boîtes
sont recapturées à chaque nouvelle passe et ne sont jamais sérialisées entre
deux exécutions LuaLaTeX.

Chaque capture produit :

- son identifiant ;
- son rôle ;
- son folio logique ;
- son index absolu monotone de `shipout`, renseigné au `shipout` du marqueur
  d'ancre et non lors de la capture initiale ;
- sa position d'ancrage verticale ;
- sa hauteur et sa profondeur mesurées ;
- sa largeur attendue, égale à `\marginparwidth` ;
- son ordre global ;
- sa variante ;
- le digest de son contenu sémantique après filtrage de variante.

Seuls les mesures, ancres et placements sont écrits entre les passes. Les
fichiers `margin-layout.previous.json` et `margin-layout.next.json` restent
dans le répertoire temporaire atomique propre au run. `next` est validé avant
un remplacement atomique de `previous`. Ils ne contiennent aucun token TeX ni
node-list et ne sont pas versionnés.

L'enveloppe de ces fichiers porte un nonce de run qui interdit de lire l'état
d'un autre assemblage. Ce nonce n'appartient pas à l'identité canonique du
placement et reste exclu de tout digest reproductible.

### 5.3 Résolution des placements

Pour chaque page, le compositeur :

1. place d'abord la file reportée de la page précédente dans son ordre global :
   la première note commence à la limite haute sûre et chaque suivante à la fin
   de la précédente augmentée de 6 pt ;
2. place ensuite les notes natives triées par ancre et par ordre global, chacune
   au maximum entre son ancre et la fin de la note précédente augmentée de 6 pt ;
3. trie les rectangles d'exclusion par ordonnée ; pour chaque boîte candidate,
   la déplace itérativement sous tout rectangle intersecté, avec 6 pt d'espace,
   puis recommence la recherche d'intersection ;
4. conserve le plus long préfixe de la file ainsi placée qui tient dans la zone
   sûre et reporte son complément, c'est-à-dire le plus court suffixe nécessaire ;
5. transfère ce suffixe à la page suivante dans son ordre global initial ; ces
   reports précèdent toujours les notes natives de la page cible ;
6. reporte immédiatement la boîte et son suffixe si le contournement d'un
   obstacle ne laisse plus de position valide ;
7. répète jusqu'à stabilisation ou jusqu'à rencontrer une impossibilité.

Chaque entrée conserve `origin_shipout_index`, `origin_folio`, `origin_y`,
`global_order`, `target_shipout_index` et `report_depth`. Une cascade de reports
sur plusieurs pages applique exactement la même règle, sans inversion.

Le placement est déterministe : aucune heuristique aléatoire ni dépendance à
l'heure courante n'est admise.

### 5.4 Recto-verso et report

La marge extérieure est déterminée à partir de l'index absolu monotone de la
page réellement expédiée, jamais à partir d'un compteur susceptible d'être
réinitialisé : droite au recto, gauche au verso. Le folio logique ne sert qu'à
la mention de provenance. Une page blanche ou un front matter participe à
l'index absolu. Un report change donc de côté avec la parité de la page cible.

Pour chaque page, TeX transmet en scaled points entiers la taille de page, la
géométrie effective de la marge et des rectangles d'exclusion. Les en-têtes,
pieds, folios et onglets déclarent leurs rectangles via
`\nxMarginReserveRect`. Le solveur n'infère aucune zone sûre depuis un numéro
de page ou une constante en pixels.

Une note faiblement déplacée reste sans marqueur supplémentaire. Une note
fortement déplacée ou reportée reçoit :

- un petit repère numéroté en overlay à l'ancre, de largeur, hauteur et
  profondeur nulles ;
- le même repère comme overlay distinct devant la note ;
- la mention « suite de la page N » dans un cartouche produit par le
  compositeur uniquement en cas de report.

Ces éléments sont composés par le moteur depuis des valeurs contrôlées ; ils ne
réévaluent jamais le contenu source. Leur rectangle est inclus dans l'emprise de
placement de la note. Dès que `report_depth > 0`, la hauteur effective utilisée
par le solveur inclut le cartouche de provenance, ses espacements et toutes les
décorations. Cette hauteur décorée participe au calcul de report et au digest de
convergence ; elle peut donc provoquer un report supplémentaire avant le rendu
final, jamais une collision tardive.

Le déplacement est « fort » au-delà de deux lignes de la note, mesurées avec son
interligne effectif. Cette règle ne dépend d'aucune page particulière. Les tests
exigent que l'ajout ou le retrait d'un repère ne modifie ni les coupures de ligne,
ni la pagination, ni les ancres du flux principal.

### 5.5 Rendu final

La passe finale lit le placement stabilisé, recapture chaque note une seule fois
et injecte au `shipout` une copie de la node-list déjà composée. Elle ne
reconstruit jamais le contenu depuis des mesures ou depuis des tokens
sérialisés. Les boîtes restent strictement contenues dans `\marginparwidth` et
dans la zone verticale sûre. Le texte principal ne réserve pas artificiellement
leur hauteur.

Chaque note est rendue dans un Form XObject PDF dédié avec son propre `/BBox`,
puis entourée d'un marked content `NXMarginNote`. Le repère overlay à l'ancre
est entouré séparément d'un marked content `NXMarginAnchor`. Les deux portent le
même identifiant et un numéro global déterministe dérivé de `global_order`. Le
gate exige une bijection exacte entre ancres et notes pour chaque annotation qui
requiert un repère. Ces identifiants restent absents de la couche de texte
extraite et ne sont pas visibles par le lecteur. Après écriture du PDF, un
contrôleur produit un ledger canonique à partir des objets réellement présents :
identifiant, rôle, page d'origine et cible, ordre, coordonnées `x/y/w/h`, repère
éventuel et digest du flux PDF décodé de la boîte. Ce ledger final, le registre
de capture et le placement résolu doivent être bijectifs.

Le mécanisme doit être encapsulé dans un fichier dédié chargé par
`nexus-manuel.cls`, afin de ne pas transformer la classe principale en moteur
monolithique. Le calcul algorithmique appartient à un module Lua dédié ; les
macros TeX assurent la capture, la mesure et le rendu.

## 6. Convergence et reproductibilité

`assemble_manuel.py` remplace son nombre fixe de passes par une boucle bornée à
six passes du compositeur. Chaque passe lit `previous`, recalcule intégralement
`next`, puis compare leurs représentations canoniques. Elle produit un état
explicite :

- `collecting` lorsqu'aucun placement précédent n'existe ;
- `changed` lorsque les ancres ou placements évoluent ;
- `stable` lorsque deux passes consécutives produisent les mêmes données ;
- `failed` lorsqu'une contrainte est impossible.

Un build accepté exige une passe qui a lu un placement et recomputé exactement
le même placement avant de produire son PDF et son ledger. Le PDF d'une passe
`collecting` ou `changed` n'est jamais publié. La sixième passe non stable
échoue comme oscillation.

Les deux fichiers de placement suivent un schéma versionné et utilisent UTF-8,
des objets triés par identifiant et ordre, des dimensions en scaled points
entiers, la variante et un digest de géométrie. La sérialisation canonique exclut
le nonce de run, l'heure, les chemins temporaires et l'ordre des tables Lua. Les
données de placement stables et le ledger final participent au reçu observé
comme dépendances générées couvertes par leurs digests.

Deux builds depuis les mêmes sources, le même `SOURCE_DATE_EPOCH` et la même
chaîne d'outils doivent produire les mêmes données de placement et les mêmes
octets PDF.

## 7. Erreurs et conditions d'arrêt

Le build échoue avec un message structuré dans les cas suivants :

- annotation plus haute que la zone marginale sûre ;
- annotation contenant un élément horizontal non cassable plus large que
  `\marginparwidth` ;
- absence de stabilisation dans la limite de passes ;
- collision résiduelle détectée dans le PDF ;
- annotation hors marge ou hors page ;
- perte, duplication ou réordonnancement d'un identifiant ;
- report impossible après la dernière page ;
- données intermédiaires mal formées ou provenant d'un autre run ;
- tentative d'utilisation dans un mode non supporté sans preuve de placement.

Aucun échec ne peut être transformé en `skip`, en avertissement toléré ou en
mise à jour automatique de baseline.

## 8. Validation TDD

L'implémentation suit un cycle rouge-vert strict.

### 8.1 Fixtures minimales

1. trois notes avec la même ancre : le test actuel doit constater leur collision,
   puis exiger trois boîtes disjointes et ordonnées ;
2. marge saturée : les dernières notes doivent être reportées sans perte ;
3. recto-verso : les notes doivent alterner de côté ;
4. page blanche et compteur logique réinitialisé : la parité doit rester fondée
   sur l'index absolu ;
5. encadré `tcolorbox` réellement cassé sur deux pages : une note contenant
   macros locales, mathématiques, couleur et lien doit rester présente en marge,
   sans double évaluation ;
6. report vers une page déjà chargée, puis cascade sur trois pages : les reports
   doivent précéder les notes natives sans inversion ;
7. une seule note parmi quatre trop haute pour la page : seul le plus court
   suffixe nécessaire doit être reporté ;
8. obstacle au milieu de la marge : la note doit être déplacée sous son
   rectangle ou reportée si aucune place ne reste ;
9. cartouche de provenance : sa hauteur décorée doit pouvoir provoquer un
   report supplémentaire avant stabilisation ;
10. variante élève : chrono présent, aucun ID interne ni corrigé dans le PDF ou
   le ledger ; variante professeur : chrono et ID attendus présents ;
11. repère overlay : flux principal, pagination et ancres identiques avec et sans
   repère ;
12. note trop haute ou contenu horizontal non cassable trop large : le build doit
    échouer avec le code prévu ;
13. transitions `collecting → changed → stable`, oscillation, état d'un autre
    run, distinction entre nonce d'enveloppe et identité canonique, et refus de
    tout PDF partiel.

### 8.2 Gate PDF intégral

Le gate croise trois preuves : inventaire des captures, ledger des marked
contents réellement injectés et géométrie bbox du PDF. Le bbox vérifie :

- rectangle de chaque annotation inclus dans la marge extérieure ;
- absence d'intersection entre annotations d'une même page ;
- espacement vertical d'au moins 6 pt.

Le croisement inventaire/ledger/PDF vérifie séparément :

- ordre des identifiants conservé ;
- repères d'ancre et de note appariés ;
- marked contents `NXMarginAnchor` et `NXMarginNote` bijectifs par identifiant et
  numéro global ;
- aucune annotation perdue ou dupliquée ;
- digest de chaque objet PDF conforme au ledger ;
- aucun marked content ou payload professeur interdit dans la variante élève.

Les cardinalités attendues sont toujours dérivées du registre de capture par
rôle et par variante. Le décompte documentaire des appels source n'est jamais
utilisé comme oracle du gate.

Les pages 18 à 21 du manuel élève constituent le premier échantillon de revue
visuelle. L'inspection s'étend ensuite aux pages de cours, méthodes, exercices
et corrigés les plus denses des deux variantes. Les contrôles automatisés
portent sur la géométrie, le ledger et le PDF final, pas sur un golden PNG.

### 8.3 Gates existants

Après les fixtures :

- tests ciblés du compositeur ;
- suite LaTeX/PDF ;
- build élève ;
- build professeur ;
- préflight PDF des deux variantes ;
- comparaison élève/professeur ;
- double build reproductible ;
- suite complète Phase 0 ;
- `--validate-model` ;
- `--fail-on-new` ;
- `--release-strict`, qui doit rester rouge tant que les autres dettes de
  publication subsistent.

## 9. Contrôle visuel et baseline

Le correctif produira un dossier de revue séparé avec :

- rendus avant/après des pages 18 à 21 ;
- planche-contact des pages marginales les plus denses ;
- liste des pages repaginées ;
- anciens et nouveaux digests PDF ;
- versions LuaTeX, Poppler et outils de rasterisation.

Ces images sont seulement des artefacts de revue et ne constituent ni un oracle
automatique ni une baseline. Aucun golden PNG, digest de référence visuelle ou
registre de baseline n'est écrit sans une nouvelle approbation humaine
explicite.

## 10. Déploiement atomique

L'implémentation sera découpée au minimum en :

1. test bbox rouge et fixtures de collision ;
2. contrat de données et solveur Lua déterministe ;
3. adaptateur TeX et branchement des macros ;
4. intégration à l'assembleur multipasse ;
5. build élève et contrôle des pages de régression ;
6. build professeur et contrôle de séparation ;
7. reçus, préflight et gates Phase 0 ;
8. dossier de revue visuelle, sans changement de baseline.

Chaque commit conserve une intention unique. Les PDF ne sont versionnés
qu'après validation de leur préflight et de leur manifeste observé.

## 11. Critère d'acceptation de cette tâche

La tâche de marge est acceptée lorsque :

- les deux PDF sont reproductibles ;
- le gate bbox trouve zéro collision marginale ;
- toutes les annotations attendues sont présentes, ordonnées et dans la bonne
  marge ;
- les pages 18 à 21 sont lisibles ;
- aucune baseline visuelle n'a été modifiée ;
- les gates de non-régression restent verts ;
- `release_acceptance=false` et le NO-GO général restent explicites.
