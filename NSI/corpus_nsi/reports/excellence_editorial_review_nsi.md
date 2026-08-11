# Revue d’excellence éditoriale et pédagogique — Corpus NSI

## 1. VERDICT GLOBAL

Verdict : ENRICHISSEMENT-REQUIS

Comptes :

| Sévérité | Nombre |
|---|---:|
| P0 | 1 |
| P1 | 12 |
| P2 | 5 |
| P3 | 0 |

Jugement d’ensemble en 5 phrases :

1. Le corpus est vaste, formellement structuré et souvent exact, mais 199 documents sur 401 restent INDIGENTS au regard de l’activité intellectuelle réellement proposée.
2. La dette la plus coûteuse est transversale : des banques alpha/beta/gamma répètent les mêmes données et des corrigés génériques là où l’élève devrait tracer, écrire, analyser, déboguer et transférer.
3. Les documents satellites P06+/T06+ — barèmes, remédiations, traces et versions aménagées — ont fréquemment la bonne rubrique sans la substance propre à leur fonction.
4. Le corpus possède néanmoins des modèles internes solides, notamment les compléments P02/P03, T01/T03/T05 et les TP ou traces T08/T18, qui prouvent qu’un standard riche est déjà atteignable dans cette architecture.
5. La priorité n’est donc pas d’ajouter des fichiers, mais de reconstruire des chaînes cohérentes cours–entraînement–évaluation–correction autour de tâches nouvelles, de raisonnements visibles et d’aides réellement graduées.

Répartition des 401 verdicts de grille : 62 RICHE, 140 CORRECT-MAIS-PERFECTIBLE, 199 INDIGENT.

## 2. TABLEAU DES CONSTATS

