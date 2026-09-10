# HGGSP 2027 — Rapport de récupération documentaire

**Date : 8 septembre 2026 — Verdict : récupération partielle exploitable, manuscrit complet non retrouvé.**

Le résultat dépasse la simple remise à disposition du kit fondateur : les images déjà présentes dans le dossier de reprise ont été exploitées pour isoler 72 vues de pages, retrouver l’organisation du manuscrit et matérialiser une partie de ses énoncés. En revanche, aucune nouvelle copie complète des onze chapitres Markdown, de la banque originale ou des cinq PDF avancés n’a été localisée par les voies effectivement consultées.

## 1. Ce qui est maintenant sauvegardé et utilisable

| Ensemble | Résultat matériel | Portée exacte |
|---|---|---|
| Deux archives jointes | Originaux préservés ; contrôles CRC et chemins avant extraction | Pas d’exécution des scripts archivés |
| Kit fondateur | 27 fichiers extraits, sources Markdown/JSON, trois couples PDF/Word, référentiel et outils | Le kit ne contient pas les onze cours développés |
| PDF du kit | Dossier fondateur : 34 pages ; module 00 candidat : 18 pages ; autocorrection : 8 pages | Ouverture technique exécutée ; pas de nouvelle validation scientifique |
| Images originales | 4 illustrations, 2 rendus individuels et 4 planches | Déjà présentes dans le dossier fourni ; aucune nouvelle image d’archive découverte |
| Pages individualisées | 72 PNG : pages source 001–054 et 127–144 | Découpes lossless des planches, pas pages haute définition retrouvées |
| Banque textuelle partielle | 32 énoncés, 20 QCM avec leurs trois options, 4 nouveaux tests | Transcription visuelle ; corrigés et clés non récupérés ; deux valeurs numériques de T06-E3 à confirmer |
| Cours en prose | Fragment d’ouverture P01 et diagnostic P01-D | Fragment identifié ; pas reconstitution du chapitre entier |
| Organisation du livre | Onze thèmes et folios, 12 méthodes, 6 remédiations, parties transversales | Relevé sélectif du sommaire ; ne remplace pas le contenu |
| Fac-similé | Un PDF de 76 pages : 72 vignettes + 2 rendus + 2 notices nouvelles | Un dossier de traces, pas un des cinq anciens PDF du manuel |
| Suivi | Matrice par thème, inventaires, journal des recherches, contrôles et manifeste SHA-256 | Les preuves de récupération et les travaux nouveaux sont distingués |

La banque nouvellement structurée est nommée `BANQUE_PARTIELLE_TRANSCRITE.json`, et non `banque_pedagogique.json` : le fichier original n’a pas été retrouvé. Les champs de corrigé, d’aide et de lien au cours non récupérés restent explicitement absents ou à `null`.

## 2. Recherches réellement effectuées

### Espace de travail local

Une inspection récursive ciblée de l’espace monté a recherché les anciennes racines, les noms des chapitres, les assemblages, les générateurs, les journaux et les sorties PDF. Aucun arbre historique autonome contenant ces sources n’a été retrouvé. Les sous-répertoires apparus ensuite lors de l’ouverture des images contiennent des remontages de nos propres dérivés de cette session : ils ne constituent pas une découverte supplémentaire.

Les pièces jointes ont été copiées dans `originaux/`. Les ZIP ont été contrôlés, puis extraits dans une destination distincte après vérification des chemins et des liens symboliques. Les originaux n’ont été ni modifiés ni supprimés.

### Bibliothèque de fichiers

Des recherches par contenu et noms exacts ont été complétées par une liste de fichiers récents. Cette liste a permis de retrouver des entrées HGGSP du dossier « Manuels scolaires », notamment le kit, les documents du module 00, la carte du programme et l’état de reprise.

Les deux ZIP conservés séparément dans la bibliothèque ont été matérialisés et comparés aux pièces jointes. **Ils sont identiques octet pour octet**, et n’apportent pas une version avancée supplémentaire. Les comparaisons sont enregistrées dans `CONTROLE_COPIES_BIBLIOTHEQUE.json`.

Une limite technique a été constatée : certaines recherches par titre et certaines listes du dossier renvoient un résultat vide alors que les entrées sont présentes dans la liste récente et peuvent être ouvertes par leur référence. Un résultat vide n’a donc pas été assimilé à une disparition du contenu. La liste récente était paginée ; seule une première page a été examinée. Cette reprise ne certifie pas une fouille exhaustive de toute la bibliothèque.

### Historique accessible

