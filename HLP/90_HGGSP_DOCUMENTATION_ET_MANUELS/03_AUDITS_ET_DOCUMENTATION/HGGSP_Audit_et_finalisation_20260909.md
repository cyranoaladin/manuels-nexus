# HGGSP 2027 — Audit du dossier et plan de finalisation

**Audit du 9 septembre 2026.**

## 1. Verdict et portée

**Les cinq volumes pédagogiques attendus figurent dans l’inventaire fourni. Le dossier affiché ne constitue pas encore, à lui seul, une collection éditoriale complète, maintenable et validée pour diffusion définitive.**

Le travail ne doit pas être recommencé. L’opération prioritaire consiste à remettre les sources et dépendances à côté des exports, à intégrer et contrôler les couvertures, à fiabiliser la validation, puis à réaliser une revue pédagogique et documentaire avant de figer une nouvelle livraison.

### Trois niveaux de preuve à ne pas confondre

1. **Poste utilisateur :** seule la sortie `ls` de `~/Documents/Manuels_Nexus/HGGSP` a été fournie. Elle affiche 21 noms : 8 PDF, 5 PNG, 3 DOCX, 4 Markdown et 1 JSON. Ce n’est ni une inspection récursive ni une lecture des fichiers locaux. Les éléments cachés ne sont pas montrés. Aucun fichier de ce poste n’a été ouvert, déplacé, renommé ou supprimé.
2. **Pièces de la conversation :** l’archive `HGGSP_2027_Edition_complete.zip`, ses cinq PDF et les rapports livrés antérieurement sont accessibles. L’archive a été contrôlée puis extraite dans un répertoire d’audit séparé. Les premières pages des cinq PDF ont été rendues et examinées. Les scripts, l’organisation des sources, les notices documentaires des chapitres, les quatre sujets N2, le module des oraux et le registre bibliographique ont été examinés de manière ciblée.
3. **Contrôles nouveaux :** réexécution du vérificateur sur copie complète, deux tests négatifs sur deux autres copies isolées, vérification des empreintes et préparation d’un inventaire local en lecture seule. **Aucune reconstruction complète des PDF et aucune relecture disciplinaire exhaustive des onze chapitres n’ont été effectuées pendant cet audit.**

Les cinq couvertures PNG mentionnées par l’utilisateur ne sont pas jointes ici : leur contenu, leur logo et leur qualité d’impression restent non inspectés.

## 2. Les cinq volumes sont bien identifiés

| ID proposé | Nom du PDF affiché | Fonction | Pages de la référence 1.0 |
|---|---|---|---:|
| V01 | `HGGSP_2027_Manuel_Cycle_terminal.pdf` | Cinq thèmes de Première, six thèmes de Terminale et ressources transversales. | 156 |
| V02 | `HGGSP_2027_Niveau_1_Premiere.pdf` | Extraction Première N1, spécialité non poursuivie. | 95 |
| V03 | `HGGSP_2027_Compagnon_Autocorrection.pdf` | Corrections et reprises du manuel et du module initial. | 82 |
| V04 | `HGGSP_2027_Epreuves_blanches_et_corriges.pdf` | Cinq compositions N1 et quatre écrits N2 avec leurs corrigés. | 46 |
| V05 | `HGGSP_2027_Epreuves_Sujets_seuls.pdf` | Les mêmes neuf épreuves sans les corrigés. | 18 |

Ces nombres ont été recomptés sur les PDF disponibles ici. Ils ne sont pas une mesure effectuée sur les PDF du poste utilisateur. Une comparaison par SHA-256 permet de savoir si ces derniers sont identiques.

Un volume « Terminale N2 seule » n’était pas un sixième livrable obligatoire. Le cycle terminal contient les six thèmes correspondants. Une extraction supplémentaire peut faciliter l’usage, à condition de provenir des mêmes sources, d’intégrer les prérequis nécessaires et de ne pas devenir un deuxième manuscrit maintenu séparément.

