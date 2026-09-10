# MISSION — Consolider HGGSP et produire réellement la collection HLP Nexus Réussite 2027

Date de préparation du mandat : 10 septembre 2026.
Nature : instruction de travail, pas certification de fichiers déjà produits.

Vous avez terminé une campagne contradictoire HGGSP. Je vous demande maintenant deux opérations distinctes : consolider les derniers points de cette collection sans régression, puis produire la collection HLP complète. Une copie du dossier Drive « HLP » vient d’être ajoutée dans votre espace de travail. Localisez-la par inspection ; ne présumez pas son chemin.

L’objectif est cinq ouvrages HLP utilisables par un candidat individuel, avec cours développés, textes, méthodes, entraînements, autocorrection, épreuves, premières et quatrièmes de couverture, sources maintenables et preuves de contrôle. Ne vous arrêtez pas à un plan, à un kit fondateur, à des prompts de couvertures ou à une nouvelle série de rapports.

## 1. Préserver HGGSP et lever les ambiguïtés du dernier rapport

Conservez un instantané de la dernière version HGGSP avec son manifeste, son identifiant de version, ses rapports et sa procédure de reconstruction. Ne remplacez jamais cette version par l’ancienne archive HGGSP contenue dans la copie du dossier HLP.

Avant de refermer cette campagne, complétez les preuves suivantes :

- QCM : remplacez l’affirmation « les QCM discriminent / le hasard » par une description exacte des indices de forme mesurés. Une bonne réponse la plus longue dans 20 cas sur 55 ne mesure pas la discrimination chez les élèves. Documentez le nombre de choix, le traitement des ex æquo, la mesure des longueurs et la répartition des positions correctes. Après les 107 réécritures, revérifiez les clés de réponse, les commentaires et les renvois dans tous les exports ; ne supposez pas leur synchronisation. Conservez les quantificateurs absolus lorsque leur emploi est disciplinairement justifié ; ne les interdisez pas mécaniquement. La plausibilité est relue à partir d’erreurs identifiées ; les fréquences de sélection et la discrimination empirique restent NON_MESUREES sans passation.
- Référentiel : expliquez le passage des 78 jalons locaux historiques aux 76 attendus annoncés. Produisez une correspondance ancien identifiant → nouveau identifiant → regroupement, différence de granularité ou correction documentée. Ne forcez ni 76 ni 78 pour satisfaire un compteur.
- Banque : détaillez les 156 objets par catégorie et par volume, sans double comptage. Reliez les 40 documents à leurs usages. Pour T06-Doc1, vérifiez aussi cellules, en-têtes, unités, provenance et correction, pas seulement son identification par l’extracteur.
- Modifications : pour les 38 corrections disciplinaires et les 462 phrases sans équivalent, fournissez les ancrages avant/après, la justification et la preuve pertinente. Une catégorie « reformulation » attribuée par l’outil ne démontre pas à elle seule la conservation des idées, réserves et exemples. Relisez les suppressions et recompositions à risque.
- Couvertures : confirmez explicitement la présence et le rôle des cinq premières et des cinq quatrièmes, leur intégration aux PDF et la disponibilité de leurs sources. Un préflight 5/5 ne précise pas à lui seul ces dix faces.
- Défauts : fournissez les identifiants, la gravité, les volumes affectés, la résolution attendue et l’incidence numérique/impression des quatre défauts ouverts. Expliquez la relation entre le registre des 25 défauts, les 38 corrections de fond et les 13 corrections orthographiques : ce sont peut-être des périmètres différents, pas nécessairement des totaux contradictoires.
- Revue des pages : distinguez contrôles automatiques, pages rendues et pages effectivement examinées. « 435 pages sans anomalie » doit préciser le périmètre du détecteur et de la revue visuelle.
- Reproductibilité : consignez les deux racines de build, les dépendances, les commandes, les journaux et les empreintes finales ; prouvez que les PDF de référence n’étaient ni lus ni copiés comme sorties.

