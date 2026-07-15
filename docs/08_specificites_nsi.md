# Manuels NSI Première & Terminale — Workflow de production
## Exploiter le dépôt cyranoaladin/NSI avec la méthodologie du manuel de mathématiques

Version 1.0 — Juillet 2026

---

# PARTIE 1 — AUDIT DE L'EXISTANT : CE QUE LE DÉPÔT NSI APPORTE DÉJÀ

Le dépôt NSI n'est pas une simple source d'inspiration : c'est **60 à 70 % du travail du LOT 0 au LOT 4 déjà réalisé**, sous une forme orientée « séquences de classe » qu'il faut restructurer en forme « manuel d'accompagnement différencié ». Inventaire de ce qui se réutilise :

## 1.1 Actifs directement réutilisables (mapping vers le noyau manuel-maths)

| Actif du dépôt NSI | Équivalent manuel-maths | État | Réutilisation |
|---|---|---|---|
| `00_programmes_officiels/programme_nsi_2019.yaml` | `referentiel/capacites_*.json` | **Fait** | Conversion de format uniquement — le LOT 0 est quasi gratuit |
| `programme_matrix_premiere.md` / `programme_matrix_terminale.md` | Matrice de couverture capacités | Fait | Alimente directement `coverage_report` |
| Canon de séquence (11 fichiers : cours_eleve, trace_ecrite, td, tp, fiche_methode, **aides_progressives**, corrige, guide_professeur, evaluation, qcm.json, projet_associe, python/, tests/) | Les objets du chapitre (9 temps) | **Fait pour le corpus certifié** | Restructuration, pas génération — voir table de transposition §3.2 |
| Campagne de certification substance : 114 capacités, 445 tests exécutables, verdicts `substance_verdict.schema.json` | Gates SymPy + adversarial | **Fait et éprouvé** | Les tests deviennent les blocs VERIFY du manuel ; le schéma de verdict est déjà compatible |
| `substance_reviews/_adversarial/` + `qa_gate_policy.md` | `prompts/verificateur_adversarial.md` + gates | Fait | Le protocole adversarial NSI est antérieur et plus mûr que celui des maths : on aligne les maths dessus, pas l'inverse |
| `human_review_*` (protocol, checklists pédagogie/science/accessibilité, register.csv) | `A_VALIDER_HUMAIN.md` | Fait, plus rigoureux | Adopter tel quel : statuts `needs_review` conservateurs, `published=0` sans revue humaine tracée |
| `sources_catalog.yml` + `scraping_strategy.md` + `scrapping_NSI/` | `sources/registry.yaml` + crawlers | Fait | Fusionner les catalogues ; l'infra de scraping NSI existe déjà |
| RAG : 22 518 chunks NSI ingérés (plateforme pgvector, reranker calibré) | `mcp-corpus` | **Opérationnel** | Le serveur de recherche existe : brancher, pas construire |
| `manifest.csv` + `check_program_coverage.py` + `generate_index.py` | `coverage_report.py` + banque d'objets | Fait | La traçabilité objet↔capacité est déjà outillée |
| `01_charte_graphique_et_pedagogique/` + `02_modeles_documents/` | `docs/06_charte` + gabarits | Partiel | À remplacer par la charte Nexus v2 (cls + icônes + figures) qui est plus aboutie |

## 1.2 Ce que le dépôt NSI n'a PAS (le travail réel du projet manuel)