| ID | Séquence | Document | Sévérité | Section du référentiel | Fichier:lignes | Extrait | Attendu vs Trouvé | Prescription actionnable | Statut |
|---|---|---|---|---|---|---|---|---|---|
| RVW-001 | T10 | Cours et évaluations SQL | P0 | Cours/évaluation — cohérence consigne, méthode et résultat | `03_progressions/supports/terminale/T10/T10_evaluation_sql_select_where_join.md:39-51` | « filtrer note >= 15 » → « JOIN -> Ada 17 » ; « joindre Eleve.id_eleve = Note.id_eleve » → « UPDATE id_note=10 -> Ada 18 » | Attendu : chaque question conduit à une requête et à un résultat du même type. Trouvé : filtrage, jointure, mise à jour et suppression sont décalés entre consignes et réponses ; l’élève peut apprendre une association fausse et le sujet n’est pas corrigeable de façon fiable. | Réécrire les quatre couples consigne/correction : fournir le schéma, exiger la requête SQL complète, donner la table résultat exacte, puis isoler SELECT/WHERE, JOIN/ON, UPDATE/WHERE et DELETE/WHERE dans quatre tâches cohérentes ; faire relire le triptyque cours–évaluation–corrigé sur une base de test unique. | CONFIRMÉ |
| RVW-002 | P08 | Deux évaluations | P1 | Évaluation — spécialisation et absence de doublon déguisé | `03_progressions/supports/premiere/P08/P08_evaluation_html_css_dom.md:26-53` ; `03_progressions/supports/premiere/P08/P08_evaluation_http_get_post_formulaires.md:26-53` | « P08 - Évaluation - HTML, CSS, DOM, HTTP et formulaires » ; « repérer header main form label input. » ; « POST sans HTTPS ne chiffre pas. » | Attendu : un sujet HTML/CSS/DOM et un sujet HTTP/formulaires mobilisant des activités distinctes. Trouvé : deux sujets quasi identiques, centrés sur le même formulaire et les mêmes réponses. | Réserver le premier à l’arbre HTML, aux sélecteurs et à un gestionnaire DOM ; réserver le second à la construction d’URL, au corps POST, à HTTPS et au classement des données selon leur confidentialité ; employer deux contextes et deux barèmes propres. | CONFIRMÉ |
| RVW-003 | P06–P14, T06–T19 | TD alpha–theta | P1 | TD — progression réelle et zéro doublon déguisé | `03_progressions/supports/premiere/P06/P06_TD_tables_recherche_tri_fusion.md:25-86` | « Socle : exercices 1 et 2. » ; « Approfondissement : exercices 7 et 8. » ; « jeu_exercice=alpha » | Attendu : données, verbes et degré de guidage évoluent du socle à l’approfondissement. Trouvé : huit variantes cycliques d’un noyau de quatre tâches ; 26 TD portent explicitement `jeu_exercice=alpha`. | Recomposer chaque TD en six tâches non redondantes : lecture guidée, trace, production, analyse, débogage, transfert ; employer au moins trois jeux de données et réserver l’approfondissement à une modification de spécification ou une justification. | CONFIRMÉ |
| RVW-004 | P00–P14, T00–T19 | Corrigés intégrés aux TD | P1 | Corrigé — raisonnement disciplinaire | `03_progressions/supports/terminale/T12/T12_TD_routage_rip_ospf.md:92-110` | « pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)` » | Attendu : table de routage, métriques, recalcul après panne et règle de décision. Trouvé : pseudo-code sans variables du problème, invariant non formulé et complexité plaquée ; ce patron apparaît dans 36 fichiers. | Supprimer les quatre lignes mécaniques par exercice ; écrire la trace réellement attendue avec données intermédiaires, décision, vérification et erreur typique propre à la notion ; ne mentionner invariant ou complexité que lorsqu’ils sont définis et utilisés. | CONFIRMÉ |
| RVW-005 | P00–P05, T00–T05 | Cours principaux | P1 | Cours — définitions précises et accessibles | `03_progressions/supports/terminale/T02/T02_cours_classes_objets.md:53-58` | « Définition D1 : classe est utilisé dans Programmation orientée objet avec une donnée, une règle et un contrôle. » | Attendu : distinguer classe, instance, attribut, méthode et état sur du code. Trouvé : phrases grammaticalement fautives et circulaires, interchangeables entre notions, qui ne définissent rien. | Pour chaque notion, écrire un triplet « formulation élève / formalisme ou code / exemple et non-exemple » ; ajouter une question flash de discrimination et une trace d’état lorsque pertinent. | CONFIRMÉ |
| RVW-006 | P02, P04 et compléments analogues | TD complémentaires | P1 | TD — énoncés autosuffisants | `03_progressions/supports/premiere/P04/P04_td_types_construits_complement.md:250-280` | « Exercice complémentaire de consolidation. » | Attendu : huit tâches distinctes avec donnée, consigne, livrable et difficulté. Trouvé : huit titres remplis par cette phrase identique, sans travail possible pour l’élève. | Supprimer le bloc ou écrire huit énoncés complets : retour de tuple, compréhension, matrice, dictionnaire, parcours, débogage, cas limite et transfert ; donner pour chacun une production observable et un renvoi précis au corrigé. | CONFIRMÉ |
| RVW-007 | T17 et évaluations de même trame | Évaluation programmation dynamique | P1 | Évaluation — activité intellectuelle, graduation et correction | `03_progressions/supports/terminale/T17/T17_evaluation_programmation_dynamique.md:25-59` | « initialiser dp[0]=0 » → « tabulation stocke chaque dp[m] » ; « remplir la table de 1 à 11 » → « sans pièce 1 certains montants impossibles ». | Attendu : définition d’état, relation, table complète, reconstruction et cas impossible sur des questions progressives. Trouvé : quatre injonctions sur la même donnée et des réponses-étiquettes qui ne montrent ni table ni raisonnement. | Fournir une table 0..11 à compléter, séparer définition/initialisation/récurrence/ordre, demander la reconstruction des pièces, puis ajouter un jeu sans pièce 1 ; corriger chaque case ou décision, pas seulement la conclusion. | CONFIRMÉ |
| RVW-008 | P06–P14, T06–T19 | Barèmes | P1 | Barème — critères observables et réponses partielles | `03_progressions/supports/terminale/T17/T17_bareme_programmation_dynamique.md:20-37` | « 8 exercices : 1 point donnée, 1 point méthode, 1 point résultat, 1 point cas limite. » | Attendu : points spécifiques aux étapes réussies et plafonds pour erreurs locales. Trouvé : grille abstraite identique pour des productions différentes ; aucune case `dp`, relation ou initialisation n’est nommée. | Détailler une ligne par question et par observable ; distinguer état, base, relation, trace, résultat et contrôle ; prévoir explicitement demi-crédits, erreurs de propagation et plafonds. | CONFIRMÉ |
| RVW-009 | P06–P14, T06–T19 | Corrigés séparés | P1 | Corrigé — méthode, trace et cas limite | `03_progressions/supports/terminale/T16/T16_corrige_diviser_pour_regner_tri_fusion.md:20-52` | « Réponse attendue : fusion -> [5,12,12,27,38,44]. » ; « Méthode : trier récursivement. » | Attendu : arbre de division, décisions de comparaison, reliquats et invariant de fusion. Trouvé : résultat, nom de méthode et étiquette de cas limite ; les réponses 5–8 répètent 1–4. | Montrer les sous-listes à chaque niveau, la fusion pas à pas et le moment où le reliquat est copié ; commenter une erreur typique et utiliser un second tableau pour le transfert. | CONFIRMÉ |
| RVW-010 | P06–P14, T06–T19 | Remédiations | P1 | Remédiation — diagnostic, autre voie et tâche de réparation | `03_progressions/supports/terminale/T17/T17_remediation_programmation_dynamique.md:20-34` | « Refaire la tâche `définir dp[m] coût minimal` et comparer avec `dp[6]=2 avec 5+1`. » | Attendu : branchement sur l’erreur, représentation alternative, réparation puis test de sortie. Trouvé : liste de diagnostics suivie du même exemple et de la réponse à comparer. | Créer trois parcours : état mal défini, initialisation oubliée, glouton confondu ; employer phrase à compléter, table partielle et contre-exemple `{1,3,4}` pour 6 ; terminer par un problème isomorphe sans aide. | CONFIRMÉ |
| RVW-011 | P06–P14, T06–T19 | Versions aménagées | P1 | Version aménagée — charge cognitive et maintien de l’objectif | `03_progressions/supports/terminale/T17/T17_version_amenagee_programmation_dynamique.md:20-34` | « Choisir la capacité : T-ALGO-04 ou T-ALGO-04. » ; « Compléter le résultat : dp[6]=2 avec 5+1. » ; « Réponse 1 : dp[6]=2 avec 5+1. » | Attendu : segmentation, appuis gradués puis retrait de l’aide sans supprimer le raisonnement. Trouvé : choix factice, recopie et résultat visible ; la réussite ne prouve pas l’apprentissage. | Fournir une table préformatée, la première case résolue, trois indices déclenchables et un lexique ; masquer le résultat final ; conserver une dernière tâche autonome avec le même objectif disciplinaire. | CONFIRMÉ |
| RVW-012 | P06–P14, T06–T19 | Traces écrites | P1 | Trace — essentiel mémorisable et réutilisable | `03_progressions/supports/terminale/T17/T17_trace_programmation_dynamique.md:20-40` | « Vocabulaire : état, récurrence, initialisation, mémoïsation, tabulation. » ; « Étape 1 : définir dp[m] coût minimal. » | Attendu : définition de l’état, base, relation avec domaine, ordre de calcul, exemple tabulé et distinction mémoïsation/tabulation. Trouvé : liste de mots, deux injonctions et résultats isolés. | Réécrire chaque trace en blocs « définition / méthode / exemple complet / pièges / auto-vérification » ; pour T17, inclure la table 0..11 et la condition `p <= m`. | CONFIRMÉ |
| RVW-013 | T19 | Évaluation bac/oral/projet | P1 | Évaluation — consignes autosuffisantes | `03_progressions/supports/terminale/T19/T19_evaluation_bac_pratique_grand_oral_projet.md:26-60` | « résoudre un exercice en temps borné » → « fonction voisins_communs(g,A,B) testée » ; « relier un choix technique à un impact historique » → « source historique vérifiée ». | Attendu : graphe, code, documents historiques et productions observables. Trouvé : injonctions sans matériau de travail et corrigés-étiquettes ; l’élève ne peut ni programmer ni argumenter. | Fournir un graphe et une signature, puis une frise et deux documents courts ; exiger code, tests, paragraphe argumenté et citation précise ; donner un corrigé modèle complet. | CONFIRMÉ |
| RVW-014 | P06–P14, T06–T19 | Différenciation des TD | P2 | Différenciation — étayage et approfondissement | `03_progressions/supports/premiere/P11/P11_TD_parcours_recherche_extremum_moyenne.md:159-162` | « Socle : données annotées. Standard : méthode complète. Expert : transfert avec cible absente. » | Attendu : aides, consignes et productions réellement différentes. Trouvé : trois étiquettes sans support joint, amorce ni défi explicité. | Sous chaque niveau, inscrire les données, l’aide, la consigne et le livrable ; fournir au socle une trace partielle, au standard la production autonome, à l’expert une preuve ou un changement de spécification. | CONFIRMÉ |
| RVW-015 | P06–P14, T06–T19 | Cours | P2 | Cours — situation-problème et activité d’entrée | `03_progressions/supports/terminale/T07/T07_cours_graphes_modelisation_listes_matrices.md:23-51` | « Situation-problème » ; « arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)] » ; « À savoir » ; « Méthodes » | Attendu : contexte qui rend la représentation nécessaire et activité de 5–10 min. Trouvé : donnée brute, sans question motivante ni travail d’entrée. | Ajouter un réseau de circulation ou de messages ; faire identifier sommets/arcs, répondre à une requête, constater la faiblesse de la liste brute et proposer une organisation avant d’institutionnaliser listes et matrices. | CONFIRMÉ |
| RVW-016 | P06–P14, T06–T19 | TP | P2 | TP — déroulé, timing et livrable | `03_progressions/supports/terminale/T17/T17_tp_programmation_dynamique.md:20-47` | « TP exécutable » ; « Produire le livrable : dp[6]=2 avec 5+1. » | Attendu : jalons réalistes, fonctions/signatures, commande de test, fichiers rendus, cas limites et prolongement. Trouvé : assets nommés mais cinq injonctions ; un résultat numérique tient lieu de livrable. | Définir une séance de 55 min, les fonctions et fichiers à rendre, la commande de test, les cas `0` et impossible, puis une extension de reconstruction des pièces ; relier chaque jalon à un observable. | CONFIRMÉ |
| RVW-017 | P07–P14, T06–T19 | Contrats de séquence | P2 | Contrat — exigence de TP | `03_progressions/supports/contracts/T17_contract.yml:29-44` | « tp_attendu: TP papier justifié avec trace, barème et corrigé question par question » | Attendu : une spécification propre à la notion, précisant action, données, livrable et vérification. Trouvé : même phrase dans 22 contrats, insuffisante pour orienter un TP de programmation dynamique, SQL, routage ou graphes. | Spécifier pour chaque contrat une production disciplinaire : signatures ou objets, jeu nominal/limite/invalide, fichiers ou trace attendus, commande ou protocole de vérification et durée cible. | CONFIRMÉ |
| RVW-018 | P00–P05 et T00–T05 | Chaînes cours–TD–évaluation | P2 | Progressivité et transfert | `03_progressions/supports/premiere/P01/P01_cours_conversions_bases.md:59-79` ; `03_progressions/supports/premiere/P01/P01_td_conversions_bases.md:52-72` ; `03_progressions/supports/premiere/P01/P01_evaluation_conversions_bases.md:53-77` | « Donnée étudiée : `13` en base dix. » ; « Énoncé : résoudre décimal vers binaire avec `13` en base dix. » ; « Réponse attendue : `1101₂`. » | Attendu : modèle au cours, entraînement varié au TD, donnée nouvelle en évaluation. Trouvé : mêmes données et mêmes résultats, ce qui mesure surtout la reconnaissance. | Garder un exemple complètement travaillé au cours ; introduire au TD zéro, largeur non multiple de 4 et chiffre interdit ; réserver à l’évaluation un octet inédit et une justification croisée binaire/hexadécimal. | CONFIRMÉ |

## 3. GRILLE DE RICHESSE

| Document | Complétude du plan | Profondeur des contenus | Qualité didactique | Langue/forme | Verdict |
|---|---|---|---|---|---|
| `03_progressions/supports/contracts/P00_contract.yml` | COMPLÈTE | FORTE | FORTE | SOIGNÉE | RICHE |
| `03_progressions/supports/contracts/P01_contract.yml` | COMPLÈTE | FORTE | FORTE | SOIGNÉE | RICHE |
| `03_progressions/supports/contracts/P02_contract.yml` | COMPLÈTE | FORTE | FORTE | SOIGNÉE | RICHE |
| `03_progressions/supports/contracts/P03_contract.yml` | COMPLÈTE | FORTE | FORTE | SOIGNÉE | RICHE |
| `03_progressions/supports/contracts/P04_contract.yml` | COMPLÈTE | FORTE | FORTE | SOIGNÉE | RICHE |
| `03_progressions/supports/contracts/P05_contract.yml` | COMPLÈTE | FORTE | FORTE | SOIGNÉE | RICHE |
| `03_progressions/supports/contracts/P06_contract.yml` | COMPLÈTE | FORTE | FORTE | SOIGNÉE | RICHE |
| `03_progressions/supports/contracts/P07_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/P08_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/P09_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/P10_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/P11_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/P12_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/P13_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/P14_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/T00_contract.yml` | COMPLÈTE | FORTE | FORTE | SOIGNÉE | RICHE |
| `03_progressions/supports/contracts/T01_contract.yml` | COMPLÈTE | FORTE | FORTE | SOIGNÉE | RICHE |
| `03_progressions/supports/contracts/T02_contract.yml` | COMPLÈTE | FORTE | FORTE | SOIGNÉE | RICHE |
| `03_progressions/supports/contracts/T03_contract.yml` | COMPLÈTE | FORTE | FORTE | SOIGNÉE | RICHE |
| `03_progressions/supports/contracts/T04_contract.yml` | COMPLÈTE | FORTE | FORTE | SOIGNÉE | RICHE |
| `03_progressions/supports/contracts/T05_contract.yml` | COMPLÈTE | FORTE | FORTE | SOIGNÉE | RICHE |
| `03_progressions/supports/contracts/T06_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/T07_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/T08_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/T09_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/T10_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/T11_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/T12_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/T13_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/T14_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/T15_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/T16_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/T17_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/T18_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/contracts/T19_contract.yml` | COMPLÈTE MAIS GÉNÉRIQUE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P00/P00_bareme_diagnostic_python.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P00/P00_corrige_diagnostic_python.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P00/P00_cours_diagnostic_python.md` | ÉLEVÉE | FAIBLE | FAIBLE | CORRECTE MAIS TEMPLÉE | INDIGENT |
| `03_progressions/supports/premiere/P00/P00_evaluation_diagnostic_python.md` | ÉLEVÉE | FAIBLE | FAIBLE | CORRECTE MAIS TEMPLÉE | INDIGENT |
| `03_progressions/supports/premiere/P00/P00_remediation_diagnostic_python.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P00/P00_td_diagnostic_python.md` | ÉLEVÉE | FAIBLE | FAIBLE | CORRECTE MAIS TEMPLÉE | INDIGENT |
| `03_progressions/supports/premiere/P00/P00_tp_diagnostic_python.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P00/P00_trace_diagnostic_python.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P00/P00_version_amenagee_diagnostic_python.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P01/P01_bareme_conversions_bases.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P01/P01_corrige_conversions_bases.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P01/P01_cours_conversions_bases.md` | ÉLEVÉE | FAIBLE | FAIBLE | CORRECTE MAIS TEMPLÉE | INDIGENT |
| `03_progressions/supports/premiere/P01/P01_evaluation_conversions_bases.md` | ÉLEVÉE | FAIBLE | FAIBLE | CORRECTE MAIS TEMPLÉE | INDIGENT |
| `03_progressions/supports/premiere/P01/P01_remediation_conversions_bases.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P01/P01_td_conversions_bases.md` | ÉLEVÉE | FAIBLE | FAIBLE | CORRECTE MAIS TEMPLÉE | INDIGENT |
| `03_progressions/supports/premiere/P01/P01_tp_conversions_bases.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P01/P01_trace_conversions_bases.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P01/P01_version_amenagee_conversions_bases.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P02/P02_bareme_complement_booleens.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P02/P02_bareme_tables_verite_booleennes.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P02/P02_corrige_complement_booleens.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P02/P02_corrige_tables_verite_booleennes.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P02/P02_cours_complement_booleens.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P02/P02_cours_tables_verite_booleennes.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P02/P02_evaluation_complement_booleens.md` | ÉLEVÉE | FAIBLE | FAIBLE | CORRECTE MAIS TEMPLÉE | INDIGENT |
| `03_progressions/supports/premiere/P02/P02_evaluation_tables_verite_booleennes.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P02/P02_remediation_complement_booleens.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P02/P02_td_complement_booleens.md` | ÉLEVÉE | FAIBLE | FAIBLE | CORRECTE MAIS TEMPLÉE | INDIGENT |
| `03_progressions/supports/premiere/P02/P02_td_tables_verite_booleennes.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P02/P02_tp_complement_booleens.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P02/P02_tp_tables_verite_booleennes.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P02/P02_trace_complement_booleens.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P02/P02_trace_tables_verite_booleennes.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P02/P02_version_amenagee_complement_booleens.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P03/P03_bareme_conversion_encodages_texte.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P03/P03_bareme_texte_reels.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P03/P03_corrige_conversion_encodages_texte.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P03/P03_corrige_texte_reels.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P03/P03_cours_conversion_encodages_texte.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P03/P03_cours_texte_reels.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P03/P03_evaluation_conversion_encodages_texte.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P03/P03_evaluation_texte_reels.md` | ÉLEVÉE | FAIBLE | FAIBLE | CORRECTE MAIS TEMPLÉE | INDIGENT |
| `03_progressions/supports/premiere/P03/P03_remediation_texte_reels.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P03/P03_td_conversion_encodages_texte.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P03/P03_td_texte_reels.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P03/P03_tp_conversion_encodages_texte.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P03/P03_tp_texte_reels.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P03/P03_trace_conversion_encodages_texte.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P03/P03_trace_texte_reels.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P03/P03_version_amenagee_texte_reels.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P04/P04_bareme_types_construits.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P04/P04_bareme_types_construits_complement.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P04/P04_corrige_types_construits.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P04/P04_corrige_types_construits_complement.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P04/P04_cours_types_construits.md` | ÉLEVÉE | FAIBLE | FAIBLE | CORRECTE MAIS TEMPLÉE | INDIGENT |
| `03_progressions/supports/premiere/P04/P04_cours_types_construits_complement.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P04/P04_evaluation_types_construits.md` | ÉLEVÉE | FAIBLE | FAIBLE | CORRECTE MAIS TEMPLÉE | INDIGENT |
| `03_progressions/supports/premiere/P04/P04_evaluation_types_construits_complement.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P04/P04_remediation_types_construits.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P04/P04_td_types_construits.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P04/P04_td_types_construits_complement.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P04/P04_tp_types_construits.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P04/P04_tp_types_construits_complement.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P04/P04_trace_types_construits.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P04/P04_trace_types_construits_complement.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P04/P04_version_amenagee_types_construits.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P05/P05_bareme_tables_csv.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P05/P05_corrige_tables_csv.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P05/P05_cours_tables_csv.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P05/P05_evaluation_tables_csv.md` | ÉLEVÉE | FAIBLE | FAIBLE | CORRECTE MAIS TEMPLÉE | INDIGENT |
| `03_progressions/supports/premiere/P05/P05_remediation_tables_csv.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P05/P05_td_tables_csv.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P05/P05_tp_tables_csv.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P05/P05_trace_tables_csv.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P05/P05_version_amenagee_tables_csv.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P06/P06_TD_tables_recherche_tri_fusion.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P06/P06_bareme_tables_recherche_tri_fusion.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P06/P06_corrige_tables_recherche_tri_fusion.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P06/P06_cours_tables_recherche_tri_fusion.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P06/P06_evaluation_tables_recherche_tri_fusion.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P06/P06_remediation_tables_recherche_tri_fusion.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P06/P06_tp_tables_recherche_tri_fusion.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P06/P06_trace_tables_recherche_tri_fusion.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P06/P06_version_amenagee_tables_recherche_tri_fusion.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P07/P07_TD_fonctions_tests_specifications.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P07/P07_TP_fonctions_tests_specifications.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P07/P07_bareme_fonctions_tests_specifications.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P07/P07_corrige_fonctions_tests_specifications.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P07/P07_cours_fonctions_tests_specifications.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P07/P07_evaluation_fonctions_tests_specifications.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P07/P07_remediation_fonctions_tests_specifications.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P07/P07_tp_fonctions_tests_specifications.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P07/P07_trace_fonctions_tests_specifications.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P07/P07_version_amenagee_fonctions_tests_specifications.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P08/P08_TD_html_css_dom.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P08/P08_TD_http_get_post_formulaires.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P08/P08_TP_html_css_dom.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P08/P08_TP_http_get_post_formulaires.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P08/P08_bareme_web_http_dom_formulaires.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P08/P08_corrige_web_http_dom_formulaires.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P08/P08_cours_web_http_dom_formulaires.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P08/P08_evaluation_html_css_dom.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P08/P08_evaluation_http_get_post_formulaires.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P08/P08_remediation_web_http_dom_formulaires.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P08/P08_trace_web_http_dom_formulaires.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P08/P08_version_amenagee_web_http_dom_formulaires.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P09/P09_TD_architecture_os_droits.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P09/P09_bareme_architecture_os_droits.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P09/P09_corrige_architecture_os_droits.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P09/P09_cours_architecture_os_droits.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P09/P09_evaluation_architecture_os_droits.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P09/P09_remediation_architecture_os_droits.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P09/P09_tp_architecture_os_droits.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P09/P09_trace_architecture_os_droits.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P09/P09_version_amenagee_architecture_os_droits.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P10/P10_TD_reseaux_protocoles_paquets.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P10/P10_bareme_reseaux_protocoles_paquets.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P10/P10_corrige_reseaux_protocoles_paquets.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P10/P10_cours_reseaux_protocoles_paquets.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P10/P10_evaluation_reseaux_protocoles_paquets.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P10/P10_remediation_reseaux_protocoles_paquets.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P10/P10_tp_reseaux_protocoles_paquets.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P10/P10_trace_reseaux_protocoles_paquets.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P10/P10_version_amenagee_reseaux_protocoles_paquets.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P11/P11_TD_parcours_recherche_extremum_moyenne.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P11/P11_bareme_parcours_recherche_extremum_moyenne.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P11/P11_corrige_parcours_recherche_extremum_moyenne.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P11/P11_cours_parcours_recherche_extremum_moyenne.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P11/P11_evaluation_parcours_recherche_extremum_moyenne.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P11/P11_remediation_parcours_recherche_extremum_moyenne.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P11/P11_tp_parcours_recherche_extremum_moyenne.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P11/P11_trace_parcours_recherche_extremum_moyenne.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P11/P11_version_amenagee_parcours_recherche_extremum_moyenne.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P12/P12_TD_tris_invariants_complexite.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P12/P12_bareme_tris_invariants_complexite.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P12/P12_corrige_tris_invariants_complexite.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P12/P12_cours_tris_invariants_complexite.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P12/P12_evaluation_tris_invariants_complexite.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P12/P12_remediation_tris_invariants_complexite.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P12/P12_tp_tris_invariants_complexite.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P12/P12_trace_tris_invariants_complexite.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P12/P12_version_amenagee_tris_invariants_complexite.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P13/P13_TD_dichotomie_glouton_knn.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P13/P13_bareme_dichotomie_glouton_knn.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P13/P13_corrige_dichotomie_glouton_knn.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P13/P13_cours_dichotomie_glouton_knn.md` | ÉLEVÉE | ÉLEVÉE | ÉLEVÉE | SOIGNÉE | RICHE |
| `03_progressions/supports/premiere/P13/P13_evaluation_dichotomie_glouton_knn.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P13/P13_remediation_dichotomie_glouton_knn.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P13/P13_tp_dichotomie_glouton_knn.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P13/P13_trace_dichotomie_glouton_knn.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P13/P13_version_amenagee_dichotomie_glouton_knn.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P14/P14_TD_synthese_projet_oral.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P14/P14_bareme_synthese_projet_oral.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P14/P14_corrige_synthese_projet_oral.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P14/P14_cours_synthese_projet_oral.md` | ÉLEVÉE | MOYENNE | MOYENNE | CORRECTE | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/premiere/P14/P14_evaluation_synthese_projet_oral.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P14/P14_remediation_synthese_projet_oral.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P14/P14_tp_synthese_projet_oral.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P14/P14_trace_synthese_projet_oral.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| `03_progressions/supports/premiere/P14/P14_version_amenagee_synthese_projet_oral.md` | MOYENNE | FAIBLE | FAIBLE | TÉLÉGRAPHIQUE | INDIGENT |
| 03_progressions/supports/terminale/T00/T00_bareme_diagnostic_tests.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T00/T00_corrige_diagnostic_tests.md | Complet | Moyenne | Moyenne | Inégale | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T00/T00_cours_diagnostic_tests.md | Complet | Moyenne | Moyenne | Inégale | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T00/T00_evaluation_diagnostic_tests.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T00/T00_remediation_diagnostic_tests.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T00/T00_td_diagnostic_tests.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T00/T00_tp_diagnostic_tests.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T00/T00_trace_diagnostic_tests.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T00/T00_version_amenagee_diagnostic_tests.md | Complet | Faible | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T01/T01_bareme_interface_implementation_complement.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T01/T01_bareme_interfaces_structures.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T01/T01_corrige_interface_implementation_complement.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T01/T01_corrige_interfaces_structures.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T01/T01_cours_interface_implementation_complement.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T01/T01_cours_interfaces_structures.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T01/T01_evaluation_interface_implementation_complement.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T01/T01_evaluation_interfaces_structures.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T01/T01_remediation_interfaces_structures.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T01/T01_td_interface_implementation_complement.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T01/T01_td_interfaces_structures.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T01/T01_tp_interface_implementation_complement.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T01/T01_tp_interfaces_structures.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T01/T01_trace_interface_implementation_complement.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T01/T01_trace_interfaces_structures.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T01/T01_version_amenagee_interfaces_structures.md | Complet | Faible | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T02/T02_bareme_classes_objets.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T02/T02_corrige_classes_objets.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T02/T02_cours_classes_objets.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T02/T02_evaluation_classes_objets.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T02/T02_remediation_classes_objets.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T02/T02_td_classes_objets.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T02/T02_tp_classes_objets.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T02/T02_trace_classes_objets.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T02/T02_version_amenagee_classes_objets.md | Complet | Faible | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T03/T03_bareme_piles_files_dictionnaires.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T03/T03_bareme_recherche_liste_dictionnaire.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T03/T03_corrige_piles_files_dictionnaires.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T03/T03_corrige_recherche_liste_dictionnaire.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T03/T03_cours_piles_files_dictionnaires.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T03/T03_cours_recherche_liste_dictionnaire.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T03/T03_evaluation_piles_files_dictionnaires.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T03/T03_evaluation_recherche_liste_dictionnaire.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T03/T03_remediation_piles_files_dictionnaires.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T03/T03_td_piles_files_dictionnaires.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T03/T03_td_recherche_liste_dictionnaire.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T03/T03_tp_piles_files_dictionnaires.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T03/T03_tp_recherche_liste_dictionnaire.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T03/T03_trace_piles_files_dictionnaires.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T03/T03_trace_recherche_liste_dictionnaire.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T03/T03_version_amenagee_piles_files_dictionnaires.md | Complet | Faible | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T04/T04_bareme_recursivite.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T04/T04_corrige_recursivite.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T04/T04_cours_recursivite.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T04/T04_evaluation_recursivite.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T04/T04_remediation_recursivite.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T04/T04_td_recursivite.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T04/T04_tp_recursivite.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T04/T04_trace_recursivite.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T04/T04_version_amenagee_recursivite.md | Complet | Faible | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T05/T05_bareme_arbres_binaires.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T05/T05_bareme_arbres_mesures_parcours_complement.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T05/T05_corrige_arbres_binaires.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T05/T05_corrige_arbres_mesures_parcours_complement.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T05/T05_cours_arbres_binaires.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T05/T05_cours_arbres_mesures_parcours_complement.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T05/T05_evaluation_arbres_binaires.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T05/T05_evaluation_arbres_mesures_parcours_complement.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T05/T05_remediation_arbres_binaires.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T05/T05_td_arbres_binaires.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T05/T05_td_arbres_mesures_parcours_complement.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T05/T05_tp_arbres_binaires.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T05/T05_tp_arbres_mesures_parcours_complement.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T05/T05_trace_arbres_binaires.md | Complet mais templé | Faible | Faible | Inégale | INDIGENT |
| 03_progressions/supports/terminale/T05/T05_trace_arbres_mesures_parcours_complement.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T05/T05_version_amenagee_arbres_binaires.md | Complet | Faible | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T06/T06_TD_arbres_binaires_recherche.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T06/T06_TP_arbres_binaires_recherche.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T06/T06_bareme_arbres_binaires_recherche.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T06/T06_corrige_arbres_binaires_recherche.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T06/T06_cours_arbres_binaires_recherche.md | Partiel | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T06/T06_evaluation_arbres_binaires_recherche.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T06/T06_remediation_arbres_binaires_recherche.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T06/T06_tp_arbres_binaires_recherche.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T06/T06_trace_arbres_binaires_recherche.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T06/T06_version_amenagee_arbres_binaires_recherche.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T07/T07_TD_graphes_modelisation_listes_matrices.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T07/T07_TP_graphes_modelisation_listes_matrices.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T07/T07_bareme_graphes_modelisation_listes_matrices.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T07/T07_corrige_graphes_modelisation_listes_matrices.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T07/T07_cours_graphes_modelisation_listes_matrices.md | Partiel | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T07/T07_evaluation_graphes_modelisation_listes_matrices.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T07/T07_remediation_graphes_modelisation_listes_matrices.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T07/T07_tp_graphes_modelisation_listes_matrices.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T07/T07_trace_graphes_modelisation_listes_matrices.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T07/T07_version_amenagee_graphes_modelisation_listes_matrices.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T08/T08_TD_bfs_dfs_cycles_chemins.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T08/T08_TP_bfs_dfs_cycles_chemins.md | Complet | Forte | Forte | Correcte | RICHE |
| 03_progressions/supports/terminale/T08/T08_bareme_bfs_dfs_cycles_chemins.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T08/T08_corrige_bfs_dfs_cycles_chemins.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T08/T08_cours_bfs_dfs_cycles_chemins.md | Partiel | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T08/T08_evaluation_bfs_dfs_cycles_chemins.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T08/T08_remediation_bfs_dfs_cycles_chemins.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T08/T08_tp_bfs_dfs_cycles_chemins.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T08/T08_trace_bfs_dfs_cycles_chemins.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T08/T08_version_amenagee_bfs_dfs_cycles_chemins.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T09/T09_TD_bases_relationnelles_cles_contraintes.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T09/T09_bareme_bases_relationnelles_cles_contraintes.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T09/T09_corrige_bases_relationnelles_cles_contraintes.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T09/T09_cours_bases_relationnelles_cles_contraintes.md | Partiel | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T09/T09_evaluation_bases_relationnelles_cles_contraintes.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T09/T09_remediation_bases_relationnelles_cles_contraintes.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T09/T09_tp_bases_relationnelles_cles_contraintes.md | Complet | Moyenne | Moyenne | Correcte | CORRECT-MAIS-PERFECTIBLE |
| 03_progressions/supports/terminale/T09/T09_trace_bases_relationnelles_cles_contraintes.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| 03_progressions/supports/terminale/T09/T09_version_amenagee_bases_relationnelles_cles_contraintes.md | Partiel ou templé | Faible | Faible | Correcte | INDIGENT |
| `03_progressions/supports/terminale/T10/T10_TD_sql_insert_update_delete.md` | Plan apparent complet | Très faible, exercices cycliques | Progression de façade, corrigés templés | Lisible, télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T10/T10_TD_sql_select_where_join.md` | Plan apparent complet | Très faible, même micro-base répétée | Peu de variété et pas de transfert | Lisible, télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T10/T10_bareme_sql_select_where_join.md` | Rubriques présentes | Très faible | Critères génériques, pas de réponses partielles | Claire mais abstraite | INDIGENT |
| `03_progressions/supports/terminale/T10/T10_corrige_sql_select_where_join.md` | Couverture TD/TP/évaluation | Très faible | Résultats sans raisonnement SQL | Télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T10/T10_cours_sql_select_where_join.md` | Plan incomplet didactiquement | Très faible | Pas d’activité d’entrée ni d’explication clause par clause | Lisible, style liste | INDIGENT |
| `03_progressions/supports/terminale/T10/T10_evaluation_sql_insert_update_delete.md` | Structure complète | Faible | Questions atomisées sur un cas unique | Lisible, répétitive | INDIGENT |
| `03_progressions/supports/terminale/T10/T10_evaluation_sql_select_where_join.md` | Structure complète | Faible | Peu graduée, pas de transfert | Lisible, répétitive | INDIGENT |
| `03_progressions/supports/terminale/T10/T10_remediation_sql_select_where_join.md` | Rubriques minimales | Très faible | Répète l’activité initiale | Claire mais générique | INDIGENT |
| `03_progressions/supports/terminale/T10/T10_tp_sql_select_where_join.md` | Assets et étapes présents | Moyenne | Exécutable, mais timing et livrable trop vagues | Claire | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/terminale/T10/T10_trace_sql_select_where_join.md` | Rubriques minimales | Très faible | Liste de mots, peu révisable | Télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T10/T10_version_amenagee_sql_select_where_join.md` | Aides/exercice/réponses présents | Très faible | Réponse donnée, étayage non progressif | Claire | INDIGENT |
| `03_progressions/supports/terminale/T11/T11_TD_processus_ordonnancement_interblocage.md` | Plan apparent complet | Très faible | Huit variantes cycliques, pseudo-code générique | Lisible, télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T11/T11_bareme_processus_ordonnancement_interblocage.md` | Rubriques présentes | Très faible | Critères non spécifiques | Claire mais abstraite | INDIGENT |
| `03_progressions/supports/terminale/T11/T11_corrige_processus_ordonnancement_interblocage.md` | Couverture TD/TP/évaluation | Très faible | Résultats sans traces d’états | Télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T11/T11_cours_processus_ordonnancement_interblocage.md` | Plan apparent complet | Faible | Définitions et mécanismes non développés | Lisible, style liste | INDIGENT |
| `03_progressions/supports/terminale/T11/T11_evaluation_processus_ordonnancement_interblocage.md` | Structure complète | Faible | Stimulus trop pauvre, réponses-étiquettes | Lisible, répétitive | INDIGENT |
| `03_progressions/supports/terminale/T11/T11_remediation_processus_ordonnancement_interblocage.md` | Rubriques minimales | Très faible | Pas d’autre voie d’accès | Claire mais générique | INDIGENT |
| `03_progressions/supports/terminale/T11/T11_tp_processus_ordonnancement_interblocage.md` | Étapes présentes | Faible | TP papier sans timing ni simulation développée | Claire | INDIGENT |
| `03_progressions/supports/terminale/T11/T11_trace_processus_ordonnancement_interblocage.md` | Rubriques minimales | Très faible | Trace insuffisante pour réviser les états | Télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T11/T11_version_amenagee_processus_ordonnancement_interblocage.md` | Aides/exercice/réponses présents | Très faible | Objectif réduit à recopier/cocher | Claire | INDIGENT |
| `03_progressions/supports/terminale/T12/T12_TD_routage_rip_ospf.md` | Plan apparent complet | Très faible | Répétitions et corrigés génériques | Lisible, télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T12/T12_bareme_routage_rip_ospf.md` | Rubriques présentes | Très faible | Pas de critères pour tables intermédiaires | Claire mais abstraite | INDIGENT |
| `03_progressions/supports/terminale/T12/T12_corrige_routage_rip_ospf.md` | Couverture TD/TP/évaluation | Très faible | Résultats sans recalcul de table | Télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T12/T12_cours_routage_rip_ospf.md` | Plan apparent complet | Faible | Méthodes nommées, non enseignées | Lisible, blocs génériques | INDIGENT |
| `03_progressions/supports/terminale/T12/T12_evaluation_routage_rip_ospf.md` | Structure complète | Faible | Quatre calculs courts sur le même graphe | Lisible, répétitive | INDIGENT |
| `03_progressions/supports/terminale/T12/T12_remediation_routage_rip_ospf.md` | Rubriques minimales | Très faible | Répète le calcul initial | Claire mais générique | INDIGENT |
| `03_progressions/supports/terminale/T12/T12_tp_routage_rip_ospf.md` | Assets et étapes présents | Moyenne | Exécutable mais déroulé et rendu insuffisants | Claire | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/terminale/T12/T12_trace_routage_rip_ospf.md` | Rubriques minimales | Très faible | Pas de table ni règle de décision mémorisable | Télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T12/T12_version_amenagee_routage_rip_ospf.md` | Aides/exercice/réponses présents | Très faible | Réponse donnée, appuis non gradués | Claire | INDIGENT |
| `03_progressions/supports/terminale/T13/T13_TD_chiffrement_https.md` | Plan apparent complet | Très faible | Alpha/beta/gamma artificiels, pseudo-code hors sujet | Lisible, télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T13/T13_bareme_chiffrement_https.md` | Rubriques présentes | Très faible | Critères génériques | Claire mais abstraite | INDIGENT |
| `03_progressions/supports/terminale/T13/T13_corrige_chiffrement_https.md` | Couverture TD/TP/évaluation | Très faible | Résultats sans schéma de flux ni raisonnement | Télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T13/T13_cours_chiffrement_https.md` | Plan apparent complet | Faible | Concepts listés, exemples sans déroulé | Lisible, blocs génériques | INDIGENT |
| `03_progressions/supports/terminale/T13/T13_evaluation_chiffrement_https.md` | Structure complète | Faible | Questions sans scénario ni flux à analyser | Lisible, répétitive | INDIGENT |
| `03_progressions/supports/terminale/T13/T13_remediation_chiffrement_https.md` | Rubriques minimales | Très faible | Pas d’autre représentation | Claire mais générique | INDIGENT |
| `03_progressions/supports/terminale/T13/T13_tp_chiffrement_https.md` | Étapes présentes | Faible | TP papier trop court, aucune temporalité | Claire | INDIGENT |
| `03_progressions/supports/terminale/T13/T13_trace_chiffrement_https.md` | Rubriques minimales | Très faible | Ne distingue pas les rôles par une phrase complète | Télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T13/T13_version_amenagee_chiffrement_https.md` | Aides/exercice/réponses présents | Très faible | Résultat donné, pas d’étayage progressif | Claire | INDIGENT |
| `03_progressions/supports/terminale/T14/T14_TD_modularite_api_paradigmes_bugs.md` | Plan apparent complet | Faible | Plusieurs consignes/réponses désalignées ; un exercice 6 concret | Lisible, répétitive | INDIGENT |
| `03_progressions/supports/terminale/T14/T14_bareme_modularite_api_paradigmes_bugs.md` | Rubriques présentes | Très faible | Critères non observables par capacité | Claire mais abstraite | INDIGENT |
| `03_progressions/supports/terminale/T14/T14_corrige_modularite_api_paradigmes_bugs.md` | Couverture TD/TP/évaluation | Moyenne localement | Exercice 6 bien expliqué, reste réduit au résultat | Claire | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/terminale/T14/T14_cours_modularite_api_paradigmes_bugs.md` | Plan apparent complet | Moyenne | Six exemples contextualisés, activité d’entrée absente | Claire, vocabulaire adapté | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/terminale/T14/T14_evaluation_modularite_api_paradigmes_bugs.md` | Structure complète | Faible | Consignes incomplètes, pas de code support | Lisible, répétitive | INDIGENT |
| `03_progressions/supports/terminale/T14/T14_remediation_modularite_api_paradigmes_bugs.md` | Rubriques minimales | Très faible | Rejoue la même tâche | Claire mais générique | INDIGENT |
| `03_progressions/supports/terminale/T14/T14_tp_modularite_api_paradigmes_bugs.md` | Étapes présentes | Faible | TP papier alors que la tâche appelle du code/documentation | Claire | INDIGENT |
| `03_progressions/supports/terminale/T14/T14_trace_modularite_api_paradigmes_bugs.md` | Rubriques minimales | Très faible | Liste de mots, aucun contrat d’API mémorisable | Télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T14/T14_version_amenagee_modularite_api_paradigmes_bugs.md` | Aides/exercice/réponses présents | Très faible | Réponse donnée, aide non graduée | Claire | INDIGENT |
| `03_progressions/supports/terminale/T15/T15_TD_calculabilite_arret.md` | Plan apparent complet | Très faible | Répétitions, pseudo-code générique | Lisible, télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T15/T15_bareme_calculabilite_arret.md` | Rubriques présentes | Très faible | Aucun critère pour les étapes de contradiction | Claire mais abstraite | INDIGENT |
| `03_progressions/supports/terminale/T15/T15_corrige_calculabilite_arret.md` | Couverture TD/TP/évaluation | Très faible | Résultats sans déroulé logique | Télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T15/T15_cours_calculabilite_arret.md` | Plan apparent complet | Faible | Idée exigeante réduite à quatre assertions | Lisible, blocs génériques | INDIGENT |
| `03_progressions/supports/terminale/T15/T15_evaluation_calculabilite_arret.md` | Structure complète | Faible | Raisonnement demandé sans étapes ni formulation précise | Lisible, répétitive | INDIGENT |
| `03_progressions/supports/terminale/T15/T15_remediation_calculabilite_arret.md` | Rubriques minimales | Très faible | Répète l’exemple de l’oracle | Claire mais générique | INDIGENT |
| `03_progressions/supports/terminale/T15/T15_tp_calculabilite_arret.md` | Étapes présentes | Faible | TP papier court sans débat, tri de cas ou trace argumentée | Claire | INDIGENT |
| `03_progressions/supports/terminale/T15/T15_trace_calculabilite_arret.md` | Rubriques minimales | Très faible | Ne restitue pas la preuve par contradiction | Télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T15/T15_version_amenagee_calculabilite_arret.md` | Aides/exercice/réponses présents | Très faible | Donne les conclusions, ne soutient pas le raisonnement | Claire | INDIGENT |
| `03_progressions/supports/terminale/T16/T16_TD_diviser_pour_regner_tri_fusion.md` | Plan apparent complet | Très faible | Doublons déguisés, progression nominale | Lisible, répétitive | INDIGENT |
| `03_progressions/supports/terminale/T16/T16_bareme_diviser_pour_regner_tri_fusion.md` | Rubriques présentes | Très faible | Pas de points par étape de fusion | Claire mais abstraite | INDIGENT |
| `03_progressions/supports/terminale/T16/T16_corrige_diviser_pour_regner_tri_fusion.md` | Couverture TD/TP/évaluation | Très faible | Résultats sans trace et réponses répétées | Télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T16/T16_cours_diviser_pour_regner_tri_fusion.md` | Plan apparent complet | Faible | Pas de définition expliquée ni exemple pas à pas | Lisible, style liste | INDIGENT |
| `03_progressions/supports/terminale/T16/T16_evaluation_diviser_pour_regner_tri_fusion.md` | Structure complète | Faible | Questions courtes sans trace exigée explicitement | Lisible, répétitive | INDIGENT |
| `03_progressions/supports/terminale/T16/T16_remediation_diviser_pour_regner_tri_fusion.md` | Rubriques minimales | Très faible | Refaire/comparer, aucune autre voie | Claire mais générique | INDIGENT |
| `03_progressions/supports/terminale/T16/T16_tp_diviser_pour_regner_tri_fusion.md` | Assets et étapes présents | Moyenne | Exécutable, mais livrable et timing insuffisants | Claire | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/terminale/T16/T16_trace_diviser_pour_regner_tri_fusion.md` | Rubriques minimales | Très faible | Pas d’arbre ni de fusion mémorisable | Télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T16/T16_version_amenagee_diviser_pour_regner_tri_fusion.md` | Aides/exercice/réponses présents | Très faible | Activité réduite à recopier/cocher | Claire | INDIGENT |
| `03_progressions/supports/terminale/T17/T17_TD_programmation_dynamique.md` | Plan apparent complet | Très faible | Huit variantes cycliques, même donnée | Lisible, répétitive | INDIGENT |
| `03_progressions/supports/terminale/T17/T17_bareme_programmation_dynamique.md` | Rubriques présentes | Très faible | Critères génériques, pas de partiel | Claire mais abstraite | INDIGENT |
| `03_progressions/supports/terminale/T17/T17_corrige_programmation_dynamique.md` | Couverture TD/TP/évaluation | Très faible | Pas de table complète ni raisonnement | Télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T17/T17_cours_programmation_dynamique.md` | Plan apparent complet | Faible | Relation donnée sans construction du besoin | Lisible, style liste | INDIGENT |
| `03_progressions/supports/terminale/T17/T17_evaluation_programmation_dynamique.md` | Structure complète | Faible | Une seule donnée, réponses trop courtes | Lisible, répétitive | INDIGENT |
| `03_progressions/supports/terminale/T17/T17_remediation_programmation_dynamique.md` | Rubriques minimales | Très faible | Pas de diagnostic branché ni contre-exemple glouton | Claire mais générique | INDIGENT |
| `03_progressions/supports/terminale/T17/T17_tp_programmation_dynamique.md` | Assets et étapes présents | Moyenne | Exécutable, mais déroulé et rendu insuffisants | Claire | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/terminale/T17/T17_trace_programmation_dynamique.md` | Rubriques minimales | Très faible | Liste de mots, aucune table | Télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T17/T17_version_amenagee_programmation_dynamique.md` | Aides/exercice/réponses présents | Très faible | Réponse donnée, étayage non progressif | Claire | INDIGENT |
| `03_progressions/supports/terminale/T18/T18_TD_boyer_moore.md` | Plan apparent complet | Très faible | Doublons et pseudo-code générique malgré une notion traçable | Lisible, répétitive | INDIGENT |
| `03_progressions/supports/terminale/T18/T18_bareme_boyer_moore.md` | Rubriques présentes | Moyenne | TP mieux critérié, évaluation encore générique | Claire | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/terminale/T18/T18_corrige_boyer_moore.md` | Couverture TD/TP/évaluation | Faible | Résultats exacts mais raisonnement trop comprimé | Télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T18/T18_cours_boyer_moore.md` | Plan apparent complet | Moyenne-faible | Exemple cohérent, explication et motivation insuffisantes | Claire | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/terminale/T18/T18_evaluation_boyer_moore.md` | Structure complète | Moyenne-faible | Trace concrète mais cas unique et corrigé court | Claire | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/terminale/T18/T18_remediation_boyer_moore.md` | Rubriques minimales | Moyenne-faible | Ajoute une comparaison guidée, mais transfert absent | Claire | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/terminale/T18/T18_tp_boyer_moore.md` | Objectif, livrable, assets et cas tests présents | Forte | Fonctions nommées, trace et cas limites exécutables | Claire et opérationnelle | RICHE |
| `03_progressions/supports/terminale/T18/T18_trace_boyer_moore.md` | Très complète | Forte | Table de trace, pseudo-code, corrigé et liens exécutables | Claire et révisable | RICHE |
| `03_progressions/supports/terminale/T18/T18_version_amenagee_boyer_moore.md` | Aides/exercice/réponses présents | Très faible | Réponses données, pas de trace à compléter | Claire | INDIGENT |
| `03_progressions/supports/terminale/T19/T19_TD_bac_pratique_grand_oral_projet.md` | Plan complet | Moyenne, très inégale | Exercices 9–10 riches ; 1–8 templés et répétitifs | Claire | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/terminale/T19/T19_bareme_bac_pratique_grand_oral_projet.md` | Rubriques présentes | Très faible | Critères génériques, ignore la richesse des ex. 9–10 | Claire mais abstraite | INDIGENT |
| `03_progressions/supports/terminale/T19/T19_corrige_bac_pratique_grand_oral_projet.md` | Couverture large | Moyenne-faible | Ex. 9–10 structurés ; reste réduit au résultat | Claire | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/terminale/T19/T19_cours_bac_pratique_grand_oral_projet.md` | Plan complet mais composite | Moyenne à forte localement | Frise et analyse historique solides ; entrée/préparation bac génériques | Claire et bien structurée localement | CORRECT-MAIS-PERFECTIBLE |
| `03_progressions/supports/terminale/T19/T19_evaluation_bac_pratique_grand_oral_projet.md` | Structure complète | Très faible | Aucun matériau fourni pour réaliser les tâches | Lisible, abstraite | INDIGENT |
| `03_progressions/supports/terminale/T19/T19_remediation_bac_pratique_grand_oral_projet.md` | Rubriques minimales | Très faible | Répète une tâche sans support | Claire mais générique | INDIGENT |
| `03_progressions/supports/terminale/T19/T19_tp_bac_pratique_grand_oral_projet.md` | Étapes présentes | Faible | Livrable annoncé sans graphe, code ni timing | Claire | INDIGENT |
| `03_progressions/supports/terminale/T19/T19_trace_bac_pratique_grand_oral_projet.md` | Rubriques minimales | Très faible | Ne conserve ni frise ni méthode d’argumentation | Télégraphique | INDIGENT |
| `03_progressions/supports/terminale/T19/T19_version_amenagee_bac_pratique_grand_oral_projet.md` | Aides/exercice/réponses présents | Très faible | Réponses données, aucun appui progressif | Claire | INDIGENT |

