# Cahier des charges — Manuel de mathématiques différencié Nexus Réussite

Version 1.0 — Juillet 2026 — Maître d'ouvrage : Nexus Réussite (M&M ACADEMY SUARL)

---

## 1. Objet

Concevoir et produire, via un pipeline agentique (Claude Code + MCP + scripts), un manuel de mathématiques par niveau, conforme aux programmes officiels français, structuré pour l'accompagnement personnalisé et la pédagogie différenciée selon le gabarit défini dans `docs/01_conception_manuel.md`.

**Périmètre initial (phase pilote)** : Première EDS Mathématiques, chapitre "Suites numériques" (`1SPE-SUITES`), production de bout en bout. **Extension** : chapitres restants de Première, puis Terminale EDS + Maths Expertes, puis autres niveaux.

## 2. Livrables

### 2.1 Livrables logiciels (le noyau, objet du présent dépôt)
- L1. Pipeline corpus : crawlers, ingestion (extraction texte+LaTeX), indexation pgvector hybride.
- L2. Base de données PostgreSQL : corpus, référentiel de capacités, banque d'objets, validations (`db/schema.sql`).
- L3. Quatre serveurs MCP : `mcp-corpus`, `mcp-banque`, `mcp-sympy`, `mcp-latex`.
- L4. Scripts de gates : vérification SymPy, anti-similarité, couverture, assemblage.
- L5. CI GitHub Actions bloquante.
- L6. Prompts systèmes des 7 agents de composition.
- L7. Kit LaTeX : classe `nexus-manuel.cls`, macros, gabarit de chapitre.

### 2.2 Livrables éditoriaux (par chapitre)
- E1. Contrat du chapitre (capacités C1..Cn en langage élève, référencées B.O.).
- E2. Diagnostic d'entrée + fiches R de remise à niveau.
- E3. Cours en 3 strates ; E4. Fiches méthodes M1..Mn ; E5. ≥ 50 exercices répartis ◆/◆◆/◆◆◆ (ratio 40/40/20) avec corrigés et coups de pouce ; E6. 2 TD ; E7. QCM d'auto-évaluation + circuit de remédiation ; E8. Évaluation A + version B + barème par compétences.
- E9. PDF chapitre compilé sous bannière Nexus Réussite + exports (QCM JSON pour plateforme).

## 3. Exigences fonctionnelles

| ID | Exigence | Priorité |
|---|---|---|
| F01 | Chaque capacité du programme officiel est couverte par : 1 section de cours, 1 fiche méthode, ≥ 2 exercices par parcours, ≥ 1 item QCM, 1 item de remédiation | Must |
| F02 | Tout exercice porte des métadonnées conformes à `schemas/exercice.schema.json` | Must |
| F03 | Les exercices numériques sont paramétrés (variables SymPy) permettant la génération de variantes isomorphes (versions B) | Should |
| F04 | Le corpus est interrogeable par requête hybride (vecteur + BM25 + rerank) avec filtres tier/type/niveau/usage_policy | Must |
| F05 | Le rapport de couverture identifie toute case vide de la matrice capacités × parcours | Must |
| F06 | L'assemblage génère le chapitre complet ET les déclinaisons (livret méthodes, recueil par parcours, livret remédiation) depuis les mêmes sources | Should |
| F07 | Les QCM ont chaque distracteur relié à une erreur type documentée avec message de diagnostic | Must |
| F08 | Système de codage C/M/R + ◆ + pictogrammes conforme à `docs/01` Partie 4 | Must |

## 4. Exigences non fonctionnelles

| ID | Exigence |
|---|---|
| N01 | **Exactitude** : 0 objet publié sans verdict SymPy `verified` ou revue humaine tracée dans `validations/` |
| N02 | **Propriété intellectuelle** : similarité n-gram (n=8) avec toute source T2/T4 < 0,35 ; attribution obligatoire pour T1/T3-libre adapté |
| N03 | **Conformité** : traçabilité complète objet ↔ capacité ↔ B.O. (tableau de correspondance généré) |
| N04 | **Reproductibilité** : `make setup && make chapter CHAP=X` reconstruit le PDF à l'identique sur machine vierge (Ubuntu 24 / Mint 22) |
| N05 | **Coût** : production LLM ≤ 40 $ par chapitre en régime de croisière (Batch API pour les lots massifs) |
| N06 | **Crawling responsable** : robots.txt respecté, throttling ≥ 2 s/req/domaine, User-Agent identifié, uniquement les domaines du registre |
| N07 | **RGPD** : aucun contenu de copie d'élève réelle non anonymisée dans le corpus |

## 5. Architecture imposée

- Python ≥ 3.11, PostgreSQL ≥ 16 + pgvector, texlive-full (pdflatex), FastMCP pour les serveurs, Git/GitHub avec CI Actions.
- Embeddings 1024d (modèle au choix : voyage-3 / bge-m3 — cohérent avec la stack RAG existante), reranker CrossEncoder MiniLM.
- Modèles LLM : Anthropic (Sonnet pour la masse, Opus/Fable pour strate ★, ◆◆◆ et revue adversariale), Batch API pour les lots non interactifs.
- Déploiement cible des services : serveur Hetzner existant (base et MCP), exécution des agents en local via Claude Code.

## 6. Critères d'acceptation de la phase pilote

1. `make setup` s'exécute sans erreur sur machine vierge.
2. Pipeline corpus opérationnel sur ≥ 10 sources du registre, ≥ 300 chunks indexés sur le thème suites, précision de la recherche validée sur 20 requêtes de test (`tests/test_retrieval.py`).
3. Chapitre 1SPE-SUITES produit intégralement (E1→E9), tous gates verts, check-list qualité (docs/01 Partie 8) à 100 %.
4. Relecture humaine finale : ≤ 3 corrections mathématiques mineures sur l'ensemble du chapitre, 0 correction majeure.
5. Rapports LOT-0 → LOT-7 présents et complets.
6. Version B de l'évaluation générée automatiquement par re-paramétrage et vérifiée.

## 7. Organisation et validation

- Production par LOTs (voir `CLAUDE.md` §3), validation humaine bloquante en sortie des LOTs 0, 2, 3 et 7.
- Toute évolution du gabarit pédagogique (docs/01) ou du référentiel passe par le maître d'ouvrage.
- Rétrospective obligatoire après le pilote : calibrage des seuils (similarité, couverture, coûts) avant industrialisation.

## 8. Risques identifiés et parades

| Risque | Parade |
|---|---|
| Extraction LaTeX défaillante sur PDF complexes | Fallback vision LLM par zone ; échantillonnage qualité 5 % en revue humaine |
| Hallucination réglementaire (capacité inventée) | Référentiel = seule source de vérité (R7) ; gate conformité |
| Contamination de licence (CC-BY-SA) | `usage_policy` propagée ; adaptation substantielle par défaut ; revue juridique avant commercialisation |
| Dérive de qualité entre chapitres | Few-shot issus du pilote certifié ; check-list bloquante identique |
| Coût API dérivant | Compteur de coût par LOT dans les rapports ; Batch API ; Haiku pour la classification |
