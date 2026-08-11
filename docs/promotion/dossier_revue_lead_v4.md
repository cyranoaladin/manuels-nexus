# Dossier de revue lead v4 — Post-W (regenere)

## Resume executif

- **Coverage** : 113/1/0 (source unique : verdicts campaign)
- **Partial** : T-LANG-04A (1/3)
- **Echantillon** : 7 fiches (6 re-jugees W + 1 partial)

---

## 1. P-ALGO-03 (RE-JUGE W) — Ecrire un algorithme qui prédit la classe d'un élément à partir de la classe majoritaire de ses k plus proches voisins.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P13/P13_cours_dichotomie_glouton_knn.md`
- **Ancre** : `#algorithme-des-k-plus-proches-voisins`
- **Citation** : La capacité P-ALGO-03 demande d'écrire un algorithme qui prédit la classe d'un élément à partir de la classe majoritaire...

**Extrait** :
```
## Algorithme des k plus proches voisins

La capacité P-ALGO-03 demande d'écrire un algorithme qui prédit la classe d'un élément à partir de la classe majoritaire de ses k plus proches voisins.

### Principe
```


### practice
- **Fichier** : `03_progressions/supports/premiere/P13/P13_TD_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-9`
- **Citation** : (9a) calculer la distance euclidienne entre le nouveau point et chaque point d'entraînement ; (9b) identifier les 3 plus...

**Extrait** :
```
### Exercice 9
- Type : production/écriture.
- Capacité officielle : P-ALGO-03.
- Données : données d'entraînement = [(2, 3, "A"), (5, 4, "B"), (1, 1, "A"), (8, 7, "B"), (3, 2, "A")]. Nouveau point = (4, 3). k = 3. ; jeu_exercice=iota
- Consigne : (9a) calculer la distance euclidienne entre le nouveau point et chaque point d'entraînement ; (9b) identifier les 3 plus proches voisins ; (9c) déterminer la classe prédite par vote majoritaire ; (9d) que se passe-t-il si k = 2 et les deux voisins sont de classes différentes ?
```


### correction
- **Fichier** : `03_progressions/supports/premiere/P13/P13_corrige_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-9`
- **Citation** : Réponse attendue : distances calculées, 3 plus proches = A(3,2) B(5,4) A(2,3), vote A=2 B=1, classe "A"....

**Extrait** :
```
### Exercice 9
- Capacité mobilisée : P-ALGO-03.
- Réponse attendue : distances calculées, 3 plus proches = A(3,2) B(5,4) A(2,3), vote A=2 B=1, classe "A".
- Méthode : distance euclidienne, tri, vote majoritaire.
- Cas limite : k=2 avec égalité de vote → résultat indéterminé.
```


### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 2. P-ALGO-04 (RE-JUGE W) — Montrer la terminaison de la recherche dichotomique à l'aide d'un variant de boucle.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P13/P13_cours_dichotomie_glouton_knn.md`
- **Ancre** : `#exemple-corrigé-2---variant-de-dichotomie-p-algo-04`
- **Citation** : Méthode : montrer que le variant V = droite − gauche + 1 (nombre de candidats) décroît strictement à chaque étape.
- Rés...