## 4. TOP-10 DES PRIORITÉS D’ENRICHISSEMENT

| Rang | Séquence/document | Problème | Impact élève | Prescription détaillée |
|---:|---|---|---|---|
| 1 | P06–P14 et T06–T19 — TD | Huit variantes cycliques sur une même donnée et corrigés alpha/beta/gamma génériques | L’élève répète des formulations et des résultats sans apprendre à transférer, programmer ou déboguer. | Recomposer chaque TD autour de six tâches distinctes et d’au moins trois données : trace guidée, application autonome, écriture, analyse, débogage, transfert ; écrire un corrigé propre à chaque tâche. |
| 2 | T10 — cours, deux évaluations, corrigé | Opérations SQL décalées entre consignes et réponses ; sujets SELECT et DML presque confondus | Risque d’apprentissage faux et impossibilité de corriger équitablement. | Refaire le lot d’un seul tenant sur un schéma relationnel explicite ; une requête complète et une table résultat par question ; séparer lecture SELECT/JOIN de l’écriture INSERT/UPDATE/DELETE ; tester toutes les requêtes sur la même base fictive. |
| 3 | P00–P05 et T00–T05 — cours principaux | Pseudo-définitions circulaires et données identiques aux trois étages | L’élève voit beaucoup de texte mais ne construit ni concept ni transfert. | Réécrire chaque définition en formulation élève + formalisme/code + exemple/non-exemple ; garder un modèle au cours, varier les données au TD et réserver un cas inédit à l’évaluation. |
| 4 | P08 et évaluations P06+/T06+ | Sujets dupliqués ou atomisés, mêmes données, barèmes interchangeables | L’évaluation mesure la reconnaissance et laisse de côté analyse, écriture et justification. | Concevoir chaque triptyque évaluation–barème–corrigé sur stimulus nouveau : lecture 20 %, application 30 %, production 30 %, justification/cas limite 20 %, avec critères et réponses partielles propres. |
| 5 | P06–P14 et T06–T19 — remédiations/versions aménagées | Même tâche rejouée ou réponse affichée | Les élèves fragiles obtiennent une réussite de copie, pas une autre voie d’apprentissage. | Brancher la remédiation sur trois diagnostics ; proposer représentation alternative et aides déclenchables ; retirer progressivement l’aide ; terminer par une tâche isomorphe sans réponse visible. |
| 6 | P06–P14 et T06–T19 — barèmes/corrigés | Points « donnée/méthode/résultat/cas limite » et corrigés réduits au résultat | Le raisonnement reste invisible et les réussites partielles ne sont pas reconnues. | Définir par question les étapes observables, plafonds et erreurs locales ; montrer dans le corrigé la trace, les décisions, le contrôle et un piège commenté. |
| 7 | P11, P12, T16, T17 — algorithmique | Algorithmes, invariants et coûts annoncés sans déroulé complet | L’élève ne peut ni reconstruire l’algorithme ni justifier correction ou complexité. | Ajouter pseudo-code complet, table de trace, invariant initialisation/conservation/terminaison, comptage exact et cas vide/doublons/impossible. |
| 8 | P02/P04 et compléments analogues | Sections « exercice complémentaire » d’une ligne et différenciation nominale | Des rubriques donnent une illusion de complétude sans tâche utilisable. | Supprimer les coquilles ou écrire des énoncés autosuffisants ; pour chaque niveau, indiquer donnée, aide, consigne, livrable et critère. |
| 9 | P06–P14 et T06–T19 — traces | Listes de mots et résultats isolés | La trace ne permet pas de réviser ni de réappliquer une méthode. | Produire une page structurée : quatre définitions utiles, méthode numérotée, exemple complet, deux pièges avec antidotes, cas limites et question d’auto-vérification. |
| 10 | P06–P14 et T06–T19 — TP et contrats | Assets parfois présents, mais déroulé, rendu et exigence contractuelle génériques | Temps de séance mal maîtrisé et production difficile à évaluer. | Définir timing, signatures, fichiers rendus, commande ou protocole de test, cas limites obligatoires et prolongement ; inscrire ces exigences explicitement dans le contrat. |

