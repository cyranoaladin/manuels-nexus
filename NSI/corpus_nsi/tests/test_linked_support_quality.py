from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import re
import hashlib

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_linked_evaluation_quality as evaluation_quality
import scripts.check_linked_td_quality as td_quality
import scripts.check_linked_td_substance as td_substance
import scripts._operational_links as operational_links
import scripts.check_operational_supports_no_indicative_debt as operational_debt


class LinkedSupportQualityTest(unittest.TestCase):
    def write_debt_register(self, root: Path, td: Path, *, sha256: str | None = None) -> None:
        relative = td.relative_to(root).as_posix()
        digest = sha256 if sha256 is not None else hashlib.sha256(td.read_bytes()).hexdigest()
        register = root / "reports" / "td_quality_debt_register.yml"
        register.parent.mkdir(parents=True, exist_ok=True)
        register.write_text(
            "schema: td_quality_debt_register_v1\n"
            "purpose: dette historique non certifiante\n"
            "entries:\n"
            f"  - path: {relative}\n"
            "    level: terminale\n"
            "    sequence: P99\n"
            "    debt_types:\n"
            "      - corrections_quasi_identiques\n"
            "    classification: mixte\n"
            f"    sha256: {digest}\n"
            "    note: dette historique à normaliser dans un lot dédié.\n",
            encoding="utf-8",
        )

    def write_contract(self, root: Path, sequence: str, *, requires_eight: bool = False) -> None:
        contract = root / "03_progressions" / "supports" / "contracts" / f"{sequence}_contract.yml"
        contract.parent.mkdir(parents=True, exist_ok=True)
        requirement = "exigences:\n  - au moins 8 exercices distincts\n" if requires_eight else ""
        contract.write_text(
            "sequence: " + sequence + "\n"
            "types_exercices_attendus:\n"
            "  - lecture\n"
            "  - trace\n"
            "  - écriture\n"
            "  - justification\n"
            "  - débogage\n"
            "  - transfert\n"
            + requirement,
            encoding="utf-8",
        )

    def write_td(self, root: Path, *, exercises: int, corrections: int, rich: bool) -> Path:
        td = root / "P99_TD_demo.md"
        task_titles = [
            "Lire et annoter [socle]",
            "Construire une table de trace [socle]",
            "Écrire une requête [standard]",
            "Justifier un résultat [standard]",
            "Déboguer une erreur [standard]",
            "Transfert vers un nouveau cas [approfondissement]",
            "Production supplémentaire [approfondissement]",
            "Analyse supplémentaire [approfondissement]",
        ]
        task_consignes = [
            "Lire le document fourni et annoter les structures repérées dans le texte source.",
            "Construire la table de trace complète en suivant l'exécution pas à pas sur les données.",
            "Écrire la requête SQL qui produit le résultat demandé à partir de la table donnée.",
            "Justifier pourquoi le résultat obtenu est correct en citant les propriétés utilisées.",
            "Trouver et corriger l'erreur dans le programme proposé puis vérifier le résultat.",
            "Adapter la solution précédente à un nouveau contexte avec des contraintes différentes.",
            "Produire un algorithme complet répondant à la consigne et vérifier son exécution.",
            "Analyser les résultats obtenus et comparer les performances des deux approches proposées.",
        ]
        lines = [
            "---",
            "title: P99 TD",
            "level: terminale",
            "sequence_id: P99",
            "document_type: td",
            "status: needs_review",
            "official_program:",
            "  capacities:",
            "    - T-ALGO-04",
            "---",
            "# TD",
            "## Exercices",
        ]
        for number in range(exercises):
            lines.extend([
                f"### Exercice {number + 1} — {task_titles[number]}",
                task_consignes[number],
            ])
        correction_texts = [
            "La structure repérée est header-main-form et le libellé est associé au champ par l'attribut for.",
            "La table de trace montre trois états successifs et la valeur finale est cohérente avec l'entrée.",
            "La requête SELECT ... WHERE ... produit exactement les lignes attendues sans doublon.",
            "Le résultat est correct parce que la propriété utilisée garantit l'unicité du résultat.",
            "L'erreur se situe à la ligne du test de condition et la correction rétablit le bon comportement.",
            "La solution précédente s'adapte en remplaçant la condition par le nouveau critère donné.",
            "L'algorithme produit le résultat attendu et la trace d'exécution le confirme pas à pas.",
            "Les deux approches donnent le même résultat mais diffèrent en complexité temporelle.",
        ]
        lines.append("## Corrigé")
        for number in range(corrections):
            lines.extend([f"### Corrigé exercice {number + 1}", correction_texts[number % len(correction_texts)]])
        if rich:
            lines.extend([
                "## Cas limite et erreurs fréquentes",
                "Cas limite : résultat vide.",
                "## Aides graduées",
                "Aide pour la différenciation.",
            ])
        td.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return td

    def write_evaluation_links(self, root: Path, *, questions: int = 4) -> tuple[str, str]:
        bareme = root / "P99_bareme_demo.md"
        corrige = root / "P99_corrige_demo.md"
        bareme.write_text(
            "# Barème\n\n"
            + "\n\n".join(
                f"## Barème question {number}\n\nCritère observable et points."
                for number in range(1, questions + 1)
            )
            + "\n",
            encoding="utf-8",
        )
        corrige.write_text(
            "# Corrigé\n\n"
            + "\n\n".join(
                f"## Question {number}\n\nMéthode justifiée et résultat vérifiable."
                for number in range(1, questions + 1)
            )
            + "\n",
            encoding="utf-8",
        )
        return bareme.name, corrige.name

    def write_evaluation(
        self,
        root: Path,
        *,
        heading_level: int = 2,
        material: str = "- Matériel : aucun.",
        bareme: str | None = None,
        corrige: str | None = None,
        rich: bool = True,
    ) -> Path:
        evaluation = root / "P99_evaluation_demo.md"
        links = []
        if bareme is not None:
            links.append(f'bareme: "{bareme}"')
        if corrige is not None:
            links.append(f'corrige: "{corrige}"')
        headings = "#" * heading_level
        lines = [
            "---",
            "title: P99 evaluation",
            "level: terminale",
            "sequence_id: P99",
            "document_type: evaluation",
            "status: needs_review",
            *links,
            "official_program:",
            "  capacities:",
            "    - T-ALGO-04",
            "---",
            "# Évaluation",
            "## Cadre",
            "- Durée : 40 minutes.",
            material,
            "- Capacités évaluées : T-ALGO-04.",
        ]
        prompts = [
            "Lire les données fournies et expliquer le résultat attendu.",
            "Calculer une trace puis compléter une table de résultats.",
            "Écrire un algorithme qui produit la valeur demandée.",
            "Corriger l'erreur proposée et justifier la correction.",
        ]
        for number, prompt in enumerate(prompts, start=1):
            lines.extend([f"{headings} Question {number} — tâche", prompt if rich else "Titre seul."])
        if rich:
            lines.extend([
                "## Critères et erreurs fréquentes",
                "Critère observable : une méthode et un résultat vérifiable.",
                "Erreur fréquente : confondre la donnée et le résultat.",
                "## Aménagement",
                "Une aide graduée est disponible sans donner la réponse.",
            ])
        evaluation.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return evaluation

    def write_tp(self, root: Path, *, substantial: bool) -> Path:
        tp = root / "P99_TP_demo.md"
        lines = [
            "---",
            "title: P99 TP",
            "level: terminale",
            "sequence_id: P99",
            "document_type: tp",
            "status: needs_review",
            "official_program:",
            "  capacities:",
            "    - T-ALGO-04",
            "---",
            "# TP P99",
            "## Objectif",
            "Construire, exécuter et vérifier un algorithme sur des données fournies.",
            "## Consignes",
            "Produire une solution testable, puis expliquer un résultat limite.",
            "## Tests et livrable",
            "Conserver les tests et rendre une trace d'exécution vérifiable.",
            "## Critères de réussite",
            "La solution doit être exécutable, justifiée et reproductible.",
        ]
        if substantial:
            lines.extend(
                f"Étape {number} : vérifier une donnée, exécuter le programme et consigner le résultat obtenu."
                for number in range(1, 81)
            )
        else:
            lines.append("Essayer une solution.")
        tp.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return tp

    def link_operational_support(self, root: Path, support: Path, element: str) -> None:
        sheet = root / "03_progressions" / "fiches_cours" / "terminale" / "P99" / "P99_fiche_cours_demo.md"
        sheet.parent.mkdir(parents=True, exist_ok=True)
        sheet.write_text(
            "---\n"
            "title: P99\n"
            "sequence_id: P99\n"
            "readiness: operational\n"
            "---\n"
            "# P99\n\n"
            "## Lien avec la progression\n"
            "| Élément | Fichier | Statut | Remarque |\n"
            "|---|---|---|---|\n"
            f"| {element} | {support.name} | existant | support réel |\n",
            encoding="utf-8",
        )

    def write_td_adversarial(
        self,
        root: Path,
        *,
        exercises: int,
        corrections: int,
        rich: bool,
        shallow_content: bool = False,
        duplicate_consignes: bool = False,
        shallow_corrections: bool = False,
        near_duplicate_consignes: bool = False,
        generic_varied_corrections: bool = False,
    ) -> Path:
        td = root / "P99_TD_demo.md"
        task_titles = [
            "Lire et annoter [socle]",
            "Construire une table de trace [socle]",
            "Écrire une requête [standard]",
            "Justifier un résultat [standard]",
            "Déboguer une erreur [standard]",
            "Transfert vers un nouveau cas [approfondissement]",
        ]
        lines = [
            "---",
            "title: P99 TD",
            "level: terminale",
            "sequence_id: P99",
            "document_type: td",
            "status: needs_review",
            "official_program:",
            "  capacities:",
            "    - T-ALGO-04",
            "---",
            "# TD",
            "## Exercices",
        ]
        for number in range(exercises):
            title = task_titles[0] if duplicate_consignes else task_titles[number % len(task_titles)]
            lines.append(f"### Exercice {number + 1} — {title}")
            if shallow_content:
                lines.append("Titre seul.")
            elif near_duplicate_consignes:
                case = chr(ord("A") + number)
                lines.append(
                    "Analyser la trace de la requête pour le cas "
                    f"{case} et justifier chaque étape avec les données fournies."
                )
            else:
                lines.append("Production attendue et contrôle du résultat obtenu par exécution directe du programme.")
        lines.append("## Corrigé")
        for number in range(corrections):
            lines.append(f"### Corrigé exercice {number + 1}")
            if shallow_corrections:
                lines.append("OK.")
            elif generic_varied_corrections:
                case = chr(ord("A") + number)
                lines.append(
                    "Réponse justifiée avec trace et vérification du résultat complet "
                    f"pour le cas {case}."
                )
            else:
                lines.append("Réponse justifiée avec trace et vérification du résultat complet.")
        if rich:
            lines.extend([
                "## Cas limite et erreurs fréquentes",
                "Cas limite : résultat vide.",
                "## Aides graduées",
                "Aide pour la différenciation.",
            ])
        td.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return td

    def test_contract_compliant_six_task_td_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.write_contract(root, "P99")
            td = self.write_td(root, exercises=6, corrections=6, rich=True)

            result = td_quality.analyze_linked_td_quality(root, [td])

            self.assertEqual(result.errors, [])

    def test_poor_six_task_td_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.write_contract(root, "P99")
            td = self.write_td(root, exercises=6, corrections=6, rich=False)

            result = td_quality.analyze_linked_td_quality(root, [td])

            self.assertTrue(any("6 tâches" in error or "8 exercices" in error for error in result.errors))

    def test_six_task_td_without_all_corrections_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.write_contract(root, "P99")
            td = self.write_td(root, exercises=6, corrections=5, rich=True)

            result = td_quality.analyze_linked_td_quality(root, [td])

            self.assertTrue(any("corrigé manquant" in error for error in result.errors))

    def test_six_task_td_is_rejected_when_contract_requires_eight_exercises(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.write_contract(root, "P99", requires_eight=True)
            td = self.write_td(root, exercises=6, corrections=6, rich=True)

            result = td_quality.analyze_linked_td_quality(root, [td])

            self.assertTrue(any("contrat exige 8 exercices" in error for error in result.errors))

    def test_eight_task_td_remains_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = self.write_td(root, exercises=8, corrections=8, rich=True)

            result = td_quality.analyze_linked_td_quality(root, [td])

            self.assertEqual(result.errors, [])

    def test_six_task_td_with_decorative_keywords_but_shallow_content_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.write_contract(root, "P99")
            td = self.write_td_adversarial(root, exercises=6, corrections=6, rich=True, shallow_content=True)

            result = td_quality.analyze_linked_td_quality(root, [td])

            self.assertTrue(any("6 tâches" in error for error in result.errors))

    def test_six_task_td_with_duplicate_consignes_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.write_contract(root, "P99")
            td = self.write_td_adversarial(root, exercises=6, corrections=6, rich=True, duplicate_consignes=True)

            result = td_quality.analyze_linked_td_quality(root, [td])

            self.assertTrue(len(result.errors) > 0)

    def test_six_task_td_with_shallow_corrections_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.write_contract(root, "P99")
            td = self.write_td_adversarial(root, exercises=6, corrections=6, rich=True, shallow_corrections=True)

            result = td_quality.analyze_linked_td_quality(root, [td])

            self.assertTrue(any("6 tâches" in error for error in result.errors))

    def test_six_task_td_without_contract_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = self.write_td(root, exercises=6, corrections=6, rich=True)

            result = td_quality.analyze_linked_td_quality(root, [td])

            self.assertTrue(len(result.errors) > 0)

    def test_eight_task_td_with_shallow_content_still_fails_quality_checks(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = self.write_td_adversarial(root, exercises=8, corrections=8, rich=False, shallow_content=True)

            result = td_quality.analyze_linked_td_quality(root, [td])

            self.assertTrue(any("trop pauvre" in error for error in result.errors))

    def test_eight_task_td_with_near_duplicate_consignes_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = self.write_td_adversarial(root, exercises=8, corrections=8, rich=True, duplicate_consignes=True)

            result = td_quality.analyze_linked_td_quality(root, [td])

            self.assertTrue(any("quasi identiques" in error for error in result.errors))

    def test_eight_task_td_with_generic_repeated_corrections_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = self.write_td_adversarial(root, exercises=8, corrections=8, rich=True, shallow_corrections=True)

            result = td_quality.analyze_linked_td_quality(root, [td])

            self.assertTrue(any("corrigé" in error and "pauvre" in error for error in result.errors))

    def test_registered_historical_td_with_exact_hash_is_reported_as_debt(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = self.write_td_adversarial(
                root, exercises=8, corrections=8, rich=True, generic_varied_corrections=True
            )
            self.write_debt_register(root, td)

            result = td_quality.analyze_linked_td_quality(root, [td])

            self.assertEqual(result.errors, [])
            self.assertEqual(result.registered_debt, [td.relative_to(root).as_posix()])

    def test_registered_historical_td_with_changed_hash_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = self.write_td_adversarial(
                root, exercises=8, corrections=8, rich=True, generic_varied_corrections=True
            )
            self.write_debt_register(root, td)
            td.write_text(td.read_text(encoding="utf-8") + "\nModification non normalisée.\n", encoding="utf-8")

            result = td_quality.analyze_linked_td_quality(root, [td])

            self.assertTrue(any("empreinte différente" in error for error in result.errors))
            self.assertEqual(result.registered_debt, [])

    def test_missing_registered_td_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            register = root / "reports" / "td_quality_debt_register.yml"
            register.parent.mkdir(parents=True, exist_ok=True)
            register.write_text(
                "schema: td_quality_debt_register_v1\nentries:\n"
                "  - path: missing/P99_TD_demo.md\n"
                "    sha256: deadbeef\n",
                encoding="utf-8",
            )

            result = td_quality.analyze_linked_td_quality(root, [])

            self.assertTrue(any("absente du disque" in error for error in result.errors))

    def test_current_t10_t17_td_are_accepted_without_registered_debt(self) -> None:
        files = [
            ROOT / "03_progressions/supports/terminale/T10/T10_TD_sql_select_where_join.md",
            ROOT / "03_progressions/supports/terminale/T17/T17_TD_programmation_dynamique.md",
        ]

        result = td_quality.analyze_linked_td_quality(ROOT, files)

        self.assertEqual(result.errors, [])
        self.assertEqual(result.registered_debt, [])

    def test_normalized_p12_td_has_no_intrinsic_quality_alert(self) -> None:
        td = ROOT / "03_progressions/supports/premiere/P12/P12_TD_tris_invariants_complexite.md"

        errors = td_quality.analyze_one_td(td, ROOT)

        self.assertEqual(errors, [])

    def test_normalized_p12_td_has_substantive_corrections(self) -> None:
        td = ROOT / "03_progressions/supports/premiere/P12/P12_TD_tris_invariants_complexite.md"

        errors = td_substance.analyze_one_td(td, ROOT)

        self.assertEqual(errors, [])

    def test_eight_task_td_with_long_near_duplicate_consignes_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = self.write_td_adversarial(
                root,
                exercises=8,
                corrections=8,
                rich=True,
                near_duplicate_consignes=True,
            )

            result = td_quality.analyze_linked_td_quality(root, [td])

            self.assertTrue(any("quasi identiques" in error for error in result.errors))

    def test_eight_task_td_with_generic_corrections_varied_by_case_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = self.write_td_adversarial(
                root,
                exercises=8,
                corrections=8,
                rich=True,
                generic_varied_corrections=True,
            )

            result = td_quality.analyze_linked_td_quality(root, [td])

            self.assertTrue(any("corrigés quasi identiques" in error for error in result.errors))

    def test_compact_td_with_generic_corrections_varied_by_case_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.write_contract(root, "P99")
            td = self.write_td_adversarial(
                root,
                exercises=6,
                corrections=6,
                rich=True,
                generic_varied_corrections=True,
            )

            result = td_quality.analyze_linked_td_quality(root, [td])

            self.assertTrue(any("corrigés quasi identiques" in error for error in result.errors))

    def test_operational_debt_accepts_short_rich_td_with_singular_objective_and_aids(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = self.write_td(root, exercises=6, corrections=6, rich=True)
            text = td.read_text(encoding="utf-8").replace(
                "## Exercices", "## Objectif de séance\n\nConstruire une requête vérifiable.\n\n## Exercices"
            )
            td.write_text(text, encoding="utf-8")
            self.link_operational_support(root, td, "TD")

            result = operational_debt.analyze_operational_supports_no_indicative_debt(root)

            self.assertEqual(result.errors, [])

    def test_operational_debt_rejects_decorative_differentiation_without_content(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = self.write_td(root, exercises=6, corrections=6, rich=False)
            text = td.read_text(encoding="utf-8").replace(
                "## Exercices", "## Objectif\n\nObjectif : produire des réponses vérifiables.\n\n## Exercices"
            )
            text = re.sub(r" \[(socle|standard|approfondissement)(?:, \d+ min)?\]", "", text)
            text += "\n## Différenciation\n"
            td.write_text(text, encoding="utf-8")
            self.link_operational_support(root, td, "TD")

            result = operational_debt.analyze_operational_supports_no_indicative_debt(root)

            self.assertTrue(any("différenciation" in error.lower() for error in result.errors))

    def test_operational_debt_accepts_short_dense_evaluation_with_linked_resources(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            bareme, corrige = self.write_evaluation_links(root)
            evaluation = self.write_evaluation(root, bareme=bareme, corrige=corrige)
            self.link_operational_support(root, evaluation, "Évaluation")

            result = operational_debt.analyze_operational_supports_no_indicative_debt(root)

            self.assertEqual(result.errors, [])

    def test_operational_debt_rejects_tp_below_depth_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            tp = self.write_tp(root, substantial=False)

            result = operational_debt.analyze_operational_supports_no_indicative_debt(root, [tp])

            self.assertTrue(any("profondeur TP insuffisante" in error for error in result.errors))

    def test_operational_debt_accepts_substantive_tp_above_depth_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            tp = self.write_tp(root, substantial=True)

            result = operational_debt.analyze_operational_supports_no_indicative_debt(root, [tp])

            self.assertEqual(result.errors, [])

    def test_operational_debt_rejects_long_but_hollow_evaluation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            bareme, corrige = self.write_evaluation_links(root)
            evaluation = self.write_evaluation(root, bareme=bareme, corrige=corrige, rich=False)
            evaluation.write_text(evaluation.read_text(encoding="utf-8") + ("Texte décoratif.\n" * 80), encoding="utf-8")
            self.link_operational_support(root, evaluation, "Évaluation")

            result = operational_debt.analyze_operational_supports_no_indicative_debt(root)

            self.assertTrue(any("consigne" in error.lower() or "critère" in error.lower() for error in result.errors))

    def test_operational_debt_rejects_empty_declared_link(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            bareme, corrige = self.write_evaluation_links(root)
            (root / corrige).write_text("", encoding="utf-8")
            evaluation = self.write_evaluation(root, bareme=bareme, corrige=corrige)
            self.link_operational_support(root, evaluation, "Évaluation")

            result = operational_debt.analyze_operational_supports_no_indicative_debt(root)

            self.assertTrue(any("corrigé lié trop pauvre" in error.lower() for error in result.errors))

    def test_current_t10_t17_operational_supports_are_accepted(self) -> None:
        result = operational_debt.analyze_operational_supports_no_indicative_debt(ROOT)

        self.assertEqual(result.errors, [])

    def test_reference_resolution_rejects_ambiguous_basename(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            first = root / "a" / "P01_TD_conversions.md"
            second = root / "b" / "P01_TD_conversions.md"
            first.parent.mkdir(parents=True)
            second.parent.mkdir(parents=True)
            first.write_text("a", encoding="utf-8")
            second.write_text("b", encoding="utf-8")

            resolution = operational_links.resolve_reference(root, "P01_TD_conversions.md")

            self.assertTrue(resolution.ambiguous)
            self.assertEqual(set(resolution.candidates), {first, second})

    def test_reference_resolution_accepts_full_non_ambiguous_path(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / "a" / "P01_TD_conversions.md"
            target.parent.mkdir(parents=True)
            target.write_text("a", encoding="utf-8")
            (root / "b").mkdir()

            resolution = operational_links.resolve_reference(root, "a/P01_TD_conversions.md")

            self.assertEqual(resolution.path, target)
            self.assertFalse(resolution.ambiguous)

    def test_reference_resolution_accepts_unique_basename(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / "a" / "P01_TD_conversions.md"
            target.parent.mkdir(parents=True)
            target.write_text("a", encoding="utf-8")

            resolution = operational_links.resolve_reference(root, "P01_TD_conversions.md")

            self.assertEqual(resolution.path, target)
            self.assertFalse(resolution.ambiguous)

    def test_reference_resolution_reports_absent_reference(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)

            resolution = operational_links.resolve_reference(root, "P01_TD_conversions.md")

            self.assertTrue(resolution.absent)

    def test_td_requires_eight_exercises_and_required_exercise_types(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = root / "P10_TD_reseaux_protocoles_paquets.md"
            td.write_text(
                """---
title: P10 TD
sequence_id: P10
document_type: td
status: needs_review
official_program:
  capacities:
    - P-ARCH-02A
---
# TD

## Exercices
### Exercice 1
Lecture d'un paquet.

## Corrigé
### Corrigé exercice 1
Réponse.
""",
                encoding="utf-8",
            )

            result = td_quality.analyze_linked_td_quality(root, [td])

            self.assertTrue(any("8 exercices" in error for error in result.errors))
            self.assertTrue(any("lecture/analyse" in error for error in result.errors))

    def test_td_check_rejects_missing_target_td_link(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            sheet = root / "03_progressions" / "fiches_cours" / "premiere" / "P10" / "P10_fiche_cours_reseaux_protocoles_paquets.md"
            sheet.parent.mkdir(parents=True)
            sheet.write_text(
                """---
title: P10
sequence_id: P10
readiness: operational
---
# P10

## Lien avec la progression
| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | P10-S1 | prête | séance réelle |
| TD | P10_TD_reseaux_protocoles_paquets.md | existant | support réel |
""",
                encoding="utf-8",
            )

            result = td_quality.analyze_linked_td_quality(root)

            self.assertTrue(any("support TD absent" in error for error in result.errors))

    def test_td_check_discovers_every_operational_sheet_not_only_recent_prefixes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            sheet = root / "03_progressions" / "fiches_cours" / "premiere" / "P01" / "P01_fiche_cours_conversions.md"
            sheet.parent.mkdir(parents=True)
            sheet.write_text(
                """---
title: P01
sequence_id: P01
readiness: operational
---
# P01

## Lien avec la progression
| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | P01-S1 | prête | séance réelle |
| TD | P01_TD_conversions.md | existant | support réel |
""",
                encoding="utf-8",
            )

            result = td_quality.analyze_linked_td_quality(root)

            self.assertTrue(any("P01_TD_conversions.md: support TD absent" in error for error in result.errors))

    def test_evaluation_requires_bareme_and_accommodations(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            evaluation = root / "T10_evaluation_sql_select_where_join.md"
            evaluation.write_text(
                """---
title: T10 evaluation
sequence_id: T10
document_type: evaluation
status: needs_review
official_program:
  capacities:
    - T-BDD-03A
---
# Evaluation

## Questions
### Question 1
SELECT simple.
""",
                encoding="utf-8",
            )

            result = evaluation_quality.analyze_linked_evaluation_quality(root, [evaluation])

            self.assertTrue(any("exigence évaluation manquante -> corrigé" in error.lower() for error in result.errors))
            self.assertTrue(any("aménagement" in error.lower() for error in result.errors))

    def test_evaluation_accepts_level_two_questions_and_linked_resources(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            bareme, corrige = self.write_evaluation_links(root)
            evaluation = self.write_evaluation(root, bareme=bareme, corrige=corrige)

            result = evaluation_quality.analyze_linked_evaluation_quality(root, [evaluation])

            self.assertEqual(result.errors, [])

    def test_evaluation_keeps_accepting_level_three_questions(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            bareme, corrige = self.write_evaluation_links(root)
            evaluation = self.write_evaluation(root, heading_level=3, bareme=bareme, corrige=corrige)

            result = evaluation_quality.analyze_linked_evaluation_quality(root, [evaluation])

            self.assertEqual(result.errors, [])

    def test_evaluation_rejects_missing_material_policy(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            bareme, corrige = self.write_evaluation_links(root)
            evaluation = self.write_evaluation(root, material="", bareme=bareme, corrige=corrige)

            result = evaluation_quality.analyze_linked_evaluation_quality(root, [evaluation])

            self.assertTrue(any("matériel" in error.lower() for error in result.errors))

    def test_evaluation_rejects_missing_linked_bareme_or_corrige(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            evaluation = self.write_evaluation(
                root,
                bareme="P99_bareme_absent.md",
                corrige="P99_corrige_absent.md",
            )

            result = evaluation_quality.analyze_linked_evaluation_quality(root, [evaluation])

            self.assertTrue(any("barème lié absent" in error.lower() for error in result.errors))
            self.assertTrue(any("corrigé lié absent" in error.lower() for error in result.errors))

    def test_evaluation_rejects_four_empty_question_titles(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            bareme, corrige = self.write_evaluation_links(root)
            evaluation = self.write_evaluation(root, bareme=bareme, corrige=corrige, rich=False)

            result = evaluation_quality.analyze_linked_evaluation_quality(root, [evaluation])

            self.assertTrue(any("consigne" in error.lower() for error in result.errors))

    def test_current_t10_t17_p08_evaluations_are_accepted(self) -> None:
        evaluations = [
            ROOT / "03_progressions/supports/premiere/P08/P08_evaluation_html_css_dom.md",
            ROOT / "03_progressions/supports/premiere/P08/P08_evaluation_http_get_post_formulaires.md",
            ROOT / "03_progressions/supports/terminale/T10/T10_evaluation_sql_select_where_join.md",
            ROOT / "03_progressions/supports/terminale/T10/T10_evaluation_sql_insert_update_delete.md",
            ROOT / "03_progressions/supports/terminale/T17/T17_evaluation_programmation_dynamique.md",
        ]

        result = evaluation_quality.analyze_linked_evaluation_quality(ROOT, evaluations)

        self.assertEqual(result.errors, [])

    def test_evaluation_check_rejects_missing_target_evaluation_link(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            sheet = root / "03_progressions" / "fiches_cours" / "terminale" / "T10" / "T10_fiche_cours_sql_select_where_join.md"
            sheet.parent.mkdir(parents=True)
            sheet.write_text(
                """---
title: T10
sequence_id: T10
readiness: operational
---
# T10

## Lien avec la progression
| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | T10-S1 | prête | séance réelle |
| Évaluation | T10_evaluation_sql_select_where_join.md | existant | support réel |
""",
                encoding="utf-8",
            )

            result = evaluation_quality.analyze_linked_evaluation_quality(root)

            self.assertTrue(any("support évaluation absent" in error for error in result.errors))

    def test_evaluation_check_discovers_every_operational_sheet_not_only_recent_prefixes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            sheet = root / "03_progressions" / "fiches_cours" / "premiere" / "P01" / "P01_fiche_cours_conversions.md"
            sheet.parent.mkdir(parents=True)
            sheet.write_text(
                """---
title: P01
sequence_id: P01
readiness: operational
---
# P01

## Lien avec la progression
| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | P01-S1 | prête | séance réelle |
| Évaluation | P01_evaluation_conversions.md | existant | support réel |
""",
                encoding="utf-8",
            )

            result = evaluation_quality.analyze_linked_evaluation_quality(root)

            self.assertTrue(any("P01_evaluation_conversions.md: support évaluation absent" in error for error in result.errors))

    def test_operational_support_debt_rejects_too_short_linked_resource(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "03_progressions" / "seances_premiere.md").parent.mkdir(parents=True)
            (root / "03_progressions" / "seances_premiere.md").write_text("### Séance P10-S1\n", encoding="utf-8")
            support = root / "03_progressions" / "supports" / "premiere" / "P10" / "P10_TD_reseaux_protocoles_paquets.md"
            support.parent.mkdir(parents=True)
            support.write_text(
                """---
title: P10 TD
sequence_id: P10
document_type: td
status: needs_review
---
# P10 TD
## Exercices
### Exercice 1
Un paquet.
## Corrigé
### Corrigé exercice 1
Réponse.
""",
                encoding="utf-8",
            )
            sheet = root / "03_progressions" / "fiches_cours" / "premiere" / "P10" / "P10_fiche_cours_reseaux_protocoles_paquets.md"
            sheet.parent.mkdir(parents=True)
            sheet.write_text(
                """---
title: P10
sequence_id: P10
readiness: operational
---
# P10

## Lien avec la progression
| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | P10-S1 | prête | séance réelle |
| TD | P10_TD_reseaux_protocoles_paquets.md | existant | support réel |
""",
                encoding="utf-8",
            )

            result = operational_debt.analyze_operational_supports_no_indicative_debt(root)

            self.assertTrue(any("tâches numérotées" in error for error in result.errors))

    def test_operational_support_debt_checks_all_operational_prefixes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "03_progressions").mkdir()
            (root / "03_progressions" / "seances_premiere.md").write_text("### Séance P01-S1\n", encoding="utf-8")
            support = root / "03_progressions" / "supports" / "premiere" / "P01" / "P01_TD_conversions.md"
            support.parent.mkdir(parents=True)
            support.write_text(
                """---
title: P01 TD
sequence_id: P01
document_type: td
status: needs_review
---
# P01 TD
## Exercices
### Exercice 1
Convertir 5.
## Corrigé
### Corrigé exercice 1
5 vaut 101 en binaire.
""",
                encoding="utf-8",
            )
            sheet = root / "03_progressions" / "fiches_cours" / "premiere" / "P01" / "P01_fiche_cours_conversions.md"
            sheet.parent.mkdir(parents=True)
            sheet.write_text(
                """---
title: P01
sequence_id: P01
readiness: operational
---
# P01

## Lien avec la progression
| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | P01-S1 | prête | séance réelle |
| TD | P01_TD_conversions.md | existant | support réel |
""",
                encoding="utf-8",
            )

            result = operational_debt.analyze_operational_supports_no_indicative_debt(root)

            self.assertTrue(any("tâches numérotées" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
