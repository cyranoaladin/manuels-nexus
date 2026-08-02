# Finalisation du manuel 1SPE pour bon à tirer — Conception

**Statut :** conception validée par le commanditaire le 26 juillet 2026  
**Auteur publié :** Alaeddine BEN RHOUMA  
**Éditeur :** Nexus Réussite  
**Marché principal :** Tunisie  
**Échéance :** bon à tirer avant la rentrée scolaire 2026  
**Ouvrages :** manuel élève et livre du professeur imprimés  
**ISBN :** aucun ISBN demandé  

## 1. Objectif

Transformer les sources existantes du manuel de mathématiques de Première,
enseignement de spécialité, en deux ouvrages cohérents, conformes au programme
applicable à la rentrée 2026-2027, relus, reproductibles et techniquement prêts
pour l'impression professionnelle.

La stratégie retenue est une refonte éditoriale contrôlée : conserver les objets
LaTeX fiables et leurs preuves, mais invalider toute attestation contredite par
l'état courant, compléter les angles morts, reconstruire les assemblages et
déployer une maquette définitive.

## 2. Sources de vérité

### 2.1 Réglementation pédagogique

La source normative unique est :

- arrêté du 26 février 2026, NOR MENE2602917A ;
- Bulletin officiel n° 14 du 2 avril 2026 ;
- annexe « Programme de spécialité de mathématiques de la classe de première de
  la voie générale » ;
- entrée en application à la rentrée scolaire 2026-2027.

Liens officiels :

- <https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A>
- <https://eduscol.education.fr/5817/programmes-et-ressources-en-mathematiques-voie-gt>

Le PDF officiel versionné dans `sources/BO2026_1SPE_specialite.pdf` doit être
rapproché du document publié en ligne par empreinte et par extraction textuelle.
Les formulations `libelle_bo` des référentiels doivent être des citations
exactes ou être explicitement marquées comme reformulations en langage élève.

La matrice réglementaire classe chaque item sans les confondre :

- `mandatory_content` : contenus, capacités attendues, parties transversales et
  « Expérimentations » ; couverture obligatoire à 100 % ;
- `prescribed_teaching` : démonstrations et exemples d'algorithmes proposés par
  le programme ; présence obligatoire dans l'enseignement ou le guide, sans les
  transformer automatiquement en attendus évaluables ;
- `optional_extension` : approfondissements possibles ; inclusion facultative,
  toujours signalée comme telle ;
- `contextual_guidance` : objectifs, histoire des mathématiques et indications
  de mise en œuvre ; traçabilité éditoriale sans création d'un faux attendu.

Le gate « conformité B.O. » exige 100 % de `mandatory_content` et de
`prescribed_teaching`. Il publie séparément le taux d'inclusion des
`optional_extension` et ne l'agrège jamais au taux obligatoire.

Le B.O. 2026 introduit explicitement les notations `u(n)`, `u_n`, `(u(n))` et
`(u_n)`. La règle éditoriale devient :

- `u_n` et `(u_n)` sont privilégiés dans la prose mathématique ;
- `u(n)` est autorisé dans un contexte de fonction, d'algorithme, de code ou de
  comparaison explicite des notations ;
- les citations exactes du B.O. conservent leur notation ;
- les contrôleurs ne peuvent interdire `u(n)` globalement : ils vérifient son
  contexte et la cohérence locale.

### 2.2 Exigences internes

Les sources internes applicables restent :

- `CAHIER_DES_CHARGES.md` ;
- `docs/01_conception_manuel.md` ;
- `docs/02_workflow_production.md` ;
- `docs/05_conventions_latex.md` ;
- `CLAUDE.md`.

En cas de contradiction, le texte officiel et les décisions de la présente
conception priment pour le manuel 1SPE.

### 2.3 Réglementation de publication en Tunisie

La mise à disposition du public impose l'enregistrement et le dépôt légal,
indépendamment de la présence d'un ISBN. La référence est la loi organique
tunisienne n° 2015-37 du 22 septembre 2015 :