1. **Mini-plan priorité 1 — banque de TD.** Diagnostic 5 min ; exemple guidé ; application sur donnée nouvelle ; trace à analyser ; code ou pseudo-code à écrire ; bug à corriger ; transfert final ; corrigé montrant chaque décision.
2. **Mini-plan priorité 2 — T10 SQL.** Schéma `Eleve/Note` et données ; lecture d’un SELECT ; construction d’un JOIN clause par clause ; UPDATE avec vérification par SELECT ; DELETE avec transaction simulée ; contre-exemples sans `ON`/`WHERE` ; deux sujets distincts et leurs corrigés exécutés.
3. **Mini-plan priorité 3 — définitions et transfert.** Situation courte ; définition élève ; formalisation ; exemple travaillé ; non-exemple ; question flash ; données différentes au TD ; cas inédit en évaluation.
4. **Mini-plan priorité 4 — évaluation.** Stimulus complet ; question de lecture ; application ; production ; débogage ou justification ; barème par observable ; corrigé raisonné ; essai chronométré par un élève moyen préparé.
5. **Mini-plan priorité 5 — remédiation/aménagement.** Production erronée réaliste ; diagnostic ; trois parcours ; aide 1 lexique, aide 2 amorce, aide 3 étape intermédiaire ; tâche de réparation ; tâche de sortie sans aide.
6. **Mini-plan priorité 6 — correction/notation.** Lister les observables ; répartir méthode/résultat ; prévoir erreurs locales ; rédiger la trace complète ; ajouter cas limite ; expliciter demi-crédits et plafonds ; aligner le barème au corrigé.
7. **Mini-plan priorité 7 — algorithmique.** Faire prédire ; tracer chaque état ; formuler l’invariant ; coder ; prouver terminaison/correction au niveau attendu ; compter opérations ; comparer deux tailles ou stratégies ; tester les limites.
8. **Mini-plan priorité 8 — compléments/différenciation.** Un exercice de lecture ; un de construction ; un de débogage ; un de transfert ; niveau socle avec support tangible ; standard autonome ; expert avec changement de spécification ; corrigés référencés.
9. **Mini-plan priorité 9 — trace écrite.** Définition ; « quand l’utiliser » ; procédure numérotée ; exemple complet ; encadré pièges ; cas limites ; mini-question de rappel ; renvoi vers un exercice corrigé.
10. **Mini-plan priorité 10 — TP/contrat.** Objectif et livrable ; 0–10 min prise en main ; 10–35 min construction ; 35–50 min tests ; 50–55 min bilan ; fichiers/signatures/commande ; nominal/limite/invalide ; extension experte.