Point disciplinaire à réexaminer expressément : ES-11/1 emploie « Deplores » au paragraphe 2 et « Demands » aux paragraphes 3 et 4, mais aussi « Condemns » au paragraphe 11 et « Condemning » dans le préambule de sa version anglaise officielle. Une correction qui attribue le bon verbe au bon objet est légitime ; une affirmation générale « ES-11/1 ne condamne pas » serait fausse. Vérifiez la formulation française exacte et le passage réellement utilisé. Ne substituez pas ES-11/4 à ES-11/1 sans vérifier l’objet de chaque résolution. Référence primaire : source U01 en annexe.

Continuez les vérifications disciplinaires documentées : l’absence de visa humain ne dispense pas de les réaliser. En revanche, n’attribuez pas à votre propre revue ni à celle d’un autre agent le statut de relecture humaine indépendante.

Conservez HUMAN_REVIEW=PENDING et HUMAN_SIGNOFF=NO tant que personne n’a effectivement signé. Le statut READY_FOR_HUMAN_BAT_DIGITAL_ONLY est un statut de soumission à relecture, pas une autorisation de publication ou d’impression.

## 2. Auditer l’import HLP sans le confondre avec un manuscrit

Lisez notamment, s’ils sont présents :
- 00_LIRE_DABORD_ETAT_DU_DEPOT.md ;
- INVENTAIRE_DEPOT_DRIVE_20260909.json ;
- ETAT_HLP_ET_LIVRABLES_NON_RETROUVES.md ;
- Programme_HLP_premiere.pdf ;
- programme_HLP_terminale.pdf ;
- voie-g_hlp_version-consolidee-2024.pdf.

La dernière vérification de ce dépôt identifiait trois références HLP, des notes d’état et des archives HGGSP, mais aucun des cinq manuscrits HLP annoncés dans une ancienne réponse. Cette annonce était incorrecte. Les anciens nombres d’exercices et d’épreuves HLP ne constituent ni un inventaire acquis ni une preuve de fabrication.

Inventoriez le contenu local réel, avec chemin relatif, taille, SHA-256, provenance, matière et rôle. Inspectez les archives avant extraction ; interdisez traversées de chemins et collisions. N’exécutez pas automatiquement leurs scripts. Une image d’état ou une mention de chemin n’est pas un manuscrit.

Après cette inspection ciblée, réutilisez uniquement les contenus HLP authentiquement retrouvés. Tout texte nouvellement rédigé doit être identifié comme nouveau. Bornez la recherche : ne recommencez pas indéfiniment la recherche d’une collection dont l’existence matérielle n’est pas établie.

## 3. Isoler la nouvelle fabrication

Créez une racine HLP active indépendante de la racine HGGSP. Si la copie HLP est à l’intérieur du dossier HGGSP, gardez l’import comme témoin et préparez un projet frère ; n’imbriquez pas la nouvelle fabrication dans le périmètre contrôlé par les manifestes HGGSP.

Adaptez une copie identifiée des composants génériques utiles : styles, assemblage, contrôles, fabrication des couvertures. Ne modifiez pas une bibliothèque partagée sous les pieds d’une campagne HGGSP en cours. Fixez la version d’origine et les changements HLP. Les contenus et attendus HGGSP ne se transposent pas à HLP.

Aucun effacement des originaux, aucun nettoyage par joker, aucun arrêt de processus fondé sur un ancien PID. Une seule fabrication par racine, avec verrou et sorties temporaires propres. Les essais négatifs utilisent des copies indépendantes et des chemins résolus hors des originaux.

## 4. Contrat de livraison HLP

Produisez obligatoirement :

V01 — HLP_2027_Manuel_Cycle_terminal.pdf
V02 — HLP_2027_Niveau_1_Premiere.pdf
V03 — HLP_2027_Compagnon_Autocorrection.pdf
V04 — HLP_2027_Epreuves_blanches_et_corriges.pdf
V05 — HLP_2027_Epreuves_Sujets_seuls.pdf

