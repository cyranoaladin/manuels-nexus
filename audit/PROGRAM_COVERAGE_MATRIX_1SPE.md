# Matrice programme ↔ manuel — 1SPE (édition 2026-2027)

Recalculée directement contre le texte officiel `MENE2602917A` (BO n°14 du
2 avril 2026), déposé et empreinté sous
`Mathematiques/manuel-maths/sources/txt/BO2026_1SPE_specialite.txt`
(`sha256:4e70f1989cdb47caf184cb138d839799e895fcdc5addec3737f0216b6bfa33df`).
`Mathematiques/manuel-maths/referentiel/CONFORMITE_BO2026.md` a servi de
point de départ mais n'a **pas** été repris comme preuve intrinsèque — cette
matrice atomise à nouveau le texte, capacité par capacité, et confronte
chaque atome au référentiel local ET au contenu réel des fichiers. Détail
complet, ligne par ligne, dans `audit/PROGRAM_COVERAGE_MATRIX_1SPE.json`
(73 lignes).

## Chiffres finaux

```
TOTAL_MANDATORY_ATOMS      = 61
STRUCTURALLY_MAPPED        = 54   (capacité identifiée, fichier existe — revue scientifique/pédagogique non encore faite, donc PAS "FULL")
FULL                       = 0    (aucune ligne n'a encore passé l'audit scientifique + pédagogique requis par la règle T2 §10)
PARTIAL                    = 3    (mappé mais écart de portée/libellé entre référentiel local et texte BO — à trancher)
MISSING                    = 1    (aucune capacité dédiée : sensibilisation intuitive à la notion de limite, SUITES)
TRANSVERSAL (hors grille)  = 3    (compétences transversales du BO — logique/ensembles, notion de liste, automatismes — non scopées à un seul chapitre, méthode d'audit différente requise)

Non obligatoire (mandatory=false), 12 lignes :
  OUT_OF_SCOPE_WITH_PROOF  = 6    (histoire des mathématiques, approfondissements explicitement facultatifs du BO)
  WRONG_YEAR               = 3    (TRIGONOMETRIE C3/C4/C5 — retirés du programme 1SPE 2026)
  UNSUPPORTED_CLAIM        = 2    (VARIABLES-ALEATOIRES C3/C4 — loi binomiale, absente du texte BO2026)
  STRUCTURALLY_MAPPED      = 1    (méthode de Monte-Carlo, "exemple d'algorithme" — enrichissement correctement présent)
```

`FULL = 0` n'est pas une régression : c'est la règle explicite du mandat
(coverage ≠ quality — un renvoi structurel ne vaut pas FULL tant que l'audit
scientifique et pédagogique n'est pas passé). `STRUCTURALLY_MAPPED = 54/61`
signifie que la quasi-totalité du programme obligatoire a un point
d'ancrage réel et vérifiable dans le manuel — le travail restant est la
revue de contenu (T3/T4), pas la création de contenu manquant.

## Trois trouvailles réelles

### 1. WRONG_YEAR — `1SPE-TRIGONOMETRIE-C3/C4/C5` (référentiel en dérive)

`referentiel/capacites_1SPE_TRIGONOMETRIE.json` liste encore trois
capacités (formules d'addition/duplication, équations trigonométriques,
étude des fonctions cos/sin) absentes du texte BO2026. Le contenu réel a
déjà été retiré (seuls `cours/10_C1_*.tex` et `11_C2_*.tex` existent dans
le chapitre — confirmé, pas de fichiers `12_C3`/`13_C4`/`14_C5`), cohérent
avec `CONFORMITE_BO2026.md` (E5-E7, "chapitre recompilé 16p"). Seul le
fichier `referentiel/*.json` (source de vérité protégée par
`Mathematiques/manuel-maths/CLAUDE.md`, non modifiable sans instruction
explicite) n'a pas été mis à jour. **Correction mécanique recommandée**
(retirer C3-C5 du référentiel local) — pas une décision éditoriale, une
synchronisation de métadonnée avec un retrait déjà exécuté et déjà décidé.

### 2. UNSUPPORTED_CLAIM — `1SPE-VARIABLES-ALEATOIRES-C3/C4` (loi binomiale)

`referentiel/capacites_1SPE_VARIABLES_ALEATOIRES.json` cite "loi de
Bernoulli et loi binomiale" comme `libelle_bo` (donc comme capacité
officielle BO). Le mot « binomiale » **n'apparaît nulle part** dans le
texte MENE2602917A (recherche exhaustive sur le texte déposé). Le programme
2026 mentionne seulement, dans Probabilités conditionnelles, "pour n≤4,
répétition de n épreuves de Bernoulli" — sans jamais formaliser de loi
binomiale nommée ni ses formules d'espérance/variance. Du contenu
substantiel existe pourtant : `cours/12_C3_bernoulli_binomiale.tex`,
`cours/13_C4_esperance_binomiale.tex` (statut META actuel : `generated`,
donc déjà non approuvé), exercices, corrigés, remédiation
(`remediation/1SPE-VARALEA-RE-C3.tex`), validations sympy/similarity.
`CONFORMITE_BO2026.md` n'a pas détecté cet écart (a validé le chapitre
« CONFORME » sur C1/C2 sans vérifier que C3/C4 sont réellement fondés sur
le BO).