### practice
- **Fichier** : `03_progressions/supports/premiere/P13/P13_TD_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-2`
- **Citation** : Consigne : montrer que le variant V = droite − gauche + 1 décroît strictement à chaque étape ; traiter aussi `cible abse...

**Extrait** :
```
### Exercice 2
- Type : production/écriture.
- Capacité officielle : P-ALGO-04.
- Données : tableau trié [4, 9, 18, 23, 37, 41] avec cible 37.
- Consigne : montrer que le variant V = droite − gauche + 1 décroît strictement à chaque étape ; traiter aussi `cible absente` si nécessaire.
```


### correction
- **Fichier** : `03_progressions/supports/premiere/P13/P13_corrige_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-2`
- **Citation** : Réponse attendue : V décroît de 6 à 3 → terminaison.
- Méthode : variant.
- Cas limite : cible absente → V=0....

**Extrait** :
```
### Exercice 2
- Capacité mobilisée : P-ALGO-04.
- Réponse attendue : V décroît de 6 à 3 → terminaison.
- Méthode : variant.
- Cas limite : cible absente → V=0.
```


### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 3. P-ALGO-05 (RE-JUGE W) — Résoudre un problème grâce à un algorithme glouton.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P13/P13_cours_dichotomie_glouton_knn.md`
- **Ancre** : `#exemple-corrigé-3---glouton-p-algo-05`
- **Citation** : Méthode : prendre la plus grande pièce possible à chaque étape.
- Résultat attendu : 28 = 10 + 10 + 5 + 2 + 1 (5 pièces)...

### practice
- **Fichier** : `03_progressions/supports/premiere/P13/P13_TD_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-3`
- **Citation** : Consigne : appliquer l'algorithme glouton pour rendre la monnaie ; traiter aussi `pièce 1 absente` si nécessaire.
- Répo...

**Extrait** :
```
### Exercice 3
- Type : production/écriture.
- Capacité officielle : P-ALGO-05.
- Données : pièces disponibles [10, 5, 2, 1] pour montant 28.
- Consigne : appliquer l'algorithme glouton pour rendre la monnaie ; traiter aussi `pièce 1 absente` si nécessaire.
```


### correction
- **Fichier** : `03_progressions/supports/premiere/P13/P13_corrige_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-3`
- **Citation** : Réponse attendue : 28=10+10+5+2+1 (5 pièces).
- Méthode : glouton.
- Cas limite : pièce 1 absente....

**Extrait** :
```
### Exercice 3
- Capacité mobilisée : P-ALGO-05.
- Réponse attendue : 28=10+10+5+2+1 (5 pièces).
- Méthode : glouton.
- Cas limite : pièce 1 absente.
```


### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 4. P-IHM-03B (RE-JUGE W) — Distinguer ce qui est mémorisé dans le client et retransmis au serveur.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P08/P08_cours_web_http_dom_formulaires.md`
- **Ancre** : `#mémorisation-et-transmission-des-données-entre-client-et-serveur`
- **Citation** : Un **cookie** est un petit fichier texte stocké par le navigateur. Le serveur le crée via l'en-tête `Set-Cookie` ; le na...

**Extrait** :
```
## Mémorisation et transmission des données entre client et serveur

La capacité P-IHM-03B demande de distinguer ce qui est mémorisé côté client (cookies, localStorage) de ce qui est retransmis au serveur à chaque requête.

### Cookies
```


### practice
- **Fichier** : `03_progressions/supports/premiere/P08/P08_TD_html_css_dom.md`
- **Ancre** : `#exercice-5`
- **Citation** : Consigne : classer chaque mécanisme (cookie, localStorage, sessionStorage) selon qu'il est retransmis au serveur à chaqu...

**Extrait** :
```
### Exercice 5
- Type : justification.
- Capacité officielle : P-IHM-03B.
- Données : `<form method=post action=/reservation><input id=nom name=nom></form>, URL /club?jour=mercredi`. ; jeu_exercice=epsilon
- Consigne : classer chaque mécanisme (cookie, localStorage, sessionStorage) selon qu'il est retransmis au serveur à chaque requête ou mémorisé uniquement côté client.
```


### correction
- **Fichier** : `03_progressions/supports/premiere/P08/P08_corrige_web_http_dom_formulaires.md`
- **Ancre** : `#exercice-5`
- **Citation** (juge 2026-07-11T19:19:20Z) : Réponse attendue : cookie → stocké côté client ET retransmis automatiquement au serveur selon Domain/Path ; localStorage → stocké côté client uniquement, jamais retransmis au serveur

