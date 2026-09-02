"""Le registre d'alignement semantique MESURE et ROUTE ; il n'approuve rien.

`build_true_pedagogical_coverage.py` definit un etat
`SEMANTICALLY_VALIDATED_CONTENT` -- « au moins une preuve separee atteste que
le corps sert cet UID » -- mais n'a aucune entree de preuve : l'etat est
inatteignable par construction, et les 371 cellules 1SPE restent
indefiniment en « identite declaree, alignement non etabli ».

Ces tests protegent trois choses, dans cet ordre.

1. La COMPLETUDE du routage. `UNKNOWN = 0` : toute cellule tombe dans
   exactement une branche. Une branche muette rendrait le registre inutile.

2. La CREDIBILITE de la branche defaut. Un registre qui ne renvoie jamais
   `DEFAUT_ETABLI` sur le corpus reel ne prouve rien tant qu'on n'a pas
   montre qu'il SAIT le renvoyer. Deux mutations le forcent : deux capacites
   soeurs creditees par un corps identique, et un corrige reattribue a un
   exercice d'une autre capacite. Sans elles, `DEFAUT_ETABLI = 0` serait
   indiscernable d'un detecteur mort.

3. La PEREMPTION. Un dossier de revue humaine qui ne bouge pas quand le
   contenu bouge certifie un contenu qui n'existe plus. Le sha256 du corps
   doit suivre le corps.

Ce que ces tests n'exigent PAS : `DEFAUT_ETABLI = 0`. Une revue humaine est un
resultat legitime.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "audit/SEMANTIC_ALIGNMENT_LEDGER.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "semantic_alignment_ledger", ROOT / "scripts/build_semantic_alignment_ledger.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def payload(producer) -> dict:
    return producer.build_ledger()


@pytest.fixture(scope="module")
def committed() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


# -- corpus reel ------------------------------------------------------------


def test_the_committed_ledger_matches_the_producer(producer) -> None:
    assert producer.main(["--check"]) == 0


def test_every_routed_cell_falls_in_exactly_one_branch(payload: dict) -> None:
    """OLD : rien -- l'etat `SEMANTICALLY_VALIDATED_CONTENT` etait inatteignable
    et aucune cellule n'etait routee.
    NEW : `UNKNOWN = 0` et la somme des dispositions egale le nombre de
    cellules traitees. Une cellule qui echapperait aux deux branches serait un
    trou de mesure deguise en resultat."""

    counts = payload["counts"]
    assert counts["UNKNOWN"] == 0
    assert (
        counts["DEFAUT_ETABLI"] + counts["JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS"]
        == counts["cells_examined"]
    )
    assert counts["cells_examined"] == len(payload["records"])
    assert {
        record["semantic_alignment"]["disposition"] for record in payload["records"]
    } <= {"DEFAUT_ETABLI", "JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS"}


def test_the_ledger_covers_exactly_the_unvalidated_cells(producer, payload) -> None:
    """Le registre ne choisit pas ses cellules : il prend TOUTES celles que la
    mesure laisse dans l'etat non valide, et aucune autre."""

    coverage = producer._coverage_module().build_coverage()
    expected = {
        f"{row['chapter']}/{row['capacity']}/{row['role']}"
        for row in coverage["rows"]
        if row["manual"] == payload["scope"]
        and row["state"] == producer.ROUTED_CELL_STATE
    }
    assert {record["cell_id"] for record in payload["records"]} == expected
    assert expected, "le corpus 1SPE doit encore porter des cellules non validees"


