#!/usr/bin/env python3
"""Build the source-locked claim ledger for the 1SPE-SUITES wrong-year P0."""

from __future__ import annotations

import argparse
import copy
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterable

import yaml


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
JSON_OUTPUT = AUDIT / "1SPE_SUITES_WRONG_YEAR_P0_FORENSICS.json"
MD_OUTPUT = AUDIT / "1SPE_SUITES_WRONG_YEAR_P0_FORENSICS.md"
LOCK_PATH = Path(tempfile.gettempdir()) / (
    ".manuels-nexus-1spe-suites-wrong-year-p0-"
    + hashlib.sha256(str(ROOT.resolve()).encode("utf-8")).hexdigest()[:16]
    + ".lock"
)

PRE_P0_REWRITE_SHA = "efd544522252c48f50f7e9ede1e1e4c88374bd1e"
CURRENT_INTEGRATION_SHA = "10cb5f07772842d6630d2a2f78531f6900371023"
SOURCE_RELATIONSHIP = "CURRENT_INTEGRATION_IS_ANCESTOR_OF_PRE_P0_REWRITE"
OFFICIAL_ATOMS_PATH = "audit/OFFICIAL_PROGRAM_ATOMS_2026_2027.json"
OFFICIAL_AUTHORITY_PATH = "audit/OFFICIAL_PROGRAM_AUTHORITY_2026_2027.yaml"
EXPECTED_OFFICIAL_ATOMS_DIGEST = (
    "sha256:9afb4acfe12a96772496a75aaa09603b48da389897922f5a5e4f9d8ffcac3fcc"
)
EXPECTED_OFFICIAL_AUTHORITY_DIGEST = (
    "sha256:c0dbd04a69c58eca13b9a70c8b1703468aae1da6d9f98b51d20fff5308f3dda7"
)
EXPECTED_OFFICIAL_MANUAL = "1SPE"
EXPECTED_OFFICIAL_NOR = "MENE2602917A"
EXPECTED_OFFICIAL_YEAR = "2026-2027"

LOG_OR_FORMAL_THRESHOLD_SET = (
    "1SPE-SUITES-EX-026",
    "1SPE-SUITES-CO-026",
    "1SPE-SUITES-EX-031",
    "1SPE-SUITES-CO-031",
    "1SPE-SUITES-EX-038",
    "1SPE-SUITES-CO-038",
    "1SPE-SUITES-CO-044",
    "1SPE-SUITES-CO-046",
    "1SPE-SUITES-EX-048",
    "1SPE-SUITES-CO-048",
    "1SPE-SUITES-CO-049",
)
FORMAL_LIMIT_CONVERGENCE_SET = (
    "1SPE-SUITES-CO-027",
    "1SPE-SUITES-CO-037",
    "1SPE-SUITES-EX-040",
    "1SPE-SUITES-CO-040",
    "1SPE-SUITES-EX-042",
    "1SPE-SUITES-CO-042",
    "1SPE-SUITES-EX-043",
    "1SPE-SUITES-CO-043",
    "1SPE-SUITES-EX-048",
    "1SPE-SUITES-CO-048",
    "1SPE-SUITES-CO-046",
    "1SPE-SUITES-CO-049",
)
EXPECTED_INTERSECTION = (
    "1SPE-SUITES-CO-046",
    "1SPE-SUITES-EX-048",
    "1SPE-SUITES-CO-048",
    "1SPE-SUITES-CO-049",
)
EXPECTED_UNION = tuple(
    dict.fromkeys(LOG_OR_FORMAL_THRESHOLD_SET + FORMAL_LIMIT_CONVERGENCE_SET)
)

ALLOWED_CLASSIFICATIONS = {
    "KEEP_AS_IS",
    "REWRITE_TO_1SPE",
    "OPTIONAL_TERMINALE_EXTENSION",
    "DELETE_INVALID",
}

AUTHORITY_THRESHOLD = (
    "MENE2602917A — 1SPE-OFFICIAL-063 : calcul algorithmique de termes, "
    "sommes et seuils ; les logarithmes ne sont pas un outil du programme de Première."
)
AUTHORITY_INTUITIVE_LIMIT = (
    "MENE2602917A — 1SPE-OFFICIAL-053 et 1SPE-OFFICIAL-059 : introduction "
    "intuitive sur des exemples et conjecture d'une limite éventuelle."
)
AUTHORITY_FIRST_SPE = (
    "MENE2602917A — 1SPE-OFFICIAL-057/060 : terme général, variations et "
    "raisonnement sur les suites arithmétiques ou géométriques."
)
AUTHORITY_TERMINALE_LIMIT = (
    "MENE1921246A — TSPE-OFFICIAL-076/077/093 : théorèmes de convergence, "
    "établissement et calcul formels de limites relèvent de Terminale."
)

CLAIM_POLICIES = {
    "log_prompt": {
        "classification": "REWRITE_TO_1SPE",
        "reason": "Le seuil est légitime, mais l'énoncé impose ou propose le logarithme comme outil de résolution, hors programme de Première.",
        "official_authority": AUTHORITY_THRESHOLD,
        "replacement_strategy": "Conserver le problème de seuil et demander des essais successifs, une table, une boucle while ou un encadrement numérique au rang minimal.",
    },
    "internal_log": {
        "classification": "REWRITE_TO_1SPE",
        "reason": "Le calcul interne verrouille la réponse par logarithme ; cette dépendance contredit la méthode Première attendue même si elle n'est pas imprimée.",
        "official_authority": AUTHORITY_THRESHOLD,
        "replacement_strategy": "Remplacer le calcul logarithmique de vérification par une recherche entière bornée et les deux contrôles au rang précédent et au rang minimal.",
    },
    "log_solver": {
        "classification": "REWRITE_TO_1SPE",
        "reason": "Le passage au logarithme est mathématiquement valide mais constitue ici un outil de résolution de Terminale dans une correction de Première.",
        "official_authority": AUTHORITY_THRESHOLD,
        "replacement_strategy": "Garder l'inéquation et le résultat, puis établir le rang minimal par algorithme, table de valeurs ou essais successifs avec double vérification.",
    },
    "log_bareme": {
        "classification": "REWRITE_TO_1SPE",
        "reason": "Le barème crédite explicitement une méthode logarithmique non exigible en Première.",
        "official_authority": AUTHORITY_THRESHOLD,
        "replacement_strategy": "Créditer la mise en inéquation, la recherche algorithmique ou numérique du rang minimal et la vérification aux deux rangs frontières.",
    },
    "log_content": {
        "classification": "REWRITE_TO_1SPE",
        "reason": "La définition d'une suite par logarithme et l'usage de ses propriétés algébriques constituent ici un contenu de Terminale, pas une méthode de Première.",
        "official_authority": "MENE1921246A — TSPE-OFFICIAL-120/121 : fonction logarithme et propriétés algébriques au programme de Terminale ; aucun atom équivalent dans MENE2602917A.",
        "replacement_strategy": "Remplacer cette question par une tâche autonome de Première sur terme général, variations ou changement de suite ne mobilisant pas le logarithme.",
    },
    "log_content_internal": {
        "classification": "REWRITE_TO_1SPE",
        "reason": "Le bloc de vérification encode un objet et des propriétés logarithmiques de Terminale.",
        "official_authority": "MENE1921246A — TSPE-OFFICIAL-120/121 : fonction logarithme et propriétés algébriques au programme de Terminale ; aucun atom équivalent dans MENE2602917A.",
        "replacement_strategy": "Aligner la vérification sur la future question Première et supprimer toute dépendance à ln/log.",
    },
    "log_content_bareme": {
        "classification": "REWRITE_TO_1SPE",
        "reason": "Le barème attribue des points à des propriétés du logarithme qui ne sont pas exigibles en Première.",
        "official_authority": "MENE1921246A — TSPE-OFFICIAL-120/121 : fonction logarithme et propriétés algébriques au programme de Terminale ; aucun atom équivalent dans MENE2602917A.",
        "replacement_strategy": "Recomposer les points sur les capacités Première de la question de remplacement, sans crédit logarithmique.",
    },
    "threshold_setup": {
        "classification": "KEEP_AS_IS",
        "reason": "La formulation d'un seuil, sa traduction en inéquation et la recherche du premier rang appartiennent au travail légitime sur les suites.",
        "official_authority": AUTHORITY_THRESHOLD,
        "replacement_strategy": "Conserver exactement cette mise en problème ; seule une méthode hors année située ailleurs doit être remplacée.",
    },
    "numeric_check": {
        "classification": "KEEP_AS_IS",
        "reason": "Le contrôle numérique aux rangs consécutifs prouve honnêtement la minimalité du seuil sans logarithme.",
        "official_authority": AUTHORITY_THRESHOLD,
        "replacement_strategy": "Conserver ces valeurs et leur comparaison ; elles doivent rester l'attestation finale du rang minimal.",
    },
    "intuitive_conjecture": {
        "classification": "KEEP_AS_IS",
        "reason": "Le passage observe des termes et formule explicitement une conjecture intuitive, exactement dans la portée de Première.",
        "official_authority": AUTHORITY_INTUITIVE_LIMIT,
        "replacement_strategy": "Conserver le vocabulaire d'observation et de conjecture sans le transformer en preuve formelle.",
    },
    "first_spe_reasoning": {
        "classification": "KEEP_AS_IS",
        "reason": "Le calcul de point fixe, de terme général, de monotonie ou de bornes est autonome et conforme ; il ne prouve pas à lui seul une convergence.",
        "official_authority": AUTHORITY_FIRST_SPE,
        "replacement_strategy": "Conserver ce raisonnement et empêcher seulement qu'il soit prolongé par un théorème ou un passage à la limite hors année.",
    },
    "formal_prompt": {
        "classification": "REWRITE_TO_1SPE",
        "reason": "La consigne exige une conclusion ou une justification formelle de convergence au-delà de la conjecture intuitive autorisée en Première.",
        "official_authority": AUTHORITY_INTUITIVE_LIMIT,
        "replacement_strategy": "Reformuler en observation numérique et conjecture, ou demander uniquement terme général, variations, bornes et interprétation sans preuve de limite.",
    },
    "formal_internal": {
        "classification": "REWRITE_TO_1SPE",
        "reason": "La vérification interne appelle un calcul formel de limite ou utilise une conclusion de convergence comme preuve du résultat.",
        "official_authority": AUTHORITY_INTUITIVE_LIMIT,
        "replacement_strategy": "Vérifier les identités exactes et un échantillon de termes ; réserver les assertions de limite à une extension Terminale séparée.",
    },
    "formal_convergence": {
        "classification": "REWRITE_TO_1SPE",
        "reason": "La conclusion formelle mobilise un théorème de convergence, un passage à la limite ou un vocabulaire de Terminale ; aucun besoin éditorial autonome non redondant ne justifie une extension.",
        "official_authority": AUTHORITY_INTUITIVE_LIMIT,
        "replacement_strategy": "Réécrire uniquement cette conclusion en observation ou conjecture intuitive ; supprimer la phrase si cette conjecture est déjà formulée ailleurs.",
    },
}

