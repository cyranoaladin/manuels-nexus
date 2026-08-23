# Matrice programme ↔ manuel — 1SPE (édition 2026-2027)

Autorité programme : `MENE2602917A`, BO n° 14 du 2 avril 2026, applicable à la rentrée 2026-2027. Le texte archivé est `Mathematiques/manuel-maths/sources/txt/BO2026_1SPE_specialite.txt` (`sha256:4e70f1989cdb47caf184cb138d839799e895fcdc5addec3737f0216b6bfa33df`).

La source ligne par ligne est `audit/PROGRAM_COVERAGE_MATRIX_1SPE.json`. L'ancien rapport `CONFORMITE_BO2026.md` n'est pas une autorité et n'a pas servi de preuve autonome.

## État courant

- Lignes : 73.
- Atoms obligatoires : 61/61 mappés.
- `STRUCTURALLY_MAPPED` : 54.
- `CONTENT_REVIEW_PENDING` : 4 (`1SPE-MATRIX-008`, `036`, `038`, `056`).
- `TRANSVERSAL_NOT_CHAPTER_SCOPED` : 3.
- `FULL` : 0. Aucun chemin existant n'est assimilé à une validation scientifique et pédagogique.
- `WRONG_YEAR` : 0.
- `UNSUPPORTED_CLAIM` : 0.

Les quatre lignes `CONTENT_REVIEW_PENDING` ont une source réelle mais restent soumises aux audits scientifique et pédagogique. Les trois lignes transversales sont couvertes hors d'un chapitre unique et restent également non `FULL`.

## Hors programme Première résolu

Les anciennes capacités trigonométriques C3/C4/C5 ont été retirées du contrat canonique. Les ressources utiles restantes sont explicitement classées `OPTIONAL_EXTENSION`, avec le label « Approfondissement — Vers la Terminale », sous les codes X1/X2/X3. Elles sont exclues du diagnostic obligatoire, des QCM du socle et des critères de couverture du programme.

La loi binomiale nommée et ses formules ne sont plus des capacités officielles alléguées. Le socle traite la répétition de deux à quatre épreuves de Bernoulli par arbres et nombre de succès, ainsi que les variables aléatoires et les transformations affines. Les ressources de formalisation binomiale conservées portent X1/X2 et le même label d'approfondissement.

Les cinq anciennes lignes de finding restent dans le JSON sous `AUDIT_METADATA_ONLY` afin de préserver l'historique de résolution ; elles ne sont pas des atoms officiels.

## Gap obligatoire fermé

`1SPE-ATOM-008`, sensibilisation intuitive aux limites finie, infinie et à l'absence de limite sans formalisation, possède maintenant un cours, une méthode, un exercice corrigé, une remédiation et un QCM dédiés. Son état reste `CONTENT_REVIEW_PENDING` jusqu'aux contrôles de qualité.

## Épreuve anticipée

L'alignement d'épreuve est un namespace distinct du programme : écrit de 2 h, coefficient 2, sans calculatrice, partie automatismes/QCM sur 6 points puis deux à trois exercices sur 14 points. Les approfondissements Terminale ne peuvent apparaître comme exigibles dans un sujet type 1SPE.
