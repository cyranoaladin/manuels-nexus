# Guide de déploiement — pipeline NSI

## Modèle mental (à retenir)

- **`latex/`** = les outils (templates) + les livrables (packs).
- **`docs/`** = le mode d'emploi (ce kit).
- **3 acteurs** : *toi* (décides), *l'agent* Codex/Claude Code (fabrique), *ChatGPT* (relit).

---

## 1. Rangement des fichiers (dépôt `cyranoaladin/NSI`)

| Fichier(s) téléchargé(s) | Destination | Rôle |
|---|---|---|
| `nsi-preamble.sty`, `modele_*.tex` | `NSI/02_modeles_documents/` | Templates réutilisables (source unique) |
| `build.sh`, `README.md` | `NSI/latex/` | Script de compilation + doc |
| `P13_pack/` (`P13_*.tex` + `P13_*.pdf`) | `NSI/latex/packs/premiere/P13/` | Livrable séquence P13 |
| `kit_production_NSI.md` | `NSI/docs/` | Mode d'emploi du pipeline |
| `revue_humaine_PR91_chatgpt.md` | `NSI/docs/` (archive) | Cas particulier PR #91 (le cahier courant = §2 du kit) |

Le `nsi-preamble.sty` doit se trouver dans le même dossier que les `.tex` à compiler (ou dans `TEXINPUTS`). Pour un pack : copier le `.sty` dans le dossier du pack, ou compiler depuis `latex/`.

---

## 2. Qui reçoit quoi

| Acteur | Reçoit | Produit |
|---|---|---|
| Agent (Codex / Claude Code) | **§3** du kit (génération) | Contenu Markdown + CI verte |
| Agent (Codex / Claude Code) | **§4** du kit (LaTeX) | Les `.tex` + PDF (ou `./build.sh`) |
| ChatGPT | **§2** du kit (cahier relecteur) **+ les PDF** | Verdict *publier / corriger* |
| Toi | les verdicts | décision de merge / publication |

---

## 3. Ordre des étapes

### Nouvelle séquence `<SEQ>`
1. (une fois) Déposer `latex/` + commit.
2. Donner le **§3** à l'agent (renseigner `<SEQ>`) → contenu + CI **verte**.
3. Donner le **§4** à l'agent, ou lancer `./build.sh` → les PDF.
4. Donner le **§2 + les PDF** à ChatGPT → décisions.
5. Corriger (reboucler 2–4) si besoin, puis publier.

### Séquence P13 (déjà avancée)
Les étapes 2 et 3 sont **faites** (contenu + 8 PDF produits). Il reste :
1. Déposer `P13_pack/` dans le dépôt.
2. Donner à **ChatGPT le §2 + les 8 PDF de `P13_pack/`**.
3. Appliquer les corrections éventuelles, puis publier.

---

## 4. Portes de qualité (ne jamais publier sans les trois)

1. **Ancrage** — le contenu vient du contrat + programme + RAG (jamais inventé).
2. **Gate machine** — CI verte (ruff, pytest, check-generated-freshness, audit-idempotence, substance_anchors).
3. **Gate humaine** — ChatGPT (§2) rend *publier*.

---

## 5. Commandes utiles

```bash
# Compiler un pack (depuis son dossier, avec nsi-preamble.sty présent) :
./build.sh

# Un seul document :
pdflatex -interaction=nonstopmode -halt-on-error P13_cours.tex

# Gates machine (depuis la racine du dépôt) — les 5 contrôles :
ruff check .
pytest
make check-generated-freshness  # rapports et inventaire régénérés == commités
make audit-idempotence          # metadata, links, privacy, substance, secrets (2 passes)
python -m scripts.check_substance_anchors
```