<https://www.bibliotheque.nat.tn/BNT/basicfilesdownload.ashx?itemGuid=2921A14E-04F7-457A-8AE5-2AEB9DA545CA>

M&M ACADEMY SUARL devra déposer quatre exemplaires de chaque livre produit ou
reproduit en Tunisie auprès de la Bibliothèque nationale dans le délai légal.

## 3. Périmètre

### 3.1 Inclus

- audit exhaustif des dix chapitres 1SPE ;
- conformité aux contenus, capacités, démonstrations, exemples d'algorithmes et
  approfondissements du B.O. 2026 ;
- couverture transversale de la logique et des ensembles, de l'algorithmique et
  des listes, et des automatismes ;
- exactitude des cours, méthodes, exercices, corrigés, QCM, remédiations, TD et
  évaluations A/B ;
- propriété intellectuelle et traçabilité des objets ;
- progression, différenciation, autonomie et lisibilité ;
- assemblages élève et professeur ;
- maquette intérieure, couvertures, pages liminaires, index et annexes ;
- production de masters prépresse et de PDF écran ;
- rapports de validation et paquet de remise à l'imprimeur.

### 3.2 Exclus

- programme de Terminale ;
- plateforme numérique interactive ;
- vidéos et QR codes dont les destinations ne sont pas pérennes ;
- obtention d'un ISBN ;
- allégation d'homologation ou d'approbation par le ministère français.

### 3.3 Réconciliation de l'état initial

Les rapports et tags antérieurs sont des preuves historiques, pas des preuves
automatiques pour la nouvelle release.

Avant toute correction, un inventaire de migration produit :

- le nombre réel d'objets par chapitre et par type ;
- les empreintes SHA-256 des sources ;
- la présence et la version de chaque preuve ;
- les divergences entre rapports, tags, directives et fichiers courants ;
- les attestations conservables, invalidées ou à rejouer ;
- le nombre réel d'exercices par chapitre, avec gate minimal de 50 ;
- la pagination et les diagnostics LaTeX actuels des deux livres.

Une preuve antérieure n'est réutilisable que si l'empreinte de l'objet, la
version du gate, le référentiel et les dépendances correspondent à la release
courante. Sinon, le gate est rejoué. Le rapport de référence est
`validations/release-1spe/baseline.json`, accompagné d'une synthèse lisible.

## 4. Architecture éditoriale

Le manuel conserve dix chapitres regroupés selon les quatre parties thématiques
du programme.

### Partie I — Algèbre

1. Suites numériques, modèles discrets.
2. Équations et fonctions polynômes du second degré.

### Partie II — Analyse

3. Dérivation : point de vue local.
4. Dérivation : point de vue global, variations et courbes.
5. Fonction exponentielle.
6. Trigonométrie.

### Partie III — Géométrie

7. Calcul vectoriel et produit scalaire.
8. Géométrie repérée.

### Partie IV — Probabilités et statistiques

9. Probabilités conditionnelles et indépendance.
10. Variables aléatoires réelles.

### Dimensions transversales

Les dimensions suivantes sont distribuées dans les chapitres, suivies par une
matrice annuelle et synthétisées dans les annexes :

- vocabulaire ensembliste et logique ;
- algorithmique, programmation et listes ;
- automatismes : évolutions et variations, calcul numérique et algébrique,
  fonctions et représentations, statistiques, probabilités ;
- expérimentations : simulation d'échantillons, estimation d'une espérance par
  une moyenne observée et étude de l'écart entre moyenne et espérance.

Elles ne forment pas de chapitres isolés. Chaque item possède un emplacement
d'introduction, au moins un réinvestissement et un renvoi dans la banque
d'automatismes ou le mémo correspondant.