Les trois autres PDF affichés concernent le dossier fondateur et les deux modules 00. Ils ne remplacent aucun des cinq volumes et ne doivent pas être présentés comme trois nouveaux manuels de contenu entièrement distinct.

Les trois DOCX sont des documents de fondation ou de module 00, non les sources Word des cinq manuels. Les sources finales sont Markdown/JSON et la chaîne de production est Pandoc/LuaLaTeX.

## 3. Intégrité de la référence : vérifications exécutées

Archive : `HGGSP_2027_Edition_complete.zip`.

- Taille : **5 300 272 octets**.
- SHA-256 : `47c37f71ae08d352c2bc44d88994cf56ab7e91b5eff39e2987459902019478c8`.
- Contrôle CRC : réussi.
- Fichiers contenus : **113**.
- Entrées du manifeste contrôlées : **112**, le manifeste n’incluant pas sa propre empreinte.
- Différences de taille ou d’empreinte : **aucune**.
- Cinq PDF ouverts ; format de page A4 retrouvé ; pagination et métadonnées relevées.

Les preuves détaillées sont dans `CONTROLE_INTEGRITE_REFERENCE.json` et `PDF_REFERENCE_DETAILS.json`.

**Ces contrôles certifient la conservation des octets de cette archive, pas l’exhaustivité scientifique des textes.**

## 4. Ce qui n’apparaît pas dans le dossier affiché

L’archive de référence contient les composants suivants, non visibles dans la sortie `ls` :

| Composant | Chemins de référence | Importance |
|---|---|---|
| Sources des cours | `sources/chapitres/P01.md` à `P05.md`, `T01.md` à `T06.md` | Modification fiable du contenu sans reconstruire le manuscrit depuis les PDF. |
| Banque structurée | `sources/banques/banque_pedagogique.json` | Énoncés, réponses, QCM, critères, aides, reprises. |
| Référentiel et sources | `sources/referentiel/programme.json`, `registre_sources.json` | Correspondance aux programmes et traçabilité documentaire. |
| Sources d’examens | `sources/examens/`, dix-huit fichiers sujet/corrigé et un catalogue JSON | Conservation synchronisée des deux volumes d’épreuves. |
| Méthodes, remédiations, oraux | `sources/methodes/` | Sources courantes des parties transversales. |
| Annexes | `sources/annexes/` | Atlas, lexique, références. |
| Témoins historiques réutilisés | `sources/originaux/` | Conservation des sept originaux effectivement réemployés. |
| Fabrication | `production/build.py`, `assemble.py`, `style.tex`, `style.css`, `atlas.py` | Regénération des ouvrages. |
| Vérification exécutable | `production/verifier.py` | Contrôles structurels, avec les limites découvertes ci-dessous. |
| Illustrations séparées | `illustrations/A01` à `A09`, PNG et PDF | Dépendances des éditions PDF et HTML. |
| Éditions web | Cinq fichiers sous `html/`, CSS associé | Lecture hors connexion, sans supprimer les images dépendantes. |
| Navigation et intégrité | `index.html`, `LISEZMOI.md`, `MANIFESTE_SHA256.json` | Accès aux ressources et identification de l’édition. |
| Preuves détaillées | `verification/`, matrices JSON/CSV, contrôles JSON, journaux | Audit plus précis qu’un seul rapport Markdown. |

**Action : récupérer l’archive complète et préserver son arborescence interne.** Ne pas déplacer uniquement les PDF en croyant avoir sauvegardé l’ouvrage modifiable. Ne pas créer de fichiers vides sous les noms historiques pour faire passer une liste de contrôle. Le schéma actuel de l’édition 1.0 prime sur les anciens chemins recherchés pendant la récupération.

## 5. Couvertures : présence nominale, intégration non démontrée

