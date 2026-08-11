# Dossier de revue lead v3 — Post-REM3 (regenere)

## Resume executif

- **Coverage** : 113/1/0 (source unique : verdicts au moment de la generation)
- **Partial** : T-LANG-04A (1/3)
- **Echantillon** : 13 verdicts (7 corriges + 6 frais seed 91)

---

## 1. P-ALGO-03 (CORRIGE) — Ecrire un algorithme qui prédit la classe d'un élément à partir de la classe majoritaire de ses k plus proches voisins.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P13/P13_cours_dichotomie_glouton_knn.md`
- **Ancre** : `#algorithme-des-k-plus-proches-voisins`
- **Citation** : La classe prédite est la **classe majoritaire** parmi ces k voisins....

**Extrait** :
```
## Algorithme des k plus proches voisins

La capacité P-ALGO-03 demande d'écrire un algorithme qui prédit la classe d'un élément à partir de l

### Principe

Soit un ensemble de points étiquetés (chaque point a des coordonnées et une classe connue). Pour pré

1. Calculer la **distance** entre le nouveau point et chaque point de l'ensemble.
2. Trier les points par distance croissante.
3. Sélectionner les **k plus proches** voisins.
4. La classe prédite est la **classe majoritaire** parmi ces k voisins.
```

### practice
- **Fichier** : `03_progressions/supports/premiere/P13/P13_TD_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-9`
- **Citation** : calculer la distance euclidienne entre le nouveau point et chaque point d'entraînement ; (9b) identifier les 3 plus proches voisins ; (9c) déterminer ...

**Extrait** :
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
- **Citation** : 3 plus proches = A(3,2) B(5,4) A(2,3), vote A=2 B=1, classe "A"....

**Extrait** :
```
### Exercice 9
- Capacité mobilisée : P-ALGO-03.
- Réponse attendue : distances calculées, 3 plus proches = A(3,2) B(5,4) A(2,3), vote A=2 B=1, class
- Méthode : distance euclidienne, tri, vote majoritaire.
- Cas limite : k=2 avec égalité de vote → résultat indéterminé.

```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 2. P-ALGO-04 (CORRIGE) — Montrer la terminaison de la recherche dichotomique à l'aide d'un variant de boucle.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P13/P13_cours_dichotomie_glouton_knn.md`
- **Ancre** : `#exemple-corrigé-2---variant-de-dichotomie-p-algo-04`
- **Citation** : Méthode : montrer que la quantité `droite - gauche` diminue strictement à chaque étape.
- Résultat attendu : étape 1 → gauche=0, droite=5 (écart 5) ; ...

