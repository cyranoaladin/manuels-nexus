# Matrice programme ↔ manuel — TNSI (édition 2026-2027)

Recalculée directement contre le texte officiel `MENE1921247A` (BO spécial
n°8 du 25 juillet 2019), extrait via `pdftotext -layout` depuis
`NSI/corpus_nsi/00_programmes_officiels/programme_nsi_terminale.pdf`
(SHA-256 `10ce34666edd722a3d8d86642a9f1ac205c7a9d128d6142a17effcba2fb85e69`,
vérifié identique à `docs/programmes/PROGRAMMES_2026_2027.yaml`). Détail
complet, ligne par ligne, dans `audit/PROGRAM_COVERAGE_MATRIX_TNSI.json`
(61 lignes).

## Chiffres finaux

```
TOTAL_MANDATORY_ATOMS      = 60
STRUCTURALLY_MAPPED        = 59   (capacité identifiée, contrat + fichiers existent — pas encore FULL : audit scientifique/pédagogique non fait)
FULL                       = 0
PARTIAL                    = 0
MISSING                    = 1    (Démarche de projet : ≥25% de l'horaire, exigence structurelle du préambule)
TRANSVERSAL (hors grille)  = 1    (Histoire de l'informatique, rubrique explicitement transversale aux 5 autres)
WRONG_YEAR                 = 0
UNSUPPORTED_CLAIM          = 0
```

## Verdict global : référentiel TNSI très fidèle au texte officiel

Contrairement à 1SPE (2 trouvailles réelles — WRONG_YEAR et
UNSUPPORTED_CLAIM), **aucune capacité fabriquée ou obsolète n'a été
trouvée** pour TNSI. Les 6 fichiers `NSI/referentiel/capacites_TNSI_*.json`
et les 6 `contrat.yaml` des chapitres (`statut: valide`, validation humaine
datée 2026-08-06) correspondent presque mot pour mot aux six rubriques du
BO (Histoire de l'informatique, Structures de données, Bases de données,
Architectures matérielles/systèmes/réseaux, Langages et programmation,
Algorithmique) et à leurs 60 capacités attendues, sans ajout ni omission
détectée dans cette passe.

## Trouvaille 1 — MISSING : Démarche de projet

Le préambule du programme exige explicitement : *"Un quart au moins de
l'horaire total de la spécialité est réservé à la conception et à
l'élaboration de projets conduits par les élèves"*, avec des exemples de
thèmes (IA/apprentissage automatique, jeu de stratégie, site Web +
base de données, structure de données complexe, traitement d'image, etc.).

**Aucun contenu de type projet n'a été trouvé** dans les 6 chapitres TNSI
(recherche par nom de fichier/dossier, 0 résultat). Ce n'est pas un défaut
de couverture d'une notion isolée mais un manque structurel de dispositif
pédagogique entier, explicitement exigé par le programme (~25% du volume
horaire). **Décision éditoriale probable (HUMAN GATE)** : format du
dispositif à trancher (dossier-guide de projet transversal, gabarit
d'évaluation, banque de sujets suggérés) plutôt qu'une simple correction
de contenu de cours.

## Trouvaille 2 — observation hors périmètre de cette matrice (signalée, non traitée)

Chaque chapitre TNSI contient, en plus des fichiers `cours/NN_C0X_*.tex`
correctement nommés et alignés sur les capacités du contrat, une seconde
série de fichiers `TNSI-<CHAP>-COURS-NN.tex` (même motif que les 47
doublons `TSPE-*-COURS-NN.tex` déjà nettoyés en T1.4). Contrairement au cas
TSPE, un examen rapide de `TNSI-ALGO-COURS-01.tex` montre un `% META`
valide avec `status: "approved"` (alors que son homologue numérique
`10_C01_arbres_parcours.tex` porte `status: "generated"`) et un corps
quasi identique — ces fichiers ne sont donc probablement PAS inertes
(T1.4 a confirmé `unassembled_objects=0` et `duplicate_assembly_objects=0`
globalement au SHA scellé, ce qui suggère qu'ils sont, d'une manière ou
d'une autre, déjà comptés comme assemblés). **Hors du périmètre de cette
tâche (matrice de programme) — signalé pour investigation séparée**, à
ne pas confondre avec la fermeture déjà scellée de T1 (ne pas rouvrir
T1_STRUCTURAL_INTEGRITY_ZERO sans preuve d'une régression réelle).

## Épreuve — rappel de séparation des namespaces

La redéfinition de l'épreuve TNSI (MENE2516123N, écrit 3h30 pondéré 0,75 +
pratique 1h pondérée 0,25, toutes deux notées /20) est déjà documentée dans
`audit/OFFICIAL_PROGRAM_AUTHORITY_2026_2027.yaml`, namespace
`definition_d_epreuve.TNSI_EPREUVE` — volontairement absente de cette
matrice de programme (namespace `programme_d_enseignement`), conformément
à la règle de séparation programme/épreuve/sujets.

## Ce que cette matrice ne couvre pas encore

- Audit scientifique (exactitude du code Python, des requêtes SQL, des
  algorithmes) et pédagogique — non commencés pour TNSI.
- Vérification que les repères historiques apparaissent bien dans les 5
  chapitres non-HISTOIRE (rubrique transversale du BO).
- Investigation de la double série de fichiers `cours/` (trouvaille 2
  ci-dessus).

## Prochaine étape

Lancer l'audit scientifique + pédagogique des 59 capacités
`STRUCTURALLY_MAPPED`, en parallèle des matrices des manuels restants
(1NSI, TSPE, TCOMPL, TEXPERTES).
