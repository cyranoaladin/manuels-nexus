# Décision : deux systèmes LaTeX coexistent — converger ou garder ?

Date : 2026-07-10. Statut : **DÉCIDÉ — Option A (kit pdflatex canonique)**.

## Les deux systèmes

### 1. Kit LaTeX pdflatex (`latex/` + `02_modeles_documents/`)

| Aspect | Détail |
|--------|--------|
| **Moteur** | `pdflatex` (inputenc/fontenc T1) |
| **Préambule** | `nsi-preamble.sty` (design system : couleurs nsiDark/nsiBlue/nsiGold, en-tête `\nsiheader`, barème, listings Python) |
| **Templates** | 8 fichiers `.tex` (cours, td, tp, corrigé, évaluation, trace, fiche_méthode, aides) |
| **Contenu ciblé** | Supports P13 (et futures séquences) — un pack par séquence dans `latex/packs/<niveau>/<SEQ>/` |
| **Compilation** | `./build.sh` par pack (ou dispatcher racine) |
| **Intégration CI** | Aucune (compilation locale uniquement) |
| **Avantage** | Autonome, simple, compatible TeX Live partielle (dégradation gracieuse), templates remplis manuellement ou par agent |
| **Limite** | Pas de fusion Markdown → PDF automatique ; contenu dupliqué entre `.md` (corpus) et `.tex` (pack) |

### 2. Pipeline render_sequence.py (`scripts/render_sequence.py`)

| Aspect | Détail |
|--------|--------|
| **Moteur** | `xelatex` via `pandoc --pdf-engine=xelatex` |
| **Charte** | Inline dans le script Python (LaTeX header template avec Merriweather/Lato/Fira Code, couleurs charter) |
| **Contenu ciblé** | Séquences pilotes (`premiere/sequences/s01_representation_donnees/`) — fusionne les `.md` en deux PDF (élève + professeur) |
| **Compilation** | `python scripts/render_sequence.py <dossier_séquence>` |
| **Intégration CI** | Référencé dans le Makefile (`render-s01`, `render-unit`) |
| **Avantage** | Source unique Markdown → PDF direct, pas de duplication de contenu, version élève et professeur séparées automatiquement |
| **Limite** | Nécessite `xelatex` + `pandoc` + polices spécifiques ; design system différent du kit |

## Points de divergence

| Critère | Kit pdflatex | render_sequence |
|---------|-------------|-----------------|
| Source du contenu | `.tex` (peut diverger du `.md`) | `.md` (source unique) |
| Design system | `nsi-preamble.sty` | Header LaTeX inline |
| Moteur | pdflatex | xelatex |
| Dépendances | TeX Live minimal | TeX Live + pandoc + polices |
| Séparation élève/prof | Manuelle (fichiers distincts) | Automatique |

## Options

### Option A — Converger vers le kit pdflatex
- Abandonner `render_sequence.py`.
- Tous les PDF produits via le kit.
- Contenu dupliqué `.md` → `.tex` (accepté comme coût).

### Option B — Converger vers render_sequence (Markdown → PDF)
- Étendre `render_sequence.py` à toutes les séquences.
- Aligner la charte visuelle (porter `nsi-preamble.sty` vers le header pandoc/xelatex).
- Supprimer les templates `.tex` du kit.
- Source unique = Markdown.

### Option C — Garder les deux (statu quo)
- Kit pour les séquences livrées (P13+).
- render_sequence pour les séquences pilotes (s01).
- Documenter les périmètres respectifs.
- Risque : dérive de charte entre les deux systèmes.

## Décision (2026-07-10)

**Option A retenue** — kit pdflatex canonique pour toutes les nouvelles séquences.
`render_sequence.py` conservé comme LEGACY pour le pilote s01 uniquement.

Les `.tex` des packs sont GÉNÉRÉS depuis le corpus `.md` (source unique = Markdown),
jamais édités à la main — ce sont des artefacts de build, comme les PDF.