La rubrique « Expérimentations » est affectée au chapitre 10 « Variables
aléatoires réelles » et à la matrice transversale d'algorithmique. Elle comprend
les quatre attendus des lignes 627 à 638 de l'annexe officielle, notamment la
simulation de variables aléatoires et d'échantillons avec Python ou un tableur.

## 5. Architecture d'un chapitre

Chaque chapitre suit neuf temps stables :

1. ouverture et contrat du chapitre ;
2. diagnostic d'entrée et fiches de remise à niveau ;
3. activités de découverte guidée et ouverte ;
4. cours en strates essentielle, d'appui et d'approfondissement ;
5. fiches méthodes alignées sur les capacités ;
6. exercices de consolidation, maitrise et approfondissement ;
7. deux TD de synthèse ;
8. auto-évaluation et remédiation ;
9. évaluations A/B et corrigés-barèmes.

Chaque capacité est reliée à au moins une section de cours, une méthode, deux
exercices dans chacun des trois parcours, un item QCM et une remédiation.

## 6. Relation entre les deux ouvrages

Les deux ouvrages proviennent d'une même base d'objets et d'un même manifeste.

### Manuel élève

Il contient les pages liminaires, les apprentissages, les méthodes, les
exercices, les aides autorisées, les auto-évaluations, les évaluations et les
annexes élèves. Aucun corrigé intégral destiné au professeur ne doit fuiter dans
cette variante.

### Livre du professeur

Il reprend le parcours et les repères du manuel élève et ajoute :

- corrigés complets ;
- intentions et prérequis pédagogiques ;
- erreurs fréquentes anticipées ;
- conseils de différenciation ;
- barèmes et critères d'observation ;
- réponses aux diagnostics, QCM et évaluations ;
- cartes de couverture et tableaux de correspondance.

### 6.1 Architecture de pagination retenue

Les deux ouvrages ont des paginations indépendantes. Les pages professeur ne
sont pas intercalées dans l'espace de folios élève.

Le manuel élève est construit en premier. Il exporte une table canonique :

`object_id → folio_eleve`

Le livre du professeur est ensuite construit à partir de cette table et exporte :

`object_id → folio_professeur`

Tout renvoi professeur vers le manuel élève utilise la forme explicite
`Élève p. <folio_eleve>`. Un renvoi interne au livre du professeur utilise
`Prof. p. <folio_professeur>`. Aucun numéro de page n'est saisi directement dans
un objet source.

### 6.2 Cardinalités et gates

- chaque objet visible dans le manuel élève possède exactement un
  `folio_eleve` canonique ;
- chaque objet élève possède au moins une occurrence repérable dans le livre du
  professeur ;
- un objet exclusivement professeur a `folio_eleve: null` et exactement un
  `folio_professeur` canonique ;
- aucun identifiant canonique n'est dupliqué ;
- 100 % des renvois générés se résolvent ;
- la table de correspondance est publiée dans le manifeste de release et testée
  après chaque changement de pagination.

Lorsqu'un objet s'étend sur plusieurs pages, son folio canonique est la première
page sur laquelle commence son contenu principal. La plage complète reste
disponible dans les champs `first_page` et `last_page` du manifeste.

## 7. Chaîne de certification

Le flux est :

`B.O. exact → référentiel → objet LaTeX → mathématiques → pédagogie → langue → visuel → prépresse`

Un objet ou un assemblage possède un seul des états suivants :

- `certified` : toutes les preuves requises sont présentes ;
- `needs_fix` : défaut identifié, reproductible et corrigeable ;
- `blocked` : donnée ou validation externe indispensable.

Les statuts vagues, les dérogations silencieuses et les restes « à revoir » sont
interdits dans une version candidate au BAT.

Chaque verdict est un document conforme à schéma contenant au minimum :

- identifiant et type d'objet ;
- empreinte SHA-256 de l'objet et de ses dépendances ;
- identifiant et version du gate ;
- référentiel réglementaire et empreinte utilisés ;
- date, acteur de vérification et commande reproductible ;
- statut, constats et pièces de preuve.

