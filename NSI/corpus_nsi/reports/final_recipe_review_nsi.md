# Revue de recette finale — Corpus NSI

## 1. VERDICT GLOBAL

Verdict : REQUIRES_FIXES

Comptes :

| Axe | P0 | P1 | P2 | P3 |
|---|---:|---:|---:|---:|
| Axe 1 | 2 | 2 | 3 | 0 |
| Axe 2 | 6 | 3 | 0 | 0 |
| Axe 3 | 0 | 0 | 5 | 0 |
| Axe 4 | 0 | 2 | 0 | 0 |
| Axe 5 | 0 | 4 | 0 | 0 |
| Axe 6 | 2 | 1 | 0 | 0 |

Jugement d’ensemble :

1. Les gates mécaniques visibles sont majoritairement verts, mais ils ne détectent ni les rotations sémantiques entre capacité, consigne et réponse, ni les fuites de corrigé dans les documents à distribuer.
2. Les chaînes P08, T07, T09 et T14 comportent des associations officiellement fausses ou des maillons d’évaluation absents ; P13 reste scientifiquement solide sur les calculs ciblés, mais son TP, sa remédiation et son corrigé séparé ne sont pas prêts à distribuer.
3. Le dossier v4 recompte correctement 113/1/0, mais deux fiches 3/3 et quatre verdicts hors dossier ne résistent pas à la lecture substantielle. Le présent rapport est un intrant de correction et ne signe ni la promotion ni la publication.

## 2. TABLEAU DES CONSTATS

