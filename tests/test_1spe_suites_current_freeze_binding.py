"""Le gel 1SPE-SUITES est une identite de CONTENU.

Decision humaine du 2026-08-30 : le gel c667f12b / 161 objets est reemis
apres la correction editoriale du chapitre ; il devient HISTORICAL_SUPERSEDED
et n'est jamais reecrit. Ces
tests fixent la semantique correspondante, dans les deux sens :

* une derive non semantique -- HEAD qui avance, branche renommee, autre
  worktree, enveloppe derivee rafraichie, ligne d'autorite d'un AUTRE chapitre
  -- ne rebinde PAS le gel ;
* une derive de contenu couvert -- source editee, objet ajoute ou retire, QCM,
  corrige, remediation, mapping programme du chapitre -- le perime.

Aucun rebind automatique dans un sens comme dans l'autre.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PRODUCER = "scripts/build_1spe_suites_current_freeze_binding.py"
BINDING = "audit/1SPE_SUITES_CURRENT_FREEZE_BINDING.json"
CURRENT = "CURRENT_EQUIVALENT_TO_FROZEN_CONTENT"
STALE = "STALE_CONTENT_CHANGED"

CHAPTER = "Mathematiques/manuel-maths/chapitres/1SPE-SUITES"
COVERAGE = "audit/official_program_coverage/1SPE.json"


def _run(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args), cwd=repo, text=True, capture_output=True, check=check, timeout=300
    )


@pytest.fixture(scope="module")
def repo(tmp_path_factory: pytest.TempPathFactory) -> Path:
    destination = tmp_path_factory.mktemp("suites-freeze-binding") / "repository"
    subprocess.run(
        ["git", "clone", "-q", "--no-hardlinks", str(ROOT), str(destination)],
        check=True,
        timeout=600,
    )
    _run(destination, "git", "config", "user.email", "test@example.invalid")
    _run(destination, "git", "config", "user.name", "test")
    return destination


@pytest.fixture()
def clean_repo(repo: Path) -> Path:
    yield repo
    _run(repo, "git", "checkout", "--quiet", "--", ".")
    _run(repo, "git", "clean", "-qfd")


def _binding_state(repo: Path) -> dict:
    _run(repo, sys.executable, PRODUCER)
    return json.loads((repo / BINDING).read_text(encoding="utf-8"))


def test_a_descendant_head_keeps_the_binding_current(clean_repo: Path) -> None:
    """HEAD qui avance sur un fichier hors perimetre ne perime rien."""
    unrelated = clean_repo / "audit" / "DEBT_BURNDOWN.md"
    unrelated.write_text(unrelated.read_text(encoding="utf-8") + "\n<!-- t -->\n", encoding="utf-8")
    _run(clean_repo, "git", "add", "audit/DEBT_BURNDOWN.md")
    _run(clean_repo, "git", "commit", "--quiet", "-m", "unrelated advance")
    payload = _binding_state(clean_repo)

    assert payload["binding_state"] == CURRENT
    assert payload["current_repository_sha"] != payload["freeze_source_sha"]
    _run(clean_repo, "git", "reset", "--quiet", "--hard", "HEAD~1")


def test_b_branch_rename_keeps_the_binding_current(clean_repo: Path) -> None:
    """Le nom de branche n'est jamais une autorite de contenu."""
    before = _binding_state(clean_repo)
    _run(clean_repo, "git", "checkout", "--quiet", "-b", "totalement/autre-nom")
    after = _binding_state(clean_repo)

    assert before["binding_state"] == after["binding_state"] == CURRENT
    assert before["current_branch"]["value"] != after["current_branch"]["value"]
    assert after["current_branch"]["binding"] == "INFORMATIONAL_ONLY"
    assert before["current_object_set_digest"] == after["current_object_set_digest"]
    _run(clean_repo, "git", "checkout", "--quiet", "-")


def test_c_another_worktree_with_the_same_content_stays_current(clean_repo: Path) -> None:
    """Le clone est a un autre chemin absolu : le verdict ne bouge pas."""
    payload = _binding_state(clean_repo)

    assert payload["binding_state"] == CURRENT
    assert str(clean_repo) != str(ROOT)
    assert "chemin absolu" in " ".join(payload["digest_semantics"]["excluded_from_comparison"])