## 5. PANTHÉON — DOCUMENTS EXEMPLAIRES

| Document | Fichier:lignes | Extrait | Pourquoi c’est exemplaire | Standard interne à généraliser |
|---|---|---|---|---|
| Cours conversion d’encodages | `03_progressions/supports/premiere/P03/P03_cours_conversion_encodages_texte.md:137-166` | « Étape 1 : Identifier l’encodage source […] Étape 2 : Lire […] Étape 3 : Écrire […] Vérification : lire le fichier produit et examiner les octets. » | Problème authentique, démarche numérotée, code complet et contrôle indépendant au niveau des octets. | Toute méthode doit articuler pourquoi, étapes exécutables et vérification observable. |
| TD tables de vérité | `03_progressions/supports/premiere/P02/P02_td_tables_verite_booleennes.md:41-138` | « niveau fondamental » → « niveau intermédiaire » → « niveau avancé » → « Application : vote majoritaire ». | La progression se lit réellement dans les données, le nombre d’étapes et le verbe demandé. | Toute gradation annoncée doit modifier charge cognitive, autonomie et type de production. |
| Cours interface/implémentation | `03_progressions/supports/terminale/T01/T01_cours_interface_implementation_complement.md:136-156` | Le tableau compare stockage, accès sommet, coûts et mémoire, puis conclut « Interface identique » avec le même code client. | Le contraste matérialise quoi/comment, relie code et coût et fournit une preuve observable de substituabilité. | Toute notion abstraite doit être montrée sur deux implémentations contrastées soumises au même test. |
| TP BFS/DFS | `03_progressions/supports/terminale/T08/T08_TP_bfs_dfs_cycles_chemins.md:80-112` | La trace détaille file, marqués et prédécesseurs étape par étape ; les fonctions retournent ordre et prédécesseurs. | Livrable testable, états internes visibles, distinction BFS/DFS et traitement de cycle, sommet isolé et destination absente. | Tout TP algorithmique doit exiger trace avant exécution, tests nominal/limite et sortie exploitable. |
| Trace Boyer–Moore | `03_progressions/supports/terminale/T18/T18_trace_boyer_moore.md:43-77` | « Alignement 0 […] max(1, 2-1)=1 […] décaler de 1 », puis pseudo-code numéroté. | Le document relie table, calcul, décision, pseudo-code et cas absent ; le raisonnement peut être reconstruit en révision. | Toute trace algorithmique doit contenir au moins une exécution complète cohérente avec la méthode et les tests. |

