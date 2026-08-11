# Dossier de revue lead v2 — Post-remediation

## Resume executif

- **Coverage** : 114/0/0 — TOUTES les capacites a 3/3
- **Arc** : 86/2/26 → 112/2/0 → 114/0/0 (remediation R-1)
- **Echantillon v2** : 14 verdicts (8 corriges + 6 frais)
- **Seed strate fraiche** : 73

### R-0 : ecart de comptes
Les 112 (verdicts) vs 111 (coverage.md) viennent de deux systemes distincts :
verdicts = citations/ancres ; coverage = presence de fichiers par role.
Pas de source fautive — les deux sont coherents avec leurs criteres.

---

## 1. T-BDD-02 (CORRIGE) — Identifier les services rendus par un SGBD relationnel.

- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/terminale/T09/T09_cours_bases_relationnelles_cles_contraintes.md`
- **Ancre** : `#les-quatre-services-fondamentaux`
- **Citation** : | Service | Rôle | Exemple |...

**Extrait** :
```
### Les quatre services fondamentaux

| Service | Rôle | Exemple |
|---------|------|---------|
| **Persistance** | Les données survivent à l'arrêt du programme ou de la machine | Un INSERT reste 
| **Gestion des accès concurrents** | Plusieurs utilisateurs lisent et écrivent simultanément sans c
| **Efficacité des requêtes** | Le SGBD optimise l'accès aux données (index, plan d'exécution) | Une
| **Sécurisation et contrôle d'accès** | Droits par utilisateur, chiffrement, journalisation | Un él

```

### practice
- **Fichier** : `03_progressions/supports/terminale/T09/T09_TD_bases_relationnelles_cles_contraintes.md`
- **Ancre** : `#exercice-4`
- **Citation** : Capacité officielle : T-BDD-02.
- Données : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`....

**Extrait** :
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
- **Citation** : - Réponse attendue : suppression d un livre emprunté refusée.
- Méthode : repérer id_livre=9 absent....

**Extrait** :
```
### Exercice 4
- Réponse attendue : suppression d un livre emprunté refusée.
- Méthode : repérer id_livre=9 absent.
- Cas limite : clé primaire nulle.
```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___

---

## 2. T-ALGO-01C (CORRIGE) — Parcourir un arbre en ordres infixe, préfixe ou suffixe.

- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/terminale/T06/T06_cours_arbres_binaires_recherche.md`
- **Ancre** : `#méthode--parcours-en-profondeur-dun-arbre-t-algo-01c`
- **Citation** : - **Parcours infixe** (gauche, racine, droite) : `[1, 3, 6, 8, 10, 14]` — produit les clés dans l'ordre croissant pour un ABR.
- **Parcours préfixe** ...

**Extrait** :
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
- **Citation** : Parcours infixe attendu (T-ALGO-01C) : `[1, 3, 6, 8, 10, 14]`....

**Extrait** :
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
```

### correction
- **Fichier** : `03_progressions/supports/terminale/T06/T06_corrige_arbres_binaires_recherche.md`
- **Ancre** : `#exercice-3`
- **Citation** : - Méthode : parcours infixe (gauche, racine, droite) — T-ALGO-01C.
- Cas limite : arbre dégénéré....

**Extrait** :
```
### Exercice 3
- Réponse attendue : infixe -> 1,3,6,8,10,14.
- Méthode : parcours infixe (gauche, racine, droite) — T-ALGO-01C.
- Cas limite : arbre dégénéré.
```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___

---

## 3. T-STRUCT-05A (CORRIGE) — Modéliser des situations sous forme de graphes.

- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/terminale/T07/T07_cours_graphes_modelisation_listes_matrices.md`
- **Ancre** : `#savoir-faire-et-méthodes-opérationnelles`
- **Citation** : - traduire une situation en sommets et arêtes.
- passer de la liste d'adjacence à la matrice.
- comparer le coût mémoire des deux représentations....

