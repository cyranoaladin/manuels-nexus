# Workflow agentique de production du manuel
## Sourcing web → base de connaissances → composition assistée → validation → publication

Ce document définit le système complet : cartographie des sources, pipeline de collecte, architecture RAG, agents spécialisés, serveurs MCP, orchestration, contrôle qualité et cadre juridique. Il est conçu pour s'appuyer sur l'infrastructure existante (Claude Code/Cowork, dépôts GitHub, PostgreSQL + pgvector, chaîne LaTeX) et sur une méthode de travail par LOTs.

---

# PARTIE 1 — CARTOGRAPHIE DES SOURCES

## 1.1 Typologie et priorisation

| Tier | Type de source | Exemples | Usage |
|---|---|---|---|
| **T1 — Officiel** | Programmes B.O., documents d'accompagnement, sujets d'examen | eduscol.education.fr, education.gouv.fr/bo, cyclades/annales officielles, rapports de jurys | Source de vérité : capacités, attendus, formats, barèmes. Réutilisation large (documents administratifs) |
| **T2 — Institutionnel académique** | Ressources produites par les académies, IREM, groupes de réflexion | pedagogie.ac-*.fr (Versailles, Nantes, Lyon, Bordeaux...), publimath, portail des IREM, revue Repères IREM | Activités de découverte, TD contextualisés, différenciation, erreurs types documentées |
| **T3 — Associatif** | APMEP, Sésamath | apmep.fr (annales bac/brevet corrigées), manuels Sésamath (licence libre CC) | Banque d'annales, exercices réutilisables (vérifier la licence : Sésamath = CC-BY-SA, réutilisation possible avec attribution) |
| **T4 — Pages personnelles d'enseignants** | Sites de cours/exercices | maths-et-tiques (Y. Monka), xmaths, jgcuaz, mathematiques-web, chingatome, mathsguyon, pyromaths... | Idées d'exercices, progressions, formulations pédagogiques. **Inspiration et reformulation uniquement** (droits d'auteur) |
| **T5 — International/complémentaire** | Ressources francophones et anglophones | RTS/Khan Academy FR, NRICH, brilliant (idées de problèmes ouverts), arXiv (histoire des maths) | Problèmes ouverts, enrichissement culturel, approches alternatives |

## 1.2 Registre des sources (source-registry)

Fichier `sources/registry.yaml` versionné, une entrée par source :

```yaml
- id: SRC-0042
  name: "Maths et tiques"
  url: "https://www.maths-et-tiques.fr"
  tier: T4
  license: "tous droits réservés"
  usage_policy: "inspiration_reformulation"   # verbatim | adaptation_attribution | inspiration_reformulation
  crawl: { method: sitemap, frequency: monthly, scope: "/cours/lycee/*" }
  quality_score: 4        # 1-5, révisé après usage
  notes: "Vidéos liées ; fiches méthodes bien structurées ; niveau standard"
```

Ce registre pilote les crawlers et impose automatiquement la politique de réutilisation en aval (l'agent rédacteur reçoit `usage_policy` avec chaque chunk récupéré).

## 1.3 Cadre juridique (règle non négociable du pipeline)

- **T1** : réutilisable (information publique), citer la source.
- **T3 licence libre** (Sésamath CC-BY-SA) : réutilisation/adaptation avec attribution et partage à l'identique — attention à la contamination de licence si intégré tel quel dans un manuel commercial → préférer l'adaptation substantielle.
- **T2/T4** : jamais de copie verbatim. Les contenus servent de matière première pédagogique (idées d'exercices, structures d'activités, formulations d'erreurs types) systématiquement **reformulés, renumérotés, recontextualisés**. Un agent anti-similarité (voir 5.7) vérifie la distance entre le contenu produit et les chunks sources utilisés.
- Traçabilité : chaque objet du manuel porte dans ses métadonnées la liste des `SRC-*` ayant inspiré sa création (audit interne, jamais publié).

---

# PARTIE 2 — ARCHITECTURE GÉNÉRALE DU PIPELINE

```
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE A — COLLECTE (hebdo/mensuel, automatisée)                │
│  Agent Scout ──> Crawlers ──> /raw (PDF, HTML, LaTeX, ODT)      │
└──────────────┬──────────────────────────────────────────────────┘
               ▼
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE B — INGESTION & NORMALISATION                            │
│  Agent Ingesteur : extraction texte+math (OCR si besoin),       │
│  conversion LaTeX/Markdown, découpage sémantique, métadonnées   │
│  ──> /corpus (chunks JSON normalisés)                           │
└──────────────┬──────────────────────────────────────────────────┘
               ▼
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE C — INDEXATION                                           │
│  PostgreSQL + pgvector (embeddings 1024d) + index BM25          │
│  + reranker CrossEncoder ──> base "corpus_manuel"               │
└──────────────┬──────────────────────────────────────────────────┘
               ▼
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE D — CURATION PAR CHAPITRE                                │
│  Agent Curateur : pour chaque capacité Cn, requêtes RAG,        │
│  sélection/notation des ressources ──> dossier_chapitre.json    │
└──────────────┬──────────────────────────────────────────────────┘
               ▼
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE E — COMPOSITION (agents rédacteurs spécialisés)          │
│  Cours │ Méthodes │ Exercices │ Corrigés │ QCM │ Évaluations    │
│  ──> objets LaTeX modulaires + métadonnées                      │
└──────────────┬──────────────────────────────────────────────────┘
               ▼
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE F — VALIDATION (gates automatiques + revue humaine)      │
│  Conformité B.O. │ Exactitude (SymPy) │ Compilation │ Similarité│
│  │ Couverture │ Lisibilité ──> statut certifié par objet        │
└──────────────┬──────────────────────────────────────────────────┘
               ▼
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE G — ASSEMBLAGE & PUBLICATION                             │
│  Génération chapitre/déclinaisons, CI GitHub Actions,           │
│  PDF bannière Nexus Réussite, export QCM plateforme             │
└─────────────────────────────────────────────────────────────────┘
```

Principe directeur : **chaque étape produit des artefacts versionnés dans Git** ; aucun agent n'écrit directement dans le manuel final ; tout passe par les gates de l'étape F.

---

# PARTIE 3 — ÉTAPES A-B-C : COLLECTE, INGESTION, INDEXATION

## 3.1 Agent Scout (veille et découverte)

- **Rôle** : découvrir de nouvelles sources et de nouveaux contenus sur les sources connues.
- **Outils MCP** : `web_search`, `fetch`, accès au `source-registry`.
- **Cadence** : run mensuel + run ponctuel au lancement d'un chapitre ("trouve les 15 meilleures ressources sur les suites arithmético-géométriques, niveau Première, priorité T1/T2").
- **Sorties** : propositions d'ajout au registre (revue humaine avant activation) + liste d'URLs à crawler.
- **Requêtes types** : `site:eduscol.education.fr ressources accompagnement première spécialité mathématiques`, `suites numériques activité découverte académie`, `rapport jury bac mathématiques erreurs fréquentes`.

## 3.2 Crawlers (scripts, pas agents)

- **Stack** : Python (`httpx` + `trafilatura` pour HTML, `sitemap` parsing), respect `robots.txt`, throttling 1 req/2s par domaine, User-Agent identifié.
- Stockage brut : `/raw/{SRC-id}/{date}/...` avec manifeste (URL, date, hash, headers).
- Détection de changement par hash → seuls les contenus nouveaux/modifiés repartent en ingestion.
- Cas particuliers : PDF Eduscol/annales (téléchargement direct), pages dynamiques (Playwright en fallback).

## 3.3 Agent Ingesteur (normalisation)

Le point dur : **extraire les mathématiques proprement**.

1. **Extraction** :
   - PDF texte : `pymupdf` ; PDF scanné : OCR (`tesseract` + fallback vision LLM pour les formules).
   - Formules : conversion vers LaTeX via un modèle vision (Claude sur images de zones détectées comme mathématiques) quand l'extraction texte les casse — c'est le poste où le LLM apporte le plus.
   - HTML : `trafilatura` + règles par source (les sites T4 ont des gabarits stables → extracteurs dédiés amortis).
2. **Normalisation** : tout converge vers Markdown+LaTeX (`$...$`), en-têtes hiérarchiques reconstruits.
3. **Découpage sémantique** : par unité pédagogique (un exercice = un chunk ; une définition+exemple = un chunk ; une activité = un chunk éventuellement long), jamais par fenêtre fixe de tokens. Un classifieur LLM léger (Haiku) étiquette chaque chunk : `{type: cours|methode|exercice|corrige|activite|evaluation|erreur_type, niveau, theme, capacites_probables[], difficulte_estimee}`.
4. **Sortie** : `corpus/{SRC-id}/{doc-id}/chunk-*.json` avec le texte normalisé + métadonnées + `usage_policy` héritée du registre.

## 3.4 Indexation (réutilisation directe de l'infra RAG existante)

- **Base** : PostgreSQL + pgvector, embeddings 1024d (même stack que la plateforme RAG NSI — schéma dupliqué dans une base `corpus_manuel_maths`).
- **Recherche hybride** : vecteur + BM25 (tsvector) fusionnés (RRF), puis **reranking CrossEncoder** avec marge calibrée — la chaîne déjà validée sur le corpus NSI (22 500 chunks) se transpose telle quelle.
- **Filtres structurés** : tier, type de chunk, niveau, thème, usage_policy → un rédacteur peut demander "exercices, suites, Première, T1-T3 uniquement".
- Table complémentaire `capacites` : le référentiel officiel du programme (extrait des B.O. à l'étape A, une ligne par capacité, identifiant stable `1SPE-SUITES-C3`) — pivot de tout le système.

---

# PARTIE 4 — ÉTAPE D : CURATION

## Agent Curateur (un run par chapitre)

- **Entrée** : le contrat du chapitre (liste des capacités `Cn` issues du référentiel).
- **Processus** : pour chaque capacité, 3–5 requêtes RAG formulées différemment (définitionnelle, méthodologique, "exercice type", "erreur fréquente", "activité d'introduction") ; agrégation, déduplication, notation de chaque ressource sur 4 critères (pertinence capacité / qualité mathématique / originalité pédagogique / exploitabilité selon usage_policy).
- **Sortie** : `chapitres/{chap-id}/dossier_curation.json` — pour chaque capacité : top 10 chunks avec notes et un **brief de synthèse** rédigé par l'agent ("les 3 approches d'introduction observées ; les 4 erreurs types documentées dans les rapports de jury ; les formats d'exercices récurrents au bac depuis 2021 ; angles morts du corpus → à créer ex nihilo").
- **Revue humaine** (30 min/chapitre) : validation du dossier avant composition. C'est le point de contrôle éditorial le plus rentable — corriger la matière première coûte 10× moins cher que corriger la rédaction.

---

# PARTIE 5 — ÉTAPE E : AGENTS DE COMPOSITION

Chaque agent est un rôle avec un prompt système dédié, le gabarit du manuel (le document de conception) en contexte, et le dossier de curation de la capacité concernée. Modèles : Sonnet pour la production de masse, Opus/Fable pour les objets à forte exigence (démonstrations, sujets d'évaluation, strate ★).

## 5.1 Rédacteur-Cours
- **Entrée** : capacités + brief de curation + extraits T1 (formulations officielles).
- **Contrainte** : strate 1 strictement conforme au B.O. (définitions et théorèmes à formulation contrôlée) ; strates 2 et 3 nourries par le corpus (reformulations, illustrations, erreurs types issues des rapports de jury).
- **Sortie** : `cours/{chap}/{section}.tex` (macros du kit LaTeX : `\definition`, `\theoreme`, `\margeAppui`, `\erreurFrequente`, `\approfondissement`).

## 5.2 Rédacteur-Méthodes
- Une fiche par capacité au format normalisé (Quand / Pas à pas / Exemple rédigé / Pièges / Vérifier / S'entraîner). L'agent croise 3–4 formulations sources de la même méthode et produit une synthèse originale, avec exemple numérique **nouveau** (jamais repris d'une source).

## 5.3 Générateur-Exercices
- **Mode 1 — Adaptation** (sources T1/T3-libres) : re-barèmage, renumérotation, actualisation des contextes, alignement sur les capacités.
- **Mode 2 — Génération inspirée** (sources T2/T4) : l'agent reçoit la *structure* d'un exercice source (type de tâche, difficulté, enchaînement des questions) et génère un exercice isomorphe avec données, contexte et valeurs entièrement nouveaux.
- **Mode 3 — Création ex nihilo** : pour les angles morts identifiés par le Curateur.
- Chaque exercice sort avec ses métadonnées complètes `{capacites[], methodes[], parcours, competences[], duree, mode_creation, sources_inspiration[]}` et **ses valeurs numériques paramétrées** quand c'est possible (variables sympy) → génération automatique des versions B d'évaluation.

## 5.4 Rédacteur-Corrigés
- Standard "copie modèle" : rédaction complète telle qu'exigée de l'élève, avec commentaires de marge. Travaille **indépendamment** de l'énoncé généré (il résout l'exercice sans voir de corrigé source) — c'est déjà un premier test de résolubilité.

## 5.5 Générateur-QCM et Coups de pouce
- QCM : distracteurs construits à partir des erreurs types documentées (chaque mauvaise réponse = une erreur réelle, avec son diagnostic "si tu as répondu B...").
- Coups de pouce : les 3 niveaux d'aide pour chaque exercice ◆, générés à partir du corrigé.

## 5.6 Vérificateur mathématique (le gate le plus important)
- **Outil** : sandbox Python avec SymPy/NumPy en MCP tool.
- Pour chaque exercice/corrigé : extraction des affirmations calculables (résultats numériques, identités, solutions d'équations, limites, sommes) → vérification symbolique/numérique scriptée. Statut : `verified | partially_verified | manual_review`.
- Pour les démonstrations et raisonnements non calculables : revue croisée par un second modèle avec prompt adversarial ("trouve la faille"), puis revue humaine obligatoire.
- Cible : **0 objet publié sans statut `verified` ou revue humaine tracée** (même discipline que la certification 114/114 du corpus NSI).

## 5.7 Agent Anti-similarité
- Compare chaque objet produit aux chunks sources de son dossier (embedding cosine + n-grammes). Seuils : similarité n-gram > 0.35 avec une source T2/T4 → rejet et régénération ; T1/T3-libre → vérification attribution.

## 5.8 Agent Conformité-programme
- Vérifie que chaque objet référence des capacités existantes du référentiel, que les notations et le vocabulaire sont ceux du B.O. du niveau (pas de notion hors programme dans les strates 1–2, hors-programme autorisé uniquement en ★ avec marquage).

---

# PARTIE 6 — SERVEURS MCP ET OUTILLAGE

## 6.1 MCP servers à déployer

| Serveur | Fonction | Implémentation |
|---|---|---|
| `mcp-corpus` | Recherche hybride dans la base pgvector (query, filtres tier/type/niveau, top-k, rerank) + lecture du référentiel capacités | FastMCP Python sur l'infra RAG existante — c'est l'adaptation du serveur NSI |
| `mcp-banque` | CRUD sur la banque d'objets du manuel : créer/lire/mettre à jour exercices, méthodes, corrigés avec métadonnées ; requêtes de couverture ("capacités sans exercice ◆◆◆") | FastMCP + PostgreSQL (tables `objets`, `metadonnees`, `validations`) |
| `mcp-sympy` | Vérification mathématique : exécute des scripts de contrôle en sandbox, retourne verdict structuré | FastMCP + subprocess isolé |
| `mcp-latex` | Compilation pdflatex d'un objet ou d'un chapitre, retour des erreurs parsées, génération d'aperçu PNG | FastMCP + conteneur texlive |
| `filesystem` / `git` | Accès aux dépôts (objets .tex, registres, dossiers de curation) | Serveurs MCP standards |
| `fetch` / `web_search` | Pour l'agent Scout uniquement | Standards |

## 6.2 Orchestration

- **Poste de pilotage** : Claude Code (ou Cowork pour les phases de curation/revue) avec les MCP ci-dessus configurés dans le projet. Chaque rôle d'agent = un fichier de commande/skill (`/rediger-methode C3`, `/generer-exercices C3 --parcours 2 --n 6`, `/verifier chap-suites`).
- **Automatisation lourde** (crawl, ingestion, indexation, batchs de vérification) : scripts Python + cron ou n8n sur le Hetzner ; pas besoin d'agent LLM pour ce qui est déterministe.
- **CI GitHub Actions** sur le dépôt du manuel :
  - à chaque PR : compilation LaTeX complète, exécution des scripts SymPy attachés aux objets modifiés, contrôle du schéma des métadonnées, rapport de couverture des capacités ;
  - merge bloqué si un gate échoue.
- **Batch API Anthropic** pour les productions de masse (génération des coups de pouce, des QCM, des versions B) : −50 % de coût, adapté aux lots non interactifs.

## 6.3 Structure du dépôt

```
manuel-maths/
├── sources/registry.yaml
├── referentiel/capacites_{niveau}.json      # extrait des B.O., versionné
├── corpus/                                   # chunks normalisés (ou lien vers la base)
├── chapitres/{chap-id}/
│   ├── contrat.yaml                          # capacités, parcours, temps estimés
│   ├── dossier_curation.json
│   ├── cours/*.tex        ├── methodes/*.tex
│   ├── exercices/*.tex    ├── corriges/*.tex
│   ├── qcm/*.json         ├── evaluations/*.tex
│   └── validations/*.json                    # verdicts sympy, similarité, conformité
├── gabarits/                                  # classes et macros LaTeX Nexus Réussite
├── scripts/  (crawl, ingest, index, verify, assemble)
└── .github/workflows/ci.yml
```

---

# PARTIE 7 — WORKFLOW OPÉRATIONNEL PAR LOTS

Cycle de production d'un chapitre (calibrage : ~2 semaines en travail parallèle, dont ~4 h de revue humaine) :

| LOT | Contenu | Acteur | Gate de sortie |
|---|---|---|---|
| **LOT 0** | Extraction du référentiel capacités du chapitre depuis les B.O., rédaction du contrat | Humain + agent | Contrat validé |
| **LOT 1** | Scout ciblé + crawl + ingestion + indexation des ressources du thème | Scripts + Scout | Corpus thème ≥ seuil de couverture par capacité |
| **LOT 2** | Curation | Curateur + revue humaine (30 min) | Dossier de curation approuvé |
| **LOT 3** | Cours (strates 1-2-3) + fiches méthodes | Rédacteurs | Conformité B.O. + compilation + revue humaine |
| **LOT 4** | Exercices 3 parcours + corrigés + coups de pouce | Générateur + Corrigés | 100 % SymPy verified ou revue tracée ; anti-similarité passé ; couverture capacités × parcours complète |
| **LOT 5** | QCM diagnostic + auto-évaluation + remédiation | Générateur-QCM | Chaque distracteur relié à une erreur documentée |
| **LOT 6** | Évaluation A + version B (re-paramétrage sympy) + barème compétences | Rédacteur (Opus/Fable) + humain | Barème vérifié, sujet testé en résolution aveugle par un agent |
| **LOT 7** | Assemblage, relecture finale humaine (3 passes), publication PDF + exports | CI + humain | Check-list qualité (Partie 8 du doc de conception) 100 % |

Chaque LOT laisse un fichier de synthèse (`LOT-n_rapport.md`) dans le dépôt : décisions, verdicts, coûts API, points reportés — traçabilité identique au workflow de certification NSI.

## Politique des PDF de preuve

Les PDF de chapitre ne sont pas versionnés dans Git : les sources LaTeX, les rapports de LOT et
les verdicts de gates constituent la source de vérité. À chaque compilation CI d'un chapitre,
notamment au LOT 7, le PDF produit dans `build/` est publié comme artefact GitHub Actions.

Au début d'une session, tout chapitre marqué complet dont le PDF est absent du répertoire local
est recompilé avec `make chapter CHAP=<identifiant>`. Le rapport de LOT ou le journal de mission
consigne alors la commande, la date, le nombre de pages et le résultat de l'inspection. Un PDF
absent ne justifie jamais d'abaisser un gate ni de déclarer un chapitre non vérifié sans cette
tentative de ré-attestation.

## Estimation de charge (ordre de grandeur, chapitre lycée standard)

- Corpus : 300–800 chunks utiles par thème après curation.
- Génération : ~120 objets par chapitre (sections de cours, 7 méthodes, ~60 exercices, corrigés, 15 QCM, 2 sujets). En Batch API Sonnet + passes Opus ciblées : quelques dollars à quelques dizaines de dollars par chapitre — le coût dominant reste la revue humaine, que le système réduit à ~4 h/chapitre au lieu de la rédaction intégrale.

---

# PARTIE 8 — DÉMARRAGE : ORDRE DE CONSTRUCTION

1. **Semaine 1** : référentiel capacités (un niveau pilote, ex. Première EDS) + registre des sources initial (~25 sources T1–T4) + duplication du schéma pgvector.
2. **Semaine 2** : crawlers T1/T3 (Eduscol, annales APMEP, Sésamath) + pipeline d'ingestion avec extraction LaTeX ; validation sur 200 chunks.
3. **Semaine 3** : `mcp-corpus` + `mcp-banque` + prompts des agents Curateur et Générateur-Exercices ; test sur une capacité unique de bout en bout.
4. **Semaine 4** : `mcp-sympy` + gates CI + anti-similarité ; production du **chapitre pilote complet (Suites)** en suivant les LOTs 0→7.
5. **Ensuite** : rétrospective du pilote, calibrage des seuils (similarité, couverture, coûts), puis industrialisation chapitre par chapitre.

Le chapitre pilote sert de référence de qualité : ses objets validés deviennent les few-shot examples injectés dans les prompts des agents pour tous les chapitres suivants — c'est le levier principal de consistance du manuel.