**Extrait** :
```
### Exemple corrigé 2 - variant de dichotomie (P-ALGO-04)
- Donnée : `tableau=[4,9,18,23,37,41], cible=37`.
- Méthode : montrer que la quantité `droite - gauche` diminue strictement à chaque étape.
- Résultat attendu : étape 1 → gauche=0, droite=5 (écart 5) ; étape 2 → gauche=3, droite=5 (écart 2)
- Contrôle : capacité P-ALGO-04 et cas limite `cible absente → l'écart atteint 0 et la boucle s'arrê
```

### practice
- **Fichier** : `03_progressions/supports/premiere/P13/P13_TD_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-2`
- **Citation** : Capacité officielle : P-ALGO-04.
- Données : `tableau=[4,9,18,23,37,41], cible=37 ; pièces=[10,5,2,1], montant=28 ; voisins=[rouge:1.2, bleu:2.0, roug...

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
- **Citation** : Capacité mobilisée : P-ALGO-04.
- Réponse attendue : le variant droite-gauche décroît de 5 à 1 sur tableau=[4,9,18,23,37,41], cible=37, prouvant la te...

**Extrait** :
```
### Exercice 2
- Capacité mobilisée : P-ALGO-04.
- Réponse attendue : le variant droite-gauche décroît de 5 à 1 sur tableau=[4,9,18,23,37,41], cible=
- Méthode : montrer que droite-gauche diminue strictement à chaque étape.
- Cas limite : cible absente → l'écart atteint 0 et la boucle s'arrête sans trouver.
```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 3. P-ALGO-05 (CORRIGE) — Résoudre un problème grâce à un algorithme glouton.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P13/P13_cours_dichotomie_glouton_knn.md`
- **Ancre** : `#exemple-corrigé-3---glouton-p-algo-05`
- **Citation** : Méthode : prendre la plus grande pièce possible à chaque étape.
- Résultat attendu : 28 = 10 + 10 + 5 + 2 + 1 (5 pièces).
- Contrôle : capacité P-ALGO...

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
- **Citation** : Consigne : montrer que droite-gauche diminue ; traiter aussi `pièce 1 absente` si nécessaire.
- Réponse attendue : 28 -> 10+10+5+2+1....

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
- **Ancre** : `#exercice-3`
- **Citation** : Réponse attendue : 28 = 10 + 10 + 5 + 2 + 1 (5 pièces, algorithme glouton avec pièces=[10,5,2,1]).
- Méthode : prendre la plus grande pièce possible à...

**Extrait** :
```
### Exercice 3
- Capacité mobilisée : P-ALGO-05.
- Réponse attendue : 28 = 10 + 10 + 5 + 2 + 1 (5 pièces, algorithme glouton avec pièces=[10,5,2,1]).
- Méthode : prendre la plus grande pièce possible à chaque étape.
- Cas limite : pièce 1 absente → le glouton peut échouer (ex. montant=3 avec pièces=[5,2]).
```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 4. T-BDD-02 (CORRIGE) — Identifier les services rendus par un SGBD relationnel.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/terminale/T09/T09_cours_bases_relationnelles_cles_contraintes.md`
- **Ancre** : `#les-quatre-services-fondamentaux`
- **Citation** : | Service | Rôle | Exemple |
|---------|------|---------|...

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
- Données : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`...

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

## 5. T-BDD-01B (CORRIGE) — Distinguer structure et contenu d'une base de données.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/terminale/T09/T09_cours_bases_relationnelles_cles_contraintes.md`
- **Ancre** : `#savoir-disciplinaire`
- **Citation** : Vocabulaire à maîtriser : relation, attribut, tuple, clé primaire, clé étrangère, contrainte, schéma, instance....

**Extrait** :
```
### Savoir disciplinaire
- Vocabulaire à maîtriser : relation, attribut, tuple, clé primaire, clé étrangère, contrainte, sché
- Capacités reliées : T-BDD-01A, T-BDD-01B, T-BDD-01C, T-BDD-02.
- Le savoir attendu consiste à expliquer le rôle de chaque objet avant de l'utiliser dans un exercic

```

### practice
- **Fichier** : `03_progressions/supports/terminale/T09/T09_TD_bases_relationnelles_cles_contraintes.md`
- **Ancre** : `#exercice-2`
- **Citation** : Consigne : vérifier unicité id_livre ; traiter aussi `doublon id_livre=1` si nécessaire....

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
- **Citation** : Réponse attendue : Emprunt.id_livre référence Livre.id_livre.
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

## 6. P-IHM-03B (CORRIGE) — Distinguer ce qui est mémorisé dans le client et retransmis au serveur.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P08/P08_cours_web_http_dom_formulaires.md`
- **Ancre** : `#mémorisation-et-transmission-des-données-entre-client-et-serveur`
- **Citation** : Un **cookie** est un petit fichier texte stocké par le navigateur. Le serveur le crée via l'en-tête `Set-Cookie` ; le navigateur le renvoie automatiqu...

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
- **Citation** : - Capacité officielle : P-IHM-03B.
- Données : `<form method=post action=/reservation><input id=nom name=nom></form>, URL /club?jour=mercredi`. ; jeu_...

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

## 7. T-LANG-04A (CORRIGE) — Distinguer sur des exemples les paradigmes impératif, fonctionnel et objet.
- **Proofs** : 1/3

### course : absent

### practice
- **Fichier** : `03_progressions/supports/terminale/T04/T04_td_recursivite.md`
- **Ancre** : `#exercice-9`
- **Citation** : on donne trois implémentations de la somme d'une liste — impérative (boucle for), fonctionnelle (récursion sans variable mutable) et objet (méthode d'...

**Extrait** :
```
### Exercice 9
- Objectif travaillé : O1, O2.
- Capacité officielle : T-LANG-04A.
- Énoncé disciplinaire : on donne trois implémentations de la somme d'une liste — impérative (boucle
- Production attendue : impératif/fonctionnel/objet identifiés, traits (état mutable / récursion / e
- Contrainte de contrôle : chaque réponse justifiée par une référence au code.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.

```

### correction : absent

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 8. P-ARCH-03B (FRAIS) — Utiliser les commandes de base en ligne de commande.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P09/P09_cours_architecture_os_droits.md`
- **Ancre** : `#méthodes`
- **Citation** : calculer chmod 640 et droit x dossier....

**Extrait** :
```
## Méthodes
- distinguer mémoire vive et stockage.
- identifier PID et processus.
- lire rwx pour propriétaire groupe autres.
- calculer chmod 640 et droit x dossier.

```

### practice
- **Fichier** : `03_progressions/supports/premiere/P09/P09_TD_architecture_os_droits.md`
- **Ancre** : `#exercice-4`
- **Citation** : Capacité officielle : P-ARCH-03B....

**Extrait** :
```
### Exercice 4
- Type : cas limite.
- Capacité officielle : P-ARCH-03B.
- Données : `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors gr
- Consigne : calculer chmod 640 et droit x dossier ; traiter aussi `fichier absent` si nécessaire.
- Réponse attendue : sans x sur dossier, lecture du fichier impossible.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `fichier absen
```

### correction
- **Fichier** : `03_progressions/supports/premiere/P09/P09_corrige_architecture_os_droits.md`
- **Ancre** : `#exercice-4`
- **Citation** : Réponse attendue : sans x sur dossier, lecture du fichier impossible....

**Extrait** :
```
### Exercice 4
- Réponse attendue : sans x sur dossier, lecture du fichier impossible.
- Méthode : calculer chmod 640 et droit x dossier.
- Cas limite : fichier absent.
```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 9. T-LANG-05 (FRAIS) — Savoir répondre aux causes typiques de bugs.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/terminale/T14/T14_cours_modularite_api_paradigmes_bugs.md`
- **Ancre** : `#erreurs-fréquentes`
- **Citation** : - import avec effet de bord.
- API sans docstring.
- bug corrigé sans test....

**Extrait** :
```
## Erreurs fréquentes
- import avec effet de bord.
- API sans docstring.
- bug corrigé sans test.

```

### practice
- **Fichier** : `03_progressions/supports/terminale/T14/T14_TD_modularite_api_paradigmes_bugs.md`
- **Ancre** : `#exercice-6`
- **Citation** : - Capacité officielle : T-LANG-05.
- Données : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,tempe...

**Extrait** :
```
### Exercice 6
- Type : lecture/analyse.
- Capacité officielle : T-LANG-05.
- Données : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{vi
- Consigne : séparer module et script principal ; traiter aussi `type chaîne` si nécessaire.
- Réponse attendue : from meteo import moyenne_temperature.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `type chaîne`.
```

### correction
- **Fichier** : `03_progressions/supports/terminale/T14/T14_corrige_modularite_api_paradigmes_bugs.md`
- **Ancre** : `#exercice-6`
- **Citation** : - Réponse attendue : from meteo import moyenne_temperature.
- Méthode : séparer module et script principal.
- Cas limite : type chaîne....

**Extrait** :
```
### Exercice 6
- Réponse attendue : from meteo import moyenne_temperature.
- Méthode : séparer module et script principal.
- Cas limite : type chaîne.
```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 10. P-DATA-CONSTR-03A (FRAIS) — Construire une entrée de dictionnaire.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P04/P04_cours_types_construits_complement.md`
- **Ancre** : `#4-p-data-constr-03a--construire-une-entrée-de-dictionnaire`
- **Citation** : Construire une entrée consiste à ajouter ou modifier une association `clé: valeur` dans un dictionnaire existant, avec la syntaxe `d[cle] = valeur`....

**Extrait** :
```
## 4. P-DATA-CONSTR-03A : Construire une entrée de dictionnaire

### Définition

Un **dictionnaire** associe des **clés** à des **valeurs**. Construire une entrée consiste à ajouter

### Formalisation

```python
d = {}              # dictionnaire vide
d[cle] = valeur     # ajoute ou met à jour l'entrée
```
```

### practice
- **Fichier** : `03_progressions/supports/premiere/P04/P04_td_types_construits_complement.md`
- **Ancre** : `#exercice-4---construire-une-entrée-de-dictionnaire-p-data-constr-03a`
- **Citation** : Compléter le code pour construire le dictionnaire `photo` contenant les entrées suivantes : `"marque"` associée à `"Sony"`, `"modele"` associée à `"A7...

**Extrait** :
```
## Exercice 4 - Construire une entrée de dictionnaire (P-DATA-CONSTR-03A)

On souhaite stocker les métadonnées EXIF fictives d’une photographie.

**Question 4a.** Compléter le code pour construire le dictionnaire `photo` contenant les entrées sui

```python
photo = {}
photo[______] = ______
photo[______] = ______
photo[______] = ______
photo[______] = ______
```

### correction
- **Fichier** : `03_progressions/supports/premiere/P04/P04_corrige_types_construits_complement.md`
- **Ancre** : `#exercice-4---construire-une-entrée-de-dictionnaire-p-data-constr-03a`
- **Citation** : photo["marque"] = "Sony"
photo["modele"] = "A7III"
photo["date_prise"] = "2025-07-01"
photo["taille"] = (6000, 4000)...

**Extrait** :
```
### Exercice 4 - Construire une entrée de dictionnaire (P-DATA-CONSTR-03A)

**4a.**

```python
photo = {}
photo["marque"] = "Sony"
photo["modele"] = "A7III"
photo["date_prise"] = "2025-07-01"
photo["taille"] = (6000, 4000)
```

```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 11. T-STRUCT-05C (FRAIS) — Ecrire l'implémentation d'un graphe par listes de successeurs ou prédécesseurs.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/terminale/T07/T07_cours_graphes_modelisation_listes_matrices.md`
- **Ancre** : `#méthodes`
- **Citation** : lister voisins sortants....

**Extrait** :
```
## Méthodes
- lister voisins sortants.
- remplir matrice 0/1.
- calculer degré sortant.
- choisir liste pour graphe peu dense.

```

### practice
- **Fichier** : `03_progressions/supports/terminale/T07/T07_TD_graphes_modelisation_listes_matrices.md`
- **Ancre** : `#exercice-3`
- **Citation** : Consigne : calculer degré sortant ; traiter aussi `arête non orientée` si nécessaire....

**Extrait** :
```
### Exercice 3
- Type : production/écriture.
- Capacité officielle : T-STRUCT-05C.
- Données : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`. ; jeu_exercice=gamma
- Consigne : calculer degré sortant ; traiter aussi `arête non orientée` si nécessaire.
- Réponse attendue : matrice 4x4 -> 16 cases.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `arête non ori
```

### correction
- **Fichier** : `03_progressions/supports/terminale/T07/T07_corrige_graphes_modelisation_listes_matrices.md`
- **Ancre** : `#exercice-3`
- **Citation** : Réponse attendue : matrice 4x4 -> 16 cases....

**Extrait** :
```
### Exercice 3
- Réponse attendue : matrice 4x4 -> 16 cases.
- Méthode : calculer degré sortant.
- Cas limite : arête non orientée.
```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 12. T-STRUCT-05B (FRAIS) — Ecrire l'implémentation d'un graphe par matrice d'adjacence.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/terminale/T07/T07_cours_graphes_modelisation_listes_matrices.md`
- **Ancre** : `#exemples-corrigés`
- **Citation** : Méthode : remplir matrice 0/1.
- Résultat attendu : ligne A : colonnes B et C valent 1.
- Contrôle : capacité T-STRUCT-05B et cas limite `boucle A->A`...

**Extrait** :
```
## Exemples corrigés
### Exemple corrigé 1
- Donnée : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`.
- Méthode : lister voisins sortants.
- Résultat attendu : A -> [B,C], B -> [D], C -> [D], D -> [B].
- Contrôle : capacité T-STRUCT-05A et cas limite `sommet isolé E`.
### Exemple corrigé 2
- Donnée : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`.
- Méthode : remplir matrice 0/1.
- Résultat attendu : ligne A : colonnes B et C valent 1.
- Contrôle : capacité T-STRUCT-05B et cas limite `boucle A->A`.
### Exemple corrigé 3
```

### practice
- **Fichier** : `03_progressions/supports/terminale/T07/T07_TD_graphes_modelisation_listes_matrices.md`
- **Ancre** : `#exercice-2`
- **Citation** : Consigne : remplir matrice 0/1 ; traiter aussi `boucle A->A` si nécessaire....

**Extrait** :
```
### Exercice 2
- Type : production/écriture.
- Capacité officielle : T-STRUCT-05B.
- Données : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`. ; jeu_exercice=beta
- Consigne : remplir matrice 0/1 ; traiter aussi `boucle A->A` si nécessaire.
- Réponse attendue : ligne A : colonnes B et C valent 1.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `boucle A->A`.
```

### correction
- **Fichier** : `03_progressions/supports/terminale/T07/T07_corrige_graphes_modelisation_listes_matrices.md`
- **Ancre** : `#exercice-2`
- **Citation** : Réponse attendue : ligne A : colonnes B et C valent 1.
- Méthode : remplir matrice 0/1.
- Cas limite : boucle A->A....

**Extrait** :
```
### Exercice 2
- Réponse attendue : ligne A : colonnes B et C valent 1.
- Méthode : remplir matrice 0/1.
- Cas limite : boucle A->A.
```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 13. P-DATA-CONSTR-02B (FRAIS) — Construire un tableau par compréhension.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P04/P04_trace_types_construits_complement.md`
- **Ancre** : `#méthode-2---construire-un-tableau-par-compréhension-p-data-constr-02b`
- **Citation** : **Modèle** :

```python
resultat = [expression for variable in iterable]
resultat = [expression for variable in iterable if condition]
```...

**Extrait** :
```
## Méthode 2 - Construire un tableau par compréhension (P-DATA-CONSTR-02B)

**Principe** : une liste par compréhension construit un nouveau tableau en une ligne lisible.

**Modèle** :

```python
resultat = [expression for variable in iterable]
resultat = [expression for variable in iterable if condition]
```

**Exemples clés** :
```

### practice
- **Fichier** : `03_progressions/supports/premiere/P04/P04_td_types_construits_complement.md`
- **Ancre** : `#exercice-2---tableau-par-compréhension-p-data-constr-02b`
- **Citation** : **Question 2c.** Écrire sur papier une compréhension qui produit la liste des cubes des entiers de 1 à 8, soit `[1, 8, 27, 64, 125, 216, 343, 512]`....

**Extrait** :
```
## Exercice 2 - Tableau par compréhension (P-DATA-CONSTR-02B)

**Question 2a.** Déterminer le contenu de chaque liste :

```python
L1 = [x ** 2 for x in range(10)]
L2 = [k * 3 for k in range(1, 6)]
L3 = [c.upper() for c in "python"]
```

**Question 2b.** Déterminer le contenu de la liste avec filtre :

```

### correction
- **Fichier** : `03_progressions/supports/premiere/P04/P04_corrige_types_construits_complement.md`
- **Ancre** : `#exercice-2---tableau-par-compréhension-p-data-constr-02b`
- **Citation** : ```python
cubes = [x ** 3 for x in range(1, 9)]
```...

**Extrait** :
```
### Exercice 2 - Tableau par compréhension (P-DATA-CONSTR-02B)

**2a.**

- `L1 = [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]`
- `L2 = [3, 6, 9, 12, 15]`
- `L3 = ['P', 'Y', 'T', 'H', 'O', 'N']`

**2b.**

`L4 = [3, 6, 9, 12, 15, 18]` (les multiples de 3 entre 1 et 20).

```

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---