| ID | Axe | Sévérité | Fichier:lignes | Extrait | Attendu vs Trouvé | Prescription | Statut |
|---|---|---|---|---|---|---|---|
| RVW-001 | Axe 1 | P0 | 03_progressions/supports/premiere/P00/P00_evaluation_diagnostic_python.md:53-58,112-116 | « Énoncé : résoudre trace d’affectation… Réponse attendue : 7 affiché » puis « Corrigé question 1 » | Attendu : sujet élève sans solution. Trouvé : réponse et corrigé dans l’évaluation imprimable ; le même motif est détecté dans 22 évaluations sur 29 du périmètre. | Séparer matériel élève et corrigé professeur, puis contrôler l’absence de « Réponse attendue » et de sections corrigées dans l’artefact élève. | CONFIRMÉ |
| RVW-002 | Axe 1 | P1 | 03_progressions/supports/premiere/P08/P08_cours_web_http_dom_formulaires.md:107-111 | « TD : P08_TD_web_http_dom_formulaires.md… TP : P08_tp_web_http_dom_formulaires.md… Évaluation : P08_evaluation_web_http_dom_formulaires.md » | Attendu : fichiers liés existants. Trouvé : les trois noms cités sont absents ; les fichiers présents ont des suffixes html_css_dom ou http_get_post_formulaires. | Remplacer chaque référence par un fichier existant ou fournir un index explicite vers les deux variantes ; ajouter un contrôle des noms placés entre délimiteurs de code. | CONFIRMÉ |
| RVW-003 | Axe 1 | P2 | 03_progressions/supports/premiere/P08/P08_TP_html_css_dom.md:1-10 ; 03_progressions/supports/premiere/P08/P08_TP_http_get_post_formulaires.md:1-10 | Les deux fichiers commencent par le même front matter et le même titre « P08 - tp - HTML, CSS, DOM, HTTP et formulaires » | Attendu : deux TP distincts ou une référence unique. Trouvé : contenus strictement identiques, SHA-256 b89aed99… pour les deux noms. | Désigner un canon et référencer l’autre, ou différencier réellement les objectifs, données et livrables. | CONFIRMÉ |
| RVW-004 | Axe 1 | P2 | 03_progressions/supports/premiere/P13/P13_bareme_dichotomie_glouton_knn.md:22-23 ; 03_progressions/supports/premiere/P13/P13_TD_dichotomie_glouton_knn.md:89-95 | « 8 exercices » ; le TD contient « Exercice 9 » | Attendu : compteur et points couvrant tous les exercices. Trouvé : l’exercice 9 n’entre pas dans le compteur. Le même décalage existe pour P07, P09, P10, P14, T07 et T19. | Recompter chaque TD depuis ses titres et attribuer explicitement les points aux exercices ajoutés, sans modifier le gate pour accepter le décalage. | CONFIRMÉ |
| RVW-005 | Axe 1 | P1 | 03_progressions/supports/premiere/P04/P04_evaluation_types_construits_complement.md:42-43,114-115,178-185 | « Question 1 … 4 points » ; « Question 5 … 4 points » ; table finale limitée aux questions 1 à 3, total 15 | Attendu : cinq questions notées et total cohérent de 20 points. Trouvé : barème final de trois questions, total 15. | Fournir cinq lignes de barème dont la somme reprend les points annoncés par les titres, puis vérifier le total. | CONFIRMÉ |
| RVW-006 | Axe 1 | P2 | 03_progressions/supports/premiere/P02/P02_evaluation_tables_verite_booleennes.md:64-70,87-100,141-148 | « Question 2 … 6 points », « Question 3 … 4 points » ; table : Q2=5, Q3=5 | Attendu : ventilation identique entre énoncé et table. Trouvé : total identique mais redistribution contradictoire. | Aligner la table finale sur 5/6/4 ou modifier les sous-points du sujet après arbitrage pédagogique explicite. | CONFIRMÉ |
| RVW-030 | Axe 1 | P0 | 03_progressions/supports/premiere/P13/P13_TD_dichotomie_glouton_knn.md:31-38,97-103 ; 03_progressions/supports/premiere/P13/P13_tp_dichotomie_glouton_knn.md:28-33,41-49 | Le TD affiche « Réponse attendue » puis un « Corrigé » ; le TP affiche son « Corrigé question par question » | Attendu : TD et TP élèves distribuables, le corrigé étant déjà un fichier séparé. Trouvé : solutions visibles dans les supports élèves ; le scan retrouve ce motif dans les 59 TD/TP du périmètre. | Générer des variantes élèves sans réponses et conserver les solutions dans les corrigés professeur ; ajouter un contrôle de rôle documentaire. | CONFIRMÉ |
| RVW-007 | Axe 2 | P0 | 03_progressions/supports/premiere/P13/P13_tp_dichotomie_glouton_knn.md:28-33,41-49 | Question 3 : « montrer que V … décroît » ; corrigé 3 : « 28 -> 10+10+5+2+1 » | Attendu : correction de la preuve de terminaison. Trouvé : réponse de glouton sans rapport avec la question. | Réaligner le corrigé question par question sur le travail demandé, puis refaire une vérification croisée TP/corrigé. | CONFIRMÉ |
| RVW-008 | Axe 2 | P0 | 03_progressions/supports/premiere/P13/P13_remediation_dichotomie_glouton_knn.md:27-32 | « Refaire la tâche calculer milieu… Relier la réponse à P-ALGO-03 » | Attendu : la dichotomie relève de P-ALGO-04. Trouvé : rattachement à P-ALGO-03, capacité k-NN. | Corriger le rattachement pédagogique et vérifier chaque activité corrective contre le référentiel officiel interne. | CONFIRMÉ |
| RVW-009 | Axe 2 | P1 | 03_progressions/supports/premiere/P13/P13_corrige_dichotomie_glouton_knn.md:64-68 | « Réponse attendue : distances calculées, 3 plus proches… » | Attendu : valeurs des cinq distances demandées en 9a. Trouvé : aucune distance chiffrée dans le corrigé canonique séparé. | Ajouter les cinq calculs et leur ordre, puis distinguer égalité de distance et égalité de vote. | CONFIRMÉ |
| RVW-010 | Axe 2 | P0 | 03_progressions/supports/premiere/P08/P08_TD_http_get_post_formulaires.md:66-78 | P-IHM-03B demande « repérer header main form… » ; P-IHM-03C demande « cibler #nom en CSS et DOM » | Attendu : mémorisation/retransmission pour P-IHM-03B et chiffrement pour P-IHM-03C. Trouvé : tâches HTML/DOM étrangères aux libellés. | Réécrire les exercices 5 et 6 à partir des libellés officiels, avec données, correction et cas limites propres. | CONFIRMÉ |
| RVW-011 | Axe 2 | P1 | 03_progressions/supports/premiere/P08/P08_evaluation_html_css_dom.md:13-23,33-53 | Métadonnées : neuf capacités P-IHM-01A à P-IHM-04C ; sujet : quatre questions arrêtées à P-IHM-03A | Attendu : chaîne d’évaluation et barème pour chaque capacité annoncée. Trouvé : cinq capacités sans question ni point. | Réduire honnêtement les capacités annoncées ou ajouter les cinq maillons évaluation/barème/corrigé manquants. | CONFIRMÉ |
| RVW-012 | Axe 2 | P0 | 03_progressions/supports/terminale/T07/T07_cours_graphes_modelisation_listes_matrices.md:63-72 | T-STRUCT-05C : « calculer degré sortant » avec résultat « matrice 4x4 -> 16 cases » ; T-STRUCT-05D : « choisir liste pour graphe peu dense » | Attendu : implémenter une liste de successeurs puis convertir une représentation. Trouvé : méthode, résultat et capacité sont désynchronisés. | Refaire la chaîne cours, TD, évaluation, barème et corrigé depuis les quatre libellés officiels ; conserver l’exercice 3bis comme point de départ pour 05C. | CONFIRMÉ |
| RVW-013 | Axe 2 | P0 | 03_progressions/supports/terminale/T09/T09_evaluation_bases_relationnelles_cles_contraintes.md:29-48 | Q1 demande schéma/instance mais répond clé primaire ; Q2 demande unicité mais répond clé étrangère ; Q4 demande id_livre=9 absent mais répond suppression | Attendu : chaque réponse répond exactement à sa question et à sa capacité. Trouvé : trois réponses décalées. | Réaligner question, capacité, réponse, barème et corrigé ; tester la chaîne avec une matrice question→production attendue. | CONFIRMÉ |
| RVW-014 | Axe 2 | P0 | 03_progressions/supports/terminale/T14/T14_cours_modularite_api_paradigmes_bugs.md:58-77 | T-LANG-03A « définir fonction publique », 03B « séparer module », 03C « choisir paradigme », 04A « écrire un test révélant un bug » | Attendu : utiliser une API, exploiter sa documentation, créer/documenter un module, distinguer les paradigmes. Trouvé : les tâches sont affectées aux mauvais libellés. | Reconstruire les exemples et exercices à partir des libellés YAML ; ne pas promouvoir par simple présence du code capacité. | CONFIRMÉ |
| RVW-015 | Axe 2 | P1 | 03_progressions/supports/terminale/T14/T14_evaluation_modularite_api_paradigmes_bugs.md:13-20,30-49 | Métadonnées : six capacités jusqu’à T-LANG-05 ; sujet : quatre questions jusqu’à T-LANG-04A | Attendu : T-LANG-04B et T-LANG-05 évaluées si annoncées. Trouvé : aucun maillon évaluation/barème pour ces deux capacités. | Ajouter des questions alignées ou réduire les métadonnées de l’évaluation ; vérifier aussi le corrigé et le barème. | CONFIRMÉ |
| RVW-016 | Axe 3 | P2 | 03_progressions/supports/terminale/T04/T04_cours_recursivite.md:208-214 ; 03_progressions/supports/terminale/T04/T04_corrige_recursivite.md:113-116 | Code : « return lst[0] + somme_fonctionnel(lst[1:]) » ; correction : « pas d’optimisation tail-call en Python » | Attendu : expliquer la pile d’appels du code non terminal. Trouvé : justification par TCO alors que l’appel récursif n’est pas en position terminale. | Expliquer que l’addition reste en attente sur la pile ; réserver la discussion TCO à un véritable code tail-récursif. | CONFIRMÉ |
| RVW-017 | Axe 3 | P2 | 03_progressions/supports/premiere/P08/P08_cours_web_http_dom_formulaires.md:164-166,187-191 | « localStorage est cloisonné par origine » puis « partagé entre tous les onglets du même domaine » | Attendu : terminologie constante « même origine » (schéma, hôte, port). Trouvé : retour au seul domaine, plus large et contradictoire. | Remplacer « domaine » par « origine » et conserver la nuance entre localStorage et sessionStorage. | CONFIRMÉ |
| RVW-018 | Axe 3 | P2 | 03_progressions/supports/premiere/P08/P08_cours_web_http_dom_formulaires.md:119-125 | « Longueur maximale ~2048 caractères » ; POST, mise en cache : « Non » | Attendu : limites dépendant du client/serveur et cache POST rare mais possible avec directives explicites. Trouvé : absolus non portables. | Reformuler comme ordres de grandeur/usage courant et préciser les dépendances d’implémentation et les exceptions HTTP. | CONFIRMÉ |
| RVW-019 | Axe 3 | P2 | 03_progressions/supports/terminale/T09/T09_cours_bases_relationnelles_cles_contraintes.md:121-125 | « Un SGBD en mémoire (Redis) sacrifie la persistance pour la vitesse » | Attendu : distinguer SGBD relationnel, magasin clé-valeur et persistance configurable. Trouvé : Redis est présenté comme contre-exemple relationnel avec absence de persistance absolue. | Employer un exemple relationnel pertinent ou qualifier Redis et ses modes de persistance. | CONFIRMÉ |
| RVW-020 | Axe 3 | P2 | 03_progressions/supports/terminale/T19/T19_cours_bac_pratique_grand_oral_projet.md:106-115,120-124 | « ARPANET (premier réseau à commutation de paquets) » ; « ENIAC, EDVAC sont câblés pour des tâches spécifiques » | Attendu : attribution historique sourcée et distinction ENIAC/EDVAC. Trouvé : deux formulations historiquement contestables ; la vérification institutionnelle externe n’a pas retourné de source exploitable pendant cette recette. | Faire vérifier par une source muséale/institutionnelle : antériorité du réseau NPL et nature à programme enregistré d’EDVAC, puis corriger ou nuancer. | SUSPECTÉ |
| RVW-021 | Axe 4 | P1 | substance_reviews/campaign/T-LANG-05_substance_review.json:10-17 | Libellé « répondre aux causes typiques de bugs » ; preuve cours « écrire un test… isoler une dépendance » | Attendu : le cours enseigne des causes typiques et leurs réponses. Trouvé : la citation enseigne une méthode de diagnostic, pas les causes. | Rejuger le rôle course ; conserver practice/correction si pertinentes et exiger une preuve de cours portant explicitement sur des causes. | CONFIRMÉ |
| RVW-022 | Axe 4 | P1 | substance_reviews/campaign/T-STRUCT-05C_substance_review.json:10-17 | Libellé « écrire l’implémentation… par listes » ; preuve cours « traduire… passer de la liste à la matrice… comparer le coût » | Attendu : construction/implémentation d’une liste de successeurs. Trouvé : la preuve cours ne l’enseigne pas. | Rejuger en 2/3 tant qu’une preuve de cours d’implémentation n’est pas fournie. | CONFIRMÉ |
| RVW-023 | Axe 5 | P1 | substance_reviews/campaign/T-BDD-02_substance_review.json:10-34 | Practice/correction : id_livre absent et suppression refusée, déclarés preuve des « services rendus par un SGBD » | Attendu : activité et correction sur persistance, concurrence, efficacité ou sécurité. Trouvé : seule une contrainte d’intégrité référentielle est travaillée. | Contester le 3/3 et fournir une activité/correction sur les services réellement listés dans le cours. | CONFIRMÉ |
| RVW-024 | Axe 5 | P1 | substance_reviews/campaign/T-LANG-03C_substance_review.json:10-34 | Libellé « créer des modules simples et les documenter » ; trois preuves sur « choisir paradigme » et convertir temperature | Attendu : création de module, interface/import et documentation. Trouvé : 3/3 pédagogiquement hors sujet, ce que la justification JSON reconnaît comme « superficiel ». | Passer le verdict substantiel à contesté et produire trois preuves réellement alignées. | CONFIRMÉ |
| RVW-025 | Axe 5 | P1 | substance_reviews/campaign/T-ALGO-03_substance_review.json:10-34 | Libellé « écrire un algorithme diviser pour régner » ; pratique « couper en deux sous-listes » | Attendu : écriture d’un algorithme complet division, cas de base, appels récursifs et combinaison. Trouvé : la preuve d’entraînement et sa correction ne couvrent que la division. | Rejuger au plus partial et ajouter une production algorithmique complète avec correction. | CONFIRMÉ |
| RVW-026 | Axe 5 | P1 | substance_reviews/campaign/P-ALGO-01A_substance_review.json:10-34 | Libellé « écrire un algorithme de recherche d’une occurrence » ; pratique « parcourir avec indice » et réponse « indice 1 » | Attendu : écrire ou compléter l’algorithme. Trouvé : calcul manuel de résultat sans production algorithmique. | Remplacer la preuve d’entraînement par une écriture de pseudo-code/Python et une correction exécutable. | CONFIRMÉ |
| RVW-027 | Axe 6 | P0 | latex/packs/premiere/P13/P13_td.tex:3,13-31 | Macro et exercices affichent « Réponse attendue » dans le TD | Attendu : version élève sans réponse. Trouvé : réponses des neuf exercices dans le même TeX. | Produire une projection élève sans le cinquième argument visible et réserver les réponses au corrigé professeur. | CONFIRMÉ |
| RVW-028 | Axe 6 | P0 | latex/packs/premiere/P13/P13_tp.tex:12-19,29-35 | « Travail demandé » suivi de « Corrigé » dans le même document | Attendu : TP élève sans solution. Trouvé : correction complète à la suite du sujet. | Séparer les projections élève/professeur et ajouter une vérification d’absence de section Corrigé dans l’élève. | CONFIRMÉ |
| RVW-029 | Axe 6 | P1 | 03_progressions/supports/premiere/P13/P13_tp_dichotomie_glouton_knn.md:46-49 ; latex/packs/premiere/P13/P13_tp.tex:29-34 | Markdown Q3 corrigée par « 28 -> 10+10+5+2+1 » ; TeX Q3 corrigée par « V … décroît de 6 à 3 » | Attendu : sens identique entre canon et projection. Trouvé : deux corrections différentes ; le TeX est aligné, le canon ne l’est pas. | Corriger le canon lors d’un lot auteur séparé, puis régénérer la projection et contrôler exercice par exercice. | CONFIRMÉ |