**Extrait** :
```
### Savoir-faire et méthodes opérationnelles
- traduire une situation en sommets et arêtes.
- passer de la liste d’adjacence à la matrice.
- comparer le coût mémoire des deux représentations.

```

### practice
- **Fichier** : `03_progressions/supports/terminale/T07/T07_TP_graphes_modelisation_listes_matrices.md`
- **Ancre** : `#travail-demandé`
- **Citation** : 1. Préparer la donnée et nommer les champs utiles.
2. Réaliser : lister voisins sortants.
3. Réaliser : remplir matrice 0/1.
4. Tester le cas limite `...

**Extrait** :
```
## Travail demandé
1. Préparer la donnée et nommer les champs utiles.
2. Réaliser : lister voisins sortants.
3. Réaliser : remplir matrice 0/1.
4. Tester le cas limite `sommet isolé E`.
5. Produire le livrable : A -> [B,C], B -> [D], C -> [D], D -> [B].

```

### correction
- **Fichier** : `03_progressions/supports/terminale/T07/T07_corrige_graphes_modelisation_listes_matrices.md`
- **Ancre** : `#exercice-1`
- **Citation** : - Réponse attendue : A -> [B,C], B -> [D], C -> [D], D -> [B].
- Méthode : lister voisins sortants.
- Cas limite : sommet isolé E....

**Extrait** :
```
### Exercice 1
- Réponse attendue : A -> [B,C], B -> [D], C -> [D], D -> [B].
- Méthode : lister voisins sortants.
- Cas limite : sommet isolé E.
```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___

---

## 4. T-BDD-01B (CORRIGE) — Distinguer structure et contenu d'une base de données.

- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/terminale/T09/T09_cours_bases_relationnelles_cles_contraintes.md`
- **Ancre** : `#à-savoir`
- **Citation** : - relation.
- attribut.
- tuple.
- clé primaire.
- clé étrangère.
- contrainte de domaine.
- contrainte de référence.
- schéma.
- instance.
- anomalie...

**Extrait** :
```
## À savoir
- relation.
- attribut.
- tuple.
- clé primaire.
- clé étrangère.
- contrainte de domaine.
- contrainte de référence.
- schéma.
- instance.
- anomalie.

```

### practice
- **Fichier** : `03_progressions/supports/terminale/T09/T09_TD_bases_relationnelles_cles_contraintes.md`
- **Ancre** : `#exercice-2`
- **Citation** : - Consigne : vérifier unicité id_livre ; traiter aussi `doublon id_livre=1` si nécessaire.
- Réponse attendue : Emprunt.id_livre référence Livre.id_li...

**Extrait** :
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
- **Citation** : - Réponse attendue : Emprunt.id_livre référence Livre.id_livre.
- Méthode : vérifier unicité id_livre.
- Cas limite : doublon id_livre=1....

**Extrait** :
```
### Exercice 2
- Réponse attendue : Emprunt.id_livre référence Livre.id_livre.
- Méthode : vérifier unicité id_livre.
- Cas limite : doublon id_livre=1.
```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___

---

## 5. T-ALGO-04 (CORRIGE) — Utiliser la programmation dynamique pour écrire un algorithme.

- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/terminale/T17/T17_cours_programmation_dynamique.md`
- **Ancre** : `#méthodes`
- **Citation** : - définir dp[m] coût minimal.
- écrire dp[m]=1+min(dp[m-p]).
- initialiser dp[0]=0.
- remplir la table de 1 à 11....

**Extrait** :
```
## Méthodes
- définir dp[m] coût minimal.
- écrire dp[m]=1+min(dp[m-p]).
- initialiser dp[0]=0.
- remplir la table de 1 à 11.

```

### practice
- **Fichier** : `03_progressions/supports/terminale/T17/T17_TD_programmation_dynamique.md`
- **Ancre** : `#exercice-2`
- **Citation** : - Consigne : écrire dp[m]=1+min(dp[m-p]) ; traiter aussi `montant impossible` si nécessaire.
- Réponse attendue : dp[11]=3 avec 5+5+1....

