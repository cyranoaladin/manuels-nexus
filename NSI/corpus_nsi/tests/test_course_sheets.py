from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_course_sheets_alignment as alignment
import scripts.check_course_sheets_coverage as coverage
import scripts.check_course_sheets_quality as quality
import scripts.check_course_sheet_linked_resources_exist as linked_resources
import scripts.check_course_sheet_readiness as readiness
import scripts.check_course_sheet_readiness_strict as readiness_strict
import scripts.check_course_sheets_no_template_abuse as no_template
import scripts.check_course_sheets_substance as substance


VALID_SHEET = """---
title: "P01 - Fiche cours conversions"
level: "premiere"
sequence_id: "P01"
document_type: "fiche_cours"
status: "needs_review"
version: "0.1.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Représentation des entiers"
notion: "conversions"
official_program:
  capacities:
    - "P-DATA-BASE-01"
private_data: false
readiness: linked
---

# P01 - Fiche cours conversions

## À savoir
Une base donne la valeur d'un chiffre par sa position.

## Méthodes
1. Diviser par la base pour travailler P-DATA-BASE-01.
2. Lire les restes dans le bon ordre.

## Exemples corrigés
### Exemple corrigé 1
Pour P-DATA-BASE-01, 13 vaut 1101 en base deux.
### Exemple corrigé 2
101101₂ vaut 45 en base dix.

## Erreurs fréquentes
- Lire les restes dans l'ordre de calcul ; correction : inverser la lecture.
- Oublier les poids ; correction : annoter chaque puissance.
- Accepter un chiffre interdit ; correction : vérifier l'alphabet.

## Cas limites
0 se code 0 et un chiffre 2 est interdit en base deux.

## Mini-exercices
### Exercice 1
Convertir 7 en binaire pour exercer P-DATA-BASE-01.
### Exercice 2
Convertir 1010₂ en décimal.
### Exercice 3
Dire pourquoi 102₂ est invalide.

## Réponses rapides
1. 111₂.
2. 10.
3. Le symbole 2 est interdit.

## À retenir
- Une base fixe les symboles autorisés.
- La position donne le poids.
- Les conversions se contrôlent.
- Le cas 0 est particulier.
- Une réponse doit citer la méthode.

## Lien avec la progression
| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | P01-S1 | prête | séance réelle |
| TD | P01_TD_conversions_exercices_1_3.md | à créer | inscrit au registre v2 |

## Auto-évaluation
- Je sais convertir un entier positif.
- Je sais vérifier une écriture binaire.
- Je sais expliquer ma méthode.
"""


