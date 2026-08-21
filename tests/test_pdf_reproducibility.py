"""Contrat exécutable de reproductibilité binaire des PDF produits.

Défaut d'origine (clôture A4, §2-§8) : deux clones frais au MÊME SHA
produisaient des PDF de SHA256 différents. Diagnostic structurel (qpdf) :
une seule divergence, le second élément du champ ``/ID`` du trailer, que
LuaTeX tire au hasard à chaque exécution même sous ``SOURCE_DATE_EPOCH``.

Correction au niveau du PRODUCTEUR : les assembleurs injectent désormais une
identité de trailer DÉTERMINISTE et DÉRIVÉE DES SOURCES
(``pdf_trailer_identity``). Ces tests verrouillent les propriétés exigées :
déterminisme, sensibilité au contenu, distinction par manuel/variante,
absence de tout aléa ou horodatage, et absence de constante globale.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MATH_SCRIPTS = ROOT / "Mathematiques" / "manuel-maths" / "scripts"
NSI_SCRIPTS = ROOT / "NSI" / "scripts"
TRAILER_ID_RE = re.compile(r"\\pdfvariable trailerid\{\[<([0-9A-F]{32})> <([0-9A-F]{32})>\]\}")


def _load(name: str, path: Path, extra_sys_path: Path):
    if str(extra_sys_path) not in sys.path:
        sys.path.insert(0, str(extra_sys_path))
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def math_assembler():
    """Charge l'assembleur Mathématiques avec un ``ROOT`` garanti.

    ``assemble_manuel`` fait ``from common import ROOT`` : si un autre module
    de test a déjà mis en cache un ``common`` issu d'une copie temporaire du
    dépôt, l'assembleur hériterait de ce ROOT et raisonnerait sur un arbre
    incomplet. La fixture recharge donc ``common`` depuis le dépôt réel et
    vérifie le ROOT obtenu, ce qui rend ces tests indépendants de l'ordre
    d'exécution de la suite.
    """
    saved = {
        name: sys.modules.pop(name, None)
        for name in ("common", "pdf_integrity", "assemble_manuel")
    }
    try:
        _load("common", MATH_SCRIPTS / "common.py", MATH_SCRIPTS)
        module = _load(
            "assemble_manuel_math_repro",
            MATH_SCRIPTS / "assemble_manuel.py",
            MATH_SCRIPTS,
        )
        assert module.ROOT == MATH_SCRIPTS.parent, module.ROOT
        yield module
    finally:
        sys.modules.pop("assemble_manuel_math_repro", None)
        for name, value in saved.items():
            sys.modules.pop(name, None)
            if value is not None:
                sys.modules[name] = value


def _math_identity(assembler, manual: str, variant: str, run_id: str) -> str:
    master = assembler.render_master(variant, run_id, manual=manual)
    match = TRAILER_ID_RE.search(master)
    assert match is not None, f"identité de trailer absente: {manual}/{variant}"
    assert match.group(1) == match.group(2)
    return match.group(1)


def test_pdf1_same_sources_same_identity(math_assembler) -> None:
    """CASE PDF1 — mêmes sources ⇒ identité (donc PDF) identique."""
    first = _math_identity(math_assembler, "TEXPERTES", "eleve", "0" * 32)
    second = _math_identity(math_assembler, "TEXPERTES", "eleve", "0" * 32)
    assert first == second


def test_pdf2_identity_is_independent_of_run_and_path(math_assembler) -> None:
    """CASE PDF2 — l'identité ne dépend ni du run_id ni du répertoire.

    Deux worktrees différents compilant les mêmes sources doivent produire le
    même PDF : l'identité ne doit donc capturer aucun chemin absolu ni aucun
    identifiant de run (qui est, lui, aléatoire par construction).
    """
    reference = _math_identity(math_assembler, "TEXPERTES", "eleve", "0" * 32)
    for run_id in ("a" * 32, "1234567890abcdef" * 2, "f" * 32):
        assert _math_identity(math_assembler, "TEXPERTES", "eleve", run_id) == (
            reference
        )


def test_pdf3_relevant_source_change_changes_identity(
    math_assembler, tmp_path
) -> None:
    """CASE PDF3 — une source pédagogique modifiée ⇒ identité différente."""
    fiche = (
        ROOT
        / "Mathematiques/manuel-maths/chapitres/TEXP-GRAPHES/methodes"
        / "TEXP-GRA-ME-002.tex"
    )
    original = fiche.read_bytes()
    before = _math_identity(math_assembler, "TEXPERTES", "eleve", "0" * 32)
    try:
        fiche.write_bytes(original + b"% perturbation de test\n")
        during = _math_identity(math_assembler, "TEXPERTES", "eleve", "0" * 32)
    finally:
        fiche.write_bytes(original)
    after = _math_identity(math_assembler, "TEXPERTES", "eleve", "0" * 32)

    assert during != before, "une source modifiée doit changer l'identité"
    assert after == before, "la restauration doit rendre l'identité initiale"


def test_pdf4_each_manual_and_variant_has_its_own_identity(math_assembler) -> None:
    """CASE PDF4 — jamais de constante globale : une identité par cible."""
    identities = {
        (manual, variant): _math_identity(
            math_assembler, manual, variant, "0" * 32
        )
        for manual in ("1SPE", "TSPE_2026_2027", "TCOMPL", "TEXPERTES")
        for variant in ("eleve", "professeur")
    }
    assert len(set(identities.values())) == len(identities), identities


def test_pdf5_identity_carries_no_clock_or_randomness() -> None:
    """CASE PDF5 — aucune horloge, aucun aléa dans le calcul de l'identité."""
    for script in (
        MATH_SCRIPTS / "pdf_reproducibility.py",
        NSI_SCRIPTS / "assemble.py",
    ):
        source = script.read_text(encoding="utf-8")
        start = source.index("def pdf_trailer_identity(")
        doc_end = source.index('"""', source.index('"""', start) + 3) + 3
        next_definition = source.find("\ndef ", doc_end)
        end = len(source) if next_definition == -1 else next_definition
        body = source[start:end]
        for forbidden in (
            "time.",
            "datetime",
            "secrets",
            "random",
            "uuid",
            "os.environ",
        ):
            assert forbidden not in body, (script.name, forbidden)


