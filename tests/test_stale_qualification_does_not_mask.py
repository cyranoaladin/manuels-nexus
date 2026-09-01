"""Une qualification perimee bloque, mais n'aveugle pas la campagne.

Defaut d'origine : `_load_dispositions` LEVAIT des la premiere qualification
derivee dont l'objet avait change. La construction de l'inventaire s'arretait
la, et les gates ne rapportaient plus qu'un unique motif,
`recalcul_impossible`. Les 86 fiches methode perimees par la campagne
diacritiques ne s'ajoutaient donc pas aux blockers existants : elles les
MASQUAIENT tous. Une campagne publish-ready ne peut pas se piloter ainsi.

Contrat retenu :

- une qualification invalide est ECARTEE, jamais levee ;
- l'anomalie qu'elle couvrait redevient une dette ouverte et bloquante, donc
  le comportement reste fail-closed ;
- son motif exact reste visible A COTE des autres blockers ;
- `InventoryError` demeure pour ce qui est illisible : schema absent,
  controle versionne invalide, donnees non analysables.
"""

from __future__ import annotations

import shutil
import sys
import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import baseline_qualification as _baseline_qualification  # noqa: E402
import inventory_collection as I  # noqa: E402

SCHEMA = "audit/schemas/v1/anomaly-dispositions.schema.json"
POLICY = "audit/A4_METHOD_REVIEW_DEBT_POLICY.md"


def _minimal_root(tmp_path: Path, records: dict[str, dict]) -> Path:
    """Racine portant le strict necessaire a `_load_dispositions`."""

    (tmp_path / "audit/schemas/v1").mkdir(parents=True)
    shutil.copy(ROOT / SCHEMA, tmp_path / SCHEMA)
    shutil.copy(ROOT / POLICY, tmp_path / POLICY)
    payload = {
        "artifact_type": "anomaly_dispositions",
        "dispositions": records,
        "fingerprint_schema_version": 1,
        "schema_ref": SCHEMA,
        "schema_version": 1,
    }
    # Le controle porte son propre condense : le calculer plutot que
    # l'inventer, sans quoi la fixture serait rejetee avant d'atteindre le
    # comportement teste.
    payload["control_digest"] = I._control_digest(payload)
    (tmp_path / "audit/ANOMALY_DISPOSITIONS.yaml").write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=True),
        encoding="utf-8",
    )
    return tmp_path


#: Les enregistrements reels servent de gabarit : le schema exige une quinzaine
#: de champs obligatoires, et une fixture inventee a la main divergerait du
#: contrat au premier changement de schema.
_REELLES = yaml.safe_load(
    (ROOT / "audit/ANOMALY_DISPOSITIONS.yaml").read_text(encoding="utf-8")
)["dispositions"]


def _renumerote(record: dict, fingerprint: str) -> dict:
    copie = {**record, "fingerprint": fingerprint}
    copie["qualification_digest"] = _baseline_qualification.qualification_digest(copie)
    return copie


def _healthy(fingerprint: str) -> dict:
    """Disposition historique reelle, sans lien avec une fiche methode."""

    modele = next(
        record
        for record in _REELLES.values()
        if not record.get("method_source_sha")
        and record.get("decision_ref") != I.A4_METHOD_REVIEW_DEBT_DECISION_REF
    )
    return _renumerote(modele, fingerprint)


def _a4_bound_to_missing_method(fingerprint: str) -> dict:
    """Qualification A4 reelle, repointee vers une fiche introuvable."""

    modele = next(
        record
        for record in _REELLES.values()
        if record.get("decision_ref") == I.A4_METHOD_REVIEW_DEBT_DECISION_REF
    )
    repointe = {
        **modele,
        "source": (
            "Mathematiques/manuel-maths/chapitres/ABSENT/methodes/ABSENT.tex"
        ),
    }
    return _renumerote(repointe, fingerprint)


# -- Une invalide parmi N saines : les N restent visibles ---------------------


def test_one_invalid_qualification_never_hides_the_others(tmp_path: Path) -> None:
    saines = {f"{index:016x}": _healthy(f"{index:016x}") for index in range(1, 6)}
    invalide = "f" * 16
    root = _minimal_root(
        tmp_path, {**saines, invalide: _a4_bound_to_missing_method(invalide)}
    )

    signalees = I.invalid_qualifications(root)
    applicables = I._load_dispositions(root)

    assert len(signalees) == 1, "l'invalide doit etre signalee, pas levee"
    assert signalees[0]["fingerprint"] == invalide
    assert set(applicables) == set(saines) | {invalide}, (
        "la disposition reste sur le disque : seule son application est suspendue"
    )


def test_the_loader_no_longer_raises_on_an_invalid_qualification(
    tmp_path: Path,
) -> None:
    invalide = "f" * 16
    root = _minimal_root(tmp_path, {invalide: _a4_bound_to_missing_method(invalide)})

    assert set(I._load_dispositions(root)) == {invalide}
    assert len(I.invalid_qualifications(root)) == 1


def test_unreadable_control_still_raises(tmp_path: Path) -> None:
    """RECALCUL_IMPOSSIBLE reste reserve a ce qui est vraiment illisible."""

    root = _minimal_root(tmp_path, {"a" * 16: _healthy("a" * 16)})
    (root / SCHEMA).unlink()

    with pytest.raises(I.InventoryError):
        I._load_dispositions(root)


# -- Sur le depot reel : toutes les perimees ET les autres blockers ----------


def test_the_repository_reports_every_stale_qualification(tmp_path: Path) -> None:
    invalides = I.invalid_qualifications(ROOT)

    # Le compte suit le corpus : il monte des qu'une fiche qualifiee de plus
    # est modifiee. Ce qui est verrouille, c'est qu'AUCUNE peremption ne soit
    # tue -- toutes portent le motif, et chaque empreinte n'apparait qu'une
    # fois.
    assert invalides, "le depot en porte, et le gate doit les voir"
    assert all(
        any("STALE" in violation for violation in entry["violations"])
        for entry in invalides
    ), "toutes portent le motif de peremption, aucune n'est un autre defaut"
    assert len({entry["fingerprint"] for entry in invalides}) == len(invalides)

    queue = json.loads(
        (ROOT / "audit/METHOD_REQUALIFICATION_QUEUE.json").read_text(encoding="utf-8")
    )
    assert (
        len(invalides)
        == queue["totals"]["stale_requiring_human_requalification"]
    )


def test_the_check_gate_shows_stale_and_other_blockers_together() -> None:
    """Le test de non-masquage : toutes les perimees restent visibles."""

    reasons = I._invalid_qualification_reasons(ROOT)
    stale = [reason for reason in reasons if reason.startswith("qualification_invalide:")]

    assert len(stale) == len(I.invalid_qualifications(ROOT))
    assert len(stale) == len(reasons), "aucun motif etranger dans ce lot"


def test_the_inventory_is_computable_despite_the_stale_qualifications() -> None:
    """L'aveuglement corrige : l'inventaire se construit malgre les 86."""

    inventory = I.build_inventory(ROOT)

    assert inventory["manuals"], "l'inventaire doit etre reellement peuple"
