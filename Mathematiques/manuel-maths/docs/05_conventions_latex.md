# Conventions LaTeX du manuel

## Classe et macros
Classe : `gabarits/nexus-manuel.cls`. Ne jamais définir de macro locale dans un objet : toute macro manquante se demande (évolution de la classe, validée par un humain).

| Usage | Macro/environnement |
|---|---|
| Définition / propriété / théorème | `\definition[num]{...}` `\propriete[num]{...}` `\theoreme[num]{...}` |
| Exemple / contre-exemple | `\exemple{...}` `\contreexemple{...}` |
| Appui de marge (strate 2) | `\margeAppui{...}` |
| Erreur fréquente | `\erreurFrequente{...}` |
| Approfondissement ★ (strate 3) | `\approfondissement{...}` |
| Fiche méthode | `\begin{fichemethode}{M2}{Montrer qu'une suite est arithmétique}` + les 6 rubriques |
| Exercice | `\begin{exercice}{1SPE-SUITES-EX-024}{2}{15}` (id, parcours 1–3, durée min) |
| Corrigé | `\begin{corrige}{1SPE-SUITES-EX-024}` |
| Coup de pouce | `\coupDePouce{1}{...}` (1=reformulation, 2=première étape, 3=plan) |
| Code Python | `\begin{python} ... \end{python}` |
| Barème | `\baremeIndicatif{Q1 : 1 pt (calculer) ; Q2 : 2 pts (raisonner, communiquer)}` |

## Notations imposées (B.O.)
- Suite : $(u_n)$ ou $(u_n)_{n\in\mathbb{N}}$ ; terme : $u_n$ ; jamais $\{u_n\}$ ni $u(n)$ (sauf lecture algorithmique explicite).
- Ensembles : $\mathbb{N}, \mathbb{Z}, \mathbb{R}$ (`amssymb`).
- Intervalles à la française : $[0\,;\,1]$, point-virgule séparateur.
- Décimaux à la française : virgule ($3{,}5$).
- Vecteurs (autres chapitres) : $\vec{u}$.

## En-têtes obligatoires de chaque fichier
```
% META: {"id": "1SPE-SUITES-EX-024", "chapitre": "1SPE-SUITES", "type_objet": "exercice", ...}
% BEGIN-VERIFY
% from sympy import *
% ...assertions...
% END-VERIFY
```
Le bloc VERIFY est obligatoire pour exercices/corrigés/évaluations à résultats calculables ; son absence entraîne `manual_review` (jamais `ready` automatique).

## Interdits
- `\\` pour sauter des lignes en mode texte ; utiliser des paragraphes.
- Packages non chargés par la classe (demander l'ajout).
- Contenu hors macro dans les strates (tout passe par les environnements : c'est ce qui permet les déclinaisons F06).
- `rsync --delete` sur `gabarits/` : les extensions NSI (`nexus-code.tex`, `nexus-figures-nsi.tex`) n'existent que côté NSI et seraient détruites.

## Polices
JetBrains Mono est résolu par nom système. Installer avec `make setup-fonts` (copie les .otf de `gabarits/fonts/` dans `~/.local/share/fonts/` et met à jour le cache fontconfig). TeX Gyre Pagella et TeX Gyre Heros sont fournis par `texlive-fonts-recommended`.

## Synchronisation de la charte
La synchro entre projets se fait UNIQUEMENT par `python scripts/check_charte_sync.py` (7 fichiers du tronc commun) ou le rsync fichier-par-fichier de `SYNC_CHARTE.md`. Voir `docs/06_charte_graphique.md` §12.
