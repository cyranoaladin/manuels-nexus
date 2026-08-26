#!/usr/bin/env python3
"""Build an independent second-pass atomization of official source segments."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import shutil
import tempfile
from collections import Counter, defaultdict
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
SOURCE_SEGMENTS_PATH = AUDIT / "OFFICIAL_SOURCE_SEGMENTS_2026_2027.json"
FIRST_PASS_ATOMS_PATH = AUDIT / "OFFICIAL_PROGRAM_ATOMS_2026_2027.json"
AUTHORITY_PATH = AUDIT / "OFFICIAL_PROGRAM_AUTHORITY_2026_2027.yaml"
SEGMENT_LEDGER_JSON = AUDIT / "OFFICIAL_SOURCE_SEGMENT_LEDGER.json"
SEGMENT_LEDGER_MD = AUDIT / "OFFICIAL_SOURCE_SEGMENT_LEDGER.md"
SECOND_PASS_JSON = AUDIT / "OFFICIAL_ATOMIZATION_SECOND_PASS.json"
SECOND_PASS_MD = AUDIT / "OFFICIAL_ATOMIZATION_SECOND_PASS.md"
SCHOOL_YEAR = "2026-2027"
MANUAL_ORDER = ("1SPE", "TSPE", "TCOMPL", "TEXPERTES", "1NSI", "TNSI")
FINDING_CODES = (
    "MANDATORY_SEGMENT_UNREPRESENTED",
    "PHANTOM_ATOM",
    "PHANTOM_NON_ATOM_DISPOSITION",
    "DUPLICATE_ATOM",
    "AMBIGUOUS_ATOM",
    "WRONG_YEAR_ATOM",
    "MANDATORY_CLASSIFICATION_DISAGREEMENT",
    "ATOM_MANUAL_DISAGREEMENT",
    "ATOM_TYPE_DISAGREEMENT",
    "ATOM_WORDING_DISAGREEMENT",
    "ATOM_JUSTIFICATION_DISAGREEMENT",
    "NON_ATOM_MANUAL_DISAGREEMENT",
    "NON_ATOM_CLASSIFICATION_DISAGREEMENT",
    "NON_ATOM_MANDATORY_DISAGREEMENT",
    "NON_ATOM_JUSTIFICATION_DISAGREEMENT",
)

DEFAULT_ATOM_TYPES = {
    ("ALGORITHMS", "NO"): "IMPLEMENTATION_GUIDANCE",
    ("ALGORITHMS", "YES"): "MANDATORY_ALGORITHM",
    ("AUTOMATISMS", "YES"): "MANDATORY_SKILL",
    ("CONTENTS", "YES"): "MANDATORY_KNOWLEDGE",
    ("EXPECTED_CAPACITIES", "YES"): "MANDATORY_CAPACITY",
    ("EXPLICIT_LIMITATIONS", "NO"): "EXPLICIT_LIMITATION",
    ("EXPLICIT_LIMITATIONS", "YES"): "MANDATORY_CAPACITY",
    ("HISTORY_CONTEXT", "NO"): "HISTORY_CONTEXT",
    ("IMPLEMENTATION_GUIDANCE", "NO"): "IMPLEMENTATION_GUIDANCE",
    ("IMPLEMENTATION_GUIDANCE", "YES"): "IMPLEMENTATION_GUIDANCE",
    ("MANDATORY_PROOFS", "NO"): "IMPLEMENTATION_GUIDANCE",
    ("MANDATORY_PROOFS", "YES"): "MANDATORY_SKILL",
    ("OPTIONAL_EXTENSIONS", "NO"): "OPTIONAL_EXTENSION",
    ("OTHER_OFFICIAL", "YES"): "OTHER_EXPLICIT",
}

# Keys are (manual, segment, anchor, exact source-wording digest).  These
# source-locked overrides resolve the few cases where a broad source role does
# not by itself determine the atom's semantic type.
ATOM_TYPE_EXCEPTIONS = {
    (
        "TCOMPL",
        "TCOMPL-SOURCE-SEG-173",
        "lines:775",
        "sha256:6c155328c668ef16f718a5db3db31b6b0793d7512c33fb4a077c443b090c3c75",
    ): "MANDATORY_CAPACITY",
    (
        "TCOMPL",
        "TCOMPL-SOURCE-SEG-174",
        "lines:776",
        "sha256:2a974a935945bc9f2f11099356b3eaf31b436bc79f6ef5f7cc78bb2f1ef8534b",
    ): "MANDATORY_CAPACITY",
    (
        "TCOMPL",
        "TCOMPL-SOURCE-SEG-175",
        "lines:777-778",
        "sha256:d6c964287765dbabb446adab32792d00f7e3645a4b373edaa9cd00dfff0425e7",
    ): "MANDATORY_CAPACITY",
    (
        "TCOMPL",
        "TCOMPL-SOURCE-SEG-176",
        "lines:779-780",
        "sha256:37e70c59d5a619e1bb9bc6bc631835ebfa07e33674b81e41aaf5a2d6146ab366",
    ): "MANDATORY_CAPACITY",
    (
        "TEXPERTES",
        "TEXPERTES-SOURCE-SEG-062",
        "lines:532",
        "sha256:82459351fdda647181df3d0f13deef465500d1c42b95e388af3d227b034c173b",
    ): "MANDATORY_ALGORITHM",
    (
        "1NSI",
        "1NSI-SOURCE-SEG-138",
        "pdf-page:2;lines:28-31",
        "sha256:b078df200f4efe7c05b62e9fa16522e9ce111bbddce208b019fbbab55b173f90",
    ): "IMPLEMENTATION_GUIDANCE",
}

CANONICAL_JUSTIFICATIONS = {
    ("1SPE", "ALGORITHMS", "IMPLEMENTATION_GUIDANCE"): "Exemple algorithmique officiel de mise en œuvre, hors contenus et capacités attendues : guide pédagogique non obligatoire pour la couverture.",
    ("1SPE", "ALGORITHMS", "MANDATORY_ALGORITHM"): "Unité algorithmique explicitement requise par le texte officiel, distincte des simples exemples de mise en œuvre.",
    ("1SPE", "AUTOMATISMS", "MANDATORY_SKILL"): "Unité publiée dans la liste officielle des automatismes : savoir-faire obligatoire et à entretenir pendant l’année.",
    ("1SPE", "CONTENTS", "MANDATORY_KNOWLEDGE"): "Unité directement extraite d’un bloc officiel de connaissances ou de contenus : obligatoire pour la couverture.",
    ("1SPE", "EXPECTED_CAPACITIES", "MANDATORY_CAPACITY"): "Unité directement extraite d’une capacité explicitement attendue par le programme : obligatoire pour la couverture.",
    ("1SPE", "EXPLICIT_LIMITATIONS", "EXPLICIT_LIMITATION"): "Limitation explicite du périmètre officiel : à tracer comme frontière réglementaire, sans créer une capacité obligatoire.",
    ("1SPE", "HISTORY_CONTEXT", "HISTORY_CONTEXT"): "Éclairage historique officiel : contexte culturel, non attendu obligatoire de couverture.",
    ("1SPE", "MANDATORY_PROOFS", "MANDATORY_SKILL"): "Unité publiée dans la rubrique officielle « Démonstrations » sans qualificatif facultatif : savoir-faire démonstratif obligatoire.",
    ("1SPE", "OPTIONAL_EXTENSIONS", "OPTIONAL_EXTENSION"): "Unité placée dans la rubrique officielle des approfondissements ou problèmes possibles : extension facultative, non obligatoire pour la couverture.",
    ("TSPE", "ALGORITHMS", "IMPLEMENTATION_GUIDANCE"): "Exemple algorithmique officiel de mise en œuvre, hors contenus et capacités attendues : guide pédagogique non obligatoire pour la couverture.",
    ("TSPE", "CONTENTS", "MANDATORY_KNOWLEDGE"): "Unité directement extraite d’un bloc officiel de connaissances ou de contenus : obligatoire pour la couverture.",
    ("TSPE", "EXPECTED_CAPACITIES", "MANDATORY_CAPACITY"): "Unité directement extraite d’une capacité explicitement attendue ou formulée comme objectif par le programme : obligatoire pour la couverture.",
    ("TSPE", "EXPLICIT_LIMITATIONS", "EXPLICIT_LIMITATION"): "Limitation explicite du périmètre officiel : à tracer comme frontière réglementaire, sans créer une capacité obligatoire.",
    ("TSPE", "HISTORY_CONTEXT", "HISTORY_CONTEXT"): "Éclairage historique officiel : contexte culturel, non attendu obligatoire de couverture.",
    ("TSPE", "MANDATORY_PROOFS", "MANDATORY_SKILL"): "Unité publiée dans la rubrique officielle « Démonstrations » sans qualificatif facultatif : savoir-faire démonstratif obligatoire.",
    ("TSPE", "OPTIONAL_EXTENSIONS", "OPTIONAL_EXTENSION"): "Unité placée dans la rubrique officielle des approfondissements ou problèmes possibles : extension facultative, non obligatoire pour la couverture.",
    ("TCOMPL", "ALGORITHMS", "IMPLEMENTATION_GUIDANCE"): "Rubrique « Exemple(s) d’algorithme(s) » : suggestion de mise en œuvre, non exigible comme capacité de couverture.",
    ("TCOMPL", "CONTENTS", "MANDATORY_CAPACITY"): "Rubrique « Capacités attendues » du programme applicable : capacité exigible pour la couverture.",
    ("TCOMPL", "CONTENTS", "MANDATORY_KNOWLEDGE"): "Rubrique « Contenus » du programme applicable : connaissance exigible pour la couverture.",
    ("TCOMPL", "EXPECTED_CAPACITIES", "MANDATORY_CAPACITY"): "Rubrique « Capacités attendues » du programme applicable : capacité exigible pour la couverture.",
    ("TCOMPL", "EXPLICIT_LIMITATIONS", "EXPLICIT_LIMITATION"): "Limitation explicite : elle borne le périmètre exigible sans créer une capacité obligatoire distincte.",
    ("TCOMPL", "IMPLEMENTATION_GUIDANCE", "IMPLEMENTATION_GUIDANCE"): "Indication officielle de mise en œuvre : elle guide l’enseignement sans constituer une capacité exigible distincte.",
    ("TCOMPL", "MANDATORY_PROOFS", "IMPLEMENTATION_GUIDANCE"): "Rubrique « Démonstration(s) possible(s) » : suggestion pédagogique, non exigible.",
    ("TCOMPL", "OPTIONAL_EXTENSIONS", "OPTIONAL_EXTENSION"): "Rubrique de problèmes possibles ou d’approfondissements : piste au choix, non exigible pour la couverture.",
    ("TCOMPL", "OTHER_OFFICIAL", "OTHER_EXPLICIT"): "Organisation réglementaire : les neuf thèmes d’étude doivent tous être abordés ; les problèmes possibles restent au choix du professeur.",
    ("TEXPERTES", "ALGORITHMS", "IMPLEMENTATION_GUIDANCE"): "Rubrique « Exemple(s) d’algorithme(s) » : suggestion de mise en œuvre, non exigible comme capacité de couverture.",
    ("TEXPERTES", "CONTENTS", "MANDATORY_ALGORITHM"): "L’algorithme d’Euclide figure dans les contenus exigibles ; il ne s’agit pas d’un simple exemple d’algorithme.",
    ("TEXPERTES", "CONTENTS", "MANDATORY_KNOWLEDGE"): "Rubrique « Contenus » du programme applicable : connaissance exigible pour la couverture.",
    ("TEXPERTES", "EXPECTED_CAPACITIES", "MANDATORY_CAPACITY"): "Rubrique « Capacités attendues » du programme applicable : capacité exigible pour la couverture.",
    ("TEXPERTES", "HISTORY_CONTEXT", "HISTORY_CONTEXT"): "Éclairage historique officiel : contexte culturel, non capacité exigible.",
    ("TEXPERTES", "MANDATORY_PROOFS", "MANDATORY_SKILL"): "Rubrique « Démonstration(s) » non qualifiée de possible : démonstration exigible.",
    ("TEXPERTES", "OPTIONAL_EXTENSIONS", "OPTIONAL_EXTENSION"): "Rubrique de problèmes possibles ou d’approfondissements : piste au choix, non exigible pour la couverture.",
    ("1NSI", "CONTENTS", "MANDATORY_KNOWLEDGE"): "Rubrique « Contenus » du tableau réglementaire ; connaissance obligatoire selon le ledger source et le PDF officiel.",
    ("1NSI", "EXPECTED_CAPACITIES", "MANDATORY_CAPACITY"): "Rubrique « Capacités attendues » du tableau réglementaire ; capacité obligatoire selon le ledger source et le PDF officiel.",
    ("1NSI", "EXPLICIT_LIMITATIONS", "EXPLICIT_LIMITATION"): "Limitation explicite de la colonne « Commentaires » ; borne réglementaire non comptée comme contenu obligatoire.",
    ("1NSI", "IMPLEMENTATION_GUIDANCE", "IMPLEMENTATION_GUIDANCE"): "Colonne « Commentaires » ; indication de mise en œuvre non incluse dans le dénominateur obligatoire.",
    ("1NSI", "OTHER_OFFICIAL", "IMPLEMENTATION_GUIDANCE"): "La démarche de projet impose explicitement de réserver au moins un quart de l’horaire ; obligation de mise en œuvre, non connaissance disciplinaire.",
    ("TNSI", "CONTENTS", "MANDATORY_KNOWLEDGE"): "Rubrique « Contenus » du tableau réglementaire ; connaissance obligatoire selon le ledger source et le PDF officiel.",
    ("TNSI", "EXPECTED_CAPACITIES", "MANDATORY_CAPACITY"): "Rubrique « Capacités attendues » du tableau réglementaire ; capacité obligatoire selon le ledger source et le PDF officiel.",
    ("TNSI", "EXPLICIT_LIMITATIONS", "EXPLICIT_LIMITATION"): "Limitation explicite de la colonne « Commentaires » ; borne réglementaire non comptée comme contenu obligatoire.",
    ("TNSI", "EXPLICIT_LIMITATIONS", "MANDATORY_CAPACITY"): "Colonne « Capacités attendues » : « sans formalisme théorique » borne la mise en œuvre, mais montrer l’indécidabilité du problème de l’arrêt demeure une capacité obligatoire.",
    ("TNSI", "IMPLEMENTATION_GUIDANCE", "IMPLEMENTATION_GUIDANCE"): "Colonne « Commentaires » ; indication de mise en œuvre non incluse dans le dénominateur obligatoire.",
}

CANONICAL_NON_ATOM_PROFILES = {
    ("1SPE", "CROSS_CUTTING_COMPETENCIES"): (
        "OTHER_EXPLICIT",
        "Compétence mathématique transversale du cadre général ; suivie comme framework, sans atom de couverture disciplinaire séparé.",
    ),
    ("1SPE", "IMPLEMENTATION_GUIDANCE"): (
        "IMPLEMENTATION_GUIDANCE",
        "Cadre transversal de mise en œuvre ou d’évaluation, sans contenu disciplinaire autonome à couvrir.",
    ),
    ("TSPE", "CROSS_CUTTING_COMPETENCIES"): (
        "OTHER_EXPLICIT",
        "Compétence mathématique transversale du cadre général ; suivie comme framework, sans atom de couverture disciplinaire séparé.",
    ),
    ("TSPE", "IMPLEMENTATION_GUIDANCE"): (
        "IMPLEMENTATION_GUIDANCE",
        "Cadre transversal de mise en œuvre ou d’évaluation, sans contenu disciplinaire autonome à couvrir.",
    ),
    ("TSPE", "ALGORITHMS"): (
        "OTHER_EXPLICIT",
        "Intertitre de rubrique capturé par l’extraction ; aucune disposition réglementaire atomique autonome.",
    ),
    ("TCOMPL", "CROSS_CUTTING_COMPETENCIES"): (
        "IMPLEMENTATION_GUIDANCE",
        "Compétence mathématique transversale du préambule : cadre général, non unité autonome de contenu ou de capacité.",
    ),
    ("TCOMPL", "ALGORITHMS"): (
        "OTHER_EXPLICIT",
        "Titre de rubrique capturé par l’extracteur : repère structurel, sans disposition réglementaire autonome.",
    ),
    ("TEXPERTES", "CROSS_CUTTING_COMPETENCIES"): (
        "IMPLEMENTATION_GUIDANCE",
        "Compétence mathématique transversale du préambule : cadre général, non unité autonome de contenu ou de capacité.",
    ),
    ("1NSI", "CROSS_CUTTING_COMPETENCIES"): (
        "OTHER_EXPLICIT",
        "Cadre transversal générique du préambule : orientation du programme, sans unité disciplinaire atomique distincte pour le dénominateur de couverture.",
    ),
    ("TNSI", "CROSS_CUTTING_COMPETENCIES"): (
        "OTHER_EXPLICIT",
        "Cadre transversal générique du préambule : orientation du programme, sans unité disciplinaire atomique distincte pour le dénominateur de couverture.",
    ),
}

JUSTIFICATION_EXCEPTIONS = {
    (
        "1NSI",
        "1NSI-SOURCE-SEG-074",
        "pdf-page:6;table:1;row:7;column:commentaires;item:1",
        "sha256:58f1aeb39ef708e9293bfc242f9b60ebc6a8d95adc0e819c44a18efb8920426c",
    ): "Colonne « Commentaires » : l’impératif « Discuter » pourrait sembler une capacité attendue, mais sa position réglementaire en fait une indication de mise en œuvre non obligatoire ; ambiguïté explicitement conservée.",
    (
        "TNSI",
        "TNSI-SOURCE-SEG-117",
        "pdf-page:2;lines:28-31",
        "sha256:f6bb464daa46081cdfcbddf6f48711adc6e20d1a80ed77346410edb73e0135cb",
    ): "La démarche de projet impose explicitement de réserver au moins un quart de l’horaire ; obligation de mise en œuvre, non connaissance disciplinaire.",
}

# The source extractor damaged or over-captured these eleven snippets.  No
# fuzzy matching is allowed: both the source identity and accepted paraphrase
# wording are digest locked.
PARAPHRASE_DIGESTS = {
    ("TCOMPL", "TCOMPL-SOURCE-SEG-172", "lines:773-774", "sha256:d2dab48927fbebdf269cbb3c72f8d5544f60c2fe487858008e716b8868f20344"): "sha256:04a39eac7f249a11c39a0515c0944526d9600a8586c4952a26f8508b776a0d88",
    ("TEXPERTES", "TEXPERTES-SOURCE-SEG-014", "lines:338", "sha256:716165dae13022e6bbc42dbb2bf3297362e9d2c3e92e41ce127eb175b95f2587"): "sha256:87e570715ccbcfad5f375944ac7d849e2e15403b3d613d441dcc91ed6c00d642",
    ("TEXPERTES", "TEXPERTES-SOURCE-SEG-019", "lines:354", "sha256:17986df4f5b99b7865915aa4ccfd67c9ec8dcc8d1eca6d4372ed6942a071ef66"): "sha256:8b15b45c8d46bac08d55507513285fdafdf163e4ba297c0e8ba4c4667e4003a7",
    ("TEXPERTES", "TEXPERTES-SOURCE-SEG-025", "lines:374", "sha256:9aeaec70c49b6fb377cfb4cf6a477a62e9699bf14d13011e17e03956d72048a2"): "sha256:29e28b3fd0aa419a4bbcd988b98fe01dbc48ad82b537eedfa5e92a513b3a0d4a",
    ("TEXPERTES", "TEXPERTES-SOURCE-SEG-030", "lines:390-392", "sha256:d48683389bafde43c7c07aa8881a495ccd22ae5f9da5c917f83856e6e7bd4d10"): "sha256:74535c5f2052358f958faabe5eaa402243d1ccea12b0988fd84a71a6d8096665",
    ("TEXPERTES", "TEXPERTES-SOURCE-SEG-031", "lines:393", "sha256:1ffe2b2e0d5e3cf0bc7a013dfe6eb1369d645e15760b2b995fc69017ffae149c"): "sha256:45d57917454f970b780c510c2100fbf369abac99ec737f537d36c9a03a4189ef",
    ("TEXPERTES", "TEXPERTES-SOURCE-SEG-049", "lines:459-460", "sha256:203f0c245f6b8445315354f16fbfd1131e1d07bb9a757b5876ff2bba09378e76"): "sha256:9ef466bbfb67b7367594d03cd7585c876acbaf52b7b5f88cf8fe8b5990802c48",
    ("TEXPERTES", "TEXPERTES-SOURCE-SEG-054", "lines:485", "sha256:cd637f6abce7c96b1c3400967543fdcbc29447146bd89672c630556bdeebd467"): "sha256:17006a96ff583ca2abef6ede0a449bcc9282845bbb3c6cfa8f4ad74f1c69e7fa",
    ("TEXPERTES", "TEXPERTES-SOURCE-SEG-073", "lines:553", "sha256:d986b5d0c4317e41d5fbf0157e05c82bfa338b7425898897c568d06a226e8b15"): "sha256:dfd133a13e4e7b1210d67d24e36c8ecd2469ce0e01fd9eec4b9308e5d5875372",
    ("1NSI", "1NSI-SOURCE-SEG-138", "pdf-page:2;lines:28-31", "sha256:b078df200f4efe7c05b62e9fa16522e9ce111bbddce208b019fbbab55b173f90"): "sha256:20417f1b63aac367b694a5363143bdd299a3b1e0dfbfd1b5f4c8c479a364125e",
    ("TNSI", "TNSI-SOURCE-SEG-117", "pdf-page:2;lines:28-31", "sha256:f6bb464daa46081cdfcbddf6f48711adc6e20d1a80ed77346410edb73e0135cb"): "sha256:0f5c7e5cfb69c140b8b8ee087666655bd21f8bd0848c2fe37efba4d052f51d27",
}


def _sha256_text(value: str) -> str:
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def _source_identity(segment: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        segment["manual"],
        segment["segment_id"],
        segment["source_anchor"],
        _sha256_text(segment["source_wording_short"]),
    )


def _semantic_profile(segment: dict[str, Any]) -> tuple[str | None, str | None]:
    identity = _source_identity(segment)
    atom_type = ATOM_TYPE_EXCEPTIONS.get(
        identity,
        DEFAULT_ATOM_TYPES.get((segment["classification"], segment["mandatory"])),
    )
    justification = JUSTIFICATION_EXCEPTIONS.get(identity)
    if justification is None and atom_type is not None:
        justification = CANONICAL_JUSTIFICATIONS.get(
            (segment["manual"], segment["classification"], atom_type)
        )
    return atom_type, justification


# These twelve decisions were reviewed from the archived sources without
# consulting atom IDs.  The physical anchor and exact source wording digest
# make an upstream wording or extraction change fail closed.
NON_ATOM_EXCEPTIONS: dict[tuple[str, str], dict[str, str]] = {
    ("TSPE", "lines:304"): {
        "wording_digest": "sha256:bf441cc6cb0af226826f7e4bf53466e73aa620748eb198ccabf7cf5321b8a8a8",
        "policy": "STRUCTURAL_HEADER",
        "reason": "Intertitre thématique capturé comme segment, sans exigence officielle autonome.",
    },
    ("TSPE", "lines:698"): {
        "wording_digest": "sha256:27cc48d8892fc6b1de7c62361e1cd7c9e902736be78a12ba8f29cd17fa3756d8",
        "policy": "STRUCTURAL_HEADER",
        "reason": "Intertitre thématique capturé comme segment, sans exigence officielle autonome.",
    },
    ("TCOMPL", "lines:554"): {
        "wording_digest": "sha256:cc8a88e6bd9c2fb065900908aa7286384a51b2ec0a9fd8784601cd1bb19a6d7c",
        "policy": "STRUCTURAL_HEADER",
        "reason": "Intertitre thématique capturé comme segment, sans exigence officielle autonome.",
    },
    ("TCOMPL", "lines:601"): {
        "wording_digest": "sha256:5f310376df3280eee8a7b3bd80c8fc797c1a1f42c3511124fdd919eb57c8ac7c",
        "policy": "STRUCTURAL_HEADER",
        "reason": "Intertitre thématique capturé comme segment, sans exigence officielle autonome.",
    },
    ("TCOMPL", "lines:628"): {
        "wording_digest": "sha256:d2760cde8a564494b23789cbdadfa8fd1baf0ca92c7be0901aa851543c053aca",
        "policy": "STRUCTURAL_HEADER",
        "reason": "Intertitre thématique capturé comme segment, sans exigence officielle autonome.",
    },
    ("TCOMPL", "lines:764"): {
        "wording_digest": "sha256:02b97476434730459b886712bed7390cdb261f3ffd4c082f45ee30fefdd38030",
        "policy": "STRUCTURAL_HEADER",
        "reason": "Intertitre thématique capturé comme segment, sans exigence officielle autonome.",
    },
    ("1SPE", "lines:10-14"): {
        "wording_digest": "sha256:9fe07413353829945389a5885b2f91d33dc977059192b5fcd1cc83a77af07dd7",
        "policy": "FRAMEWORK",
        "reason": "Cadre général d'organisation et de mise en œuvre, sans objet de couverture autonome.",
    },
    ("1SPE", "lines:107-116"): {
        "wording_digest": "sha256:fda994d81d49b384a7c9a99e5ca5d5a2c97e6d61f5b04cabfab0fae3ce739a98",
        "policy": "FRAMEWORK",
        "reason": "Cadre transversal d'évaluation, sans objet disciplinaire autonome.",
    },
    ("1SPE", "lines:192-194"): {
        "wording_digest": "sha256:0d212381e76086d588455e24f9fa70d6e2e8f2962c13fb742f4bcb247870c0ab",
        "policy": "FRAMEWORK",
        "reason": "Cadre transversal de mise en œuvre du vocabulaire et de la logique.",
    },
    ("TSPE", "lines:97"): {
        "wording_digest": "sha256:65b6d983fe6985e2f84c9906b0c7ac1e28363e621a03f7b62d4c92b6d0e066e7",
        "policy": "FRAMEWORK",
        "reason": "Cadre transversal d'évaluation, sans objet disciplinaire autonome.",
    },
    ("TSPE", "lines:985-988"): {
        "wording_digest": "sha256:0d212381e76086d588455e24f9fa70d6e2e8f2962c13fb742f4bcb247870c0ab",
        "policy": "FRAMEWORK",
        "reason": "Cadre transversal de mise en œuvre du vocabulaire et de la logique.",
    },
    ("TSPE", "lines:996-1004"): {
        "wording_digest": "sha256:b8e3fab4b90b6b212343705abf133b134b791d70a6c5341266e2e2909cea7267",
        "policy": "FRAMEWORK",
        "reason": "Cadre transversal d'articulation de la notion de fonction.",
    },
}


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _payload_digest(named_payloads: dict[str, Any]) -> str:
    digest = hashlib.sha256()
    for name in sorted(named_payloads):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(
            json.dumps(
                named_payloads[name],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _manual_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for manual in MANUAL_ORDER:
        subset = [row for row in rows if row["manual"] == manual]
        result[manual] = {
            "source_segments": len(subset),
            "atoms": sum(row["disposition"] == "ATOM" for row in subset),
            "non_atoms": sum(row["disposition"] == "NON_ATOM" for row in subset),
            "mandatory_atoms": sum(
                row["disposition"] == "ATOM"
                and row["mandatory_for_coverage"] == "YES"
                for row in subset
            ),
        }
    return result


def build_independent_requirements(source_payload: dict[str, Any]) -> dict[str, Any]:
    """Classify serialized source segments without consulting first-pass atoms."""

    rows: list[dict[str, Any]] = []
    policy_counts = Counter()
    seen_exceptions: set[tuple[str, str]] = set()
    unknown = 0

    for segment in source_payload["segments"]:
        key = (segment["manual"], segment["source_anchor"])
        wording_digest = _sha256_text(segment["source_wording_short"])
        source_identity = _source_identity(segment)
        exception = NON_ATOM_EXCEPTIONS.get(key)
        disposition = "ATOM"
        decision_basis = "SUBSTANTIVE_OFFICIAL_SOURCE_UNIT"
        mandatory = segment["mandatory"]

        if segment["classification"] == "CROSS_CUTTING_COMPETENCIES":
            disposition = "NON_ATOM"
            mandatory = "NO"
            decision_basis = (
                "TRANSVERSAL_FRAMEWORK_NOT_A_SEPARATE_COVERAGE_REQUIREMENT"
            )
            policy_counts["cross_cutting_non_atoms"] += 1
        elif exception:
            seen_exceptions.add(key)
            if wording_digest != exception["wording_digest"]:
                disposition = "UNKNOWN"
                mandatory = segment["mandatory"]
                decision_basis = "LOCKED_SOURCE_WORDING_DIGEST_MISMATCH"
                unknown += 1
            else:
                disposition = "NON_ATOM"
                mandatory = "NO"
                decision_basis = exception["reason"]
                if exception["policy"] == "STRUCTURAL_HEADER":
                    policy_counts["structural_non_atoms"] += 1
                else:
                    policy_counts["framework_non_atoms"] += 1

        if disposition == "NON_ATOM" and segment["mandatory"] != "NO":
            disposition = "UNKNOWN"
            mandatory = segment["mandatory"]
            decision_basis = "MANDATORY_SOURCE_CANNOT_BE_DISCARDED_AS_NON_ATOM"
            unknown += 1

        expected_atom_type: str | None = None
        canonical_justification: str | None = None
        allowed_paraphrase_digest: str | None = None
        expected_non_atom_classification: str | None = None
        canonical_non_atom_justification: str | None = None
        if disposition == "ATOM":
            expected_atom_type, canonical_justification = _semantic_profile(segment)
            allowed_paraphrase_digest = PARAPHRASE_DIGESTS.get(source_identity)
            if expected_atom_type is None or canonical_justification is None:
                disposition = "UNKNOWN"
                decision_basis = "SOURCE_SEMANTIC_TAXONOMY_UNCLASSIFIED"
                unknown += 1
        elif disposition == "NON_ATOM":
            non_atom_profile = CANONICAL_NON_ATOM_PROFILES.get(
                (segment["manual"], segment["classification"])
            )
            if non_atom_profile is None:
                disposition = "UNKNOWN"
                decision_basis = "NON_ATOM_SEMANTIC_TAXONOMY_UNCLASSIFIED"
                unknown += 1
            else:
                (
                    expected_non_atom_classification,
                    canonical_non_atom_justification,
                ) = non_atom_profile

        rows.append(
            {
                "second_pass_requirement_id": (
                    f"SECOND-PASS::{segment['segment_id']}"
                    if disposition == "ATOM"
                    else None
                ),
                "segment_id": segment["segment_id"],
                "manual": segment["manual"],
                "authority_NOR": segment["authority_NOR"],
                "official_section": segment["official_section"],
                "source_path": segment["source_path"],
                "source_anchor": segment["source_anchor"],
                "source_wording_digest": wording_digest,
                "source_role": segment["classification"],
                "source_mandatory": segment["mandatory"],
                "disposition": disposition,
                "mandatory_for_coverage": mandatory,
                "decision_basis": decision_basis,
                "expected_atom_type": expected_atom_type,
                "canonical_justification": canonical_justification,
                "allowed_paraphrase_digest": allowed_paraphrase_digest,
                "expected_non_atom_classification": (
                    expected_non_atom_classification
                ),
                "canonical_non_atom_justification": (
                    canonical_non_atom_justification
                ),
            }
        )

    missing_exceptions = set(NON_ATOM_EXCEPTIONS) - seen_exceptions
    unknown += len(missing_exceptions)
    return {
        "schema_version": 1,
        "methodology": {
            "source": "serialized official source segments",
            "first_pass_atoms_read": False,
            "imports_first_pass_code": False,
            "policy": "source role plus twelve digest-locked reviewed non-atom exceptions",
        },
        "summary": {
            "source_segments": len(rows),
            "atoms": sum(row["disposition"] == "ATOM" for row in rows),
            "non_atoms": sum(row["disposition"] == "NON_ATOM" for row in rows),
            "mandatory_atoms": sum(
                row["disposition"] == "ATOM"
                and row["mandatory_for_coverage"] == "YES"
                for row in rows
            ),
            "unknown": unknown,
            "policy_counts": {
                "cross_cutting_non_atoms": policy_counts[
                    "cross_cutting_non_atoms"
                ],
                "structural_non_atoms": policy_counts["structural_non_atoms"],
                "framework_non_atoms": policy_counts["framework_non_atoms"],
            },
            "by_manual": _manual_summary(rows),
        },
        "requirements": rows,
    }


def _authorities(authority_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for key, authority in authority_payload["programme_d_enseignement"].items():
        manual = "TSPE" if key == "TSPE_2026_2027" else key
        result[manual] = authority
    return result


def _wrong_year(atom: dict[str, Any], authorities: dict[str, dict[str, Any]]) -> list[str]:
    reasons: list[str] = []
    authority = authorities.get(atom.get("manual", ""))
    if authority is None:
        return ["MANUAL_NOT_IN_2026_2027_AUTHORITY"]
    expected = {
        "authority_NOR": authority["official_ref"],
        "applicable_school_year": SCHOOL_YEAR,
        "effective_year": authority["effective_from"],
        "official_document_digest": authority["local_archival_digest"],
    }
    for field, value in expected.items():
        if atom.get(field) != value:
            reasons.append(f"{field}:{atom.get(field)!r}!={value!r}")
    if authority.get("applicable_2026_2027") is not True:
        reasons.append("AUTHORITY_NOT_APPLICABLE_2026_2027")
    if authority["effective_from"] > SCHOOL_YEAR:
        reasons.append("AUTHORITY_STARTS_AFTER_2026_2027")
    effective_until = authority.get("effective_until")
    if effective_until and effective_until < SCHOOL_YEAR:
        reasons.append("AUTHORITY_ENDED_BEFORE_2026_2027")
    return reasons


def _deduplicate_findings(findings: dict[str, list[dict[str, Any]]]) -> None:
    for code, items in findings.items():
        unique = {
            json.dumps(item, ensure_ascii=False, sort_keys=True): item for item in items
        }
        findings[code] = [unique[key] for key in sorted(unique)]


def _require_unique_nonempty_identifiers(
    rows: list[dict[str, Any]], field: str, label: str
) -> None:
    identifiers = [row.get(field) for row in rows]
    empty = [
        value
        for value in identifiers
        if not isinstance(value, str) or not value.strip()
    ]
    counts = Counter(value for value in identifiers if isinstance(value, str))
    duplicates = sorted(value for value, count in counts.items() if count > 1)
    if empty or duplicates:
        raise ValueError(
            f"{label} must be non-empty and unique; "
            f"empty={len(empty)} duplicates={duplicates}"
        )


def build_payloads(
    source_payload: dict[str, Any],
    atom_payload: dict[str, Any],
    authority_payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    _require_unique_nonempty_identifiers(
        source_payload["segments"], "segment_id", "source segment_id"
    )
    _require_unique_nonempty_identifiers(
        atom_payload["atoms"], "atom_id", "first-pass atom_id"
    )
    independent = build_independent_requirements(source_payload)
    requirements = independent["requirements"]
    requirement_by_segment = {row["segment_id"]: row for row in requirements}
    source_by_segment = {
        row["segment_id"]: row for row in source_payload["segments"]
    }
    authorities = _authorities(authority_payload)
    findings: dict[str, list[dict[str, Any]]] = {
        code: [] for code in FINDING_CODES
    }
    atoms_by_segment: dict[str, list[dict[str, Any]]] = defaultdict(list)
    non_atoms_by_segment: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for atom in atom_payload["atoms"]:
        atom_id = atom.get("atom_id", "")
        source_ids = atom.get("source_segment_ids", [])
        if len(source_ids) != 1:
            findings["AMBIGUOUS_ATOM"].append(
                {
                    "atom_id": atom_id,
                    "source_segment_ids": source_ids,
                    "reason": "ATOM_MUST_REFERENCE_EXACTLY_ONE_SECOND_PASS_UNIT",
                }
            )
            for segment_id in source_ids:
                if segment_id not in requirement_by_segment:
                    findings["PHANTOM_ATOM"].append(
                        {
                            "atom_id": atom_id,
                            "segment_id": segment_id,
                            "reason": "SOURCE_SEGMENT_NOT_IN_SECOND_PASS",
                        }
                    )
            continue

        segment_id = source_ids[0]
        requirement = requirement_by_segment.get(segment_id)
        if requirement is None:
            findings["PHANTOM_ATOM"].append(
                {
                    "atom_id": atom_id,
                    "segment_id": segment_id,
                    "reason": "SOURCE_SEGMENT_NOT_IN_SECOND_PASS",
                }
            )
            continue

        atoms_by_segment[segment_id].append(atom)
        if requirement["disposition"] != "ATOM":
            findings["PHANTOM_ATOM"].append(
                {
                    "atom_id": atom_id,
                    "segment_id": segment_id,
                    "reason": "FIRST_PASS_ATOM_TARGETS_SECOND_PASS_NON_ATOM",
                }
            )
        else:
            segment = source_by_segment[segment_id]
            if atom.get("manual") != segment["manual"]:
                findings["ATOM_MANUAL_DISAGREEMENT"].append(
                    {
                        "atom_id": atom_id,
                        "segment_id": segment_id,
                        "first_pass_manual": atom.get("manual"),
                        "second_pass_manual": segment["manual"],
                    }
                )
            if atom.get("type") != requirement["expected_atom_type"]:
                findings["ATOM_TYPE_DISAGREEMENT"].append(
                    {
                        "atom_id": atom_id,
                        "segment_id": segment_id,
                        "first_pass_type": atom.get("type"),
                        "second_pass_type": requirement["expected_atom_type"],
                    }
                )
            atom_wording_digest = _sha256_text(
                atom.get("short_official_wording_or_paraphrase", "")
            )
            exact_source_wording = (
                atom.get("short_official_wording_or_paraphrase")
                == segment["source_wording_short"]
            )
            locked_paraphrase = (
                requirement["allowed_paraphrase_digest"] is not None
                and atom_wording_digest == requirement["allowed_paraphrase_digest"]
            )
            if not exact_source_wording and not locked_paraphrase:
                findings["ATOM_WORDING_DISAGREEMENT"].append(
                    {
                        "atom_id": atom_id,
                        "segment_id": segment_id,
                        "first_pass_wording_digest": atom_wording_digest,
                        "source_wording_digest": requirement[
                            "source_wording_digest"
                        ],
                        "allowed_paraphrase_digest": requirement[
                            "allowed_paraphrase_digest"
                        ],
                    }
                )
            if (
                atom.get("mandatory_justification")
                != requirement["canonical_justification"]
            ):
                findings["ATOM_JUSTIFICATION_DISAGREEMENT"].append(
                    {
                        "atom_id": atom_id,
                        "segment_id": segment_id,
                        "first_pass_justification": atom.get(
                            "mandatory_justification"
                        ),
                        "canonical_justification": requirement[
                            "canonical_justification"
                        ],
                    }
                )
        if atom.get("official_page_or_anchor") != requirement["source_anchor"]:
            findings["AMBIGUOUS_ATOM"].append(
                {
                    "atom_id": atom_id,
                    "segment_id": segment_id,
                    "reason": "OFFICIAL_ANCHOR_DISAGREEMENT",
                    "first_pass_anchor": atom.get("official_page_or_anchor"),
                    "second_pass_anchor": requirement["source_anchor"],
                }
            )
        if atom.get("mandatory") != requirement["mandatory_for_coverage"]:
            findings["MANDATORY_CLASSIFICATION_DISAGREEMENT"].append(
                {
                    "atom_id": atom_id,
                    "segment_id": segment_id,
                    "first_pass_mandatory": atom.get("mandatory"),
                    "second_pass_mandatory": requirement[
                        "mandatory_for_coverage"
                    ],
                }
            )
        wrong_year_reasons = _wrong_year(atom, authorities)
        if wrong_year_reasons:
            findings["WRONG_YEAR_ATOM"].append(
                {
                    "atom_id": atom_id,
                    "segment_id": segment_id,
                    "reasons": wrong_year_reasons,
                }
            )

    for item in atom_payload["classified_non_atoms"]:
        segment_id = item.get("source_segment_id", "")
        if segment_id not in requirement_by_segment:
            findings["PHANTOM_NON_ATOM_DISPOSITION"].append(
                {
                    "segment_id": segment_id,
                    "manual": item.get("manual"),
                    "reason": "SOURCE_SEGMENT_NOT_IN_SECOND_PASS",
                }
            )
            continue
        requirement = requirement_by_segment[segment_id]
        if requirement["disposition"] == "NON_ATOM":
            if item.get("manual") != requirement["manual"]:
                findings["NON_ATOM_MANUAL_DISAGREEMENT"].append(
                    {
                        "segment_id": segment_id,
                        "first_pass_manual": item.get("manual"),
                        "second_pass_manual": requirement["manual"],
                    }
                )
            if (
                item.get("classification")
                != requirement["expected_non_atom_classification"]
            ):
                findings["NON_ATOM_CLASSIFICATION_DISAGREEMENT"].append(
                    {
                        "segment_id": segment_id,
                        "first_pass_classification": item.get("classification"),
                        "second_pass_classification": requirement[
                            "expected_non_atom_classification"
                        ],
                    }
                )
            if item.get("mandatory_for_coverage") != "NO":
                findings["NON_ATOM_MANDATORY_DISAGREEMENT"].append(
                    {
                        "segment_id": segment_id,
                        "first_pass_mandatory": item.get(
                            "mandatory_for_coverage"
                        ),
                        "second_pass_mandatory": "NO",
                    }
                )
            if (
                item.get("justification")
                != requirement["canonical_non_atom_justification"]
            ):
                findings["NON_ATOM_JUSTIFICATION_DISAGREEMENT"].append(
                    {
                        "segment_id": segment_id,
                        "first_pass_justification": item.get("justification"),
                        "canonical_justification": requirement[
                            "canonical_non_atom_justification"
                        ],
                    }
                )
        non_atoms_by_segment[segment_id].append(item)

    for requirement in requirements:
        segment_id = requirement["segment_id"]
        atoms = atoms_by_segment.get(segment_id, [])
        non_atoms = non_atoms_by_segment.get(segment_id, [])
        if requirement["disposition"] == "ATOM":
            if not atoms:
                findings["AMBIGUOUS_ATOM"].append(
                    {
                        "segment_id": segment_id,
                        "reason": "SECOND_PASS_ATOM_HAS_NO_FIRST_PASS_ATOM",
                    }
                )
                if requirement["mandatory_for_coverage"] == "YES":
                    findings["MANDATORY_SEGMENT_UNREPRESENTED"].append(
                        {
                            "segment_id": segment_id,
                            "reason": "MANDATORY_SECOND_PASS_ATOM_HAS_NO_FIRST_PASS_ATOM",
                        }
                    )
            elif len(atoms) > 1:
                findings["DUPLICATE_ATOM"].append(
                    {
                        "segment_id": segment_id,
                        "atom_ids": sorted(atom["atom_id"] for atom in atoms),
                        "reason": "MULTIPLE_FIRST_PASS_ATOMS_FOR_ONE_SECOND_PASS_UNIT",
                    }
                )
            if non_atoms:
                findings["AMBIGUOUS_ATOM"].append(
                    {
                        "segment_id": segment_id,
                        "reason": "FIRST_PASS_NON_ATOM_DISAGREES_WITH_SECOND_PASS_ATOM",
                    }
                )
        elif requirement["disposition"] == "NON_ATOM":
            if len(non_atoms) != 1:
                findings["AMBIGUOUS_ATOM"].append(
                    {
                        "segment_id": segment_id,
                        "reason": "SECOND_PASS_NON_ATOM_NEEDS_ONE_FIRST_PASS_DISPOSITION",
                        "first_pass_non_atom_count": len(non_atoms),
                    }
                )

    _deduplicate_findings(findings)

    finding_codes_by_segment: dict[str, set[str]] = defaultdict(set)
    finding_codes_by_atom: dict[str, set[str]] = defaultdict(set)
    for code, items in findings.items():
        for item in items:
            if item.get("segment_id"):
                finding_codes_by_segment[item["segment_id"]].add(code)
            if item.get("atom_id"):
                finding_codes_by_atom[item["atom_id"]].add(code)

    ledger_rows: list[dict[str, Any]] = []
    ledger_unknown = 0
    for segment in source_payload["segments"]:
        segment_id = segment["segment_id"]
        atoms = atoms_by_segment.get(segment_id, [])
        non_atoms = non_atoms_by_segment.get(segment_id, [])
        first_pass_atom_ids = sorted(atom["atom_id"] for atom in atoms)
        no_atom_reason: str | None = None
        if len(atoms) == 1 and not non_atoms:
            disposition = "ATOM"
        elif not atoms and len(non_atoms) == 1 and non_atoms[0].get(
            "justification", ""
        ).strip():
            disposition = "NON_ATOM"
            no_atom_reason = non_atoms[0]["justification"].strip()
        else:
            disposition = "UNKNOWN"
            ledger_unknown += 1

        row_findings = set(finding_codes_by_segment.get(segment_id, set()))
        for atom_id in first_pass_atom_ids:
            row_findings.update(finding_codes_by_atom.get(atom_id, set()))
        expected_disposition = requirement_by_segment[segment_id]["disposition"]
        traceability_status = (
            "PASS"
            if not row_findings and disposition == expected_disposition
            else "RED"
        )
        source_document = source_payload["source_documents"][segment["manual"]]
        ledger_rows.append(
            {
                "segment_id": segment_id,
                "manual": segment["manual"],
                "authority_NOR": segment["authority_NOR"],
                "applicable_school_year": source_document[
                    "applicable_school_year"
                ],
                "source_path": segment["source_path"],
                "source_document_digest": source_document["digest"],
                "official_section": segment["official_section"],
                "source_anchor": segment["source_anchor"],
                "source_wording_short": segment["source_wording_short"],
                "source_wording_digest": _sha256_text(
                    segment["source_wording_short"]
                ),
                "source_classification": segment["classification"],
                "source_mandatory": segment["mandatory"],
                "first_pass_disposition": disposition,
                "first_pass_atom_ids": first_pass_atom_ids,
                "no_atom_reason": no_atom_reason,
                "traceability_status": traceability_status,
                "finding_codes": sorted(row_findings),
            }
        )

    source_digest = _payload_digest(
        {
            "authority": authority_payload,
            "first_pass_atoms": atom_payload,
            "source_segments": source_payload,
        }
    )
    any_findings = any(findings.values())
    second_unknown = independent["summary"]["unknown"] + ledger_unknown
    second_status = "RED" if any_findings or second_unknown else "PASS"
    independent_unknown = independent["summary"]["unknown"]
    trace_red_rows = sum(
        row["traceability_status"] != "PASS" for row in ledger_rows
    )
    ledger_status = (
        "RED"
        if any_findings
        or ledger_unknown
        or independent_unknown
        or trace_red_rows
        else "PASS"
    )
    mandatory_denominator = independent["summary"]["mandatory_atoms"]
    first_pass_mandatory_atoms = sum(
        atom.get("mandatory") == "YES" for atom in atom_payload["atoms"]
    )

    ledger = {
        "schema_version": 1,
        "artifact_name": "OFFICIAL_SOURCE_SEGMENT_LEDGER",
        "namespace": "PROGRAMME_D_ENSEIGNEMENT",
        "applicable_school_year": SCHOOL_YEAR,
        "source_digest": source_digest,
        "methodology": {
            "source_segments": str(SOURCE_SEGMENTS_PATH.relative_to(ROOT)),
            "first_pass_atoms": str(FIRST_PASS_ATOMS_PATH.relative_to(ROOT)),
            "total_partition_required": True,
            "explicit_non_atom_reason_required": True,
            "unknown_allowed": False,
        },
        "summary": {
            "status": ledger_status,
            "source_segments": len(ledger_rows),
            "atomized_source_segments": sum(
                row["first_pass_disposition"] == "ATOM" for row in ledger_rows
            ),
            "classified_non_atoms": sum(
                row["first_pass_disposition"] == "NON_ATOM"
                for row in ledger_rows
            ),
            "official_atoms": len(atom_payload["atoms"]),
            "mandatory_atoms": first_pass_mandatory_atoms,
            "unknown": ledger_unknown,
            "independent_unknown": independent_unknown,
            "trace_red_rows": trace_red_rows,
            "by_manual": independent["summary"]["by_manual"],
        },
        "rows": ledger_rows,
    }
    second_pass = {
        "schema_version": 1,
        "artifact_name": "OFFICIAL_ATOMIZATION_SECOND_PASS",
        "namespace": "PROGRAMME_D_ENSEIGNEMENT",
        "applicable_school_year": SCHOOL_YEAR,
        "source_digest": source_digest,
        "independent_requirements_digest": _payload_digest(
            {"independent_requirements": independent}
        ),
        "methodology": {
            "imports_first_pass_code": False,
            "first_pass_atoms_shape_second_pass": False,
            "comparison_boundary": "serialized outputs only",
            "fuzzy_matches_are_proof": False,
            "internal_capacities_are_source": False,
            "denominator_is_derived": True,
        },
        "summary": {
            "status": second_status,
            "source_segments": independent["summary"]["source_segments"],
            "second_pass_atoms": independent["summary"]["atoms"],
            "second_pass_non_atoms": independent["summary"]["non_atoms"],
            "first_pass_atoms": len(atom_payload["atoms"]),
            "mandatory_denominator": mandatory_denominator,
            "first_pass_mandatory_atoms": first_pass_mandatory_atoms,
            "denominator_delta": first_pass_mandatory_atoms
            - mandatory_denominator,
            "unknown": second_unknown,
            "findings_by_code": {
                code: len(findings[code]) for code in FINDING_CODES
            },
            "policy_counts": independent["summary"]["policy_counts"],
            "by_manual": independent["summary"]["by_manual"],
        },
        "findings": findings,
        "requirements": requirements,
    }
    return ledger, second_pass


def _cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        value = ", ".join(str(item) for item in value)
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_segment_ledger_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# OFFICIAL SOURCE SEGMENT LEDGER",
        "",
        f"Status: **{summary['status']}**.",
        "",
        f"- Source segments: {summary['source_segments']}",
        f"- Atomized segments: {summary['atomized_source_segments']}",
        f"- Classified non-atoms: {summary['classified_non_atoms']}",
        f"- Official atoms: {summary['official_atoms']}",
        f"- Mandatory atoms: {summary['mandatory_atoms']}",
        f"- UNKNOWN: {summary['unknown']}",
        "",
        "| Segment | Manuel | Ancre | Mandatory | Disposition | Atoms | Raison non-atom | Trace |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in payload["rows"]:
        lines.append(
            "| "
            + " | ".join(
                _cell(value)
                for value in (
                    row["segment_id"],
                    row["manual"],
                    row["source_anchor"],
                    row["source_mandatory"],
                    row["first_pass_disposition"],
                    row["first_pass_atom_ids"],
                    row["no_atom_reason"],
                    row["traceability_status"],
                )
            )
            + " |"
        )
    return "\n".join(lines).rstrip() + "\n"


def render_second_pass_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# OFFICIAL ATOMIZATION — SECOND PASS",
        "",
        f"Status: **{summary['status']}**.",
        "",
        f"- Source segments: {summary['source_segments']}",
        f"- Second-pass atoms: {summary['second_pass_atoms']}",
        f"- Second-pass non-atoms: {summary['second_pass_non_atoms']}",
        f"- Mandatory denominator: {summary['mandatory_denominator']}",
        f"- First-pass mandatory atoms: {summary['first_pass_mandatory_atoms']}",
        f"- Denominator delta: {summary['denominator_delta']}",
        f"- UNKNOWN: {summary['unknown']}",
        "",
        "## Findings",
        "",
    ]
    for code in FINDING_CODES:
        lines.append(f"- `{code}`: {len(payload['findings'][code])}")
    lines.extend(
        [
            "",
            "## Independent requirements",
            "",
            "| Segment | Manuel | Ancre | Source role | Disposition | Mandatory | Decision basis |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for row in payload["requirements"]:
        lines.append(
            "| "
            + " | ".join(
                _cell(value)
                for value in (
                    row["segment_id"],
                    row["manual"],
                    row["source_anchor"],
                    row["source_role"],
                    row["disposition"],
                    row["mandatory_for_coverage"],
                    row["decision_basis"],
                )
            )
            + " |"
        )
    return "\n".join(lines).rstrip() + "\n"


def _fsync_directory(directory: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    descriptor = os.open(directory, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


@contextmanager
def _directory_lock(directory: Path, *, exclusive: bool):
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    descriptor = os.open(directory, flags)
    try:
        operation = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
        fcntl.flock(descriptor, operation)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def _write_fsynced(path: Path, content: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())


class OutputBundleRecoveryError(RuntimeError):
    def __init__(
        self, recovery_directory: Path, rollback_errors: list[BaseException]
    ) -> None:
        self.recovery_directory = recovery_directory
        self.rollback_errors = tuple(rollback_errors)
        super().__init__(
            "output bundle installation and rollback both failed; "
            f"recovery directory preserved at {recovery_directory}"
        )


def commit_output_bundle(outputs: dict[Path, str]) -> None:
    """Replace one four-file bundle or restore every previous output."""

    if len(outputs) != 4:
        raise ValueError("the official atomization output bundle has four files")
    targets = sorted((Path(path) for path in outputs), key=lambda path: path.name)
    parent_directories = {path.parent.resolve() for path in targets}
    if len(parent_directories) != 1:
        raise ValueError("the output bundle must have one canonical directory")
    directory = parent_directories.pop()

    with _directory_lock(directory, exclusive=True):
        staging = Path(
            tempfile.mkdtemp(prefix=".official-atomization-second-pass-", dir=directory)
        )
        attempted: list[Path] = []
        previous: dict[Path, Path | None] = {}
        staged: dict[Path, Path] = {}
        preserve_staging = False
        try:
            for index, target in enumerate(targets):
                new_path = staging / f"{index}.new"
                _write_fsynced(new_path, outputs[target].encode("utf-8"))
                staged[target] = new_path
                if target.exists():
                    old_path = staging / f"{index}.old"
                    _write_fsynced(old_path, target.read_bytes())
                    previous[target] = old_path
                else:
                    previous[target] = None
            _fsync_directory(staging)

            try:
                for target in targets:
                    attempted.append(target)
                    os.replace(staged[target], target)
                _fsync_directory(directory)
            except BaseException as replacement_error:
                rollback_errors: list[BaseException] = []
                for target in reversed(attempted):
                    try:
                        old_path = previous[target]
                        if old_path is None:
                            target.unlink(missing_ok=True)
                        else:
                            os.replace(old_path, target)
                    except BaseException as rollback_error:
                        rollback_errors.append(rollback_error)
                if rollback_errors:
                    preserve_staging = True
                try:
                    _fsync_directory(directory)
                except BaseException as rollback_sync_error:
                    rollback_errors.append(rollback_sync_error)
                    preserve_staging = True
                if rollback_errors:
                    raise OutputBundleRecoveryError(
                        staging, rollback_errors
                    ) from replacement_error
                raise
        finally:
            if not preserve_staging:
                shutil.rmtree(staging, ignore_errors=True)
                _fsync_directory(directory)


def _load_payloads() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    source_payload = json.loads(SOURCE_SEGMENTS_PATH.read_text(encoding="utf-8"))
    atom_payload = json.loads(FIRST_PASS_ATOMS_PATH.read_text(encoding="utf-8"))
    authority_payload = yaml.safe_load(AUTHORITY_PATH.read_text(encoding="utf-8"))
    return source_payload, atom_payload, authority_payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    ledger, second_pass = build_payloads(*_load_payloads())
    expected = {
        SEGMENT_LEDGER_JSON: render_json(ledger),
        SEGMENT_LEDGER_MD: render_segment_ledger_markdown(ledger),
        SECOND_PASS_JSON: render_json(second_pass),
        SECOND_PASS_MD: render_second_pass_markdown(second_pass),
    }
    if args.check:
        with _directory_lock(AUDIT, exclusive=False):
            stale = [
                path
                for path, content in expected.items()
                if not path.exists()
                or path.read_text(encoding="utf-8") != content
            ]
        if stale:
            for path in stale:
                print(f"STALE_OR_MISSING: {path.relative_to(ROOT)}")
            return 1
        if second_pass["summary"]["status"] != "PASS":
            print("OFFICIAL_ATOMIZATION_SECOND_PASS: RED")
            return 2
        print(
            "official atomization second pass current: "
            f"{second_pass['summary']['second_pass_atoms']} atoms; "
            f"mandatory denominator {second_pass['summary']['mandatory_denominator']}"
        )
        return 0

    commit_output_bundle(expected)
    for path in expected:
        print(f"wrote {path.relative_to(ROOT)}")
    return 0 if second_pass["summary"]["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
