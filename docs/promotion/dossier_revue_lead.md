# Dossier de revue lead — Promotion des verdicts de substance

## Résumé exécutif

- **Coverage** : 112 capacités à 3/3, 2 partials, 0 needs_content
- **Arc** : 86/2/26 (campagne initiale) → 112/2/0 (Phase K)
- **Coût API Phase K** : ~$4.05 (9 PRs, #78-#86)
- **Échantillon** : 18 verdicts stratifiés

### Ce que la signature promeut

needs_review → validated_pedagogy pour les 112 capacités à 3/3,
conformément à AGENTS.md §6 : validation humaine TRACÉE par échantillon.
Les 2 partials (P-IHM-03B, T-LANG-04A) sont présentés pour décision.

### Ce que la signature ne promet pas

La relecture exhaustive des 114 verdicts. L'échantillon (18 verdicts
stratifiés) est la méthode — pas un substitut à l'expertise du lead.

### Seed aléatoire : 42 (strate silencieuse)

---

## 1. T-BDD-02 — Identifier les services rendus par un SGBD relationnel.

- **Séquence** : campaign
- **Proofs** : 3/3
- **Justification** : Le cours enseigne les méthodes liées aux services d'un SGBD (contrôle de clés, détection d'anomalies). Le TD fait pratiquer via l'exercice 4 (contrainte de référence, suppression refusée). Le corrigé fournit la réponse attendue pour T-BDD-02. Le lien

### course
- **Fichier** : `03_progressions/supports/terminale/T09/T09_cours_bases_relationnelles_cles_contraintes.md`
- **Ancre** : `#savoir-faire-et-méthodes-opérationnelles`
- **Citation verdict** : - identifier la clé primaire d'une relation.
- contrôler une clé étrangère avec la table référencée.
- détecter une anomalie de redondance....

**Extrait réel** (`T09_cours_bases_relationnelles_cles_contraintes.md#savoir-faire-et-méthodes-opérationnelles`) :
```
### Savoir-faire et méthodes opérationnelles
- identifier la clé primaire d’une relation.
- contrôler une clé étrangère avec la table référencée.
- détecter une anomalie de redondance.

```

### practice
- **Fichier** : `03_progressions/supports/terminale/T09/T09_TD_bases_relationnelles_cles_contraintes.md`
- **Ancre** : `#exercice-4`
- **Citation verdict** : Consigne : repérer id_livre=9 absent ; traiter aussi `clé primaire nulle` si nécessaire.
- Réponse attendue : suppression d un livre emprunté refusée....

**Extrait réel** (`T09_TD_bases_relationnelles_cles_contraintes.md#exercice-4`) :
```
### Exercice 4
- Type : cas limite.
- Capacité officielle : T-BDD-02.
- Données : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`. ; 
- Consigne : repérer id_livre=9 absent ; traiter aussi `clé primaire nulle` si nécessaire.
- Réponse attendue : suppression d un livre emprunté refusée.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `clé primaire 
```

### correction
- **Fichier** : `03_progressions/supports/terminale/T09/T09_corrige_bases_relationnelles_cles_contraintes.md`
- **Ancre** : `#exercice-4`
- **Citation verdict** : - Réponse attendue : suppression d un livre emprunté refusée.
- Méthode : repérer id_livre=9 absent.
- Cas limite : clé primaire nulle....

**Extrait réel** (`T09_corrige_bases_relationnelles_cles_contraintes.md#exercice-4`) :
```
### Exercice 4
- Réponse attendue : suppression d un livre emprunté refusée.
- Méthode : repérer id_livre=9 absent.
- Cas limite : clé primaire nulle.
```

### Grille de relecture

- [ ] Q1 L'ancre pointe la bonne section
- [ ] Q2 L'extrait enseigne/exerce au niveau du libellé
- [ ] Q3 J'aurais rendu le même verdict
- Observation : ___

---

## 2. T-LANG-02B — Analyser le fonctionnement d'un programme récursif.

- **Séquence** : campaign
- **Proofs** : 3/3
- **Justification** : Le cours enseigne explicitement la méthode d'analyse d'un programme récursif (T-LANG-02B) avec trace d'appels et variant. Le TD fait pratiquer l'analyse sur une fonction concrète. Le corrigé professeur fournit la correction complète avec méthode et e

### course
- **Fichier** : `03_progressions/supports/terminale/T04/T04_cours_recursivite.md`
- **Ancre** : `#méthode--analyser-un-appel-récursif`
- **Citation verdict** : Pour analyser le fonctionnement d'un programme récursif (T-LANG-02B) :

1. **Identifier le cas de base** : quelle condition arrête la récursion ?
2. **Tracer les appels** : suivre la pile d'appels ave...

**Extrait réel** (`T04_cours_recursivite.md#méthode--analyser-un-appel-récursif`) :
```
## Méthode — analyser un appel récursif

Pour analyser le fonctionnement d'un programme récursif (T-LANG-02B) :

1. **Identifier le cas de base** : quelle condition arrête la récursion ?
2. **Tracer les appels** : suivre la pile d'appels avec les valeurs d'arguments à chaque niveau. Exe
3. **Prouver la terminaison** : exhiber un variant (mesure entière positive strictement décroissante
4. **Compter les appels** : le nombre d'appels récursifs de `fact(n)` est `n`, celui de `somme(lst)`

### Exemple corrigé 4 - terminaison
- Donnée étudiée : `n` décroît vers 0.
- Méthode : montrer une mesure entière strictement décroissante.
- Résultat obtenu : preuve de terminaison.
- Contrôle : le cas limite « appel avec même argument » est vérifié séparément.
```

### practice
- **Fichier** : `03_progressions/supports/terminale/T04/T04_td_recursivite.md`
- **Ancre** : `#exercice-4`
- **Citation verdict** : Énoncé disciplinaire : soit la fonction `def decompte(n): print(n); return decompte(n - 1)`. (a) Tracer les 4 premiers appels pour `decompte(3)` en indiquant la valeur de `n` à chaque appel. (b) Ident...

**Extrait réel** (`T04_td_recursivite.md#exercice-4`) :
```
### Exercice 4
- Objectif travaillé : O4.
- Capacité officielle : T-LANG-02A, T-LANG-02B.
- Énoncé disciplinaire : soit la fonction `def decompte(n): print(n); return decompte(n - 1)`. (a) T
- Production attendue : trace `decompte(3)→n=3, decompte(2)→n=2, decompte(1)→n=1, decompte(0)→n=0` ;
- Contrainte de contrôle : corriger l’erreur « Ne pas traiter l’entrée vide. » ; vérifier que `decom
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
```

### correction
- **Fichier** : `03_progressions/supports/terminale/T04/T04_corrige_recursivite.md`
- **Ancre** : `#corrigé-exercice-4`
- **Citation verdict** : - Méthode : isoler l'erreur fréquente « Ne pas traiter l'entrée vide. » puis reprendre la procédure correcte.
- Résultat : preuve de terminaison.
- Contrôle : corriger l'erreur « Ne pas traiter l'entr...