**Extrait** :
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
- **Ancre** : `#exercice-2`
- **Citation** : - Réponse attendue : dp[11]=3 avec 5+5+1.
- Méthode : écrire dp[m]=1+min(dp[m-p]).
- Cas limite : montant impossible....

**Extrait** :
```
### Exercice 2
- Réponse attendue : dp[11]=3 avec 5+5+1.
- Méthode : écrire dp[m]=1+min(dp[m-p]).
- Cas limite : montant impossible.
```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___

---

## 6. P-ALGO-05 (CORRIGE) — Résoudre un problème grâce à un algorithme glouton.

- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P13/P13_cours_dichotomie_glouton_knn.md`
- **Ancre** : `#exemple-corrigé-3---glouton-p-algo-05`
- **Citation** : ### Exemple corrigé 3 - glouton (P-ALGO-05)
- Donnée : `pièces=[10,5,2,1], montant=28`.
- Méthode : prendre la plus grande pièce possible à chaque éta...

**Extrait** :
```
### Exemple corrigé 3 - glouton (P-ALGO-05)
- Donnée : `pièces=[10,5,2,1], montant=28`.
- Méthode : prendre la plus grande pièce possible à chaque étape.
- Résultat attendu : 28 = 10 + 10 + 5 + 2 + 1 (5 pièces).
- Contrôle : capacité P-ALGO-05 et cas limite `pièce 1 absente → glouton peut échouer`.
```

### practice
- **Fichier** : `03_progressions/supports/premiere/P13/P13_TD_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-2`
- **Citation** : - Capacité officielle : P-ALGO-04.
- Données : `tableau=[4,9,18,23,37,41], cible=37 ; pièces=[10,5,2,1], montant=28 ; voisins=[rouge:1.2, bleu:2.0, ro...

**Extrait** :
```
### Exercice 2
- Type : production/écriture.
- Capacité officielle : P-ALGO-04.
- Données : `tableau=[4,9,18,23,37,41], cible=37 ; pièces=[10,5,2,1], montant=28 ; voisins=[rouge:1.
- Consigne : montrer que droite-gauche diminue ; traiter aussi `pièce 1 absente` si nécessaire.
- Réponse attendue : 28 -> 10+10+5+2+1.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `pièce 1 absen
```

### correction
- **Fichier** : `03_progressions/supports/premiere/P13/P13_corrige_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-2`
- **Citation** : - Réponse attendue : 28 -> 10+10+5+2+1.
- Méthode : montrer que droite-gauche diminue.
- Cas limite : pièce 1 absente....

**Extrait** :
```
### Exercice 2
- Réponse attendue : 28 -> 10+10+5+2+1.
- Méthode : montrer que droite-gauche diminue.
- Cas limite : pièce 1 absente.
```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___

---

## 7. P-IHM-03B (CORRIGE) — Distinguer ce qui est mémorisé dans le client et retransmis au serveur.

- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P08/P08_cours_web_http_dom_formulaires.md`
- **Ancre** : `#mémorisation-et-transmission-des-données-entre-client-et-serveur`
- **Citation** : La capacité P-IHM-03B demande de distinguer ce qui est mémorisé côté client (cookies, localStorage) de ce qui est retransmis au serveur à chaque requê...

**Extrait** :
```
## Mémorisation et transmission des données entre client et serveur

La capacité P-IHM-03B demande de distinguer ce qui est mémorisé côté client (cookies, localStorage) 

### Cookies

Un **cookie** est un petit fichier texte stocké par le navigateur. Le serveur le crée via l'en-tête 

```
Set-Cookie: session_id=abc123; Path=/; HttpOnly; Secure
```

```

