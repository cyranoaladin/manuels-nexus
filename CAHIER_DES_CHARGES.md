# Cahier des charges — Manuels NSI Première & Terminale Nexus Réussite

Version 1.0 — Juillet 2026 — Maître d'ouvrage : Nexus Réussite (M&M ACADEMY SUARL)

## 1. Objet

Produire, via le pipeline agentique éprouvé sur le manuel de mathématiques, deux manuels d'accompagnement différencié pour la spécialité NSI (Première et Terminale), conformes au programme officiel, en **restructurant prioritairement le corpus propriétaire certifié** du dépôt `cyranoaladin/NSI` (114 capacités, 445 tests exécutables) selon la table de transposition de `docs/08_specificites_nsi.md`.

**Phase pilote** : Première, chapitre `1NSI-TYPES-CONSTRUITS` (p-uplets, tableaux, dictionnaires) — le mieux couvert par le corpus, riche en erreurs types, représentatif (code + figures mémoire + QCM). **Extension** : Première complète (10 chapitres), puis Terminale (12 chapitres + blocs ECE/écrit).

## 2. Livrables

### 2.1 Logiciels (le noyau, présent dépôt)
- L1. Pipeline de récolte T0 : `harvest_nsi.py` + filtre `md2nexus.lua` + rapport de transposition.
- L2. Gates NSI : `verify_python.py` (exécution sandbox, pytest, traces), gate ruff, similarité avec exemption T0, couverture, accents.
- L3. Référentiels générés depuis `programme_nsi_2019.yaml` (`convert_programme_yaml.py`).
- L4. Extensions charte : `nexus-code.tex` (code/console), `nexus-figures-nsi.tex` (arbres, mémoire, graphes, SQL, réseaux), icônes partagées.
- L5. MCP : corpus (RAG NSI existant), banque, python-sandbox, latex. CI bloquante.
- L6. Prompts : restructurateur (nouveau), générateur ECE (nouveau), + les 7 agents hérités adaptés.

