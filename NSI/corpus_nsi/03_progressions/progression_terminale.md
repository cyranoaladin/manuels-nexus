# Progression annuelle NSI Terminale - Tunisie 2026-2027

- Statut : prototype annuel non publiable.
- Base horaire : calendrier scolaire Tunisie 2026-2027, voir `calendar_2026_2027_tunisia.md`.
- Hypothèse horaire NSI Terminale : 210 h annuelles.
- Projet exigé : au moins 52,5 h.
- Projet planifié : 60 h, soit 28,6 %.
- Décision pédagogique : aucune ressource n'est publiée ; aucune capacité n'est déclarée `covered` par cette progression.
- Séquence pilote existante : `terminale/sequences/s01_structures_donnees_interfaces_implementations/` conservée comme prototype à découper.
- Variante plus sûre : BDD et SQL sont avancés avant Ramadan, Boyer-Moore est anticipé avant juin, Grand Oral et pratique bac sont distribués de janvier à juin.

## Répartition annuelle révisée

| Séquence | Mois dominant | Volume | Projet | Capacités atomiques principales | Évaluation prévue | Période sensible |
|---|---:|---:|---:|---|---|---|
| T00 - Reprise Python, tests, complexité de base | septembre | 8 h | 2 h | T-HIST-01A, T-HIST-01B, T-LANG-03A, T-LANG-05 | diagnostic + mini-problème | reprise |
| T01 - Structures abstraites, interface, implémentation | septembre | 10 h | 2 h | T-STRUCT-01A, T-STRUCT-01B, T-STRUCT-01C | analyse courte | favorable |
| T02 - POO utile : classes, attributs, méthodes | septembre-octobre | 10 h | 2 h | T-STRUCT-02A, T-STRUCT-02B, T-LANG-04A | programmation guidée | favorable |
| T03 - Piles, files, dictionnaires, choix de structure | octobre-novembre | 12 h | 3 h | T-STRUCT-03A, T-STRUCT-03B, T-STRUCT-03C | TP noté court | favorable |
| T04 - Récursivité et preuves de terminaison | novembre | 10 h | 2 h | T-LANG-02A, T-LANG-02B | devoir court | favorable |
| T05 - Arbres binaires, taille, hauteur, parcours | novembre | 10 h | 2 h | T-STRUCT-04A, T-STRUCT-04B, T-ALGO-01A, T-ALGO-01B, T-ALGO-01C, T-ALGO-01D | exercices + code | favorable |
| T06 - Arbres binaires de recherche | décembre | 10 h | 2 h | T-ALGO-01E, T-ALGO-01F | TP + analyse | fin de période |
| T07 - Graphes : modélisation, listes/matrices | décembre-janvier | 10 h | 3 h | T-STRUCT-05A, T-STRUCT-05B, T-STRUCT-05C, T-STRUCT-05D | modélisation | favorable |
| T08 - Graphes : BFS, DFS, cycles, chemins | janvier-début février | 12 h | 3 h | T-ALGO-02A, T-ALGO-02B, T-ALGO-02C, T-ALGO-02D | TP + sujet pratique | coeur avant Ramadan |
| T09 - Bases de données relationnelles : modèle, clés, contraintes | décembre-janvier | 12 h | 3 h | T-BDD-01A, T-BDD-01B, T-BDD-01C, T-BDD-02 | étude de schéma | avant Ramadan |
| T10 - SQL : SELECT, FROM, WHERE, JOIN, ORDER BY, INSERT, UPDATE, DELETE | janvier-début février | 10 h | 3 h | T-BDD-03A, T-BDD-03B, T-BDD-03C, T-BDD-03D, T-BDD-03E, T-BDD-03F, T-BDD-03G, T-BDD-03H | pratique guidée | exercices guidés pendant Ramadan |
| T11 - Systèmes : SoC, processus, ordonnancement, interblocage | mars | 10 h | 2 h | T-ARCH-01, T-ARCH-02A, T-ARCH-02B, T-ARCH-02C | analyse de situations | reprise après Aïd |
| T12 - Réseaux : routage RIP/OSPF, lien avec graphes | mars-avril | 10 h | 3 h | T-ARCH-03 | exercice réseau | favorable |
| T13 - Sécurité : chiffrement symétrique/asymétrique, HTTPS | avril | 10 h | 3 h | T-ARCH-04A, T-ARCH-04B | étude de protocole | favorable |
| T14 - Langages : modularité, API, paradigmes, bugs | avril-mai | 10 h | 3 h | T-LANG-03A, T-LANG-03B, T-LANG-03C, T-LANG-04A, T-LANG-04B, T-LANG-05 | revue de code | Aïd al-Adha en mai |
| T15 - Calculabilité, programme comme donnée, arrêt | mai | 6 h | 1 h | T-LANG-01A, T-LANG-01B, T-LANG-01C | activité courte argumentée | période sensible |
| T16 - Diviser pour régner, tri fusion | mai | 10 h | 3 h | T-ALGO-03 | devoir algorithmique | période sensible |
| T17 - Programmation dynamique | mai-juin | 10 h | 3 h | T-ALGO-04 | problème guidé | favorable après Aïd |
| T18 - Boyer-Moore | avril-mai | 8 h | 2 h | T-ALGO-05 | analyse d'algorithme | anticipé avant juin |
| T19 - Bac écrit, pratique, Grand Oral, projet final | janvier-juin | 22 h | 13 h | synthèse atomique | entraînements distribués | fil rouge |
| **Total** | année | **210 h** | **60 h** | toutes les capacités identifiées | évaluations réparties | marge intégrée |

