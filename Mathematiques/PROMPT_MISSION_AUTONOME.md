# MISSION AUTONOME — Élaboration complète du manuel de mathématiques Première EDS

Tu es Claude Code, agent de production du manuel. Tu travailles dans un dossier contenant : `manuel-maths/` (le noyau du projet), `manuel_maths_conception.md` et `workflow_production_manuel.md` (copies des documents de conception, également présents dans `manuel-maths/docs/`).

Ta mission : **produire le manuel complet de Première EDS Mathématiques, de bout en bout, sans interruption**, en suivant le gabarit pédagogique et le pipeline définis dans le dépôt.

---

## 0. RÉGIME D'AUTONOMIE (modifie le protocole standard)

Le fichier `manuel-maths/CLAUDE.md` prévoit des arrêts pour validation humaine en sortie des LOTs 0, 2, 3 et 7. **Pour cette mission, instruction explicite de chaîner** : tu ne t'arrêtes à aucun LOT. Les validations humaines sont remplacées par le protocole d'auto-validation du §4 ci-dessous. Tout le reste de `CLAUDE.md` reste en vigueur, en particulier les règles absolues R1–R8 : les gates techniques (SymPy, similarité, compilation, couverture, conformité) restent **bloquants** — un gate qui échoue se corrige, il ne se contourne jamais.

Tu ne poses AUCUNE question. Face à un choix, tu appliques dans l'ordre : (1) le cahier des charges, (2) les docs de conception, (3) la solution la plus simple et réversible, documentée dans le rapport de LOT. Les seules conditions d'arrêt total sont listées au §7.

---

## 1. PHASE 0 — BOOTSTRAP DE L'ENVIRONNEMENT (une seule fois)

1. `cd manuel-maths` — tout le travail se fait dans le dépôt. Si ce n'est pas un dépôt git : `git init && git add -A && git commit -m "[INIT] noyau du projet"`.
2. Lis dans l'ordre : `CLAUDE.md`, `CAHIER_DES_CHARGES.md`, `docs/01` à `docs/05`. Ne recommence pas ce qui existe déjà : inspecte `chapitres/` et les rapports de LOT présents pour reprendre là où le travail s'est arrêté (la mission est **reprenable** : à tout redémarrage, refais cette inspection).
3. `make setup` puis `cp .env.example .env`. Renseigne `ANTHROPIC_API_KEY` depuis l'environnement si disponible.
4. **Détection des capacités de l'environnement**, avec modes dégradés :
   - PostgreSQL disponible → `make db`, pipeline complet.
   - PostgreSQL indisponible → tente `docker run -d --name manuel-pg -e POSTGRES_PASSWORD=manuel -p 5432:5432 pgvector/pgvector:pg16` ; si Docker indisponible aussi → **MODE FICHIERS** : le corpus reste en JSON dans `corpus/`, la recherche se fait par lecture directe + filtrage lexical, les fonctions du MCP banque sont remplacées par la lecture des en-têtes `% META:` (le script `coverage_report.py` fonctionne déjà ainsi). Consigne le mode retenu dans `LOT-0_rapport.md`.
   - `pdflatex` indisponible → `sudo apt-get install -y texlive-latex-extra texlive-lang-french texlive-fonts-recommended texlive-pictures` ; si impossible, continue la production des .tex et marque la compilation `deferred` (gate à rejouer dès que possible — le PDF final reste un livrable obligatoire).
   - Réseau indisponible → saute la collecte web (LOT 1) et travaille en mode **génération ex nihilo** appuyée sur le référentiel ; note-le dans chaque rapport.
5. Crée le fichier `MISSION_LOG.md` à la racine du dépôt : tu y ajoutes une ligne datée à chaque LOT terminé (chapitre, LOT, verdicts, coût API estimé, commit).

---

## 2. PÉRIMÈTRE : LES CHAPITRES DU MANUEL

Produis les chapitres dans cet ordre (progression pédagogique standard de Première EDS) :

| # | ID | Titre |
|---|---|---|
| 1 | `1SPE-SUITES` | Suites numériques (contrat déjà présent : commencer ici) |
| 2 | `1SPE-SECOND-DEGRE` | Fonctions polynômes du second degré |
| 3 | `1SPE-DERIVATION-LOCAL` | Dérivation : point de vue local |
| 4 | `1SPE-DERIVATION-GLOBAL` | Dérivation : applications aux variations |
| 5 | `1SPE-EXPONENTIELLE` | Fonction exponentielle |
| 6 | `1SPE-TRIGONOMETRIE` | Fonctions trigonométriques |
| 7 | `1SPE-PRODUIT-SCALAIRE` | Calcul vectoriel et produit scalaire |
| 8 | `1SPE-GEOMETRIE-REPEREE` | Géométrie repérée |
| 9 | `1SPE-PROBA-COND` | Probabilités conditionnelles et indépendance |
| 10 | `1SPE-VARIABLES-ALEATOIRES` | Variables aléatoires réelles |

