# Contre-expertise des attendus non couverts

Artefact derive : `audit/PROGRAMME_COUNTER_EXPERTISE_REPORT.json`.
Aucun chiffre de cette page n'est saisi a la main ; tous viennent du
generateur `scripts/build_counter_expertise_report.py`, qui compare
la ligne de base `af8506b79` a la matrice courante.

## Synthese

| Compteur | Valeur |
| --- | --- |
| MISSING_BEFORE | 13 |
| PARTIAL_BEFORE | 45 |
| UNDECIDABLE_BEFORE | 3 |
| FALSE_MISSING_TOOLING | 7 |
| MISSING_FROM_ASSEMBLY | 4 |
| TRUE_CONTENT_GAP | 2 |
| FALSE_PARTIAL_TOOLING | 42 |
| TRUE_PARTIAL_PEDAGOGICAL | 3 |
| UNDECIDABLE_FALSE_MISSING_TOOLING | 2 |
| UNDECIDABLE_TRUE_CONTENT_GAP | 1 |
| OFFICIAL_REQUIRED_MISSING_NOW | 0 |
| OFFICIAL_REQUIRED_PARTIAL_NOW | 0 |
| CONTENT_CREATED_FOR_TRUE_MISSING | 2 |
| CONTENT_CREATED_FOR_TRUE_PARTIAL_PEDAGOGICAL | 6 |
| CONTENT_CREATED_AFTER_UNDECIDABLE_REVIEW | 1 |
| CONTENT_CREATED_FOR_NEXUS_QUALITY_ENRICHMENT | 2 |

## Les anciens « manquants »