### 2.2 Éditoriaux (par chapitre)
E1–E8 identiques au manuel maths (contrat, diagnostic+fiches R, cours 3 strates, méthodes, ≥50 exercices 40/40/20 avec corrigés et CDP, 2 TD, QCM+remédiation, évaluations A/B), plus :
- **E9. Mini-projet** jalonné (cahier des charges, jalons à critères testables, grille d'auto-évaluation, extension ◆◆◆).
- **E10 (Terminale)** : ≥ 2 sujets format Épreuve pratique par chapitre concerné (prog. sur spécification + code à compléter), corrigés validés par exécution contre les jeux de tests.
- **E11. Déclinaison livret professeur** (depuis `guide_professeur.md` des séquences).

## 3. Exigences fonctionnelles

| ID | Exigence | Priorité |
|---|---|---|
| F01 | Couverture : chaque capacité a 1 section de cours, 1 fiche M, ≥2 ex/parcours, ≥1 QCM, 1 remédiation | Must |
| F02 | Métadonnées conformes aux schémas, avec `mode_creation` et traçabilité vers corpus_nsi | Must |
| F03 | **Toute sortie de programme affichée est produite par exécution réelle** (gate traces) | Must |
| F04 | Tout code élève est ruff-clean, Python 3 ; annotations de type en Terminale | Must |
| F05 | Matrice de couverture avec détection des cases vides | Must |
| F06 | Déclinaisons depuis les mêmes sources : complet, méthodes, remédiation, **livret professeur** | Should |
| F07 | QCM : chaque distracteur = erreur documentée + diagnostic + renvoi | Must |
| F08 | Héritage des statuts : objet issu d'une séquence `needs_review` → flag dans `A_VALIDER_HUMAIN.md` | Must |
| F09 | Mini-projet par chapitre avec jalons testables ; 2 projets fil rouge par manuel | Must |
| F10 | Terminale : formats officiels écrit (3 exercices) et ECE respectés (vérifiés en ligne, R7) | Must |
| F11 | Déclinaison version aménagée par chapitre : énoncés allégés, consignes séquencées, mise en page aérée, générée depuis les mêmes objets avec les sources `version_amenagee` transposées | Should |

## 4. Exigences non fonctionnelles

| ID | Exigence |
|---|---|
| N01 | 0 objet `ready` sans verdict d'exécution `verified` ou revue humaine tracée |
| N02 | Similarité n-gram (n=8) < 0,35 contre toute source T2/T4 ; T0 exempté |
| N03 | Traçabilité objet ↔ capacité ↔ B.O. ↔ séquence source |
| N04 | Reproductible : `make setup && make chapter CHAP=X` sur machine vierge (Mint 22 / Ubuntu 24) |
| N05 | Coût LLM ≤ 25 $/chapitre Première (restructuration dominante), ≤ 40 $/chapitre Terminale |
| N06 | `corpus_nsi/` en lecture seule ; RGPD : aucun contenu élève non anonymisé |
| N07 | Accents français corrects dans tout libellé imprimé (gate CI) |

## 5. Architecture imposée

Python ≥ 3.11, pandoc (filtre Lua), texlive-full, ruff, pytest ; PostgreSQL+pgvector optionnel (MODE FICHIERS supporté nativement, leçon du run maths) ; FastMCP ; charte Nexus synchronisée depuis manuel-maths (tronc commun intouchable, extensions NSI en fichiers séparés) ; modèles Anthropic (Sonnet production, Opus ◆◆◆/ECE/adversarial) quand la clé est disponible, rédaction locale par l'agent sinon (mode nominal, coût 0 $ consigné).

## 6. Check-list NSI ajoutée au LOT 7 (en plus de docs/01 Partie 8)

- [ ] 100 % des sorties de programmes vérifiées par exécution (rapport verify joint).
- [ ] 100 % du code élève ruff-clean.
- [ ] ≥ 8 figures dans les chapitres structures/architecture ; chaque déroulé d'algorithme illustré.
- [ ] Rubrique « À la machine » présente dans chaque section.
- [ ] Mini-projet jalonné avec tests fournis et exécutés.
- [ ] Terminale : ≥ 2 sujets ECE au format officiel, corrigés validés contre les tests.
- [ ] Version aménagée (F11) : extrait généré et joint au PDF pilote pour validation.
- [ ] Distinction visuelle code/console respectée partout.
- [ ] Erreurs fréquentes NSI : ≥ 4 par chapitre, issues du corpus ou documentées.
- [ ] Aucun objet `ready` hérité d'une séquence `needs_review` sans revue tracée.

## 7. Critères d'acceptation du pilote

1. `make setup` sans erreur ; `make harvest CHAP=1NSI-TYPES-CONSTRUITS` produit le rapport de transposition avec ≥ 80 % des capacités couvertes par des sources T0.
2. Chapitre pilote complet (E1–E9), check-lists 100 %, PDF compilé sous charte Nexus.
3. Relecture humaine : ≤ 3 corrections mineures, 0 majeure ; **validation visuelle et pédagogique humaine du pilote avant industrialisation** (rendu figures mémoire, équilibre transposition/réécriture, densité `\codereference`).
4. Rapports LOT 0→7 + rapport de transposition présents.

## 8. Risques et parades

| Risque | Parade |
|---|---|
| Conversion Markdown → LaTeX dégradée (code, tableaux) | Filtre Lua dédié + gate compilation objet par objet + échantillonnage visuel |
| Contenu source `needs_review` publié sans audit | F08 : héritage de statut bloquant + registre |
| Programme NSI modifié depuis BO 2019 | R7 : vérification en ligne au LOT 0, YAML source mis à jour en amont |
| Formats ECE/écrit obsolètes | R7 : vérification des textes en vigueur avant LOT 6 Terminale |
| Divergence de charte entre manuels | Tronc commun synchronisé depuis manuel-maths, extensions en fichiers séparés uniquement |
