# Conformite BO 2026 — Manuel 1SPE Mathematiques

> **VALIDATION HUMAINE FINALE requise avant commercialisation.**
> Conformite verifiee le 18 juillet 2026 sur le texte officiel
> `sources/BO2026_1SPE_specialite.pdf` (NOR MENE2602917A, BO n 14 du 02-04-2026).

## Methode

Extraction texte par `pdftotext -layout` sur le PDF officiel depose.
Confrontation capacite par capacite avec les referentiels `capacites_1SPE_*.json`.
Reference croisee avec `BO2019_1SPE_specialite.pdf` pour les chapitres ancres 2019.

## Tableau de conformite

| Chapitre | Verdict | Detail |
|---|---|---|
| 1SPE-SUITES | **CONFORME** (reformulations mineures) | Contenus et capacites identiques au BO 2026 section "Suites numeriques, modeles discrets" (l.333-388). Demonstrations exigibles : terme general arith/geo, 1+2+...+n, 1+q+...+q^n. Ajout BO 2026 : motifs geometriques/combinatoires dans modes de generation. |
| 1SPE-SECOND-DEGRE | **CONFORME** (reformulations) | Section "Equations, fonctions polynomes du second degre" (l.370-388). Forme canonique, discriminant, factorisation, signe. BO 2026 ajoute : "diversifier les strategies de factorisation (racine evidente, somme/produit, identite remarquable, formules generales)". Demonstration exigible : resolution equation 2nd degre. |
| 1SPE-DERIVATION-LOCAL | **CONFORME** | Section "Derivation — Point de vue local" (l.433-455). Taux de variation, nombre derive, tangente, approximation lineaire. |
| 1SPE-DERIVATION-GLOBAL | **AJOUTS REQUIS** | Section "Derivation — Point de vue global" + "Variations et courbes" (l.456-490). Conforme pour : fonction derivee, operations, signe/variations, extremums, optimisation. **Manquent** : (1) fonctions paires/impaires + traduction geometrique ; (2) fonction valeur absolue : derivabilite en 0 ; (3) pour n dans Z, derivee de x^n. |
| 1SPE-EXPONENTIELLE | **CONFORME** | Section "Fonction exponentielle" (l.479-500). Definition, proprietes algebriques, e^(at), signe, variations. Demonstration : unicite admise. |
| 1SPE-TRIGONOMETRIE | **HORS PROGRAMME PARTIEL** | Section "Trigonometrie" (l.503-518). **Maintenu** : C1 (cercle, radian, enroulement), C2 (valeurs remarquables, angles associes par lecture du cercle). **Retire du programme 1SPE 2026** : C3 (formules d'addition/duplication), C4 (equations trigonometriques), C5 (fonctions cos/sin : variations, periodicite, courbes). Ces contenus passent en Terminale (TSPE v2, programme 2027). |
| 1SPE-PRODUIT-SCALAIRE | **CONFORME** | Section "Calcul vectoriel et produit scalaire" (l.541-561). Projection, cosinus, bilinearite, expression analytique, Al-Kashi, MA.MB. Demonstrations exigibles : Al-Kashi, ensemble MA.MB=0. |
| 1SPE-GEOMETRIE-REPEREE | **CONFORME** | Section "Geometrie reperee" (l.564-578). Vecteur normal, projection orthogonale, equation de cercle. |
| 1SPE-PROBA-COND | **CONFORME** (precision ajoutee) | Section "Probabilites conditionnelles et independance" (l.612-633). BO 2026 precise : "Pour n<=4, repetition de n epreuves de Bernoulli". |
| 1SPE-VARIABLES-ALEATOIRES | **AJOUT REQUIS** | Section "Variables aleatoires reelles" (l.634-667). Conforme pour : VA, loi, esperance, variance, ecart type, linearite. **Manque** : formule de Konig-Huygens (contenu explicite du BO 2026). |

## Detail des ecarts

### Ecarts de contenu (correctifs requis)

| # | Chapitre | Type | Contenu | Action |
|---|---|---|---|---|
| E1 | DERIVATION-GLOBAL | AJOUT | Fonctions paires, impaires : representation algebrique et graphique, traduction geometrique | Ajouter section cours + 2-3 exercices |
| E2 | DERIVATION-GLOBAL | AJOUT | Fonction valeur absolue : etude de la derivabilite en 0 | Ajouter dans cours C1 ou C2 |
| E3 | DERIVATION-GLOBAL | VERIFIER | Pour n dans Z, derivee de x^n | Verifier si present dans le cours actuel |
| E4 | VARIABLES-ALEATOIRES | AJOUT | Formule de Konig-Huygens : V(X) = E(X^2) - [E(X)]^2 | Ajouter dans cours C2 + exercices |
| E5 | TRIGONOMETRIE | RETRAIT | Formules d'addition cos(a+b), sin(a+b), duplication | Deplacer vers backlog TSPE v2 |
| E6 | TRIGONOMETRIE | RETRAIT | Equations trigonometriques cos(x)=a, sin(x)=a | Deplacer vers backlog TSPE v2 |
| E7 | TRIGONOMETRIE | RETRAIT | Fonctions cos/sin : variations, periodicite, courbes, derivees | Deplacer vers backlog TSPE v2 |

### Ecarts de formulation seule (JSON a mettre a jour)

Les `libelle_bo` dans les 10 referentiels doivent etre reecrites comme citations exactes du BO 2026 (actuellement formulations agent, pas citations verbatim).

## Diff 2019 vs 2026 pour les chapitres ancres 2019

### Suites
- **Maintenu** : modes de generation, arithmetiques, geometriques, sommes, sens de variation
- **Ajoute 2026** : motifs geometriques/combinatoires dans les modes de generation ; notation u(n) en plus de u_n
- **Reformule** : "sensibilisation a l'idee de limite" (plus explicite en 2026)

### Second degre
- **Maintenu** : forme canonique, discriminant, racines, signe
- **Ajoute 2026** : diversification des strategies de factorisation, lien avec variance
- **Supprime** : rien de significatif

### Trigonometrie
- **Maintenu** : cercle trigonometrique, radian, enroulement, cos/sin d'un reel, valeurs remarquables
- **Supprime en 1SPE** : formules d'addition, equations trigo, etude des fonctions cos/sin
- **Destination** : Terminale (TSPE v2, programme 2027, MENE2602919A)