Un objet est `certified` seulement si tous ses gates obligatoires sont
`certified` sur les mêmes empreintes. Un chapitre est `certified` seulement si
tous ses objets obligatoires le sont. Une release est `certified` seulement si
les dix chapitres, les blocs transversaux, les assemblages et les contrôles
prépresse numériques sont certifiés et qu'aucun `needs_fix` ou `blocked`
numérique ne subsiste.

### 7.1 Audit réglementaire

Une matrice relie chaque item officiel à :

- son type : contenu, capacité, démonstration, algorithme, approfondissement ou
  transversal ;
- sa citation exacte et sa page dans le PDF officiel ;
- le ou les objets du manuel qui le couvrent ;
- les folios élève et professeur ;
- la preuve de contrôle.

Les colonnes `obligation_class`, `bo_page`, `bo_quote`,
`manual_object_ids`, `student_folios`, `teacher_folios` et `verdict` sont
obligatoires. Les approfondissements possibles ont un verdict éditorial
`included`, `excluded_with_rationale` ou `not_applicable`, jamais
`missing_mandatory`.

### 7.2 Audit mathématique

- vérification symbolique ou numérique de toute affirmation calculable ;
- résolution indépendante des exercices, QCM et évaluations ;
- revue adversariale des démonstrations et raisonnements non calculables ;
- contrôle des hypothèses, domaines, cas limites, unités et arrondis ;
- concordance énoncé, aide, corrigé, barème et variante B.

### 7.3 Audit pédagogique

- prérequis explicites et progression sans dépendance circulaire ;
- exemples et contre-exemples pertinents ;
- charge cognitive, gradation et autonomie ;
- couverture équilibrée des six compétences mathématiques ;
- pertinence des distracteurs et des remédiations ;
- absence de faux contexte ou de décor pseudo-réaliste ;
- différenciation réelle entre les trois parcours.

### 7.4 Audit linguistique et éditorial

- français corrigé et accents présents ;
- notations cohérentes avec le B.O. ;
- titres, légendes, tableaux, unités et références homogènes ;
- absence de doublons, de texte provisoire et d'identifiants techniques visibles ;
- index, sommaires et renvois reconstruits et contrôlés.

L'audit met à jour `docs/05_conventions_latex.md` et les contrôleurs de notation
pour la règle contextuelle `u(n)` / `u_n` définie en section 2.1.

### 7.5 Propriété intellectuelle

Chaque objet conserve ses métadonnées de création et ses sources d'inspiration.
Les contrôles d'anti-similarité et les règles de licence existantes restent
bloquants. Aucun contenu de tiers n'est intégré sans droit ou transformation
conforme.

## 8. Direction graphique

### 8.1 Format

Le format fini validé est **195 × 270 mm**.

La grille doit :

- conserver une largeur suffisante pour les formules et tableaux ;
- permettre une composition à deux colonnes lorsqu'elle améliore le repérage ;
- revenir à une colonne pour les démonstrations, tableaux et diagnostics qui
  l'exigent ;
- réserver une marge intérieure compatible avec un ouvrage épais et cousu ;
- assurer une taille de lecture confortable sans réduction locale abusive.

Le budget de pagination cible est de 448 à 480 pages pour l'élève et de 512 à
544 pages pour le professeur. Les maxima de release sont respectivement 480 et
560 pages, pages techniques de cahiers comprises. Une réduction de corps ou une
compression locale n'est jamais utilisée pour respecter le budget. Un
dépassement rouvre la conception de pagination et le façonnage.

### 8.2 Système intérieur

La direction validée est **« V5 raffinée — Clarté Nexus »** :

- continuité avec le bleu profond, le safran et les accents secondaires de la
  maquette v5 ;
- hiérarchie plus calme ;
- moins de boites concurrentes ;
- davantage d'espace entre les unités ;
- un message secondaire dominant au maximum par zone ;
- onglets, badges et pictogrammes utilisés pour la navigation, pas comme décor.

