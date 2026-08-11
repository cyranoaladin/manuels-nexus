# Kit de production NSI — Revue ChatGPT + génération LaTeX/PDF

> **État de départ.** Corpus `cyranoaladin/NSI`, séquence pilote **P13** (dichotomie / glouton / k-NN). La PR #91 (remediation/p13-coherence) corrige le contenu P13 et ajoute un guard dédié — elle reste ouverte en attente de merge. Le pipeline de production s'appuie sur les gates CI existants (voir ci-dessous).

---

## 0. Principe directeur

Chaque document produit passe **trois portes** avant publication :
1. **Ancrage** — tout contenu vient du corpus, du contrat de séquence et du programme officiel. Interdiction d'inventer données, résultats ou capacités.
2. **Gate machine** — la CI (`.github/workflows/ci.yml`) doit être **verte** : ruff, pytest, freshness, audit-idempotence, check_substance_anchors, check_status_promotion_guard, check_no_committed_secrets.
3. **Gate humaine** — revue ChatGPT selon le cahier des charges §2 (recalcul à la main, conformité pédagogique, rendu).

Un document qui ne franchit pas les trois portes ne devient pas un PDF publié.

---

## 0bis. Règle d'architecture (source unique + CANON-FIRST)

Le `.md` certifié dans `03_progressions/supports/` est la **SOURCE UNIQUE**. Les `.tex`
dans `latex/packs/` sont des projections manuelles de ce corpus via les templates de
`02_modeles_documents/`. À terme, un script de projection `md→tex` déterministe les
régénérera automatiquement.

**CANON-FIRST** : toute correction de contenu commence par le `.md` canonique, puis se
propage à la projection `.tex` — JAMAIS l'inverse. Une correction qui n'existe que dans
`latex/` est une divergence, pas une correction.

**État actuel (2026-07-11)** : le gate `check-generated-freshness` couvre les rapports et
l'inventaire (manifest.csv, qa_report.md, etc.). Il ne couvre **PAS encore** la fraîcheur
md↔tex des packs LaTeX — ce gate sera implémenté à l'étape « industrialisation LaTeX »
(post-flip RELEASE_READY). En attendant, la cohérence md↔tex est vérifiée manuellement.

> **Dette inscrite** : gate de fraîcheur md↔tex — déclencheur = étape industrialisation LaTeX.

> **Post-mortem PR #91 (2026-07-11)** : la PR « REM4 : éradiquer la contamination
> par rotation +1 dans P13 » a été fermée sans merge le 2026-07-10 au motif
> « remplacé par le pack ». Or le pack .tex est une PROJECTION du canon .md
> (règle CANON-FIRST ci-dessus) — pas un substitut. La fermeture a jeté le fix
> de rotation des exercices 2-8, entraînant un cycle de correction F5/F5C/W.
>
> **RÈGLE** : une PR de remédiation de CONTENU (fichiers .md canon) ne se ferme
> jamais sans preuve `git diff main -- <fichiers_canon>` montrant que main
> subsume déjà le diff. À défaut, la PR reste ouverte ou son diff est cherry-
> picked avant fermeture.

**Diff de cohérence md↔tex P13** (4 champs, après corrections F5) :

| Ex | Champ | Canon (.md) | Projection (.tex) | ✓ |
|----|-------|-------------|-------------------|---|
| 1 (P-ALGO-04) | Résultat | milieux 18 puis 37 → indice 4 | valeurs lues aux milieux : 18 puis 37 → indice 4 | ✓ |
| 2 (P-ALGO-04) | Variant | V décroît de 6 à 3 → terminaison | V = 6 → 3 → terminaison | ✓ |
| 3 (P-ALGO-05) | Cas limite | montant=28 avec [10,5,2] → reste 1 | montant 28 avec [10,5,2] → reste 1 | ✓ |
| 4 (P-ALGO-03) | Résultat | rouge (2 voix) vs bleu (1) → classe rouge | rouge 2, bleu 1 → classe rouge | ✓ |

---

## 1. Architecture du pipeline (ÉTAT CIBLE — générateur md→tex, post-flip)

> État actuel : la projection md→tex est manuelle, sous règle CANON-FIRST.