**Extrait réel** (`T04_corrige_recursivite.md#corrigé-exercice-4`) :
```
### Corrigé exercice 4
- Méthode : isoler l’erreur fréquente « Ne pas traiter l’entrée vide. » puis reprendre la procédure 
- Résultat : preuve de terminaison.
- Contrôle : corriger l’erreur « Ne pas traiter l’entrée vide. ».
- Erreur traitée : EF4 - Ne pas traiter l’entrée vide.
```

### Grille de relecture

- [ ] Q1 L'ancre pointe la bonne section
- [ ] Q2 L'extrait enseigne/exerce au niveau du libellé
- [ ] Q3 J'aurais rendu le même verdict
- Observation : ___

---

## 3. P-HIST-01 — Situer dans le temps les principaux événements de l'histoire de l'informatique et leurs protagonistes.

- **Séquence** : campaign
- **Proofs** : 3/3
- **Justification** : Le cours fournit une frise chronologique structurée avec protagonistes (Turing, von Neumann, Berners-Lee…). L'exercice 9 du TD fait pratiquer l'ordonnancement et l'association événement-protagoniste. Le corrigé fournit la réponse complète avec la fri

### course
- **Fichier** : `03_progressions/supports/premiere/P14/P14_cours_synthese_projet_oral.md`
- **Ancre** : `#principaux-événements-de-lhistoire-de-linformatique`
- **Citation verdict** : | 1936 | Machine de Turing (modèle théorique de calcul) | Alan Turing | Fondation théorique : tout calcul est une suite d'opérations élémentaires sur une bande |...

**Extrait réel** (`P14_cours_synthese_projet_oral.md#principaux-événements-de-lhistoire-de-linformatique`) :
```
## Principaux événements de l'histoire de l'informatique

La capacité P-HIST-01 demande de situer dans le temps les principaux événements de l'histoire de l'i

### Frise chronologique structurée

| Date | Événement | Acteur(s) | Rupture technique |
|------|-----------|-----------|-------------------|
| 1936 | Machine de Turing (modèle théorique de calcul) | Alan Turing | Fondation théorique : tout c
| 1945 | Architecture von Neumann (programme stocké en mémoire) | John von Neumann | Le programme et
| 1946 | ENIAC (premier calculateur électronique généraliste) | John Mauchly, J. Presper Eckert | Pa
| 1958-59 | Circuit intégré (Kilby 1958, Noyce 1959) | Jack Kilby (Texas Instruments), Robert Noyce 
| 1971 | Microprocesseur Intel 4004 | Ted Hoff, Federico Faggin | Un processeur complet sur une seul
| 1977 | Micro-ordinateurs personnels : Apple II (Jobs, Wozniak), TRS-80 (Tandy), Commodore PET (Ped
| 1989 | Invention du World Wide Web | Tim Berners-Lee (CERN) | Hypertexte + HTTP + URL : l'informat
```

### practice
- **Fichier** : `03_progressions/supports/premiere/P14/P14_TD_synthese_projet_oral.md`
- **Ancre** : `#exercice-9`
- **Citation verdict** : Consigne : (9a) ordonner les événements suivants du plus ancien au plus récent : microprocesseur Intel 4004, machine de Turing, invention du Web, ENIAC, circuit intégré. (9b) Associer chaque événement...

**Extrait réel** (`P14_TD_synthese_projet_oral.md#exercice-9`) :
```
### Exercice 9
- Type : lecture/analyse.
- Capacité officielle : P-HIST-01.
- Données : frise chronologique de l'histoire de l'informatique : Turing 1936, von Neumann 1945, ENI
- Consigne : (9a) ordonner les événements suivants du plus ancien au plus récent : microprocesseur I
- Réponse attendue : (9a) Turing 1936 < ENIAC 1946 < circuit intégré 1958 < microprocesseur 1971 < W
- Critère de réussite : ordre chronologique correct, associations exactes, rupture von Neumann justi

```

### correction
- **Fichier** : `03_progressions/supports/premiere/P14/P14_corrige_synthese_projet_oral.md`
- **Ancre** : `#exercice-9`
- **Citation verdict** : Réponse attendue : frise ordonnée (Turing 1936, ENIAC 1946, CI 1958, i4004 1971, Web 1989), associations protagonistes, rupture von Neumann, distinction Internet/Web....

**Extrait réel** (`P14_corrige_synthese_projet_oral.md#exercice-9`) :
```
### Exercice 9
- Capacité mobilisée : P-HIST-01.
- Réponse attendue : frise ordonnée (Turing 1936, ENIAC 1946, CI 1958, i4004 1971, Web 1989), associ
- Méthode : classement chronologique, association événement-protagoniste, analyse rupture.
- Cas limite : ENIAC n'est pas le premier ordinateur (Colossus 1943, Z3 1941).

```

### Grille de relecture

- [ ] Q1 L'ancre pointe la bonne section
- [ ] Q2 L'extrait enseigne/exerce au niveau du libellé
- [ ] Q3 J'aurais rendu le même verdict
- Observation : ___

---

## 4. T-ALGO-01C — Parcourir un arbre en ordres infixe, préfixe ou suffixe.

- **Séquence** : campaign
- **Proofs** : 3/3
- **Justification** : Le cours enseigne les trois ordres de parcours (infixe, préfixe, suffixe) avec exemples. Le TP fait pratiquer le parcours infixe sur l'ABR donné. Le corrigé fournit la méthode et le résultat attendu pour le parcours infixe.

### course
- **Fichier** : `03_progressions/supports/terminale/T06/T06_cours_arbres_binaires_recherche.md`
- **Ancre** : `#méthode--parcours-en-profondeur-dun-arbre-t-algo-01c`
- **Citation verdict** : **Parcours infixe** (gauche, racine, droite) : `[1, 3, 6, 8, 10, 14]` — produit les clés dans l'ordre croissant pour un ABR.
- **Parcours préfixe** (racine, gauche, droite) : `[8, 3, 1, 6, 10, 14]` — ...

**Extrait réel** (`T06_cours_arbres_binaires_recherche.md#méthode--parcours-en-profondeur-dun-arbre-t-algo-01c`) :
```
### Méthode — parcours en profondeur d'un arbre (T-ALGO-01C)

Sur l'ABR `[8, 3, 10, 1, 6, 14]`, les trois ordres de parcours en profondeur donnent :

- **Parcours infixe** (gauche, racine, droite) : `[1, 3, 6, 8, 10, 14]` — produit les clés dans l'or
- **Parcours préfixe** (racine, gauche, droite) : `[8, 3, 1, 6, 10, 14]` — la racine apparaît en pre
- **Parcours suffixe** (gauche, droite, racine) : `[1, 6, 3, 14, 10, 8]` — la racine apparaît en der

Chacun est récursif : on applique le même parcours aux sous-arbres gauche et droit, puis on traite l

```

### practice
- **Fichier** : `03_progressions/supports/terminale/T06/T06_TP_arbres_binaires_recherche.md`
- **Ancre** : `#trace-attendue-détaillée`
- **Citation verdict** : Parcours infixe attendu (T-ALGO-01C) : `[1, 3, 6, 8, 10, 14]`....