| Manuel | Attendu officiel | Ancien verdict | Verdict apres contre-expertise | Cause | Preuve existante | Modification | Contenu ecrit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1NSI | Utilisation de bibliothèques | MISSING | FALSE_MISSING_TOOLING | la ligne du tableau officiel n'etait pas conservee : le contenu et les capacites qui le realisent etaient mesures separement | 1NSI-LANG-COURS-C5, 1NSI-LANG-EVAL-B, 1NSI-LANG-M3, 1NSI-LANGAGE-QCM | preuve etablie par OFFICIAL_ROW_EVIDENCE | NO |
| 1SPE | Utiliser un repère pour étudier une configuration. | MISSING | FALSE_MISSING_TOOLING | le mot « configuration » ne figure dans aucun objet, alors que c'est le seul terme distinctif du libelle avec « repere » | 1SPE-GEOMETRIE-REPEREE-QCM, 1SPE-GEOREP-CO-020, 1SPE-GEOREP-CO-031, 1SPE-GEOREP-CO-032, 1SPE-GEOREP-CO-033, 1SPE-GEOREP-CO-034 | revue contradictoire declaree ; verdict rendu a la lecture de l'objet : FALSE_MISSING_TOOLING | NO |
| TCOMPL | Continuité et dérivation. | MISSING | FALSE_MISSING_TOOLING | l'attendu n'etait rattache a aucun atome, et le rapprochement par contenu ne concluait pas | TCOMPL-AIR-CO-010, TCOMPL-AIR-CR-010, TCOMPL-AIR-CR-012, TCOMPL-AIR-EV-B, TCOMPL-AIR-EV-B-corrige, TCOMPL-AIR-EX-009 | preuve etablie par CONTENT_MATCH | NO |
| TCOMPL | Statistique descriptive : caractéristiques de dispersion (médiane, quartiles, déciles, rap | MISSING | TRUE_CONTENT_GAP | aucun cours du manuel n'exposait mediane, quartiles, deciles ni rapport interdecile | TCOMPL-INEG-CR-009 | cours redige : dispersion, quartiles, deciles, rapport interdecile, exemple travaille sur vingt revenus | YES |
| TCOMPL | lire et écrire des propositions contenant les connecteurs « et », « ou » ; | MISSING | MISSING_FROM_ASSEMBLY | meme cause : page transversale existante, absente de l'assemblage TCOMPL | TCOMPL-TRANSVERSAL-LOGIQUE_RAISONNEMENT | ANNEXES_TRANSVERSALES etendu | NO |
| TCOMPL | formuler une implication, une équivalence logique, et à les mobiliser dans un raisonnement | MISSING | MISSING_FROM_ASSEMBLY | meme cause : page transversale existante, absente de l'assemblage TCOMPL | TCOMPL-TRANSVERSAL-LOGIQUE_RAISONNEMENT | ANNEXES_TRANSVERSALES etendu | NO |
| TCOMPL | reconnaître ce qu’est une proposition mathématique, à utiliser des variables pour écrire d | MISSING | MISSING_FROM_ASSEMBLY | la page transversale de logique existait, mais l'assembleur ne la portait dans aucun manuel de terminale complementaire | TCOMPL-TRANSVERSAL-LOGIQUE_RAISONNEMENT | ANNEXES_TRANSVERSALES etendu : une source logique canonique, plusieurs assemblages | NO |
| TCOMPL | lire et écrire des propositions contenant une quantification universelle ou existentielle  | MISSING | MISSING_FROM_ASSEMBLY | meme cause : page transversale existante, absente de l'assemblage TCOMPL | TCOMPL-TRANSVERSAL-LOGIQUE_RAISONNEMENT | ANNEXES_TRANSVERSALES etendu | NO |
| TEXPERTES | Effectuer des calculs sur des nombres complexes en choisissant une forme adaptée, en parti | MISSING | FALSE_MISSING_TOOLING | les termes du libelle -- « effectuer », « calculs », « choisissant », « adaptee » -- sont trop generiques pour designer quoi que ce soit | TEXP-CTP-CR-010, TEXP-CTP-ME-001, TEXP-CTP-ME-002 | revue contradictoire declaree ; verdict rendu a la lecture de l'objet : FALSE_MISSING_TOOLING | NO |
| TNSI | Sécurisation des communications. | MISSING | FALSE_MISSING_TOOLING | la ligne du tableau officiel n'etait pas conservee : le contenu et les capacites qui le realisent etaient mesures separement | TNSI-ARCH-CO-004, TNSI-ARCH-CO-007, TNSI-ARCH-CR-013, TNSI-ARCH-EVAL-B, TNSI-ARCH-EVAL-B-corrige, TNSI-ARCH-EX-004 | preuve etablie par OFFICIAL_ROW_EVIDENCE | NO |
| TSPE | Développement de u  v , formules de polarisation. | MISSING | TRUE_CONTENT_GAP | le chapitre traitait le produit scalaire sans developper la norme d'une somme ni enoncer les formules de polarisation | TSPE-GEOESPACE-CR-012, TSPE-SUITLIM-EX-033 | cours redige : developpement de la norme d'une somme et d'une difference, les deux formules de polarisation et leurs dem | YES |
| TSPE | Simulation d’une marche aléatoire. | MISSING | FALSE_MISSING_TOOLING | NORMATIVITY_MISCLASSIFIED : le BO nomme un exemple d'algorithme, il ne l'impose pas ; l'atomisation en avait fait une obligation | TSPE-CONCLGN-ALG-018, TSPE-PROBA-ALG-017 | normativite corrigee ; l'attendu ne compte plus au denominateur des obligations | NO |
| TSPE | Simulation de la planche de Galton. | MISSING | FALSE_MISSING_TOOLING | NORMATIVITY_MISCLASSIFIED : le BO nomme un exemple d'algorithme, il ne l'impose pas ; l'atomisation en avait fait une obligation | TSPE-PROBA-ALG-017 | normativite corrigee ; l'attendu ne compte plus au denominateur des obligations | NO |

## Les anciens « partiels »

| Manuel | Attendu officiel | Ancien verdict | Verdict apres contre-expertise | Cause | Preuve existante | Modification | Contenu ecrit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1NSI | Indexation de tables | PARTIAL | FALSE_PARTIAL_TOOLING | la ligne du tableau officiel n'etait pas conservee : le contenu et les capacites qui le realisent etaient mesures separement | 1NSI-TAB-AM-EXTRAIT, 1NSI-TAB-COURS-C1, 1NSI-TAB-EVAL-A, 1NSI-TAB-EVAL-B, 1NSI-TAB-EX-001, 1NSI-TAB-M1 | preuve etablie par OFFICIAL_ROW_EVIDENCE | NO |
| 1SPE | Calcul du terme général d’une suite arithmétique, d’une suite géométrique. | PARTIAL | FALSE_PARTIAL_TOOLING | l'attendu n'etait rattache a aucun atome, et le rapprochement par contenu ne concluait pas | 1SPE-SUITES-CO-001, 1SPE-SUITES-CO-002, 1SPE-SUITES-CO-003, 1SPE-SUITES-CO-004, 1SPE-SUITES-CO-005, 1SPE-SUITES-CO-006 | preuve etablie par CONTENT_MATCH | NO |
| 1SPE | Itérer sur les éléments d’une liste. | PARTIAL | FALSE_PARTIAL_TOOLING | la recherche etait bornee a une portee de theme, et s'arretait avant le reste du manuel -- une page transversale ou un autre chapitre | 1SPE-TRANSVERSAL-LOGIQUE_RAISONNEMENT, 1SPE-TRANSVERSAL-MEMO_PYTHON | preuve etablie par CONTENT_MATCH_MANUAL_WIDE | NO |
| 1SPE | Manipuler des éléments d’une liste (ajouter, supprimer, etc.) et leurs indices. | PARTIAL | FALSE_PARTIAL_TOOLING | la recherche etait bornee a une portee de theme, et s'arretait avant le reste du manuel -- une page transversale ou un autre chapitre | 1SPE-TRANSVERSAL-MEMO_PYTHON | preuve etablie par CONTENT_MATCH_MANUAL_WIDE | NO |
| 1SPE | Fonction dérivée de la fonction carrée, de la fonction inverse. | PARTIAL | FALSE_PARTIAL_TOOLING | l'attendu n'etait rattache a aucun atome, et le rapprochement par contenu ne concluait pas | 1SPE-DERGLOBAL-CO-002, 1SPE-DERGLOBAL-CO-044, 1SPE-DERGLOBAL-CO-051, 1SPE-DERGLOBAL-COURS-C1, 1SPE-DERGLOBAL-COURS-C2, 1SPE-DERGLOBAL-COURS-C3 | preuve etablie par CONTENT_MATCH | NO |
| 1SPE | Fonction dérivée d’un produit. | PARTIAL | FALSE_PARTIAL_TOOLING | l'attendu n'etait rattache a aucun atome, et le rapprochement par contenu ne concluait pas | 1SPE-DERGLOBAL-ALG-015, 1SPE-DERGLOBAL-CO-011, 1SPE-DERGLOBAL-CO-019, 1SPE-DERGLOBAL-CO-054, 1SPE-DERGLOBAL-COURS-C2, 1SPE-DERGLOBAL-COURS-C5 | preuve etablie par CONTENT_MATCH | NO |
| 1SPE | Équation de la tangente en un point à une courbe représentative. | PARTIAL | FALSE_PARTIAL_TOOLING | la demonstration est redigee dans le chapitre voisin, celui de la derivation locale, que la recherche n'a pas atteint | 1SPE-DERGLOBAL-ALG-015, 1SPE-DERGLOBAL-COURS-C1, 1SPE-DERGLOBAL-COURS-C3, 1SPE-DERGLOBAL-COURS-C4, 1SPE-DERGLOBAL-EV-A, 1SPE-DERGLOBAL-EV-A-corrige | revue contradictoire declaree ; verdict rendu a la lecture de l'objet : FALSE_PARTIAL_TOOLING | NO |
| 1SPE | La fonction racine carrée n’est pas dérivable en 0. | PARTIAL | FALSE_PARTIAL_TOOLING | la demonstration est redigee dans un bloc de contre-exemple, que le detecteur de preuve ne reconnaissait pas | 1SPE-DERGLOBAL-ALG-015, 1SPE-DERGLOBAL-CO-002, 1SPE-DERGLOBAL-COURS-C1, 1SPE-DERGLOBAL-COURS-C3, 1SPE-DERGLOBAL-COURS-C4, 1SPE-DERGLOBAL-ME-001 | revue contradictoire declaree ; verdict rendu a la lecture de l'objet : FALSE_PARTIAL_TOOLING | NO |
| 1SPE | Enroulement de la droite sur le cercle trigonométrique. Image d’un nombre réel. | PARTIAL | FALSE_PARTIAL_TOOLING | l'attendu n'etait rattache a aucun atome, et le rapprochement par contenu ne concluait pas | 1SPE-TRIGO-CR-011, 1SPE-TRIGO-EV-A, 1SPE-TRIGO-EV-A-corrige, 1SPE-TRIGO-EV-B, 1SPE-TRIGO-EV-B-corrige, 1SPE-TRIGO-ME-004 | preuve etablie par CONTENT_MATCH | NO |
| 1SPE | Exploiter les variations d’une fonction pour établir une inégalité. Étudier la position re | PARTIAL | FALSE_PARTIAL_TOOLING | l'attendu n'etait rattache a aucun atome, et le rapprochement par contenu ne concluait pas | 1SPE-DERGLOBAL-COURS-C5 | preuve etablie par CONTENT_MATCH | NO |
| 1SPE | Calculer un taux d’évolution réciproque. | PARTIAL | TRUE_PARTIAL_PEDAGOGICAL | automatisme travaille dans un seul chapitre, ce que le programme exclut | 1SPE-EXPO-CO-052, 1SPE-EXPO-EX-052, 1SPE-SUITES-CO-052, 1SPE-SUITES-EX-052, 1SPE-TRANSVERSAL-STATISTIQUES_AUTOMATISMES | reinvestissement ecrit dans un autre chapitre, avec son corrige | YES |
| 1SPE | Calculer le taux d’évolution équivalent à plusieurs évolutions successives. | PARTIAL | TRUE_PARTIAL_PEDAGOGICAL | automatisme travaille dans un seul chapitre, ce que le programme exclut | 1SPE-EXPO-CO-051, 1SPE-EXPO-EX-051, 1SPE-SECDEG-CO-103, 1SPE-SECDEG-EX-103, 1SPE-SUITES-CO-034, 1SPE-SUITES-COURS-00 | reinvestissement ecrit dans un autre chapitre, avec son corrige | YES |
| 1SPE | Calculer et interpréter des indicateurs statistiques pour une série statistique. | PARTIAL | TRUE_PARTIAL_PEDAGOGICAL | automatisme travaille dans un seul chapitre, ce que le programme exclut | 1SPE-PROBCOND-EX-051, 1SPE-TRANSVERSAL-STATISTIQUES_AUTOMATISMES, 1SPE-VARALEA-CO-055, 1SPE-VARALEA-EX-055 | reinvestissement ecrit dans un autre chapitre, avec son corrige | YES |
| 1SPE | formuler une implication, une équivalence logique, et à les mobiliser dans un raisonnement | PARTIAL | FALSE_PARTIAL_TOOLING | la recherche etait bornee a une portee de theme, et s'arretait avant le reste du manuel -- une page transversale ou un autre chapitre | 1SPE-TRANSVERSAL-LOGIQUE_RAISONNEMENT | preuve etablie par CONTENT_MATCH_MANUAL_WIDE | NO |
| 1SPE | lire et écrire des propositions contenant les connecteurs logiques « et », « ou » ; | PARTIAL | FALSE_PARTIAL_TOOLING | la recherche etait bornee a une portee de theme, et s'arretait avant le reste du manuel -- une page transversale ou un autre chapitre | 1SPE-TRANSVERSAL-LOGIQUE_RAISONNEMENT | preuve etablie par CONTENT_MATCH_MANUAL_WIDE | NO |
| 1SPE | utiliser les quantificateurs (les symboles ∀ et ∃ ne sont pas exigibles) et repérer les qu | PARTIAL | FALSE_PARTIAL_TOOLING | la recherche etait bornee a une portee de theme, et s'arretait avant le reste du manuel -- une page transversale ou un autre chapitre | 1SPE-PRODSCAL-COURS-C5, 1SPE-SUITES-CO-048, 1SPE-TRANSVERSAL-LOGIQUE_RAISONNEMENT | preuve etablie par CONTENT_MATCH_MANUAL_WIDE | NO |
| 1SPE | formuler la réciproque d'une implication, la contraposée ; | PARTIAL | FALSE_PARTIAL_TOOLING | la recherche etait bornee a une portee de theme, et s'arretait avant le reste du manuel -- une page transversale ou un autre chapitre | 1SPE-TRANSVERSAL-LOGIQUE_RAISONNEMENT | preuve etablie par CONTENT_MATCH_MANUAL_WIDE | NO |
| TCOMPL | Interpréter une intégrale, une valeur moyenne dans un contexte issu d’une autre discipline | PARTIAL | FALSE_PARTIAL_TOOLING | meme cause | TCOMPL-AIR-CR-012, TCOMPL-AIR-EX-006 | revue contradictoire declaree ; verdict rendu a la lecture de l'objet : FALSE_PARTIAL_TOOLING | NO |
| TCOMPL | Présentation de l’intégrale des fonctions continues de signe quelconque. | PARTIAL | FALSE_PARTIAL_TOOLING | le cours de calcul integral n'a pas ete atteint par la recherche | TCOMPL-AIR-CR-012, TCOMPL-AIR-ME-001, TCOMPL-CALCULS-AIRES-QCM | revue contradictoire declaree ; verdict rendu a la lecture de l'objet : FALSE_PARTIAL_TOOLING | NO |
| TCOMPL | Équation différentielle y’ = a y + b, où a et b sont des réels ; allure des courbes. | PARTIAL | FALSE_PARTIAL_TOOLING | le cours est dans le theme des modeles d'evolution | TCOMPL-ME-ALG-015, TCOMPL-ME-CR-012, TCOMPL-MODELES-EVOLUTION-QCM | revue contradictoire declaree ; verdict rendu a la lecture de l'objet : FALSE_PARTIAL_TOOLING | NO |
| TCOMPL | Dans le cadre de la résolution de problème, utiliser l’espérance des lois précédentes. | PARTIAL | FALSE_PARTIAL_TOOLING | l'attendu n'etait rattache a aucun atome, et le rapprochement par contenu ne concluait pas | TCOMPL-ATT-CR-010 | preuve etablie par CONTENT_MATCH | NO |
| TCOMPL | Minimum d’une fonction trinôme. | PARTIAL | FALSE_PARTIAL_TOOLING | meme cause | TCOMPL-MF-CR-010, TCOMPL-MF-ME-001 | revue contradictoire declaree ; verdict rendu a la lecture de l'objet : FALSE_PARTIAL_TOOLING | NO |
| TCOMPL | Étude de fonction. | PARTIAL | FALSE_PARTIAL_TOOLING | contenu associe a un theme d'etude, enseigne dans le theme voisin des modeles definis par une fonction | TCOMPL-CORR-CO-010, TCOMPL-MF-CR-010, TCOMPL-MF-ME-001, TCOMPL-MF-ME-002, TCOMPL-MF-ME-005 | revue contradictoire declaree ; verdict rendu a la lecture de l'objet : FALSE_PARTIAL_TOOLING | NO |
| TCOMPL | Fonctions de référence. | PARTIAL | FALSE_PARTIAL_TOOLING | meme cause : contenu associe enseigne dans un autre theme | TCOMPL-MF-CR-010, TCOMPL-MF-ME-003 | revue contradictoire declaree ; verdict rendu a la lecture de l'objet : FALSE_PARTIAL_TOOLING | NO |
| TCOMPL | Lois uniformes discrètes et continues sur [0,1]. | PARTIAL | FALSE_PARTIAL_TOOLING | l'attendu n'avait aucun parent etabli : la disposition a tranche le rattachement | TCOMPL-ECH-CO-037, TCOMPL-ECH-CO-038, TCOMPL-ECH-CR-013, TCOMPL-ECH-EV-B, TCOMPL-ECH-EV-B-corrige, TCOMPL-ECH-EX-037 | preuve etablie par DECLARED_CAPACITY | NO |
| TCOMPL | mobiliser un contre-exemple pour montrer qu’une proposition est fausse ; | PARTIAL | FALSE_PARTIAL_TOOLING | la recherche etait bornee a une portee de theme, et s'arretait avant le reste du manuel -- une page transversale ou un autre chapitre | TCOMPL-TRANSVERSAL-LOGIQUE_RAISONNEMENT | preuve etablie par CONTENT_MATCH_MANUAL_WIDE | NO |
| TCOMPL | formuler la négation de propositions simples (sans implication ni quantificateurs) ; | PARTIAL | FALSE_PARTIAL_TOOLING | la recherche etait bornee a une portee de theme, et s'arretait avant le reste du manuel -- une page transversale ou un autre chapitre | TCOMPL-TRANSVERSAL-LOGIQUE_RAISONNEMENT | preuve etablie par CONTENT_MATCH_MANUAL_WIDE | NO |
| TCOMPL | formuler la réciproque d’une implication ; | PARTIAL | FALSE_PARTIAL_TOOLING | la recherche etait bornee a une portee de theme, et s'arretait avant le reste du manuel -- une page transversale ou un autre chapitre | TCOMPL-TRANSVERSAL-LOGIQUE_RAISONNEMENT | preuve etablie par CONTENT_MATCH_MANUAL_WIDE | NO |
| TEXPERTES | Forme trigonométrique. | PARTIAL | FALSE_PARTIAL_TOOLING | le cours s'intitule « forme exponentielle » et traite la forme trigonometrique dont elle derive | TEXP-CAG-ME-004, TEXP-CTP-CR-010 | revue contradictoire declaree ; verdict rendu a la lecture de l'objet : FALSE_PARTIAL_TOOLING | NO |
| TNSI | Recherche textuelle. | PARTIAL | FALSE_PARTIAL_TOOLING | la ligne du tableau officiel n'etait pas conservee : le contenu et les capacites qui le realisent etaient mesures separement | TNSI-ALGO-CO-010, TNSI-ALGO-CR-016, TNSI-ALGO-EVAL-B, TNSI-ALGO-EVAL-B-corrige, TNSI-ALGO-EX-010, TNSI-ALGORITHMIQUE-QCM | preuve etablie par OFFICIAL_ROW_EVIDENCE | NO |
| TNSI | Récursivité. | PARTIAL | FALSE_PARTIAL_TOOLING | la ligne du tableau officiel n'etait pas conservee : le contenu et les capacites qui le realisent etaient mesures separement | TNSI-LANG-CR-011, TNSI-LANG-EX-001, TNSI-LANGAGES-ET-PROGRAMMATION-QCM | preuve etablie par OFFICIAL_ROW_EVIDENCE | NO |
| TNSI | Notion de programme en tant que donnée. | PARTIAL | FALSE_PARTIAL_TOOLING | la ligne du tableau officiel n'etait pas conservee : le contenu et les capacites qui le realisent etaient mesures separement | TNSI-LANG-CO-005, TNSI-LANG-CO-006, TNSI-LANG-CR-010, TNSI-LANG-EVAL-A, TNSI-LANG-EVAL-A-corrige, TNSI-LANG-EVAL-B | preuve etablie par OFFICIAL_ROW_EVIDENCE | NO |
| TNSI | Gestion des bugs. | PARTIAL | FALSE_PARTIAL_TOOLING | la ligne du tableau officiel n'etait pas conservee : le contenu et les capacites qui le realisent etaient mesures separement | TNSI-ECRIT-S3-EX3, TNSI-LANG-AM-EXTRAIT, TNSI-LANG-CO-004, TNSI-LANG-CO-008, TNSI-LANG-CR-014, TNSI-LANG-EVAL-B | preuve etablie par OFFICIAL_ROW_EVIDENCE | NO |
| TNSI | Dictionnaires, index et clé. | PARTIAL | FALSE_PARTIAL_TOOLING | la ligne du tableau officiel n'etait pas conservee : le contenu et les capacites qui le realisent etaient mesures separement | TNSI-ECRIT-S2-EX1, TNSI-PRATIQUE-P6, TNSI-STRUCT-AM-EXTRAIT, TNSI-STRUCT-CO-006, TNSI-STRUCT-CR-012, TNSI-STRUCT-EVAL-A | preuve etablie par OFFICIAL_ROW_EVIDENCE | NO |
| TSPE | Générer une liste (en extension, par ajouts successifs ou en compréhension). | PARTIAL | FALSE_PARTIAL_TOOLING | la recherche etait bornee a une portee de theme, et s'arretait avant le reste du manuel -- une page transversale ou un autre chapitre | TSPE-TRANSVERSAL-MEMO_PYTHON | preuve etablie par CONTENT_MATCH_MANUAL_WIDE | NO |
| TSPE | Itérer sur les éléments d’une liste. | PARTIAL | FALSE_PARTIAL_TOOLING | la recherche etait bornee a une portee de theme, et s'arretait avant le reste du manuel -- une page transversale ou un autre chapitre | TSPE-COMBI-ALG-015, TSPE-COMBI-CR-010, TSPE-COMBI-EV-B-corrige, TSPE-COMBINATOIRE-QCM, TSPE-TRANSVERSAL-LOGIQUE_RAISONNEMENT, TSPE-TRANSVERSAL-MEMO_PYTHON | preuve etablie par CONTENT_MATCH_MANUAL_WIDE | NO |
| TSPE | Manipuler des éléments d’une liste (ajouter, supprimer…) et leurs indices. | PARTIAL | FALSE_PARTIAL_TOOLING | la recherche etait bornee a une portee de theme, et s'arretait avant le reste du manuel -- une page transversale ou un autre chapitre | TSPE-TRANSVERSAL-MEMO_PYTHON | preuve etablie par CONTENT_MATCH_MANUAL_WIDE | NO |
| TSPE | Primitives des fonctions de référence : x ↦ xn pour n ∈ ℤ, x  , exponentielle, x sinus, c | PARTIAL | FALSE_PARTIAL_TOOLING | le cours dedie n'a pas ete atteint par la recherche | TSPE-PRIMEQ-CR-011, TSPE-TRIGONOMETRIE-QCM | revue contradictoire declaree ; verdict rendu a la lecture de l'objet : FALSE_PARTIAL_TOOLING | NO |
| TSPE | Appliquer l’inégalité de Bienaymé-Tchebychev pour définir une taille d’échantillon, en fon | PARTIAL | FALSE_PARTIAL_TOOLING | le cours dedie n'etait pas rattache a cet attendu | TSPE-PROBA-CO-009, TSPE-PROBA-EV-B, TSPE-PROBA-EV-B-corrige, TSPE-PROBA-EX-009, TSPE-PROBABILITES-QCM | revue contradictoire declaree ; verdict rendu a la lecture de l'objet : FALSE_PARTIAL_TOOLING | NO |
| TSPE | lire et écrire des propositions contenant les connecteurs « et », « ou » ; | PARTIAL | FALSE_PARTIAL_TOOLING | la recherche etait bornee a une portee de theme, et s'arretait avant le reste du manuel -- une page transversale ou un autre chapitre | TSPE-LIMFCT-CR-010, TSPE-TRANSVERSAL-LOGIQUE_RAISONNEMENT | preuve etablie par CONTENT_MATCH_MANUAL_WIDE | NO |
| TSPE | lire et écrire des propositions contenant une quantification universelle ou existentielle  | PARTIAL | FALSE_PARTIAL_TOOLING | la recherche etait bornee a une portee de theme, et s'arretait avant le reste du manuel -- une page transversale ou un autre chapitre | TSPE-TRANSVERSAL-LOGIQUE_RAISONNEMENT | preuve etablie par CONTENT_MATCH_MANUAL_WIDE | NO |
| TSPE | formuler la réciproque d’une implication, ou sa contraposée ; | PARTIAL | FALSE_PARTIAL_TOOLING | la recherche etait bornee a une portee de theme, et s'arretait avant le reste du manuel -- une page transversale ou un autre chapitre | TSPE-TRANSVERSAL-LOGIQUE_RAISONNEMENT | preuve etablie par CONTENT_MATCH_MANUAL_WIDE | NO |
| TSPE | formuler une implication, une équivalence logique, et à les mobiliser dans un raisonnement | PARTIAL | FALSE_PARTIAL_TOOLING | la recherche etait bornee a une portee de theme, et s'arretait avant le reste du manuel -- une page transversale ou un autre chapitre | TSPE-TRANSVERSAL-LOGIQUE_RAISONNEMENT | preuve etablie par CONTENT_MATCH_MANUAL_WIDE | NO |
| TSPE | reconnaître ce qu’est une proposition mathématique, à utiliser des variables pour écrire d | PARTIAL | FALSE_PARTIAL_TOOLING | la recherche etait bornee a une portee de theme, et s'arretait avant le reste du manuel -- une page transversale ou un autre chapitre | TSPE-TRANSVERSAL-LOGIQUE_RAISONNEMENT | preuve etablie par CONTENT_MATCH_MANUAL_WIDE | NO |
| TSPE | raisonner par disjonctions des cas, par l’absurde, par contraposée ; | PARTIAL | FALSE_PARTIAL_TOOLING | la recherche etait bornee a une portee de theme, et s'arretait avant le reste du manuel -- une page transversale ou un autre chapitre | TSPE-TRANSVERSAL-LOGIQUE_RAISONNEMENT | preuve etablie par CONTENT_MATCH_MANUAL_WIDE | NO |

## Les anciens « indecidables »

| Manuel | Attendu officiel | Ancien verdict | Verdict apres contre-expertise | Cause | Preuve existante | Modification | Contenu ecrit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1SPE | Calcul de 1 + 𝑞 + … + 𝑞𝑛. | UNDECIDABLE_BY_CONTENT_MATCH | FALSE_MISSING_TOOLING | meme cause : un libelle sans mot distinctif | 1SPE-SUITES-CR-013 | revue contradictoire declaree ; verdict rendu a la lecture de l'objet : FALSE_MISSING_TOOLING | NO |
| 1SPE | Calcul de 1 + 2 + … + 𝑛. | UNDECIDABLE_BY_CONTENT_MATCH | FALSE_MISSING_TOOLING | le libelle officiel se reduit a des symboles mathematiques : aucun mot distinctif, donc aucune recherche possible | 1SPE-SUITES-CR-013 | revue contradictoire declaree ; verdict rendu a la lecture de l'objet : FALSE_MISSING_TOOLING | NO |
| 1SPE | Calcul de cos , sin , cos , sin . 4 4 3 3 | UNDECIDABLE_BY_CONTENT_MATCH | TRUE_CONTENT_GAP | le libelle officiel a perdu ses fractions a l'extraction (« Calcul de cos , sin , cos , sin . 4 4 3 3 ») : aucune recherche n'etait possible. La lectu | 1SPE-TRIGO-ALG-015, 1SPE-TRIGO-CO-011, 1SPE-TRIGO-CO-012, 1SPE-TRIGO-CO-013, 1SPE-TRIGO-CO-014, 1SPE-TRIGO-CO-015 | demonstration complete redigee : cosinus et sinus de pi/4, pi/3 et pi/6, avec hypotheses et chaine logique, plus bloc VE | YES |

## Contenu ecrit, par cause

Ce qui a ete ECRIT, et rien d'autre : les reparations d'outillage n'y
figurent pas. Chaque fichier releve d'une seule cause principale.

| Fichier | Manuel | Cause | Attendu | Verdict |
| --- | --- | --- | --- | --- |
| `Mathematiques/manuel-maths/chapitres/TCOMPL-INEGALITES/cours/10_C0_dispersion.tex` | TCOMPL | CONTENT_CREATED_FOR_TRUE_MISSING | Statistique descriptive : caractéristiques de dispersion (médiane, qua | TRUE_CONTENT_GAP |
| `Mathematiques/manuel-maths/chapitres/TSPE-GEOMETRIE-ESPACE/cours/12_C7_produit_scalaire.tex` | TSPE | CONTENT_CREATED_FOR_TRUE_MISSING | Développement de u  v , formules de polarisation. | TRUE_CONTENT_GAP |
| `Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-051.tex` | 1SPE | CONTENT_CREATED_FOR_TRUE_PARTIAL_PEDAGOGICAL | Calculer un taux d’évolution réciproque. | TRUE_PARTIAL_PEDAGOGICAL |
| `Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-051.tex` | 1SPE | CONTENT_CREATED_FOR_TRUE_PARTIAL_PEDAGOGICAL | Calculer un taux d’évolution réciproque. | TRUE_PARTIAL_PEDAGOGICAL |
| `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-052.tex` | 1SPE | CONTENT_CREATED_FOR_TRUE_PARTIAL_PEDAGOGICAL | Calculer le taux d’évolution équivalent à plusieurs évolutions success | TRUE_PARTIAL_PEDAGOGICAL |
| `Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-052.tex` | 1SPE | CONTENT_CREATED_FOR_TRUE_PARTIAL_PEDAGOGICAL | Calculer le taux d’évolution équivalent à plusieurs évolutions success | TRUE_PARTIAL_PEDAGOGICAL |
| `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-055.tex` | 1SPE | CONTENT_CREATED_FOR_TRUE_PARTIAL_PEDAGOGICAL | Calculer et interpréter des indicateurs statistiques pour une série st | TRUE_PARTIAL_PEDAGOGICAL |
| `Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-055.tex` | 1SPE | CONTENT_CREATED_FOR_TRUE_PARTIAL_PEDAGOGICAL | Calculer et interpréter des indicateurs statistiques pour une série st | TRUE_PARTIAL_PEDAGOGICAL |
| `Mathematiques/manuel-maths/chapitres/1SPE-TRIGONOMETRIE/cours/11_C2_cosinus_sinus.tex` | 1SPE | CONTENT_CREATED_AFTER_UNDECIDABLE_REVIEW | Calcul de cos , sin , cos , sin . 4 4 3 3 | TRUE_CONTENT_GAP |

## CONTENT_CREATED_FOR_NEXUS_QUALITY_ENRICHMENT

Ecrit aussi, mais pour une autre raison : le programme NOMME ces
exemples d'algorithme sans les imposer. Ils ne comblent aucun manque
obligatoire et ne comptent a aucun denominateur.

| Fichier | Fondement | Norme |
| --- | --- | --- |
| `Mathematiques/manuel-maths/chapitres/TSPE-PROBABILITES/cours/17_ALG_planche_de_galton.tex` | Exemple d'algorithme cite par le programme, non impose | NEXUS_ALGORITHMIC_QUALITY_STANDARD |
| `Mathematiques/manuel-maths/chapitres/TSPE-PROBABILITES/cours/18_ALG_marche_aleatoire.tex` | Exemple d'algorithme cite par le programme, non impose | NEXUS_ALGORITHMIC_QUALITY_STANDARD |