def test_pdf5b_producers_pin_the_trailer_identity() -> None:
    """Le mécanisme est CANONIQUE côté producteur, pas un post-traitement."""
    math_source = (MATH_SCRIPTS / "assemble_manuel.py").read_text(
        encoding="utf-8"
    )
    chapter_source = (MATH_SCRIPTS / "assemble.py").read_text(encoding="utf-8")
    assert "from pdf_reproducibility import" in math_source
    assert "from pdf_reproducibility import" in chapter_source
    assert "\\\\pdfvariable trailerid" in math_source
    assert "\\\\pdfvariable trailerid" in chapter_source

    template = (ROOT / "NSI" / "gabarits" / "book_master.tex").read_text(
        encoding="utf-8"
    )
    assert "\\pdfvariable trailerid{[<%%PDF_TRAILER_ID%%> <%%PDF_TRAILER_ID%%>]}" in (
        template
    )
    nsi_source = (NSI_SCRIPTS / "assemble.py").read_text(encoding="utf-8")
    assert '"%%PDF_TRAILER_ID%%", trailer_identity' in nsi_source


def test_pdf6_tracked_pdfs_are_byte_reproducible_evidence() -> None:
    """CASE PDF6 — les 12 PDF de build sont suivis et attestés.

    La reproduction binaire elle-même est rejouée hors suite (deux clones
    frais au SHA de scellement) ; ce test verrouille le PÉRIMÈTRE : aucune
    cible de la matrice ne doit disparaître du dépôt sans décision.
    """
    expected = {
        "Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf",
        "Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf",
        "Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf",
        "Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.pdf",
        "Mathematiques/manuel-maths/build/MANUEL_TCOMPL/MANUEL_TCOMPL_eleve.pdf",
        "Mathematiques/manuel-maths/build/MANUEL_TCOMPL/MANUEL_TCOMPL_professeur.pdf",
        "Mathematiques/manuel-maths/build/MANUEL_TEXPERTES/MANUEL_TEXPERTES_eleve.pdf",
        "Mathematiques/manuel-maths/build/MANUEL_TEXPERTES/MANUEL_TEXPERTES_professeur.pdf",
        "NSI/build/MANUEL_1NSI/MANUEL_1NSI_eleve.pdf",
        "NSI/build/MANUEL_1NSI/MANUEL_1NSI_professeur.pdf",
        "NSI/build/MANUEL_TNSI/MANUEL_TNSI_eleve.pdf",
        "NSI/build/MANUEL_TNSI/MANUEL_TNSI_professeur.pdf",
    }
    for relative in sorted(expected):
        assert (ROOT / relative).is_file(), relative


def test_pdf7_preimage_excludes_every_produced_output(math_assembler) -> None:
    """§2/§7 — SELF_REFERENCE = NO.

    Le préimage ne doit contenir AUCUN artefact produit : ni le PDF, ni son
    SHA, ni un master compilé, ni un manifeste dérivé. Il ne contient que des
    sources versionnées (objets assemblés, transversaux, classe et charte
    canoniques).
    """
    objects = []
    for chapter in math_assembler.MANUAL_CHAPTERS["TEXPERTES"]:
        objects.extend(
            math_assembler.collect_chapter(
                math_assembler.ROOT / "chapitres" / chapter, "eleve"
            )
        )
    master = math_assembler.render_master("eleve", "0" * 32, manual="TEXPERTES")
    body = master.split("\\begin{document}", 1)[1]
    sources = math_assembler._master_source_digests(
        body, objects=objects, git_root=ROOT
    )

    assert sources, "le préimage doit référencer des sources"
    for relative in sources:
        assert "/build/" not in relative, relative
        assert not relative.endswith(".pdf"), relative
        assert not relative.endswith(".fls"), relative
        assert not relative.startswith("audit/"), relative
        assert "MANUELS_PDF_PUBLICATION" not in relative, relative
        # Chemins repo-relatifs uniquement : aucun chemin absolu ne doit
        # entrer dans le digest (sinon deux worktrees divergeraient).
        assert not relative.startswith("/"), relative