## Décisions de charge

- SQL est concentré avant le 8 février ; pendant Ramadan, les séances SQL restantes sont des exercices guidés, corrections courtes et remédiations.
- Boyer-Moore n'est plus lancé en juin : la découverte est placée en avril-mai et juin reste réservé aux entraînements, finalisation et oral.
- La calculabilité est maintenue comme activité courte de mai, sans surcharge de preuve formelle.
- Grand Oral, bac écrit et bac pratique commencent en janvier par micro-oraux et sujets courts, puis sont repris en T19.
- T-ALGO-02A à T-ALGO-02D restent `partial` tant que les documents graphes dédiés ne sont pas relus.

## Détails par séquence

## T00 - Reprise Python, tests, complexité de base

- Mois : septembre.
- Volume horaire : 8 h, dont 2 h de projet.
- Documents à produire : diagnostic, tests, complexité intuitive, carnet de bord.
- TD ou TP : fonctions testées et correction de bug.
- Évaluation : micro-problème court.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : mise en place du dépôt projet.
- Différenciation : rappels guidés ou analyse de coût.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : bac écrit : lecture de code ; pratique : tests ; oral : expliquer un bug.

## T01 - Structures abstraites, interface, implémentation

- Mois : septembre.
- Volume horaire : 10 h, dont 2 h de projet.
- Documents à produire : interface, opérations, invariants, implémentations.
- TD ou TP : spécifier une structure et comparer deux représentations.
- Évaluation : analyse courte.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : interface d’un composant projet.
- Différenciation : table d’opérations fournie ou coût comparé.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : écrit : abstraction ; pratique : respecter une interface ; oral : choix technique.

## T02 - POO utile : classes, attributs, méthodes

- Mois : septembre-octobre.
- Volume horaire : 10 h, dont 2 h de projet.
- Documents à produire : classe, attribut, méthode, état.
- TD ou TP : lecture de classe et écriture guidée.
- Évaluation : programmation guidée.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : classe métier testée.
- Différenciation : squelette fourni ou invariants.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : écrit : état d’objet ; pratique : classe ; oral : encapsulation.

## T03 - Piles, files, dictionnaires, choix de structure

- Mois : octobre-novembre.
- Volume horaire : 12 h, dont 3 h de projet.
- Documents à produire : LIFO, FIFO, clé, accès par dictionnaire.
- TD ou TP : choisir selon opérations dominantes.
- Évaluation : TP noté court.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : simulateur pile/file/dictionnaire.
- Différenciation : cartes opérations ou discussion coût.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : écrit : états successifs ; pratique : pile/file ; oral : usage.

## T04 - Récursivité et preuves de terminaison

- Mois : novembre.
- Volume horaire : 10 h, dont 2 h de projet.
- Documents à produire : cas de base, appel récursif, variant.
- TD ou TP : arbres d’appels et fonctions récursives.
- Évaluation : devoir court.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : fonction récursive documentée.
- Différenciation : schémas guidés ou variantes.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : écrit : terminaison ; pratique : récursivité ; oral : définition récursive.