### 8.3 Couvertures

Le système validé est **« Courbes signature »** :

- bleu profond ;
- courbes mathématiques et accent safran ;
- titre « Mathématiques » ;
- niveau « Première · spécialité » ;
- mention « Programme applicable à la rentrée 2026-2027 » ;
- auteur « Alaeddine BEN RHOUMA » ;
- déclinaisons clairement identifiables « Manuel élève » et « Professeur ».

La couverture ne doit jamais utiliser « manuel officiel », « homologué » ou une
formulation laissant croire à une approbation ministérielle.

## 9. Standard de fabrication

### 9.1 Intérieur

- quadrichromie CMJN ;
- papier offset blanc naturel haute opacité 80 g/m² ;
- certification FSC ou PEFC ;
- surface adaptée à l'annotation ;
- images continues à 300 ppp à leur taille finale ;
- dessins, courbes et formules en vectoriel ;
- traits techniques d'épaisseur imprimable.
- intention de sortie par défaut PSO Uncoated v3 / FOGRA52, adaptée au papier
  intérieur non couché, sous réserve du profil fourni par l'imprimeur.

### 9.2 Couverture

- 300 g/m² couché une face ;
- quadrichromie recto ;
- pelliculage mat anti-rayures ;
- dos calculé après pagination finale et mesure du papier réel ;
- intention de sortie par défaut PSO Coated v3 / FOGRA51 ;
- couverture livrée à plat, composée sur le gabarit validé de l'imprimeur.

### 9.3 Façonnage

- cahiers cousus ;
- collage PUR ;
- plan de cahiers déterminé avec l'imprimeur à partir du nombre final de pages ;
- sens du grain parallèle au dos ;
- prototype façonné obligatoire avant signature du BAT.

### 9.4 Fichiers prépresse

- format fini 195 × 270 mm ;
- fonds perdus 3 mm ;
- zone de sécurité minimale 5 mm ;
- marge intérieure renforcée selon la pagination et le façonnage ;
- polices entièrement incorporées ;
- noir de texte en noir seul ;
- noir enrichi réservé aux grands aplats de couverture ;
- taux d'encrage maximal 300 % ;
- master intérieur PDF/X-4 avec intention de sortie PSO Uncoated v3 / FOGRA52 ;
- master couverture PDF/X-4 avec intention de sortie PSO Coated v3 / FOGRA51 ;
- export de compatibilité PDF/X-1a uniquement avec les profils explicitement
  acceptés par l'imprimeur ;
- aucun contenu RVB non géré dans les masters ;
- surimpressions et transparences contrôlées.

Le profil final et le gabarit de couverture sont des paramètres d'interface
imprimeur. Toute substitution doit être déclarée dans le manifeste de
publication et repasser les contrôles prépresse.

### 9.5 Interface imprimeur et solution de repli

Nexus Réussite nomme l'imprimeur principal au plus tard le 3 août 2026 et un
prestataire de repli au plus tard le 5 août. Pour chacun, le dossier technique
doit fournir :

- procédé d'impression ;
- références, grammage, main, opacité et certifications du papier ;
- profils ICC acceptés ;
- taux d'encrage maximal ;
- gabarit de couverture et formule du dos ;
- contraintes de cahiers, sens du grain et reliure ;
- format PDF/X accepté ;
- calendrier d'épreuves et de façonnage.

Sans dossier imprimeur au 5 août, le pipeline produit les masters génériques
FOGRA52 intérieur et FOGRA51 couverture, mais le jalon reste
`blocked_external_printer` : ces fichiers sont des candidats prépresse, pas un
BAT signé.

## 10. Mentions légales et métadonnées de publication

La page légale contient au minimum :