```
séquence choisie
   │
   ├─ SOURCES : contrat (_contract.yml) + programme_nsi_2019.yaml + corpus .md + RAG (cyranoaladin/RAG)
   │
   ▼
[Agent de génération]  → produit / met en forme le contenu par type de document
   │                      (cours, TD, corrigé, TP, évaluation, barème, fiche)
   ▼
[Gate machine]  CI verte (ruff + pytest + audit + substance_anchors)  → doit être VERT
   │
   ▼
[Agent LaTeX]  → .tex via le kit pdflatex (02_modeles_documents/ + nsi-preamble.sty)
   │              Les .tex sont GÉNÉRÉS depuis le corpus .md (source unique = Markdown),
   │              jamais édités à la main — artefacts de build comme les PDF.
   ▼
[Compile]  pdflatex (build.sh)  → PDF
   │
   ▼
[Gate humaine]  Revue ChatGPT (cahier des charges §2)  → PASS / corrections
   │
   ├─ corrections → retour à l'agent concerné → régénération
   ▼
PUBLICATION (PDF + sources versionnées)
```

Le RAG (`cyranoaladin/RAG`, pgvector) sert à **retrouver et réutiliser** les formulations, définitions et exemples déjà validés du corpus — pas à générer du neuf non ancré.

---

## 2. Cahier des charges — ChatGPT relecteur NSI (généralisé, réutilisable)

> À coller à ChatGPT pour **toute** revue de document ou de séquence, pas seulement une PR. ChatGPT a accès à GitHub : lui donner le dépôt, la branche/commit et le(s) fichier(s) ou le PDF à revoir.

Tu es **relecteur pédagogique et technique senior** (professeur agrégé NSI + lead technique). Tu fais la revue humaine qualifiée d'un document NSI destiné à des élèves, avant publication. Tu ne refais pas le travail des agents et **tu ne leur fais pas confiance** : tu vérifies toi-même contre les sources.