| Couverture affichée | Appariement proposé | Réserve |
|---|---|---|
| `couverture_manuel_cycle_terminal_HGGSP.png` | V01 | Appariement par nom ; image non inspectée. |
| `couverture_manuel_premiere_EDS_NP_HGGSP.png` | V02 | Vérifier le titre Première et la spécialité non poursuivie. |
| `couverture_autocorrection_HGGSP.png` | V03 | Vérifier la distinction avec les épreuves corrigées. |
| `couverture_epreuves_blanches_et_corriges_HGGSP.png` | V04 | La mention « et corrigés » doit être lisible. |
| `couverture_epreuves_blanches_HGGSP.png` | V05, **hypothèse seulement** | Le nom ne prouve pas qu’il s’agit des « Sujets seuls ». Lire l’image avant de renommer ou de l’affecter. |

Les premières pages des cinq PDF de référence ont encore la couverture typographique initiale, blanche, portant le nom Nexus Réussite en texte. Les nouveaux visuels PNG ne sont pas intégrés dans ces PDF de référence.

Le script de fabrication fourni ne comporte pas de liaison aux cinq nouveaux fichiers de couverture. Une insertion manuelle isolée serait donc perdue au prochain build si cette liaison n’est pas ajoutée.

### Travail à effectuer

- Conserver les PNG reçus comme originaux immuables ; identifier une seule version active de chaque couverture dans le catalogue.
- Retrouver le véritable fichier de logo, qui n’apparaît pas séparément dans la liste. Ne pas substituer au logo officiel une approximation générée.
- Contrôler le titre, les accents, la session, la signature, l’absence d’auteur ou de label inventé, le contraste et la cohérence entre volumes.
- Mesurer les dimensions et le ratio. À titre de calcul, une image A4 à 300 pixels par pouce représente environ 2 480 × 3 508 pixels hors fond perdu. Un simple rééchantillonnage ne restitue pas des détails absents de l’original. Les paramètres définitifs viennent de l’imprimeur.
- Intégrer la couverture dans la fabrication, sans convertir l’intérieur en images. Prévoir une vraie page de titre et les informations éditoriales ; éviter deux premières couvertures successives par accident.
- Recontrôler pagination, sommaire, liens, signets et métadonnées après intégration ; établir de nouvelles empreintes. Un rapport de l’édition 1.0 ne valide pas automatiquement ces fichiers modifiés.

Pour une impression reliée, une première de couverture seule ne suffit pas nécessairement : le dos, la quatrième, les fonds perdus et les dimensions de l’ensemble sont à établir selon la pagination et les spécifications de fabrication réellement retenues. Cela ne constitue pas un manuel supplémentaire manquant.

## 6. Résultats nouveaux sur le vérificateur

### 6.1 Réexécution normale

Sur une copie intacte : **505 contrôles, 505 réussites, aucun échec, code de sortie 0**. Le résultat historique est donc reproduit dans l’environnement de cet audit pour les fichiers livrés.

### 6.2 Test négatif : ancre d’un jalon retirée uniquement dans une copie de test

L’ancre `P01-AXE1-J01` a été remplacée dans la copie, sans toucher à la référence ni au poste utilisateur.

Résultat : **504 réussites et 1 échec**, code de sortie 1. La détection de l’ancre absente fonctionne. Cependant :

- le référentiel continue à recevoir `COUVERTURE_REDIGEE_COMPLETE_REVUE_INTERNE` ;
- la ligne correspondante de la matrice porte encore `REDIGE ; REVUE INTERNE, NON INDEPENDANTE`, malgré un décompte de zéro mot sous l’ancre attendue ;
- le script écrit dans `sources/referentiel/programme.json` pendant ce qui est présenté comme une vérification.

**Interprétation : la synthèse des contrôles ne masque pas l’échec, mais les états éditoriaux produits deviennent contradictoires avec cette synthèse.** Ils ne doivent pas être utilisés comme indicateur de publication automatique.

### 6.3 Test négatif : absence des cinq exports HTML

Les cinq fichiers `.html` ont été retirés d’une troisième copie uniquement. Résultat : **490 contrôles, 490 réussites, aucun échec, code de sortie 0**. Le vérificateur parcourt les HTML qu’il trouve, sans imposer l’existence des cinq fichiers attendus. Une absence de ressources réduit donc le nombre de contrôles sans bloquer ce scénario de livraison incomplète.