**Extrait réel** (`T06_TP_arbres_binaires_recherche.md#trace-attendue-détaillée`) :
```
## Trace attendue détaillée
Insertion de la séquence `[8, 3, 10, 1, 6, 14]` :
1. `8` devient racine.
2. `3 < 8`, donc `3` devient fils gauche de `8`.
3. `10 > 8`, donc `10` devient fils droit de `8`.
4. `1 < 8` puis `1 < 3`, donc `1` devient fils gauche de `3`.
5. `6 < 8` puis `6 > 3`, donc `6` devient fils droit de `3`.
6. `14 > 8` puis `14 > 10`, donc `14` devient fils droit de `10`.

Parcours infixe attendu (T-ALGO-01C) : `[1, 3, 6, 8, 10, 14]`.

Recherche de `6` :
1. comparer `6` à `8` : descendre à gauche ;
2. comparer `6` à `3` : descendre à droite ;
3. comparer `6` à `6` : valeur trouvée.
```

### correction
- **Fichier** : `03_progressions/supports/terminale/T06/T06_corrige_arbres_binaires_recherche.md`
- **Ancre** : `#exercice-3`
- **Citation verdict** : Méthode : parcours infixe (gauche, racine, droite) — T-ALGO-01C....

**Extrait réel** (`T06_corrige_arbres_binaires_recherche.md#exercice-3`) :
```
### Exercice 3
- Réponse attendue : infixe -> 1,3,6,8,10,14.
- Méthode : parcours infixe (gauche, racine, droite) — T-ALGO-01C.
- Cas limite : arbre dégénéré.
```

### Grille de relecture

- [ ] Q1 L'ancre pointe la bonne section
- [ ] Q2 L'extrait enseigne/exerce au niveau du libellé
- [ ] Q3 J'aurais rendu le même verdict
- Observation : ___

---

## 5. T-STRUCT-05A — Modéliser des situations sous forme de graphes.

- **Séquence** : campaign
- **Proofs** : 3/3
- **Justification** : Le cours enseigne la modélisation par graphes (traduire une situation en sommets et arêtes), le TD fait pratiquer sur des arcs concrets avec la capacité T-STRUCT-05A, et le corrigé fournit la réponse attendue avec méthode et cas limite.

### course
- **Fichier** : `03_progressions/supports/terminale/T07/T07_cours_graphes_modelisation_listes_matrices.md`
- **Ancre** : `#savoir-faire-et-méthodes-opérationnelles`
- **Citation verdict** : - traduire une situation en sommets et arêtes.
- passer de la liste d'adjacence à la matrice.
- comparer le coût mémoire des deux représentations....

**Extrait réel** (`T07_cours_graphes_modelisation_listes_matrices.md#savoir-faire-et-méthodes-opérationnelles`) :
```
### Savoir-faire et méthodes opérationnelles
- traduire une situation en sommets et arêtes.
- passer de la liste d’adjacence à la matrice.
- comparer le coût mémoire des deux représentations.

```

### practice
- **Fichier** : `03_progressions/supports/terminale/T07/T07_TD_graphes_modelisation_listes_matrices.md`
- **Ancre** : `#exercice-1`
- **Citation verdict** : Consigne : lister voisins sortants ; traiter aussi `sommet isolé E` si nécessaire.
- Réponse attendue : A -> [B,C], B -> [D], C -> [D], D -> [B]....

**Extrait réel** (`T07_TD_graphes_modelisation_listes_matrices.md#exercice-1`) :
```
### Exercice 1
- Type : lecture/analyse.
- Capacité officielle : T-STRUCT-05A.
- Données : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`. ; jeu_exercice=alpha
- Consigne : lister voisins sortants ; traiter aussi `sommet isolé E` si nécessaire.
- Réponse attendue : A -> [B,C], B -> [D], C -> [D], D -> [B].
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `sommet isolé 
```

### correction
- **Fichier** : `03_progressions/supports/terminale/T07/T07_corrige_graphes_modelisation_listes_matrices.md`
- **Ancre** : `#exercice-1`
- **Citation verdict** : - Réponse attendue : A -> [B,C], B -> [D], C -> [D], D -> [B].
- Méthode : lister voisins sortants.
- Cas limite : sommet isolé E....

**Extrait réel** (`T07_corrige_graphes_modelisation_listes_matrices.md#exercice-1`) :
```
### Exercice 1
- Réponse attendue : A -> [B,C], B -> [D], C -> [D], D -> [B].
- Méthode : lister voisins sortants.
- Cas limite : sommet isolé E.
```

### Grille de relecture

- [ ] Q1 L'ancre pointe la bonne section
- [ ] Q2 L'extrait enseigne/exerce au niveau du libellé
- [ ] Q3 J'aurais rendu le même verdict
- Observation : ___

---

## 6. T-BDD-01B — Distinguer structure et contenu d'une base de données.

- **Séquence** : campaign
- **Proofs** : 3/3
- **Justification** : Le cours enseigne le vocabulaire schéma/instance/attribut, le TD fait pratiquer la vérification de la structure (clé primaire, clé étrangère) sur des données concrètes, et le corrigé fournit la réponse attendue pour la capacité T-BDD-01B.

### course
- **Fichier** : `03_progressions/supports/terminale/T09/T09_cours_bases_relationnelles_cles_contraintes.md`
- **Ancre** : `#savoir-disciplinaire`
- **Citation verdict** : Vocabulaire à maîtriser : relation, attribut, tuple, clé primaire, clé étrangère, contrainte, schéma, instance....

**Extrait réel** (`T09_cours_bases_relationnelles_cles_contraintes.md#savoir-disciplinaire`) :
```
### Savoir disciplinaire
- Vocabulaire à maîtriser : relation, attribut, tuple, clé primaire, clé étrangère, contrainte, sché
- Capacités reliées : T-BDD-01A, T-BDD-01B, T-BDD-01C, T-BDD-02.
- Le savoir attendu consiste à expliquer le rôle de chaque objet avant de l'utiliser dans un exercic

```

### practice
- **Fichier** : `03_progressions/supports/terminale/T09/T09_TD_bases_relationnelles_cles_contraintes.md`
- **Ancre** : `#exercice-2`
- **Citation verdict** : Consigne : vérifier unicité id_livre ; traiter aussi `doublon id_livre=1` si nécessaire....

**Extrait réel** (`T09_TD_bases_relationnelles_cles_contraintes.md#exercice-2`) :
```
### Exercice 2
- Type : production/écriture.
- Capacité officielle : T-BDD-01B.
- Données : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`. ; 
- Consigne : vérifier unicité id_livre ; traiter aussi `doublon id_livre=1` si nécessaire.
- Réponse attendue : Emprunt.id_livre référence Livre.id_livre.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `doublon id_li
```

### correction
- **Fichier** : `03_progressions/supports/terminale/T09/T09_corrige_bases_relationnelles_cles_contraintes.md`
- **Ancre** : `#exercice-2`
- **Citation verdict** : Réponse attendue : Emprunt.id_livre référence Livre.id_livre.
- Méthode : vérifier unicité id_livre.
- Cas limite : doublon id_livre=1....

**Extrait réel** (`T09_corrige_bases_relationnelles_cles_contraintes.md#exercice-2`) :
```
### Exercice 2
- Réponse attendue : Emprunt.id_livre référence Livre.id_livre.
- Méthode : vérifier unicité id_livre.
- Cas limite : doublon id_livre=1.
```