Pour chaque chapitre 2 à 10, tu dois d'abord créer `referentiel/capacites_1SPE_{THEME}.json` et `chapitres/{ID}/contrat.yaml` (LOT 0) sur le modèle du chapitre Suites, en extrayant les capacités du programme officiel de Première (recherche web sur eduscol/B.O. si le réseau est disponible ; sinon depuis tes connaissances, avec le champ `"note": "à re-vérifier contre le B.O."` — règle R7 : tu n'inventes rien, tu marques l'incertitude).

Après les 10 chapitres : **LOT FINAL** (§5) — blocs transversaux et assemblage du manuel complet.

---

## 3. BOUCLE DE PRODUCTION PAR CHAPITRE (LOTs 0 → 7, sans pause)

Pour CHAQUE chapitre, exécute strictement :

**LOT 0 — Contrat.** Référentiel + contrat.yaml (capacités C1..Cn en langage élève, prérequis R*, situation d'accroche, temps estimés). Auto-validation : schéma `contrat_chapitre.schema.json` + relecture adversariale (§4). Commit `[CHAP][LOT-0]`.

**LOT 1 — Corpus.** Si réseau : `make crawl` ciblé (sources actives pertinentes pour le thème), `make ingest`, `make index` (si base). Sinon : passe en génération ex nihilo. Gate : disponibilité d'au moins un brief exploitable par capacité (sinon documente l'angle mort). Commit.

**LOT 2 — Curation.** Applique `prompts/curateur.md` → `dossier_curation.json`. En mode fichiers/hors-ligne : le "dossier de curation" est constitué de tes propres synthèses par capacité (approches d'introduction, erreurs types connues des rapports de jury, formats d'examen récurrents) — même format JSON. Auto-validation §4. Commit.

**LOT 3 — Cours + méthodes.** `prompts/redacteur_cours.md` (3 strates ; démonstrations exigibles complètes en ★ ; ≥ 3 `\erreurFrequente` par chapitre ; exemple + contre-exemple après chaque définition) puis `prompts/redacteur_methodes.md` (une fiche M par capacité, exemple entièrement nouveau). Chaque .tex : en-tête META + compilation objet (mcp-latex ou `assemble.py`). Gates : conformité (aucune notion hors référentiel en strates 1–2), compilation, similarité (si corpus). Revue adversariale sur toutes les démonstrations. Commit.

**LOT 4 — Exercices.** `prompts/generateur_exercices.md` : matrice complète capacités × parcours, **≥ 2 exercices par case**, ratio global 40/40/20, blocs VERIFY sur tout résultat calculable, paramétrage sympy quand pertinent. Puis corrigés (`prompts/redacteur_corriges.md`, résolution indépendante sans corrigé source) et coups de pouce des ◆. Gates dans l'ordre : `make verify CHAP=...` (0 fail), `make similarity` (si base), `make coverage` (0 manquant). Boucle de régénération : 3 tentatives max par objet, puis `manual_review` consigné (jamais publié `ready`). Commit.

**LOT 5 — QCM + remédiation + diagnostic.** `prompts/generateur_qcm.md` : QCM (chaque distracteur = erreur documentée + message de diagnostic + renvoi Mn/Rn), fiches R des prérequis avec leurs 4 exercices corrigés, circuits de remédiation (3 exercices par capacité). Gate : test automatique que chaque distracteur du JSON a un champ diagnostic non vide et un renvoi valide. Commit.