Produisez aussi leurs cinq HTML, les sources, les références, les dépendances autorisées et dix faces de couverture : cinq premières et cinq quatrièmes. Une extraction Terminale seule est facultative et dérivée des mêmes sources.

Le module 00 candidat, son autocorrection, le carnet de progression et les grilles méthodologiques doivent être utilisables ; leurs exports autonomes sont générés depuis le contenu canonique, pas entretenus comme des manuscrits concurrents.

## 5. Verrou réglementaire propre à HLP

Réouvrez les sources officielles HLP01 à HLP08 de l’annexe. Distinguez date du texte, session d’application, date de consultation et version éditoriale. Les pages anciennes non consolidées ne priment pas sur leurs modifications ultérieures.

Repères vérifiés pour préparer ce mandat, à reconfirmer avant fabrication finale :

N1 — spécialité non poursuivie : 2 heures, coefficient 8 ; deux questions sur un même texte, une interprétation et une réflexion à partir du texte, articulant littérature et philosophie ; 10 points par question.

N2 — spécialité conservée : 4 heures, coefficient 16 ; une interprétation littéraire et un essai philosophique, ou une interprétation philosophique et un essai littéraire, sur un même texte ; 10 points par question et deux copies distinctes.

Depuis la modification applicable à compter de 2024, le périmètre de l’écrit HLP est le programme de Terminale en vigueur : n’excluez ni « Éducation, transmission et émancipation » ni « Création, continuités et ruptures » en recopiant l’ancienne limitation. Ne transposez pas la rotation HGGSP à HLP.

Vérifiez séparément Grand oral et oral de contrôle. Préservez le coefficient 8 du Grand oral en voie générale à partir de 2027. Ne réduisez pas ses deux questions à HLP en ignorant l’autre spécialité du candidat.

Expliquez la différence entre parcours d’apprentissage et inscription administrative ; n’inventez ni calendrier tunisien, ni dispense, ni autorisation individuelle de réunir des épreuves. Le manuel prépare HLP, pas l’ensemble du baccalauréat.

## 6. Programme complet et découpage éditorial

Respectez les quatre ensembles semestriels et leurs douze entrées. Les codes suivants sont proposés pour le rangement, non comme des identifiants ministériels.

PREMIÈRE — Les pouvoirs de la parole
HLP-P01 : L’art de la parole.
HLP-P02 : L’autorité de la parole.
HLP-P03 : Les séductions de la parole.

PREMIÈRE — Les représentations du monde
HLP-P04 : Découverte du monde et pluralité des cultures.
HLP-P05 : Décrire, figurer, imaginer.
HLP-P06 : L’homme et l’animal.

TERMINALE — La recherche de soi
HLP-T01 : Éducation, transmission et émancipation.
HLP-T02 : Les expressions de la sensibilité.
HLP-T03 : Les métamorphoses du moi.

TERMINALE — L’Humanité en question
HLP-T04 : Création, continuités et ruptures.
HLP-T05 : Histoire et violence.
HLP-T06 : L’humain et ses limites.

Reprenez les périodes de référence des programmes et leurs développements, sans transformer ces repères en frontières historiques rigides. Traitez les entrées sous les deux approches, non en attribuant six chapitres aux lettres et six à la philosophie. La bibliographie officielle est indicative, pas une liste nationale d’œuvres imposées à apprendre intégralement.

## 7. Matrice de couverture probante

Décomposez les attentes des programmes à une granularité utile, sans inventer des prescriptions ministérielles. Pour chacune, reliez :
attente → passage développé du cours → texte ou exemple → activité → correction → indicateur de maîtrise → reprise.

Distinguez attente explicite, explicitation éditoriale et approfondissement facultatif. Ajoutez des colonnes lettres/philosophie pour rendre les déséquilibres visibles. Plusieurs attentes peuvent partager une activité, mais le rapprochement doit être argumenté.

Les statuts distinguent rédaction, vérification documentaire, revue littéraire, revue philosophique et validation humaine. Une ancre, un titre, un nombre de mots ou un compteur de fichiers ne suffit pas à déclarer une ligne couverte.

