"""Une re-liaison accentuelle doit refuser tout ce qui n'est pas un accent.

La décision humaine autorise à re-lier une qualification au texte courant
lorsque SEULE l'accentuation a changé. Ces tests vérifient que le producteur
sait dire non : un nombre, une formule, un opérateur, une ligne de code, un
exemple, une phrase, une capacité, la META substantielle ou un oracle
modifiés doivent tous faire sortir l'objet du lot.

`ACCENT_ONLY_REBIND_FALSE_ACCEPTANCE` est le nombre de mutations
substantielles acceptées à tort. Il doit valoir zéro.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_trigo_accent_rebind as rebind  # noqa: E402

CIBLE = ROOT / "Mathematiques/manuel-maths/chapitres/1SPE-TRIGONOMETRIE/methodes/1SPE-TRIGO-ME-003.tex"
OBJET = "1SPE-TRIGO-ME-003"


def _couverts(verdict: dict) -> set[str]:
    return {entree["object_id"] for entree in verdict["covered"]}


def _refus(verdict: dict, object_id: str) -> list[str]:
    for entree in verdict["excluded"]:
        if entree["object_id"] == object_id:
            return entree["refus"]
    return []


class _Mutation:
    """Applique une mutation au fichier, puis le restitue à l'octet près."""

    def __init__(self, avant: str, apres: str) -> None:
        self.avant, self.apres = avant, apres
        self.origine = CIBLE.read_bytes()

    def __enter__(self) -> dict:
        texte = self.origine.decode("utf-8")
        assert self.avant in texte, f"motif absent : {self.avant!r}"
        CIBLE.write_text(texte.replace(self.avant, self.apres, 1), encoding="utf-8")
        return rebind.assess()

    def __exit__(self, *_: object) -> None:
        CIBLE.write_bytes(self.origine)


# ══════════════════════════════════════════════════════════════════════════
# L'état courant : la re-liaison est faite, il n'y a plus rien à re-lier
# ══════════════════════════════════════════════════════════════════════════
def test_after_the_rebind_there_is_nothing_left_to_rebind() -> None:
    """État terminal sain : la qualification porte sur le texte courant."""
    verdict = rebind.assess()
    assert verdict["covered"] == []
    for entree in verdict["excluded"]:
        assert entree["recomputed_change_class"] == "UNCHANGED"
        assert any("rien à re-lier" in motif for motif in entree["refus"])


def test_the_deposited_receipt_carries_the_mandated_fields() -> None:
    receipt = json.loads(
        (ROOT / "audit/TRIGO_ACCENT_REBIND_RECEIPT.json").read_text(encoding="utf-8")
    )
    for champ in (
        "REVIEWER_IDENTITY", "DECISION", "OBJECT_IDS",
        "OLD_QUALIFICATION_FINGERPRINTS", "NEW_QUALIFICATION_FINGERPRINTS",
        "ACCENT_ONLY_FORENSICS_DIGEST", "PEDAGOGICAL_CONTENT_UNCHANGED",
    ):
        assert champ in receipt, champ
    assert receipt["DECISION"] == "ACCEPT_ACCENT_ONLY_QUALIFICATION_REBIND"
    assert receipt["REVIEWER_IDENTITY"] == "abenrhouma"
    assert receipt["PEDAGOGICAL_CONTENT_UNCHANGED"] is True
    assert receipt["OBJECT_IDS"] == list(rebind.AUTHORIZED_OBJECT_IDS)
    assert len(receipt["OLD_QUALIFICATION_FINGERPRINTS"]) == 3
    assert receipt["OLD_QUALIFICATION_FINGERPRINTS"] != receipt[
        "NEW_QUALIFICATION_FINGERPRINTS"
    ]


def test_the_chain_is_bound_to_the_current_text() -> None:
    """Packet, décision et disposition doivent dire la même empreinte."""
    import hashlib

    import yaml

    decision = json.loads(rebind.DECISION_JSON.read_text(encoding="utf-8"))
    dispositions = yaml.safe_load(
        (ROOT / "audit/ANOMALY_DISPOSITIONS.yaml").read_text(encoding="utf-8")
    )["dispositions"]
    par_objet = {
        str(record.get("object_id")): record
        for record in dispositions.values()
        if str(record.get("object_id")) in rebind.AUTHORIZED_OBJECT_IDS
    }
    for objet in decision["objects"]:
        source = ROOT / objet["source_path"]
        observe = hashlib.sha256(source.read_bytes()).hexdigest()
        assert objet["current_source_sha"] == observe, objet["object_id"]
        packet = ROOT / objet["current_packet_path"]
        assert json.loads(packet.read_text(encoding="utf-8"))[
            "current_source_sha"
        ] == observe
        assert hashlib.sha256(packet.read_bytes()).hexdigest() == objet[
            "current_packet_sha256"
        ]
        record = par_objet[objet["object_id"]]
        assert record["method_source_sha"] == observe
        assert record["review_packet_sha"] == objet["current_packet_sha256"]


def test_the_rebind_promoted_nothing() -> None:
    """§1 : les quatre revues restent PENDING, la dette reste bloquante."""
    decision = json.loads(rebind.DECISION_JSON.read_text(encoding="utf-8"))
    assert decision["review_state"] == "PENDING"
    assert decision["required_reviews"] == {
        "scientific": "PENDING", "pedagogical": "PENDING",
        "editorial": "PENDING", "variant": "PENDING",
    }
    assert decision["content_approval"] is False
    assert decision["release_blocking"] is True
    assert decision["source_status"] == "needs_review"
    assert decision["invalidate_on_source_change"] is True
    for objet in decision["objects"]:
        meta = json.loads(
            (ROOT / objet["source_path"]).read_text(encoding="utf-8").split("\n", 1)[0][8:]
        )
        assert meta["status"] == "needs_review"


