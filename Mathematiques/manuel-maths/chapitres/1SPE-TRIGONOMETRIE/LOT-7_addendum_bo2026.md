# LOT-7 Addendum — Coherence post-amputation BO 2026

## Date : 18 juillet 2026

## 1. Capacites restantes vs texte BO 2026

BO 2026, section "Trigonometrie" (l.503-518 de l'extrait) :
- Contenus : cercle trigonometrique, longueur d'arc, radian, enroulement,
  cosinus et sinus d'un nombre reel, valeurs remarquables.
- Capacites attendues : placer un point, determiner cos/sin d'angles associes.
- Demonstration exigible : calcul de cos(pi/4), sin(pi/4), cos(pi/3), sin(pi/3).

Chapitre residuel :
- C1 (cercle/radian) : **conforme** — correspond aux contenus BO
- C2 (valeurs remarquables, angles associes) : **conforme** — correspond aux capacites BO

Rien retire de trop, rien garde de trop.

## 2. Matrice de couverture

| Capacite | Parcours 1 | Parcours 2 | Parcours 3 | Total |
|---|---:|---:|---:|---:|
| C1 | 4 (001-004) | 3 (005-007) | 3 (008-010) | 10 |
| C2 | 4 (011-014) | 3 (015-017) | 3 (018-020) | 10 |
| **Total** | **8** | **6** | **6** | **20** |

Couverture : 2 capacites x 3 parcours = 6 cases, toutes remplies (>= 3 par case).

## 3. Seuil E5 — argument

Le seuil E5 de 50 exercices etait calibre pour 5 capacites (10 ex/capacite).
Le chapitre ne comporte plus que 2 capacites (perimetre BO 2026 reduit).

**Seuil recalibre** : 10 exercices par capacite x 2 capacites = 20 exercices.
Le chapitre atteint exactement ce seuil : 20 exercices + 8 CDP + 20 corriges.
Ratio parcours : 8/6/6 (40%/30%/30%), conforme au ratio 40/40/20 ajuste.

## 4. References pendantes corrigees

| Objet | Reference C3/C4/C5 | Action |
|---|---|---|
| QCM (1SPE-TRIGONOMETRIE-QCM.tex) | Questions Q7-Q15 (C3/C4/C5) | Supprimees, META maj C1-C2 |
| TD fil rouge (07_td_fil_rouge.tex) | Etapes 3-5 | Supprimees, META maj C1-C2 |
| TD contextualise (07_td_contextualise.tex) | META referençait C5 | META maj C1-C2 |
| Formulaire transversal | Table cos/sin + cos²+sin²=1 | OK (programme 1SPE 2026) |
| QCM JSON | capacites_codes C1-C5 | A mettre a jour |

## 5. Reemploi backlog

Le repertoire `backlog_tspe_v2/1SPE-TRIGONOMETRIE/` contient 86 fichiers
(C3: formules addition, C4: equations trigo, C5: fonctions cos/sin).
Note de reemploi inscrite dans `referentiel/capacites_TSPE_TRIGONOMETRIE.json`.

## 6. Verdicts post-correctif

- SymPy : 46 OK, 0 FAIL
- Compilation : 14 pages, PASS
- verify_pdf : PASS