### 6.4 Datation et portabilité

Les trois exécutions du 9 septembre écrivent encore la date `2026-09-08`, car elle est codée dans le vérificateur. La date d’édition et l’horodatage d’un audit doivent être deux champs différents.

Le contrôle de livraison initial indique explicitement que la reconstruction complète des PDF n’a pas été réexécutée dans la copie de portabilité. Il prouve la portabilité du vérificateur, pas une reconstruction intégrale dans un environnement neuf. Cet audit n’effectue pas non plus cette reconstruction.

### Corrections techniques prioritaires

1. Rendre le vérificateur non modifiant pour les sources ; séparer génération de matrices et vérification.
2. Calculer les états par élément et le statut global à partir des résultats réels. N’écrire aucun état « complet » inconditionnel.
3. Déclarer dans le catalogue la liste exacte des cinq PDF, cinq HTML, illustrations et ressources requises ; refuser les absences, plutôt que seulement parcourir les fichiers présents.
4. Enregistrer un horodatage réel, une version du vérificateur et les empreintes des entrées et sorties contrôlées.
5. Tester la synchronisation sources → assemblages → PDF/HTML, l’intégration des couvertures et l’intégralité des deux corrigés de dissertation.
6. Réaliser une reconstruction isolée complète, avec les dépendances documentées, puis comparer contenus, navigation et rendu. Une identité binaire n’est pas toujours un critère adapté à des PDF comportant des dates de création ; expliciter le niveau de reproductibilité attendu.

Les faits reproduits sont consignés dans `PREUVES_TESTS_VERIFICATEUR.json`. Aucun code corrigé n’a été substitué aux scripts du projet pendant cet audit.

## 7. Couverture pédagogique : acquis et limites

### Acquis présents dans la référence

La structure contient onze chapitres et les 78 jalons locaux, ainsi qu’une banque de 88 exercices, 55 QCM et 11 nouveaux tests. Les méthodes, les six remédiations, le module initial et les parties orales existent. Les neuf examens sont présents avec leurs fichiers de correction. Il ne s’agit pas d’un simple plan vide.

Ces nombres décrivent le contenu disponible ; ils ne prouvent pas que chaque attente du programme est enseignée et évaluée avec une profondeur suffisante.

### Réserve documentaire principale

Les quatre sujets N2 ont été lus. Chacun associe un document reformulé/adapté par l’édition et un tableau éditorial. Certains passages énoncent déjà une limite interprétative que le candidat est ensuite appelé à discuter. Les notices signalent correctement cette fabrication ; ces textes ne sont pas présentés comme des citations littérales.

**Avis pédagogique :** ces dossiers ont un intérêt pour l’apprentissage guidé, mais un corpus exclusivement constitué de ce type ne suffit pas à démontrer un entraînement documentaire exhaustif. Pour une édition destinée au travail autonome et à des simulations authentiques, ajouter ou substituer des extraits identifiables d’acteurs, archives, textes institutionnels, cartes, données et images documentaires, choisis selon le sujet, avec un appareil explicatif qui n’effectue pas déjà tout le travail critique.

Ce n’est pas l’affirmation que toute adaptation pédagogique serait interdite. La recommandation porte sur la diversité réelle des sources, l’autonomie de l’analyse et la fidélité des simulations aux compétences visées.

Les 22 entrées `Doc1`/`Doc2` des onze cours sont aussi largement construites comme synthèses, tableaux, reformulations ou situations méthodologiques. Cette conception doit être prise en compte dans la revue documentaire, et non confondue avec 22 fac-similés de documents historiques distincts.

### Matrice : passer du thème au jalon

La matrice relie actuellement tous les exercices d’un thème à chacun de ses jalons. Son en-tête reconnaît que ce rattachement est thématique. Elle ne prouve pas qu’un exercice spécifique vérifie chaque jalon.