**Aucun contenu supprimé dans ce lot.** Décision éditoriale réelle
nécessaire : reclassifier en `\approfondissement` explicite, déplacer en
backlog comme pour TRIGONOMETRIE C3-C5, ou conserver avec justification
pédagogique documentée (cohérence avec la suite du cursus, préparation à
TCOMPL/TSPE où la loi binomiale reste au programme). **HUMAN GATE.**

### 3. MISSING — sensibilisation à la notion de limite (SUITES)

Le BO demande une "sensibilisation à l'idée de limite, finie ou infinie,
ou l'absence de limite" sur les suites, sans formalisation. Aucune capacité
dédiée dans le référentiel local (C1-C7 de SUITES ne la nomment pas
explicitement). Peut être diffuse dans plusieurs fichiers existants
(`14_C5_variations.tex`, `16_C7_algorithmique.tex`) — à vérifier lors de
l'audit de contenu, pas nécessairement un vide total, mais structurellement
non tracé.

## Trois écarts de portée à trancher (PARTIAL)

- **EXPONENTIELLE-C3** : le référentiel ajoute "connaître ses limites en
  ±∞", non explicitement listé comme capacité BO distincte dans le texte
  fourni.
- **EXPONENTIELLE-C5** : le référentiel formule "résoudre des équations et
  inéquations exponentielles" ; le texte BO fourni ne liste pas cette
  capacité nommément dans cette section.
- **GEOMETRIE-REPEREE-C4** : le référentiel parle de "positions relatives
  (parallélisme, intersection, tangence)" ; le texte BO parle de
  "projection orthogonale d'un point sur une droite" — portées différentes,
  à vérifier contre le contenu réel du fichier.

## Ce que cette matrice ne couvre pas encore

- Audit scientifique (exactitude des démonstrations, du code Python, des
  valeurs numériques) — T4, non commencé pour 1SPE.
- Audit pédagogique (progression, qualité des exercices, cohérence
  cours-méthodes-exercices-évaluation) — T3, non commencé.
- EXAM_ALIGNMENT détaillé (répartition automatismes/exercices dans le
  manuel en cohérence avec la structure 6pts QCM + 14pts exercices de
  l'épreuve anticipée) — signalé comme risque dans la ligne Automatismes,
  pas encore audité.
- Les cinq autres manuels (TSPE, TCOMPL, TEXPERTES, 1NSI, TNSI).

## Prochaine étape

Lancer l'audit scientifique + pédagogique des chapitres déjà
`STRUCTURALLY_MAPPED` (prioriser forte densité d'exercices), en parallèle
de la construction de la matrice pour les cinq autres manuels.