## 8. Écrire un véritable cours autonome

Pour chaque entrée, développez une enquête intellectuelle : problème initial, contexte, notions, distinctions, textes analysés, arguments, objections, limites, confrontation et synthèse. Donnez des transitions et expliquez pourquoi chaque référence éclaire la question.

En lettres, reliez énonciation, genre, construction, images, rythme ou dispositifs narratifs à un effet de sens ; évitez le catalogue de procédés. Distinguez auteur, narrateur, personnage et destinataire.

En philosophie, reconstruisez la difficulté, les distinctions et les arguments ; ne réduisez pas un auteur à une opinion sommaire. Montrez comment un exemple étaye ou met à l’épreuve une thèse. Distinguez objection, contre-exemple, contradiction et simple désaccord.

Croisez les démarches sans les rendre indistinctes. Prévenez anachronismes, citations apocryphes, oppositions artificielles et généralités sur des cultures entières. Une synthèse de révision vient après le développement ; elle ne le remplace pas.

## 9. Construire un corpus exploitable et fidèle

Objectif éditorial de départ : au moins deux extraits substantiels par entrée, permettant une véritable lecture littéraire et philosophique. Ce plancher n’est ni une prescription du BO ni une garantie d’exhaustivité. Complétez lorsque les problèmes de l’entrée l’exigent.

Intégrez réellement les textes nécessaires aux exercices. Une citation d’une ligne, un résumé ou un lien ne remplace pas le document dont l’analyse est demandée. Numérotez les lignes de manière stable et gardez les mêmes repères dans les corrections.

Pour chaque extrait : auteur, œuvre, date, édition, traducteur éventuel, emplacement vérifiable, langue, source consultée, coupes, modernisation éventuelle et statut de reproduction. Confrontez le texte à une édition fiable ; corrigez les erreurs d’extraction sans réécrire silencieusement l’œuvre.

Séparez texte authentique, traduction, adaptation, synthèse Nexus et situation fictive. N’attribuez jamais une rédaction Nexus à un écrivain ou à un philosophe. Ne fournissez pas de références de pages inventées.

Diversifiez les genres et les voix sans choix décoratifs. Ne choisissez pas tous les textes uniquement pour leur facilité d’accès. Pour les œuvres et traductions protégées, vérifiez les droits applicables à l’édition et à sa diffusion ; ne présumez pas que l’usage scolaire autorise une republication commerciale. Si nécessaire, choisissez un texte réellement exploitable ou consignez une autorisation précise. L’ancienneté de l’auteur ne règle pas automatiquement le statut d’une traduction récente.

## 10. Donner une place à la lecture suivie

Proposez un parcours de lecture suivie par ensemble semestriel, avec œuvre ou ensemble cohérent, calendrier réaliste, repères et questions progressives. C’est un choix pédagogique de la collection, pas une liste officielle d’œuvres obligatoires.

Précisez l’édition conseillée et ce que le lecteur doit acquérir séparément, le cas échéant. Ne conditionnez pas les exercices fondamentaux à des extraits absents. Les ressources de lecture comprennent des vérifications de compréhension, une analyse de passages et une mobilisation dans une question nouvelle, pas seulement une fiche de résumé.

## 11. Méthodes distinctes et exemples rédigés

Construisez quatre familles clairement repérées : interprétation littéraire, interprétation philosophique, essai littéraire, essai philosophique. Expliquez aussi la question de réflexion N1 et la montée en exigence vers N2.

Pour chaque famille : lire la consigne, circonscrire l’enjeu, préparer, sélectionner, citer, interpréter ou argumenter, organiser, rédiger, relire. Donnez au moins un exemple intégralement rédigé et commenté, puis un exemple moins guidé.

Ne transformez pas l’interprétation HLP en commentaire EAF obligatoire, ni l’essai en dissertation de philosophie de tronc commun. N’imposez ni trois parties universelles ni un nombre normatif de pages. Évaluez la précision et la progression, pas le remplissage.

