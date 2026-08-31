"""Une capacite se resout par egalite, jamais par ressemblance.

`C1` seul ne designe rien : chaque chapitre de la collection en possede un.
Le defaut repare ici extrayait un jeton local d'une reference pleinement
qualifiee -- `TSPE-CONCLGN-C1` lu comme `C1` -- et faisait ainsi crediter le
contenu d'une capacite a sa voisine.

Ces tests verifient la resolution dans les DEUX sens, parce que les deux
erreurs coutent aussi cher :

* ne pas resoudre ce qui existe fabrique une lacune, et envoie reecrire du
  contenu qui va tres bien ;
* resoudre vers la mauvaise capacite fabrique un credit, et laisse une
  capacite reellement vide passer pour servie.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def module():
    spec = importlib.util.spec_from_file_location(
        "capacity_identity", ROOT / "scripts/capacity_identity.py"
    )
    assert spec and spec.loader
    loaded = importlib.util.module_from_spec(spec)
    # `@dataclass` lit le module de la classe : sans enregistrement prealable
    # dans sys.modules, la resolution echoue a l'import.
    sys.modules[spec.name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


def _corpus(tmp_path: Path, chapters: dict[str, dict]) -> tuple[Path, ...]:
    root = tmp_path / "chapitres"
    root.mkdir(parents=True, exist_ok=True)
    for name, document in chapters.items():
        directory = root / name
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "contrat.yaml").write_text(
            yaml.safe_dump(document, allow_unicode=True), encoding="utf-8"
        )
    return (root,)


# -- A. le meme code local dans deux chapitres est deux capacites ------------


def test_the_same_local_code_in_two_chapters_is_two_capacities(module, tmp_path):
    corpora = _corpus(
        tmp_path,
        {
            "TSPE-CHAPITRE-A": {"capacites": [{"code": "C1", "ref_capacite": "A-C1"}]},
            "TSPE-CHAPITRE-B": {"capacites": [{"code": "C1", "ref_capacite": "B-C1"}]},
        },
    )
    resolver = module.CapacityIdentityResolver.from_corpora(corpora)
    left = resolver.resolve("TSPE-CHAPITRE-A", "C1").identity
    right = resolver.resolve("TSPE-CHAPITRE-B", "C1").identity

    assert left != right
    assert left.uid != right.uid
    assert left.local_code == right.local_code == "C1"


def test_a_local_code_never_resolves_outside_its_chapter(module, tmp_path):
    """La portee d'un code local est son chapitre, jamais la collection."""

    corpora = _corpus(
        tmp_path,
        {
            "TSPE-CHAPITRE-A": {"capacites": [{"code": "C1", "ref_capacite": "A-C1"}]},
            "TSPE-CHAPITRE-B": {"capacites": [{"code": "C9", "ref_capacite": "B-C9"}]},
        },
    )
    resolver = module.CapacityIdentityResolver.from_corpora(corpora)
    with pytest.raises(module.UnresolvedCapacityIdentity):
        resolver.resolve("TSPE-CHAPITRE-B", "C1")


# -- B. le cas prouve : une reference vers un AUTRE chapitre -----------------


def test_a_reference_into_another_chapter_never_credits_the_local_twin(
    module, tmp_path
):
    """Le defaut fondateur, reduit a sa plus simple expression.

    `TSPE-PROBABILITES` possede une capacite locale `C10` dont la reference
    officielle est `TSPE-CONCLGN-C1`, et possede par ailleurs un `C1`. Lire
    la reference comme `C1` donnait a la capacite voisine le credit d'un
    contenu qui ne la sert pas.
    """

    corpora = _corpus(
        tmp_path,
        {
            "TSPE-PROBABILITES": {
                "capacites": [
                    {"code": "C1", "ref_capacite": "TSPE-PROBA-C1"},
                    {"code": "C10", "ref_capacite": "TSPE-CONCLGN-C1"},
                ]
            }
        },
    )
    resolver = module.CapacityIdentityResolver.from_corpora(corpora)

    resolution = resolver.resolve("TSPE-PROBABILITES", "TSPE-CONCLGN-C1")
    assert resolution.rule == module.REF_EXACT
    assert resolution.identity.local_code == "C10", (
        "la reference designe C10 ; la lire comme C1 vole le credit du voisin"
    )
    assert resolver.resolve("TSPE-PROBABILITES", "C1").identity.local_code == "C1"


# -- C. l'alias officiel ne vaut que si le contrat l'etablit -----------------


def test_an_official_reference_resolves_only_where_the_contract_declares_it(
    module, tmp_path
):
    corpora = _corpus(
        tmp_path,
        {
            "1NSI-AVEC-ALIAS": {
                "capacites": [{"code": "C1", "ref_capacite": "P-ALGO-01A"}]
            },
            "1NSI-SANS-ALIAS": {
                "capacites": [{"code": "C1", "ref_capacite": "P-AUTRE-99"}]
            },
        },
    )
    resolver = module.CapacityIdentityResolver.from_corpora(corpora)

    assert (
        resolver.resolve("1NSI-AVEC-ALIAS", "P-ALGO-01A").identity.local_code == "C1"
    )
    # Le meme alias dans un chapitre qui ne le declare pas ne resout pas.
    with pytest.raises(module.UnresolvedCapacityIdentity):
        resolver.resolve("1NSI-SANS-ALIAS", "P-ALGO-01A")


# -- D. meme suffixe, references differentes : capacites distinctes ----------