### Grille de relecture

- [ ] Q1 L'ancre pointe la bonne section
- [ ] Q2 L'extrait enseigne/exerce au niveau du libellé
- [ ] Q3 J'aurais rendu le même verdict
- Observation : ___

---

## 7. T-ALGO-04 — Utiliser la programmation dynamique pour écrire un algorithme.

- **Séquence** : campaign
- **Proofs** : 3/3
- **Justification** : Le cours enseigne la programmation dynamique (état, tabulation, récurrence), le TD fait pratiquer avec des consignes explicites sur dp[m], et le corrigé fournit les réponses attendues pour chaque exercice.

### course
- **Fichier** : `03_progressions/supports/terminale/T17/T17_cours_programmation_dynamique.md`
- **Ancre** : `#savoir-faire-et-méthodes-opérationnelles`
- **Citation verdict** : - définir l'état dp[i] avant la relation.
- remplir une table dans un ordre qui respecte les dépendances.
- comparer récursion naïve et tabulation....

**Extrait réel** (`T17_cours_programmation_dynamique.md#savoir-faire-et-méthodes-opérationnelles`) :
```
### Savoir-faire et méthodes opérationnelles
- définir l’état dp[i] avant la relation.
- remplir une table dans un ordre qui respecte les dépendances.
- comparer récursion naïve et tabulation.

```

### practice
- **Fichier** : `03_progressions/supports/terminale/T17/T17_TD_programmation_dynamique.md`
- **Ancre** : `#exercice-2`
- **Citation verdict** : - Consigne : écrire dp[m]=1+min(dp[m-p]) ; traiter aussi `montant impossible` si nécessaire.
- Réponse attendue : dp[11]=3 avec 5+5+1....

**Extrait réel** (`T17_TD_programmation_dynamique.md#exercice-2`) :
```
### Exercice 2
- Type : production/écriture.
- Capacité officielle : T-ALGO-04.
- Données : `pieces=[1,5,7], montant=11, dp[0]=0`. ; jeu_exercice=beta
- Consigne : écrire dp[m]=1+min(dp[m-p]) ; traiter aussi `montant impossible` si nécessaire.
- Réponse attendue : dp[11]=3 avec 5+5+1.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `montant impos
```

### correction
- **Fichier** : `03_progressions/supports/terminale/T17/T17_corrige_programmation_dynamique.md`
- **Ancre** : `#exercice-1`
- **Citation verdict** : - Réponse attendue : dp[6]=2 avec 5+1.
- Méthode : définir dp[m] coût minimal.
- Cas limite : montant 0....

**Extrait réel** (`T17_corrige_programmation_dynamique.md#exercice-1`) :
```
### Exercice 1
- Réponse attendue : dp[6]=2 avec 5+1.
- Méthode : définir dp[m] coût minimal.
- Cas limite : montant 0.
```

### Grille de relecture

- [ ] Q1 L'ancre pointe la bonne section
- [ ] Q2 L'extrait enseigne/exerce au niveau du libellé
- [ ] Q3 J'aurais rendu le même verdict
- Observation : ___

---

## 8. P-DATA-BASE-02A — Evaluer le nombre de bits nécessaires à l'écriture en base 2 d'un entier, d'une somme ou d'un produit.

- **Séquence** : campaign
- **Proofs** : 3/3
- **Justification** : Le cours enseigne la règle ⌊log₂(n)⌋+1 et la méthode par divisions successives. Le TD (exercice 9) fait pratiquer sur des entiers, sommes et produits. Le corrigé professeur fournit les réponses détaillées avec vérification par encadrement.

### course
- **Fichier** : `03_progressions/supports/premiere/P02/P02_cours_complement_booleens.md`
- **Ancre** : `#évaluer-le-nombre-de-bits-nécessaires-en-base-2`
- **Citation verdict** : Un entier naturel `n` (n ≥ 1) s'écrit en base 2 avec exactement `⌊log₂(n)⌋ + 1` bits. En pratique, on cherche la plus petite puissance de 2 strictement supérieure à `n`....

**Extrait réel** (`P02_cours_complement_booleens.md#évaluer-le-nombre-de-bits-nécessaires-en-base-2`) :
```
## Évaluer le nombre de bits nécessaires en base 2

La capacité P-DATA-BASE-02A demande d'évaluer le nombre de bits nécessaires à l'écriture en base 2 d

### Règle fondamentale

Un entier naturel `n` (n ≥ 1) s'écrit en base 2 avec exactement `⌊log₂(n)⌋ + 1` bits. En pratique, o

| Entier `n` | Écriture binaire | Nombre de bits |
|-----------|-----------------|---------------|
| 0 | `0` | 1 |
| 1 | `1` | 1 |
| 7 | `111` | 3 |
| 8 | `1000` | 4 |
| 255 | `11111111` | 8 |
```

### practice
- **Fichier** : `03_progressions/supports/premiere/P02/P02_td_complement_booleens.md`
- **Ancre** : `#exercice-9`
- **Citation verdict** : Combien de bits sont nécessaires pour écrire 200 en base 2 ? Justifier par la méthode des divisions successives....

**Extrait réel** (`P02_td_complement_booleens.md#exercice-9`) :
```
### Exercice 9
- Objectif travaillé : O1, O2, O3, O4.
- Capacité officielle : P-DATA-BASE-02A.
- Énoncé disciplinaire : évaluer le nombre de bits nécessaires à l’écriture en base 2 d’un entier, d
- Production attendue : 8 bits (200), 10 bits (1023), 11 bits (somme), 19 bits (produit), débordemen
- Contrainte de contrôle : vérifier chaque résultat par encadrement entre deux puissances de 2 consé
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.

```

### correction
- **Fichier** : `03_progressions/supports/premiere/P02/P02_corrige_complement_booleens.md`
- **Ancre** : `#corrigé-exercice-9--évaluer-le-nombre-de-bits-nécessaires-p-data-base-02a`
- **Citation verdict** : 200 nécessite **8 bits**. Méthode : 8 divisions successives par 2. Vérification : 2⁷ = 128 ≤ 200 < 256 = 2⁸....

**Extrait réel** (`P02_corrige_complement_booleens.md#corrigé-exercice-9--évaluer-le-nombre-de-bits-nécessaires-p-data-base-02a`) :
```
### Corrigé exercice 9 — Évaluer le nombre de bits nécessaires (P-DATA-BASE-02A)
- **9a.** 200 nécessite **8 bits**. Méthode : 8 divisions successives par 2. Vérification : 2⁷ = 128
- **9b.** Valeur maximale 1023. 2⁹ = 512 ≤ 1023 < 1024 = 2¹⁰. Il faut **10 bits**.
- **9c.** 500 nécessite **9 bits** (2⁸ = 256 ≤ 500 < 512 = 2⁹, donc ⌊log₂(500)⌋+1 = 9). 600 nécessit
- **9d.** Non : 255 + 255 = 510 nécessite 9 bits. Débordement sur 8 bits. Il faut au moins 9 bits.
- Contrôle : la règle « somme sur k+1 bits, produit sur p+q bits » est vérifiée sur chaque réponse.
- Erreur traitée : confondre le nombre de bits d'un entier avec sa valeur.

```

### Grille de relecture