Les propositions de correction doivent admettre les démarches différentes qui répondent effectivement au sujet. Dans les exercices ouverts, « proposition de réponse argumentée » est souvent plus juste que « unique bonne réponse ».

## 12. Progression, exercices et reprises

Créez un module 00 de diagnostic, lecture, vocabulaire, argumentation et organisation du travail. Orientez vers un parcours N1 complet ou vers des passerelles de Première avant N2. Associez un calendrier conseillé et une charge de travail estimée, explicitement éditoriale et adaptable.

Chaque entrée doit comporter repérage, compréhension, analyse précise, confrontation, écriture partielle, réponse autonome et réactivation différée. Les exercices développent des gestes différents ; ne remplissez pas une banque avec des variantes superficielles.

La banque canonique associe identifiant, objectif, approche, niveau, documents, énoncé, aides graduées, critères, correction, erreurs fréquentes et remédiation. Les QCM peuvent servir aux repères ou à des distinctions définies ; ils ne doivent pas transformer des interprétations recevables en erreurs arbitraires ni remplacer l’écrit.

Rédigez les reprises à partir d’une difficulté réelle : paraphrase, citation non analysée, confusion des voix, exemple décoratif, généralisation, raisonnement circulaire, hors-sujet. Un nouveau test vérifie le transfert, pas la mémorisation du corrigé.

## 13. Compagnon d’autocorrection complet

Toutes les tâches demandées ont un retour exploitable : diagnostic, exercices, QCM, questions sur les textes, méthodes et tests. Pour les questions ouvertes, donnez critères observables, proposition raisonnée, alternatives acceptables et limites.

Expliquez comment la réponse s’appuie sur les lignes du texte et sur les connaissances pertinentes. Ne vous contentez pas de « voir le cours ». Ne réservez pas les explications essentielles à un professeur.

Les identifiants, les textes et les corrections doivent rester synchronisés dans V01, V02 et V03. Le compagnon et le cours doivent préciser quand consulter la correction.

## 14. Épreuves blanches réellement nouvelles

Objectif éditorial : douze épreuves complètes, six N1 et six N2. Ce nombre est un contrat de production proposé maintenant, non une reprise d’un stock HLP supposé existant et non une obligation réglementaire.

Organisez leur couverture des six entrées de chaque niveau, avec un équilibre des deux couplages disciplinaires. Chaque sujet repose sur un même texte et comporte les deux questions adaptées à son niveau. Les extraits de simulation ne doivent pas être ceux déjà corrigés dans les cours ; un auteur peut naturellement être réutilisé.

Les consignes, le paratexte et les notes ne doivent pas livrer l’argument attendu. Vérifiez longueur, difficulté, lisibilité, contexte et droits de chaque texte. Distinguez analyse de sujets officiels existants et création d’épreuves Nexus ; ne présentez pas vos créations comme des annales officielles.

Rédigez les corrections des vingt-quatre questions, avec analyse du sujet, cheminement, réponse développée, références, critères et variantes pertinentes. Les barèmes détaillés internes sont des propositions pédagogiques, pas des grilles ministérielles inventées.

Générez V04 et V05 depuis les mêmes objets de sujet. Comparez texte, documents, questions, notes et lignes dans les deux exports. Interdisez les réponses dans le contenu, les pièces jointes ou le code HTML destiné aux sujets seuls. Ne cherchez pas à interdire les exemples résolus légitimes du manuel.

## 15. Oraux et autonomie du candidat

Ajoutez une préparation au Grand oral qui articule une question HLP avec le projet réel du candidat et son autre spécialité, sans inventer cette dernière. Travaillez formulation, démonstration orale, références, objections et échange. Séparez les règles officielles des entraînements conseillés.

Ajoutez une méthode de l’oral de contrôle correspondant à sa définition propre ; ce n’est pas un second Grand oral. Préparez des simulations avec critères, reprises et conseils de gestion du temps. Les informations administratives spécifiques aux candidats individuels doivent être vérifiées sur les sources officielles applicables.

