# Programme d'enrichissement — regime de croisiere post-flip

## Standard de reference

Le PANTHEON de la revue (fiches T05 arbres, P11 parcours, T09 bases relationnelles)
sert de reference qualitative pour toute production future. Chaque lot respecte le
pipeline integral : production -> gates -> juge -> echantillon lead.

## Regle d'execution

Tout enrichissement suit le cycle :
1. Production du contenu (cours/TD/TP/eval/corrige/bareme)
2. Passage des gates automatiques (audit-core + CI)
3. Jugement de substance (judge_campaign --force)
4. Echantillon lead (revue humaine sur les verdicts)

## Lots d'enrichissement

### E1 — Separation eleve/professeur (fuite de corriges)
- **Perimetre** : P00, P02, P03, P04, P07, P08, P09, P10, P13, P14, T00, T01, T03, T04, T05, T07, T09, T10, T14, T17, T19 (22 evaluations sur 29, 59 TD/TP)
- **Impact eleve** : les eleves recoivent actuellement les reponses et corriges dans les sujets distribues, ce qui annule la valeur formative et sommative de chaque activite
- **Mini-plan** :
  1. Generer des variantes eleve sans sections « Reponse attendue » ni « Corrige » pour tous les TD, TP et evaluations (RVW-001, RVW-030)
  2. Conserver les solutions exclusivement dans les fichiers corriges professeur
  3. Ajouter un controle automatique (gate) verifiant l'absence de motifs solution dans les artefacts eleve
  4. Appliquer le meme traitement aux projections LaTeX (RVW-027, RVW-028)
  5. Valider par echantillon lead sur cinq sequences representatives

### E2 — Reconstruction de la chaine P08 Web/HTTP/DOM/formulaires
- **Perimetre** : P08 (tous les fichiers : cours, TD, TP, evaluation, bareme, corrige)
- **Impact eleve** : la sequence Web est actuellement inutilisable en l'etat — references brisees, contenus dupliques, capacites non evaluees, erreurs scientifiques
- **Mini-plan** :
  1. Corriger les references de fichiers (TD/TP/evaluation inexistants, RVW-002)
  2. Dedupliquer les deux TP identiques html_css_dom et http_get_post_formulaires (RVW-003)
  3. Reecrire les exercices 5 et 6 du TD depuis les libelles officiels P-IHM-03B/03C (RVW-010)
  4. Completer l'evaluation avec les cinq capacites manquantes ou reduire les metadonnees (RVW-011)
  5. Corriger les imprecisions scientifiques : « origine » vs « domaine » pour localStorage, limites GET/POST (RVW-017, RVW-018)

### E3 — Reconstruction de la chaine T14 modularite/API/paradigmes/bugs
- **Perimetre** : T14 (cours, TD, evaluation, bareme, corrige)
- **Impact eleve** : les taches sont affectees aux mauvais libelles de capacite et deux capacites annoncees ne sont pas evaluees, rendant la sequence inutile pour la certification
- **Mini-plan** :
  1. Reconstruire les exemples et exercices du cours a partir des libelles YAML T-LANG-03A/03B/03C/04A (RVW-014)
  2. Ajouter les questions d'evaluation pour T-LANG-04B et T-LANG-05 ou reduire les metadonnees (RVW-015)
  3. Produire les preuves de substance alignees pour T-LANG-03C (creation et documentation de module, RVW-024)
  4. Fournir une preuve de cours portant sur les causes typiques de bugs pour T-LANG-05 (RVW-021)
  5. Rejuger l'ensemble via judge_campaign --force

### E4 — Reconstruction de la chaine T07 graphes
- **Perimetre** : T07 (cours, TD, evaluation, bareme, corrige)
- **Impact eleve** : les capacites T-STRUCT-05C et 05D sont desynchronisees entre methode, resultat et capacite ; l'eleve ne peut pas construire de competence fiable sur les representations de graphes
- **Mini-plan** :
  1. Refaire la chaine cours/TD/evaluation/bareme/corrige depuis les quatre libelles officiels T-STRUCT-05A a 05D (RVW-012)
  2. Conserver l'exercice 3bis comme point de depart pour 05C (implementation par listes)
  3. Fournir une preuve de cours d'implementation (pas seulement traduction/conversion) pour T-STRUCT-05C (RVW-022)
  4. Passer les gates et rejuger

### E5 — Reconstruction de la chaine T09 bases relationnelles
- **Perimetre** : T09 (evaluation, corrige, bareme, cours)
- **Impact eleve** : trois reponses d'evaluation sont decalees par rapport aux questions posees ; l'eleve qui revise avec le corrige apprend les mauvaises associations
- **Mini-plan** :
  1. Realigner question, capacite, reponse, bareme et corrige pour les quatre questions de l'evaluation (RVW-013)
  2. Tester la chaine avec une matrice question->production attendue
  3. Corriger l'exemple Redis dans le cours : distinguer SGBD relationnel et magasin cle-valeur (RVW-019)
  4. Produire une activite/correction sur les services du SGBD (persistance, concurrence, securite) pour T-BDD-02 (RVW-023)