## 6. COUVERTURE

### Documents lus

- 35 contrats : `03_progressions/supports/contracts/*.yml`.
- 160 maîtres Première : `03_progressions/supports/premiere/P00-P14/*.md`.
- 206 maîtres Terminale : `03_progressions/supports/terminale/T00-T19/*.md`.
- La liste individuelle exhaustive des 401 documents est la grille de la section 3.
- Lecture approfondie section par section des 41 cours, 43 TD et 43 évaluations ; analyse ciblée exhaustive des 41 barèmes, 41 corrigés, 41 traces, 46 TP, 35 versions aménagées et 35 remédiations.

### Méthode d’analyse

- Contexte capturé : branche `main`, HEAD `a6e7736a66a03f8e34e836d2a29f3fed3867cf1f`; `git status --short` vide au départ ; historique récent consulté sur 12 commits.
- Présence vérifiée du canon `03_progressions/supports/` et du référentiel `00_programmes_officiels/programme_nsi_2019.yaml`.
- Inventaire par `find` et classement par famille ; repérage par `rg` des variantes, alpha/beta/gamma, critères génériques, différenciations, remédiations et titres.
- Analyse complémentaire en lecture seule : longueurs de sections, répétitions normalisées et similarités ; 26 fichiers portent `jeu_exercice=alpha`, 36 fichiers le pseudo-code `if cas_…`, 23 versions aménagées demandent de « choisir la capacité ».
- Toute preuve retenue dans les constats et le panthéon a été relue dans le fichier source avec `nl -ba fichier | sed -n 'X,Yp'`.
- Trois lots indépendants ont été relus puis consolidés : Première 160/160, Terminale T00–T09 114/114, Terminale T10–T19 92/92 ; chaque grille a été contrôlée contre `find` avant fusion.