def test_no_object_outside_the_three_can_inherit() -> None:
    """§2 : un objet non nommé ne peut pas hériter de cette autorisation."""
    assert rebind.AUTHORIZED_OBJECT_IDS == (
        "1SPE-TRIGO-ME-003", "1SPE-TRIGO-ME-004", "1SPE-TRIGO-ME-005",
    )
    receipt = json.loads(
        (ROOT / "audit/TRIGO_ACCENT_REBIND_RECEIPT.json").read_text(encoding="utf-8")
    )
    faux = dict(receipt, OBJECT_IDS=[*receipt["OBJECT_IDS"], "1SPE-TRIGO-ME-006"])
    assert any("hors périmètre" in v for v in rebind.validate_receipt(faux))


def test_an_applied_receipt_cannot_be_replayed() -> None:
    """La re-liaison n'est pas rejouable : le recalcul ne retrouve plus le lot."""
    receipt = json.loads(
        (ROOT / "audit/TRIGO_ACCENT_REBIND_RECEIPT.json").read_text(encoding="utf-8")
    )
    violations = rebind.validate_receipt(receipt)
    assert any("recalcul" in v for v in violations)
    menteur = dict(receipt, ACCENT_ONLY_FORENSICS_DIGEST="sha256:" + "0" * 64)
    assert any("forensics" in v for v in rebind.validate_receipt(menteur))


# ══════════════════════════════════════════════════════════════════════════
# Les mutations : chacune doit faire sortir l'objet du lot
# ══════════════════════════════════════════════════════════════════════════
MUTATIONS = {
    "un nombre": (
        "$\\cos a = \\dfrac{3}{5}$", "$\\cos a = \\dfrac{4}{5}$",
    ),
    "une formule": (
        "$\\cos(a+b) = \\cos a\\cos b - \\sin a\\sin b$",
        "$\\cos(a+b) = \\cos a\\cos b + \\sin a\\sin b$",
    ),
    "un operateur": (
        "$\\sin(2a) = 2\\sin a\\cos a$", "$\\sin(2a) = 2\\sin a + \\cos a$",
    ),
    "une ligne de code": (
        "% assert simplify(expand_trig(sin(2*a)) - 2*sin(a)*cos(a)) == 0",
        "% assert simplify(expand_trig(sin(2*a)) - 3*sin(a)*cos(a)) == 0",
    ),
    "un exemple": (
        "$\\frac{\\pi}{12} = \\frac{\\pi}{3} - \\frac{\\pi}{4}$",
        "$\\frac{\\pi}{12} = \\frac{\\pi}{6} - \\frac{\\pi}{4}$",
    ),
    "une phrase": (
        "les lignes\n      trigonométriques ne sont PAS lineaires.",
        "les lignes\n      trigonométriques sont lineaires.",
    ),
    "une capacite": (
        '"methodes": ["M3"]', '"methodes": ["M4"]',
    ),
    "la META substantielle": (
        '"programme_alignment": "OPTIONAL_EXTENSION"',
        '"programme_alignment": "MANDATORY"',
    ),
    "un oracle": (
        "% assert sa**2 + ca**2 == 1", "% assert sa**2 + ca**2 == 2",
    ),
}


@pytest.mark.parametrize("nature", sorted(MUTATIONS))
def test_a_substantive_mutation_is_refused(nature: str) -> None:
    avant, apres = MUTATIONS[nature]
    with _Mutation(avant, apres) as verdict:
        assert OBJET not in _couverts(verdict), nature
        assert _refus(verdict, OBJET), nature


def test_false_acceptance_is_zero() -> None:
    """`ACCENT_ONLY_REBIND_FALSE_ACCEPTANCE` = 0, mesuré et non affirmé."""
    fausses_acceptations = 0
    for nature, (avant, apres) in sorted(MUTATIONS.items()):
        with _Mutation(avant, apres) as verdict:
            if OBJET in _couverts(verdict):
                fausses_acceptations += 1
    assert fausses_acceptations == 0


def test_a_genuine_accent_correction_is_accepted() -> None:
    """Le refus doit venir de la mutation, pas d'un producteur qui dit non à tout."""
    # `lineaires` est réellement sans accent dans la fiche : le corriger est
    # exactement le geste que la décision couvre.
    with _Mutation("PAS lineaires", "PAS linéaires") as verdict:
        assert OBJET in _couverts(verdict)
        entree = next(e for e in verdict["covered"] if e["object_id"] == OBJET)
        assert entree["recomputed_change_class"] == "ACCENT_ONLY"
        assert entree["meta_identical"] is True
        assert entree["verify_blocks_identical"] is True


def test_a_promoted_status_is_refused() -> None:
    """Re-lier ne promeut rien : un `approved` fait sortir l'objet du lot."""
    with _Mutation('"status": "needs_review"', '"status": "approved"') as verdict:
        assert OBJET not in _couverts(verdict)
        assert any("promeut" in motif for motif in _refus(verdict, OBJET))


def test_the_decision_substance_must_stay_intact() -> None:
    """Si une revue cessait d'être PENDING, plus rien ne serait re-liable."""
    chemin = rebind.DECISION_JSON
    origine = chemin.read_bytes()
    try:
        decision = json.loads(origine.decode("utf-8"))
        decision["required_reviews"]["scientific"] = "DONE"
        chemin.write_text(json.dumps(decision, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        verdict = rebind.assess()
        assert verdict["covered"] == []
        assert all(
            any("PENDING" in motif for motif in entree["refus"])
            for entree in verdict["excluded"]
        )
    finally:
        chemin.write_bytes(origine)