- titre et version de l'ouvrage ;
- auteur : Alaeddine BEN RHOUMA ;
- éditeur légal : M&M ACADEMY SUARL ;
- marque éditoriale : Nexus Réussite ;
- raison sociale et adresse de l'éditeur ;
- copyright et année ;
- nom, adresse et pays de l'imprimeur ;
- lieu et date d'impression ;
- numéro d'édition et tirage ;
- mention de dépôt légal ;
- absence volontaire de ligne ISBN.

Les données variables sont fournies au générateur par un fichier de métadonnées
de publication validé par schéma. Une construction `release` échoue si un champ
légal obligatoire manque. Les valeurs d'imprimeur, de date et de tirage sont
renseignées après choix du prestataire et avant le BAT.

Sauf instruction juridique écrite contraire, la formulation éditoriale est :
« Édité par M&M ACADEMY SUARL sous la marque Nexus Réussite ». M&M ACADEMY
SUARL est responsable de l'inscription au registre, du dépôt légal et de la
conservation des preuves.

Le fichier de suivi légal contient :

- numéro et date d'inscription de chaque ouvrage ;
- date de mise à disposition du public ;
- preuve du dépôt de quatre exemplaires élève et quatre exemplaires professeur ;
- récépissé de la Bibliothèque nationale ;
- calcul et suivi du délai légal d'un mois.

L'adresse légale complète est fournie par Nexus Réussite au plus tard le
3 août. Le nom et l'adresse de l'imprimeur, le tirage et la date d'impression
sont gelés au plus tard lors de l'acceptation du gabarit de couverture.

## 11. Architecture de construction

Les sources suivent ce flux :

`objets certifiés → manifeste commun → socle élève → manuel élève`

`objets certifiés → manifeste commun + enrichissements → livre professeur`

Chaque build produit :

- un PDF de contrôle ;
- un journal LaTeX ;
- un manifeste d'objets et de renvois ;
- un rapport de conformité PDF ;
- les empreintes SHA-256.

L'ordre de construction est bloquant :

1. construire l'élève et exporter `folios-eleve.json` ;
2. valider l'unicité et la complétude des folios ;
3. construire le professeur en injectant cette table ;
4. exporter `folios-professeur.json` et la table croisée ;
5. refuser la release au moindre renvoi non résolu.

Les masters d'impression et les PDF écran sont des sorties distinctes. Le PDF
écran privilégie les signets, liens et l'accessibilité ; le master privilégie
PDF/X, la colorimétrie et le façonnage.

### 11.1 Contrat des PDF écran accessibles

Les PDF écran ciblent PDF/UA-1 et les critères WCAG 2.2 niveau AA applicables
aux documents :

- PDF balisé et arbre de structure complet ;
- langue principale `fr-FR`, titre, auteur et métadonnées renseignés ;
- ordre de lecture logique sur chaque page ;
- hiérarchie de titres et signets cohérente ;
- texte sélectionnable et recherchable ;
- tableaux avec en-têtes et associations de cellules ;
- figures informatives avec texte alternatif, décors marqués comme artefacts ;
- liens nommés et annotations correctement balisées ;
- formules importantes avec texte de remplacement ou représentation accessible
  permettant une lecture non ambiguë ;
- contraste minimal de 4,5:1 pour le texte courant, 3:1 pour le grand texte et
  les éléments graphiques porteurs d'information ;
- navigation clavier sans piège dans les éléments interactifs.

Le gate exige :

- zéro échec dans un validateur PDF/UA indépendant tel que PAC ou veraPDF, avec
  version de l'outil consignée ;
- zéro incohérence de langue, titre, signets ou balises dans les contrôles
  automatisés ;
- 100 % des pages contrôlées pour l'ordre d'extraction textuelle ;
- 100 % des figures et tableaux présents dans l'inventaire d'accessibilité ;
- validation manuelle des points non automatisables avec lecteur d'écran et
  navigation clavier sur chaque famille de pages.

Si l'outil de composition ne permet pas de satisfaire PDF/UA-1, le PDF écran
reste `needs_fix` ou `blocked` ; il n'est jamais qualifié d'accessible par
simple présence de texte sélectionnable.

