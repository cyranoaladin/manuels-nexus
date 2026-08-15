# V5 15 TO 16 ROOT CAUSE ANALYSIS

```yaml
first_divergent_page: 3
last_equal_page: 2
object_pushed: "chapitres/1SPE-DERIVATION-LOCAL/qcm/1SPE-DERIVATION-LOCAL-QCM.tex (débordement vertical QCM)"
source_file: "chapitres/1SPE-DERIVATION-LOCAL/qcm/1SPE-DERIVATION-LOCAL-QCM.tex"
responsible_style_or_class: "N/A (contenu QCM)"
responsible_commit: "533d1919"
root_cause: "La restructuration du QCM de 1SPE-DERIVATION-LOCAL dans le commit 533d1919 a ajouté une grille explicative étendue des réponses et diagnostics, augmentant la hauteur verticale imprimée dans l'environnement faireLePoint, ce qui a poussé la section vers une 16e page."
proof: "Expériences A, B, C et bissection git : commit ff55af2e = 15 pages ; commit 533d1919 = 16 pages. Les 3 paramètres d'onglets (16mm/6mm/6pt) n'ont AUCUN effet sur le nombre de pages (16 pages avant et après en Phase C)."
fix: "Optimiser la mise en page verticale du QCM dans 1SPE-DERIVATION-LOCAL-QCM.tex ou ajuster la réserve d'espace pour ré-englober le QCM et ses diagnostics exacts sur la page 10 sans ajouter de 16e page."
regression_test: "tests/test_maquette_v5.py::test_maquette_v5_acceptance"
```