1. **La couche « manuel »** : le contenu est organisé en séquences d'enseignement (pilotées par le professeur), pas en chapitres d'auto-accompagnement (pilotés par l'élève). Il manque : contrat en « je sais... », diagnostic d'entrée + fiches R, cours en 3 strates, matrice ◆/◆◆/◆◆◆, QCM à distracteurs diagnostiques, circuits de remédiation, tableau de bord.
2. **La chaîne LaTeX/PDF Nexus** : le dépôt est en Markdown (TeX : 0,3 %). Toute la charte v2 (nexus-manuel.cls, icônes TikZ, figures, onglets, ouvertures de chapitre) est à transposer, avec une **bibliothèque de figures NSI** à créer (§5).
3. **La différenciation par parcours** : les séquences ont des `aides_progressives` (excellent point de départ pour les coups de pouce) mais pas de gradation ◆/◆◆/◆◆◆ systématique ni le ratio 40/40/20.
4. **Les formats d'examen NSI** : sujets type bac écrit (3 exercices) et **épreuve pratique** (ECE : exercice de programmation + code à compléter) — spécificité Terminale absente du canon de séquence.

**Conclusion de l'audit** : le meilleur moyen de tirer le meilleur est un pipeline dont le mode dominant n'est pas la génération ex nihilo (comme en maths, faute de corpus) mais la **RESTRUCTURATION CERTIFIÉE** : contenu propriétaire déjà validé → transposition vers le gabarit manuel → enrichissement différencié → gates par exécution.

---

# PARTIE 2 — ARCHITECTURE : UN NOYAU COMMUN, DEUX DÉPÔTS DE PRODUCTION

## 2.1 Décision structurante

Ne pas forker manuel-maths, ne pas polluer le dépôt NSI (qui reste le corpus source et l'outil de classe). Créer **`manuel-nsi/`**, troisième dépôt, construit ainsi :

```
manuel-nsi/
├── CLAUDE.md / CAHIER_DES_CHARGES.md / DIRECTIVES_EN_COURS.md   # adaptés de manuel-maths
├── docs/            # 01 conception (identique), 02 workflow, 06 charte, 07 ligne éditoriale (identiques),
│                    # + 08_specificites_nsi.md (ce document, sections 3-6)
├── gabarits/        # nexus-manuel.cls, nexus-icons.tex, nexus-figures.tex PARTAGÉS (git subtree depuis manuel-maths)
│                    # + nexus-figures-nsi.tex, nexus-code.tex (nouveaux, §5)
├── referentiel/     # généré depuis 00_programmes_officiels/programme_nsi_2019.yaml
├── corpus_nsi/      # lien vers le dépôt NSI (submodule ou clone) = SOURCE T0
├── sources/registry.yaml   # fusion sources_catalog.yml (NSI) + registre maths, tiers T0 ajouté
├── schemas/ scripts/ mcp/ prompts/ chapitres/ .claude/  # structure manuel-maths, scripts adaptés
└── build/
```

**Règle de partage** : la charte graphique (cls, icônes, palette, grille) vit dans manuel-maths et se synchronise vers manuel-nsi (subtree/copie versionnée). Une seule identité visuelle Nexus pour toute la collection ; les ajouts spécifiques NSI vivent dans des fichiers séparés qui ne touchent pas au tronc commun.

## 2.2 Le tier T0 : contenu propriétaire (la grande différence avec les maths)

Nouveau tier dans le registre des sources :

```yaml
- id: SRC-0000
  name: "Corpus NSI Nexus (cyranoaladin/NSI)"
  tier: T0
  license: "propriétaire Nexus Réussite"
  usage_policy: verbatim          # notre contenu : réutilisation totale, adaptation libre
  quality_status: "substance certifiée 114/114, needs_review humain avant publication"
```

Conséquences : le gate anti-similarité ne s'applique PAS aux chunks T0 (c'est notre texte) ; il reste actif contre les tiers T2/T4 (sites de collègues NSI : pixees.fr, Balabonski, infoforall, lyceum, fabricenativel, etc. — à cataloguer en `inspiration_reformulation`). Le statut `needs_review` du dépôt source se propage : un objet du manuel issu d'une séquence non auditée hérite du flag dans `A_VALIDER_HUMAIN.md`.

---

# PARTIE 3 — LE PIPELINE DE TRANSPOSITION SÉQUENCE → CHAPITRE

## 3.1 Le LOT R (nouveau, entre LOT 1 et LOT 2) : récupération structurée

Script `scripts/harvest_nsi.py` : pour un chapitre donné, identifie dans le dépôt NSI les séquences couvrant ses capacités (via `manifest.csv` + matrices de programme), extrait les 11 fichiers types de chaque séquence, les convertit en objets candidats avec métadonnées héritées (capacités, statut de revue, chemin source pour traçabilité). Conversion Markdown → macros Nexus via pandoc + filtre Lua dédié (`scripts/md2nexus.lua`) : titres → sections, blocs code → `\begin{python}`, admonitions → encadrés Nexus.

## 3.2 Table de transposition (le cœur du système)

| Fichier séquence NSI | Objet(s) manuel | Transformation |
|---|---|---|
| `cours_eleve.md` + `trace_ecrite.md` | Cours strate 1 + strate 2 | Fusion : trace écrite = l'essentiel (strate 1), cours élève = développements et exemples (strate 2) ; ajout contre-exemples et ⚠ manquants |
| `fiche_methode.md` | Fiches Mn | Reformater aux 6 rubriques du gabarit (quand/pas-à-pas/exemple/pièges/vérifier/s'entraîner) |
| `td.md` | Exercices ◆◆ majoritairement | Découpage en exercices atomiques, métadonnées, gradation |
| `tp.md` | Exercices ⌨ + **Mini-projet** | Les TP guidés → exercices Python ◆/◆◆ ; les TP ouverts → rubrique Mini-projet (§4.3) |
| `aides_progressives.md` | **Coups de pouce** | Mapping quasi direct — le concept existe déjà, re-normer en 3 niveaux, fichiers {ID}-CDP.tex |
| `corrige.md` | Corrigés copie-modèle | Enrichir au standard (code commenté ligne à ligne, complexité justifiée, conclusion) |
| `evaluation.md` | Base du sujet A | Re-barémer par compétences ; compléter aux formats bac (§4.4) |
| `qcm.json` | QCM diagnostique | **Enrichissement obligatoire** : chaque distracteur reçoit son diagnostic (« si tu as répondu B, tu as confondu mutation et réaffectation → M3 ») |
| `python/` + `tests/` | **Blocs VERIFY** | Les 445 tests existants deviennent les vérifications exécutables des exercices (§4.1) — actif le plus précieux du dépôt |
| `guide_professeur.md` | Déclinaison « livret professeur » | Hors manuel élève ; nouvelle déclinaison F06 assemblée à part |
| `projet_associe.md` | Mini-projet de chapitre | §4.3 |

Ce qui reste à générer ex nihilo par chapitre : le contrat en langage élève (léger : traduit du YAML), le diagnostic d'entrée + fiches R, les contre-exemples, la gradation ◆◆◆ (prise d'initiative), les distracteurs diagnostiques, la remédiation, les figures.

---

# PARTIE 4 — SPÉCIFICITÉS NSI DU GABARIT ET DES GATES

## 4.1 Le gate d'exécution (remplace SymPy — et il est plus fort)

En NSI, la vérité est exécutable. `scripts/verify_python.py` :
- Chaque exercice/corrigé embarque un bloc `% BEGIN-VERIFY ... % END-VERIFY` contenant du **pytest** : le code du corrigé est extrait, exécuté en sandbox (`python -I`, timeout, sans réseau), les assertions valident les sorties.
- **Gate de trace** : pour les exercices « que fait ce programme ? » / « donner la sortie », la sortie affirmée dans le corrigé est vérifiée par exécution réelle — zéro trace de sortie non exécutée dans tout le manuel.
- **Gate de style** : tout code montré à l'élève passe `ruff` (PEP 8) ; conventions imposées : annotations de type dans les corrigés de Terminale, docstrings avec préconditions (c'est au programme : spécification/prototypage), `assert` pour les tests dans le texte élève.
- Réutilisation : les tests du dépôt NSI sont importés comme base ; tout nouvel exercice ajoute les siens.