## 3. GRILLE DE RECETTE

| Document | Complet | Autosuffisant | Cohérent | Correct | Clair | Niveau | Verdict |
|---|---|---|---|---|---|---|---|
| `03_progressions/supports/premiere/P00/P00_bareme_diagnostic_python.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P00/P00_corrige_diagnostic_python.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P00/P00_cours_diagnostic_python.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P00/P00_evaluation_diagnostic_python.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P00/P00_remediation_diagnostic_python.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P00/P00_td_diagnostic_python.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P00/P00_tp_diagnostic_python.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P00/P00_trace_diagnostic_python.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P00/P00_version_amenagee_diagnostic_python.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P02/P02_bareme_complement_booleens.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P02/P02_corrige_complement_booleens.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P02/P02_corrige_tables_verite_booleennes.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P02/P02_cours_complement_booleens.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P02/P02_cours_tables_verite_booleennes.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P02/P02_evaluation_complement_booleens.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P02/P02_evaluation_tables_verite_booleennes.md` | Non | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P02/P02_remediation_complement_booleens.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P02/P02_td_complement_booleens.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P02/P02_td_tables_verite_booleennes.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P02/P02_tp_complement_booleens.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P02/P02_tp_tables_verite_booleennes.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P02/P02_trace_complement_booleens.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P02/P02_trace_tables_verite_booleennes.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P02/P02_version_amenagee_complement_booleens.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P03/P03_bareme_texte_reels.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P03/P03_corrige_conversion_encodages_texte.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P03/P03_corrige_texte_reels.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P03/P03_cours_conversion_encodages_texte.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P03/P03_cours_texte_reels.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P03/P03_evaluation_conversion_encodages_texte.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P03/P03_evaluation_texte_reels.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P03/P03_remediation_texte_reels.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P03/P03_td_conversion_encodages_texte.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P03/P03_td_texte_reels.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P03/P03_tp_conversion_encodages_texte.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P03/P03_tp_texte_reels.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P03/P03_trace_conversion_encodages_texte.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P03/P03_trace_texte_reels.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P03/P03_version_amenagee_texte_reels.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P04/P04_bareme_types_construits.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P04/P04_corrige_types_construits.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P04/P04_corrige_types_construits_complement.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P04/P04_cours_types_construits.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P04/P04_cours_types_construits_complement.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P04/P04_evaluation_types_construits.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P04/P04_evaluation_types_construits_complement.md` | Non | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P04/P04_remediation_types_construits.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P04/P04_td_types_construits.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P04/P04_td_types_construits_complement.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P04/P04_tp_types_construits.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P04/P04_tp_types_construits_complement.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P04/P04_trace_types_construits.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P04/P04_trace_types_construits_complement.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P04/P04_version_amenagee_types_construits.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P07/P07_TD_fonctions_tests_specifications.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P07/P07_TP_fonctions_tests_specifications.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P07/P07_bareme_fonctions_tests_specifications.md` | Non | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P07/P07_corrige_fonctions_tests_specifications.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P07/P07_cours_fonctions_tests_specifications.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P07/P07_evaluation_fonctions_tests_specifications.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P07/P07_remediation_fonctions_tests_specifications.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P07/P07_tp_fonctions_tests_specifications.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P07/P07_trace_fonctions_tests_specifications.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P07/P07_version_amenagee_fonctions_tests_specifications.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P08/P08_TD_html_css_dom.md` | Oui | Oui | Non | Non | Oui | Première | NON |
| `03_progressions/supports/premiere/P08/P08_TD_http_get_post_formulaires.md` | Oui | Oui | Non | Non | Oui | Première | NON |
| `03_progressions/supports/premiere/P08/P08_TP_html_css_dom.md` | Oui | Non | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P08/P08_TP_http_get_post_formulaires.md` | Oui | Non | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P08/P08_bareme_web_http_dom_formulaires.md` | Non | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P08/P08_corrige_web_http_dom_formulaires.md` | Oui | Oui | Non | Non | Oui | Première | NON |
| `03_progressions/supports/premiere/P08/P08_cours_web_http_dom_formulaires.md` | Oui | Non | Oui | Réserve | Oui | Première | NON |
| `03_progressions/supports/premiere/P08/P08_evaluation_html_css_dom.md` | Oui | Non | Non | Non | Oui | Première | NON |
| `03_progressions/supports/premiere/P08/P08_evaluation_http_get_post_formulaires.md` | Oui | Non | Non | Non | Oui | Première | NON |
| `03_progressions/supports/premiere/P08/P08_remediation_web_http_dom_formulaires.md` | Réserve | Oui | Réserve | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P08/P08_trace_web_http_dom_formulaires.md` | Réserve | Oui | Réserve | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P08/P08_version_amenagee_web_http_dom_formulaires.md` | Réserve | Oui | Réserve | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P09/P09_TD_architecture_os_droits.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P09/P09_bareme_architecture_os_droits.md` | Non | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P09/P09_corrige_architecture_os_droits.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P09/P09_cours_architecture_os_droits.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P09/P09_evaluation_architecture_os_droits.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P09/P09_remediation_architecture_os_droits.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P09/P09_tp_architecture_os_droits.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P09/P09_trace_architecture_os_droits.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P09/P09_version_amenagee_architecture_os_droits.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P10/P10_TD_reseaux_protocoles_paquets.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P10/P10_bareme_reseaux_protocoles_paquets.md` | Non | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P10/P10_corrige_reseaux_protocoles_paquets.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P10/P10_cours_reseaux_protocoles_paquets.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P10/P10_evaluation_reseaux_protocoles_paquets.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P10/P10_remediation_reseaux_protocoles_paquets.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P10/P10_tp_reseaux_protocoles_paquets.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P10/P10_trace_reseaux_protocoles_paquets.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P10/P10_version_amenagee_reseaux_protocoles_paquets.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P13/P13_TD_dichotomie_glouton_knn.md` | Oui | Oui | Réserve | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P13/P13_bareme_dichotomie_glouton_knn.md` | Non | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P13/P13_corrige_dichotomie_glouton_knn.md` | Non | Oui | Oui | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P13/P13_cours_dichotomie_glouton_knn.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P13/P13_evaluation_dichotomie_glouton_knn.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P13/P13_remediation_dichotomie_glouton_knn.md` | Oui | Oui | Non | Non | Oui | Première | NON |
| `03_progressions/supports/premiere/P13/P13_tp_dichotomie_glouton_knn.md` | Oui | Oui | Non | Non | Oui | Première | NON |
| `03_progressions/supports/premiere/P13/P13_trace_dichotomie_glouton_knn.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P13/P13_version_amenagee_dichotomie_glouton_knn.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P14/P14_TD_synthese_projet_oral.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P14/P14_bareme_synthese_projet_oral.md` | Non | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P14/P14_corrige_synthese_projet_oral.md` | Oui | Oui | Oui | Réserve | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P14/P14_cours_synthese_projet_oral.md` | Oui | Oui | Oui | Réserve | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P14/P14_evaluation_synthese_projet_oral.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P14/P14_remediation_synthese_projet_oral.md` | Oui | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P14/P14_tp_synthese_projet_oral.md` | Oui | Oui | Non | Oui | Oui | Première | NON |
| `03_progressions/supports/premiere/P14/P14_trace_synthese_projet_oral.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/premiere/P14/P14_version_amenagee_synthese_projet_oral.md` | Réserve | Oui | Oui | Oui | Oui | Première | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T00/T00_bareme_diagnostic_tests.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T00/T00_corrige_diagnostic_tests.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T00/T00_cours_diagnostic_tests.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T00/T00_evaluation_diagnostic_tests.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T00/T00_remediation_diagnostic_tests.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T00/T00_td_diagnostic_tests.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T00/T00_tp_diagnostic_tests.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T00/T00_trace_diagnostic_tests.md` | Réserve | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T00/T00_version_amenagee_diagnostic_tests.md` | Réserve | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T01/T01_bareme_interfaces_structures.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T01/T01_corrige_interface_implementation_complement.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T01/T01_corrige_interfaces_structures.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T01/T01_cours_interface_implementation_complement.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T01/T01_cours_interfaces_structures.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T01/T01_evaluation_interface_implementation_complement.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T01/T01_evaluation_interfaces_structures.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T01/T01_remediation_interfaces_structures.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T01/T01_td_interface_implementation_complement.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T01/T01_td_interfaces_structures.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T01/T01_tp_interface_implementation_complement.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T01/T01_tp_interfaces_structures.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T01/T01_trace_interface_implementation_complement.md` | Réserve | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T01/T01_trace_interfaces_structures.md` | Réserve | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T01/T01_version_amenagee_interfaces_structures.md` | Réserve | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T03/T03_bareme_piles_files_dictionnaires.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T03/T03_corrige_piles_files_dictionnaires.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T03/T03_corrige_recherche_liste_dictionnaire.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T03/T03_cours_piles_files_dictionnaires.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T03/T03_cours_recherche_liste_dictionnaire.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T03/T03_evaluation_piles_files_dictionnaires.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T03/T03_evaluation_recherche_liste_dictionnaire.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T03/T03_remediation_piles_files_dictionnaires.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T03/T03_td_piles_files_dictionnaires.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T03/T03_td_recherche_liste_dictionnaire.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T03/T03_tp_piles_files_dictionnaires.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T03/T03_tp_recherche_liste_dictionnaire.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T03/T03_trace_piles_files_dictionnaires.md` | Réserve | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T03/T03_trace_recherche_liste_dictionnaire.md` | Réserve | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T03/T03_version_amenagee_piles_files_dictionnaires.md` | Réserve | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T04/T04_bareme_recursivite.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T04/T04_corrige_recursivite.md` | Oui | Oui | Oui | Réserve | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T04/T04_cours_recursivite.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T04/T04_evaluation_recursivite.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T04/T04_remediation_recursivite.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T04/T04_td_recursivite.md` | Oui | Oui | Non | Réserve | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T04/T04_tp_recursivite.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T04/T04_trace_recursivite.md` | Réserve | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T04/T04_version_amenagee_recursivite.md` | Réserve | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T05/T05_bareme_arbres_binaires.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T05/T05_corrige_arbres_binaires.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T05/T05_corrige_arbres_mesures_parcours_complement.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T05/T05_cours_arbres_binaires.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T05/T05_cours_arbres_mesures_parcours_complement.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T05/T05_evaluation_arbres_binaires.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T05/T05_evaluation_arbres_mesures_parcours_complement.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T05/T05_remediation_arbres_binaires.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T05/T05_td_arbres_binaires.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T05/T05_td_arbres_mesures_parcours_complement.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T05/T05_tp_arbres_binaires.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T05/T05_tp_arbres_mesures_parcours_complement.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T05/T05_trace_arbres_binaires.md` | Réserve | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T05/T05_trace_arbres_mesures_parcours_complement.md` | Réserve | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T05/T05_version_amenagee_arbres_binaires.md` | Réserve | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T07/T07_TD_graphes_modelisation_listes_matrices.md` | Oui | Oui | Non | Non | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T07/T07_TP_graphes_modelisation_listes_matrices.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T07/T07_bareme_graphes_modelisation_listes_matrices.md` | Non | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T07/T07_corrige_graphes_modelisation_listes_matrices.md` | Oui | Oui | Non | Non | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T07/T07_cours_graphes_modelisation_listes_matrices.md` | Oui | Oui | Non | Non | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T07/T07_evaluation_graphes_modelisation_listes_matrices.md` | Oui | Oui | Non | Non | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T07/T07_remediation_graphes_modelisation_listes_matrices.md` | Réserve | Oui | Réserve | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T07/T07_tp_graphes_modelisation_listes_matrices.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T07/T07_trace_graphes_modelisation_listes_matrices.md` | Réserve | Oui | Réserve | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T07/T07_version_amenagee_graphes_modelisation_listes_matrices.md` | Réserve | Oui | Réserve | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T09/T09_TD_bases_relationnelles_cles_contraintes.md` | Oui | Oui | Non | Non | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T09/T09_bareme_bases_relationnelles_cles_contraintes.md` | Non | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T09/T09_corrige_bases_relationnelles_cles_contraintes.md` | Oui | Oui | Non | Non | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T09/T09_cours_bases_relationnelles_cles_contraintes.md` | Oui | Oui | Non | Non | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T09/T09_evaluation_bases_relationnelles_cles_contraintes.md` | Oui | Oui | Non | Non | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T09/T09_remediation_bases_relationnelles_cles_contraintes.md` | Réserve | Oui | Réserve | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T09/T09_tp_bases_relationnelles_cles_contraintes.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T09/T09_trace_bases_relationnelles_cles_contraintes.md` | Réserve | Oui | Réserve | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T09/T09_version_amenagee_bases_relationnelles_cles_contraintes.md` | Réserve | Oui | Réserve | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T10/T10_TD_sql_insert_update_delete.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T10/T10_TD_sql_select_where_join.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T10/T10_bareme_sql_select_where_join.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T10/T10_corrige_sql_select_where_join.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T10/T10_cours_sql_select_where_join.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T10/T10_evaluation_sql_insert_update_delete.md` | Oui | Non | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T10/T10_evaluation_sql_select_where_join.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T10/T10_remediation_sql_select_where_join.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T10/T10_tp_sql_select_where_join.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T10/T10_trace_sql_select_where_join.md` | Réserve | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T10/T10_version_amenagee_sql_select_where_join.md` | Réserve | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T14/T14_TD_modularite_api_paradigmes_bugs.md` | Oui | Oui | Non | Non | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T14/T14_bareme_modularite_api_paradigmes_bugs.md` | Non | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T14/T14_corrige_modularite_api_paradigmes_bugs.md` | Oui | Oui | Non | Non | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T14/T14_cours_modularite_api_paradigmes_bugs.md` | Oui | Oui | Non | Non | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T14/T14_evaluation_modularite_api_paradigmes_bugs.md` | Oui | Oui | Non | Non | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T14/T14_remediation_modularite_api_paradigmes_bugs.md` | Réserve | Oui | Réserve | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T14/T14_tp_modularite_api_paradigmes_bugs.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T14/T14_trace_modularite_api_paradigmes_bugs.md` | Réserve | Oui | Réserve | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T14/T14_version_amenagee_modularite_api_paradigmes_bugs.md` | Réserve | Oui | Réserve | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T17/T17_TD_programmation_dynamique.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T17/T17_bareme_programmation_dynamique.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T17/T17_corrige_programmation_dynamique.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T17/T17_cours_programmation_dynamique.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T17/T17_evaluation_programmation_dynamique.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T17/T17_remediation_programmation_dynamique.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T17/T17_tp_programmation_dynamique.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T17/T17_trace_programmation_dynamique.md` | Réserve | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T17/T17_version_amenagee_programmation_dynamique.md` | Réserve | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T19/T19_TD_bac_pratique_grand_oral_projet.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T19/T19_bareme_bac_pratique_grand_oral_projet.md` | Non | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T19/T19_corrige_bac_pratique_grand_oral_projet.md` | Oui | Oui | Oui | Réserve | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T19/T19_cours_bac_pratique_grand_oral_projet.md` | Oui | Oui | Oui | Réserve | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T19/T19_evaluation_bac_pratique_grand_oral_projet.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T19/T19_remediation_bac_pratique_grand_oral_projet.md` | Oui | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T19/T19_tp_bac_pratique_grand_oral_projet.md` | Oui | Oui | Non | Oui | Oui | Terminale | NON |
| `03_progressions/supports/terminale/T19/T19_trace_bac_pratique_grand_oral_projet.md` | Réserve | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `03_progressions/supports/terminale/T19/T19_version_amenagee_bac_pratique_grand_oral_projet.md` | Réserve | Oui | Oui | Oui | Oui | Terminale | EXPLOITABLE-AVEC-RÉSERVES |
| `docs/promotion/dossier_revue_lead_v4.md` | Oui | Oui | Réserve | Réserve | Oui | Première + Terminale | EXPLOITABLE-AVEC-RÉSERVES |

## 4. GRILLE DOSSIER v4

| Fiche | Q1 | Q2 | Q3 | Observation |
|---|---|---|---|---|
| P-ALGO-03 | Oui | Oui | Oui | Ancres exactes ; cours, exercice 9 et corrigé enseignent, entraînent et corrigent le k-NN. |
| P-ALGO-04 | Oui | Oui | Oui | Variant correct V = droite − gauche + 1 ; traces 37, 23 et 38 recalculées. |
| P-ALGO-05 | Oui | Oui | Oui | Exemple glouton et contre-exemple de blocage avec représentation alternative cohérents. |
| P-IHM-03B | Oui | Oui | Oui | La fiche pointe le TD html_css_dom corrigé ; Domain/Path et stockage client/serveur sont effectivement traités. |
| T-LANG-05 | Oui | Non | Non | Practice et correction sont valides ; la preuve course ne porte pas sur les causes typiques de bugs. Verdict humain : 2/3. |
| T-STRUCT-05C | Oui | Non | Non | Exercise 3bis et correction valides ; la preuve course porte sur traduction/conversion/coût, pas sur l’implémentation. Verdict humain : 2/3. |
| T-LANG-04A | Oui | Oui | Oui | Partial 1/3 maintenu comme dette connue et décision lead pendante ; aucune promotion n’est proposée ici. |

Recomptage indépendant des JSON non adversariaux : full 113, partial 1, absent 0. Le résumé exécutif 113/1/0 est arithmétiquement exact ; ce comptage de présences ne remplace pas les contestations de substance ci-dessus.

## 5. SONDAGE VERDICTS

| Capacité | Décision | Motif |
|---|---|---|
| P-HIST-01 | contresigné | Frise, ordonnancement et association événement-protagoniste présents dans les trois rôles ; réserves scientifiques séparées en Axe 3. |
| P-LANG-01 | contresigné | Le contexte de l’ancre de cours présente affectation, chaîne, condition et fonction ; entraînement et correction sont concrets. |
| P-ARCH-01B | contresigné | Jeu d’instructions, trace CO/registres/mémoire et correction à quatre étapes répondent au libellé. |
| P-IHM-04C | contresigné | GET/POST/HTTPS sont comparés puis appliqués à quatre situations de confidentialité, avec correction correspondante. |
| P-ALGO-01A | contesté | La preuve d’entraînement calcule un indice mais ne fait pas écrire l’algorithme demandé. |
| T-BDD-02 | contesté | Course valide, mais practice/correction portent sur l’intégrité référentielle, pas sur les services du SGBD. |
| T-STRUCT-04B | contresigné | Taille, hauteur et feuilles sont définies, calculées sur un arbre, puis corrigées avec résultats vérifiables. |
| T-LANG-03C | contesté | Les trois preuves portent sur choix de paradigme/type chaîne, non sur création et documentation d’un module. |
| T-ALGO-03 | contesté | La preuve retenue ne demande que de couper une liste ; elle ne fait pas écrire l’algorithme diviser-pour-régner complet. |
| T-HIST-01B | contresigné | Les trois rôles font analyser quatre périodes et la nuance GPU/TPU ; l’exactitude de deux formulations historiques reste à vérifier séparément. |

## 6. COUVERTURE

### Axe 1

- Vérifié : 232 documents Markdown canoniques (9 P13 + 223 phase K) et le dossier v4, soit 233 lignes de grille.
- Méthode : lecture des métadonnées et titres, contrôle des sections par type, comptage exercices/questions/corrigés, résolution des références de fichiers, scan des réponses intégrées, contrôle des barèmes et lectures approfondies ciblées.
- Sain : métadonnées YAML lisibles ; les types attendus sont présents ; aucun fichier clé demandé ne manque ; les remédiations de forme riche contiennent diagnostic, activité corrective et critère de sortie.

### Axe 2

- Vérifié : chaînes complètes P13, P08, T07, T09 et T14.
- Méthode : matrice capacité officielle → cours → TD/TP → évaluation → barème → corrigé → remédiation/version aménagée.
- Sain : P13 enseigne correctement les trois algorithmes dans le cours et le TD ; l’exercice 3bis de T07 et l’exercice 6 de T14 constituent des maillons substantiels réutilisables.

### Axe 3

- Vérifié : dichotomie 37/23/38, sommes gloutonnes, cinq distances et votes k-NN, récursivité/TCO, cookies Domain/Path, localStorage/origine, HTTPS et GET/POST, SGBD, schéma/instance/intégrité, repères historiques P14/T19.
- Méthode : recalcul manuel des traces et distances, lecture du code Python cité, confrontation au référentiel YAML et recherche externe tentée pour les points historiques.
- Sain : V = droite − gauche + 1 et les traces 6→3, 6→3→1, 6→3→1→0 sont exactes ; les distances k-NN et les votes sont exacts ; le contre-exemple glouton distingue un blocage malgré une représentation existante ; cookies Domain/Path et localStorage par origine sont explicitement enseignés.

### Axe 4

- Vérifié : sept fiches du dossier v4, ancres, citations et sources canoniques.
- Méthode : ouverture de chaque ancre, lecture du contexte, comparaison au libellé YAML et contre-jugement du nombre de rôles substantiels.
- Sain : cinq fiches conservent leur verdict ; le résumé 113/1/0 correspond au recomptage JSON.

### Axe 5

- Vérifié : dix capacités hors dossier, cinq de Première et cinq de Terminale, couvrant histoire, langage, algorithmique, Web, architecture, BDD et structures.
- Méthode : lecture du JSON, puis des trois sources aux ancres annoncées ; aucune extrapolation statistique au reste des 114 verdicts.
- Sain : six verdicts sont contresignés ; quatre sont contestés avec motif précis.

### Axe 6

- Vérifié : les huit fichiers TeX de latex/packs/premiere/P13, comparés aux neuf Markdown canoniques.
- Méthode : comparaison données, résultats, consignes, exercices 1 à 9, corrigés, barèmes et séparation élève/professeur ; compilation non jugée.
- Sain : cours, fiche méthode, évaluation sans réponses, aides, trace et corrigé professeur reprennent correctement les données et résultats scientifiques de P13.

## 7. LIMITES

- Contexte Git de départ : branche fix/wdt-bis-guard-refinements, HEAD 3a5cb333960e6b36ebf76e02af2f55f4c1480a28, worktree propre.
- Le module demandé scripts.check_answer_capacity_coherence est absent. Les remplaçants disponibles ont été exécutés : check_question_capacity_alignment PASS (4 questions), check_sequence_capacity_alignment PASS (10 fichiers), check_sequence_pedagogical_coherence PASS (35 séquences) et check_corrected_answers_are_concrete PASS (749 blocs). Leur périmètre limité explique qu’ils ne prouvent pas la substance.
- check_substance_anchors PASS (114 verdicts), check_contract_substance_quality PASS (35 contrats riches), check_status_promotion_guard PASS et les contrôles audit-core visibles avant les tests Python sont passés.
- pytest a collecté 445 tests mais n’a pas produit de résumé avant l’interruption de la fenêtre d’exécution. scripts.run_python_tests a été borné à 20 secondes et a quitté avec le code 124 ; aucun succès global des tests n’est revendiqué.
- make audit-core a régénéré coverage.md, coverage_sources.md, les matrices et dix index, mais ces sorties étaient identiques à Git et ne subsistent pas comme modifications. La cible n’a pas atteint de résumé après scripts.run_python_tests.
- La recherche institutionnelle externe sur ARPANET/NPL et EDVAC n’a pas retourné de contenu exploitable dans l’environnement ; RVW-020 reste donc SUSPECTÉ.
- La grille exhaustive combine contrôles mécaniques sur les 233 documents et lecture humaine approfondie sur les cinq chaînes imposées. « Correct = Oui » hors ciblage scientifique signifie « aucune erreur trouvée par les contrôles effectués », non une validation scientifique exhaustive.
- Les élisions manquantes des corrigés legacy, le gate de fraîcheur md↔tex prévu post-flip, T-LANG-04A partial et la normalisation des backticks du checker de diversité sont des dettes connues ; elles ne sont pas recomptées comme anomalies nouvelles.
- Aucun contenu, statut, verdict, projection LaTeX, manifeste ou fichier de couverture n’a été corrigé par cette recette. La décision finale et toute promotion restent du ressort du lead humain.

BLOCKER: validation impossible pour cette ressource.
Raison : la suite complète de 445 tests et scripts.run_python_tests n’ont pas atteint leur résumé dans la fenêtre d’exécution ; le code 124 constate un délai, pas un succès ni un échec fonctionnel.
Action nécessaire : relancer les deux suites sans limite courte et archiver leur résumé complet avant signature.

BLOCKER: validation impossible pour cette ressource.
Raison : les attributions historiques ARPANET/NPL et ENIAC/EDVAC de RVW-020 n’ont pas pu être confrontées à une source institutionnelle externe accessible.
Action nécessaire : revue humaine avec sources institutionnelles datées avant toute correction ou publication de ces formulations.