- [ ] Q1 L'ancre pointe la bonne section
- [ ] Q2 L'extrait enseigne/exerce au niveau du libellé
- [ ] Q3 J'aurais rendu le même verdict
- Observation : ___

---

## 9. P-ARCH-01B — Dérouler l'exécution d'une séquence d'instructions simples de type langage machine.

- **Séquence** : campaign
- **Proofs** : 3/3
- **Justification** : Le cours enseigne le jeu d'instructions simplifié et la trace d'exécution avec exemple complet. L'exercice 9 du TD fait pratiquer le déroulement instruction par instruction. Le corrigé fournit la trace attendue et le cas d'inversion.

### course
- **Fichier** : `03_progressions/supports/premiere/P09/P09_cours_architecture_os_droits.md`
- **Ancre** : `#dérouler-lexécution-dinstructions-machine`
- **Citation verdict** : | `LOAD R, adresse` | Copie le contenu de la mémoire[adresse] dans le registre R |
| `STORE R, adresse` | Copie le contenu du registre R dans la mémoire[adresse] |
| `ADD R1, R2` | R1 ← R1 + R2 |
| `S...

**Extrait réel** (`P09_cours_architecture_os_droits.md#dérouler-lexécution-dinstructions-machine`) :
```
## Dérouler l'exécution d'instructions machine

La capacité P-ARCH-01B demande de dérouler l'exécution d'une séquence d'instructions simples de type

### Modèle simplifié

Un processeur possède :
- des **registres** (petites mémoires rapides, notés R0, R1, R2…) ;
- une **mémoire** (tableau de cases numérotées) ;
- un **compteur ordinal** (CO) qui indique l'adresse de la prochaine instruction.

### Jeu d'instructions simplifié

| Instruction | Effet |
|------------|-------|
```

### practice
- **Fichier** : `03_progressions/supports/premiere/P09/P09_TD_architecture_os_droits.md`
- **Ancre** : `#exercice-9`
- **Citation verdict** : Consigne : (9a) dérouler l'exécution instruction par instruction en construisant la trace (CO, instruction, R0, R1, mémoire[12]) ; (9b) donner la valeur finale de mémoire[12] ; (9c) que se passerait-i...

**Extrait réel** (`P09_TD_architecture_os_droits.md#exercice-9`) :
```
### Exercice 9
- Type : production/écriture.
- Capacité officielle : P-ARCH-01B.
- Données : mémoire initiale `[10]` = 12, `[11]` = 5, `[12]` = 0. Programme : `LOAD R0, [10] ; LOAD 
- Consigne : (9a) dérouler l'exécution instruction par instruction en construisant la trace (CO, ins
- Réponse attendue : (9a) trace 4 étapes ; (9b) mémoire[12] = 7 ; (9c) R0 contiendrait 5 et R1 conti
- Critère de réussite : trace complète avec valeurs correctes à chaque étape, cas d'inversion traité

```

### correction
- **Fichier** : `03_progressions/supports/premiere/P09/P09_corrige_architecture_os_droits.md`
- **Ancre** : `#exercice-9`
- **Citation verdict** : Réponse attendue : trace 4 étapes (LOAD R0=12, LOAD R1=5, SUB R0=7, STORE mémoire[12]=7). Inversion → R0=5, R1=12, résultat −7....

**Extrait réel** (`P09_corrige_architecture_os_droits.md#exercice-9`) :
```
### Exercice 9
- Capacité mobilisée : P-ARCH-01B.
- Réponse attendue : trace 4 étapes (LOAD R0=12, LOAD R1=5, SUB R0=7, STORE mémoire[12]=7). Inversio
- Méthode : dérouler instruction par instruction en mettant à jour registres et mémoire.
- Cas limite : valeurs égales → SUB donne 0.

```

### Grille de relecture

- [ ] Q1 L'ancre pointe la bonne section
- [ ] Q2 L'extrait enseigne/exerce au niveau du libellé
- [ ] Q3 J'aurais rendu le même verdict
- Observation : ___

---

## 10. P-ALGO-03 — Ecrire un algorithme qui prédit la classe d'un élément à partir de la classe majoritaire de ses k plus proches voisins.

- **Séquence** : campaign
- **Proofs** : 3/3
- **Justification** : Le cours enseigne explicitement l'algorithme k-NN avec implémentation Python et cas limites. Le TD fait pratiquer le calcul de distances, la sélection des k voisins et le vote majoritaire. Le corrigé fournit les réponses détaillées pour l'exercice 9.

### course
- **Fichier** : `03_progressions/supports/premiere/P13/P13_cours_dichotomie_glouton_knn.md`
- **Ancre** : `#algorithme-des-k-plus-proches-voisins`
- **Citation verdict** : La capacité P-ALGO-03 demande d'écrire un algorithme qui prédit la classe d'un élément à partir de la classe majoritaire de ses k plus proches voisins....

**Extrait réel** (`P13_cours_dichotomie_glouton_knn.md#algorithme-des-k-plus-proches-voisins`) :
```
## Algorithme des k plus proches voisins

La capacité P-ALGO-03 demande d'écrire un algorithme qui prédit la classe d'un élément à partir de l

### Principe

Soit un ensemble de points étiquetés (chaque point a des coordonnées et une classe connue). Pour pré

1. Calculer la **distance** entre le nouveau point et chaque point de l'ensemble.
2. Trier les points par distance croissante.
3. Sélectionner les **k plus proches** voisins.
4. La classe prédite est la **classe majoritaire** parmi ces k voisins.

### Exemple complet — classification de fleurs

```

### practice
- **Fichier** : `03_progressions/supports/premiere/P13/P13_TD_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-9`
- **Citation verdict** : Consigne : (9a) calculer la distance euclidienne entre le nouveau point et chaque point d'entraînement ; (9b) identifier les 3 plus proches voisins ; (9c) déterminer la classe prédite par vote majorit...

**Extrait réel** (`P13_TD_dichotomie_glouton_knn.md#exercice-9`) :
```
### Exercice 9
- Type : production/écriture.
- Capacité officielle : P-ALGO-03.
- Données : données d'entraînement = [(2, 3, "A"), (5, 4, "B"), (1, 1, "A"), (8, 7, "B"), (3, 2, "A"
- Consigne : (9a) calculer la distance euclidienne entre le nouveau point et chaque point d'entraîne
- Réponse attendue : distances calculées, 3 plus proches identifiés, classe prédite = "A", cas k=2 →
- Critère de réussite : distances correctes, tri vérifié, vote majoritaire explicite, cas d'égalité 

```

### correction
- **Fichier** : `03_progressions/supports/premiere/P13/P13_corrige_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-9`
- **Citation verdict** : Réponse attendue : distances calculées, 3 plus proches = A(3,2) B(5,4) A(2,3), vote A=2 B=1, classe "A"....

**Extrait réel** (`P13_corrige_dichotomie_glouton_knn.md#exercice-9`) :
```
### Exercice 9
- Capacité mobilisée : P-ALGO-03.
- Réponse attendue : distances calculées, 3 plus proches = A(3,2) B(5,4) A(2,3), vote A=2 B=1, class
- Méthode : distance euclidienne, tri, vote majoritaire.
- Cas limite : k=2 avec égalité de vote → résultat indéterminé.

```

