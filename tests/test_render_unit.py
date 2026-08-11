from __future__ import annotations

import unittest

from scripts.check_rendered_unit_artifacts import check_unit, student_leak_errors
from scripts.render_unit import build_html, strip_teacher_sections


class RenderUnitStudentTeacherSeparationTests(unittest.TestCase):
    def test_student_scenario_with_professeur_is_preserved(self) -> None:
        markdown = """# Activité

## Consigne

Le professeur veut obtenir les identifiants classés.
"""

        rendered = strip_teacher_sections(markdown)

        self.assertIn("Le professeur veut obtenir", rendered)

    def test_teacher_section_is_removed_until_same_level_heading(self) -> None:
        markdown = """# Activité

## Consigne

Le professeur veut obtenir les identifiants classés.

## Repères enseignant — à masquer dans la projection élève

| Question | Réponse attendue |
|---|---|
| 1 | SELECT id FROM Eleve; |

### Détail de correction

La solution complète reste réservée au professeur.

## Aides élèves

Choisir la colonne affichée avant d'écrire la requête.
"""

        rendered = strip_teacher_sections(markdown)

        self.assertNotIn("Repères enseignant", rendered)
        self.assertNotIn("Réponse attendue", rendered)
        self.assertNotIn("SELECT id FROM Eleve", rendered)
        self.assertIn("Le professeur veut obtenir", rendered)
        self.assertIn("Aides élèves", rendered)

    def test_inline_teacher_resource_is_removed_without_hiding_public_bareme(self) -> None:
        markdown = """# TP

## Barème associé

- 2 points : donnée préparée.

## Assets Python

- Starter élève : `starter.py`.
- Corrigé professeur : `corrige_professeur.py`.
"""

        rendered = strip_teacher_sections(markdown)

        self.assertIn("Barème associé", rendered)
        self.assertIn("2 points", rendered)
        self.assertIn("Starter élève", rendered)
        self.assertNotIn("Corrigé professeur", rendered)
        self.assertNotIn("corrige_professeur.py", rendered)

    def test_student_gate_accepts_teacher_word_in_scenario(self) -> None:
        errors = student_leak_errors("<p>Le professeur veut obtenir un résultat trié.</p>")

        self.assertEqual(errors, [])

    def test_student_gate_rejects_visible_teacher_section(self) -> None:
        errors = student_leak_errors(
            "<h2>Repères enseignant</h2>\n"
            "<p>Réponse attendue : SELECT id FROM Eleve;</p>"
        )

        self.assertTrue(any("Repères enseignant" in error for error in errors))

    def test_student_gate_rejects_inline_teacher_resource(self) -> None:
        errors = student_leak_errors("<p>Corrigé professeur : corrige_professeur.py</p>")

        self.assertTrue(any("contenu de correction" in error for error in errors))

    def test_real_t10_student_render_has_no_teacher_sections_or_answers(self) -> None:
        student = build_html("T10", teacher=False)
        teacher = build_html("T10", teacher=True)

        self.assertIn("Le professeur veut les identifiants", student)
        self.assertNotIn("Repères enseignant", student)
        self.assertNotIn("six notes deviendraient 16", student)
        self.assertNotIn("contrôle avant : `(11, 13)`", student)
        self.assertIn("Repères enseignant", teacher)
        self.assertIn("six notes deviendraient 16", teacher)

    def test_reponses_rapides_section_is_stripped_from_student(self) -> None:
        markdown = """# Version aménagée

## Aides intégrées
- Mots utiles : HTML, CSS, DOM.

## Réponses rapides
- Réponse 1 : <label for=nom>Nom</label>.
- Réponse 2 : document.querySelector("#nom").value.

## Exercice guidé
1. Recopier la donnée utile.
"""

        rendered = strip_teacher_sections(markdown)

        self.assertNotIn("Réponses rapides", rendered)
        self.assertNotIn("Réponse 1", rendered)
        self.assertNotIn("querySelector", rendered)
        self.assertIn("Aides intégrées", rendered)
        self.assertIn("Exercice guidé", rendered)

    def test_numbered_answer_key_detected_in_student_gate(self) -> None:
        errors = student_leak_errors(
            "<p>Réponse 1 : SELECT id FROM Eleve;</p>"
        )

        self.assertTrue(any("réponse numérotée" in error for error in errors))

    def test_legitimate_student_reponse_is_not_flagged(self) -> None:
        errors = student_leak_errors(
            "<p>Écrire votre réponse dans le fichier starter.</p>"
        )

        self.assertEqual(errors, [])

    def test_student_gate_rejects_contextual_final_answer_without_banning_api_terms(self) -> None:
        errors = student_leak_errors(
            "<p>Résultat final : document.querySelector(\"#nom\").value lit la saisie.</p>"
        )

        self.assertTrue(any("résultat final" in error for error in errors))

    def test_student_gate_rejects_pre_filled_cryptography_deliverable(self) -> None:
        errors = student_leak_errors(
            "<p>Livrable prérempli : message chiffré avec Ksession.</p>"
        )

        self.assertTrue(any("livrable prérempli" in error.lower() for error in errors))

    def test_resultat_de_reference_section_is_stripped_from_student(self) -> None:
        markdown = """# Trace

## Étapes
- Étape 1 : repérer les données.

## Résultats attendus
- Résultat : SELECT id FROM Eleve;

## Exercice
1. Compléter.
"""
        rendered = strip_teacher_sections(markdown)
        self.assertNotIn("Résultats attendus", rendered)
        self.assertNotIn("SELECT id FROM Eleve", rendered)
        self.assertIn("Étapes", rendered)
        self.assertIn("Exercice", rendered)

    def test_real_p08_student_has_no_direct_answers(self) -> None:
        student = build_html("P08", teacher=False)
        teacher = build_html("P08", teacher=True)

        self.assertNotIn("Réponses rapides", student)
        self.assertNotIn("Réponse 1", student)
        self.assertNotIn("Résultats attendus", student)
        self.assertIn("Exercice guidé", student)
        self.assertIn("Aides intégrées", student)
        self.assertIn("________________", student)
        self.assertIn("Repères enseignant", teacher)

    def test_real_t13_student_has_no_direct_answers(self) -> None:
        student = build_html("T13", teacher=False)
        teacher = build_html("T13", teacher=True)

        self.assertNotIn("Réponses rapides", student)
        self.assertNotIn("Réponse 1", student)
        self.assertIn("Exercice guidé", student)
        self.assertIn("________________", student)
        self.assertIn("Repères enseignant", teacher)

    def test_p08_version_amenagee_remains_substantive(self) -> None:
        student = build_html("P08", teacher=False)
        self.assertIn("Exercice guidé", student)
        self.assertIn("Aides intégrées", student)
        self.assertIn("Cas limites", student)

    def test_real_p08_render_passes_student_teacher_gate(self) -> None:
        self.assertEqual(check_unit("P08"), [])

    def test_real_t13_render_passes_student_teacher_gate(self) -> None:
        self.assertEqual(check_unit("T13"), [])

    def test_real_t10_render_passes_student_teacher_gate(self) -> None:
        self.assertEqual(check_unit("T10"), [])


if __name__ == "__main__":
    unittest.main()
