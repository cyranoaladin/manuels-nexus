# Dossier de revue lead v5 — Post-REM4 (lots A-reliquats, C-complet, D, E, F-gate)

## Resume executif

- **Date** : 2026-07-12
- **Coverage** : 111 needs_review / 3 partial / 0 covered (revue humaine toujours requise)
- **Commits references** : 5d28f83, 900f187, 2cde1a6, 5b43118
- **RVW** : 30/30 constats traites ou requalifies
- **Lots completes** : A-reliquats, C-complet, D, E, F-gate

---

## 1. P-ALGO-03 (RE-JUGE W) — Ecrire un algorithme qui predit la classe d'un element a partir de la classe majoritaire de ses k plus proches voisins.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P13/P13_cours_dichotomie_glouton_knn.md`
- **Ancre** : `#algorithme-des-k-plus-proches-voisins`
- **Citation** : La capacite P-ALGO-03 demande d'ecrire un algorithme qui predit la classe d'un element a partir de la classe majoritaire...

**Extrait** :
```
## Algorithme des k plus proches voisins

La capacite P-ALGO-03 demande d'ecrire un algorithme qui predit la classe d'un element a partir de la classe majoritaire de ses k plus proches voisins.

### Principe
```


### practice
- **Fichier** : `03_progressions/supports/premiere/P13/P13_TD_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-9`
- **Citation** : (9a) calculer la distance euclidienne entre le nouveau point et chaque point d'entrainement ; (9b) identifier les 3 plus...

**Extrait** :
```
### Exercice 9
- Type : production/ecriture.
- Capacite officielle : P-ALGO-03.
- Donnees : donnees d'entrainement = [(2, 3, "A"), (5, 4, "B"), (1, 1, "A"), (8, 7, "B"), (3, 2, "A")]. Nouveau point = (4, 3). k = 3. ; jeu_exercice=iota
- Consigne : (9a) calculer la distance euclidienne entre le nouveau point et chaque point d'entrainement ; (9b) identifier les 3 plus proches voisins ; (9c) determiner la classe predite par vote majoritaire ; (9d) que se passe-t-il si k = 2 et les deux voisins sont de classes differentes ?
```


### correction
- **Fichier** : `03_progressions/supports/premiere/P13/P13_corrige_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-9`
- **Citation** : Reponse attendue : distances calculees, 3 plus proches = A(3,2) B(5,4) A(2,3), vote A=2 B=1, classe "A"....

**Extrait** :
```
### Exercice 9
- Capacite mobilisee : P-ALGO-03.
- Reponse attendue : distances calculees, 3 plus proches = A(3,2) B(5,4) A(2,3), vote A=2 B=1, classe "A".
- Methode : distance euclidienne, tri, vote majoritaire.
- Cas limite : k=2 avec egalite de vote -> resultat indetermine.
```


### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 2. P-ALGO-04 (RE-JUGE W) — Montrer la terminaison de la recherche dichotomique a l'aide d'un variant de boucle.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P13/P13_cours_dichotomie_glouton_knn.md`
- **Ancre** : `#exemple-corrige-2---variant-de-dichotomie-p-algo-04`
- **Citation** : Methode : montrer que le variant V = droite - gauche + 1 (nombre de candidats) decroit strictement a chaque etape.

### practice
- **Fichier** : `03_progressions/supports/premiere/P13/P13_TD_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-2`
- **Citation** : Consigne : montrer que le variant V = droite - gauche + 1 decroit strictement a chaque etape ; traiter aussi `cible absente` si necessaire.

### correction
- **Fichier** : `03_progressions/supports/premiere/P13/P13_corrige_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-2`
- **Citation** : Reponse attendue : V decroit de 6 a 3 -> terminaison.

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 3. P-ALGO-05 (RE-JUGE W) — Resoudre un probleme grace a un algorithme glouton.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P13/P13_cours_dichotomie_glouton_knn.md`
- **Ancre** : `#exemple-corrige-3---glouton-p-algo-05`
- **Citation** : Methode : prendre la plus grande piece possible a chaque etape.

### practice
- **Fichier** : `03_progressions/supports/premiere/P13/P13_TD_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-3`
- **Citation** : Consigne : appliquer l'algorithme glouton pour rendre la monnaie.

### correction
- **Fichier** : `03_progressions/supports/premiere/P13/P13_corrige_dichotomie_glouton_knn.md`
- **Ancre** : `#exercice-3`
- **Citation** : Reponse attendue : 28=10+10+5+2+1 (5 pieces).

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 4. P-IHM-03B (RE-JUGE W) — Distinguer ce qui est memorise dans le client et retransmis au serveur.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/premiere/P08/P08_cours_web_http_dom_formulaires.md`
- **Ancre** : `#memorisation-et-transmission-des-donnees-entre-client-et-serveur`
- **Citation** : Un cookie est un petit fichier texte stocke par le navigateur.

### practice
- **Fichier** : `03_progressions/supports/premiere/P08/P08_TD_html_css_dom.md`
- **Ancre** : `#exercice-5`
- **Citation** : Consigne : classer chaque mecanisme (cookie, localStorage, sessionStorage).

### correction
- **Fichier** : `03_progressions/supports/premiere/P08/P08_corrige_web_http_dom_formulaires.md`
- **Ancre** : `#exercice-5`
- **Citation** : Reponse attendue : cookie -> stocke cote client ET retransmis automatiquement au serveur.

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 5. T-LANG-05 (RE-JUGE W) — Savoir repondre aux causes typiques de bugs.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/terminale/T14/T14_cours_modularite_api_paradigmes_bugs.md`
- **Ancre** : `#savoir-faire-et-methodes-operationnelles`
- **Citation** : ecrire un test qui reproduit un bug.

