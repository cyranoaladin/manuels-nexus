# LOT 3bis — Charte graphique professionnelle

Date : 2026-07-15. Coût API estimé : 0 $ (production locale). Mode : fichiers / ex nihilo.

La spécification `docs/06_charte_graphique.md` fixe la grille A4 à marge pédagogique, la hiérarchie Libertine, les cinq couleurs Nexus, les pictogrammes, les encadrés imprimables et les règles de respiration. La classe active microtype, `\raggedbottom`, la protection veuves/orphelines, les styles de section et l'ouverture automatique `\ouverturechapitre` alimentée depuis `contrat.yaml` par l'assembleur.

Gates : test rouge puis vert de l'ouverture et des coups de pouce (`2 passed`) ; compilation Suites, Second degré et Dérivation locale : PASS. Inspection réelle des PNG des pages 3, 8 et 29 de Suites : PASS, détail dans `validations/charte.visual.json`.

Exigences métier permanentes : E5/F01 impose au minimum 50 exercices par chapitre et au moins 2 exercices dans chaque case capacité × parcours, au ratio 40/40/20. Tout objet est autonome : corrigé copie-modèle, méthode illustrée, diagnostic de QCM et coups de pouce séparés pour ◆.