Ajouter pour chaque attendu : localisation du cours ; document effectivement disponible ; tâche qui mobilise cet attendu ; correction correspondante ; critère observable ; remédiation ; retest ; état de lecture disciplinaire. Une même tâche peut couvrir plusieurs jalons, mais la correspondance doit être justifiée. Une case vide doit demeurer « à compléter », sans mapping artificiel.

### Références

Le registre contient **129 identifiants**, mais **48 sont classés comme renvois thématiques vers un accompagnement officiel**. On dénombre **80 URL principales distinctes**. Ce ne sont pas 129 documents indépendants intégralement reproduits ou validés. Le rapport initial indiquait déjà que ces références n’étaient pas 129 ouvrages intégralement lus.

Il convient de rapprocher les affirmations importantes de leurs sources réellement probantes et de documenter, pour les ressources reproduites, auteur/organisme, titre, date, nature, localisation, provenance, éventuelles coupes ou traduction, et statut des droits. Un lien vers une ressource d’accompagnement n’équivaut pas à la présence d’un dossier documentaire complet dans le manuel.

### Relecture disciplinaire et essais d’usage

Avant de qualifier l’édition de complète et exhaustive, prévoir une relecture des onze thèmes et de tous les corrigés par un lecteur compétent en HGGSP, puis un essai de parcours autonome : accès aux documents, exécution des tâches, orientation vers les corrections et les reprises. Contrôler notamment chronologies, contextualisation, échelles, termes, interprétations et mises à jour sensibles. Aucun quota de mots ou de pages ne remplace cette lecture.

## 8. Vérification institutionnelle ciblée, séparée de l’analyse des fichiers

Sources officielles ouvertes lors de cet audit :

- Ministère de l’Éducation nationale, note du 27 août 2025, BO n° 33 du 4 septembre 2025, NOR MENE2521923N : https://www.education.gouv.fr/bo/2025/Hebdo33/MENE2521923N
- Éduscol, programmes et ressources en HGGSP, voie générale : https://eduscol.education.gouv.fr/5802/programmes-et-ressources-en-histoire-geographie-geopolitique-et-sciences-politiques-voie-g

La note confirme l’écrit de quatre heures, deux dissertations au choix sur deux thèmes différents et une étude critique portant sur un troisième thème. Pour l’année impaire 2027, la rotation désigne T02, T04, T05 et T06. L’étude critique vise l’analyse de sources et de natures diverses ainsi que le recul critique. Cette vérification ciblée ne vaut ni homologation de ces sujets ni audit intégral de toutes les règles d’inscription et du Grand oral.

Conserver les six thèmes de Terminale ; la rotation ne transforme pas les thèmes hors écrit de 2027 en fichiers obsolètes à supprimer. Archiver le référentiel institutionnel utilisé avec son URL et sa date, dans les conditions autorisées ; le garder distinct du manuscrit Nexus.

## 9. Module 00 et fondation : éviter deux versions actives

Les sources de la version intégrée ont effectivement adapté les identifiants du module fondateur : par exemple `D1` devient `00-D1`, `E1` devient `00-E1`, et des remédiations portent le préfixe `00-`. Des zones de réponse ont aussi été remplacées par l’invitation à travailler dans un cahier. Les déclarations de version ont été actualisées.

Ainsi, les anciens DOCX/PDF du module 00 ne doivent pas être distribués avec les corrigés intégrés en présumant des renvois identiques. Leur conservation est nécessaire comme historique ; leur utilisation actuelle exige une vérification. La meilleure solution pour proposer un module autonome courant est de l’exporter depuis les sources intégrées, avec les mêmes identifiants.

Le dossier fondateur, la mission et la carte de programme historique restent des documents utiles au pilotage et à la provenance. Ils ne doivent pas être confondus avec le référentiel courant ni faire office d’ouvrage principal pour les élèves. Ne rien supprimer à partir du nom seulement.

## 10. Organisation recommandée