## 4.2 Cours : adaptations du gabarit 9 temps

Le gabarit maths (docs/01) s'applique intégralement avec ces ajustements :
- **Strate 1** : définitions + propriétés + **spécifications d'interface** (pour les structures de données : les opérations abstraites AVANT toute implémentation — exigence du programme de Terminale).
- **Nouveau bloc `\coderéférence`** : implémentation de référence commentée ligne à ligne, distincte des exemples (encadré fond `nxBleu!3`, numéros de ligne, commentaires en marge).
- **⚠ Erreurs fréquentes NSI** : typologie propre à documenter systématiquement — mutation vs copie de liste, effets de bord, `is` vs `==`, indices off-by-one, portée des variables, récursion sans cas de base, confusion print/return, encodage.
- **Rubrique « À la machine »** : chaque section indique ce que l'élève doit reproduire dans un éditeur (le manuel accompagne un élève qui code, pas qui lit).

## 4.3 Le Temps 7-projet (obligatoire, spécificité programme)

Le B.O. NSI consacre ~25 % de l'horaire au mode projet. Chaque chapitre du manuel comporte donc, après les TD, un **Mini-projet** normé : cahier des charges court, découpage en jalons avec critères de validation exécutables (tests fournis), grille d'auto-évaluation, extensions ◆◆◆. Source : `projet_associe.md` des séquences, re-normé. Les mini-projets se combinent en 2 « projets fil rouge » par manuel (annuel), documentés dans les blocs transversaux.