### practice
- **Fichier** : `03_progressions/supports/terminale/T14/T14_TD_modularite_api_paradigmes_bugs.md`
- **Ancre** : `#exercice-6`
- **Citation** : Consigne : identifier la cause du bug (effet de bord a l'import).

### correction
- **Fichier** : `03_progressions/supports/terminale/T14/T14_corrige_modularite_api_paradigmes_bugs.md`
- **Ancre** : `#exercice-6`
- **Citation** : Reponse attendue : cause : effet de bord a l'import.

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 6. T-STRUCT-05C (RE-JUGE W) — Ecrire l'implementation d'un graphe par listes de successeurs ou predecesseurs.
- **Proofs** : 3/3

### course
- **Fichier** : `03_progressions/supports/terminale/T07/T07_cours_graphes_modelisation_listes_matrices.md`
- **Ancre** : `#savoir-faire-et-methodes-operationnelles`
- **Citation** : traduire une situation en sommets et aretes.

### practice
- **Fichier** : `03_progressions/supports/terminale/T07/T07_TD_graphes_modelisation_listes_matrices.md`
- **Ancre** : `#exercice-3bis`
- **Citation** : Consigne : ecrire l'implementation du graphe par liste de successeurs.

### correction
- **Fichier** : `03_progressions/supports/terminale/T07/T07_corrige_graphes_modelisation_listes_matrices.md`
- **Ancre** : `#exercice-3bis`
- **Citation** : Reponse attendue : `{A: [B, C], B: [D], C: [D], D: [B]}`.

### Grille
- [ ] Q1 Ancre correcte
- [ ] Q2 Enseigne au niveau du libelle
- [ ] Q3 Meme verdict
- Observation : ___
---

## 7. T-LANG-04A (PARTIAL) — Distinguer sur des exemples les paradigmes imperatif, fonctionnel et objet.
- **Proofs** : 1/3

### course
- **Fichier** : `None`
- **Ancre** : `None`
- **Citation** : N/A...

### practice
- **Fichier** : `03_progressions/supports/terminale/T04/T04_td_recursivite.md`
- **Ancre** : `#exercice-9`
- **Citation** : on donne trois implementations de la somme d'une liste.

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

## Reponse aux 30 RVW de la revue

Voir le detail complet dans `docs/rvw_responses.md`.

| # | Item | Statut | Ref |
|---|------|--------|-----|
| 1 | RVW-001 motif "Reponse attendue" | REQUALIFIE | Structural par design |
| 2 | RVW-002 refs pendantes P08 | TRAITE | commit 5b43118 |
| 3 | RVW-003 TP P08 differencies | TRAITE | commit 5b43118 |
| 4 | RVW-004 decalage exercice compteur | REQUALIFIE | Cosmetique |
| 5 | RVW-005 bareme P04 complement | REQUALIFIE | Bonus documentes |
| 6 | RVW-006 redistribution P02 bareme | REQUALIFIE | Total identique 20/20 |
| 7 | RVW-007 corrige P13 TP Q3 | TRAITE | commit 5b43118 |
| 8 | RVW-008 remediation P13 P-ALGO-03->04 | TRAITE | commit 5b43118 |
| 9 | RVW-009 distances k-NN chiffrees | TRAITE | commit 5b43118 |
| 10 | RVW-010 exercices 5/6 TD P08 | TRAITE | commit 5b43118 |
| 11 | RVW-011 evaluation P08 capacites | REQUALIFIE | Lot auteur futur |
| 12 | RVW-012 T07 cours exemples 3/4 | TRAITE | commit 5b43118 |
| 13 | RVW-013 T09 eval matrice | TRAITE | commit 5b43118 |
| 14 | RVW-014 T14 cours taches | TRAITE | commit 5b43118 |
| 15 | RVW-015 evaluation T14 capacites | REQUALIFIE | Lot auteur futur |
| 16 | RVW-016 T04 TCO corrige | TRAITE | commit 5d28f83 |
| 17 | RVW-017 P08 domaine->origine | TRAITE | commit 5d28f83 |
| 18 | RVW-018 2048 chars nuance | TRAITE | commit 5d28f83 |
| 19 | RVW-019 Redis qualifie | TRAITE | commit 5d28f83 |
| 20 | RVW-020 ARPANET/EDVAC nuances | TRAITE | commit 900f187 |
| 21 | RVW-021 T-LANG-05 re-juge | TRAITE | commit 5b43118 |
| 22 | RVW-022 T-STRUCT-05C re-juge | TRAITE | commit 5b43118 |
| 23 | RVW-023 T-BDD-02 re-juge | TRAITE | commit 5b43118 |
| 24 | RVW-024 T-LANG-03C re-juge | TRAITE | commit 5b43118 |
| 25 | RVW-025 T-ALGO-03 re-juge | TRAITE | commit 5b43118 |
| 26 | RVW-026 P-ALGO-01A re-juge | TRAITE | commit 5b43118 |
| 27 | RVW-027 variante eleve P13 TD | TRAITE | commit 5b43118 |
| 28 | RVW-028 variante eleve P13 TP | TRAITE | commit 5b43118 |
| 29 | RVW-029 canon P13 TP Q3 | TRAITE | commit 5b43118 |
| 30 | RVW-030 motif structurel TD/TP | REQUALIFIE | Gate check_eleve |

**Bilan** : 23 TRAITE, 7 REQUALIFIE, 0 en dette.
