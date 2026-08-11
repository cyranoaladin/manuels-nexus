from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_drive_integration_plan as drive_plan
import scripts.check_linked_evaluation_substance as evaluation_substance
import scripts.check_linked_td_substance as td_substance
import scripts.check_no_operational_scope_hardcoding as scope_hardcoding
import scripts.check_operational_readiness_quality_coupling as readiness_coupling
import scripts.check_register_no_hidden_operational_debt as hidden_debt


def operational_sheet(root: Path, sequence: str, td: str = "", evaluation: str = "") -> Path:
    level = "premiere" if sequence.startswith("P") else "terminale"
    sheet = root / "03_progressions" / "fiches_cours" / level / sequence / f"{sequence}_fiche_cours_demo.md"
    sheet.parent.mkdir(parents=True)
    links = [
        f"| Séance | {sequence}-S1 | prête | séance réelle |",
    ]
    if td:
        links.append(f"| TD | {td} | existant | support réel |")
    if evaluation:
        links.append(f"| Évaluation | {evaluation} | existant | support réel |")
    sheet.write_text(
        f"""---
title: {sequence}
sequence_id: {sequence}
readiness: operational
---
# {sequence}

## Lien avec la progression
| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
{chr(10).join(links)}
""",
        encoding="utf-8",
    )
    progression = root / "03_progressions" / ("seances_premiere.md" if sequence.startswith("P") else "seances_terminale.md")
    progression.parent.mkdir(parents=True, exist_ok=True)
    progression.write_text(f"### Séance {sequence}-S1\n", encoding="utf-8")
    return sheet


