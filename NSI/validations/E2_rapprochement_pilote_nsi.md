# E.2.3 — Tableau de rapprochement 1NSI-TYPES-CONSTRUITS vs PILOTE_A_VALIDER.md

Date : 16 juillet 2026.

## Methode de decomptage

Comptage des lignes `\input{...}` dans le fichier maitre
`build/1NSI-TYPES-CONSTRUITS/1NSI-TYPES-CONSTRUITS_complet.tex` (103 lignes, genere par `scripts/assemble.py`).
Les corriges ne sont pas inclus dans la variante `complet` ; comptes sur disque.
Les questions QCM sont comptees par grep de `\textbf{Q` dans les fichiers QCM.

**Note sur les TD et le projet** : les TD sont stockes dans `cours/07_td*.tex`
(et non dans un repertoire `td/` separe) ; le projet est dans `projet/`. Un
comptage par repertoire seul (cherchant `td/` ou `projets/`) produit un faux zero.
La methode retenue est le decompte des `\input` du maitre, lignes 95–97 :
- l.95 : `\input{chapitres/1NSI-TYPES-CONSTRUITS/cours/07_td1_station_meteo.tex}`
- l.96 : `\input{chapitres/1NSI-TYPES-CONSTRUITS/cours/07_td2_classement_esport.tex}`
- l.97 : `\input{chapitres/1NSI-TYPES-CONSTRUITS/projet/1NSI-TC-PROJET.tex}`

## Tableau par type d'objet

| Type d'objet | PILOTE attendu | Constate (maitre .tex) | Constate (disque) | Ecart |
|---|---:|---:|---:|---|
| Cours (C1-C5) | 5 sections | 5 (l.5-9) | 5 | 0 |
| Methodes (M1-M5) | 5 | 5 (l.10-14) | 5 | 0 |
| Exercices | 55 | 55 (l.15-69) | 55 | 0 |
| Corriges | 55 | 0 (non inclus variante complet) | 55 | 0 |
| Coups de pouce | 24 | 24 (l.70-93) | 24 | 0 |
| QCM diagnostique | 16 questions | 1 fichier DIAG (l.97) | 1 | 0 (*) |
| QCM chapitre | (inclus ci-dessus) | 1 fichier QCM (l.98) | 1 | 0 |
| Remediation | 5 fiches R1-R5 | 1 fichier REM (l.101) | 1 | 0 (**) |
| Evaluations (A + B) | 2 | 2 (l.99-100) | 2 | 0 |
| TD | 2 | 2 (l.95-96) | 2 | 0 (***) |
| Projet | 1 | 1 (l.97) | 1 | 0 |
| Version amenagee (F11) | 1 | 0 (non inclus variante complet) | 1 | 0 |
| **Total \input** | | **97** | | |
| **Total fichiers .tex sur disque** | | | **153 (+amenagee)** | |
| **PDF** | 641 Ko | 213 Ko, 34 p. | | Voir E.2.5 |

(*) Le QCM diagnostique contient 16 questions dans un fichier unique ; le comptage
par question dans PILOTE_A_VALIDER.md (16) correspond au nombre de `\textbf{Q`
dans `qcm/1NSI-TC-QCM-DIAG.tex`.

(**) La remediation est regroupee dans un fichier unique `1NSI-TC-REM.tex` contenant
5 sections (R1 a R5). Ce regroupement differe de la convention maths (1 fichier/fiche)
mais le contenu est identique a l'attendu.

(***) Le precedent comptage « td 0 / projets 0 » etait un artefact de decomptage :
le parcours de repertoires ne comptait ni les TD stockes sous `cours/07_td*.tex`
ni le projet sous `projet/`. L'inventaire reellement present est identique a
l'attendu (2 TD + 1 projet), confirme par les lignes 95–97 du maitre et par
inspection sur disque des fichiers `cours/07_td1_station_meteo.tex`,
`cours/07_td2_classement_esport.tex` et `projet/1NSI-TC-PROJET.tex`.

## Verdict

Inventaire objet : **0 ecart** entre PILOTE_A_VALIDER.md et le maitre .tex.
L'ecart de taille PDF (641 -> 213 Ko) est analyse dans le livrable E.2.4
(`Mathematiques/manuel-maths/validations/E2/diff_visuel_pages.md`, section NSI).