def _claim(
    claim_id: str,
    line_start: int,
    line_end: int,
    policy: str,
    line_digest: str,
) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "line_start": line_start,
        "line_end": line_end,
        "line_range": f"{line_start}-{line_end}",
        "line_digest": line_digest,
        **CLAIM_POLICIES[policy],
    }


def _object(
    object_id: str,
    path: str,
    source_digest: str,
    claims: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "object_id": object_id,
        "path": path,
        "student_teacher": (
            "STUDENT_STATEMENT" if "-EX-" in object_id else "TEACHER_CORRECTION"
        ),
        "source_digest": source_digest,
        "claims": claims,
    }


CHAPTER = "Mathematiques/manuel-maths/chapitres/1SPE-SUITES"

OBJECT_SPECS = [
    _object("1SPE-SUITES-EX-026", f"{CHAPTER}/exercices/1SPE-SUITES-EX-026.tex", "sha256:a31d801cafa7d5187185dc4e983dfd2077e90919b19a18dc086fa06faca25cbb", [
        _claim("1SPE-SUITES-EX-026-C01", 30, 30, "log_prompt", "sha256:077677ee7106e0379aad5cc1e536a20463d7c3606f8114c5e0908ef19e2c2897"),
    ]),
    _object("1SPE-SUITES-CO-026", f"{CHAPTER}/corriges/1SPE-SUITES-CO-026.tex", "sha256:2d18cd2e2f496203198f2d51af8f57eae5a39b2cc82e5fdd67289ebe2e37029a", [
        _claim("1SPE-SUITES-CO-026-C01", 16, 20, "internal_log", "sha256:386b63c7091e1c74933b03f2aa8e4fd34844ea9799fe14cdce86a45bd4b94476"),
        _claim("1SPE-SUITES-CO-026-C02", 21, 22, "numeric_check", "sha256:298f2c443e4ef52ae5a2654524bb748e5a68f253611f2dc880142ca1464aa5d1"),
        _claim("1SPE-SUITES-CO-026-C03", 68, 70, "threshold_setup", "sha256:a73e350d79c489ea5f41a44adf858706b26116afe78878ee01a4dee4e7e53373"),
        _claim("1SPE-SUITES-CO-026-C04", 73, 85, "log_solver", "sha256:c806b083c16d7a63070dc572c03aed7f7cd84a0ee21d6919694d7a4297add018"),
        _claim("1SPE-SUITES-CO-026-C05", 87, 92, "numeric_check", "sha256:456723fd708773588385f8111a07833da01e4fcd50abaf8fccb6aecf567cb9d8"),
        _claim("1SPE-SUITES-CO-026-C06", 94, 94, "log_bareme", "sha256:90362f05846bf4d8d2ca8e1d2652249cda64c99155f3af113bf563dc9a36aba2"),
    ]),
    _object("1SPE-SUITES-EX-031", f"{CHAPTER}/exercices/1SPE-SUITES-EX-031.tex", "sha256:0db334d0d3f2cd39865b645734072b1bb77fe0fd993c06cab8b6f2991b088bc6", [
        _claim("1SPE-SUITES-EX-031-C01", 29, 31, "log_content", "sha256:e50dbc90185cd282bb6b9b0180a551cfbbfbf75107196d8d7be9734757dbcddc"),
    ]),
    _object("1SPE-SUITES-CO-031", f"{CHAPTER}/corriges/1SPE-SUITES-CO-031.tex", "sha256:dc6789950a2919f4d0b7ff2359032509db897fe678626f34703bbf981d1fb49e", [
        _claim("1SPE-SUITES-CO-031-C01", 16, 20, "log_content_internal", "sha256:5fbf83cc1628f42b9b28c4e3840abf7f9bcf25f4848878e7ae48c373df0260c8"),
        _claim("1SPE-SUITES-CO-031-C02", 58, 85, "log_content", "sha256:bb577b909ae24b6116f272e60f7191ad51ab5d7b37ec6f7e8208ee3d9ecaabe9"),
        _claim("1SPE-SUITES-CO-031-C03", 87, 87, "log_content_bareme", "sha256:b0c2932d2e6f70918a18569ec5643c378018f7a42acc9a7eb4a22d35a081092f"),
    ]),
    _object("1SPE-SUITES-EX-038", f"{CHAPTER}/exercices/1SPE-SUITES-EX-038.tex", "sha256:c12639ed21411bf6a8927d7d648d626787f85e2a820c818d889b4f5812133161", [
        _claim("1SPE-SUITES-EX-038-C01", 14, 17, "internal_log", "sha256:5068ad7c1aecbec09c9dd103bfc96e9cbba34b55972f0dbb110de8ce2bf0e889"),
        _claim("1SPE-SUITES-EX-038-C02", 31, 33, "threshold_setup", "sha256:df5494b3ebe0102c412dfe42026c23c0dcc6f4d42fede3eef56de672919f2f9a"),
        _claim("1SPE-SUITES-EX-038-C03", 34, 34, "log_prompt", "sha256:f57d286fa51fe973d84a3bb7ef9aa6cc20418b996b1d03825a4405ba00b1f1b0"),
        _claim("1SPE-SUITES-EX-038-C04", 35, 35, "threshold_setup", "sha256:1231c462e38058cf41397979b43fc92490f2b81b83e05f5ad779ad76f3a8cf14"),
    ]),
    _object("1SPE-SUITES-CO-038", f"{CHAPTER}/corriges/1SPE-SUITES-CO-038.tex", "sha256:c529c8522e0ec4b7d0b15897469f1f02b49e7d91d73920e69ec46ba17ab99402", [
        _claim("1SPE-SUITES-CO-038-C01", 15, 19, "internal_log", "sha256:4d6d59cdc7fe6852ec99e4276527beaf58fccf55e54902720391c22b93d12f93"),
        _claim("1SPE-SUITES-CO-038-C02", 20, 21, "numeric_check", "sha256:aaece27e0c16c1ae61aceb76b70da198e7311227416f5abeaa8ff83aa2358811"),
        _claim("1SPE-SUITES-CO-038-C03", 64, 70, "threshold_setup", "sha256:f2e95a4f6874ed9100fae6eed06b4bfebe6ba383732731809bb9001b345430af"),
        _claim("1SPE-SUITES-CO-038-C04", 73, 82, "log_solver", "sha256:6949b5f24102017b9ef016746dec51d65946acd08a88972f41866d66bb807ea4"),
        _claim("1SPE-SUITES-CO-038-C05", 84, 98, "numeric_check", "sha256:281bfff2850e597f85594b41e2d4c5f2ff48ba13192e150c60d0c394b8bb0a4d"),
        _claim("1SPE-SUITES-CO-038-C06", 100, 100, "log_bareme", "sha256:c861bf65867545bc484a39f7ab9ed80e08755102d66ce569c65f0e34e5847071"),
    ]),
    _object("1SPE-SUITES-CO-044", f"{CHAPTER}/corriges/1SPE-SUITES-CO-044.tex", "sha256:d852ba89c2893887b2f5491f370766a20a638cfa3c216601904ef00bea8252d7", [
        _claim("1SPE-SUITES-CO-044-C01", 18, 19, "internal_log", "sha256:3cc12b2028c85fad663c1a54318d8f9677aa5c9c70117837b3629306617cf395"),
        _claim("1SPE-SUITES-CO-044-C02", 20, 21, "numeric_check", "sha256:352512215bc23b6855b1f6bc9bb4ad43d7a9afd71e7d98a46023fbe0e83f3232"),
        _claim("1SPE-SUITES-CO-044-C03", 58, 62, "threshold_setup", "sha256:b2fc6fe125e79469665a8a6f779570e8d5f960d4c88f93bb5183ae09b7a214cd"),
        _claim("1SPE-SUITES-CO-044-C04", 64, 69, "log_solver", "sha256:ac57b22d3070129db7b67f4cb8de415d68cca727f83330e869e2a287a8b1c879"),
        _claim("1SPE-SUITES-CO-044-C05", 71, 75, "numeric_check", "sha256:77605dc1c83da414d5887d23026612f3e0094ee1a7dacec7ff9b7995653b70ea"),
    ]),
    _object("1SPE-SUITES-CO-046", f"{CHAPTER}/corriges/1SPE-SUITES-CO-046.tex", "sha256:d2e49911939defec34d0c37f43550236d824a00cf72e8bdc749012a8048633ce", [
        _claim("1SPE-SUITES-CO-046-C01", 27, 28, "formal_internal", "sha256:25133cc8708a41d442f5ec05db7ecfd787e7b14ca67b3bf9b10ffbda8a7f808e"),
        _claim("1SPE-SUITES-CO-046-C02", 29, 32, "internal_log", "sha256:d7302579ead594ffe9f1c5736dc8b631a5342a48e7a67dd5fe03bf4598192464"),
        _claim("1SPE-SUITES-CO-046-C03", 33, 34, "numeric_check", "sha256:4809a66bc7c5dc709cfdaf4a47241f03ee9bf9b81abaf4051732f819758affb8"),
        _claim("1SPE-SUITES-CO-046-C04", 39, 45, "formal_internal", "sha256:86be7e7ed8b726950af539509e5fc28d0adb73d3ed8daadc9a8654ec96047191"),
        _claim("1SPE-SUITES-CO-046-C05", 97, 99, "formal_convergence", "sha256:9d80b01603a777501ccb65f8a3df80d9fdc5f1c73e40e04dadc7da56f4e78e04"),
        _claim("1SPE-SUITES-CO-046-C06", 101, 101, "threshold_setup", "sha256:6ea8c87a3bb5ecdde71e2bc5ad7c17523bc2ee263f1f3f18a8f249c5c98800db"),
        _claim("1SPE-SUITES-CO-046-C07", 103, 103, "log_solver", "sha256:4a835f9797bf39f3c26cefbbd1e89476f9a0c2dccee9625a9413a2c09550a6e4"),
        _claim("1SPE-SUITES-CO-046-C08", 105, 109, "threshold_setup", "sha256:ec02b4edc068f14e4a044c1d20a37ea31867c35b899181c99c65e1fdfc30207a"),
        _claim("1SPE-SUITES-CO-046-C09", 112, 120, "log_solver", "sha256:3791895f89bd7939d97607e97b1c2f62870abfb0bd7c52a659bb3f99a29b2a87"),
        _claim("1SPE-SUITES-CO-046-C10", 122, 128, "numeric_check", "sha256:e90f6242d2d381cc166f256f721b1fc1c542f09feb477f3021624985d5b61e61"),
        _claim("1SPE-SUITES-CO-046-C11", 130, 132, "formal_convergence", "sha256:22b25b3a6cad6085b96e0f1a51d9f345c771c083fa512b6c59bfecc6868c5442"),
    ]),
    _object("1SPE-SUITES-EX-048", f"{CHAPTER}/exercices/1SPE-SUITES-EX-048.tex", "sha256:c45b492fa9428846b0444f8173bb525a2bc97f4830a67d5247a7949590fd6ba3", [
        _claim("1SPE-SUITES-EX-048-C01", 19, 24, "formal_internal", "sha256:20e02754ce6eb4c34d8345d3e69e219fb37359c4d8b62170669aed905c41659c"),
        _claim("1SPE-SUITES-EX-048-C02", 25, 29, "internal_log", "sha256:2133e3b1b56a60db409690778f84be59f63b18ae2da3d055fc32371f6918741e"),
        _claim("1SPE-SUITES-EX-048-C03", 48, 52, "formal_prompt", "sha256:0a950a9838e7b53efd3173cbfc192fa366f6fe6f5f40265fb33a713fe6df2aa5"),
        _claim("1SPE-SUITES-EX-048-C04", 54, 54, "threshold_setup", "sha256:651bd924eba4ab7708612e30a6856b2e5532a51ba72f501affe7b8ebe1acc1db"),
        _claim("1SPE-SUITES-EX-048-C05", 55, 55, "log_prompt", "sha256:af4ec5c4164b5b71230aadf01fd99799ce49ca4e25043aa90ca86efc68e8fcae"),
        _claim("1SPE-SUITES-EX-048-C06", 57, 59, "formal_prompt", "sha256:76a20e6c21aa4e15b8229c9483446e9f5eca3f8e56ee5d14e607f47c346b0229"),
    ]),
    _object("1SPE-SUITES-CO-048", f"{CHAPTER}/corriges/1SPE-SUITES-CO-048.tex", "sha256:34e5d35ada846555cfe82ad858ce7b77a173519700c4515f07d13a75a7dd03ae", [
        _claim("1SPE-SUITES-CO-048-C01", 25, 26, "formal_internal", "sha256:ebe6837af2900263520f5f907acbefc70d5bc2c3900091ba4a6da26ed6526513"),
        _claim("1SPE-SUITES-CO-048-C02", 27, 39, "internal_log", "sha256:cbde59cb7715b00b001443583b0d0b9d4996508c8e468a9fc18bf17c8c73933d"),
        _claim("1SPE-SUITES-CO-048-C03", 89, 105, "formal_convergence", "sha256:696de5bfba06615ff9c2624298ca89ae88dc0bd5055c69e6be6322e11873e2b8"),
        _claim("1SPE-SUITES-CO-048-C04", 107, 107, "threshold_setup", "sha256:fa14c1aaa94faab1620964e5a8fa2f0d28d7632b95ee2901194362adaa96f8f7"),
        _claim("1SPE-SUITES-CO-048-C05", 109, 109, "log_solver", "sha256:0a620eff1b286cf695740873eaebed6e5260e4a46476262431a6232d9c88779e"),
        _claim("1SPE-SUITES-CO-048-C06", 111, 113, "threshold_setup", "sha256:bf5703b87a67fb7386b15cef425b6c3e45442556e1f213d4ef09fb54ad3bf4b0"),
        _claim("1SPE-SUITES-CO-048-C07", 115, 130, "log_solver", "sha256:5a385f2ebea275ff800ed447a7f7427451cc7ca7812298fb50434dddffec42f3"),
        _claim("1SPE-SUITES-CO-048-C08", 132, 138, "numeric_check", "sha256:7a15c1e6179e89ea7d6467c877f8f22771f56988ea353381d19a2aece2ab3d66"),
        _claim("1SPE-SUITES-CO-048-C09", 140, 154, "formal_convergence", "sha256:b385b74fee8a95c3a70af43f699ce6ae80b9cbf613bf44e80c83632163967caf"),
    ]),
    _object("1SPE-SUITES-CO-049", f"{CHAPTER}/corriges/1SPE-SUITES-CO-049.tex", "sha256:047917751697bf7f87f3ede824dd5c007755c5522f1f7c4e48a413a0ede3ceae", [
        _claim("1SPE-SUITES-CO-049-C01", 18, 20, "internal_log", "sha256:871790a6ba637a98499e78672980a2f6bf3a16db1055c7e1396e16920d99e1d6"),
        _claim("1SPE-SUITES-CO-049-C02", 21, 22, "numeric_check", "sha256:3c497f79b0170e7e012641c64fbfd6c63046ae59caee74e40830c71ace76cc73"),
        _claim("1SPE-SUITES-CO-049-C03", 87, 87, "threshold_setup", "sha256:221299460d892fbfe77115250beb307c2204c1698afbf08fa50b1fd9ba0a5be3"),
        _claim("1SPE-SUITES-CO-049-C04", 89, 89, "log_solver", "sha256:218bde2c770a21d708c530a2b6cbe646a684c780c6471a6169280034b0de12c5"),
        _claim("1SPE-SUITES-CO-049-C05", 91, 93, "threshold_setup", "sha256:44f58821845614c6c96c40ec9f57d2f1a3dbf91f5e2ec6b57fc45073945f3236"),
        _claim("1SPE-SUITES-CO-049-C06", 95, 100, "log_solver", "sha256:20d110fcfe33bcda5827cdff6488dad02a618cf064ad691d8bfb730415102b55"),
        _claim("1SPE-SUITES-CO-049-C07", 102, 104, "numeric_check", "sha256:2dd45dcf9c473158d878257962338bfef38e45dcf39c7b52a0689e04520f9fc7"),
        _claim("1SPE-SUITES-CO-049-C08", 177, 187, "formal_convergence", "sha256:c83ef36785c514e16b862d262f74f6b6ebf0bf47f9f956a0bc5303759cd71d94"),
    ]),
    _object("1SPE-SUITES-CO-027", f"{CHAPTER}/corriges/1SPE-SUITES-CO-027.tex", "sha256:a1ad2299f2b4401a4d58900a2e761c64615fdfa0338b3af4a0eff38aa590b1e9", [
        _claim("1SPE-SUITES-CO-027-C01", 89, 93, "formal_convergence", "sha256:5480dc3f452949e3a54b90c8efa92e9fd498fd3a2cd023761cbc20fc2fb447a7"),
    ]),
    _object("1SPE-SUITES-CO-037", f"{CHAPTER}/corriges/1SPE-SUITES-CO-037.tex", "sha256:7e69f1e6d103eef2bb92a1545fdd4f26771465f0286655ad6bf2497d95359b91", [
        _claim("1SPE-SUITES-CO-037-C01", 84, 91, "first_spe_reasoning", "sha256:f36bd25ddb0185eec1115b33c30388f391f4da7ab3bce7ddfeb635bb4c88937d"),
        _claim("1SPE-SUITES-CO-037-C02", 93, 93, "formal_convergence", "sha256:70a6a98092742d7c8a6c426820f28e253f323a941804dbeabbf7e7b5e4425ed9"),
    ]),
    _object("1SPE-SUITES-EX-040", f"{CHAPTER}/exercices/1SPE-SUITES-EX-040.tex", "sha256:39702cfcc2ffdb6e90407224f74911dfe8cf08ea957ff04c687c54176f9cdb68", [
        _claim("1SPE-SUITES-EX-040-C01", 35, 35, "intuitive_conjecture", "sha256:d72e3eacd7144096b7cf0b75296a4e107239aded87c83c94403bf992dbbf0178"),
        _claim("1SPE-SUITES-EX-040-C02", 37, 41, "first_spe_reasoning", "sha256:5c5ecc10e5f5a3b408f61301cc5fe04e8a560ba144e52b09fe115fe9dc37b7f6"),
        _claim("1SPE-SUITES-EX-040-C03", 43, 43, "formal_prompt", "sha256:1667e5fa1f15c6bc899eae2a10a4d46e688450e4b918b416673698345e7bf208"),
    ]),
    _object("1SPE-SUITES-CO-040", f"{CHAPTER}/corriges/1SPE-SUITES-CO-040.tex", "sha256:2164361a82fa0f10284465c6e0f10843ec1c56e87d6e422935b05c66b3bf07a6", [
        _claim("1SPE-SUITES-CO-040-C01", 40, 42, "intuitive_conjecture", "sha256:a327eff9859cdb36f7369f60f98694f0b536d0fe7eb6db70bc04d1339659342d"),
        _claim("1SPE-SUITES-CO-040-C02", 44, 48, "first_spe_reasoning", "sha256:e831026908a547740e275a79ce81269d7febb1cabe6c894ebf72c6479fb5647c"),
        _claim("1SPE-SUITES-CO-040-C03", 50, 50, "formal_convergence", "sha256:0c897fbedb093902703ae2c4eef25586ed76253e565538a09beef70be47661df"),
        _claim("1SPE-SUITES-CO-040-C04", 77, 87, "formal_convergence", "sha256:4e2cb13b69861efcf69c7fb96a30855627c53cc8314abd85f6fe66a55d8eb4d4"),
    ]),
    _object("1SPE-SUITES-EX-042", f"{CHAPTER}/exercices/1SPE-SUITES-EX-042.tex", "sha256:a869b6388d90809fd16b5a080285479f0bc1da9b9e9ef0b7e9bc20c4b564c4b6", [
        _claim("1SPE-SUITES-EX-042-C01", 22, 25, "formal_internal", "sha256:28fe2362ab992bd5df55531e1543fbaf7a77f38d8f1d0b42490ed27128b91f44"),
        _claim("1SPE-SUITES-EX-042-C02", 31, 31, "intuitive_conjecture", "sha256:15513d55e51b54c7f8a7b8bd7232d2e1eb7a877a00c0d2e5bc585bf53da2c328"),
        _claim("1SPE-SUITES-EX-042-C03", 38, 42, "first_spe_reasoning", "sha256:52935e23fa1a52dd2022c3411f854ad4f0480698851f903066435e6e0f277f47"),
        _claim("1SPE-SUITES-EX-042-C04", 44, 44, "formal_prompt", "sha256:1d615206aaf6620c955ac29fe9acb63d2c50833ac8f016eca2e495f8029281b5"),
    ]),
    _object("1SPE-SUITES-CO-042", f"{CHAPTER}/corriges/1SPE-SUITES-CO-042.tex", "sha256:4928effe3a95f01233c7d6874ac93d6875975df55f6a08d8a28c08f60b47e33b", [
        _claim("1SPE-SUITES-CO-042-C01", 55, 59, "first_spe_reasoning", "sha256:68741a298d1881fa53ef59eed345452b59388ebfd61d9360947c12c5d1306b0e"),
        _claim("1SPE-SUITES-CO-042-C02", 61, 61, "formal_convergence", "sha256:4fc4171de957edc4d691d50a7ce7c6db770c5f0cd94b315ab4535cca59ba9b64"),
    ]),
    _object("1SPE-SUITES-EX-043", f"{CHAPTER}/exercices/1SPE-SUITES-EX-043.tex", "sha256:e1d4a3d57d1a54d784db9526681dcfc587c4690abe27b5a1c6534936ff90278b", [
        _claim("1SPE-SUITES-EX-043-C01", 25, 28, "formal_internal", "sha256:ab52e79b9215ac7224cb59a391bf586e9ea8174a56ea438027ba7b2e100564fe"),
        _claim("1SPE-SUITES-EX-043-C02", 39, 39, "intuitive_conjecture", "sha256:fba4179ee4ff8d2c9fc4f9bf5f77582ab6d5a2c6c202b39759baf05d9cf0a4f8"),
        _claim("1SPE-SUITES-EX-043-C03", 41, 50, "first_spe_reasoning", "sha256:c4fa2e64ca21bfa5ce5d540c13e96281ec64f0758ab78b11aaa916daa00d0756"),
        _claim("1SPE-SUITES-EX-043-C04", 53, 53, "formal_prompt", "sha256:b86cc0b2e0b3a1f3ce162e0669bede43728ce5379870ec70009d24583b824f90"),
    ]),
    _object("1SPE-SUITES-CO-043", f"{CHAPTER}/corriges/1SPE-SUITES-CO-043.tex", "sha256:9477617cc58055aed5022a40d9a80660ea7c3a209998788977f383cd7d4e389e", [
        _claim("1SPE-SUITES-CO-043-C01", 35, 35, "intuitive_conjecture", "sha256:abf09ffa261b9884b1db593e459004b77fb8bdd6a625cbf314dd5c528c13ef6d"),
        _claim("1SPE-SUITES-CO-043-C02", 37, 55, "first_spe_reasoning", "sha256:103b8156703311385b0634f44dd6098fdc7e2185513c1a573fc51988ccc77fde"),
        _claim("1SPE-SUITES-CO-043-C03", 58, 72, "first_spe_reasoning", "sha256:8f57b9fbb2fa3bc72f622ab34c69752b7f590414d6a2c0e1e95b49e2ebf1d5b0"),
        _claim("1SPE-SUITES-CO-043-C04", 74, 74, "formal_convergence", "sha256:ab5832b22ebb7c3168d588c51c6ae65bfb021f380159c7fc7fe6f656539164a0"),
    ]),
]

