from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_chapter_sources_do_not_use_undefined_blacklozenge():
    offenders = [
        path.relative_to(ROOT)
        for path in (ROOT / "chapitres").rglob("*.tex")
        if "\\blacklozenge" in path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_nexus_class_loads_amssymb_for_square_symbol():
    document_class = (ROOT / "gabarits" / "nexus-manuel.cls").read_text(encoding="utf-8")

    assert r"\RequirePackage{amssymb}" in document_class


def test_nexus_class_loads_amsthm_after_amsmath_for_qed():
    document_class = (ROOT / "gabarits" / "nexus-manuel.cls").read_text(encoding="utf-8")

    assert document_class.index(r"\RequirePackage{amsmath}") < document_class.index(
        r"\RequirePackage{amsthm}"
    )


def test_nexus_class_loads_common_assets_from_the_gabarits_directory():
    document_class = (ROOT / "gabarits" / "nexus-manuel.cls").read_text(encoding="utf-8")

    assert r"\InputIfFileExists{gabarits/nexus-icons.tex}" in document_class


def test_nexus_class_has_no_hardcoded_subject_label():
    """B.2 — aucun libelle de matiere en dur dans la classe."""
    document_class = (ROOT / "gabarits" / "nexus-manuel.cls").read_text(encoding="utf-8")

    for label in ["Manuel NSI", "Manuel Mathématiques", "Manuel Physique"]:
        assert label not in document_class, (
            f"Libellé de matière « {label} » codé en dur dans nexus-manuel.cls"
        )