## 12. Contrôles et prévention des régressions

Les gates bloquants couvrent :

- exhaustivité du programme ;
- schémas de métadonnées ;
- vérifications mathématiques ;
- résolution indépendante des évaluations ;
- anti-similarité ;
- compilation de chaque chapitre et des deux livres ;
- absence de références non résolues ;
- cohérence des folios élève/professeur ;
- absence de débordements et collisions ;
- pages blanches uniquement si déclarées ;
- intégrité des polices, images et profils colorimétriques ;
- conformité PDF/X ;
- conformité PDF/UA-1 et WCAG 2.2 AA applicable pour les PDF écran ;
- comparaison visuelle sur pages témoins et échantillonnage de toutes les
  familles de pages ;
- reconstruction reproductible depuis un environnement propre.

Les seuils numériques minimaux sont :

- 0 référence LaTeX non résolue ;
- 0 `Overfull \hbox` ou `Overfull \vbox` dans les masters ;
- 0 objet obligatoire sans preuve sur l'empreinte courante ;
- 0 page dont une boite de contenu franchit la zone de sécurité déclarée ;
- 0 police non incorporée ;
- 0 image continue sous 300 ppp à taille finale ;
- 0 trait technique sous 0,25 pt ;
- 0 couleur RVB non gérée dans un master ;
- taux d'encrage inférieur ou égal à 300 % ;
- 100 % des pages rasterisées et contrôlées automatiquement ;
- 100 % des pages parcourues visuellement à taille lisible par un agent de
  relecture, puis par le signataire du BAT sur l'épreuve ;
- 100 % des familles de pages comparées aux références visuelles approuvées.

Le contrôle PDF/X comprend la génération normalisée, les inspections
`pdfinfo`/`pdffonts`/images/couleurs et un préflight indépendant fourni par
l'imprimeur ou un outil certifié. Le simple marquage `GTS_PDFXVersion` ne vaut
pas preuve de conformité.

Chaque correction d'un défaut reproductible ajoute ou renforce un test. Une
modification postérieure au gel éditorial invalide automatiquement les preuves
portant sur les objets ou assemblages affectés.

## 13. Critères d'acceptation du BAT

Le BAT n'est proposé que si :

1. 100 % des `mandatory_content` et `prescribed_teaching` du B.O. sont couverts
   et tracés, tandis que les `optional_extension` sont séparés ;
2. aucune erreur mathématique connue ne subsiste ;
3. aucune divergence énoncé-corrigé-barème ne subsiste ;
4. toutes les dimensions transversales sont couvertes sur l'année ;
5. aucun texte provisoire, doublon, identifiant technique ou renvoi rompu ne
   subsiste ;
6. les versions élève et professeur sont cohérentes ;
7. le français, les notations, figures, tableaux et index sont relus ;
8. les masters passent les contrôles prépresse ;
9. les mentions légales sont complètes ;
10. l'épreuve physique et le prototype façonné sont approuvés.

Les validations non automatisables sont explicites :

- revue éditoriale et mathématique indépendante ;
- approbation des mentions légales par l'éditeur ;
- validation de l'épreuve et du prototype par l'éditeur et l'imprimeur ;
- signature du procès-verbal de BAT.

Les jalons ont des sens distincts :

1. `digital_candidate` : sources, PDF écran et contrôles éditoriaux verts ;
2. `printer_package` : masters génériques et dossier technique complet ;
3. `printer_accepted` : profils et gabarits acceptés par l'imprimeur ;
4. `prototype_approved` : épreuve et prototype façonné approuvés ;
5. `bat_signed` : procès-verbal signé ;
6. `legal_deposit_completed` : mise à disposition datée, huit exemplaires
   déposés et récépissés archivés.

Aucun jalon n'est présenté comme équivalent au suivant.

## 14. Calendrier cible

