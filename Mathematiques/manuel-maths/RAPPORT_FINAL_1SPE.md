# RAPPORT FINAL — Manuel de Mathematiques Premiere Specialite

## Date : 18 juillet 2026

---

## 1. Inventaire complet

### Chapitres (10)

| # | Chapitre | Exercices | VERIFY OK | Pages (chap) | Tag |
|---|---|---:|---:|---:|---|
| 1 | Suites | 49 | ~140 | 82 | chap/1SPE-SUITES-v1 |
| 2 | Second degre | 42 | ~140 | 65 | chap/1SPE-SECOND-DEGRE-v1 |
| 3 | Derivation locale | 30 | ~90 | 39 | chap/1SPE-DERIVATION-LOCAL-v1 |
| 4 | Derivation globale | 50 | 146 | 46 | chap/1SPE-DERIVATION-GLOBAL-v1 |
| 5 | Exponentielle | 50 | 119 | 46 | chap/1SPE-EXPONENTIELLE-v1 |
| 6 | Trigonometrie | 50 | 116 | 33 | chap/1SPE-TRIGONOMETRIE-v1 |
| 7 | Produit scalaire | 50 | 119 | 30 | chap/1SPE-PRODUIT-SCALAIRE-v1 |
| 8 | Geometrie reperee | 50 | 117 | 33 | chap/1SPE-GEOMETRIE-REPEREE-v1 |
| 9 | Probabilites conditionnelles | 50 | 117 | 31 | chap/1SPE-PROBA-COND-v1 |
| 10 | Variables aleatoires | 50 | 117 | 37 | chap/1SPE-VARIABLES-ALEATOIRES-v1 |
| | **Total** | **~471** | **~1221** | **442** | |

### Objets par type (par chapitre type, x10)
- Contrat : 10
- Dossier curation : 10
- Cours (C1-C5 + TD) : ~70 fichiers
- Methodes : 50
- Exercices : ~471
- Corriges : ~471
- Coups de pouce (CDP) : ~180
- QCM : 20 (10 tex + 10 json)
- Remediation : 100 (50 FR + 50 RE)
- Evaluations : 40 (10 x (A + A-corrige + B + B-corrige))
- Rapports LOT : ~80

### Blocs transversaux
- Page de garde, avant-propos, mode d'emploi, formulaire, memo Python, index capacites

### Variantes assemblees

| Variante | Pages | Taille |
|---|---:|---:|
| Professeur (tout) | 445 | 2.1 Mo |
| Eleve (sans corriges) | 399 | 1.9 Mo |

---

## 2. Tableau des gates

| Gate | Statut | Detail |
|---|---|---|
| verify_sympy (R2) | PASS | ~1221 assertions OK, 0 FAIL residuel |
| verify_pdf | PASS | 10/10 chapitres + 2 variantes manuel |
| Compilation LaTeX (R6) | PASS | 10/10 chapitres, 2 variantes |
| Charte sync | PASS | 7/7 fichiers identiques Maths=NSI |
| Resolution aveugle A+B | PASS | 10/10 chapitres, 0 divergence |
| CI GitHub Actions | PASS | Tous les pushs CI verte |
| Non-regression cls (LF.0) | PASS | 10/10 recompilent apres ajouts |

---

## 3. Validations humaines en attente (BLOQUANT COMMERCIALISATION)

Voir `A_VALIDER_HUMAIN.md` pour la liste complete.

### Critiques
- [ ] **BO 2026** : texte absent du depot, 10/10 referentiels A_VALIDER_HUMAIN
- [ ] **Contrats de chapitre** : validation enseignant
- [ ] **Specimen v4.1** : rendu imprime

### Non bloquantes pour le contenu
- [ ] Logo Nexus Reussite definitif
- [ ] Couleurs par chapitre (chapcolor unique actuellement)
- [ ] Temps verifies sur eleves reels

---

## 4. Cout cumule estime

| Poste | Cout |
|---|---|
| 10 chapitres (LOT 0-7 chacun) | ~160 $ |
| LF.0-LF.5 | ~15 $ |
| **Total** | **~175 $** |

---

## 5. Tags

- 10 tags `chap/*-v1` (immuables)
- Tag `manuel/1SPE-v1` : marque la completion du manuel Premiere