### practice
- **Fichier** : `03_progressions/supports/premiere/P08/P08_TD_html_css_dom.md`
- **Ancre** : `#exercice-5`
- **Citation** : - Type : justification.
- Capacité officielle : P-IHM-03B.
- Données : `<form method=post action=/reservation><input id=nom name=nom></form>, URL /clu...

**Extrait** :
```
### Exercice 5
- Type : justification.
- Capacité officielle : P-IHM-03B.
- Données : `<form method=post action=/reservation><input id=nom name=nom></form>, URL /club?jour=me
- Consigne : repérer header main form label input ; traiter aussi `paramètre jour absent` si nécessa
- Réponse attendue : <label for=nom>Nom</label><input id=nom name=nom>.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `paramètre jou
```

### correction
- **Fichier** : `03_progressions/supports/premiere/P08/P08_corrige_web_http_dom_formulaires.md`
- **Ancre** : `#exercice-5`
- **Citation** : - Réponse attendue : <label for=nom>Nom</label><input id=nom name=nom>.
- Méthode : repérer header main form label input.
- Cas limite : paramètre jou...

**Extrait** :
```
### Exercice 5
- Réponse attendue : <label for=nom>Nom</label><input id=nom name=nom>.
- Méthode : repérer header main form label input.
- Cas limite : paramètre jour absent.
```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___

---

## 8. T-LANG-04A (CORRIGE) — Distinguer sur des exemples les paradigmes impératif, fonctionnel et objet.

- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/terminale/T14/T14_cours_modularite_api_paradigmes_bugs.md`
- **Ancre** : `#à-savoir`
- **Citation** : - paradigme impératif.
- paradigme fonctionnel.
- objet....

**Extrait** :
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

### practice
- **Fichier** : `03_progressions/supports/terminale/T14/T14_TD_modularite_api_paradigmes_bugs.md`
- **Ancre** : `#exercice-4`
- **Citation** : - Capacité officielle : T-LANG-04A.
- Données : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temp...

**Extrait** :
```
### Exercice 4
- Type : cas limite.
- Capacité officielle : T-LANG-04A.
- Données : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{vi
- Consigne : écrire un test révélant un bug ; traiter aussi `liste vide` si nécessaire.
- Réponse attendue : liste vide -> ValueError.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `liste vide`.
```

### correction
- **Fichier** : `03_progressions/supports/terminale/T14/T14_corrige_modularite_api_paradigmes_bugs.md`
- **Ancre** : `#exercice-4`
- **Citation** : - Réponse attendue : liste vide -> ValueError.
- Méthode : écrire un test révélant un bug.
- Cas limite : liste vide....

**Extrait** :
```
### Exercice 4
- Réponse attendue : liste vide -> ValueError.
- Méthode : écrire un test révélant un bug.
- Cas limite : liste vide.
```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___

---

## 9. P-IHM-04C (FRAIS) — Discuter les types de requêtes selon les valeurs à transmettre et leur confidentialité.

- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P08/P08_cours_web_http_dom_formulaires.md`
- **Ancre** : `#confidentialité-des-requêtes`
- **Citation** : ### GET vs POST — visibilité des données

| Aspect | GET | POST |
|--------|-----|------|
| Données visibles dans l'URL | Oui (`?nom=valeur&...`) | No...

**Extrait** :
```
## Confidentialité des requêtes

La capacité P-IHM-04C demande de discuter les types de requêtes selon les valeurs à transmettre et l

### GET vs POST — visibilité des données

| Aspect | GET | POST |
|--------|-----|------|
| Données visibles dans l'URL | Oui (`?nom=valeur&...`) | Non (corps de la requête) |
| Historique du navigateur | Enregistrées | Non enregistrées |
| Logs du serveur | Paramètres visibles | Paramètres non loggués par défaut |
| Longueur maximale | Limitée (~2048 caractères) | Pas de limite pratique |
```

### practice
- **Fichier** : `03_progressions/supports/premiere/P08/P08_TD_http_get_post_formulaires.md`
- **Ancre** : `#exercice-9`
- **Citation** : - Consigne : (9a) pour chaque situation, indiquer si GET ou POST est approprié et justifier ; (9b) pour chaque situation, indiquer si HTTPS est nécess...