### Grille de relecture

- [ ] Q1 L'ancre pointe la bonne section
- [ ] Q2 L'extrait enseigne/exerce au niveau du libellé
- [ ] Q3 J'aurais rendu le même verdict
- Observation : ___

---

## 11. T-HIST-01B — Identifier l'évolution des rôles relatifs des logiciels et des matériels.

- **Séquence** : campaign
- **Proofs** : 3/3
- **Justification** : Le cours expose explicitement l'évolution des rôles matériel/logiciel en 4 périodes historiques. L'exercice 10 du TD fait pratiquer cette analyse par période avec exemples concrets. Le corrigé fournit les réponses attendues incluant la nuance GPU/TPU

### course
- **Fichier** : `03_progressions/supports/terminale/T19/T19_cours_bac_pratique_grand_oral_projet.md`
- **Ancre** : `#évolution-des-rôles-matériel-et-logiciel-t-hist-01b`
- **Citation verdict** : L'histoire de l'informatique montre un transfert progressif de complexité du matériel vers le logiciel :

1. **Années 1940-1950 — le matériel est roi** : les premiers ordinateurs (ENIAC, EDVAC) sont c...

**Extrait réel** (`T19_cours_bac_pratique_grand_oral_projet.md#évolution-des-rôles-matériel-et-logiciel-t-hist-01b`) :
```
### Évolution des rôles matériel et logiciel (T-HIST-01B)

L'histoire de l'informatique montre un transfert progressif de complexité du matériel vers le logici

1. **Années 1940-1950 — le matériel est roi** : les premiers ordinateurs (ENIAC, EDVAC) sont câblés 

2. **Années 1960-1970 — naissance du logiciel** : les langages de haut niveau (FORTRAN 1957, COBOL 1

3. **Années 1980-1990 — le logiciel prend le pouvoir** : le matériel se standardise (IBM PC compatib

4. **Années 2000-2020 — le logiciel mange le monde** : le cloud computing virtualise le matériel. Le

```

### practice
- **Fichier** : `03_progressions/supports/terminale/T19/T19_TD_bac_pratique_grand_oral_projet.md`
- **Ancre** : `#exercice-10`
- **Citation verdict** : Consigne : (10a) pour chaque période, décrire en une phrase le rôle dominant (matériel ou logiciel). (10b) citer un exemple concret (produit, langage, système) pour chaque période. (10c) expliquer pou...

**Extrait réel** (`T19_TD_bac_pratique_grand_oral_projet.md#exercice-10`) :
```
### Exercice 10
- Type : production/écriture.
- Capacité officielle : T-HIST-01B.
- Données : quatre périodes — (A) 1940-1960 câblage, (B) 1960-1980 langages haut niveau, (C) 1980-20
- Consigne : (10a) pour chaque période, décrire en une phrase le rôle dominant (matériel ou logiciel
- Réponse attendue : (A) matériel dominant (ENIAC câblé), (B) naissance logiciel (C, Unix), (C) logi
- Critère de réussite : 4 périodes décrites avec exemple, nuance GPU/TPU présente.

```

### correction
- **Fichier** : `03_progressions/supports/terminale/T19/T19_corrige_bac_pratique_grand_oral_projet.md`
- **Ancre** : `#exercice-10`
- **Citation verdict** : Réponse attendue : 4 périodes (matériel dominant → logiciel → cloud/IA → nuance GPU/TPU).
- Méthode : analyse par période avec exemple concret.
- Cas limite : matériel spécialisé (GPU, TPU) nuance le ...

**Extrait réel** (`T19_corrige_bac_pratique_grand_oral_projet.md#exercice-10`) :
```
### Exercice 10
- Capacité mobilisée : T-HIST-01B.
- Réponse attendue : 4 périodes (matériel dominant → logiciel → cloud/IA → nuance GPU/TPU).
- Méthode : analyse par période avec exemple concret.
- Cas limite : matériel spécialisé (GPU, TPU) nuance le transfert matériel→logiciel.

```

### Grille de relecture

- [ ] Q1 L'ancre pointe la bonne section
- [ ] Q2 L'extrait enseigne/exerce au niveau du libellé
- [ ] Q3 J'aurais rendu le même verdict
- Observation : ___

---

## 12. P-ALGO-05 — Résoudre un problème grâce à un algorithme glouton.

- **Séquence** : campaign
- **Proofs** : 3/3
- **Justification** : Le cours présente la méthode gloutonne (prendre la plus grande pièce possible), le TD fait pratiquer l'algorithme glouton sur le problème du rendu de monnaie (exercice 3, capacité P-ALGO-05), et le corrigé fournit la réponse attendue. Les trois preuv

### course
- **Fichier** : `03_progressions/supports/premiere/P13/P13_cours_dichotomie_glouton_knn.md`
- **Ancre** : `#méthodes`
- **Citation verdict** : prendre la plus grande pièce possible....

**Extrait réel** (`P13_cours_dichotomie_glouton_knn.md#méthodes`) :
```
## Méthodes
- calculer milieu puis réduire intervalle.
- montrer que droite-gauche diminue.
- prendre la plus grande pièce possible.
- voter parmi k=3 voisins.

```

### practice
- **Fichier** : `03_progressions/supports/premiere/P13/P13_TD_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-3`
- **Citation verdict** : Consigne : prendre la plus grande pièce possible ; traiter aussi `égalité de vote` si nécessaire....