Les recherches contextuelles n’ont fourni aucun texte intégral supplémentaire des anciens chapitres ou générateurs. Les informations détaillées disponibles sur la tentative précédente proviennent principalement de l’état de reprise fourni. Elles restent des attestations historiques secondaires, et non des commandes de création originales récupérées avec leur contenu complet.

### Dépôt GitHub `cyranoaladin/manuels-nexus`

Consultation strictement en lecture seule : métadonnées du dépôt, liste des sept branches, arbre récursif de `main`, recherche HGGSP dans les fichiers et recherche HGGSP dans les messages de commits. Aucun manuscrit HGGSP n’a été retrouvé par ces opérations. La branche `main` consultée pointait sur `a21ff532750cebd156b4a77666f434c40ae9ee20`.

Cette conclusion ne couvre pas tous les anciens blobs, les branches non inspectées récursivement, les références supprimées ou les fichiers jamais envoyés au dépôt. Aucune publication, modification, fusion ou suppression n’a été effectuée.

### Google Drive

Le montage Google Drive a été identifié, puis sa racine parcourue. Une recherche native par nom contenant « HGGSP » a retrouvé quatre dossiers de ressources et un PDF documentaire. Les enfants directs des quatre dossiers sont des rubriques de programmes, ressources d’accompagnement et évaluations/examens. Aucun fichier du manuscrit recherché n’est apparu dans ces résultats.

La requête native initiale avait une syntaxe de filtre erronée ; elle a été corrigée et réexécutée. Les sous-dossiers n’ont pas été intégralement parcourus. Cette recherche n’établit pas l’absence de toute sauvegarde sous un nom différent ou un format non retourné par le connecteur.

## 3. Ce que les images permettent de retrouver

Le sommaire permet de situer P01 au folio 14, P02 au folio 25, P03 au folio 37, P04 au folio 48, puis les autres thèmes jusqu’à T06 au folio 118. Il mentionne aussi l’oral, le lexique, le carnet cartographique, la correspondance au programme et les références.

Les plages visuelles correspondant à P01, P02 et P03 sont présentes dans les planches, selon les débuts de thèmes indiqués au sommaire. La fin de ces thèmes comprend effectivement les exercices, QCM et tests transcrits. Cela ne signifie pas que chaque phrase des trois cours est déjà transcrite, lisible avec certitude ou scientifiquement relue. Seules les deux premières pages source de P04 sont présentes. Pour T06, six pages de fin de thème sont présentes, dont la banque d’entraînement.

Les textes matérialisés comprennent notamment :

- P01 : régimes politiques, participation athénienne, représentation européenne, transitions, analyse d’une copie fictive, composition et oral ;
- P02 : instruments de puissance, Empire ottoman, alliance atlantique avec tableau, langues et numérique, routes de la soie, comparaison diachronique ;
- P03 : définition de frontière, conférence de Berlin, Schengen, séparations coréenne et germano-polonaise, espaces maritimes, problématisation ;
- T06 : information et connaissance, production collective d’une découverte, lecture statistique, diaspora et renseignement, cloud, souveraineté et cyberespace.

Ces thèmes décrivent le contenu des énoncés retrouvés, non une nouvelle validation de leurs données. Les compositions et la dissertation proposées dans ces exercices ne sont pas confondues avec les neuf examens blancs distincts recherchés.

### Réserve sur T06-E3

La consigne est lisible, mais deux données de la vignette sont insuffisamment nettes : le taux d’alphabétisation de 1975 et le nombre de millions d’adultes. Les lectures candidates sont signalées entre crochets avec un point d’interrogation. Elles n’ont pas été remplacées par des chiffres trouvés ailleurs et aucun calcul n’est présenté comme corrigé retrouvé.

### Réserve sur les versions de mise en page

Le rendu individuel 028 et la vignette source 028 diffèrent : présence ou absence de numérotation de sous-sections et coupures de blocs QCM à des endroits différents. Des marques `**` apparaissent dans certains titres de QCM des planches. Les deux témoins sont conservés ; le nom historique `rendus_finaux` n’est pas assimilé à une validation éditoriale.

## 4. Fichiers encore non retrouvés

Les onze sources `chapitres/P01.md` à `P05.md` et `T01.md` à `T06.md` restent non retrouvées sous leur forme originale. Il en va de même pour :