## 4.4 LOT 6 : les formats d'examen NSI

- **Première** : devoirs type + QCM chronométrés (préparation au format des évaluations communes).
- **Terminale — écrit** : sujets à 3 exercices au format bac (croisant les domaines : structures + BDD + algo, etc.), barème officiel /20.
- **Terminale — Épreuve pratique (ECE)** : par chapitre concerné, ≥ 2 sujets au format officiel : exercice 1 (programmer une fonction depuis sa spécification, avec jeu de tests) + exercice 2 (code à trous à compléter et faire fonctionner). Gate : les deux exercices sont validés par exécution du corrigé contre les tests. La banque officielle des sujets d'EP (publique) entre au registre en T1.
- **Grand Oral** : la question orale 🗣 de chaque chapitre est calibrée comme amorce de Grand Oral NSI.

## 4.5 Vérification réglementaire (R7)

Le dépôt est ancré BO 2019. Avant le LOT 0 : vérifier en ligne si le programme NSI a été modifié depuis (comme découvert pour les maths avec le BO d'avril 2026). Si changement → mettre à jour le YAML source dans le dépôt NSI d'abord (source de vérité unique), puis régénérer le référentiel du manuel. Sinon → consigner la vérification datée dans le rapport LOT 0.

---

# PARTIE 5 — CHARTE : EXTENSIONS NSI DE L'IDENTITÉ NEXUS

La charte Nexus v2 (grille, palette, icônes TikZ, onglets, motifs de chapitre) s'applique telle quelle. Ajouts spécifiques, dans des fichiers dédiés :

1. **`nexus-code.tex`** : environnement code élève (fond blanc, filet gauche nxBleu, numéros de ligne, police mono avec ligatures désactivées), environnement **console** (fond nxGris!8, chevrons `>>>`, distinction visuelle nette code/sortie — l'erreur classique des manuels NSI est de les confondre), bloc `\coderéférence` avec commentaires de marge alignés sur les lignes.
2. **`nexus-figures-nsi.tex`** : bibliothèque TikZ normalisée (mêmes traits/couleurs que les figures maths) pour les invariants du programme : tableaux mémoire et références (boîtes + flèches), listes chaînées, piles/files, **arbres binaires** (style unique : nœuds ronds nxBleu, arêtes 0.8pt), graphes orientés/non orientés, tables SQL (en-tête nxBleu!10), architecture von Neumann, trames réseau et encapsulation, chronogrammes de processus, tables de vérité. Règle éditoriale : ≥ 8 figures par chapitre de structures de données/architecture, chaque exécution d'algorithme sur un exemple est accompagnée de son schéma d'état.
3. **Motifs de chapitre** (signature d'ouverture) : binaire = trame de 0/1 en dégradé, arbres = arbre stylisé, réseaux = maillage de nœuds, BDD = tables imbriquées, POO = classes emboîtées — même langage graphique nxBleu!12 que les maths.

---

# PARTIE 6 — PÉRIMÈTRE : LES CHAPITRES DES DEUX MANUELS

Alignés sur les domaines du programme et les progressions du dépôt (`03_progressions/`) ; à confirmer contre celles-ci au LOT 0 de chaque manuel.

**Manuel Première NSI (10 chapitres)** : 1. Types de base et représentation binaire (entiers, flottants, booléens, caractères) — 2. Types construits (p-uplets, tableaux, dictionnaires) — 3. Traitement de données en tables — 4. Web et IHM (HTML/CSS, formulaires, HTTP) — 5. Architecture de von Neumann et systèmes d'exploitation — 6. Réseaux : transmission de données — 7. Langage Python : spécification, tests, mise au point — 8. Algorithmique 1 : parcours, tris par insertion et sélection — 9. Algorithmique 2 : dichotomie, algorithmes gloutons, k plus proches voisins — 10. Projet et méthodes (chapitre transversal : gestion de projet, débogage, documentation).

**Manuel Terminale NSI (12 chapitres)** : 1. Structures de données : interfaces, listes, piles, files — 2. Dictionnaires, tables de hachage — 3. Arbres et arbres binaires de recherche — 4. Graphes et leurs algorithmes — 5. Bases de données relationnelles et SQL — 6. Architectures : processus, ordonnancement, SoC — 7. Réseaux : protocoles de routage, sécurisation des communications — 8. Récursivité — 9. Modularité et programmation objet — 10. Diviser pour régner, tri fusion — 11. Programmation dynamique et recherche textuelle — 12. Calculabilité, décidabilité, paradigmes. + Bloc transversal « Préparation Épreuve pratique » (banque ECE) et « Préparation écrit » (sujets 3 exercices).

---

# PARTIE 7 — PLAN D'EXÉCUTION

**Phase 0 — Bootstrap (1 session agent)** : créer manuel-nsi depuis le squelette manuel-maths (copie + adaptation CLAUDE.md/CDC : gate SymPy → gate pytest, exigences ECE, Temps 7-projet, tier T0) ; subtree de la charte ; submodule du dépôt NSI ; conversion `programme_nsi_2019.yaml` → référentiels Première/Terminale ; fusion des registres de sources ; écriture de `harvest_nsi.py` + `md2nexus.lua` + `verify_python.py` (adaptation directe de verify_sympy) ; `DIRECTIVES_EN_COURS.md` en place dès le premier commit (leçon apprise du run maths).

**Phase 1 — Chapitre pilote** : Première, chapitre 2 « Types construits » (le mieux couvert par le corpus certifié, riche en erreurs types, représentatif : code + figures mémoire + QCM). Boucle LOT 0 → R → 2 → 7 complète. **Validation humaine visuelle et pédagogique du pilote par toi** avant industrialisation — les décisions spécifiques (rendu des figures mémoire, équilibre restructuration/réécriture, densité du bloc code référence) se jugent sur pièce.

**Phase 2 — Industrialisation** : Première complète (le corpus T0 y est le plus dense), puis Terminale (davantage de génération pour ◆◆◆ et ECE), puis LOTs FINAUX (blocs transversaux, manuels assemblés, déclinaisons dont livret professeur, harmonisation inter-manuels avec les maths : mêmes ouvertures, même tableau de bord, même voix éditoriale).

**Critères d'acceptation ajoutés au CDC NSI** : 100 % des sorties de programmes affichées vérifiées par exécution ; 100 % du code élève ruff-clean ; ≥ 2 sujets ECE par chapitre Terminale concerné ; mini-projet jalonné et testé par chapitre ; zéro objet publié dont la séquence source était `needs_review` sans revue humaine tracée (héritage du protocole NSI, plus strict que le manuel maths — c'est lui qui fait référence désormais pour les deux projets).

L'ordre de grandeur d'effort, comparé aux maths : le LOT 3-4 d'un chapitre Première NSI devrait coûter 40 à 50 % de son équivalent maths grâce à la restructuration T0 ; la Terminale, 60 à 70 % (ECE et ◆◆◆ à créer). Le vrai chantier neuf est graphique (nexus-figures-nsi) et il est amorti sur les deux manuels.