def test_pdf8_identity_survives_replacing_the_tracked_output(
    math_assembler, tmp_path
) -> None:
    """§7 — remplacer le PDF suivi ne doit RIEN changer à l'identité.

    Les PDF de build sont versionnés : si leur contenu entrait dans le
    préimage, reconstruire puis committer changerait l'identité au coup
    suivant et la reproductibilité serait circulaire.
    """
    tracked_pdf = (
        ROOT
        / "Mathematiques/manuel-maths/build/MANUEL_TEXPERTES"
        / "MANUEL_TEXPERTES_eleve.pdf"
    )
    if not tracked_pdf.is_file():  # pragma: no cover - dépôt sans artefact
        pytest.skip("PDF suivi absent")
    original = tracked_pdf.read_bytes()
    before = _math_identity(math_assembler, "TEXPERTES", "eleve", "0" * 32)
    try:
        tracked_pdf.write_bytes(original + b"%% octets de perturbation\n")
        during = _math_identity(math_assembler, "TEXPERTES", "eleve", "0" * 32)
    finally:
        tracked_pdf.write_bytes(original)

    assert during == before, (
        "l'identité dépend du PDF produit : auto-référence (SELF_REFERENCE BUG)"
    )


def test_pdf9_identity_is_independent_of_the_absolute_worktree_path(
    math_assembler, tmp_path
) -> None:
    """§3 — même arbre logique, chemin absolu différent ⇒ même identité."""
    import shutil

    reference = _math_identity(math_assembler, "TEXPERTES", "eleve", "0" * 32)

    mirror_root = tmp_path / "mirror"
    manual_source = ROOT / "Mathematiques" / "manuel-maths"
    manual_mirror = mirror_root / "Mathematiques" / "manuel-maths"
    manual_mirror.parent.mkdir(parents=True)
    shutil.copytree(
        manual_source,
        manual_mirror,
        ignore=shutil.ignore_patterns("build", "__pycache__", ".git"),
    )
    shutil.copytree(ROOT / "gabarits", mirror_root / "gabarits")

    # `common` (qui porte ROOT) est mis en cache par le premier chargement :
    # le purger force le miroir à résoudre SON propre ROOT.
    cached_common = sys.modules.pop("common", None)
    cached_pdf_integrity = sys.modules.pop("pdf_integrity", None)
    sys.path.insert(0, str(manual_mirror / "scripts"))
    try:
        mirrored = _load(
            "assemble_manuel_math_mirror",
            manual_mirror / "scripts" / "assemble_manuel.py",
            manual_mirror / "scripts",
        )
        assert mirrored.ROOT == manual_mirror, mirrored.ROOT
    finally:
        sys.modules.pop("common", None)
        sys.modules.pop("pdf_integrity", None)
        if cached_common is not None:
            sys.modules["common"] = cached_common
        if cached_pdf_integrity is not None:
            sys.modules["pdf_integrity"] = cached_pdf_integrity
    # Le miroir n'est pas un dépôt Git : on lui fournit la même vue de
    # fichiers suivis (l'arbre logique est identique, seul le chemin absolu
    # change — c'est précisément la variable testée).
    tracked = math_assembler.load_tracked_paths(ROOT)
    try:
        master = mirrored.render_master(
            "eleve",
            "0" * 32,
            manual="TEXPERTES",
            git_root=mirror_root,
            tracked_paths=tracked,
        )
    finally:
        sys.modules.pop("assemble_manuel_math_mirror", None)
        sys.path[:] = [p for p in sys.path if str(manual_mirror) not in p]
    match = TRAILER_ID_RE.search(master)
    assert match is not None
    assert match.group(1) == reference, (
        "l'identité dépend du chemin absolu du worktree"
    )


def test_pdf10_producer_schema_version_is_part_of_the_preimage() -> None:
    """§4 — le contrat couvre une évolution du producteur hors master/gabarits."""
    for script in (
        MATH_SCRIPTS / "pdf_reproducibility.py",
        NSI_SCRIPTS / "assemble.py",
    ):
        source = script.read_text(encoding="utf-8")
        assert "PDF_TRAILER_PRODUCER_SCHEMA_VERSION" in source, script.name
        assert 'f"producer_schema_version=' in source, script.name
