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

Nexus Réussite devra déposer quatre exemplaires de chaque livre produit ou
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
  fonctions et représentations, statistiques, probabilités.

Elles ne forment pas de chapitres isolés. Chaque item possède un emplacement
d'introduction, au moins un réinvestissement et un renvoi dans la banque
d'automatismes ou le mémo correspondant.

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

Tout renvoi à une page élève doit rester fiable dans la version professeur. Le
générateur utilise des identifiants d'objets et une table de renvois, jamais des
numéros saisis manuellement. Si une pagination strictement identique ne peut
être maintenue, chaque renvoi professeur affiche explicitement le folio élève.

## 7. Chaîne de certification

Le flux est :

`B.O. exact → référentiel → objet LaTeX → mathématiques → pédagogie → langue → visuel → prépresse`

Un objet ou un assemblage possède un seul des états suivants :

- `certified` : toutes les preuves requises sont présentes ;
- `needs_fix` : défaut identifié, reproductible et corrigeable ;
- `blocked` : donnée ou validation externe indispensable.

Les statuts vagues, les dérogations silencieuses et les restes « à revoir » sont
interdits dans une version candidate au BAT.

### 7.1 Audit réglementaire

Une matrice relie chaque item officiel à :

- son type : contenu, capacité, démonstration, algorithme, approfondissement ou
  transversal ;
- sa citation exacte et sa page dans le PDF officiel ;
- le ou les objets du manuel qui le couvrent ;
- les folios élève et professeur ;
- la preuve de contrôle.

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

### 9.2 Couverture

- 300 g/m² couché une face ;
- quadrichromie recto ;
- pelliculage mat anti-rayures ;
- dos calculé après pagination finale et mesure du papier réel ;
- fichiers séparés première, dos, quatrième ou gabarit à plat selon l'imprimeur.

### 9.3 Façonnage

- cahiers cousus ;
- collage PUR ;
- plan de cahiers déterminé avec l'imprimeur à partir du nombre final de pages ;
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
- master PDF/X-4 avec intention de sortie PSO Coated v3 / FOGRA51 ;
- export de compatibilité PDF/X-1a / FOGRA39 si demandé par l'imprimeur ;
- aucun contenu RVB non géré dans les masters ;
- surimpressions et transparences contrôlées.

Le profil final et le gabarit de couverture sont des paramètres d'interface
imprimeur. Toute substitution doit être déclarée dans le manifeste de
publication et repasser les contrôles prépresse.

## 10. Mentions légales et métadonnées de publication

La page légale contient au minimum :

- titre et version de l'ouvrage ;
- auteur : Alaeddine BEN RHOUMA ;
- éditeur : Nexus Réussite ;
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

Les masters d'impression et les PDF écran sont des sorties distinctes. Le PDF
écran privilégie les signets, liens et l'accessibilité ; le master privilégie
PDF/X, la colorimétrie et le façonnage.

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
- comparaison visuelle sur pages témoins et échantillonnage de toutes les
  familles de pages ;
- reconstruction reproductible depuis un environnement propre.

Chaque correction d'un défaut reproductible ajoute ou renforce un test. Une
modification postérieure au gel éditorial invalide automatiquement les preuves
portant sur les objets ou assemblages affectés.

## 13. Critères d'acceptation du BAT

Le BAT n'est proposé que si :

1. 100 % des items du B.O. sont couverts et tracés ;
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

## 14. Calendrier cible

- 27 juillet–2 août 2026 : inventaire, matrice B.O. et audit initial ;
- 3–16 août : corrections mathématiques, pédagogiques et transversales ;
- 10–20 août : format 195 × 270, système intérieur et couvertures ;
- 17–23 août : assemblages, relectures et gates ;
- 24–27 août : épreuves imprimeur et prototype ;
- 28–30 août : corrections finales, BAT et archivage.

Les travaux éditoriaux et graphiques peuvent se chevaucher uniquement lorsque
leurs interfaces sont gelées. Un changement de contenu qui modifie la pagination
réouvre les contrôles de renvois et de prépresse.

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