def test_every_record_carries_the_four_required_elements(payload: dict) -> None:
    for record in payload["records"]:
        capacity = record["official_capacity"]
        assert capacity["canonical_uid"].startswith(payload["scope"] + "::")
        assert capacity["local_code"]
        assert capacity["student_wording"], record["cell_id"]
        assert "official_atoms" in capacity
        assert [atom["atom_id"] for atom in capacity["official_atoms"]] == capacity[
            "official_atom_ids"
        ]
        for atom in capacity["official_atoms"]:
            assert atom["atom_id"]
            assert atom["official_wording_or_short_paraphrase"]

        assert record["pedagogical_role"]

        assert record["actual_body"], record["cell_id"]
        for entry in record["actual_body"]:
            assert entry["object_id"]
            assert entry["path"]
            assert entry["body_sha256"].startswith("sha256:")
            assert len(entry["body_sha256"]) == len("sha256:") + 64

        alignment = record["semantic_alignment"]
        assert alignment["disposition"]
        assert alignment["because"]
        assert isinstance(alignment["evidence"], list)


def test_the_because_field_names_its_evidence(payload: dict) -> None:
    for record in payload["records"]:
        alignment = record["semantic_alignment"]
        because = alignment["because"]
        if alignment["disposition"] == "DEFAUT_ETABLI":
            assert alignment["evidence"]
            for row in alignment["evidence"]:
                assert row["channel"] in because
                assert row["artifact"] in because
        else:
            assert not alignment["evidence"]
            assert "jugement pedagogique" in because
            assert "scripts/capacity_identity.py" in because


def test_the_ledger_approves_nothing_and_closes_no_gate(payload: dict) -> None:
    """Le depot refuse de deduire un alignement semantique d'une preuve
    structurelle : aucune branche ne certifie POSITIVEMENT un alignement."""

    assert payload["approves_nothing"] is True
    assert payload["closes_no_gate"] is True
    assert set(payload["dispositions"]) == {
        "DEFAUT_ETABLI",
        "JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS",
    }
    assert "ALIGNE" not in json.dumps(payload["dispositions"], ensure_ascii=False)


def test_the_ledger_never_touches_the_publish_readiness_gate(committed: dict) -> None:
    matrix = json.loads(
        (ROOT / "audit/PUBLISH_READINESS_CHAPTER_MATRIX.json").read_text(
            encoding="utf-8"
        )
    )
    statuses = {
        chapter["pedagogical_role_coverage"]["status"]
        for chapter in matrix["chapters"]
        if chapter["manual"] == committed["scope"]
    }
    assert statuses == {"GAP"}, (
        "la decision de fermer ce gate est humaine ; ce registre ne la prend pas"
    )


def test_two_runs_produce_the_same_artifact(producer) -> None:
    first = producer.render_json(producer.build_ledger())
    second = producer.render_json(producer.build_ledger())
    assert first == second


# -- corpus synthetique -----------------------------------------------------


def _corpus(tmp_path: Path, codes: tuple[str, ...] = ("C1", "C2")) -> tuple[Path, Path]:
    corpus = tmp_path / "chapitres"
    chapter = corpus / "TSPE-X"
    chapter.mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        yaml.safe_dump(
            {
                "capacites": [
                    {
                        "code": code,
                        "ref_capacite": f"TSPE-X-{code}",
                        "libelle_eleve": f"Je sais faire {code}.",
                    }
                    for code in codes
                ]
            }
        ),
        encoding="utf-8",
    )
    return corpus, chapter


_DEFAULT_TYPES = {
    "cours": "cours",
    "methodes": "methode",
    "exercices": "exercice",
    "corriges": "corrige",
    "remediation": "remediation",
    "evaluations": "evaluation",
}


def _source(path: Path, meta: dict, body: str = "Contenu.") -> Path:
    meta = {"type_objet": _DEFAULT_TYPES.get(path.parent.name), **meta}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("% META: " + json.dumps(meta) + "\n" + body + "\n", encoding="utf-8")
    return path


def _build(producer, corpus: Path, sources: list[Path]) -> dict:
    return producer.build_ledger(
        scope="TSPE",
        corpora=(corpus,),
        clone_ledger={
            "objects_on_invalid_credit": [],
            "objects_with_indeterminate_credit": [],
            "groups": [],
        },
        ex_co_graph={},
        official_coverage={},
        qcm_evidence={},
        source_paths=sources,
        qcm_paths=[],
    )