- 27 juillet–1er août 2026 : inventaire, matrice B.O. et audit initial ;
- 2 août : gel de la baseline et estimation révisée de charge ;
- 3 août : adresse légale et imprimeur principal nommés ;
- 5 août : imprimeur de repli et dossiers techniques reçus ;
- 3–16 août : corrections mathématiques, pédagogiques et transversales ;
- 10–20 août : format 195 × 270, système intérieur et couvertures ;
- 17–20 août : première release candidate numérique ;
- 21 août : première épreuve et premier prototype ;
- 22–25 août : corrections et seconde release candidate ;
- 26–28 août : seconde épreuve ou prototype de repli si nécessaire ;
- 29 août : gel du paquet imprimeur final ;
- 30 août : validation finale ;
- **31 août 2026 à 18 h 00, heure de Tunis : échéance contractuelle du BAT
  signé**, avec une journée de marge après le gel final.

Les travaux éditoriaux et graphiques peuvent se chevaucher uniquement lorsque
leurs interfaces sont gelées. Un changement de contenu qui modifie la pagination
réouvre les contrôles de renvois et de prépresse.

Si la baseline du 2 août révèle une charge incompatible avec la date, la règle
de décision est : conformité et exactitude priment sur la quantité
d'approfondissements facultatifs, puis sur les enrichissements non demandés.
Aucun contenu obligatoire ni gate n'est supprimé pour tenir le calendrier.

## 15. Livrables finaux

- master PDF/X-4 du manuel élève ;
- master PDF/X-4 du livre du professeur ;
- couvertures à plat élève et professeur ;
- exports PDF/X-1a si requis ;
- PDF écran élève et professeur ;
- sources LaTeX reproductibles ;
- manifeste de publication ;
- matrice de conformité B.O. ;
- rapports mathématique, pédagogique, linguistique, visuel et prépresse ;
- licences des polices et inventaire des ressources ;
- page légale finalisée ;
- instructions de papier, impression et façonnage ;
- fichier d'empreintes SHA-256 ;
- procès-verbal de BAT à signer ;
- protocole de dépôt légal en Tunisie.

## 16. Autorité de validation

Les agents de production peuvent corriger, vérifier et recommander. Ils ne
remplacent pas :

- la responsabilité éditoriale de Nexus Réussite ;
- la validation physique de l'imprimeur ;
- la signature humaine du BAT ;
- l'accomplissement du dépôt légal.

La version n'est déclarée « prête pour impression » qu'après disparition de tous
les bloqueurs numériques et remise du paquet complet à l'imprimeur. Elle n'est
déclarée « bon à tirer signé » qu'après validation du prototype physique par les
parties responsables.

### 16.1 RACI

| Activité | Responsable | Approbateur | Consultés / informés |
|---|---|---|---|
| Baseline, sources et builds | agent de production | Alaeddine BEN RHOUMA | agents de revue |
| Conformité B.O. | agent de conformité indépendant | Alaeddine BEN RHOUMA | relecteur pédagogique |
| Mathématiques et corrigés | agents mathématiques indépendants | Alaeddine BEN RHOUMA | agent adversarial |
| Langue et maquette | agents éditorial et visuel | Alaeddine BEN RHOUMA | agent prépresse |
| Données légales | M&M ACADEMY SUARL | représentant légal | agent de production |
| Profils, dos et prototype | imprimeur | M&M ACADEMY SUARL | agent prépresse |
| BAT | M&M ACADEMY SUARL | signataire habilité | imprimeur et auteur |
| Dépôt légal | M&M ACADEMY SUARL | représentant légal | Bibliothèque nationale |

### 16.2 Versionnement des candidats

Chaque release candidate reçoit un identifiant immuable `1SPE-RC<n>`, un
commit Git et un manifeste signé par empreintes SHA-256. Toutes les preuves
référencent l'identifiant et les empreintes du candidat. Une modification crée
un nouveau candidat ; aucune preuve n'est transférée sans contrôle d'impact.