## 16. Conception éditoriale intérieure

Adoptez la signature Nexus mais concevez une maquette HLP : lisibilité des textes longs, marges de lecture, numéros de lignes, notes, références et respiration. Une maquette de géopolitique ne devient pas une maquette HLP par remplacement du sigle.

Stabilisez grille, typographies, styles de titres, corps, interlignage, encadrés, légendes, tableaux, pagination et index. Distinguez visuellement cours, source, interprétation, méthode, exercice et correction sans multiplier les boîtes.

Contrôlez veuves/orphelines, césures, italiques d’œuvres, espaces insécables, guillemets, caractères grecs ou autres lorsqu’utiles, contrastes et repères non exclusivement colorés. Aucun texte réduit à une taille illisible pour faire tenir une page. Les citations restent du texte sélectionnable, non des captures floues.

Ajoutez sommaire cliquable, signets hiérarchiques, index des notions et des auteurs, renvois réciproques et bibliographie vérifiable. Testez réellement les navigations HTML et PDF.

## 17. Cinq premières et cinq quatrièmes de couverture

Produisez dix faces originales et leurs sources éditables, pas seulement dix prompts. Auditez les images existantes avant réutilisation ; aucune couverture HLP ancienne ne doit être présumée disponible.

Employez le véritable logo Nexus dans une version adaptée, sans redessiner ses lettres, déformer ses proportions ou inventer un emblème. Texte, logo et éléments structurants doivent, autant que possible, rester vectoriels ; l’illustration est une couche distincte. Conservez la provenance des éléments.

L’univers HLP peut travailler voix, lecture, dialogue, représentation et pluralité des points de vue. Évitez les portraits inventés présentés comme historiques, les citations décoratives fausses et l’imitation reconnaissable d’un éditeur concurrent. Le haut de gamme vient de la typographie et de la composition, pas d’effets de dorure.

Chaque première annonce le bon volume, HLP, Humanités, littérature et philosophie, le périmètre, Nexus Réussite et la session 2027. V04 et V05 se distinguent par le titre, les masses et la composition, pas uniquement par une teinte.

Chaque quatrième comporte un texte spécifique : fonction du volume, public, contenus réellement livrés, articulation avec les autres ouvrages et signature Nexus. Toute quantité annoncée est tirée de l’inventaire final. Ne prétendez pas qu’un volume de sujets contient ses corrigés. Aucun ISBN, partenaire, label officiel, auteur personnel, témoignage ou garantie de résultat inventé.

## 18. Sorties écran et impression

Faites des couvertures des dépendances du build. Produisez les cinq PDF de lecture avec première, page de titre intérieure adaptée, crédits, contenu et quatrième. N’ajoutez pas manuellement une image devant une ancienne couverture oubliée.

Préparez aussi les intérieurs séparés et les premières/quatrièmes séparées pour la fabrication. Contrôlez la résolution effective des images à leur taille de placement ; changer l’étiquette ppp ou interpoler une image ne prouve pas une amélioration du détail original. Visez les spécifications de l’imprimeur, avec 300 ppp comme objectif de départ pour les images matricielles de couverture à taille finale, non comme une règle universelle pour les éléments vectoriels.

Sans papier, pagination finale et mode de reliure déterminés, n’inventez ni largeur de dos ni couverture ouverte prétendument prête à imprimer. Fournissez un gabarit paramétrable et un statut distinct : numérique vérifié / intérieur préparé / couverture à calibrer / BAT imprimeur non délivré.

## 19. Sources, architecture et validations

Adoptez une organisation stable, adaptée aux chemins réellement utilisés :
HLP/README.md, CATALOGUE_COLLECTION.json, CHANGELOG.md ;
00_IMPORTS_REFERENCE/ ;
01_FABRICATION/sources/, production/, illustrations/, html/, pdf/ ;
02_IDENTITE_VISUELLE/logo/, premieres/, quatriemes/, gabarits/ ;
03_DIFFUSION/LECTURE/, IMPRESSION/, WEB/ ;
04_REFERENCES/ ; 05_CONTROLES/ ; 90_ARCHIVES/.