def test_c_bis_derived_envelope_refresh_does_not_rebind(clean_repo: Path) -> None:
    """BUILD_MANIFEST est une enveloppe derivee, pas une liaison de contenu."""
    manifest = clean_repo / "audit" / "BUILD_MANIFEST.json"
    document = json.loads(manifest.read_text(encoding="utf-8"))
    document.setdefault("provenance", {})["head_sha"] = "0" * 40
    manifest.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    assert _binding_state(clean_repo)["binding_state"] == CURRENT


def test_c_ter_authority_line_of_another_chapter_does_not_rebind(clean_repo: Path) -> None:
    """Le defaut structurel corrige : une ligne GEOREP ne perime pas SUITES."""
    coverage = clean_repo / COVERAGE
    document = json.loads(coverage.read_text(encoding="utf-8"))
    touched = 0
    for row in document["rows"]:
        if row.get("chapter") != "1SPE-SUITES":
            row["official_section"] = str(row.get("official_section")) + " (edit)"
            touched += 1
    assert touched, "aucune ligne d'un autre chapitre a editer"
    coverage.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    payload = _binding_state(clean_repo)

    assert payload["programme_authority_identity_pass"] is True
    assert payload["binding_state"] == CURRENT


# -- Autorite semantique vs artefact de rendu --------------------------------
#
# QCM_SEMANTIC_AUTHORITY = JSON canonique
# QCM_RENDER_ARTIFACT    = TeX genere
#
# Le TeX genere ne doit jamais devenir une seconde autorite semantique
# concurrente du JSON : une correction typographique du gabarit change ses
# octets sans changer une seule reponse.

QCM_JSON = f"{CHAPTER}/qcm/1SPE-SUITES-QCM.json"
QCM_TEX = f"{CHAPTER}/qcm/1SPE-SUITES-QCM.tex"


def _mutate(repo: Path, relative: str, old: str, new: str) -> None:
    """Remplace `old` par `new` et refuse une mutation qui ne mute rien."""

    target = repo / relative
    text = target.read_text(encoding="utf-8")
    mutant = text.replace(old, new, 1)
    assert mutant != text, f"TEST_SETUP_FAILURE: {old!r} absent de {relative}"
    target.write_text(mutant, encoding="utf-8")


def test_e_accent_only_change_of_the_generated_tex_keeps_the_freeze_current(
    clean_repo: Path,
) -> None:
    """1. TeX genere accentue, JSON canonique inchange => gel CURRENT."""

    before = _binding_state(clean_repo)
    json_before = (clean_repo / QCM_JSON).read_bytes()
    # Le chapitre est desormais correctement accentue : la mutation
    # accent-only va donc de la forme accentuee vers la forme ASCII.
    _mutate(clean_repo, QCM_TEX, "num\u00e9riques", "numeriques")
    payload = _binding_state(clean_repo)

    assert (clean_repo / QCM_JSON).read_bytes() == json_before
    assert payload["binding_state"] == CURRENT
    assert payload["semantic_identity_pass"] is True
    assert payload["findings"]["covered_source_drift"] == []
    assert payload["findings"]["render_artifact_drift"] == [QCM_TEX]
    assert payload["render_evidence_state"] == "RENDER_CHANGED"
    assert before["qcm_semantic_digest"] == payload["qcm_semantic_digest"]


def test_f_typography_only_template_change_keeps_the_freeze_current(
    clean_repo: Path,
) -> None:
    """2. Le gabarit ne change que la typographie => gel CURRENT."""

    _mutate(clean_repo, QCM_TEX, "d\u00e9finie", "definie")
    payload = _binding_state(clean_repo)

    assert payload["binding_state"] == CURRENT
    assert payload["qcm_semantic_authority"] == QCM_JSON
    assert payload["qcm_render_artifact"] == QCM_TEX


def test_g_a_canonical_option_change_makes_the_freeze_stale(clean_repo: Path) -> None:
    """3. Une option du JSON canonique change => gel STALE."""

    document = json.loads((clean_repo / QCM_JSON).read_text(encoding="utf-8"))
    question = document["questions"][0]
    letter = next(iter(question["options"]))
    question["options"][letter] = question["options"][letter] + " (modifie)"
    (clean_repo / QCM_JSON).write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    payload = _binding_state(clean_repo)

    assert payload["binding_state"] == STALE
    assert QCM_JSON in payload["findings"]["covered_source_drift"]


