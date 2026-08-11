# Kit LaTeX NSI — prod-ready

Système de templates unifié pour produire les documents d'une séquence NSI (cours, TD, TP,
corrigé, évaluation, trace, fiche méthode, aides) en PDF, à partir du corpus assaini.

## Contenu

| Fichier | Rôle |
|---|---|
| `build.sh` | Compile tous les `.tex` du dossier en PDF (pdflatex). |
| `packs/premiere/P13/` | Pack compilé séquence P13 (`.tex` + `.pdf` + `build.sh` local). |
| `../02_modeles_documents/nsi-preamble.sty` | Préambule partagé (design system, source unique). |
| `../02_modeles_documents/modele_*.tex` | 8 templates, un par type de document (source unique). |

## Moteur

**pdflatex** (choix assumé : compatible avec l'encodage `inputenc/fontenc T1` des templates,
sans migration ni shell-escape). Le préambule dégrade gracieusement si `babel-french` ou
`lmodern` sont absents (`\IfFileExists`), donc il compile même sur une TeX Live partielle ;
en environnement complet, la typographie française s'active automatiquement.

## Utilisation

```bash
# Compiler tout le dossier :
./build.sh

# Ou un seul document :
pdflatex -interaction=nonstopmode -halt-on-error P13_evaluation.tex
```

Le `.sty` doit être dans le dossier de compilation (ou dans le `TEXINPUTS`).

## Design system (`nsi-preamble.sty`)

- Tokens couleur : `nsiDark`, `nsiBlue`, `nsiGold`, `nsiGray`.
- En-tête unifié `\nsiheader{titre}{niveau}{séquence}{durée}{capacités}{source}{statut}` (7 champs cohérents).
- Titres stylés (`titlesec`), listes (`enumitem`), tables (`booktabs`), math (`amsmath`).
- Code Python : style `nsipython` (`listings`), accents gérés.
- Barème normalisé : environnement `bareme` (deux colonnes Compétence / Pts).

## Règle impérative pour la génération automatique

Trois commandes LaTeX avalent un argument optionnel `[...]` :  `\\[`, `\midrule[`, `\tabularnewline[`.
Donc **toute cellule de tableau qui commence par un placeholder `[...]` doit être protégée par `{}`** :

```latex
{[Compétence 1]} & [pts] \\      % correct
[Compétence 1]  & [pts] \\        % casse la compilation
```

L'agent LaTeX du pipeline doit appliquer cette règle systématiquement.

## Place dans le pipeline (voir kit_production_NSI.md)

1. Génération du contenu (Markdown) ancré sur contrat + programme + RAG.
2. **Gate machine** : CI verte (ruff + pytest + audit + substance_anchors).
3. Mise en forme via ces templates → PDF (`build.sh`).
4. **Gate humaine** : revue ChatGPT.
5. Publication.

## Types couverts vs `modele_sequence.yaml`

Couverts : cours, td, tp, corrige, evaluation, trace (trace\_ecrite), fiche\_methode, aides (aides\_progressives).
Le `guide_prof` reste en Markdown (`.md`) et le `qcm` en JSON — non concernés par LaTeX.