Une seule source active par contenu. Les exports sont dérivés. Toute réorganisation suit un inventaire et une table de migration ; aucun déplacement massif improvisé. N’incluez aucun fichier de police autonome dans les paquets.

Le vérificateur ne modifie pas les sources. Il utilise un contrat de ressources attendues, indépendant des fichiers qu’il trouve. Un PDF, un HTML, une correction ou une couverture obligatoire absent provoque un échec explicite ; le test ne disparaît pas simplement du décompte. Distinguez OK, ECHEC et NON_APPLICABLE justifié. Ne recopiez pas artificiellement les 190 contrôles HGGSP comme quota HLP.

Contrôlez identifiants uniques, liens, références, documents, correspondance questions/réponses, séparation des sujets, pagination, métadonnées et incorporation des polices. Les empreintes garantissent l’identité de fichiers, pas la vérité de leur contenu. Les statuts humains restent distincts des résultats automatisés.

## 20. Reconstruction et revue finale

Rebâtissez depuis une copie propre, sans PDF de référence utilisés comme sorties, sans anciens auxiliaires et sans dépendances vers un répertoire temporaire historique. Documentez versions des outils, commandes et ressources externes nécessaires ; après acquisition des sources, le build doit pouvoir fonctionner hors réseau si possible.

Reproduisez le build depuis un second emplacement. Comparez les sorties par empreinte ; lorsqu’une différence provient de métadonnées non déterministes, identifiez-la et contrôlez séparément contenu et rendu. Ne revendiquez pas une identité bit à bit non observée.

Effectuez une revue littéraire et philosophique documentée, puis rendez toutes les pages. Tracez précisément celles effectivement examinées et les corrections. Les dix faces, tous les corpus de textes, tableaux, débuts/fins d’unités, épreuves et corrigés longs doivent être revus. Toute alerte automatique est examinée. Ne faites pas passer un parcours de vignettes pour une lecture intégrale en taille réelle.

Préparez un paquet de relecture humaine avec liste de questions ciblées, sans bloquer entre-temps la rédaction que vous pouvez réaliser. Une passation pilote permettra d’évaluer les instruments ; ne prétendez pas disposer de données d’élèves absentes.

## 21. Checkpoints et dépôt vérifié

Sauvegardez après chaque unité significative : sources, documents autorisés, banque, exports existants, rapports, manifeste et prochaine opération. Ne laissez pas le travail uniquement dans un scratchpad.

J’autorise la poursuite de la rédaction et de la fabrication dans la racine HLP isolée sans une validation après chaque chapitre. Les opérations destructrices, les modifications de permissions et la publication publique ne sont pas autorisées par ce mandat.

Le dossier de dépôt déjà désigné est :
https://drive.google.com/drive/folders/1F1etk1--bceaH3q9T-20e1FYs0UOerTN

Si votre environnement possède un accès de dépôt autorisé, ajoutez des versions clairement identifiées, sans écraser les archives ni toucher aux permissions. Vérifiez l’identifiant de chaque fichier envoyé, sa taille et, par retéléchargement ou contrôle disponible, son intégrité. Un répertoire Drive créé n’est pas une livraison ; une ligne de lien dans un message n’est pas la preuve qu’un fichier existe. Sans accès d’envoi, fournissez le paquet local existant et son manifeste, sans prétendre l’avoir transféré.

## 22. Définition de terminé et action immédiate

La rédaction n’est complète que si les douze entrées sont développées sous les deux approches, les documents nécessaires intégrés, les méthodes utilisables, les tâches corrigées et les douze épreuves synchronisées. La fabrication n’est complète que si les cinq PDF, cinq HTML et dix faces s’ouvrent et correspondent aux sources. La validation humaine et le BAT imprimeur sont deux états supplémentaires, jamais déduits de compteurs techniques.