### Zones jugées saines

- Les compléments P02 tables de vérité, P03 encodages, T01 interface/implémentation, T03 recherche liste/dictionnaire et T05 arbres montrent une vraie construction des notions.
- Plusieurs TP sont réellement exploitables, notamment P07 fonctions/tests et T08 BFS/DFS ; T18 relie correctement trace, tests et cas limites.
- P13 propose un cours et un TD globalement substantiels malgré une répétition locale de k-NN.
- Les remédiations P00–P05 sont généralement plus concrètes et diversifiées que celles de P06–P14.
- La langue et l’organisation matérielle sont le plus souvent lisibles ; la faiblesse dominante porte sur la substance et la progressivité, non sur l’architecture des maîtres avec réponses intégrées.

## 7. LIMITES

- La revue porte sur la richesse pédagogique et éditoriale des maîtres Markdown et des contrats ; elle ne rejoue ni gates CI, ni validation de statut, ni campagne de substance↔libellé.
- Les projections LaTeX n’ont pas été relues et l’architecture « documents maîtres avec réponses embarquées » a été traitée comme normale.
- Les assets Python mentionnés par les TP n’ont pas été exécutés : l’exécutabilité est réputée déjà traitée ; le jugement porte sur le scénario, les appuis annoncés, le livrable et les cas limites.
- Aucune famille n’a été échantillonnée pour la grille : 401/401 documents sont classés ; l’analyse des familles hors cours/TD/évaluation est ciblée par fonction documentaire, non une nouvelle validation scientifique.
- Les dettes explicitement exclues par la mission (élisions legacy, décision sur les deux TP P08, gate post-flip, T-LANG-04A partial, exactitude mécanique, campagne de substance) n’ont pas été comptées comme anomalies nouvelles.
- Une revue humaine ultérieure en situation de classe reste nécessaire pour chronométrer les évaluations et TP, observer les aides avec des élèves et confirmer l’efficacité des remédiations.