```text
HGGSP/
├── README.md
├── CATALOGUE_COLLECTION.json
├── CHANGELOG.md
├── 01_FABRICATION/
│   ├── LISEZMOI.md
│   ├── index.html
│   ├── sources/
│   │   ├── chapitres/
│   │   ├── banques/
│   │   ├── examens/
│   │   ├── methodes/
│   │   ├── annexes/
│   │   ├── referentiel/
│   │   └── originaux/
│   ├── production/
│   │   └── assemblages/       # générés, pas de retouches manuelles
│   ├── illustrations/
│   ├── pdf/                   # sorties de fabrication
│   ├── html/                  # sorties web, avec leur CSS
│   ├── verification/          # conserver ici les chemins attendus par les scripts
│   └── MANIFESTE_SHA256.json   # à régénérer pour une nouvelle livraison
├── 02_IDENTITE_VISUELLE/
│   ├── logo/                  # véritable fichier source du logo
│   ├── couvertures/           # une version active par volume
│   └── originaux_generes/     # témoins immuables, distincts des masters actifs
├── 03_DIFFUSION/
│   ├── V01_Manuel_cycle_terminal/
│   ├── V02_Premiere_N1/
│   ├── V03_Autocorrection/
│   ├── V04_Epreuves_et_corriges/
│   ├── V05_Sujets_seuls/
│   └── web/                   # export cohérent HTML + ressources dépendantes
├── 04_REFERENCES_OFFICIELLES/
│   └── registre_documents.json
├── 05_CONTROLES_LIVRAISON/
│   ├── edition_1_0_reference/
│   └── nouvelle_edition/      # preuves produites après les modifications
└── 90_ARCHIVES/
    ├── fondation/
    ├── checkpoints/
    └── editions_livrees/
```

### Règles de classement

- Copier initialement **le contenu complet de la racine interne de l’archive** sous `01_FABRICATION/`, sans éclater ses sous-dossiers. Le déplacement de cette racine conserve les chemins relatifs des scripts ; la migration doit tout de même être testée.
- Les contenus canoniques demeurent dans `01_FABRICATION/sources/`. Les assemblages, PDF et HTML sont générés.
- Les PDF de `03_DIFFUSION/` sont des copies contrôlées des sorties libérées, avec empreintes identiques documentées ; ce ne sont pas des fichiers à corriger manuellement. Une copie de diffusion ou de sauvegarde justifiée n’est pas une deuxième source éditoriale.
- Ne pas disperser les HTML entre des dossiers individuels sans régénérer leurs chemins d’images et de CSS. L’édition web doit conserver une arborescence cohérente.
- Le catalogue relie l’ID de volume, le titre, les parcours, les sources, la couverture active, la version, les exports et leurs empreintes. Les appariements proposés ne deviennent actifs qu’après validation.
- Garder les rapports historiques avec leur édition. Les nouveaux rapports ne doivent ni effacer l’historique ni recycler une ancienne réussite.
- Sauvegarder les originaux également hors de ce répertoire ou sur un autre support. Un sous-dossier `90_ARCHIVES/` sur le même disque ne suffit pas à constituer une sauvegarde indépendante.

Le détail proposé pour les 21 entrées figure dans `PLAN_CLASSEMENT_21_ENTREES.json`. **Aucun classement n’a été exécuté sur le poste de l’utilisateur.**

## 11. Ressources supplémentaires : distinguer besoin et multiplication des volumes

### À rétablir en priorité

Sources, scripts, illustrations, HTML, registre, navigation et manifeste sont déjà disponibles dans l’archive. Il faut les conserver, pas les rédiger de nouveau.

### À compléter pour une édition finale robuste

Une fiche de lecture pour orienter le candidat entre V01–V05 ; un catalogue de volumes ; une page éditoriale et un registre de crédits ; une correspondance fine jalons–tâches–corrigés ; une revue documentaire ; les contrôles de nouvelles couvertures ; une validation de la nouvelle livraison.

### Extraire seulement si cela facilite l’usage