## T05 - Arbres binaires, taille, hauteur, parcours

- Mois : novembre.
- Volume horaire : 10 h, dont 2 h de projet.
- Documents à produire : arbre, taille, hauteur, parcours.
- TD ou TP : calculer et programmer parcours.
- Évaluation : exercices + code.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : hiérarchie fictive.
- Différenciation : arbres dessinés ou coût.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : écrit : mesures ; pratique : parcours ; oral : hiérarchie.

## T06 - Arbres binaires de recherche

- Mois : décembre.
- Volume horaire : 10 h, dont 2 h de projet.
- Documents à produire : propriété ABR, recherche, insertion.
- TD ou TP : vérifier, insérer, repérer dégénérescence.
- Évaluation : TP + analyse.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : recherche ABR testée.
- Différenciation : valeurs guidées ou limites.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : écrit : propriété ; pratique : recherche ; oral : arbre dégénéré.

## T07 - Graphes : modélisation, listes/matrices

- Mois : décembre-janvier.
- Volume horaire : 10 h, dont 3 h de projet.
- Documents à produire : sommets, arêtes, orientation, matrice, liste.
- TD ou TP : modéliser et convertir.
- Évaluation : modélisation.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : graphe du projet.
- Différenciation : graphe dessiné ou coût mémoire.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : écrit : représentations ; pratique : construire ; oral : modèle.

## T08 - Graphes : BFS, DFS, cycles, chemins

- Mois : janvier-début février.
- Volume horaire : 12 h, dont 3 h de projet.
- Documents à produire : BFS, DFS, cycle, chemin.
- TD ou TP : tracer et coder sur petits graphes.
- Évaluation : TP + sujet pratique.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : parcours limité.
- Différenciation : petits graphes ou extensions cycles.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : écrit : ordre de visite ; pratique : parcours ; oral : chemin.

## T09 - Bases relationnelles : modèle, clés, contraintes

- Mois : décembre-janvier.
- Volume horaire : 12 h, dont 3 h de projet.
- Documents à produire : relation, attribut, domaine, clé, schéma, SGBD.
- TD ou TP : analyser un schéma fictif.
- Évaluation : étude de schéma.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : base fictive du projet.
- Différenciation : schéma annoté ou anomalies.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : écrit : schéma ; pratique : SQLite ; oral : qualité donnée.

## T10 - SQL atomique

- Mois : janvier-début février.
- Volume horaire : 10 h, dont 3 h de projet.
- Documents à produire : SELECT, FROM, WHERE, JOIN, ORDER BY, INSERT, UPDATE, DELETE.
- TD ou TP : requêtes guidées avant Ramadan.
- Évaluation : pratique guidée.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : requêtes projet.
- Différenciation : requêtes à trous ou jointures.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : écrit : clause ; pratique : SQL ; oral : usage/limite.

## T11 - Systèmes : SoC, processus, ordonnancement, interblocage

- Mois : mars.
- Volume horaire : 10 h, dont 2 h de projet.
- Documents à produire : SoC, processus, ressources, ordonnancement.
- TD ou TP : scénarios et observation contrôlée.
- Évaluation : analyse de situations.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : note système.
- Différenciation : scénarios guidés ou politique.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : écrit : processus ; pratique : simulation ; oral : système invisible.

## T12 - Réseaux : routage RIP/OSPF

- Mois : mars-avril.
- Volume horaire : 10 h, dont 3 h de projet.
- Documents à produire : table de routage, distance, état de lien.
- TD ou TP : calculer routes sur graphes.
- Évaluation : exercice réseau.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : routage simulé.
- Différenciation : réseau à quatre nœuds ou convergence.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : écrit : RIP/OSPF ; pratique : chemin ; oral : routes.

## T13 - Sécurité : chiffrement et HTTPS

- Mois : avril.
- Volume horaire : 10 h, dont 3 h de projet.
- Documents à produire : symétrique, asymétrique, échange de clé.
- TD ou TP : analyser un protocole simplifié.
- Évaluation : étude de protocole.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : fiche sécurité projet.
- Différenciation : schémas étapes ou attaque.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : écrit : clés ; pratique : simulation ; oral : confiance.

## T14 - Langages : modularité, API, paradigmes, bugs