LEGACY_OBJECT_SPECS = OBJECT_SPECS


def _sha256(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _git_source(path: str) -> str:
    return _git_blob(PRE_P0_REWRITE_SHA, path)


def _git_blob(sha: str, path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{sha}:{path}"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise ValueError(
            f"source inaccessible au SHA figé {sha}: {path}: {result.stderr.strip()}"
        )
    return result.stdout


# This manifest deliberately describes rendered curricular passages only.  The
# BEGIN-VERIFY blocks are inventoried separately as non-rendered technical
# oracles.  Counts are an independent fail-closed contract, not inferred from
# the mutable OBJECT_SPECS used by mutation tests.
EXPECTED_RENDERED_CLAIM_COUNTS = {
    "1SPE-SUITES-EX-026": 1, "1SPE-SUITES-CO-026": 5,
    "1SPE-SUITES-EX-031": 1, "1SPE-SUITES-CO-031": 2,
    "1SPE-SUITES-EX-038": 5, "1SPE-SUITES-CO-038": 5,
    "1SPE-SUITES-CO-044": 3, "1SPE-SUITES-CO-046": 8,
    "1SPE-SUITES-EX-048": 5, "1SPE-SUITES-CO-048": 11,
    "1SPE-SUITES-CO-049": 8, "1SPE-SUITES-CO-027": 1,
    "1SPE-SUITES-CO-037": 2, "1SPE-SUITES-EX-040": 3,
    "1SPE-SUITES-CO-040": 5, "1SPE-SUITES-EX-042": 3,
    "1SPE-SUITES-CO-042": 2, "1SPE-SUITES-EX-043": 3,
    "1SPE-SUITES-CO-043": 4,
}
EXPECTED_RENDERED_CLAIM_IDS = {
    f"{object_id}-C{index:02d}"
    for object_id, count in EXPECTED_RENDERED_CLAIM_COUNTS.items()
    for index in range(1, count + 1)
}
EXPECTED_RENDERED_CLAIM_COUNT = 77
EXPECTED_OPTIONAL_COUNT = 0
EXPECTED_RENDERED_CLAIM_DIGEST = (
    "sha256:95bbdd64c260723b71fd97b7fcd14fac401f8cdd55f82bdb9c89f1499a1b1afb"
)

# (line_start, line_end, claim policy, optional exact sub-passage)
RENDERED_CLAIM_LAYOUT: dict[str, list[tuple[int, int, str, str | None]]] = {
    "1SPE-SUITES-EX-026": [(30, 30, "log_prompt", None)],
    "1SPE-SUITES-CO-026": [
        (68, 70, "threshold_setup", None), (73, 83, "log_solver", None),
        (85, 85, "numeric_check", None), (87, 92, "numeric_check", None),
        (94, 94, "log_bareme", None),
    ],
    "1SPE-SUITES-EX-031": [(29, 31, "log_content", None)],
    "1SPE-SUITES-CO-031": [
        (58, 85, "log_content", None), (87, 87, "log_content_bareme", None),
    ],
    "1SPE-SUITES-EX-038": [
        (31, 33, "threshold_setup", None),
        (34, 34, "threshold_setup", "Montrer par essais successifs"),
        (34, 34, "log_prompt", "(ou en utilisant $\\log_{10}(0{,}88) \\approx -0{,}0555$ et $\\log_{10}(0{,}5) \\approx -0{,}301$)"),
        (34, 34, "threshold_setup", "que la valeur passe en dessous de $9\\,000$~\\euro{} lors de la $7^e$ année."),
        (35, 35, "threshold_setup", None),
    ],
    "1SPE-SUITES-CO-038": [
        (64, 70, "threshold_setup", None), (73, 80, "log_solver", None),
        (82, 82, "numeric_check", None), (84, 98, "numeric_check", None),
        (100, 100, "log_bareme", None),
    ],
    "1SPE-SUITES-CO-044": [
        (58, 62, "threshold_setup", None), (64, 69, "log_solver", None),
        (71, 75, "numeric_check", None),
    ],
    "1SPE-SUITES-CO-046": [
        (97, 99, "formal_convergence", None), (101, 101, "threshold_setup", None),
        (103, 103, "log_solver", None), (105, 109, "threshold_setup", None),
        (112, 118, "log_solver", None), (120, 120, "numeric_check", None),
        (122, 128, "numeric_check", None), (132, 132, "formal_convergence", None),
    ],
    "1SPE-SUITES-EX-048": [
        (50, 50, "first_spe_reasoning", None), (51, 51, "formal_prompt", None),
        (54, 54, "threshold_setup", None), (55, 55, "log_prompt", None),
        (57, 59, "formal_prompt", None),
    ],
    "1SPE-SUITES-CO-048": [
        (93, 93, "first_spe_reasoning", None), (95, 105, "formal_convergence", None),
        (107, 107, "threshold_setup", None), (109, 109, "log_solver", None),
        (111, 113, "threshold_setup", None), (115, 127, "log_solver", None),
        (130, 130, "numeric_check", None), (132, 138, "numeric_check", None),
        (142, 142, "formal_convergence", None), (144, 147, "first_spe_reasoning", None),
        (149, 154, "formal_convergence", None),
    ],
    "1SPE-SUITES-CO-049": [
        (87, 87, "threshold_setup", None), (89, 89, "log_solver", None),
        (91, 93, "threshold_setup", None), (95, 97, "log_solver", None),
        (100, 100, "numeric_check", None), (102, 104, "numeric_check", None),
        (179, 183, "formal_convergence", None), (185, 187, "first_spe_reasoning", None),
    ],
    "1SPE-SUITES-CO-027": [(89, 93, "formal_convergence", None)],
    "1SPE-SUITES-CO-037": [
        (84, 91, "first_spe_reasoning", None), (93, 93, "formal_convergence", None),
    ],
    "1SPE-SUITES-EX-040": [
        (35, 35, "intuitive_conjecture", None), (37, 41, "first_spe_reasoning", None),
        (43, 43, "formal_prompt", None),
    ],
    "1SPE-SUITES-CO-040": [
        (40, 42, "intuitive_conjecture", None), (44, 48, "first_spe_reasoning", None),
        (50, 50, "first_spe_reasoning", "\\textit{Interprétation.} La fonction $f(x) = \\dfrac{x^2+3}{2x}$ est la moyenne arithmétique de $x$ et $\\dfrac{3}{x}$, qui est la méthode de Héron pour approcher $\\sqrt{3}$.") ,
        (50, 50, "formal_convergence", "La suite converge vers le point fixe $\\sqrt{3}$ de $f$."),
        (79, 87, "formal_convergence", None),
    ],
    "1SPE-SUITES-EX-042": [
        (31, 31, "intuitive_conjecture", None), (38, 42, "first_spe_reasoning", None),
        (44, 44, "formal_prompt", None),
    ],
    "1SPE-SUITES-CO-042": [
        (55, 59, "first_spe_reasoning", None), (61, 61, "formal_convergence", None),
    ],
    "1SPE-SUITES-EX-043": [
        (39, 39, "intuitive_conjecture", None), (41, 50, "first_spe_reasoning", None),
        (53, 53, "formal_prompt", None),
    ],
    "1SPE-SUITES-CO-043": [
        (35, 35, "intuitive_conjecture", None), (37, 55, "first_spe_reasoning", None),
        (58, 72, "first_spe_reasoning", None), (74, 74, "formal_convergence", None),
    ],
}


def _rendered_object_specs() -> list[dict[str, Any]]:
    legacy = {row["object_id"]: row for row in LEGACY_OBJECT_SPECS}
    rendered: list[dict[str, Any]] = []
    for object_id in EXPECTED_UNION:
        base = legacy[object_id]
        source_lines = _git_source(base["path"]).splitlines(keepends=True)
        claims: list[dict[str, Any]] = []
        for index, (start, end, policy, passage) in enumerate(
            RENDERED_CLAIM_LAYOUT[object_id], start=1
        ):
            text = "".join(source_lines[start - 1 : end])
            claim = _claim(
                f"{object_id}-C{index:02d}", start, end, policy, _sha256(text)
            )
            if passage is not None:
                claim["passage_text"] = passage
                claim["passage_digest"] = _sha256(passage)
            claims.append(claim)
        rendered.append(_object(
            object_id, base["path"], base["source_digest"], claims
        ))
    return rendered


OBJECT_SPECS = _rendered_object_specs()
CANONICAL_OBJECTS = {row["object_id"]: copy.deepcopy(row) for row in OBJECT_SPECS}
CANONICAL_CLAIMS = {
    claim["claim_id"]: copy.deepcopy(claim)
    for row in OBJECT_SPECS for claim in row["claims"]
}

CLAIM_AWARE_OFFICIAL_ATOMS = {object_id: [] for object_id in EXPECTED_UNION}
for _object_id in (
    "1SPE-SUITES-EX-026", "1SPE-SUITES-CO-026", "1SPE-SUITES-EX-038",
    "1SPE-SUITES-CO-038", "1SPE-SUITES-CO-046", "1SPE-SUITES-EX-048",
    "1SPE-SUITES-CO-048",
):
    CLAIM_AWARE_OFFICIAL_ATOMS[_object_id] = ["1SPE-OFFICIAL-063"]
for _object_id in (
    "1SPE-SUITES-CO-037", "1SPE-SUITES-EX-040", "1SPE-SUITES-CO-040",
    "1SPE-SUITES-EX-043", "1SPE-SUITES-CO-043",
):
    CLAIM_AWARE_OFFICIAL_ATOMS[_object_id] = [
        "1SPE-OFFICIAL-053", "1SPE-OFFICIAL-059"
    ]


def _meta(source: str) -> dict[str, Any]:
    first_line = source.splitlines()[0]
    prefix = "% META: "
    if not first_line.startswith(prefix):
        raise ValueError("META absente de la première ligne")
    return json.loads(first_line[len(prefix) :])


def _finding(code: str, subject: str, detail: str) -> dict[str, str]:
    return {"code": code, "subject": subject, "detail": detail}


def _validate_source_freeze(
    pre_sha: str, integration_sha: str
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    valid: dict[str, bool] = {}
    for label, sha in (
        ("PRE_P0_REWRITE_SHA", pre_sha),
        ("CURRENT_INTEGRATION_SHA", integration_sha),
    ):
        result = subprocess.run(
            ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        valid[label] = result.returncode == 0
        if not valid[label]:
            findings.append(_finding(
                "SOURCE_FREEZE_SHA_INVALID", label,
                f"{sha} ne désigne pas un commit Git accessible",
            ))
    if all(valid.values()):
        relation = subprocess.run(
            ["git", "merge-base", "--is-ancestor", integration_sha, pre_sha],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if relation.returncode != 0:
            findings.append(_finding(
                "SOURCE_FREEZE_RELATION_INVALID", "source_freeze",
                f"{integration_sha} n'est pas ancêtre de {pre_sha}",
            ))
    return findings


def _load_and_validate_official_authority(
    *,
    pre_sha: str,
    atom_map: dict[str, list[str]],
    claim_specs: list[dict[str, Any]],
    authority_loader: Callable[[str, str], str],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], list[dict[str, str]]]:
    findings: list[dict[str, str]] = []
    raw_by_path: dict[str, str] = {}
    for path in (OFFICIAL_ATOMS_PATH, OFFICIAL_AUTHORITY_PATH):
        try:
            raw_by_path[path] = authority_loader(pre_sha, path)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            findings.append(_finding(
                "OFFICIAL_AUTHORITY_SOURCE_LOAD_FAILURE", path, str(exc)
            ))
            raw_by_path[path] = ""

    atoms_digest = _sha256(raw_by_path[OFFICIAL_ATOMS_PATH])
    authority_digest = _sha256(raw_by_path[OFFICIAL_AUTHORITY_PATH])
    for path, observed, expected in (
        (OFFICIAL_ATOMS_PATH, atoms_digest, EXPECTED_OFFICIAL_ATOMS_DIGEST),
        (
            OFFICIAL_AUTHORITY_PATH,
            authority_digest,
            EXPECTED_OFFICIAL_AUTHORITY_DIGEST,
        ),
    ):
        if observed != expected:
            findings.append(_finding(
                "OFFICIAL_AUTHORITY_SOURCE_DIGEST_MISMATCH", path,
                f"attendu={expected} observé={observed}",
            ))

    try:
        atoms_payload = json.loads(raw_by_path[OFFICIAL_ATOMS_PATH])
    except (json.JSONDecodeError, TypeError) as exc:
        findings.append(_finding(
            "OFFICIAL_AUTHORITY_SOURCE_PARSE_FAILURE", OFFICIAL_ATOMS_PATH, str(exc)
        ))
        atoms_payload = {"atoms": []}
    try:
        authority_payload = yaml.safe_load(raw_by_path[OFFICIAL_AUTHORITY_PATH]) or {}
    except yaml.YAMLError as exc:
        findings.append(_finding(
            "OFFICIAL_AUTHORITY_SOURCE_PARSE_FAILURE", OFFICIAL_AUTHORITY_PATH, str(exc)
        ))
        authority_payload = {}

    programme_authorities = (
        authority_payload.get("programme_d_enseignement", {})
        if isinstance(authority_payload, dict) else {}
    )
    first_authority = programme_authorities.get("1SPE", {})
    if first_authority.get("manual") != EXPECTED_OFFICIAL_MANUAL:
        findings.append(_finding(
            "OFFICIAL_AUTHORITY_MANUAL_MISMATCH", "1SPE",
            f"manual={first_authority.get('manual')}",
        ))
    if first_authority.get("official_ref") != EXPECTED_OFFICIAL_NOR:
        findings.append(_finding(
            "OFFICIAL_AUTHORITY_NOR_MISMATCH", "1SPE",
            f"official_ref={first_authority.get('official_ref')}",
        ))
    if (
        first_authority.get("effective_from") != EXPECTED_OFFICIAL_YEAR
        or first_authority.get("applicable_2026_2027") is not True
    ):
        findings.append(_finding(
            "OFFICIAL_AUTHORITY_YEAR_MISMATCH", "1SPE",
            "l'autorité doit être applicable à l'édition 2026-2027",
        ))

    atoms = {
        row.get("atom_id"): row
        for row in atoms_payload.get("atoms", [])
        if isinstance(row, dict) and row.get("atom_id")
    }
    authority_by_manual = {
        ("TSPE" if key == "TSPE_2026_2027" else key): value
        for key, value in programme_authorities.items()
        if isinstance(value, dict)
    }
    cited_ids = sorted(
        {atom for values in atom_map.values() for atom in values}
        | _cited_atom_ids(claim_specs)
    )
    evidence: dict[str, dict[str, Any]] = {}
    for atom_id in cited_ids:
        atom = atoms.get(atom_id)
        if atom is None:
            findings.append(_finding(
                "OFFICIAL_ATOM_NOT_FOUND", atom_id,
                f"absent de {OFFICIAL_ATOMS_PATH} au SHA figé",
            ))
            continue
        expected_manual = atom_id.split("-OFFICIAL-", 1)[0]
        cited_authority = authority_by_manual.get(expected_manual, {})
        if atom.get("manual") != expected_manual:
            findings.append(_finding(
                "OFFICIAL_ATOM_MANUAL_MISMATCH", atom_id,
                f"manual={atom.get('manual')}",
            ))
        if (
            not cited_authority
            or atom.get("authority_NOR") != cited_authority.get("official_ref")
        ):
            findings.append(_finding(
                "OFFICIAL_ATOM_NOR_MISMATCH", atom_id,
                f"authority_NOR={atom.get('authority_NOR')} autorité={cited_authority.get('official_ref')}",
            ))
        if (
            atom.get("effective_year") != cited_authority.get("effective_from")
            or atom.get("applicable_school_year") != EXPECTED_OFFICIAL_YEAR
            or cited_authority.get("applicable_2026_2027") is not True
        ):
            findings.append(_finding(
                "OFFICIAL_ATOM_YEAR_MISMATCH", atom_id,
                "effective_year et applicable_school_year doivent valoir 2026-2027",
            ))
        wording = atom.get("short_official_wording_or_paraphrase")
        if not isinstance(wording, str) or not wording.strip():
            findings.append(_finding(
                "OFFICIAL_ATOM_WORDING_INVALID", atom_id,
                "le libellé officiel ou sa paraphrase sourcée doit être non vide",
            ))
        evidence[atom_id] = {
            field: atom.get(field)
            for field in (
                "atom_id", "manual", "authority_NOR", "effective_year",
                "applicable_school_year", "official_page_or_anchor",
                "official_section", "short_official_wording_or_paraphrase",
            )
        }

    sources = {
        "source_sha": pre_sha,
        "atoms": {"path": OFFICIAL_ATOMS_PATH, "digest": atoms_digest},
        "authority": {
            "path": OFFICIAL_AUTHORITY_PATH, "digest": authority_digest
        },
    }
    return sources, evidence, findings


def _cited_atom_ids(specs: list[dict[str, Any]]) -> set[str]:
    cited: set[str] = set()
    pattern = re.compile(r"((?:1SPE|TSPE)-OFFICIAL-)(\d{3})(?:/(\d{3}))?")
    for row in specs:
        for claim in row.get("claims", []):
            authority = str(claim.get("official_authority", ""))
            for match in pattern.finditer(authority):
                cited.add(match.group(1) + match.group(2))
                if match.group(3):
                    cited.add(match.group(1) + match.group(3))
    return cited


def _rendered_claim_manifest_digest(specs: list[dict[str, Any]]) -> str:
    rows = sorted(
        (
            {
                "claim_id": claim.get("claim_id"),
                "line_start": claim.get("line_start"),
                "line_end": claim.get("line_end"),
                "line_range": claim.get("line_range"),
                "line_digest": claim.get("line_digest"),
                "passage_digest": claim.get("passage_digest"),
                "classification": claim.get("classification"),
                "reason": claim.get("reason"),
                "official_authority": claim.get("official_authority"),
                "replacement_strategy": claim.get("replacement_strategy"),
            }
            for row in specs for claim in row.get("claims", [])
        ),
        key=lambda row: str(row["claim_id"]),
    )
    serialized = json.dumps(
        rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return _sha256(serialized)


def _pair_stem(object_id: str) -> str:
    return object_id.replace("-EX-", "-").replace("-CO-", "-")


def _location_buckets(object_ids: set[str]) -> dict[str, Any]:
    student = sorted(item for item in object_ids if "-EX-" in item)
    teacher = sorted(item for item in object_ids if "-CO-" in item)
    student_stems = {_pair_stem(item) for item in student}
    teacher_stems = {_pair_stem(item) for item in teacher}
    return {
        "physical_source": {
            "STUDENT_STATEMENT": len(student),
            "TEACHER_CORRECTION": len(teacher),
        },
        "pair_scope": {
            "STUDENT_STATEMENT_ONLY": sorted(student_stems - teacher_stems),
            "CORRECTION_ONLY": sorted(teacher_stems - student_stems),
            "BOTH": sorted(student_stems & teacher_stems),
        },
    }


def build_forensics(
    *,
    specs: list[dict[str, Any]] | None = None,
    log_set: Iterable[str] | None = None,
    formal_set: Iterable[str] | None = None,
    source_loader: Callable[[str], str] | None = None,
    pre_sha: str = PRE_P0_REWRITE_SHA,
    integration_sha: str = CURRENT_INTEGRATION_SHA,
    atom_map: dict[str, list[str]] | None = None,
    authority_loader: Callable[[str, str], str] = _git_blob,
) -> dict[str, Any]:
    working_specs = copy.deepcopy(OBJECT_SPECS if specs is None else specs)
    active_atom_map = copy.deepcopy(
        CLAIM_AWARE_OFFICIAL_ATOMS if atom_map is None else atom_map
    )
    if source_loader is None:
        source_loader = lambda path: _git_blob(pre_sha, path)
    actual_log = set(LOG_OR_FORMAL_THRESHOLD_SET if log_set is None else log_set)
    actual_formal = set(
        FORMAL_LIMIT_CONVERGENCE_SET if formal_set is None else formal_set
    )
    actual_intersection = actual_log & actual_formal
    actual_union = actual_log | actual_formal
    expected_log = set(LOG_OR_FORMAL_THRESHOLD_SET)
    expected_formal = set(FORMAL_LIMIT_CONVERGENCE_SET)
    expected_union = set(EXPECTED_UNION)
    findings = _validate_source_freeze(pre_sha, integration_sha)
    if active_atom_map != CLAIM_AWARE_OFFICIAL_ATOMS:
        findings.append(_finding(
            "OFFICIAL_ATOM_MAPPING_MISMATCH", "CLAIM_AWARE_OFFICIAL_ATOMS",
            "la décision de mapping objet→atomes diffère du verrou canonique",
        ))
    authority_sources, official_atom_evidence, authority_findings = (
        _load_and_validate_official_authority(
            pre_sha=pre_sha,
            atom_map=active_atom_map,
            claim_specs=working_specs,
            authority_loader=authority_loader,
        )
    )
    findings.extend(authority_findings)

    if actual_log != expected_log or actual_formal != expected_formal:
        findings.append(_finding(
            "SET_IDENTITY_MISMATCH",
            "sets",
            "les deux ensembles doivent être exactement ceux du checkpoint humain",
        ))
    if actual_intersection != set(EXPECTED_INTERSECTION):
        findings.append(_finding(
            "INTERSECTION_MISMATCH",
            "INTERSECTION",
            f"attendu={sorted(EXPECTED_INTERSECTION)} observé={sorted(actual_intersection)}",
        ))
    if actual_union != expected_union:
        findings.append(_finding(
            "UNION_MISMATCH",
            "UNION",
            f"attendu={sorted(expected_union)} observé={sorted(actual_union)}",
        ))

    spec_ids = [row.get("object_id", "") for row in working_specs]
    if len(spec_ids) != len(set(spec_ids)) or set(spec_ids) != expected_union:
        findings.append(_finding(
            "OBJECT_SET_MISMATCH",
            "objects",
            f"attendu={sorted(expected_union)} observé={sorted(set(spec_ids))}",
        ))

    rendered_manifest_ids = [
        claim.get("claim_id", "")
        for row in working_specs
        for claim in row.get("claims", [])
    ]
    if (
        len(rendered_manifest_ids) != EXPECTED_RENDERED_CLAIM_COUNT
        or len(rendered_manifest_ids) != len(set(rendered_manifest_ids))
        or set(rendered_manifest_ids) != EXPECTED_RENDERED_CLAIM_IDS
    ):
        findings.append(_finding(
            "CLAIM_SET_MISMATCH",
            "rendered_claim_manifest",
            f"exactement {EXPECTED_RENDERED_CLAIM_COUNT} IDs rendus indépendamment verrouillés sont requis",
        ))
    manifest_digest = _rendered_claim_manifest_digest(working_specs)
    if manifest_digest != EXPECTED_RENDERED_CLAIM_DIGEST:
        findings.append(_finding(
            "CLAIM_MANIFEST_DIGEST_MISMATCH", "rendered_claim_manifest",
            f"attendu={EXPECTED_RENDERED_CLAIM_DIGEST} observé={manifest_digest}",
        ))

    objects: list[dict[str, Any]] = []
    technical_oracles: list[dict[str, Any]] = []
    unknown = 0
    for spec in working_specs:
        object_id = spec.get("object_id", "")
        canonical = CANONICAL_OBJECTS.get(object_id)
        if canonical and spec.get("student_teacher") != canonical["student_teacher"]:
            findings.append(_finding(
                "STUDENT_TEACHER_BUCKET_MISMATCH",
                object_id,
                "le rôle physique élève/correction ne correspond pas au manifeste canonique",
            ))
        if canonical and spec.get("path") != canonical["path"]:
            findings.append(_finding(
                "OBJECT_PATH_MISMATCH", object_id, "chemin différent du manifeste canonique"
            ))
        try:
            source = source_loader(spec["path"])
            meta = _meta(source)
        except (KeyError, ValueError, json.JSONDecodeError) as exc:
            findings.append(_finding("SOURCE_LOAD_FAILURE", object_id, str(exc)))
            continue

        actual_source_digest = _sha256(source)
        if canonical and spec.get("source_digest") != canonical["source_digest"]:
            findings.append(_finding(
                "SOURCE_DIGEST_MISMATCH", object_id, "digest source muté dans le manifeste"
            ))
        if actual_source_digest != spec.get("source_digest"):
            findings.append(_finding(
                "SOURCE_DIGEST_MISMATCH",
                object_id,
                f"attendu={spec.get('source_digest')} observé={actual_source_digest}",
            ))
        if meta.get("id") != object_id:
            findings.append(_finding(
                "SOURCE_OBJECT_ID_MISMATCH", object_id, f"META.id={meta.get('id')}"
            ))

        canonical_claim_ids = {
            claim["claim_id"] for claim in (canonical or {}).get("claims", [])
        }
        claim_ids = [claim.get("claim_id", "") for claim in spec.get("claims", [])]
        if len(claim_ids) != len(set(claim_ids)) or set(claim_ids) != canonical_claim_ids:
            findings.append(_finding(
                "CLAIM_SET_MISMATCH", object_id, "claims omis, dupliqués ou ajoutés"
            ))

        if canonical:
            canonical_has_keep = any(
                claim["classification"] == "KEEP_AS_IS" for claim in canonical["claims"]
            )
            observed_has_keep = any(
                claim.get("classification") == "KEEP_AS_IS"
                for claim in spec.get("claims", [])
            )
            if canonical_has_keep and not observed_has_keep:
                findings.append(_finding(
                    "WHOLE_OBJECT_OVERCLASSIFICATION",
                    object_id,
                    "des passages conformes KEEP_AS_IS ont été absorbés par une décision globale",
                ))

        source_lines = source.splitlines(keepends=True)
        begin_lines = [
            index for index, line in enumerate(source_lines, start=1)
            if line.rstrip("\n") == "% BEGIN-VERIFY"
        ]
        end_lines = [
            index for index, line in enumerate(source_lines, start=1)
            if line.rstrip("\n") == "% END-VERIFY"
        ]
        if len(begin_lines) != 1 or len(end_lines) != 1 or begin_lines[0] >= end_lines[0]:
            findings.append(_finding(
                "TECHNICAL_ORACLE_SCOPE_MISMATCH", object_id,
                "un unique bloc BEGIN-VERIFY/END-VERIFY ordonné est requis",
            ))
        else:
            oracle_start, oracle_end = begin_lines[0], end_lines[0]
            oracle_text = "".join(source_lines[oracle_start - 1 : oracle_end]).rstrip("\n")
            technical_oracles.append({
                "oracle_id": f"{object_id}-TECHNICAL-ORACLE",
                "object_id": object_id,
                "path": spec["path"],
                "line_start": oracle_start,
                "line_end": oracle_end,
                "line_range": f"{oracle_start}-{oracle_end}",
                "oracle_digest": _sha256("".join(source_lines[oracle_start - 1 : oracle_end])),
                "current_oracle": oracle_text,
                "classification": "NON_RENDERED_ORACLE_KEEP",
                "source_sha": pre_sha,
            })
        rendered_claims: list[dict[str, Any]] = []
        for claim in spec.get("claims", []):
            claim_id = claim.get("claim_id", "")
            canonical_claim = CANONICAL_CLAIMS.get(claim_id)
            start = claim.get("line_start")
            end = claim.get("line_end")
            if canonical_claim and (start, end) != (
                canonical_claim["line_start"],
                canonical_claim["line_end"],
            ):
                findings.append(_finding(
                    "CLAIM_LINE_MISMATCH", claim_id, "plage de lignes différente du verrou"
                ))
            expected_line_range = f"{start}-{end}"
            if (
                claim.get("line_range") != expected_line_range
                or (
                    canonical_claim
                    and claim.get("line_range") != canonical_claim.get("line_range")
                )
            ):
                findings.append(_finding(
                    "CLAIM_LINE_RANGE_MISMATCH", claim_id,
                    "line_range doit correspondre aux bornes et au verrou canonique",
                ))
            if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start or end > len(source_lines):
                findings.append(_finding(
                    "CLAIM_LINE_MISMATCH", claim_id, "plage de lignes invalide"
                ))
                statement = "<INVALID_LINE_RANGE>"
                actual_line_digest = _sha256(statement)
            else:
                statement = "".join(source_lines[start - 1 : end]).rstrip("\n")
                actual_line_digest = _sha256("".join(source_lines[start - 1 : end]))

            passage = claim.get("passage_text")
            passage_digest = None
            if passage is not None:
                if statement.count(passage) != 1:
                    findings.append(_finding(
                        "CLAIM_PASSAGE_MISMATCH", claim_id,
                        "le sous-passage exact doit apparaître une seule fois dans la plage verrouillée",
                    ))
                statement = passage
                passage_digest = _sha256(passage)
                if claim.get("passage_digest") != passage_digest:
                    findings.append(_finding(
                        "CLAIM_DIGEST_MISMATCH", claim_id,
                        "digest du sous-passage différent du verrou",
                    ))

            if canonical_claim and claim.get("line_digest") != canonical_claim["line_digest"]:
                findings.append(_finding(
                    "CLAIM_DIGEST_MISMATCH", claim_id, "digest de claim différent du verrou"
                ))
            if claim.get("line_digest") != actual_line_digest:
                findings.append(_finding(
                    "CLAIM_DIGEST_MISMATCH",
                    claim_id,
                    f"attendu={claim.get('line_digest')} observé={actual_line_digest}",
                ))
            classification = claim.get("classification")
            if classification not in ALLOWED_CLASSIFICATIONS:
                unknown += 1
                findings.append(_finding(
                    "UNKNOWN_CLASSIFICATION", claim_id, f"classification={classification}"
                ))
            if canonical_claim and classification != canonical_claim["classification"]:
                findings.append(_finding(
                    "CLAIM_CLASSIFICATION_MISMATCH",
                    claim_id,
                    "classification différente de la décision canonique claim-level",
                ))
            if canonical_claim and claim.get("official_authority") != canonical_claim["official_authority"]:
                findings.append(_finding(
                    "CLAIM_AUTHORITY_MISMATCH",
                    claim_id,
                    "autorité officielle différente du verrou canonique",
                ))
            if canonical_claim and claim.get("reason") != canonical_claim["reason"]:
                findings.append(_finding(
                    "CLAIM_REASON_MISMATCH", claim_id,
                    "motif éditorial différent du verrou canonique",
                ))
            if canonical_claim and claim.get("replacement_strategy") != canonical_claim["replacement_strategy"]:
                findings.append(_finding(
                    "CLAIM_REPLACEMENT_STRATEGY_MISMATCH", claim_id,
                    "stratégie de remplacement différente du verrou canonique",
                ))
            rendered_claims.append({
                "claim_id": claim_id,
                "line_start": start,
                "line_end": end,
                "line_range": claim.get("line_range"),
                "line_digest": claim.get("line_digest"),
                "passage_digest": passage_digest,
                "current_statement_or_reasoning": statement,
                "classification": classification,
                "reason": claim.get("reason", ""),
                "official_authority": claim.get("official_authority", ""),
                "replacement_strategy": claim.get("replacement_strategy", ""),
            })

        capacities = list(meta.get("capacites_codes", []))
        objects.append({
            "object_id": object_id,
            "path": spec["path"],
            "object_type": meta.get("type_objet"),
            "student_teacher": spec.get("student_teacher"),
            "capacities": capacities,
            "official_atoms": active_atom_map.get(object_id, []),
            "source_sha": pre_sha,
            "source_digest": spec.get("source_digest"),
            "set_membership": [
                name
                for name, members in (
                    ("LOG_OR_FORMAL_THRESHOLD_SET", actual_log),
                    ("FORMAL_LIMIT_CONVERGENCE_SET", actual_formal),
                )
                if object_id in members
            ],
            "claims": rendered_claims,
        })

    rendered_claims_flat = [claim for row in objects for claim in row["claims"]]
    classification_counts = {
        classification: sum(
            claim.get("classification") == classification
            for claim in rendered_claims_flat
        )
        for classification in ALLOWED_CLASSIFICATIONS
    }
    optional_count = classification_counts["OPTIONAL_TERMINALE_EXTENSION"]
    if optional_count != EXPECTED_OPTIONAL_COUNT:
        findings.append(_finding(
            "OPTIONAL_COUNT_MISMATCH", "rendered_claim_manifest",
            f"attendu={EXPECTED_OPTIONAL_COUNT} observé={optional_count}",
        ))
    if len(technical_oracles) != len(expected_union):
        findings.append(_finding(
            "TECHNICAL_ORACLE_COUNT_MISMATCH", "technical_oracles",
            f"attendu={len(expected_union)} observé={len(technical_oracles)}",
        ))
    summary = {
        "status": "RED" if findings else "PASS",
        "log_or_formal_threshold_count": len(actual_log),
        "formal_limit_convergence_count": len(actual_formal),
        "intersection_count": len(actual_intersection),
        "union_count": len(actual_union),
        "rendered_claim_count": len(rendered_claims_flat),
        "technical_oracle_count": len(technical_oracles),
        "keep_as_is_count": classification_counts["KEEP_AS_IS"],
        "rewrite_to_1spe_count": classification_counts["REWRITE_TO_1SPE"],
        "optional_terminale_extension_count": optional_count,
        "delete_invalid_count": classification_counts["DELETE_INVALID"],
        "unknown": unknown,
        "finding_count": len(findings),
    }
    return {
        "artifact": "1SPE_SUITES_WRONG_YEAR_P0_FORENSICS",
        "source_freeze": {
            "PRE_P0_REWRITE_SHA": pre_sha,
            "CURRENT_INTEGRATION_SHA": integration_sha,
            "relationship": SOURCE_RELATIONSHIP,
        },
        "official_authority_sources": authority_sources,
        "official_atom_evidence": official_atom_evidence,
        "scope_note": (
            "Union physique exacte du checkpoint humain. Les occurrences voisines, notamment "
            "évaluations, cours contextualisé et autres EX/CO, restent hors de ce rapport et "
            "devront être auditées séparément sans élargissement implicite."
        ),
        "rendered_claim_manifest_digest": manifest_digest,
        "sets": {
            "LOG_OR_FORMAL_THRESHOLD_SET": sorted(actual_log),
            "FORMAL_LIMIT_CONVERGENCE_SET": sorted(actual_formal),
            "INTERSECTION": sorted(actual_intersection),
            "UNION": sorted(actual_union),
        },
        "location_buckets": _location_buckets(expected_union),
        "summary": summary,
        "objects": objects,
        "technical_oracles": technical_oracles,
        "findings": findings,
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Forensic P0 wrong-year — 1SPE-SUITES",
        "",
        f"- Statut : **{summary['status']}**",
        f"- `PRE_P0_REWRITE_SHA` : `{payload['source_freeze']['PRE_P0_REWRITE_SHA']}`",
        f"- `CURRENT_INTEGRATION_SHA` : `{payload['source_freeze']['CURRENT_INTEGRATION_SHA']}`",
        f"- Relation : `{payload['source_freeze']['relationship']}`",
        f"- Objets : `{summary['union_count']}` ; claims rendus : `{summary['rendered_claim_count']}` ; oracles techniques non rendus : `{summary['technical_oracle_count']}` ; `UNKNOWN={summary['unknown']}`",
        f"- Dispositions rendues : `KEEP={summary['keep_as_is_count']}` ; `REWRITE={summary['rewrite_to_1spe_count']}` ; `OPTIONAL={summary['optional_terminale_extension_count']}` ; `DELETE={summary['delete_invalid_count']}`",
        "",
        payload["scope_note"],
        "",
        "## Autorité officielle figée",
        "",
        f"- Registre d'atomes : `{payload['official_authority_sources']['atoms']['path']}` / `{payload['official_authority_sources']['atoms']['digest']}`",
        f"- Registre d'autorité : `{payload['official_authority_sources']['authority']['path']}` / `{payload['official_authority_sources']['authority']['digest']}`",
        f"- SHA de lecture : `{payload['official_authority_sources']['source_sha']}`",
        "",
    ]
    for atom_id, atom in sorted(payload["official_atom_evidence"].items()):
        lines.append(
            f"- `{atom_id}` — `{atom['manual']}` / `{atom['authority_NOR']}` / "
            f"`{atom['effective_year']}` — {atom['short_official_wording_or_paraphrase']}"
        )
    lines.extend([
        "",
        "## Algèbre exacte",
        "",
        f"- `LOG_OR_FORMAL_THRESHOLD_SET={summary['log_or_formal_threshold_count']}`",
        f"- `FORMAL_LIMIT_CONVERGENCE_SET={summary['formal_limit_convergence_count']}`",
        f"- `INTERSECTION={summary['intersection_count']}`",
        f"- `UNION={summary['union_count']}`",
        "",
    ])
    for name in (
        "LOG_OR_FORMAL_THRESHOLD_SET",
        "FORMAL_LIMIT_CONVERGENCE_SET",
        "INTERSECTION",
        "UNION",
    ):
        lines.extend((f"### {name}", "", ", ".join(f"`{item}`" for item in payload["sets"][name]), ""))

    lines.extend(("## Objets et claims", ""))
    for row in payload["objects"]:
        official_atoms = ", ".join(
            f"`{item}`" for item in row["official_atoms"]
        ) or "aucun"
        lines.extend((
            f"### {row['object_id']}",
            "",
            f"- Chemin : `{row['path']}`",
            f"- Type / rôle : `{row['object_type']}` / `{row['student_teacher']}`",
            f"- Capacités : {', '.join(f'`{item}`' for item in row['capacities'])}",
            f"- Atomes officiels : {official_atoms}",
            f"- Source : `{row['source_sha']}` / `{row['source_digest']}`",
            f"- Ensembles : {', '.join(f'`{item}`' for item in row['set_membership'])}",
            "",
            "| Claim | Lignes | Digest | Passage courant | Classification | Motif | Autorité | Stratégie |",
            "|---|---:|---|---|---|---|---|---|",
        ))
        for claim in row["claims"]:
            lines.append(
                "| "
                + " | ".join(
                    _cell(value)
                    for value in (
                        f"`{claim['claim_id']}`",
                        claim["line_range"],
                        f"`{claim['line_digest']}`",
                        claim["current_statement_or_reasoning"],
                        f"`{claim['classification']}`",
                        claim["reason"],
                        claim["official_authority"],
                        claim["replacement_strategy"],
                    )
                )
                + " |"
            )
        lines.append("")

    lines.extend(("## Oracles techniques non rendus", ""))
    for oracle in payload["technical_oracles"]:
        lines.append(
            f"- `{oracle['oracle_id']}` — lignes `{oracle['line_range']}` — "
            f"`{oracle['oracle_digest']}` — `{oracle['classification']}`"
        )
    lines.append("")

    lines.extend(("## Findings", ""))
    if payload["findings"]:
        for finding in payload["findings"]:
            lines.append(f"- `{finding['code']}` — `{finding['subject']}` — {finding['detail']}")
    else:
        lines.append("Aucun finding structurel : algèbre, sources, claims, digests et classifications sont verrouillés.")
    lines.append("")
    return "\n".join(lines)


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


@contextmanager
def _exclusive_lock(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


@contextmanager
def _shared_lock(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_SH)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _validate_canonical_outputs(outputs: dict[Path, str]) -> None:
    if set(outputs) != {JSON_OUTPUT, MD_OUTPUT}:
        raise ValueError("bundle must contain exactly the canonical JSON and MD outputs")


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


def commit_output_bundle(
    outputs: dict[Path, str],
    *,
    replace_func: Callable[[str | os.PathLike[str], str | os.PathLike[str]], Any] = os.replace,
) -> None:
    _validate_canonical_outputs(outputs)
    parents = {target.parent.resolve() for target in outputs}
    if len(parents) != 1:
        raise ValueError("all bundle outputs must share one directory")
    parent = next(iter(parents))
    with _exclusive_lock(LOCK_PATH):
        staging = Path(tempfile.mkdtemp(prefix=".1spe-wrong-year-p0-", dir=parent))
        staged: dict[Path, Path] = {}
        backups: dict[Path, Path | None] = {}
        attempted: list[Path] = []
        preserve_staging = False
        try:
            targets = sorted(outputs, key=lambda path: path.name)
            for index, target in enumerate(targets):
                content = outputs[target]
                staged_path = staging / f"new-{index}-{target.name}"
                with staged_path.open("w", encoding="utf-8") as handle:
                    handle.write(content)
                    handle.flush()
                    os.fsync(handle.fileno())
                staged[target] = staged_path
                if target.exists():
                    backup = staging / f"old-{index}-{target.name}"
                    shutil.copy2(target, backup)
                    with backup.open("rb") as handle:
                        os.fsync(handle.fileno())
                    backups[target] = backup
                else:
                    backups[target] = None
            _fsync_directory(staging)
            try:
                for target in targets:
                    attempted.append(target)
                    replace_func(staged[target], target)
                _fsync_directory(parent)
            except BaseException as installation_error:
                rollback_errors: list[BaseException] = []
                for target in reversed(attempted):
                    try:
                        backup = backups[target]
                        if backup is None:
                            target.unlink(missing_ok=True)
                        else:
                            replace_func(backup, target)
                    except BaseException as rollback_error:
                        rollback_errors.append(rollback_error)
                try:
                    _fsync_directory(parent)
                except BaseException as rollback_sync_error:
                    rollback_errors.append(rollback_sync_error)
                if rollback_errors:
                    preserve_staging = True
                    raise OutputBundleRecoveryError(
                        staging, rollback_errors
                    ) from installation_error
                raise
        finally:
            if not preserve_staging:
                shutil.rmtree(staging, ignore_errors=True)
                _fsync_directory(parent)


def check_output_bundle(outputs: dict[Path, str]) -> list[Path]:
    _validate_canonical_outputs(outputs)
    with _shared_lock(LOCK_PATH):
        return [
            path
            for path, expected in outputs.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != expected
        ]


def _build_outputs() -> tuple[dict[str, Any], dict[Path, str]]:
    payload = build_forensics()
    return payload, {
        JSON_OUTPUT: render_json(payload),
        MD_OUTPUT: render_markdown(payload),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="vérifie les deux sorties fixes sans écrire")
    args = parser.parse_args(argv)
    payload, outputs = _build_outputs()
    if payload["summary"]["status"] != "PASS":
        print(render_json(payload))
        return 1
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path in check_output_bundle(outputs)]
        if stale:
            print("STALE: " + ", ".join(stale))
            return 1
        print(
            f"PASS: {payload['summary']['union_count']} objects, "
            f"{payload['summary']['rendered_claim_count']} rendered claims, "
            f"{payload['summary']['technical_oracle_count']} technical oracles, "
            "UNKNOWN=0, outputs deterministic"
        )
        return 0
    commit_output_bundle(outputs)
    print("WROTE: " + ", ".join(str(path.relative_to(ROOT)) for path in outputs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