**Posture (obligatoire) :**
1. Ne crois aucun rapport d'agent ni aucun « PASS » automatique. Ouvre les fichiers réels et le PDF.
2. **Recalcule à la main** chaque valeur numérique (traces d'algorithmes, variants, sommes gloutonnes, votes k-NN, complexités). Un contenu « cohérent » peut rester faux.
3. Vérifie la **conformité au programme officiel** `00_programmes_officiels/programme_nsi_2019.yaml` : chaque capacité annoncée (P-ALGO-xx, P-IHM-xx, T-LANG-xx…) correspond bien à ce que le document enseigne réellement.
4. Vérifie la **cohérence transversale** : énoncé ↔ corrigé ↔ barème ↔ évaluation ↔ fiche partagent les mêmes données, résultats et capacités. Aucune rotation, aucune notation contradictoire.
5. Vérifie le **rendu** : le PDF compile, pas de débordement, tables/figures/algorithmes lisibles, code correctement formaté, français correct.
6. Respecte les **règles maison** : synthèses de cours NSI terminale ≤ 3 paragraphes ; style factuel sans envolées ; pas de chiffres d'utilisateurs invérifiables ; images à texte exclusivement français.
7. Conclus **par une décision nette** par document : `PASS` / `À CORRIGER` (liste précise `fichier:ligne` + correction attendue) ; puis **Publier / Publier après corrections / Ne pas publier**.

**Points de substance que les guards ne voient pas (à traquer en priorité) :**
- exactitude arithmétique (variants qui doivent atteindre 0 en cas absent ; sommes ; distances k-NN) ;
- faisabilité : tout exercice doit être résoluble avec les seules données fournies (un code à corriger doit figurer dans l'énoncé) ;
- adéquation capacité ↔ contenu réel (l'étiquette ne doit pas mentir) ;
- qualité pédagogique : progressivité, consignes non ambiguës, corrigés qui répondent aux questions posées.

**Format de sortie :** (1) verdict global ; (2) tableau `document | PASS/À CORRIGER | preuve | correction` ; (3) anomalies de substance détaillées avec recalcul ; (4) décision de publication.

---

## 3. Prompt — Agent de génération (séquence → contenu ancré)

> À coller à l'agent (Codex / Claude Code) pour produire ou mettre en forme le contenu d'une séquence avant LaTeX.

CONTEXTE : dépôt `cyranoaladin/NSI`. Produire les documents de la séquence <SEQ> (niveau <NIVEAU>).
SOURCES D'AUTORITÉ, dans cet ordre : (1) `…/contracts/<SEQ>_contract.yml` (capacités, notions, cas-limites,
exemples obligatoires) ; (2) `00_programmes_officiels/programme_nsi_2019.yaml` ; (3) le corpus `.md` existant
de la séquence ; (4) le RAG `cyranoaladin/RAG` pour réutiliser formulations et exemples déjà validés.

RÈGLES :
- N'invente aucune donnée, aucun résultat, aucune capacité. Tout est traçable aux sources ci-dessus.
- Étiquetage des capacités STRICTEMENT conforme au programme (ex. P-ALGO-03 = k-NN ; P-ALGO-04 = recherche
  dichotomique, recherche + variant ; P-ALGO-05 = glouton).
- Style factuel, sans envolées. Synthèses de cours NSI terminale : ≤ 3 paragraphes.
- Cohérence transversale : mêmes données/résultats dans cours, TD, corrigé, TP, évaluation, barème, fiche.

DOCUMENTS À PRODUIRE (par type) : cours, TD, corrigé du TD, TP, évaluation, corrigé + barème, fiche de révision.

GATE OBLIGATOIRE avant de rendre : la CI (ruff + pytest + audit + substance_anchors) doit être **VERTE**.
Si rouge, corriger jusqu'au vert. Fournir la sortie de la CI comme preuve.

SORTIE : fichiers Markdown mis à jour + confirmation guard vert. NE PAS compiler le LaTeX ici (étape séparée).

---

## 4. Prompt — Agent LaTeX → PDF

> Étape de mise en forme, une fois le contenu validé par la gate machine.

CONTEXTE : contenu Markdown validé de la séquence <SEQ>. Le transformer en documents LaTeX puis PDF.
- Utilise le **kit LaTeX partagé `nsi-preamble.sty`** (design system NSI). Chaque document commence par
  `\documentclass[a4paper,11pt]{article}` puis `\usepackage{nsi-preamble}` — ne réinvente pas la charte.
- Un `.tex` par document, sur le modèle correspondant (cours, td, tp, corrige, evaluation, trace,
  fiche_methode, aides).
- En-tête via `\nsiheader{titre}{niveau}{séquence}{durée}{capacités}{source}{statut}`.
- Code Python via l'environnement `listings` (style `nsipython`) ; math via `amsmath` ; barème via
  l'environnement `bareme`.
- **RÈGLE IMPÉRATIVE** : toute cellule de tableau commençant par un placeholder `[...]` doit être
  protégée par `{}` (`{[Compétence 1]}`), sinon `\\[`, `\midrule[` ou `\tabularnewline[` avalent la cellule.
- Moteur : **pdflatex** (compatible `inputenc/fontenc T1` du kit). Compiler avec `./build.sh` ou
  `pdflatex -interaction=nonstopmode -halt-on-error <fichier>.tex` ; corriger jusqu'au PDF propre.

SORTIE : les `.tex` + les PDF compilés, versionnés. Signale tout débordement ou glyphe manquant.

---

## 5. Pilote — Séquence P13 (à lancer en premier)

P13 est le meilleur candidat pilote : contenu vérifié, contrat à jour, guard vert.

**Lot pilote (definition of done) :** un pack cohérent élève + enseignant, en PDF —
`P13_cours`, `P13_TD` + `P13_corrige`, `P13_tp`, `P13_evaluation` + `P13_bareme`, `P13_fiche_revision`.

**Critères de sortie du pilote :**
- guard vert sur tout le contenu P13 ;
- chaque PDF compile sans erreur, sans débordement ;
- revue ChatGPT (cahier des charges §2) → **Publier** sur les 7 documents ;
- arithmétique du variant conforme (convention `V = droite − gauche + 1`, atteint 0 en cas absent).

Une fois le pilote publié, le même enchaînement (§3 → gate → §4 → §2) se rejoue séquence par séquence.

---

## 6. Ordre de lancement (pour démarrer aujourd'hui)

1. **Merger PR #91** puis soumettre le dossier v3 (`docs/promotion/`) à la revue lead pour promotion `needs_review → validated_pedagogy` (cf. AGENTS.md §6 — revue lead signée, pas de promotion automatique).
2. Lancer l'**agent de génération** (§3) sur `<SEQ>=P13, <NIVEAU>=premiere` → contenu + guard vert.
3. Lancer l'**agent LaTeX** (§4) → 7 PDF.
4. Confier les 7 PDF + sources à **ChatGPT** (§2) → décisions de publication.
5. Boucler les corrections éventuelles, publier, puis passer à la séquence suivante.

---

### Une note de cadrage
Le pilote P13 sert à **éprouver le pipeline**, pas seulement à sortir des PDF : c'est là qu'on vérifie que les trois portes (ancrage, gate machine, gate humaine) s'enchaînent proprement. Ne pas lancer 15 séquences en parallèle avant que P13 soit publié et que le pipeline soit rodé — sinon on rediffuse à l'échelle les défauts qu'on vient de mettre des jours à corriger sur une seule séquence.