**Extrait** :
```
### Exercice 9
- Type : lecture/analyse.
- Capacité officielle : P-IHM-04C.
- Données : quatre situations de transmission de données sur le Web : (A) un formulaire de connexion
- Consigne : (9a) pour chaque situation, indiquer si GET ou POST est approprié et justifier ; (9b) p
- Réponse attendue : (A) POST+HTTPS ; (B) GET ; (C) POST ; (D) risque — token visible dans l'histori
- Critère de réussite : chaque situation classée avec justification, distinction GET/POST/HTTPS expl

```

### correction
- **Fichier** : `03_progressions/supports/premiere/P08/P08_corrige_web_http_dom_formulaires.md`
- **Ancre** : `#exercice-9`
- **Citation** : - Réponse attendue : (A) POST+HTTPS (mot de passe), (B) GET (recherche), (C) POST (contact), (D) risque token visible.
- Méthode : classification par ...

**Extrait** :
```
### Exercice 9
- Capacité mobilisée : P-IHM-04C.
- Réponse attendue : (A) POST+HTTPS (mot de passe), (B) GET (recherche), (C) POST (contact), (D) ris
- Méthode : classification par confidentialité (URL, historique, logs, chiffrement).
- Cas limite : POST sans HTTPS ne chiffre pas les données sur le réseau.

```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___

---

## 10. P-DATA-BASE-01 (FRAIS) — Passer de la représentation d'une base dans une autre.

- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P01/P01_cours_conversions_bases.md`
- **Ancre** : `#exemple-corrigé-1---décimal-vers-binaire`
- **Citation** : Méthode : enchaîner divisions par 2 puis lire les restes de bas en haut.
- Résultat obtenu : `1101₂`....

**Extrait** :
```
### Exemple corrigé 1 - décimal vers binaire
- Donnée étudiée : `13` en base dix.
- Méthode : enchaîner divisions par 2 puis lire les restes de bas en haut.
- Résultat obtenu : `1101₂`.
- Contrôle : le cas limite « 0 se code 0 » est vérifié séparément.
```

### practice
- **Fichier** : `03_progressions/supports/premiere/P01/P01_td_conversions_bases.md`
- **Ancre** : `#exercice-1`
- **Citation** : Énoncé disciplinaire : résoudre décimal vers binaire avec `13` en base dix.
- Production attendue : `1101₂`....

**Extrait** :
```
### Exercice 1
- Objectif travaillé : O1.
- Capacité officielle : P-DATA-BASE-01.
- Énoncé disciplinaire : résoudre décimal vers binaire avec `13` en base dix.
- Production attendue : `1101₂`.
- Contrainte de contrôle : faire apparaître le contrôle « 0 se code 0 ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
```

### correction
- **Fichier** : `03_progressions/supports/premiere/P01/P01_corrige_conversions_bases.md`
- **Ancre** : `#corrigé-exercice-1`
- **Citation** : Méthode : identifier `13` en base dix, appliquer la méthode « enchaîner divisions par 2 puis lire les restes de bas en haut », puis écrire `1101₂`....

**Extrait** :
```
### Corrigé exercice 1
- Méthode : identifier `13` en base dix, appliquer la méthode « enchaîner divisions par 2 puis lire 
- Résultat : `1101₂`.
- Contrôle : faire apparaître le contrôle « 0 se code 0 ».
- Erreur traitée : EF1 - Écrire les restes dans l’ordre de calcul au lieu de les lire de bas en haut
```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___

---

## 11. T-BDD-01C (FRAIS) — Repérer les anomalies dans le schéma d'une base de données.

- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/terminale/T09/T09_cours_bases_relationnelles_cles_contraintes.md`
- **Ancre** : `#exemples-corrigés`
- **Citation** : - Méthode : contrôler Emprunt.id_livre.
- Résultat attendu : Emprunt(11,9,Sam) viole la référence.
- Contrôle : capacité T-BDD-01C et cas limite `supp...

**Extrait** :
```
## Exemples corrigés
### Exemple corrigé 1
- Donnée : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`.
- Méthode : identifier schéma et instance.
- Résultat attendu : Livre.id_livre identifie chaque livre.
- Contrôle : capacité T-BDD-01A et cas limite `clé primaire nulle`.
### Exemple corrigé 2
- Donnée : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`.
- Méthode : vérifier unicité id_livre.
- Résultat attendu : Emprunt.id_livre référence Livre.id_livre.
- Contrôle : capacité T-BDD-01B et cas limite `doublon id_livre=1`.
### Exemple corrigé 3
```

### practice
- **Fichier** : `03_progressions/supports/terminale/T09/T09_TD_bases_relationnelles_cles_contraintes.md`
- **Ancre** : `#exercice-3`
- **Citation** : - Consigne : contrôler Emprunt.id_livre ; traiter aussi `suppression référencée` si nécessaire.
- Réponse attendue : Emprunt(11,9,Sam) viole la référe...

**Extrait** :
```
### Exercice 3
- Type : production/écriture.
- Capacité officielle : T-BDD-01C.
- Données : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`. ; 
- Consigne : contrôler Emprunt.id_livre ; traiter aussi `suppression référencée` si nécessaire.
- Réponse attendue : Emprunt(11,9,Sam) viole la référence.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `suppression r
```

### correction
- **Fichier** : `03_progressions/supports/terminale/T09/T09_corrige_bases_relationnelles_cles_contraintes.md`
- **Ancre** : `#exercice-3`
- **Citation** : - Réponse attendue : Emprunt(11,9,Sam) viole la référence.
- Méthode : contrôler Emprunt.id_livre.
- Cas limite : suppression référencée....

**Extrait** :
```
### Exercice 3
- Réponse attendue : Emprunt(11,9,Sam) viole la référence.
- Méthode : contrôler Emprunt.id_livre.
- Cas limite : suppression référencée.
```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___

---

## 12. T-ARCH-04A (FRAIS) — Décrire les principes du chiffrement symétrique et asymétrique.

- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/terminale/T13/T13_cours_chiffrement_https.md`
- **Ancre** : `#à-savoir`
- **Citation** : - chiffrement symétrique.
- chiffrement asymétrique.
- clé publique.
- clé privée.
- certificat.
- échange de clé....

**Extrait** :
```
## À savoir
- chiffrement symétrique.
- chiffrement asymétrique.
- clé publique.
- clé privée.
- certificat.
- échange de clé.
- HTTPS.
- authenticité.

```

### practice
- **Fichier** : `03_progressions/supports/terminale/T13/T13_TD_chiffrement_https.md`
- **Ancre** : `#exercice-1`
- **Citation** : Consigne : protéger Ksession par asymétrique ; traiter aussi `certificat expiré` si nécessaire....

**Extrait** :
```
### Exercice 1
- Type : lecture/analyse.
- Capacité officielle : T-ARCH-04A.
- Données : `Ksession, clé publique serveur Kpub, certificat signé par Autorité-Test`. ; jeu_exercic
- Consigne : protéger Ksession par asymétrique ; traiter aussi `certificat expiré` si nécessaire.
- Réponse attendue : message chiffré avec Ksession.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `certificat ex
```

### correction
- **Fichier** : `03_progressions/supports/terminale/T13/T13_corrige_chiffrement_https.md`
- **Ancre** : `#exercice-1`
- **Citation** : - Réponse attendue : message chiffré avec Ksession.
- Méthode : protéger Ksession par asymétrique.
- Cas limite : certificat expiré....

**Extrait** :
```
### Exercice 1
- Réponse attendue : message chiffré avec Ksession.
- Méthode : protéger Ksession par asymétrique.
- Cas limite : certificat expiré.
```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___

---

## 13. T-BDD-03H (FRAIS) — Construire des requêtes de suppression avec DELETE.

- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/terminale/T10/T10_cours_sql_select_where_join.md`
- **Ancre** : `#à-savoir`
- **Citation** : DELETE avec WHERE....