def _record(ledger: dict, cell_id: str) -> dict:
    return next(row for row in ledger["records"] if row["cell_id"] == cell_id)


def test_mutation_de_peremption_le_sha_suit_le_corps(producer, tmp_path: Path) -> None:
    """Un registre qui ne bouge pas quand le contenu bouge ne prouve rien.

    Un dossier de revue humaine certifie un corps precis. Si ce corps change
    sans que le registre change, la revue humaine porte sur un contenu qui
    n'existe plus.
    """

    corpus, chapter = _corpus(tmp_path)
    course = _source(
        chapter / "cours/a.tex",
        {"id": "A", "chapitre": "TSPE-X", "capacites_codes": ["C1"]},
        body="Premiere redaction du cours.",
    )
    before = _build(producer, corpus, [course])
    record_before = _record(before, "TSPE-X/C1/cours")
    sha_before = record_before["actual_body"][0]["body_sha256"]

    course.write_text(
        course.read_text(encoding="utf-8").replace(
            "Premiere redaction du cours.", "Seconde redaction du cours."
        ),
        encoding="utf-8",
    )

    after = _build(producer, corpus, [course])
    record_after = _record(after, "TSPE-X/C1/cours")
    sha_after = record_after["actual_body"][0]["body_sha256"]

    assert sha_after != sha_before
    assert record_after["actual_body_digest"] != record_before["actual_body_digest"]
    assert after["records_digest"] != before["records_digest"]


def test_mutation_de_detection_deux_soeurs_un_seul_corps(
    producer, tmp_path: Path
) -> None:
    """La signature du P0 fondateur : deux capacites soeurs, un corps unique.

    Dix-sept fiches identiques declarees C1 a C16 creditaient seize capacites
    alors qu'une seule etait traitee. Au plus une des attributions peut etre
    juste : c'est une contradiction demontree, pas un doute.
    """

    corpus, chapter = _corpus(tmp_path)
    shared = "Un seul et meme cours, recopie."
    first = _source(
        chapter / "cours/a.tex",
        {"id": "A", "chapitre": "TSPE-X", "capacites_codes": ["C1"]},
        body=shared,
    )
    second = _source(
        chapter / "cours/b.tex",
        {"id": "B", "chapitre": "TSPE-X", "capacites_codes": ["C2"]},
        body=shared,
    )

    ledger = _build(producer, corpus, [first, second])

    for cell_id in ("TSPE-X/C1/cours", "TSPE-X/C2/cours"):
        alignment = _record(ledger, cell_id)["semantic_alignment"]
        assert alignment["disposition"] == "DEFAUT_ETABLI"
        channels = {row["channel"] for row in alignment["evidence"]}
        assert producer.SIBLING_SHARED_BODY in channels
    assert ledger["counts"]["DEFAUT_ETABLI"] == 2
    assert ledger["counts"]["UNKNOWN"] == 0


def test_un_objet_unique_declarant_deux_capacites_n_est_pas_un_defaut(
    producer, tmp_path: Path
) -> None:
    """Le detecteur vise DEUX corps, pas UN objet a deux etiquettes.

    Une evaluation couvre legitimement plusieurs capacites du chapitre. Lire
    cela comme la signature du clonage fabriquerait un P0 la ou le contrat est
    respecte -- et un defaut invente coute aussi cher qu'un defaut ignore.
    """

    corpus, chapter = _corpus(tmp_path)
    evaluation = _source(
        chapter / "evaluations/ev.tex",
        {"id": "EV", "chapitre": "TSPE-X", "capacites_codes": ["C1", "C2"]},
        body="Evaluation couvrant tout le chapitre.",
    )

    ledger = _build(producer, corpus, [evaluation])

    assert ledger["counts"]["DEFAUT_ETABLI"] == 0
    for cell_id in ("TSPE-X/C1/evaluations", "TSPE-X/C2/evaluations"):
        assert (
            _record(ledger, cell_id)["semantic_alignment"]["disposition"]
            == "JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS"
        )