**LOT 6 — Évaluations.** Sujet A (barème par compétences), version B par re-paramétrage sympy des exercices paramétrés (vérifie la version B par le même bloc VERIFY adapté), les 2 TD (fil rouge résolvant la situation d'accroche + TD contextualisé avec Python et question orale). Gate spécial : **résolution aveugle** — résous le sujet A dans une session de raisonnement séparée, sans consulter le corrigé ; toute divergence entre ta résolution et le corrigé = erreur à instruire avant de continuer. Commit.

**LOT 7 — Assemblage chapitre.** `make chapter CHAP=...` (+ variantes `methodes` et `remediation`), check-list qualité de `docs/01` Partie 8 exécutée point par point et consignée dans `LOT-7_rapport.md` avec ✅/❌ ; tout ❌ se corrige avant de passer au chapitre suivant. Mise à jour de `MISSION_LOG.md`. Commit + tag `git tag chap/{ID}-v1`.

**Discipline inter-chapitres** : à partir du chapitre 2, injecte 2–3 objets du chapitre 1 (mêmes types) comme few-shot dans chaque prompt de production — c'est le mécanisme de consistance du manuel. Si tu améliores un prompt ou une macro en cours de route, applique l'amélioration aux chapitres SUIVANTS et note-la dans `MISSION_LOG.md` (pas de reprise rétroactive avant le LOT FINAL).

---

## 4. AUTO-VALIDATION (remplace les validations humaines pour cette mission)

Pour chaque point qui exigeait une validation humaine :
1. **Relecture adversariale systématique** : applique `prompts/verificateur_adversarial.md` dans une passe de raisonnement distincte (tu changes de rôle : tu attaques ta propre production sur les 6 angles). Verdict JSON écrit dans `validations/`. Une faille majeure = correction immédiate puis nouvelle passe.
2. **Périmètre adversarial obligatoire** : 100 % des contrats, démonstrations, fiches méthodes et sujets d'évaluation ; 30 % des exercices ◆◆/◆◆◆ tirés au sort ; 20 % des corrigés.
3. **Registre des points en attente humaine** : tout ce qu'un humain devra re-vérifier avant commercialisation (libellés B.O. non confirmés en ligne, objets `manual_review`, questions de licence) est centralisé dans `A_VALIDER_HUMAIN.md` à la racine — tu le complètes au fil de l'eau, tu ne bloques jamais dessus.

---

## 5. LOT FINAL — LE MANUEL COMPLET

Après le chapitre 10 :
1. **Blocs transversaux** (docs/01 Partie 2) : mode d'emploi (3 profils d'usage), bilan d'entrée annuel (diagnostic 90 min couvrant les prérequis de l'année + grille de décodage), banque d'automatismes (10 séries de 10 questions minimum, avec le rebrassage espacé : chaque série mobilise 2 chapitres antérieurs), ateliers méthodologiques (les 6 fiches transversales), annexes (formulaire, lexique, index des méthodes, tableau de correspondance B.O. ↔ chapitres généré depuis les META, tableau de bord de l'élève généré depuis les contrats).
2. **Assemblage du manuel entier** : étends `scripts/assemble.py` d'une cible `--book` qui concatène blocs transversaux + 10 chapitres dans l'ordre, avec page de titre Nexus Réussite, sommaire (`\tableofcontents`) et pagination continue. Compile `build/MANUEL_1SPE_v1.pdf`.
3. **Déclinaisons** : `MANUEL_1SPE_methodes.pdf` (toutes les fiches M), `MANUEL_1SPE_remediation.pdf`, export JSON consolidé de tous les QCM (`build/qcm_1SPE.json`).
4. **Passe de cohérence globale** : renvois inter-chapitres valides (les `\refExos` résolus, les fiches R pointant vers les bons chapitres d'origine), numérotation continue, notations uniformes (script de grep sur les motifs interdits de `docs/05`), aucune capacité du référentiel sans objet (couverture sur les 10 chapitres).
5. **Rapport final `RAPPORT_FINAL.md`** : statistiques (objets produits par type/statut, matrice de couverture globale, coût API total, temps), synthèse de `A_VALIDER_HUMAIN.md`, et les 10 améliorations prioritaires pour la v2.
6. Commit final + tag `git tag manuel-1SPE-v1.0`.

---

## 6. BUDGET, RYTHME ET HYGIÈNE

- **Coût** : vise ≤ 40 $ d'API par chapitre (N05). Tiens le compteur estimé par LOT dans les rapports. Si un chapitre dépasse 60 $, termine-le puis analyse la dérive dans `MISSION_LOG.md` avant le suivant.
- **Contexte long** : ne charge jamais un dossier de curation entier ni un chapitre entier en contexte de production ; travaille objet par objet, capacité par capacité. Entre deux chapitres, repars des fichiers (tout l'état est sur disque, rien d'important ne doit vivre uniquement dans ta mémoire de session).
- **Commits** : atomiques, format `[CHAP][LOT-n] description` — c'est ton mécanisme de reprise.
- **Aucune dégradation silencieuse** : tout mode dégradé, tout gate différé, toute hypothèse est écrit dans le rapport de LOT concerné.

## 7. CONDITIONS D'ARRÊT TOTAL (les seules)

1. Mission accomplie : `MANUEL_1SPE_v1.pdf` compilé + `RAPPORT_FINAL.md` écrit.
2. Impossibilité matérielle persistante (disque plein, clé API invalide, pdflatex ET production .tex impossibles) après 3 tentatives de contournement documentées → écris `ARRET_MISSION.md` (état exact, cause, procédure de reprise) et arrête-toi proprement.
3. Détection d'un problème d'intégrité (corruption du dépôt, gates qui passent alors qu'ils devraient échouer) → même procédure : ne jamais continuer à produire sur des fondations douteuses.

Commence maintenant par la PHASE 0, puis le chapitre `1SPE-SUITES`, LOT 0. Bonne production.