**Extrait** :
```
### Exercice 5
- Capacité mobilisée : P-IHM-03B.
- Réponse attendue : cookie → stocké côté client ET retransmis automatiquement au serveur selon Domain/Path ; localStorage → stocké côté client uniquement, jamais retransmis au serveur ; donnée de formulaire → transmise au serveur à la soumission uniquement ; session → stockée côté serveur (seul l'identifiant de session transite dans le cookie).
- Méthode : classer chaque mécanisme selon le lieu de stockage (client/serveur) et la retransmission automatique (oui/non, selon Domain et Path pour le cookie).
- Cas limite : en navigation privée le cookie et le localStorage sont effacés à la fermeture ; un cookie expiré (Max-Age écoulé) n'est plus retransmis.
```


### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 5. T-LANG-05 (RE-JUGE W) — Savoir répondre aux causes typiques de bugs.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/terminale/T14/T14_cours_modularite_api_paradigmes_bugs.md`
- **Ancre** : `#savoir-faire-et-méthodes-opérationnelles`
- **Citation** : - écrire un test qui reproduit un bug.
- isoler une dépendance dans un module....

### practice
- **Fichier** : `03_progressions/supports/terminale/T14/T14_TD_modularite_api_paradigmes_bugs.md`
- **Ancre** : `#exercice-6`
- **Citation** : Consigne : identifier la cause du bug (effet de bord à l'import) puis corriger en séparant module et script principal ; ...

**Extrait** :
```
### Exercice 6
- Type : lecture/analyse.
- Capacité officielle : T-LANG-05.
- Données : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`. ; jeu_exercice=zeta
- Consigne : identifier la cause du bug (effet de bord à l'import) puis corriger en séparant module et script principal ; traiter aussi `variable globale mutée` si nécessaire.
```


### correction
- **Fichier** : `03_progressions/supports/terminale/T14/T14_corrige_modularite_api_paradigmes_bugs.md`
- **Ancre** : `#exercice-6`
- **Citation** (juge 2026-07-11T19:19:45Z) : Réponse attendue : cause : effet de bord à l'import — le module exécute du code (print, calcul, mutation de variable globale) dès qu'il est importé ; correction : protéger le code exécutable par `if __name__ == "__main__":` afin qu'il ne s'exécute que lorsque le fichier est lancé directement, pas lors d'un import.

**Extrait** :
```
### Exercice 6
- Capacité mobilisée : T-LANG-05.
- Réponse attendue : cause : effet de bord à l'import — le module exécute du code (print, calcul, mutation de variable globale) dès qu'il est importé ; correction : protéger le code exécutable par `if __name__ == "__main__":` afin qu'il ne s'exécute que lorsque le fichier est lancé directement, pas lors d'un import.
- Méthode : identifier l'instruction provoquant l'effet de bord (appel de fonction ou affectation au niveau module), puis la déplacer dans le bloc `if __name__ == "__main__":`.
- Cas limite : variable globale mutée à l'import — si un autre module importe celui-ci, la mutation se produit une seule fois (au premier import, grâce au cache `sys.modules`), mais l'état global reste pollué pour tous les importateurs.
```


### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 6. T-STRUCT-05C (RE-JUGE W) — Ecrire l'implémentation d'un graphe par listes de successeurs ou prédécesseurs.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/terminale/T07/T07_cours_graphes_modelisation_listes_matrices.md`
- **Ancre** : `#savoir-faire-et-méthodes-opérationnelles`
- **Citation** : - traduire une situation en sommets et arêtes.
- passer de la liste d'adjacence à la matrice.
- comparer le coût mémoire...

### practice
- **Fichier** : `03_progressions/supports/terminale/T07/T07_TD_graphes_modelisation_listes_matrices.md`
- **Ancre** : `#exercice-3bis`
- **Citation** : Consigne : écrire l'implémentation du graphe par liste de successeurs (dictionnaire Python) ; afficher les successeurs d...

**Extrait** :
```
### Exercice 3bis
- Type : production/écriture.
- Capacité officielle : T-STRUCT-05C.
- Données : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`.
- Consigne : écrire l'implémentation du graphe par liste de successeurs (dictionnaire Python) ; afficher les successeurs de chaque sommet.
```


### correction
- **Fichier** : `03_progressions/supports/terminale/T07/T07_corrige_graphes_modelisation_listes_matrices.md`
- **Ancre** : `#exercice-3bis`
- **Citation** (juge 2026-07-11T19:19:33Z) : Méthode : pour chaque arc (u, v) dans arcs, ajouter v à la liste graphe[u] ; initialiser chaque sommet avec une liste vide avant parcours.

**Extrait** :
```
### Exercice 3bis
- Capacité mobilisée : T-STRUCT-05C.
- Réponse attendue : `{A: [B, C], B: [D], C: [D], D: [B]}`.
- Méthode : pour chaque arc (u, v) dans arcs, ajouter v à la liste graphe[u] ; initialiser chaque sommet avec une liste vide avant parcours.
- Cas limite : sommet isolé (pas d'arc sortant) → sa clé existe dans le dictionnaire avec une liste vide.
```


### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 7. T-LANG-04A (PARTIAL) — Distinguer sur des exemples les paradigmes impératif, fonctionnel et objet.
- **Proofs** : 1/3

### course
- **Fichier** : `None`
- **Ancre** : `None`
- **Citation** : N/A...

### practice
- **Fichier** : `03_progressions/supports/terminale/T04/T04_td_recursivite.md`
- **Ancre** : `#exercice-9`
- **Citation** : on donne trois implémentations de la somme d'une liste — impérative (boucle for), fonctionnelle (récursion sans variable...

**Extrait** :
```
### Exercice 9
- Objectif travaillé : O1, O2.
- Capacité officielle : T-LANG-04A.
- Énoncé disciplinaire : on donne trois implémentations de la somme d'une liste — impérative (boucle for), fonctionnelle (récursion sans variable mutable) et objet (méthode d'une classe ListeNombres). (9a) Identifier le paradigme de chaque version. (9b) Citer un trait distinctif de chaque paradigme visible dans le code. (9c) Laquelle risque de déborder la pile pour une liste de 10 000 éléments, et pourquoi ?
- Production attendue : impératif/fonctionnel/objet identifiés, traits (état mutable / récursion / encapsulation), récursion = pile.
```


### correction
- **Fichier** : `None`
- **Ancre** : `None`
- **Citation** : N/A...

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## Reponse aux 16 RVW de la revue v2

| # | Item | Statut | Ref |
|---|------|--------|-----|
| 1 | TD rotation Ex1-8 | TRAITE | PR #99 W-1 |
| 2 | Cours Ex1 tag P-ALGO-03 | TRAITE | PR #99 |
| 3 | Eval Q1 tag P-ALGO-03 | TRAITE | PR #99 |
| 4 | Bareme Q1 tag P-ALGO-03 | TRAITE | PR #99 |
| 5 | Contrat cible 40 absente | TRAITE | PR #99 |
| 6 | Contrat RVW-006 | TRAITE | PR #99 |
| 7 | P-IHM-03B Ex5 misalign | TRAITE | PR #99 W-2 |
| 8 | T-BDD-02 | INFIRME | Contenu correct V-2b |
| 9 | T-STRUCT-05C Ex3 ≠ implem | TRAITE | PR #99 W-2 Ex3bis |
| 10 | T-BDD-01B | INFIRME | Contenu correct V-2b |
| 11 | T-LANG-05 Ex6 tangentiel | TRAITE | PR #99 W-2 |
| 12 | Dossier v3 perime | REMPLACE | Ce dossier v4 |
| 13 | T-LANG-04A partial 1/3 | DETTE | Pas actionnable |
| 14 | Cours cas limites generiques | TRAITE | PR #99 W-1d |
| 15 | TD doublons Ex5-8 | TRAITE | PR #99 donnees variees |
| 16 | Corrige/eval rotation | TRAITE | PR #99+#100 |