def test_h_a_canonical_key_change_makes_the_freeze_stale(clean_repo: Path) -> None:
    """4. La bonne reponse du JSON canonique change => gel STALE."""

    document = json.loads((clean_repo / QCM_JSON).read_text(encoding="utf-8"))
    question = document["questions"][0]
    other = next(
        letter for letter in question["options"] if letter != question["correcte"]
    )
    question["correcte"] = other
    (clean_repo / QCM_JSON).write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    payload = _binding_state(clean_repo)

    assert payload["binding_state"] == STALE
    assert QCM_JSON in payload["findings"]["covered_source_drift"]


def test_i_a_diagnostic_change_makes_the_freeze_stale(clean_repo: Path) -> None:
    """5. Un diagnostic du JSON canonique change => gel STALE."""

    document = json.loads((clean_repo / QCM_JSON).read_text(encoding="utf-8"))
    question = next(item for item in document["questions"] if item.get("diagnostics"))
    letter = next(iter(question["diagnostics"]))
    entry = question["diagnostics"][letter]
    entry["erreur"] = str(entry.get("erreur", "")) + " (modifie)"
    (clean_repo / QCM_JSON).write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    payload = _binding_state(clean_repo)

    assert payload["binding_state"] == STALE
    assert QCM_JSON in payload["findings"]["covered_source_drift"]


def test_j_a_remediation_change_still_makes_the_freeze_stale(clean_repo: Path) -> None:
    """La remediation reste une source semantique couverte."""

    remediation = sorted((clean_repo / CHAPTER / "remediation").glob("*.tex"))[0]
    remediation.write_text(
        remediation.read_text(encoding="utf-8") + "\n% derive semantique\n",
        encoding="utf-8",
    )
    payload = _binding_state(clean_repo)

    assert payload["binding_state"] == STALE


def test_d_covered_source_change_makes_the_binding_stale(clean_repo: Path) -> None:
    course = clean_repo / CHAPTER / "cours" / "10_C1_generalites_suites.tex"
    course.write_text(course.read_text(encoding="utf-8") + "\n% derive\n", encoding="utf-8")
    payload = _binding_state(clean_repo)

    assert payload["binding_state"] == STALE
    assert payload["object_blob_identity_pass"] is False
    assert payload["findings"]["modified_objects"], "l'objet modifie doit etre nomme"


def test_e_added_object_makes_the_binding_stale(clean_repo: Path) -> None:
    extra = clean_repo / CHAPTER / "exercices" / "1SPE-SUITES-EX-999.tex"
    extra.write_text(
        '% META: {"id": "1SPE-SUITES-EX-999", "type_objet": "exercice", "status": "draft"}\n',
        encoding="utf-8",
    )
    payload = _binding_state(clean_repo)

    assert payload["binding_state"] == STALE
    assert payload["findings"]["supplementary_objects"]


def test_e_bis_removed_object_makes_the_binding_stale(clean_repo: Path) -> None:
    victim = clean_repo / CHAPTER / "exercices" / "1SPE-SUITES-EX-001.tex"
    victim.unlink()
    payload = _binding_state(clean_repo)

    assert payload["binding_state"] == STALE
    assert payload["findings"]["missing_objects"]
    assert payload["current_object_count"] < payload["freeze_object_count"]


def test_f_qcm_change_makes_the_binding_stale(clean_repo: Path) -> None:
    qcm = clean_repo / CHAPTER / "qcm" / "1SPE-SUITES-QCM.json"
    qcm.write_text(qcm.read_text(encoding="utf-8").replace("}\n", "}\n", 1) + "\n", encoding="utf-8")
    payload = _binding_state(clean_repo)

    assert payload["binding_state"] == STALE
    assert payload["findings"]["covered_source_drift"]


def test_f_bis_remediation_change_makes_the_binding_stale(clean_repo: Path) -> None:
    remediation = clean_repo / CHAPTER / "remediation" / "1SPE-SUITES-RE-C1.tex"
    remediation.write_text(
        remediation.read_text(encoding="utf-8") + "\n% derive\n", encoding="utf-8"
    )

    assert _binding_state(clean_repo)["binding_state"] == STALE