def test_mutation_label_sensitive_un_corrige_reattribue_devient_un_defaut(
    producer, tmp_path: Path
) -> None:
    """Reattribuer un corrige a un exercice d'une AUTRE capacite est un defaut.

    Le corrige continue de REVENDIQUER `C1` alors qu'il corrige un exercice de
    `C2`. La mesure lui retire son credit ; la revendication, elle, reste une
    contradiction demontree qui PORTE SUR la cellule `C1` -- l'oublier
    laisserait un defaut prouve sans destinataire.
    """

    corpus, chapter = _corpus(tmp_path)
    first_exercise = _source(
        chapter / "exercices/ex1.tex",
        {"id": "EX1", "chapitre": "TSPE-X", "capacites_codes": ["C1"]},
        body="Enonce un.",
    )
    second_exercise = _source(
        chapter / "exercices/ex2.tex",
        {"id": "EX2", "chapitre": "TSPE-X", "capacites_codes": ["C2"]},
        body="Enonce deux.",
    )
    kept = _source(
        chapter / "corriges/co1.tex",
        {
            "id": "CO1",
            "chapitre": "TSPE-X",
            "capacites_codes": ["C1"],
            "exercice_id": "EX1",
        },
        body="Corrige un.",
    )
    moved = _source(
        chapter / "corriges/co2.tex",
        {
            "id": "CO2",
            "chapitre": "TSPE-X",
            "capacites_codes": ["C1"],
            "exercice_id": "EX1",
        },
        body="Corrige deux.",
    )
    sources = [first_exercise, second_exercise, kept, moved]

    before = _build(producer, corpus, sources)
    assert (
        _record(before, "TSPE-X/C1/corriges")["semantic_alignment"]["disposition"]
        == "JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS"
    )

    moved.write_text(
        moved.read_text(encoding="utf-8").replace(
            '"exercice_id": "EX1"', '"exercice_id": "EX2"'
        ),
        encoding="utf-8",
    )

    after = _build(producer, corpus, sources)
    alignment = _record(after, "TSPE-X/C1/corriges")["semantic_alignment"]
    assert alignment["disposition"] == "DEFAUT_ETABLI"
    evidence = [
        row
        for row in alignment["evidence"]
        if row["channel"] == producer.EX_CO_CAPACITY_CONTRADICTION
    ]
    assert evidence
    assert evidence[0]["classification"] == "MISMATCHED_CAPACITY"
    assert evidence[0]["object_id"] == "CO2"
    assert evidence[0]["correction_capacities"] == ["C1"]
    assert evidence[0]["exercise_capacities"] == ["C2"]


def test_une_fausse_copie_du_ledger_de_clones_est_un_defaut(
    producer, tmp_path: Path
) -> None:
    """Le ledger de clones a deja tranche : cet objet n'est pas le proprietaire.

    La disposition se deduit de ce que l'artefact DIT, jamais d'une liste
    d'identifiants inscrite ici.
    """

    corpus, chapter = _corpus(tmp_path)
    course = _source(
        chapter / "cours/a.tex",
        {"id": "A", "chapitre": "TSPE-X", "capacites_codes": ["C1"]},
        body="Cours recopie.",
    )
    ledger = producer.build_ledger(
        scope="TSPE",
        corpora=(corpus,),
        clone_ledger={
            "objects_on_invalid_credit": [],
            "objects_with_indeterminate_credit": [],
            "groups": [
                {
                    "clone_group_id": "CG-TEST",
                    "canonical_selection": {"false_copy_paths": [str(course)]},
                }
            ],
        },
        ex_co_graph={},
        official_coverage={},
        qcm_evidence={},
        source_paths=[course],
        qcm_paths=[],
    )
    alignment = _record(ledger, "TSPE-X/C1/cours")["semantic_alignment"]
    assert alignment["disposition"] == "DEFAUT_ETABLI"
    assert {row["channel"] for row in alignment["evidence"]} == {
        producer.CLONE_FALSE_COPY
    }