class OperationalSubstanceControlsTest(unittest.TestCase):
    def test_td_substance_rejects_trivial_numeric_correction(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = root / "P11_TD_parcours_recherche_extremum_moyenne.md"
            td.write_text(
                """---
title: P11 TD
level: premiere
sequence_id: P11
document_type: td
status: needs_review
official_program:
  capacities:
    - P-ALGO-01A
---
# TD

## Exercices
### Exercice 1
- Données : liste [1, 2, 3].
- Consigne : calculer la moyenne et justifier.

## Corrigé
### Corrigé exercice 1
Le résultat est 1.
""",
                encoding="utf-8",
            )

            result = td_substance.analyze_linked_td_substance(root, [td])

            self.assertTrue(any("sans preuve disciplinaire" in error.lower() for error in result.errors))

    def test_td_substance_rejects_only_a_number(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = root / "P11_TD_parcours_recherche_extremum_moyenne.md"
            td.write_text(
                """# TD
### Exercice 1
- Données : liste [1, 2, 3].
### Corrigé exercice 1
1
""",
                encoding="utf-8",
            )

            result = td_substance.analyze_linked_td_substance(root, [td])

            self.assertTrue(any("sans preuve disciplinaire" in error.lower() for error in result.errors))

    def test_td_substance_rejects_vague_correction_not_in_generic_phrase_list(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = root / "P12_TD_tris_invariants_complexite.md"
            td.write_text(
                """# TD
### Exercice 1
- Données : tableau [3, 1, 2].
- Consigne : décrire le tri attendu.
### Corrigé exercice 1
La réponse est acceptable si elle explique correctement la situation.
""",
                encoding="utf-8",
            )

            result = td_substance.analyze_linked_td_substance(root, [td])

            self.assertTrue(any("sans preuve disciplinaire" in error.lower() for error in result.errors))

    def test_td_substance_rejects_decorative_table_without_interpreted_result(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = root / "T10_TD_sql_select_where_join.md"
            td.write_text(
                """# TD
### Exercice 1
- Données : table Eleve.
- Consigne : prévoir la requête et le résultat.
### Corrigé exercice 1
| colonne | valeur |
|---|---|
| a | b |
""",
                encoding="utf-8",
            )

            result = td_substance.analyze_linked_td_substance(root, [td])

            self.assertTrue(any("sans preuve disciplinaire" in error.lower() for error in result.errors))

    def test_td_substance_rejects_sql_without_expected_result(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = root / "T10_TD_sql_select_where_join.md"
            td.write_text(
                """# TD
### Exercice 1
- Données : Eleve(id, nom).
- Consigne : écrire la requête.
### Corrigé exercice 1
SELECT nom FROM Eleve;
""",
                encoding="utf-8",
            )

            result = td_substance.analyze_linked_td_substance(root, [td])

            self.assertTrue(any("sql" in error.lower() and "résultat" in error.lower() for error in result.errors))

    def test_td_substance_rejects_network_without_fields_routes_or_decision(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = root / "P10_TD_reseaux_protocoles_paquets.md"
            td.write_text(
                """# TD
### Exercice 1
- Données : une communication.
### Corrigé exercice 1
La communication se déroule correctement entre les machines.
""",
                encoding="utf-8",
            )

            result = td_substance.analyze_linked_td_substance(root, [td])

            self.assertTrue(any("réseau" in error.lower() for error in result.errors))

    def test_td_substance_rejects_algorithm_without_trace_invariant_complexity_or_pseudocode(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = root / "T17_TD_programmation_dynamique.md"
            td.write_text(
                """# TD
### Exercice 1
- Données : problème d'optimisation.
### Corrigé exercice 1
On applique la méthode vue en cours et on obtient la meilleure valeur.
""",
                encoding="utf-8",
            )

            result = td_substance.analyze_linked_td_substance(root, [td])

            self.assertTrue(any("algorithmique" in error.lower() for error in result.errors))

    def test_td_substance_accepts_real_algorithmic_correction(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = root / "T17_TD_programmation_dynamique.md"
            td.write_text(
                """# TD
### Exercice 1
- Données : grille 3x3, déplacements droite ou bas.
### Corrigé exercice 1
État : dp[i][j] compte les chemins vers la case (i,j).
Initialisation : dp[0][j]=1 et dp[i][0]=1.
Récurrence : dp[i][j] = dp[i-1][j] + dp[i][j-1].
Trace : ligne0 [1,1,1], ligne1 [1,2,3], ligne2 [1,3,6].
Complexité : O(n*m), chaque case est remplie une fois.
""",
                encoding="utf-8",
            )

            self.assertTrue(td_substance.correction_has_substance(td, "grille", td.read_text(encoding="utf-8")))

    def test_td_substance_rejects_generic_correction_without_real_result(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = root / "P10_TD_reseaux_protocoles_paquets.md"
            td.write_text(
                """---
title: P10 TD
level: premiere
sequence_id: P10
document_type: td
status: needs_review
official_program:
  capacities:
    - P-ARCH-02A
---
# TD réseaux

## Exercices
### Exercice 1
- Données : paquet de test.
- Consigne : analyser la situation.
- Production attendue : conclusion.

## Corrigé
### Corrigé exercice 1
Résultat indicatif : l'élève doit obtenir une conclusion explicite.
Démarche : partir de la donnée fournie, isoler les grandeurs utiles.
""",
                encoding="utf-8",
            )

            result = td_substance.analyze_linked_td_substance(root, [td])

            self.assertTrue(any("corrigé générique" in error.lower() for error in result.errors))

    def test_evaluation_substance_rejects_vague_answer_and_repeated_bareme(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            evaluation = root / "T10_evaluation_sql_select_where_join.md"
            evaluation.write_text(
                """---
title: T10 évaluation
level: terminale
sequence_id: T10
document_type: evaluation
status: needs_review
official_program:
  capacities:
    - T-BDD-03A
---
# Évaluation SQL

## Questions
### Question 1
Écrire une requête SQL adaptée.
### Question 2
Écrire une autre requête SQL adaptée.
### Question 3
Expliquer l'erreur.
### Question 4
Corriger la requête.

## Barème
- Question 1 : 1 point méthode, 1 point résultat.
- Question 2 : 1 point méthode, 1 point résultat.
- Question 3 : 1 point méthode, 1 point résultat.
- Question 4 : 1 point méthode, 1 point résultat.

## Corrigé professeur
### Question 1
Solution explicite attendue.
### Question 2
Solution explicite attendue.
""",
                encoding="utf-8",
            )

            result = evaluation_substance.analyze_linked_evaluation_substance(root, [evaluation])

            self.assertTrue(any("réponse attendue vague" in error.lower() for error in result.errors))
            self.assertTrue(any("barème trop répétitif" in error.lower() for error in result.errors))

    def test_evaluation_substance_rejects_questions_without_explicit_corrections(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            evaluation = root / "T10_evaluation_sql_select_where_join.md"
            evaluation.write_text(
                """# Évaluation
## Questions
### Question 1
Écrire SELECT nom FROM Eleve.
### Question 2
Prévoir le résultat.

## Barème
- Question 1 : requête SELECT correcte avec colonne nom.
- Question 2 : résultat attendu cité.
""",
                encoding="utf-8",
            )

            result = evaluation_substance.analyze_linked_evaluation_substance(root, [evaluation])

            self.assertTrue(any("section corrigé question" in error.lower() for error in result.errors))

    def test_evaluation_substance_does_not_treat_questions_as_corrections(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            evaluation = root / "T10_evaluation_sql_select_where_join.md"
            evaluation.write_text(
                """# Évaluation
## Questions
### Question 1
SELECT nom FROM Eleve WHERE classe='T1';
### Question 2
Résultat attendu à donner.
""",
                encoding="utf-8",
            )

            result = evaluation_substance.analyze_linked_evaluation_substance(root, [evaluation])

            self.assertTrue(any("corrigé absent" in error.lower() for error in result.errors))

    def test_evaluation_substance_rejects_repeated_bareme_even_without_forbidden_phrase(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            evaluation = root / "P10_evaluation_reseaux_protocoles_paquets.md"
            evaluation.write_text(
                """# Évaluation
## Questions
### Question 1
Identifier les champs d'un paquet.
### Question 2
Décrire une route.
### Question 3
Décider pour un TTL.
### Question 4
Justifier un protocole.

## Barème
- Question 1 : 1 point méthode, 1 point résultat.
- Question 2 : 1 point méthode, 1 point résultat.
- Question 3 : 1 point méthode, 1 point résultat.
- Question 4 : 1 point méthode, 1 point résultat.

## Corrigé professeur
### Corrigé question 1
IP source 192.168.1.20, IP destination 172.16.0.8, protocole TCP.
### Corrigé question 2
Route locale puis passerelle 192.168.1.1.
### Corrigé question 3
TTL décrémenté à 0 : paquet détruit, message ICMP possible.
### Corrigé question 4
ACK confirme la réception et déclenche la suite.
""",
                encoding="utf-8",
            )

            result = evaluation_substance.analyze_linked_evaluation_substance(root, [evaluation])

            self.assertTrue(any("barème trop répétitif" in error.lower() for error in result.errors))

    def test_evaluation_substance_rejects_narrative_correction_without_proof(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            evaluation = root / "T17_evaluation_programmation_dynamique.md"
            evaluation.write_text(
                """# Évaluation
### Question 1
Résoudre le problème.
### Corrigé question 1
L'élève explique clairement la démarche et conclut correctement.
## Barème
- Question 1 : critère spécifique sur l'état et la récurrence.
""",
                encoding="utf-8",
            )

            result = evaluation_substance.analyze_linked_evaluation_substance(root, [evaluation])

            self.assertTrue(any("sans preuve disciplinaire" in error.lower() for error in result.errors))

    def test_evaluation_substance_accepts_question_by_question_correction(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            evaluation = root / "T10_evaluation_sql_select_where_join.md"
            evaluation.write_text(
                """# Évaluation
### Question 1
Prévoir le résultat de SELECT nom FROM Eleve WHERE classe='T1' ORDER BY nom.
### Corrigé question 1
Requête lue : SELECT nom FROM Eleve WHERE classe='T1' ORDER BY nom.
Résultat attendu : deux lignes, Ada puis Grace, car seuls les élèves de T1 sont gardés.
## Barème
- Question 1 : colonne nom identifiée ; filtre classe='T1' appliqué ; ordre Ada puis Grace obtenu.
""",
                encoding="utf-8",
            )

            self.assertTrue(
                evaluation_substance.correction_has_substance(
                    evaluation,
                    "SELECT nom FROM Eleve WHERE classe='T1'",
                    "Résultat attendu : deux lignes, Ada puis Grace.",
                )
            )

    def test_scope_hardcoding_rejects_fixed_target_prefix_set(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            script = root / "check_demo.py"
            script.write_text("TARGET_PREFIXES = {'P10', 'P11', 'T10'}\n", encoding="utf-8")

            result = scope_hardcoding.analyze_no_operational_scope_hardcoding(root, [script])

            self.assertTrue(any("TARGET_PREFIXES" in error for error in result.errors))

    def test_scope_hardcoding_scans_all_check_scripts_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            scripts = root / "scripts"
            scripts.mkdir()
            (scripts / "check_demo.py").write_text("TARGET_SEQUENCES = {'P10', 'T10'}\n", encoding="utf-8")

            result = scope_hardcoding.analyze_no_operational_scope_hardcoding(root)

            self.assertTrue(any("check_demo.py" in error for error in result.errors))

    def test_readiness_quality_coupling_rejects_operational_sheet_with_formal_td(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            td = root / "P10_TD_reseaux_protocoles_paquets.md"
            td.write_text(
                """---
title: P10 TD
level: premiere
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
Lire un paquet.
## Corrigé
### Corrigé exercice 1
Réponse explicite attendue.
""",
                encoding="utf-8",
            )
            operational_sheet(root, "P10", td=td.name)

            result = readiness_coupling.analyze_operational_readiness_quality_coupling(root)

            self.assertTrue(any("P10_TD_reseaux_protocoles_paquets.md" in error for error in result.errors))

    def test_register_hidden_debt_rejects_operational_sheet_in_general_debt(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            operational_sheet(root, "P10", td="P10_TD_reseaux_protocoles_paquets.md")
            (root / "missing_documents_register_v2.md").write_text(
                """# Registre

## Dettes pédagogiques générales non liées à une fiche opérationnelle
| Fichier | Niveau | Séquence | Séance(s) | Type | Priorité | Statut | Responsable | Date cible | Source possible | Lien Drive éventuel | Dépendance | Décision | Blocage si absent | Fiche(s) concernée(s) | Impact pédagogique |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P10_TD_reseaux_protocoles_paquets.md | premiere | P10 | P10-S1 | TD | haute | absent | equipe NSI | 2027-06-30 | Documents_DRIVE | NA | fiche P10 | créer | oui | P10_fiche_cours_demo.md | TD absent |
""",
                encoding="utf-8",
            )

            result = hidden_debt.analyze_register_no_hidden_operational_debt(root)

            self.assertTrue(any("fiche opérationnelle" in error.lower() for error in result.errors))

    def test_drive_plan_requires_inventory_and_quarantine_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            result = drive_plan.analyze_drive_integration_plan(root)

            self.assertTrue(any("drive_inventory.csv absent" in error for error in result.errors))
            self.assertTrue(any("drive_quarantine_manifest.csv absent" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