def test_two_references_sharing_a_suffix_stay_distinct(module, tmp_path):
    corpora = _corpus(
        tmp_path,
        {
            "TNSI-CHAPITRE": {
                "capacites": [
                    {"code": "C1", "ref_capacite": "P-STRUCT-C3"},
                    {"code": "C2", "ref_capacite": "P-ALGO-C3"},
                ]
            }
        },
    )
    resolver = module.CapacityIdentityResolver.from_corpora(corpora)

    assert resolver.resolve("TNSI-CHAPITRE", "P-STRUCT-C3").identity.local_code == "C1"
    assert resolver.resolve("TNSI-CHAPITRE", "P-ALGO-C3").identity.local_code == "C2"
    # Le suffixe partage `C3` n'est le code local d'aucune des deux.
    with pytest.raises(module.UnresolvedCapacityIdentity):
        resolver.resolve("TNSI-CHAPITRE", "C3")


# -- E. toute ambiguite echoue, elle ne se tranche pas -----------------------


def test_a_reference_shared_by_two_capacities_fails_closed(module, tmp_path):
    corpora = _corpus(
        tmp_path,
        {
            "TSPE-AMBIGU": {
                "capacites": [
                    {"code": "C1", "ref_capacite": "PARTAGEE"},
                    {"code": "C2", "ref_capacite": "PARTAGEE"},
                ]
            }
        },
    )
    with pytest.raises(module.AmbiguousCapacityIdentity):
        module.CapacityIdentityResolver.from_corpora(corpora)


def test_a_reference_that_is_also_a_local_code_fails_closed(module, tmp_path):
    """Sinon la meme chaine resoudrait vers deux capacites differentes."""

    corpora = _corpus(
        tmp_path,
        {
            "TSPE-COLLISION": {
                "capacites": [
                    {"code": "C1", "ref_capacite": "REF-C1"},
                    {"code": "C2", "ref_capacite": "C1"},
                ]
            }
        },
    )
    with pytest.raises(module.AmbiguousCapacityIdentity):
        module.CapacityIdentityResolver.from_corpora(corpora)


def test_an_unknown_string_never_resolves_to_a_best_effort(module, tmp_path):
    corpora = _corpus(
        tmp_path, {"TSPE-X": {"capacites": [{"code": "C1", "ref_capacite": "X-C1"}]}}
    )
    resolver = module.CapacityIdentityResolver.from_corpora(corpora)
    for unknown in ("C2", "X-C2", "P-ALGO-01A", "", "  "):
        with pytest.raises(module.CapacityIdentityError):
            resolver.resolve("TSPE-X", unknown)


# -- normalisation : le qualifiant n'est jamais retire -----------------------


def test_normalisation_only_trims_whitespace(module):
    assert module.normalise("  C1 ") == "C1"
    assert module.normalise("TSPE-CONCLGN-C1") == "TSPE-CONCLGN-C1"
    assert module.normalise("c1") == "c1", "la casse n'est pas normalisee"


# -- la collection reelle se resout entierement -----------------------------


def test_the_whole_collection_resolves_without_unknown(module):
    """UNKNOWN = 0 sur le corpus reel, sans aucune inference lexicale."""

    clone = importlib.util.spec_from_file_location(
        "p0_clone_ledger", ROOT / "scripts/build_p0_content_clone_ledger.py"
    )
    ledger = importlib.util.module_from_spec(clone)
    clone.loader.exec_module(ledger)

    resolver = module.CapacityIdentityResolver.from_corpora()
    unresolved: list[tuple[str, str]] = []
    declarations: list[tuple[str, str]] = []
    visited_sources: set[Path] = set()
    expected_sources = {
        path
        for corpus in module.CORPORA
        if corpus.is_dir()
        for path in corpus.rglob("*.tex")
        if not any(part in module.UNPUBLISHED for part in path.parts)
        and path.parts[path.parts.index("chapitres") + 1] in resolver.chapters
    }
    for corpus in module.CORPORA:
        if not corpus.is_dir():
            continue
        for path in corpus.rglob("*.tex"):
            if any(part in module.UNPUBLISHED for part in path.parts):
                continue
            chapter = path.parts[path.parts.index("chapitres") + 1]
            if chapter not in resolver.chapters:
                continue
            visited_sources.add(path)
            meta = ledger.read_meta(path.read_text(encoding="utf-8", errors="replace"))
            raws = {
                module.normalise(value)
                for key in ("capacites_codes", "capacites")
                for value in (meta.get(key) or [])
            }
            for raw in raws:
                declarations.append((chapter, raw))

    for chapter, raw in declarations:
        try:
            resolver.resolve(chapter, raw)
        except module.CapacityIdentityError:
            unresolved.append((chapter, raw))

    assert visited_sources == expected_sources
    assert declarations, "le corpus doit etre reellement parcouru"
    assert unresolved == [], f"declarations non resolues: {unresolved[:10]}"


def test_the_alias_map_is_one_to_one_and_committed(module):
    payload = module.build_alias_map()
    uids = [row["canonical_uid"] for row in payload["entries"]]
    assert len(set(uids)) == len(uids) == payload["count"]

    # Un alias officiel ne peut designer deux capacites d'un meme chapitre.
    by_chapter: dict[str, set[str]] = {}
    for row in payload["entries"]:
        if not row["official_ref"]:
            continue
        seen = by_chapter.setdefault(row["chapter"], set())
        assert row["official_ref"] not in seen, row
        seen.add(row["official_ref"])

    assert module.main(["--check"]) == 0
