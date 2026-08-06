# LOT 3 — Cours TEXP-COMPLEXES-ALGEBRE-GEOMETRIE
2 fichiers de cours (algebre : inverse, equation az=b, demonstrations
conjugue produit/inverse/puissance et binome dans C ; geometrie :
module/argument/affixe, demonstrations |z|^2=z*zbar et module d'un
produit/d'une puissance).

3 defauts trouves et corriges avant commit :
1. Artefact de scratch-work ("if False else...") laisse dans un bloc
   VERIFY -- meme pattern recurrent deja identifie dans les chapitres
   precedents, nettoye.
2. Assertion sympy trop fragile : simplify() ne reduit pas
   automatiquement |z^n|-|z|^n=0 pour z symbolique complexe meme quand
   c'est mathematiquement vrai (limitation connue de sympy sur les
   puissances de modules symboliques) -- remplace par une verification
   numerique exacte (valeurs rationnelles concretes) qui teste la meme
   propriete de facon robuste.
3. Erreur d'infrastructure critique : le caractere unicode brut "ℂ"
   (U+2102) dans le libelle_eleve de contrat.yaml provoque une erreur
   fatale "Glyphe manquant" a la compilation (police TeXGyrePagella sans
   ce glyphe) -- corrige en remplacant par $\mathbb{C}$ (macro LaTeX
   standard). Regle generalisable : ne jamais utiliser de caracteres
   unicode a double barre (ℂ, ℝ, ℕ, ℤ, 𝕌) dans les champs texte de
   contrat.yaml, toujours utiliser $\mathbb{...}$.

0 FAIL et 0 erreur pdflatex apres les trois correctifs.