**Extrait réel** (`P13_TD_dichotomie_glouton_knn.md#exercice-3`) :
```
### Exercice 3
- Type : production/écriture.
- Capacité officielle : P-ALGO-05.
- Données : `tableau=[4,9,18,23,37,41], cible=37 ; pièces=[10,5,2,1], montant=28 ; voisins=[rouge:1.
- Consigne : prendre la plus grande pièce possible ; traiter aussi `égalité de vote` si nécessaire.
- Réponse attendue : rouge, bleu, rouge -> classe rouge.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `égalité de vo
```

### correction
- **Fichier** : `03_progressions/supports/premiere/P13/P13_corrige_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-3`
- **Citation verdict** : Réponse attendue : rouge, bleu, rouge -> classe rouge....

**Extrait réel** (`P13_corrige_dichotomie_glouton_knn.md#exercice-3`) :
```
### Exercice 3
- Réponse attendue : rouge, bleu, rouge -> classe rouge.
- Méthode : prendre la plus grande pièce possible.
- Cas limite : égalité de vote.
```

### Grille de relecture

- [ ] Q1 L'ancre pointe la bonne section
- [ ] Q2 L'extrait enseigne/exerce au niveau du libellé
- [ ] Q3 J'aurais rendu le même verdict
- Observation : ___

---

## 13. P-ALGO-01B — Ecrire un algorithme de recherche d'un extremum ou de calcul d'une moyenne.

- **Séquence** : campaign
- **Proofs** : 3/3
- **Justification** : Le cours enseigne les méthodes d'initialisation d'extremum et de test liste vide avant moyenne. Le TD fait pratiquer la recherche de maximum et le calcul de moyenne avec cas limites. Le corrigé fournit les réponses attendues pour chaque exercice lié 

### course
- **Fichier** : `03_progressions/supports/premiere/P11/P11_cours_parcours_recherche_extremum_moyenne.md`
- **Ancre** : `#méthodes`
- **Citation verdict** : - initialiser maximum à la première valeur.
- tester liste vide avant moyenne....

**Extrait réel** (`P11_cours_parcours_recherche_extremum_moyenne.md#méthodes`) :
```
## Méthodes
- parcourir avec indice.
- mémoriser le premier indice de 21.
- initialiser maximum à la première valeur.
- tester liste vide avant moyenne.

```

### practice
- **Fichier** : `03_progressions/supports/premiere/P11/P11_TD_parcours_recherche_extremum_moyenne.md`
- **Ancre** : `#exercice-2`
- **Citation verdict** : - Consigne : mémoriser le premier indice de 21 ; traiter aussi `cible absente` si nécessaire.
- Réponse attendue : maximum -> 24....

**Extrait réel** (`P11_TD_parcours_recherche_extremum_moyenne.md#exercice-2`) :
```
### Exercice 2
- Type : production/écriture.
- Capacité officielle : P-ALGO-01B.
- Données : `mesures=[18,21,17,24,21], cible=21, seuil=22`. ; jeu_exercice=beta
- Consigne : mémoriser le premier indice de 21 ; traiter aussi `cible absente` si nécessaire.
- Réponse attendue : maximum -> 24.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `cible absente
```

### correction
- **Fichier** : `03_progressions/supports/premiere/P11/P11_corrige_parcours_recherche_extremum_moyenne.md`
- **Ancre** : `#exercice-2`
- **Citation verdict** : - Réponse attendue : maximum -> 24.
- Méthode : mémoriser le premier indice de 21.
- Cas limite : cible absente....

**Extrait réel** (`P11_corrige_parcours_recherche_extremum_moyenne.md#exercice-2`) :
```
### Exercice 2
- Réponse attendue : maximum -> 24.
- Méthode : mémoriser le premier indice de 21.
- Cas limite : cible absente.
```

### Grille de relecture

- [ ] Q1 L'ancre pointe la bonne section
- [ ] Q2 L'extrait enseigne/exerce au niveau du libellé
- [ ] Q3 J'aurais rendu le même verdict
- Observation : ___

---

## 14. P-DATA-CONSTR-01 — Ecrire une fonction renvoyant un p-uplet de valeurs.

- **Séquence** : campaign
- **Proofs** : 3/3
- **Justification** : Le cours complément enseigne la syntaxe return pour renvoyer un p-uplet, le TD fait pratiquer l'écriture de fonctions renvoyant des tuples, et le corrigé fournit les réponses attendues avec les valeurs correctes.

### course
- **Fichier** : `03_progressions/supports/premiere/P04/P04_cours_types_construits_complement.md`
- **Ancre** : `#1-p-data-constr-01--écrire-une-fonction-renvoyant-un-p-uplet-de-valeurs`
- **Citation verdict** : La syntaxe `return a, b` est équivalente à `return (a, b)`. Python construit automatiquement un tuple....

**Extrait réel** (`P04_cours_types_construits_complement.md#1-p-data-constr-01--écrire-une-fonction-renvoyant-un-p-uplet-de-valeurs`) :
```
## 1. P-DATA-CONSTR-01 : Écrire une fonction renvoyant un p-uplet de valeurs

### Définition

Un **p-uplet** (tuple) est une collection ordonnée et **immuable** de valeurs. Une fonction peut ren

La syntaxe `return a, b` est équivalente à `return (a, b)`. Python construit automatiquement un tupl

### Formalisation

```python
def nom_fonction(parametres):
    # calculs
    return valeur1, valeur2  # renvoie un tuple (valeur1, valeur2)
```
```

### practice
- **Fichier** : `03_progressions/supports/premiere/P04/P04_td_types_construits_complement.md`
- **Ancre** : `#exercice-1---fonction-renvoyant-un-p-uplet-p-data-constr-01`
- **Citation verdict** : Écrire sur papier une fonction `extremes(a, b)` qui renvoie le tuple `(plus_petit, plus_grand)` de deux nombres `a` et `b`....

**Extrait réel** (`P04_td_types_construits_complement.md#exercice-1---fonction-renvoyant-un-p-uplet-p-data-constr-01`) :
```
## Exercice 1 - Fonction renvoyant un p-uplet (P-DATA-CONSTR-01)

On considère la fonction suivante :

```python
def analyser_notes(notes):
    mini = notes[0]
    maxi = notes[0]
    somme = 0
    for n in notes:
        if n < mini:
            mini = n
        if n > maxi:
            maxi = n
        somme = somme + n
```

### correction
- **Fichier** : `03_progressions/supports/premiere/P04/P04_corrige_types_construits_complement.md`
- **Ancre** : `#exercice-1---fonction-renvoyant-un-p-uplet-p-data-constr-01`
- **Citation verdict** : La valeur renvoyée est de type `tuple`. Plus précisément, c'est un tuple de trois éléments : `(8, 15, 11.25)`....

**Extrait réel** (`P04_corrige_types_construits_complement.md#exercice-1---fonction-renvoyant-un-p-uplet-p-data-constr-01`) :
```
### Exercice 1 - Fonction renvoyant un p-uplet (P-DATA-CONSTR-01)

**1a.** La valeur renvoyée est de type `tuple`. Plus précisément, c'est un tuple de trois éléments :

**1b.**

- `a = 8` (minimum)
- `b = 15` (maximum)
- `c = 11.25` (moyenne : (12 + 8 + 15 + 10) / 4 = 45 / 4 = 11.25)

**1c.**

```python
def extremes(a, b):
    if a <= b:
```

### Grille de relecture

- [ ] Q1 L'ancre pointe la bonne section
- [ ] Q2 L'extrait enseigne/exerce au niveau du libellé
- [ ] Q3 J'aurais rendu le même verdict
- Observation : ___

---

## 15. T-ARCH-03 — Identifier, selon le protocole de routage utilisé, la route empruntée par un paquet.

- **Séquence** : campaign
- **Proofs** : 3/3
- **Justification** : Le cours enseigne les méthodes RIP/OSPF avec exemples corrigés, le TD fait pratiquer le comptage de sauts et le calcul de coûts sur des données explicites, et le corrigé fournit les réponses attendues exercice par exercice.

### course
- **Fichier** : `03_progressions/supports/terminale/T12/T12_cours_routage_rip_ospf.md`
- **Ancre** : `#méthodes`
- **Citation verdict** : - compter sauts RIP.
- additionner coûts OSPF.
- choisir route en égalité documentée.
- recalculer après panne....

**Extrait réel** (`T12_cours_routage_rip_ospf.md#méthodes`) :
```
## Méthodes
- compter sauts RIP.
- additionner coûts OSPF.
- choisir route en égalité documentée.
- recalculer après panne.

```

### practice
- **Fichier** : `03_progressions/supports/terminale/T12/T12_TD_routage_rip_ospf.md`
- **Ancre** : `#exercice-1`
- **Citation verdict** : Consigne : compter sauts RIP ; traiter aussi `égalité exacte` si nécessaire.
- Réponse attendue : RIP : A-B-D et A-C-D ont 2 sauts....

**Extrait réel** (`T12_TD_routage_rip_ospf.md#exercice-1`) :
```
### Exercice 1
- Type : lecture/analyse.
- Capacité officielle : T-ARCH-03.
- Données : `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`. ; jeu_exercice=alp
- Consigne : compter sauts RIP ; traiter aussi `égalité exacte` si nécessaire.
- Réponse attendue : RIP : A-B-D et A-C-D ont 2 sauts.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `égalité exact
```

### correction
- **Fichier** : `03_progressions/supports/terminale/T12/T12_corrige_routage_rip_ospf.md`
- **Ancre** : `#exercice-2`
- **Citation verdict** : - Réponse attendue : OSPF : A-B-D coût 10, A-C-D coût 11.
- Méthode : additionner coûts OSPF.
- Cas limite : lien indisponible....

**Extrait réel** (`T12_corrige_routage_rip_ospf.md#exercice-2`) :
```
### Exercice 2
- Réponse attendue : OSPF : A-B-D coût 10, A-C-D coût 11.
- Méthode : additionner coûts OSPF.
- Cas limite : lien indisponible.
```

### Grille de relecture

- [ ] Q1 L'ancre pointe la bonne section
- [ ] Q2 L'extrait enseigne/exerce au niveau du libellé
- [ ] Q3 J'aurais rendu le même verdict
- Observation : ___

---

## 16. T-ARCH-02C — Mettre en évidence le risque d'interblocage.

- **Séquence** : campaign
- **Proofs** : 3/3
- **Justification** : Le cours présente la méthode de détection d'attente circulaire (interblocage), le TD fait pratiquer la capacité T-ARCH-02C, et le corrigé fournit la réponse attendue. Les preuves sont cohérentes avec la capacité 'mettre en évidence le risque d'interb

### course
- **Fichier** : `03_progressions/supports/terminale/T11/T11_cours_processus_ordonnancement_interblocage.md`
- **Ancre** : `#exemples-corrigés`
- **Citation verdict** : Méthode : détecter attente circulaire....

**Extrait réel** (`T11_cours_processus_ordonnancement_interblocage.md#exemples-corrigés`) :
```
## Exemples corrigés
### Exemple corrigé 1
- Donnée : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`.
- Méthode : identifier CPU mémoire interfaces.
- Résultat attendu : P1 20 ms, P2 20 ms, P1 20 ms.
- Contrôle : capacité T-ARCH-01 et cas limite `un seul processus prêt`.
### Exemple corrigé 2
- Donnée : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`.
- Méthode : décrire création de processus.
- Résultat attendu : P1 attend journal et P2 attend camera.
- Contrôle : capacité T-ARCH-02A et cas limite `ressource libérée avant attente`.
### Exemple corrigé 3
- Donnée : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`.
- Méthode : simuler round-robin.
- Résultat attendu : CPU + mémoire + contrôleur caméra intégrés.
```

### practice
- **Fichier** : `03_progressions/supports/terminale/T11/T11_TD_processus_ordonnancement_interblocage.md`
- **Ancre** : `#exercice-4`
- **Citation verdict** : Capacité officielle : T-ARCH-02C....

**Extrait réel** (`T11_TD_processus_ordonnancement_interblocage.md#exercice-4`) :
```
### Exercice 4
- Type : cas limite.
- Capacité officielle : T-ARCH-02C.
- Données : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`.
- Consigne : détecter attente circulaire ; traiter aussi `un seul processus prêt` si nécessaire.
- Réponse attendue : processus bloqué ne consomme pas CPU.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `un seul proce
```

### correction
- **Fichier** : `03_progressions/supports/terminale/T11/T11_corrige_processus_ordonnancement_interblocage.md`
- **Ancre** : `#exercice-4`
- **Citation verdict** : Réponse attendue : processus bloqué ne consomme pas CPU....

**Extrait réel** (`T11_corrige_processus_ordonnancement_interblocage.md#exercice-4`) :
```
### Exercice 4
- Réponse attendue : processus bloqué ne consomme pas CPU.
- Méthode : détecter attente circulaire.
- Cas limite : un seul processus prêt.
```

### Grille de relecture

- [ ] Q1 L'ancre pointe la bonne section
- [ ] Q2 L'extrait enseigne/exerce au niveau du libellé
- [ ] Q3 J'aurais rendu le même verdict
- Observation : ___

---

## 17. P-IHM-03B — Distinguer ce qui est mémorisé dans le client et retransmis au serveur.

- **Séquence** : campaign
- **Proofs** : 1/3
- **Justification** : Aucun extrait ne traite explicitement de ce qui est mémorisé côté client (cookies, localStorage, sessionStorage) et retransmis au serveur. Les exercices 5 portant le tag P-IHM-03B portent sur la structure HTML/CSS, pas sur la distinction client/serve

### course
- **Fichier** : `03_progressions/supports/premiere/P08/P08_cours_web_http_dom_formulaires.md`
- **Ancre** : `#à-savoir`
- **Citation verdict** : - paramètre URL.
- formulaire.
- HTTPS....

**Extrait réel** (`P08_cours_web_http_dom_formulaires.md#à-savoir`) :
```
## À savoir
- HTML structurel.
- sélecteur CSS.
- DOM.
- événement submit.
- GET.
- POST.
- paramètre URL.
- formulaire.
- HTTPS.

```

### practice : absent

### correction : absent

### Grille de relecture

- [ ] Q1 L'ancre pointe la bonne section
- [ ] Q2 L'extrait enseigne/exerce au niveau du libellé
- [ ] Q3 J'aurais rendu le même verdict
- Observation : ___

### Décision partials

- **Rôle(s) manquant(s)** : practice, correction
- [ ] Option A : compléter via mini-PR (lot R1)
- [ ] Option B : accepter l'état partiel documenté

---

## 18. T-LANG-04A — Distinguer sur des exemples les paradigmes impératif, fonctionnel et objet.

- **Séquence** : campaign
- **Proofs** : 1/3
- **Justification** : Le cours mentionne les paradigmes impératif, fonctionnel et objet dans la liste 'À savoir', ce qui constitue une trace minimale d'enseignement. Cependant, aucun exercice du TD ne demande explicitement de distinguer les trois paradigmes sur des exempl

### course
- **Fichier** : `03_progressions/supports/terminale/T14/T14_cours_modularite_api_paradigmes_bugs.md`
- **Ancre** : `#à-savoir`
- **Citation verdict** : paradigme impératif.
- paradigme fonctionnel.
- objet....

**Extrait réel** (`T14_cours_modularite_api_paradigmes_bugs.md#à-savoir`) :
```
## À savoir
- API.
- documentation.
- module.
- paradigme impératif.
- paradigme fonctionnel.
- objet.
- bug de typage.
- effet de bord.

```

### practice : absent

### correction : absent

### Grille de relecture

- [ ] Q1 L'ancre pointe la bonne section
- [ ] Q2 L'extrait enseigne/exerce au niveau du libellé
- [ ] Q3 J'aurais rendu le même verdict
- Observation : ___

### Décision partials

- **Rôle(s) manquant(s)** : practice, correction
- [ ] Option A : compléter via mini-PR (lot R1)
- [ ] Option B : accepter l'état partiel documenté

---