class CourseSheetsTest(unittest.TestCase):
    def test_missing_sequence_sheet_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "03_progressions").mkdir()
            (root / "03_progressions" / "progression_premiere.md").write_text(
                "| P00 | Septembre | 4 h | 1 h | P-HIST-01 | Diagnostic |\n"
                "| P01 | Septembre | 8 h | 1 h | P-DATA-BASE-01 | Quiz |\n",
                encoding="utf-8",
            )
            (root / "03_progressions" / "progression_terminale.md").write_text("", encoding="utf-8")

            result = coverage.analyze_course_sheet_coverage(root, program_ids={"P-HIST-01", "P-DATA-BASE-01"})

            self.assertTrue(any("P01: aucune fiche" in error for error in result.errors))

    def test_low_quality_sheet_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            sheet = root / "03_progressions" / "fiches_cours" / "premiere" / "P01" / "P01_fiche_cours_bases.md"
            sheet.parent.mkdir(parents=True)
            sheet.write_text("---\ndocument_type: fiche_cours\nstatus: needs_review\n---\n# Fiche\n", encoding="utf-8")

            result = quality.analyze_course_sheets_quality(root, program_ids={"P-DATA-BASE-01"})

            self.assertTrue(any("frontmatter incomplet" in error for error in result.errors))
            self.assertTrue(any("section manquante" in error for error in result.errors))

    def test_unknown_capacity_is_rejected_by_alignment(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            sheet = root / "03_progressions" / "fiches_cours" / "premiere" / "P01" / "P01_fiche_cours_bases.md"
            sheet.parent.mkdir(parents=True)
            sheet.write_text(VALID_SHEET.replace("P-DATA-BASE-01", "P-UNKNOWN-99"), encoding="utf-8")

            result = alignment.analyze_course_sheets_alignment(root, program_ids={"P-DATA-BASE-01"})

            self.assertTrue(any("capacité absente du YAML" in error for error in result.errors))

    def test_cross_sheet_repetition_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repeated = "- Ce paragraphe long répété dans trop de fiches signale un gabarit artificiel sans ajout disciplinaire."
            files: list[Path] = []
            for index in range(6):
                sheet = root / f"P{index:02d}_fiche_cours_test.md"
                sheet.write_text(f"---\nstatus: needs_review\n---\n# Fiche\n{repeated}\n", encoding="utf-8")
                files.append(sheet)

            errors = quality.cross_sheet_repetition_errors(files)

            self.assertTrue(any("répétition transversale excessive" in error for error in errors))

    def test_substance_rejects_generic_examples_and_answers(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            sheet = root / "03_progressions" / "fiches_cours" / "premiere" / "P01" / "P01_fiche_cours_bases.md"
            sheet.parent.mkdir(parents=True)
            sheet.write_text(
                VALID_SHEET
                .replace("101101₂ vaut 45 en base dix.", "On reprend le premier exemple avec une donnée différente.")
                .replace("2. 10.", "2. La réponse doit montrer les étapes utiles."),
                encoding="utf-8",
            )

            result = substance.analyze_course_sheets_substance(root)

            self.assertTrue(any("exemple générique" in error for error in result.errors))
            self.assertTrue(any("réponse rapide vague" in error for error in result.errors))

    def test_template_abuse_rejects_repeated_auto_evaluation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repeated_auto = "- Je sais relier cette fiche à une séance, un TD ou un TP du chapitre."
            for index in range(6):
                sheet = root / "03_progressions" / "fiches_cours" / "premiere" / f"P{index:02d}" / f"P{index:02d}_fiche_cours_test.md"
                sheet.parent.mkdir(parents=True)
                sheet.write_text(VALID_SHEET.replace("P01", f"P{index:02d}") + repeated_auto + "\n", encoding="utf-8")

            result = no_template.analyze_course_sheets_no_template_abuse(root)

            self.assertTrue(any("auto-évaluation trop similaire" in error for error in result.errors))

    def test_missing_linked_resource_must_be_registered(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            sheet = root / "03_progressions" / "fiches_cours" / "premiere" / "P01" / "P01_fiche_cours_bases.md"
            sheet.parent.mkdir(parents=True)
            sheet.write_text(VALID_SHEET.replace("P01_TD_conversions_exercices_1_3.md", "P01_TD_absent.md"), encoding="utf-8")

            result = linked_resources.analyze_course_sheet_links(root)

            self.assertTrue(any("absent non inscrit au registre" in error for error in result.errors))

    def test_readiness_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "03_progressions").mkdir()
            (root / "03_progressions" / "seances_premiere.md").write_text("### Séance P01-S1\n", encoding="utf-8")
            register = root / "missing_documents_register_v2.md"
            register.write_text(
                "| Fichier | Niveau | Séquence | Type | Priorité | Statut | Responsable | Date cible | Source possible | Décision | Blocage si absent |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| P01_TD_conversions_exercices_1_3.md | premiere | P01 | td | haute | absent | equipe | 2026-10-01 | BO | créer | oui |\n",
                encoding="utf-8",
            )
            sheet = root / "03_progressions" / "fiches_cours" / "premiere" / "P01" / "P01_fiche_cours_bases.md"
            sheet.parent.mkdir(parents=True)
            sheet.write_text(VALID_SHEET.replace("readiness: linked", "readiness: operational"), encoding="utf-8")

            result = readiness.analyze_course_sheet_readiness(root)

            self.assertTrue(any("readiness déclarée operational mais calculée linked" in error for error in result.errors))

    def test_strict_readiness_lists_linked_missing_supports(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "03_progressions").mkdir()
            (root / "03_progressions" / "seances_premiere.md").write_text("### Séance P01-S1\n", encoding="utf-8")
            (root / "missing_documents_register_v2.md").write_text(
                "| Fichier | Niveau | Séquence | Séance(s) | Type | Priorité | Statut | Responsable | Date cible | Source possible | Lien Drive éventuel | Dépendance | Décision | Blocage si absent | Fiche(s) concernée(s) | Impact pédagogique |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| P01_TD_conversions_exercices_1_3.md | premiere | P01 | P01-S1 | td | haute | absent | equipe | 2026-10-01 | BO | NA | aucune | créer | oui | P01_fiche_cours_bases.md | TD absent donc fiche non opérationnelle |\n",
                encoding="utf-8",
            )
            sheet = root / "03_progressions" / "fiches_cours" / "premiere" / "P01" / "P01_fiche_cours_bases.md"
            sheet.parent.mkdir(parents=True)
            sheet.write_text(VALID_SHEET, encoding="utf-8")

            result = readiness_strict.analyze_course_sheet_readiness_strict(root)

            self.assertEqual(result.counts["linked"], 1)
            missing = "\n".join(item for values in result.linked_missing.values() for item in values)
            self.assertIn("P01_TD_conversions_exercices_1_3.md", missing)

    def test_strict_readiness_rejects_operational_with_absent_td(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "03_progressions").mkdir()
            (root / "03_progressions" / "seances_premiere.md").write_text("### Séance P01-S1\n", encoding="utf-8")
            (root / "missing_documents_register_v2.md").write_text(
                "| Fichier | Niveau | Séquence | Séance(s) | Type | Priorité | Statut | Responsable | Date cible | Source possible | Lien Drive éventuel | Dépendance | Décision | Blocage si absent | Fiche(s) concernée(s) | Impact pédagogique |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| P01_TD_conversions_exercices_1_3.md | premiere | P01 | P01-S1 | td | haute | absent | equipe | 2026-10-01 | BO | NA | aucune | créer | oui | P01_fiche_cours_bases.md | TD absent donc fiche non opérationnelle |\n",
                encoding="utf-8",
            )
            sheet = root / "03_progressions" / "fiches_cours" / "premiere" / "P01" / "P01_fiche_cours_bases.md"
            sheet.parent.mkdir(parents=True)
            sheet.write_text(VALID_SHEET.replace("readiness: linked", "readiness: operational"), encoding="utf-8")

            result = readiness_strict.analyze_course_sheet_readiness_strict(root)

            self.assertTrue(any("operational" in error and "support absent" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