### E6 — Reconstruction de la chaine P13 dichotomie/glouton/k-NN
- **Perimetre** : P13 (TD, TP, corrige, remediation, bareme, projections LaTeX)
- **Impact eleve** : le corrige du TP repond a une mauvaise question, la remediation rattache a une mauvaise capacite et le corrige separe manque de valeurs chiffrees
- **Mini-plan** :
  1. Realigner le corrige TP question par question sur le travail demande (RVW-007)
  2. Corriger le rattachement pedagogique de la remediation : dichotomie releve de P-ALGO-04, pas P-ALGO-03 (RVW-008)
  3. Ajouter les cinq distances calculees et leur ordre au corrige canonique (RVW-009)
  4. Harmoniser le canon Markdown et la projection TeX pour la Q3 (RVW-029)
  5. Recompter les exercices et ajuster le bareme pour inclure l'exercice 9 (RVW-004)

### E7 — Alignement des baremes et compteurs d'exercices
- **Perimetre** : P04, P07, P09, P10, P14, T07, T19 (toutes les evaluations et baremes concernes)
- **Impact eleve** : des exercices ou questions existent dans les sujets mais n'ont pas de points attribues, ce qui cree de l'ambiguite sur la notation
- **Mini-plan** :
  1. Recompter chaque TD depuis ses titres et attribuer explicitement les points aux exercices ajoutes (RVW-004)
  2. Corriger le bareme P04-complement : cinq questions notees avec total coherent de 20 points (RVW-005)
  3. Aligner la table P02 sur la ventilation des points annoncee par les titres (RVW-006)
  4. Verifier tous les baremes du perimetre avec un controle somme = 20

### E8 — Preuves de substance pour verdicts contestes
- **Perimetre** : capacites P-ALGO-01A, T-BDD-02, T-LANG-03C, T-ALGO-03
- **Impact eleve** : quatre capacites ont des verdicts 3/3 qui ne resistent pas a la lecture substantielle ; les exercices ne font pas produire ce que le libelle exige
- **Mini-plan** :
  1. P-ALGO-01A : remplacer la preuve d'entrainement par une ecriture de pseudo-code/Python et une correction executable (RVW-026)
  2. T-ALGO-03 : ajouter une production algorithmique complete diviser-pour-regner avec correction (RVW-025)
  3. T-LANG-03C : produire trois preuves sur creation de module, interface/import et documentation (RVW-024)
  4. T-BDD-02 : fournir une activite/correction sur les services reellement listes dans le cours (RVW-023)
  5. Rejuger les quatre capacites et soumettre a l'echantillon lead

### E9 — Corrections scientifiques de precision
- **Perimetre** : T04 recursivite, P08 cours Web, T09 cours BDD, T19 reperes historiques
- **Impact eleve** : des formulations scientifiquement inexactes ou contestables sont enseignees comme des faits etablis
- **Mini-plan** :
  1. T04 : expliquer que l'addition reste en attente sur la pile au lieu de justifier par TCO un appel non terminal (RVW-016)
  2. P08 : remplacer « domaine » par « origine » pour localStorage et reformuler les limites GET/POST comme ordres de grandeur (RVW-017, RVW-018)
  3. T09 : qualifier Redis et ses modes de persistance au lieu de presenter l'absence de persistance comme absolue (RVW-019)
  4. T19 : faire verifier par une source museale/institutionnelle l'anteriorite NPL/ARPANET et la nature d'EDVAC (RVW-020)

### E10 — Gate de fraicheur Markdown/LaTeX et deblocage des tests
- **Perimetre** : infrastructure (gates, CI, projections LaTeX)
- **Impact eleve** : sans gate de fraicheur, les corrections Markdown ne se propagent pas aux projections LaTeX distribuees aux eleves ; sans suite de tests complete, aucune regression n'est detectee
- **Mini-plan** :
  1. Implementer le gate de fraicheur md<->tex prevu post-flip (dette connue du rapport)
  2. Relancer la suite complete de 445 tests sans limite de temps et archiver le resume (BLOCKER du rapport)
  3. Corriger le code 124 de scripts.run_python_tests (timeout, pas echec fonctionnel)
  4. Ajouter un gate verifiant l'absence de motifs solution dans les artefacts eleve (complement de E1)
  5. Normaliser les backticks du checker de diversite (dette connue)

## Statut

POST-FLIP — regime de croisiere. Le rapport de revue reste dans
`reports/final_recipe_review_nsi.md` comme reference.