def test_une_relation_ex_co_structurellement_en_echec_est_un_defaut(
    producer, tmp_path: Path
) -> None:
    """Le graphe EX/CO a deja rendu son verdict : la relation est en echec.

    Le registre ne rejuge pas la relation ; il lit le verdict de l'artefact et
    l'attache a la cellule que l'objet credite.
    """

    corpus, chapter = _corpus(tmp_path)
    exercise = _source(
        chapter / "exercices/ex.tex",
        {"id": "EX", "chapitre": "TSPE-X", "capacites_codes": ["C1"]},
        body="Enonce.",
    )
    correction = _source(
        chapter / "corriges/co.tex",
        {"id": "CO", "chapitre": "TSPE-X", "capacites_codes": ["C1"]},
        body="Corrige sans exercice nomme.",
    )
    ledger = producer.build_ledger(
        scope="TSPE",
        corpora=(corpus,),
        clone_ledger={
            "objects_on_invalid_credit": [],
            "objects_with_indeterminate_credit": [],
            "groups": [],
        },
        ex_co_graph={
            "relations": [
                {
                    "correction_id": "CO",
                    "structural_status": "FAIL",
                    "classifications": ["ORPHAN_CO"],
                    "exercise_id": None,
                }
            ]
        },
        official_coverage={},
        qcm_evidence={},
        source_paths=[exercise, correction],
        qcm_paths=[],
    )
    alignment = _record(ledger, "TSPE-X/C1/corriges")["semantic_alignment"]
    assert alignment["disposition"] == "DEFAUT_ETABLI"
    evidence = alignment["evidence"]
    assert {row["channel"] for row in evidence} == {producer.EX_CO_STRUCTURAL_FAILURE}
    assert evidence[0]["classifications"] == ["ORPHAN_CO"]
    # L'exercice, lui, n'est cite par aucun echec : sa cellule reste humaine.
    assert (
        _record(ledger, "TSPE-X/C1/exercices")["semantic_alignment"]["disposition"]
        == "JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS"
    )


def test_une_cle_qcm_contredite_par_la_preuve_independante_est_un_defaut(
    producer, tmp_path: Path
) -> None:
    """La preuve independante n'a jamais vu la cle : sa contradiction demontre."""

    corpus, chapter = _corpus(tmp_path)
    qcm = chapter / "qcm/TSPE-X-QCM.json"
    qcm.parent.mkdir(parents=True)
    qcm.write_text(
        json.dumps(
            {
                "chapitre": "TSPE-X",
                "questions": [{"id": "Q1", "capacite": "TSPE-X-C1"}],
            }
        ),
        encoding="utf-8",
    )
    ledger = producer.build_ledger(
        scope="TSPE",
        corpora=(corpus,),
        clone_ledger={
            "objects_on_invalid_credit": [],
            "objects_with_indeterminate_credit": [],
            "groups": [],
        },
        ex_co_graph={},
        official_coverage={},
        qcm_evidence={
            "questions": [
                {
                    "source_path": str(qcm),
                    "question_id": "Q1",
                    "evidence_digest": "sha256:0",
                    "verification": {
                        "declared_key": "B",
                        "computed_unique_answer": "A",
                        "answer_key_verdict": "FAIL",
                        "declared_key_matches_computation": False,
                    },
                }
            ]
        },
        source_paths=[],
        qcm_paths=[qcm],
    )
    alignment = _record(ledger, "TSPE-X/C1/qcm")["semantic_alignment"]
    assert alignment["disposition"] == "DEFAUT_ETABLI"
    assert {row["channel"] for row in alignment["evidence"]} == {
        producer.QCM_KEY_CONTRADICTED
    }
    body = _record(ledger, "TSPE-X/C1/qcm")["actual_body"][0]
    assert body["question_id"] == "Q1"
    assert body["body_kind"] == "qcm_question"