- Mois : avril-mai.
- Volume horaire : 10 h, dont 3 h de projet.
- Documents à produire : module, API, paradigme, bug.
- TD ou TP : refactoriser et documenter.
- Évaluation : revue de code.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : module stabilisé.
- Différenciation : grille simplifiée ou comparaison.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : écrit : modularité ; pratique : debug ; oral : architecture.

## T15 - Calculabilité, programme comme donnée, arrêt

- Mois : mai.
- Volume horaire : 6 h, dont 1 h de projet.
- Documents à produire : programme-donnée, calculabilité, arrêt.
- TD ou TP : activité courte argumentée.
- Évaluation : questions brèves.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : capsule orale.
- Différenciation : exemples concrets ou approfondissement marqué.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : écrit : argument ; pratique : terminaison ; oral : limites.

## T16 - Diviser pour régner, tri fusion

- Mois : mai.
- Volume horaire : 10 h, dont 3 h de projet.
- Documents à produire : découper, résoudre, combiner.
- TD ou TP : tri fusion et traces.
- Évaluation : devoir algorithmique.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : tri instrumenté.
- Différenciation : pseudo-code ou complexité.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : écrit : stratégie ; pratique : tri ; oral : efficacité.

## T17 - Programmation dynamique

- Mois : mai-juin.
- Volume horaire : 10 h, dont 3 h de projet.
- Documents à produire : sous-problèmes, mémoïsation, table.
- TD ou TP : transformer une solution récursive.
- Évaluation : problème guidé.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : optimisation limitée.
- Différenciation : table préremplie ou compromis.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : écrit : table ; pratique : mémoïsation ; oral : temps-mémoire.

## T18 - Boyer-Moore

- Mois : avril-mai.
- Volume horaire : 8 h, dont 2 h de projet.
- Documents à produire : motif, texte, table de décalage.
- TD ou TP : tracer une recherche textuelle.
- Évaluation : analyse d’algorithme.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : recherche textuelle.
- Différenciation : alphabet réduit ou variante.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : écrit : trace ; pratique : chaîne ; oral : prétraitement.

## T19 - Bac écrit, pratique, Grand Oral, projet final

- Mois : janvier-juin.
- Volume horaire : 22 h, dont 13 h de projet.
- Documents à produire : révisions, sujets pratiques, oral, projet.
- TD ou TP : entraînements courts distribués puis synthèse.
- Évaluation : bac blanc fragmenté.
- Sujet pratique : entraînement lié à la capacité dominante, sans publication.
- Projet : dossier et soutenance.
- Différenciation : sujets gradués ou amélioration.
- Ressources Drive candidates : à identifier dans `drive_inventory.csv`, sans intégration locale à ce stade.
- Liens bac et Grand Oral : écrit : toutes rubriques ; pratique : sujets ; oral : problématique.

## Capacités atomiques planifiées

T-HIST-01A, T-HIST-01B, T-STRUCT-01A, T-STRUCT-01B, T-STRUCT-01C, T-STRUCT-02A, T-STRUCT-02B, T-STRUCT-03A, T-STRUCT-03B, T-STRUCT-03C, T-STRUCT-04A, T-STRUCT-04B, T-STRUCT-05A, T-STRUCT-05B, T-STRUCT-05C, T-STRUCT-05D, T-BDD-01A, T-BDD-01B, T-BDD-01C, T-BDD-02, T-BDD-03A, T-BDD-03B, T-BDD-03C, T-BDD-03D, T-BDD-03E, T-BDD-03F, T-BDD-03G, T-BDD-03H, T-ARCH-01, T-ARCH-02A, T-ARCH-02B, T-ARCH-02C, T-ARCH-03, T-ARCH-04A, T-ARCH-04B, T-LANG-01A, T-LANG-01B, T-LANG-01C, T-LANG-02A, T-LANG-02B, T-LANG-03A, T-LANG-03B, T-LANG-03C, T-LANG-04A, T-LANG-04B, T-LANG-05, T-ALGO-01A, T-ALGO-01B, T-ALGO-01C, T-ALGO-01D, T-ALGO-01E, T-ALGO-01F, T-ALGO-02A, T-ALGO-02B, T-ALGO-02C, T-ALGO-02D, T-ALGO-03, T-ALGO-04, T-ALGO-05.