def test_f_ter_chapter_programme_mapping_change_makes_the_binding_stale(
    clean_repo: Path,
) -> None:
    coverage = clean_repo / COVERAGE
    document = json.loads(coverage.read_text(encoding="utf-8"))
    touched = 0
    for row in document["rows"]:
        if row.get("chapter") == "1SPE-SUITES":
            row["contract_capacity"] = "1SPE-SUITES-C99"
            touched += 1
    assert touched, "aucune ligne SUITES a editer"
    coverage.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    payload = _binding_state(clean_repo)

    assert payload["programme_authority_identity_pass"] is False
    assert payload["binding_state"] == STALE


def test_the_historical_freeze_artifact_is_never_rewritten(clean_repo: Path) -> None:
    """Le producteur de liaison ne touche jamais le gel historique."""
    freeze = clean_repo / "audit" / "1SPE_SUITES_REVIEW_SOURCE_FREEZE.json"
    before = freeze.read_bytes()
    _binding_state(clean_repo)

    assert freeze.read_bytes() == before
    payload = json.loads((clean_repo / BINDING).read_text(encoding="utf-8"))
    assert payload["freeze_source_sha"] == "1057951c1a7e8be8731982b5918effb60f2471cc"
    assert payload["freeze_object_count"] == 161
    assert payload["staleness_rules"]["automatic_rebind"] == "FORBIDDEN"


def test_the_binding_artifact_is_not_stale_after_a_later_commit(clean_repo: Path) -> None:
    """Publier le rapport ne doit pas perimer le rapport."""

    _run(clean_repo, sys.executable, PRODUCER)
    payload = json.loads((clean_repo / BINDING).read_text(encoding="utf-8"))
    payload["current_repository_sha"] = "0" * 40
    payload["current_branch"]["value"] = "un/commit/plus/tard"
    (clean_repo / BINDING).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    checked = _run(clean_repo, sys.executable, PRODUCER, "--check", check=False)

    assert checked.returncode == 0, checked.stderr
    assert CURRENT in checked.stdout


def _load_freeze_producer(repo: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        f"suites_freeze_{repo.parent.name}",
        repo / "scripts" / "build_1spe_suites_review_source_freeze.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ------------------------------------------- autorite programme GLOBALE ------


@pytest.mark.parametrize(
    "authority",
    [
        "Mathematiques/manuel-maths/sources/txt/BO2026_1SPE_specialite.txt",
        "audit/OFFICIAL_PROGRAM_AUTHORITY_2026_2027.yaml",
        "audit/official_program_contracts/1SPE.yaml",
        "audit/OFFICIAL_SOURCE_SEGMENT_LEDGER.json",
    ],
)
def test_a_global_programme_rule_change_makes_the_binding_stale(
    clean_repo: Path, authority: str
) -> None:
    """La projection de chapitre ne doit pas devenir une echappatoire.

    Seule la matrice de couverture est structuree par chapitre, donc seule elle
    est projetee. Les autorites GLOBALES -- texte officiel, autorite programme,
    contrat de manuel, registre de segments -- restent liees integralement :
    une regle applicable a tous les chapitres perime bien ce gel.
    """

    path = clean_repo / authority
    path.write_text(
        path.read_text(encoding="utf-8") + "\n# regle globale modifiee\n",
        encoding="utf-8",
    )
    payload = _binding_state(clean_repo)

    assert payload["programme_authority_identity_pass"] is False
    assert authority in payload["findings"]["programme_authority_drift"]
    assert payload["binding_state"] == STALE


def test_only_the_chapter_structured_authority_is_projected(clean_repo: Path) -> None:
    """Une seule autorite est projetee ; les autres sont liees a l'octet."""

    producer = _load_freeze_producer(clean_repo)
    frozen = json.loads(
        (clean_repo / "audit" / "1SPE_SUITES_REVIEW_SOURCE_FREEZE.json").read_text(
            encoding="utf-8"
        )
    )
    declared = {row["path"] for row in frozen["programme_authority"]["sources"]}
    projected = set(producer.CHAPTER_SCOPED_AUTHORITY_PATHS)

    assert projected <= declared
    assert len(projected) == 1
    assert declared - projected, "toutes les autorites ne peuvent pas etre projetees"