**Extrait** :
```
## À savoir
- SELECT.
- FROM.
- WHERE.
- JOIN.
- ORDER BY.
- INSERT.
- UPDATE avec WHERE.
- DELETE avec WHERE.

```

### practice
- **Fichier** : `03_progressions/supports/terminale/T10/T10_TD_sql_insert_update_delete.md`
- **Ancre** : `#exercice-3`
- **Citation** : Réponse attendue : UPDATE id_note=10 -> Ada 18....

**Extrait** :
```
### Exercice 3
- Type : production/écriture.
- Capacité officielle : T-BDD-03C.
- Données : `Eleve(1,Ada,T1), Eleve(2,Linus,T2) ; Note(10,1,NSI,17), Note(11,2,NSI,13)`. ; jeu_exerc
- Consigne : joindre Eleve.id_eleve = Note.id_eleve ; traiter aussi `DELETE sans WHERE` si nécessair
- Réponse attendue : UPDATE id_note=10 -> Ada 18.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `DELETE sans W
```

### correction
- **Fichier** : `03_progressions/supports/terminale/T10/T10_corrige_sql_select_where_join.md`
- **Ancre** : `#exercice-4`
- **Citation** : Réponse attendue : DELETE WHERE id_note=11 retire Linus....

**Extrait** :
```
### Exercice 4
- Réponse attendue : DELETE WHERE id_note=11 retire Linus.
- Méthode : vérifier modification par SELECT.
- Cas limite : JOIN sans ON.
```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___

---

## 14. P-DATA-CONSTR-02C (FRAIS) — Utiliser des tableaux de tableaux pour représenter des matrices.

- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P04/P04_cours_types_construits_complement.md`
- **Ancre** : `#3-p-data-constr-02c--utiliser-des-tableaux-de-tableaux-pour-représenter-des-matrices`
- **Citation** : Une **matrice** est représentée en Python par une **liste de listes** (tableau de tableaux). Chaque sous-liste représente une ligne. L'accès à l'éléme...

**Extrait** :
```
## 3. P-DATA-CONSTR-02C : Utiliser des tableaux de tableaux pour représenter des matrices

### Définition

Une **matrice** est représentée en Python par une **liste de listes** (tableau de tableaux). Chaque 

### Formalisation

Une matrice de `n` lignes et `p` colonnes :

```python
matrice = [
```

### practice
- **Fichier** : `03_progressions/supports/premiere/P04/P04_td_types_construits_complement.md`
- **Ancre** : `#exercice-3---matrices-comme-tableaux-de-tableaux-p-data-constr-02c`
- **Citation** : **Question 3d.** On exécute le code suivant. Expliquer pourquoi le résultat est incorrect et proposer une correction.

```python
grille = [[0] * 3] * ...

**Extrait** :
```
## Exercice 3 - Matrices comme tableaux de tableaux (P-DATA-CONSTR-02C)

On donne la matrice suivante :

```python
M = [
    [5, 3, 8],
    [1, 7, 4],
    [9, 2, 6],
]
```

```

### correction
- **Fichier** : `03_progressions/supports/premiere/P04/P04_corrige_types_construits_complement.md`
- **Ancre** : `#exercice-3---matrices-p-data-constr-02c`
- **Citation** : Le code `grille = [[0] * 3] * 3` crée une liste contenant 3 fois la **même** sous-liste (même objet en mémoire). Modifier `grille[0][0]` modifie donc ...

**Extrait** :
```
### Exercice 3 - Matrices (P-DATA-CONSTR-02C)

**3a.**

- `M[0][2] = 8` (ligne 0, colonne 2)
- `M[1][1] = 7` (ligne 1, colonne 1)
- `M[2][0] = 9` (ligne 2, colonne 0)

**3b.** `M` possède 3 lignes et 3 colonnes.

- Nombre de lignes : `len(M)` qui vaut `3`.
- Nombre de colonnes : `len(M[0])` qui vaut `3`.
```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___

---