- la banque avancée, les examens originaux, la couverture de rédaction et le registre avancé de références ;
- les trois fichiers de méthodes du manuscrit et les contenus de correction associés ;
- les cinq sources assemblées `manuel_cycle.md`, `manuel_niveau1.md`, `compagnon.md`, `epreuves.md`, `sujets_seuls.md` ;
- les générateurs avancés `build.py`, `banque.py`, `examens.py`, `assemble.py`, `atlas.py`, le gabarit LaTeX et les journaux de compilation ;
- les cinq PDF `HGGSP_2027_Manuel_Cycle_terminal.pdf`, `HGGSP_2027_Niveau_1_Premiere.pdf`, `HGGSP_2027_Compagnon_Autocorrection.pdf`, `HGGSP_2027_Epreuves_blanches_et_corriges.pdf`, `HGGSP_2027_Epreuves_Sujets_seuls.pdf` ;
- les textes complets des cinq compositions N1 et des quatre examens N2 décrits historiquement, avec leurs corrigés ;
- les autres illustrations annoncées mais absentes du dossier de reprise.

Les trois PDF du kit fondateur et son script `generer_documents.py` ne sont pas les équivalents de ces sorties et générateurs avancés.

## 5. Chiffres historiques : ce qu’ils prouvent et ce qu’ils ne prouvent pas

L’état de reprise fourni rapporte 40 905 mots pour les onze chapitres à un stade de travail, puis 60 208 mots sur un assemblage plus large avec une méthode de comptage différente. Il décrit 88 exercices, 55 QCM, 12 méthodes, 6 remédiations, 11 nouveaux tests et neuf sujets blancs. Il rapporte aussi un contrôle passé de 723 réussites et 7 échecs, puis 730 réussites.

Ces données aident à identifier le travail recherché. Elles ne sont pas les volumes actuellement récupérés, et **les 730 contrôles n’ont pas été réexécutés dans cette session**. Les contenus nécessaires ne sont pas disponibles. Aucune nouvelle conformité aux textes officiels de la session 2027 n’est certifiée par cette récupération.

## 6. Vérifications effectivement exécutées ici

Les ZIP fournis ont été testés par CRC. Les 41 entrées déclarées dans les deux manifestes internes, hors fichiers manifestes eux-mêmes, ont été rapprochées des empreintes recalculées : aucune différence. Les deux copies provenant de la bibliothèque ont été comparées à leurs homologues joints : identité binaire.

Les trois PDF fondateurs ont été ouverts techniquement. Les 72 images découpées ont été indexées et hachées. La banque JSON a été relue par le programme de vérification : 56 identifiants distincts, 32 exercices, 20 QCM à trois options, 4 tests, toutes les images sources référencées présentes, aucun corrigé ni clé de QCM ajouté.

Le fac-similé a été rouvert avec un lecteur PDF : 76 pages, 74 pages porteuses d’images, 13 signets. Les pages PDF 1, 29, 56 et 76 ont été inspectées visuellement après rendu. Huit pages ont été rendues pour contrôle, sans prétendre avoir inspecté visuellement toutes les pages du nouveau PDF.

Les pages source 2, 3, 4, 5, 19, 27, 28, 29, 38, 39, 40, 41, 49, 50, 51, 52, 129, 130, 131 et 132 ont été utilisées en lecture visuelle ciblée pour le relevé. Cette liste ne vaut pas relecture intégrale de chaque page. Le rendu individuel 028 a aussi été examiné. Aucun OCR n’a été employé.

Le manifeste final et le rapport externe de contrôle d’archive donnent les tailles, empreintes et résultats de vérification du paquet remis. Aucun fichier de police autonome n’est inclus.

## 7. Ce qui a été nouvellement créé

Sont nouveaux : les scripts de récupération, les découpes, l’index de consultation, le fac-similé d’assemblage, les rapports, la matrice et la structuration Markdown/JSON des transcriptions. Les passages de cours et les énoncés proviennent des images identifiées ; aucun chapitre manquant n’a été rédigé puis présenté comme retrouvé.

Les textes d’explication et de statut du présent rapport sont nouveaux. Ils restent séparés du contenu du manuel. Les originaux, leurs empreintes et les références visuelles permettent de distinguer les deux.

## 8. Prochaine opération précise

La reprise peut désormais partir des fichiers effectivement récupérés, sans refaire le kit ni réinventer les 32 énoncés. L’opération suivante la plus utile consiste à transcrire, avec contrôle phrase à phrase, les pages de cours visibles de P01 puis P02 et P03, en maintenant les lacunes et les incertitudes signalées. Toute partie réellement absente devra être marquée comme reconstruction nouvelle, accompagnée d’une vérification des sources et de la réglementation avant intégration au manuel.

Les images, les transcriptions et leurs liens sont conservés dans ce paquet portable. Un futur accès à un export de conversation ou à une sauvegarde locale contenant les sources avancées pourra être rapproché du présent inventaire, sans écraser les témoins de versions déjà sauvegardés.