Module 00 courant, carnet de suivi, grilles d’autoévaluation, chronologies, atlas, fiches méthodes et éventuelle extraction N2 peuvent devenir des ressources imprimables autonomes. Les produire à partir des mêmes sources : ils ne doivent pas introduire une deuxième rédaction des mêmes notions. Les cinq volumes contiennent déjà plusieurs de ces éléments ; leur absence comme fichiers séparés n’est pas une absence de contenu.

Il n’est pas nécessaire de multiplier artificiellement le nombre de manuels pour justifier le mot « complet ». L’exhaustivité doit être appréciée relativement au programme et aux usages annoncés.

## 12. Séquence de finalisation

### Étape 1 — Conservation et inventaire

Créer une sauvegarde indépendante ; calculer tailles et empreintes ; effectuer un inventaire récursif incluant les fichiers cachés ; ne pas suivre les liens symboliques sans examen. Identifier les éditions par leurs empreintes, pas seulement par leur date ou leur nom.

### Étape 2 — Restauration de la fabrication

Contrôler l’archive de référence, l’extraire dans un dossier neuf, rapprocher les fichiers sans écrasement, conserver son arborescence. Examiner les scripts avant toute exécution. Ne pas exécuter automatiquement le vérificateur ancien sur les originaux puisqu’il écrit dans le référentiel.

### Étape 3 — Consolidation des sources et de l’identité

Arrêter le catalogue des cinq volumes, identifier les couvertures et le vrai logo, arbitrer V05, adapter la chaîne de production. Distinguer les pages de titre des premières couvertures. Préserver les fichiers originaux et documenter toute modification.

### Étape 4 — Finalisation pédagogique et documentaire

Revoir les jalons, enrichir la diversité documentaire des simulations, valider toutes les corrections, resynchroniser le module 00. Dater les informations contemporaines et documenter les sources. Ne pas fabriquer une validation indépendante si elle n’a pas eu lieu.

### Étape 5 — Fabrication et validation nouvelle

Corriger le vérificateur, installer les dépendances selon l’environnement documenté, construire les cinq PDF et cinq HTML depuis une copie de travail isolée. Contrôler la cohérence des sources/exports, les huit corrigés de dissertations, les cinq compositions, les quatre études, les reprises, les liens et les ressources. Tester les absences et les erreurs intentionnelles sur des copies de test.

Effectuer une revue visuelle de toutes les pages destinées à la nouvelle diffusion, adaptée au niveau de garantie recherché. L’ancienne revue de 29 pages était un échantillonnage déclaré, non une inspection exhaustive. Contrôler un exemplaire imprimé ou une épreuve imprimeur selon le mode de diffusion retenu.

### Étape 6 — Livraison

Créer des paquets de lecture clairs, une version web avec ses dépendances et une archive éditoriale complète. Un pack de première passation doit permettre d’accéder aux sujets sans ouvrir les corrigés par erreur ; le compagnon demeure disponible pour l’autocorrection après tentative. Ne pas présenter ces sujets déjà accessibles dans un recueil corrigé comme une évaluation confidentielle.

Fixer la version, établir le journal des changements, régénérer toutes les empreintes et les preuves, tester les archives et la navigation hors connexion. Déclarer explicitement les contrôles exécutés et les éventuelles réserves restantes.

## 13. Critères de fermeture

Le dossier peut être considéré comme finalisé pour le périmètre annoncé lorsque les cinq volumes sont identifiés et ouvrables, leurs sources et dépendances sont préservées, les nouvelles couvertures sont intégrées correctement, les parcours et corrigés sont cohérents, le contenu a subi la revue annoncée, les ressources documentaires sont traçables, la reconstruction complète a été testée et les preuves décrivent exactement les fichiers livrés.

**Situation actuelle : collection nominale des cinq PDF présente ; fabrication complète disponible dans l’archive ; intégration des nouvelles couvertures sur le poste non démontrée ; contrôles à fiabiliser ; exhaustivité pédagogique et documentaire non certifiée.**