Commencez maintenant :
1. Figez le dernier HGGSP et établissez les preuves complémentaires ciblées, sans relancer une boucle d’audit générale.
2. Inventoriez la copie HLP et ses véritables apports, puis créez le projet HLP indépendant et son contrat de livraison.
3. Vérifiez les sources officielles ; rédigez le module 00 et une première unité HLP complète avec ses textes, méthodes, exercices et corrections.
4. Fabriquez immédiatement un export de contrôle de cette unité et une première/quatrième pilotes ; ce checkpoint doit contenir du cours et des fichiers, pas seulement des intentions.
5. Poursuivez toutes les unités, les épreuves, les couvertures et les exports, avec sauvegardes progressives.

À chaque point, donnez : fichiers effectivement créés, tailles/empreintes, contenu rédigé, contrôles réellement exécutés, pages examinées, défauts ouverts, décision suivante. Ne déclarez jamais « cinq manuels livrés » tant que les cinq fichiers n’ont pas été ouverts et vérifiés.

Le prochain retour attendu est un checkpoint de production HLP matériellement exploitable, accompagné de la consolidation ciblée HGGSP. Le résultat final attendu est une collection, pas une succession de rapports d’audit.

---

## Annexe — Références à rouvrir

HLP01 — Programmes et ressources HLP, Éduscol :
https://eduscol.education.gouv.fr/5805/programmes-et-ressources-en-humanites-litterature-et-philosophie-voie-g

HLP02 — Programme de Première, BO spécial n° 1 du 22 janvier 2019, PDF institutionnel :
https://eduscol.education.gouv.fr/sites/default/files/document/spe578annexe1063002pdf-83919.pdf

HLP03 — Programme de Terminale, BO spécial n° 8 du 25 juillet 2019, PDF institutionnel :
https://eduscol.education.gouv.fr/sites/default/files/document/spe255annexe1158920pdf-83922.pdf

HLP04 — Évaluation ponctuelle de la spécialité non poursuivie, note du 29 juillet 2021, NOR MENE2121284N :
https://www.education.gouv.fr/bo/21/Hebdo31/MENE2121284N.htm

HLP05 — Définition de l’épreuve HLP, consolidation août 2024 :
https://eduscol.education.gouv.fr/sites/default/files/document/nds-consolidee-definition-epreuve-bac-hlp-102114.pdf

HLP06 — Modification du programme d’examen applicable à partir de 2024, NOR MENE2323020N :
https://www.education.gouv.fr/bo/2023/Hebdo36/MENE2323020N
Vérifiez les références dans le BO lui-même : le PDF consolidé comporte une coquille dans la reproduction de ce NOR.

HLP07 — Attendus des épreuves et éléments d’évaluation, Éduscol :
https://eduscol.education.gouv.fr/sites/default/files/document/ra19lyceeg1-thlpattendus-epreuveselements-evaluation1205353pdf-83928.pdf

HLP08 — Épreuves terminales : coefficients et durées, Éduscol :
https://eduscol.education.gouv.fr/5706/les-epreuves-terminales-du-baccalaureat-general

HLP09 — Grand oral, modification applicable à partir de 2024, NOR MENE2323117N :
https://www.education.gouv.fr/bo/2023/Hebdo36/MENE2323117N

U01 — Assemblée générale des Nations unies, ES-11/1, version anglaise officielle :
https://documents.un.org/doc/undoc/gen/n22/293/36/pdf/n2229336.pdf
La vérification française de la formulation doit compléter cette lecture, sans confondre préambule, dispositif, verbe et objet.

FAB01 — Adobe, distinction pixels/résolution/dimensions :
https://helpx.adobe.com/photoshop/desktop/crop-resize-transform/resize-adjust-resolution/printed-image-resolution.html

FAB02 — Adobe, résolution de départ pour l’impression à adapter aux spécifications du prestataire :
https://helpx.adobe.com/photoshop/desktop/crop-resize-transform/resize-adjust-resolution/change-print-dimensions-and-resolution.html
