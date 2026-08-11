"""Contrat executable du protocole de revue scientifique et pedagogique 1NSI."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import time
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "review_1nsi_content.py"
POLICY_PATH = ROOT / "audit" / "1NSI_CONTENT_REVIEW_POLICY.yaml"
SCHEMA_PATH = ROOT / "audit" / "schemas" / "v1" / "1nsi-content-review.schema.json"
FINDINGS_PATH = ROOT / "audit" / "1NSI_CONTENT_REVIEW_FINDINGS.yaml"
ACTOR_PROVENANCE_PATH = (
    ROOT / "audit" / "reviews" / "1nsi" / "2026-08-11-actor-provenance.yaml"
)
CONTRACT_RECEIPT_PATH = (
    ROOT / "audit" / "reviews" / "1nsi" / "runs" / "2026-08-10-contracts.yaml"
)
ALGORITHM_RECEIPT_PATH = (
    ROOT / "audit" / "reviews" / "1nsi" / "runs" / "2026-08-10-algorithms.yaml"
)
SECOND_REVIEWER_ID = "019febc0-6f71-7a92-a196-d579889d7e6e"
C3_REVIEWER_ID = "019fec35-2ae8-7051-be21-6b3754d1f688"
C3_REVIEW_RUN_ID = "1nsi-objects-algorithms-2026-08-10-c3-review-019fec35-v1"
C3_REVIEWER_MODEL = "codex-gpt5"
PRE_C3_REVIEWER_IDS = {
    "019feb3f-cd89-7242-9a84-6fafbc77e0d8",
    "019feb71-27c9-7530-ab01-ce74cea1b4a2",
    "019feb71-89a9-77b3-9103-ad05eacf18ca",
    "019feb72-1592-7900-b0b1-02fae59a6a39",
    "019feb72-7252-77a1-b864-775b021ed954",
    "019feb72-ceeb-7d72-9abd-de60ca43316e",
    SECOND_REVIEWER_ID,
}
PRE_C3_REVIEW_RUN_IDS = {
    "1nsi-contracts-2026-08-10-plato-reattestation-v2",
    "1nsi-objects-algorithms-2026-08-10-bernoulli-v1",
    "1nsi-objects-algorithms-2026-08-10-second-review-019febc0-v1",
    "1nsi-objects-data-basics-tables-2026-08-10-chandrasekhar-v1",
    "1nsi-objects-language-project-2026-08-10-lorentz-v1",
    "1nsi-objects-systems-web-2026-08-10-boyle-v1",
    "1nsi-objects-types-construits-2026-08-10-epicurus-v1",
}
ALGORITHM_SOURCE_COMMIT = "30f4e1b429ad7006ac34d0ac720e5bc0db608f71"
ALGORITHM_RECEIPT_COMMIT = "bdd80c4f52e122b2c1954ea3771d151829df6630"
ALGORITHM_RECEIPT_SHA256 = (
    "sha256:25dc602d9dd6251e49cfee8c3eae7fd65dee8af7d329a6b09e57a770ac8c3190"
)
ALGORITHM_REVIEW_RUN_ID = C3_REVIEW_RUN_ID
ALGORITHM_REVIEWER_MODEL = "codex-gpt5"
OLD_ALGORITHM_REVIEWER_ID = "019feb71-27c9-7530-ab01-ce74cea1b4a2"
OLD_ALGORITHM_REVIEW_RUN_ID = "1nsi-objects-algorithms-2026-08-10-bernoulli-v1"
CONTRACT_RECEIPT_COMMIT = "c5ab5d4607eb38b41e5824561aad1c7a8abcb275"
CONTRACT_RECEIPT_SHA256 = (
    "sha256:302ab9747f528753ada5fbba7fa4ab7810bd02eddc64a12e433ef54386734162"
)
PRE_TEN_P0_BASE_SHA = "7afc4b4e9dffa6fe9c2a5c46833e490df0026a6d"
PRE_ADGK_BASE_SHA = "086c5b2086335d6f6e3b3f059f938a6cf41a088f"
PRE_OPTIMIZATION_BASE_SHA = "ef28edb826a3389150a8d88bd6eb017ddc83251a"
PRE_PRECONDITION_BASE_SHA = "ef8d1db888807370f46693547139df9e7512c811"
PRE_EXECUTION_RECEIPT_BASE_SHA = "d1defc745c605fe80d8b4cdbb3eaceaed1d2fae0"
PRE_LANGUAGE_RECEIPT_BASE_SHA = "98bcf780e0a788603ffed0a4ad3c123de1858f77"
PRE_COPY_RECEIPT_BASE_SHA = "4239262b3f436cc76f4cd9936eedcbf389c31425"
PRE_SEPARATION_LOCK_BASE_SHA = "775bfc90cbd26a4aac8494bfbf3757703442ab45"
PRE_LANGUAGE_TRACE_BASE_SHA = "0085e91405c96ece34a1f5e40b6d8af8347dbc49"
PRE_SIX_P0_BASE_SHA = "7cb8ad6ba526a7d53ad3dd9a804dcea581e32812"
PRE_ACTOR_PROVENANCE_BASE_SHA = "1fc0bf5d74fa11db657c5d53fdb7e3983368bde9"
PRE_COUNTER_REVIEW_BASE_SHA = "ba9d2196fbbaaf6f8dd36311187a8c8261dd278d"
BASE_SHA = "f0c1a095288e000fa014653afc7f60f5c2b0b273"
PRE_BUILD_MANIFEST_PROTOCOL_DIGEST = (
    "sha256:66fb1d8fa7a6b8699fa291bf57b935c2d21f9c573cb9158d5c0a10797f6825f9"
)
PRE_TEN_P0_PROTOCOL_DIGEST = (
    "sha256:ccf155dc42c557a0b2b684267adee402d5886c944cac07baff4295f38c751e51"
)
TEN_P0_PROTOCOL_DIGEST = (
    "sha256:1467725d0bf734b28becae772d3c966f00c3a1dd984e2aec1c164b25d36911e3"
)
ADGK_PROTOCOL_DIGEST = (
    "sha256:23951bfd3d842e6d417100ab84b9e0aa976333a1cee2526374002b3de7701c47"
)
PRE_ADGK_POLICY_COMMIT = "113539aadd376b9e4e5c3b9a351207b099c08253"
OPTIMIZATION_PROTOCOL_DIGEST = (
    "sha256:0f43741f48ac3b6bc5a7c776f89cedf806d73519ce35b4533f1d62bec0a64f04"
)
PRE_OPTIMIZATION_POLICY_COMMIT = "b8a5b987e2d7942ae984abb9d013883e420c18c8"
PRECONDITION_PROTOCOL_DIGEST = (
    "sha256:f36df9b5cf24a8d597720a8a0a4450c54b3e24df8ab02b43cefda1e6e750bcc2"
)
PRE_PRECONDITION_POLICY_COMMIT = "54482def7e75f981a8e4e9c935c698ff69584374"
EXECUTION_RECEIPT_PROTOCOL_DIGEST = (
    "sha256:8bd253c35a3fcc2f28a3adfccb8398e8d6cfe302c90ca91db2be81f8fa3cfccc"
)
PRE_EXECUTION_RECEIPT_POLICY_COMMIT = "482670a4ea94a24b4cfeadc33857d0ad4e5577b6"
LANGUAGE_RECEIPT_PROTOCOL_DIGEST = (
    "sha256:e707d598cfeca9cb5a054d5d9617233c30d8a89c3a0ab912191cbb18715e036d"
)
PRE_LANGUAGE_RECEIPT_POLICY_COMMIT = "08244ef71a0a947e634e4eeb2320f9d2792c68f0"
COPY_RECEIPT_PROTOCOL_DIGEST = (
    "sha256:b6fb227985632e64b9c9d5af0bc1492ece1e411b1c1b25339bf0c35361a518ff"
)
PRE_COPY_RECEIPT_POLICY_COMMIT = "9a60daf4850e6bdbe7bd25c6e082da7310633514"
SEPARATION_LOCK_PROTOCOL_DIGEST = (
    "sha256:ca320655b09895e60930f9ec0f04c5794faf11e80bf89712a67575c0471fe25a"
)
PRE_SEPARATION_LOCK_POLICY_COMMIT = "de82f7d2f457875056ffbe534f1922862bdf5986"
LANGUAGE_TRACE_PROTOCOL_DIGEST = (
    "sha256:9fb019e749096a244a0f5565ef31e01b69e4f81f38af3a4f7449abbfd3058555"
)
PRE_LANGUAGE_TRACE_POLICY_COMMIT = "21f3faeadd80016476f7a65cf66620046f940890"
SIX_P0_PROTOCOL_DIGEST = (
    "sha256:f1dacc0230ee6b2fe898c6f7b728af7ad72b3f44b00f653cacadb05245080b57"
)
ACTOR_PROVENANCE_PROTOCOL_DIGEST = (
    "sha256:40cb76f9b329a7f38b5e3d6580146c0578439f4a004a2c2c1c6e66f9f076b064"
)
COUNTER_REVIEW_PROTOCOL_DIGEST = (
    "sha256:8127337d665962e008eb129348ddb29f59df1e666503d73929bdb644ddf30f28"
)
GOVERNANCE_REVIEWER_MODEL = "gpt-5.6-sol"
SIX_RESOLVED_P0_IDS = {
    "1NSI-REV-ARCH-C1-DIAGRAM-FLOWS",
    "1NSI-REV-RES-IHM-COURSE",
    "1NSI-REV-TAB-CO-005-COLLISION-COLONNES",
    "1NSI-REV-TAB-CO-005-FUSION-DOUBLONS",
    "1NSI-REV-TB-RE-C3-CORRIGE-EGALITE-FLOTTANTS",
    "1NSI-REV-WEB-POST-LOGS-CO004",
}
SIX_P0_ATTESTATION_PATHS = {
    "audit/reviews/1nsi/p0/2026-08-11-architecture-flux-von-neumann.yaml",
    "audit/reviews/1nsi/p0/2026-08-11-reseaux-ihm-thermostat.yaml",
    "audit/reviews/1nsi/p0/2026-08-11-tables-fusion-collisions.yaml",
    "audit/reviews/1nsi/p0/2026-08-11-tables-fusion-doublons.yaml",
    "audit/reviews/1nsi/p0/2026-08-11-types-base-egalite-flottants.yaml",
    "audit/reviews/1nsi/p0/2026-08-11-web-post-portee.yaml",
}
PRE_SIX_P0_POLICY_COMMIT = "563680078cb336766c2f892a8fc72539eea90fbe"
PRE_SIX_P0_RECEIPTS_COMMIT = "e32d4cf6de9bac9b722eb1b4f6ec94968c1d2e8d"
PRE_ACTOR_PROVENANCE_POLICY_COMMIT = "1329a4217a6d1d920a3e62ff5cc845579dedbf30"
PRE_ACTOR_PROVENANCE_RECEIPTS_COMMIT = "bbea8bd7d13c67dd7618c2bde8cd4a8929307555"
PRE_COUNTER_REVIEW_POLICY_COMMIT = "f0c1a095288e000fa014653afc7f60f5c2b0b273"
PRE_TEN_P0_POLICY_COMMIT = "372d8ad8d80d977f70d32cc30aabc8bf9fe6f723"
POLICY_COMMIT = "6fdd04b2e8e68a77fd27cdd630284a14a029ee14"
RECEIPTS_COMMIT = "60847229983f6712d1ed7f36791a0037ca5b5282"
CURRENT_RECEIPT_SEALS = {
    "audit/reviews/1nsi/runs/2026-08-10-algorithms.yaml": (
        "sha256:1a02fa37a9c45b1cbef5c30ff8e95893e1faaca672c5b473ef511b788a0b4066"
    ),
    "audit/reviews/1nsi/runs/2026-08-10-contracts.yaml": (
        "sha256:5dd69794cad89b5f89a5a0a2148c6d7da1cde56926232d96078bdb4dd539f23b"
    ),
    "audit/reviews/1nsi/runs/2026-08-10-data-basics-tables.yaml": (
        "sha256:3afebc4c6263ad9e5b454f17615136addd5584c5c669fee715793ca1c3ad46c6"
    ),
    "audit/reviews/1nsi/runs/2026-08-10-language-project.yaml": (
        "sha256:71c853c987a94bebc15fe9a5061a9b08406f8b43255f4926e1efe678e80a8fa7"
    ),
    "audit/reviews/1nsi/runs/2026-08-10-systems-web.yaml": (
        "sha256:232ccb9335a13d5593df033a8a5938137a7144cb19062a210ba73460d462474c"
    ),
    "audit/reviews/1nsi/runs/2026-08-10-types-construits.yaml": (
        "sha256:057995e913387674e6f9a52b8cc501355d4a0c4e90b373880ba3b080265867dc"
    ),
}
PRE_TEN_P0_RECEIPTS_COMMIT = "c101f539668d48ba6e2e9d32e5cf68e3dc64f872"
PRE_TEN_P0_RECEIPT_SEALS = {
    "audit/reviews/1nsi/runs/2026-08-10-algorithms.yaml": (
        "sha256:bed9bc079bc621ec3ab67da234d274f540963090a294efa1290782d326bba872"
    ),
    "audit/reviews/1nsi/runs/2026-08-10-contracts.yaml": (
        "sha256:9946804b5f5a7af0b5f1d4f0b53e1a871cb65c760b3150b22d24286ac19b5797"
    ),
    "audit/reviews/1nsi/runs/2026-08-10-data-basics-tables.yaml": (
        "sha256:1248d76e4926f2688a64497e2c0b2177f461f168d8c2b6bc3b0f76b7359e0f1a"
    ),
    "audit/reviews/1nsi/runs/2026-08-10-language-project.yaml": (
        "sha256:0263aa85f9f7d18b6262819fb7ba113c3c804d38e0f5939c7f5c3d05a844fb26"
    ),
    "audit/reviews/1nsi/runs/2026-08-10-systems-web.yaml": (
        "sha256:5c13f4527855d90c84490392263b3b58d0f9f4e7330ab9e6b2ec6ea99a415373"
    ),
    "audit/reviews/1nsi/runs/2026-08-10-types-construits.yaml": (
        "sha256:7de97aac1c10c6bcd17bd5b1117148abddad957c9155e6ab5e23fbd6a97f91e4"
    ),
}
GOVERNANCE_REVIEW_CONFIG = {
    "audit/reviews/1nsi/runs/2026-08-10-contracts.yaml": {
        "reviewer_id": "019ff06c-1355-7cb3-84fd-fa8b6398357a",
        "review_run_id": "1nsi-contracts-2026-08-11-actor-provenance-019ff06c-v2",
        "previous_reviewed_at": "2026-08-11T10:30:45+01:00",
        "reviewed_at": "2026-08-11T12:15:00+01:00",
    },
    "audit/reviews/1nsi/runs/2026-08-10-algorithms.yaml": {
        "reviewer_id": "019ff06c-13e1-79b3-837c-fa66c123609f",
        "review_run_id": (
            "1nsi-objects-algorithms-2026-08-11-counter-review."
            "62d88c4a-8e3b-4f2c-9c45-e58336c1396b-v2"
        ),
        "previous_reviewed_at": "2026-08-11T10:31:31+01:00",
        "reviewed_at": "2026-08-11T12:16:33+01:00",
    },
    "audit/reviews/1nsi/runs/2026-08-10-systems-web.yaml": {
        "reviewer_id": "019ff06c-14b7-70c0-8106-cb6a133181d0",
        "review_run_id": (
            "1nsi-objects-systems-web-2026-08-11-counter-review-"
            "9a634c32-df8b-4f1f-857a-7a4c8a50a2c9-v2"
        ),
        "previous_reviewed_at": "2026-08-11T10:32:28+01:00",
        "reviewed_at": "2026-08-11T12:13:04+01:00",
    },
    "audit/reviews/1nsi/runs/2026-08-10-language-project.yaml": {
        "reviewer_id": "019ff06c-1446-7f42-8d98-326189198929",
        "review_run_id": (
            "1nsi-objects-language-project-2026-08-11-actor-provenance-"
            "019ff06c-1446-7f42-8d98-326189198929-v2"
        ),
        "previous_reviewed_at": "2026-08-11T10:32:42+01:00",
        "reviewed_at": "2026-08-11T12:13:05+01:00",
    },
    "audit/reviews/1nsi/runs/2026-08-10-data-basics-tables.yaml": {
        "reviewer_id": "019ff06c-1816-7bc2-8903-91b3e638556e",
        "review_run_id": (
            "1nsi-data-basics-tables-20260811T111530Z-"
            "635c7730-a034-4e57-992e-934a3a6e9dbf-v2"
        ),
        "previous_reviewed_at": "2026-08-11T10:30:35+01:00",
        "reviewed_at": "2026-08-11T12:15:30+01:00",
    },
    "audit/reviews/1nsi/runs/2026-08-10-types-construits.yaml": {
        "reviewer_id": "019ff06c-17cb-7270-8842-5d873cb89437",
        "review_run_id": (
            "1nsi-objects-types-construits-2026-08-11-final-019ff06c-v2"
        ),
        "previous_reviewed_at": "2026-08-11T10:32:30+01:00",
        "reviewed_at": "2026-08-11T12:12:28+01:00",
    },
}
PRE_GOVERNANCE_REVIEWER_IDS = {
    "019ff021-bfee-7950-b26d-34689f197ee3",
    "019ff021-c059-7fe2-a84d-ddc9fdb3e495",
    "019ff021-c0a3-71c2-a2b3-b5cfacd770cc",
    "019ff022-24e3-71d3-a75b-c73958d31b31",
    "019ff022-2527-7970-8dae-59748b06ba3a",
    "019ff022-2583-71e3-ad83-0199360bb747",
    "019feeea-7360-7ec1-b9d6-7a6bd1ae85e9",
    "019feeea-73d9-7c90-9a08-27018cd7c72d",
    "019feeea-741e-7b53-9c40-bda2f515e04e",
    "019feeea-7468-73d3-bdb2-3896a3930c8b",
    "019feeea-74da-7211-99ae-3715f605f195",
    "019feef5-b487-7993-b072-b2b1e7fcc4ff",
    "019feb3f-cd89-7242-9a84-6fafbc77e0d8",
    "019feb71-89a9-77b3-9103-ad05eacf18ca",
    "019feb72-1592-7900-b0b1-02fae59a6a39",
    "019feb72-7252-77a1-b864-775b021ed954",
    "019feb72-ceeb-7d72-9abd-de60ca43316e",
    "019fec51-6552-7ac2-8a57-962a9f664475",
    "019fec51-8875-7243-98ab-d44ab2f963eb",
    "019fec51-a5a3-79b1-b9c9-27987dec5f98",
    "019fec51-c41b-75a0-8d7f-bd4d10d9d44d",
    "019fec51-e0b5-7531-99ff-997bd9f1247d",
    "019fec52-0bf5-73f3-b8d9-1004f8e54c87",
    C3_REVIEWER_ID,
}
PRE_GOVERNANCE_REVIEW_RUN_IDS = {
    "1nsi-contracts-2026-08-11-six-p0-019ff021-v1",
    "1nsi-objects-algorithms-2026-08-11-six-p0.9f59a4c7-455a-49b8-a1f7-a6bb5af90347",
    "1nsi-objects-data-basics-tables-2026-08-11-six-p0-35a10009-3947-43f6-af4c-95c0b9339d34",
    "1nsi-objects-language-project-2026-08-11-six-p0-bd346cbf-v1",
    "1nsi-objects-systems-web-2026-08-11-six-p0-c64cae93-bc64-4484-9031-4e4981a891cc-v1",
    "1nsi-objects-types-construits-2026-08-11-six-p0.81a8936e-0386-4cad-bd5b-ce77b2f2ae41",
    "1nsi-contracts-2026-08-11-language-trace-019feeea-v1",
    "1nsi-objects-algorithms-2026-08-11-language-trace-019feeea-v1",
    "1nsi-objects-data-basics-tables-2026-08-11-language-trace-019feeea-v1",
    "1nsi-objects-language-project-2026-08-11-language-trace-019feeea-v1",
    "1nsi-objects-systems-web-2026-08-11-language-trace-019feeea-v1",
    "1nsi-objects-types-construits-2026-08-11-language-trace-019feef5-v1",
    "1nsi-contracts-2026-08-10-plato-reattestation-v2",
    "1nsi-contracts-2026-08-10-build-manifest-019fec51-v1",
    C3_REVIEW_RUN_ID,
    "1nsi-objects-algorithms-2026-08-10-build-manifest-019fec51-v1",
    "1nsi-objects-data-basics-tables-2026-08-10-chandrasekhar-v1",
    "1nsi-objects-data-basics-tables-2026-08-10-build-manifest-019fec51-v1",
    "1nsi-objects-language-project-2026-08-10-lorentz-v1",
    "1nsi-objects-language-project-2026-08-10-build-manifest-019fec51-v1",
    "1nsi-objects-systems-web-2026-08-10-boyle-v1",
    "1nsi-objects-systems-web-2026-08-10-build-manifest-019fec51-v1",
    "1nsi-objects-types-construits-2026-08-10-epicurus-v1",
    "1nsi-objects-types-construits-2026-08-10-build-manifest-019fec52-v1",
}
EXPECTED_EXECUTION_DEBT = {
    "1NSI-LANGAGE-RE-C4": ["execution_receipt_diverged"],
    "1NSI-LANGAGE-RE-C4-CORRIGE": ["missing_receipt"],
    "1NSI-PM-RE-C3": ["execution_receipt_diverged"],
    "1NSI-PM-RE-C3-CORRIGE": ["missing_receipt"],
    "1NSI-RESEAUX-RE-C1": ["execution_receipt_diverged"],
    "1NSI-RESEAUX-RE-C1-CORRIGE": ["missing_receipt"],
    "1NSI-TABLES-RE-C2": ["execution_receipt_diverged"],
    "1NSI-TABLES-RE-C2-CORRIGE": ["missing_receipt"],
    "1NSI-TYPES-BASE-RE-C3": ["execution_receipt_diverged"],
    "1NSI-TYPES-BASE-RE-C3-CORRIGE": ["missing_receipt"],
    "1NSI-TC-AM-EXTRAIT": ["missing_receipt"],
    "1NSI-TC-QCM": ["missing_receipt"],
    "1NSI-WEB-IHM-RE-C9": ["execution_receipt_diverged"],
    "1NSI-WEB-IHM-RE-C9-CORRIGE": ["missing_receipt"],
}
PDF_SHA256 = "7ca9a32e1823be6c1120cb0417324c3cb01688d1d194c7614a88ea851ccc60b0"
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
CURRENT_ALLOWED_FILES = {
    "NSI/tests/test_1nsi_content_reviews.py",
    "scripts/review_1nsi_content.py",
    "audit/1NSI_CONTENT_REVIEW_POLICY.yaml",
    "audit/schemas/v1/1nsi-content-review.schema.json",
    "audit/sources/1nsi/programme-premiere-nsi.pdf",
    "audit/sources/1nsi/legifrance-arrete-17-janvier-2019.html",
    "audit/sources/1nsi/eduscol-programmes-nsi.html",
    "audit/reviews/1nsi/2026-08-11-actor-provenance.yaml",
}
INVENTORY_INTEGRATION_FILES = {
    "scripts/inventory_collection.py",
    "tests/test_inventory_collection.py",
    "ETAT_COLLECTION.md",
    "audit/ECARTS_ET_CONTRADICTIONS.yaml",
    "audit/INVENTAIRE_COLLECTION.json",
    "audit/MATRICE_LIVRABLES.yaml",
}
REVIEW_OUTPUTS = {
    "audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml",
    "audit/1NSI_CONTENT_REVIEWS.json",
    "audit/1NSI_CONTENT_REVIEW_SUMMARY.md",
}
REVIEW_RUNS = {
    f"audit/reviews/1nsi/runs/2026-08-10-{name}.yaml"
    for name in (
        "contracts",
        "algorithms",
        "systems-web",
        "language-project",
        "data-basics-tables",
        "types-construits",
    )
}
OBJECT_REVIEW_RUNS = REVIEW_RUNS - {
    "audit/reviews/1nsi/runs/2026-08-10-contracts.yaml"
}
ALLOWED_FILES = (
    CURRENT_ALLOWED_FILES | INVENTORY_INTEGRATION_FILES | REVIEW_OUTPUTS | REVIEW_RUNS
)
CONTRACTUAL_DOCUMENTS = {
    "NSI/docs/01_conception_manuel.md",
    "NSI/docs/02_workflow_production.md",
    "NSI/docs/05_conventions_latex.md",
    "docs/codex/QUALITY_GATES.md",
    "docs/codex/ISSUE_REGISTER_TEMPLATE.md",
    "audit/reviews/1nsi/2026-08-11-actor-provenance.yaml",
}
FORBIDDEN_GOVERNANCE_REVIEW_ROLES = {
    "correction_author",
    "correction_reviewer",
    "governance_integrator",
    "receipt_integrator",
}
CANONICAL_PDFS = {
    f"NSI/build/MANUEL_1NSI/MANUEL_1NSI_{variant}.pdf"
    for variant in (
        "amenagee",
        "eleve",
        "evaluations",
        "methodes",
        "professeur",
        "projets",
        "remediation",
    )
}


@pytest.fixture(scope="module")
def review_module():
    if not MODULE_PATH.is_file():
        return None
    spec = importlib.util.spec_from_file_location("review_1nsi_content", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def policy():
    if not POLICY_PATH.is_file():
        return None
    return yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def sources(review_module):
    if review_module is None:
        return None
    return review_module.discover_sources(ROOT)


def _sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_historical_fact(
    fact: dict,
    allowed_paths: set[str],
    commit: str,
) -> None:
    assert fact["path"] in allowed_paths
    assert "TNSI" not in fact["path"]
    source = _git_bytes(ROOT, "show", f"{commit}:{fact['path']}")
    lines = source.splitlines(keepends=True)
    assert 1 <= fact["line_start"] <= fact["line_end"] <= len(lines)
    excerpt = b"".join(lines[fact["line_start"] - 1 : fact["line_end"]])
    assert fact["excerpt_sha256"] == (
        "sha256:" + hashlib.sha256(excerpt).hexdigest()
    )


def _contract_refs() -> set[tuple[str, str]]:
    refs = set()
    for path in sorted((ROOT / "NSI" / "chapitres").glob("1NSI-*/contrat.yaml")):
        contract = yaml.safe_load(path.read_text(encoding="utf-8"))
        refs.update(
            (contract["chapitre"], capacity["ref_capacite"])
            for capacity in contract["capacites"]
        )
    return refs


def _excerpt_digest(path: Path, start: int = 1, end: int = 1) -> str:
    lines = path.read_bytes().splitlines(keepends=True)
    return "sha256:" + hashlib.sha256(b"".join(lines[start - 1 : end])).hexdigest()


def _fact(
    source: dict,
    observation: str,
    *,
    fact_type: str = "source_statement",
    root: Path = ROOT,
) -> dict:
    path = root / source["path"]
    return {
        "path": source["path"],
        "line_start": 1,
        "line_end": 1,
        "excerpt_sha256": _excerpt_digest(path),
        "fact_type": fact_type,
        "observation": observation,
    }


def _finding(
    source: dict,
    *,
    reviewer_id: str = "independent-reviewer",
    provenance: dict | None = None,
    root: Path = ROOT,
) -> dict:
    refs = source.get("capacity_refs", [])
    if provenance is None:
        provenance = {
            "reviewer_id": reviewer_id,
            "review_run_id": "unit-review-run",
            "reviewer_model": "unit-reviewer-model",
            "integrator_id": "integrator",
        }
    return {
        "id": source["id"],
        "scope": source["scope"],
        "chapter": source["chapter"],
        "source_path": source["path"],
        "source_status": source["status"],
        "capacity_refs": refs,
        "provenance": copy.deepcopy(provenance),
        "dimensions": {
            "scientific": {
                "verdict": "pass",
                "justification": "Le fait scientifique ancre a ete examine dans cette fixture.",
                "facts": [
                    _fact(
                        source,
                        f"Constat scientifique propre a {source['id']}.",
                        root=root,
                    )
                ],
                "anomaly_ids": [],
            },
            "pedagogical": {
                "verdict": "pass",
                "justification": "Le fait pedagogique ancre a ete examine dans cette fixture.",
                "facts": [
                    _fact(
                        source,
                        f"Constat pedagogique propre a {source['id']}.",
                        root=root,
                    )
                ],
                "anomaly_ids": [],
            },
        },
        "anomalies": [],
    }


def _git(root: Path, *args: str, input_text: str | None = None) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        input=input_text,
    ).stdout.strip()


def _git_bytes(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
    ).stdout


def _review_run_receipt(
    review_module,
    policy: dict,
    sources: list[dict],
    root: Path,
    *,
    review_run_id: str,
    reviewer_id: str,
    reviewer_model: str,
) -> dict:
    scopes = {source["scope"] for source in sources}
    assert len(scopes) == 1
    reviews = []
    for source in sources:
        finding = _finding(source, root=root)
        reviews.append(
            {
                "id": source["id"],
                "chapter": source["chapter"],
                "scope": source["scope"],
                "payload": {
                    "dimensions": finding["dimensions"],
                    "anomalies": finding["anomalies"],
                },
            }
        )
    source_manifest = {
        "review_tool_sha256": _sha(root / "scripts/review_1nsi_content.py"),
        "execution_checker_sha256": _sha(root / "NSI/scripts/verify_python.py"),
        "execution_common_sha256": _sha(root / "NSI/scripts/common.py"),
        "entries": [
            {
                "id": source["id"],
                "path": source["path"],
                "source_sha256": _sha(root / source["path"]),
                "dependency_digest": review_module.compute_dependency_digest(
                    source, sources, root, policy
                ),
            }
            for source in sorted(sources, key=lambda item: item["id"])
        ],
    }
    return {
        "artifact_type": "1nsi_review_run",
        "schema_version": 1,
        "manual": "1NSI",
        "review_run_id": review_run_id,
        "reviewer_id": reviewer_id,
        "reviewer_model": reviewer_model,
        "protocol_digest": policy["protocol_digest"],
        "reviewed_at": "2026-08-10T12:00:00+00:00",
        "assignment": {
            "scope": scopes.pop(),
            "chapters": sorted({source["chapter"] for source in sources}),
            "source_ids": sorted(source["id"] for source in sources),
        },
        "source_manifest": source_manifest,
        "reviews": reviews,
    }


def _install_review_support(root: Path) -> None:
    for relative in (
        "scripts/review_1nsi_content.py",
        "NSI/scripts/verify_python.py",
        "NSI/scripts/common.py",
        "audit/schemas/v1/1nsi-content-review.schema.json",
    ):
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)


def _reseal_review_receipt(sealed_review: dict, receipt: dict) -> None:
    path = sealed_review["receipt_path"]
    path.write_text(
        yaml.safe_dump(receipt, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    root = sealed_review["root"]
    _git(root, "add", path.relative_to(root).as_posix())
    _git(root, "commit", "-q", "-m", "reseal review receipt")
    sealed_review["provenance"]["review_receipt_sha256"] = _sha(path)
    sealed_review["provenance"]["sealing_commit_sha"] = _git(root, "rev-parse", "HEAD")


def _seal_finding_payload_with_anomalies(sealed_review: dict) -> dict:
    source = sealed_review["sources"][0]
    finding = _finding(
        source,
        provenance=sealed_review["provenance"],
        root=sealed_review["root"],
    )
    anomaly_ids = ["1NSI-REV-SEALED-A", "1NSI-REV-SEALED-B"]
    finding["dimensions"]["scientific"]["verdict"] = "issue"
    finding["dimensions"]["scientific"]["anomaly_ids"] = anomaly_ids.copy()
    finding["anomalies"] = []
    for index, anomaly_id in enumerate(anomaly_ids, start=1):
        fact = copy.deepcopy(finding["dimensions"]["scientific"]["facts"][0])
        fact["observation"] = f"Anomalie scellee distincte {index}."
        finding["anomalies"].append(
            {
                "id": anomaly_id,
                "severity": "P1",
                "dimension": "scientific",
                "fact": fact,
                "consequence": f"Consequence scellee {index}.",
                "expected_action": f"Action scellee {index}.",
            }
        )

    receipt = copy.deepcopy(sealed_review["receipt"])
    review = next(item for item in receipt["reviews"] if item["id"] == source["id"])
    review["payload"] = {
        "dimensions": copy.deepcopy(finding["dimensions"]),
        "anomalies": copy.deepcopy(finding["anomalies"]),
    }
    _reseal_review_receipt(sealed_review, receipt)
    finding["provenance"] = copy.deepcopy(sealed_review["provenance"])
    return finding


@pytest.fixture
def sealed_review(tmp_path, policy, review_module):
    chapter = tmp_path / "NSI" / "chapitres" / "1NSI-UNIT"
    contract_path = chapter / "contrat.yaml"
    receipt_path = tmp_path / "audit/reviews/1nsi/runs/2026-08-10-contracts.yaml"
    object_paths = [
        chapter / "exercices" / "1NSI-UNIT-EX-001.tex",
        chapter / "exercices" / "1NSI-UNIT-EX-002.tex",
    ]
    contract_path.parent.mkdir(parents=True)
    receipt_path.parent.mkdir(parents=True)
    object_paths[0].parent.mkdir(parents=True)
    contract_path.write_text(
        "chapitre: 1NSI-UNIT\nstatut: draft\ncapacites: []\n", encoding="utf-8"
    )
    _install_review_support(tmp_path)
    sources = []
    for index, path in enumerate(object_paths, start=1):
        object_id = f"1NSI-UNIT-EX-{index:03d}"
        path.write_text(
            f'% META: {{"id":"{object_id}","chapitre":"1NSI-UNIT",'
            '"type_objet":"exercice","status":"verified"}}\n'
            f"Contenu unitaire {index}.\n",
            encoding="utf-8",
        )
        sources.append(
            {
                "id": object_id,
                "scope": "object",
                "chapter": "1NSI-UNIT",
                "path": path.relative_to(tmp_path).as_posix(),
                "status": "verified",
                "type": "exercice",
                "capacity_refs": [],
                "metadata": {},
                "source_sha256": _sha(path),
            }
        )
    receipt = _review_run_receipt(
        review_module,
        policy,
        sources,
        tmp_path,
        review_run_id="unit-review-run",
        reviewer_id="independent-reviewer",
        reviewer_model="unit-reviewer-model",
    )
    receipt_path.write_text(
        yaml.safe_dump(receipt, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )

    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "Nexus Tests")
    _git(tmp_path, "config", "user.email", "nexus-tests@example.invalid")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "seal review receipt")
    sealing_commit = _git(tmp_path, "rev-parse", "HEAD")
    provenance = {
        "reviewer_id": "independent-reviewer",
        "review_run_id": "unit-review-run",
        "reviewer_model": "unit-reviewer-model",
        "integrator_id": "integrator",
        "review_receipt_path": receipt_path.relative_to(tmp_path).as_posix(),
        "review_receipt_sha256": _sha(receipt_path),
        "sealing_commit_sha": sealing_commit,
    }
    return {
        "root": tmp_path,
        "policy": copy.deepcopy(policy),
        "sources": sources,
        "provenance": provenance,
        "receipt_path": receipt_path,
        "receipt": receipt,
    }


def test_policy_closes_manual_decision_and_verdicts(policy) -> None:
    assert policy is not None, "la politique de revue doit etre creee"
    assert policy["artifact_type"] == "1nsi_content_review_policy"
    assert policy["manual"] == "1NSI"
    assert policy["decision"]["date"] == "2026-08-10"
    assert policy["decision"]["publication_approval"] is False
    assert policy["decision"]["human_confirmation_required"] is True
    assert policy["decision"]["release_acceptance"] is False
    assert policy["verdicts"] == [
        "pass",
        "issue",
        "not_applicable",
        "human_confirmation_required",
    ]
    assert policy["review_dimensions"] == ["scientific", "pedagogical"]
    assert set(policy["prohibited_transitions"]) == {"approved", "ready", "rejected"}
    assert set(policy["allowlist"]) == ALLOWED_FILES


def test_policy_pins_official_and_contractual_sources(policy, review_module) -> None:
    assert policy is not None, "la politique de revue doit etre creee"
    assert review_module is not None, "le generateur de revue doit etre cree"
    official = policy["official_sources"]
    assert len(official) == 3
    assert {item["kind"] for item in official} == {
        "official_programme_pdf",
        "legifrance_consolidated_text",
        "eduscol_programme_page",
    }
    assert {item["consulted_on"] for item in official} == {"2026-08-10"}
    for item in official:
        snapshot = ROOT / item["snapshot_path"]
        assert snapshot.is_file()
        assert item["sha256"] == _sha(snapshot)
        assert item["url"].startswith("https://")
        assert item["capture_status"] == "content"
        if snapshot.suffix == ".html":
            html = snapshot.read_text(encoding="utf-8")
            assert "Attention Required!" not in html
            assert "Vérification de sécurité en cours" not in html
    assert "Arrêté du 17 janvier 2019" in (
        ROOT / "audit/sources/1nsi/legifrance-arrete-17-janvier-2019.html"
    ).read_text(encoding="utf-8")
    assert "Programme en vigueur" in (
        ROOT / "audit/sources/1nsi/eduscol-programmes-nsi.html"
    ).read_text(encoding="utf-8")
    programme = next(
        item for item in official if item["kind"] == "official_programme_pdf"
    )
    assert programme["sha256"] == f"sha256:{PDF_SHA256}"

    local = policy["contractual_documents"]
    assert {item["path"] for item in local} == CONTRACTUAL_DOCUMENTS
    assert all(item["sha256"] == _sha(ROOT / item["path"]) for item in local)
    assert SHA256.fullmatch(policy["protocol_digest"])
    assert (
        review_module.compute_protocol_digest(ROOT, policy) == policy["protocol_digest"]
    )


def test_actor_provenance_seals_the_human_process_decision_and_forbidden_roles(
    policy,
) -> None:
    provenance = yaml.safe_load(ACTOR_PROVENANCE_PATH.read_text(encoding="utf-8"))
    assert set(provenance) == {
        "artifact_type",
        "schema_version",
        "manual",
        "decision",
        "actors",
    }
    assert provenance["artifact_type"] == "1nsi_review_actor_provenance"
    assert provenance["schema_version"] == 1
    assert provenance["manual"] == "1NSI"

    decision = provenance["decision"]
    assert set(decision) == {
        "id",
        "human_instruction",
        "supersedes_plan_invariant",
        "operational_effect",
        "retained_new_anomaly_ids",
        "publication_approval",
        "release_acceptance",
        "human_confirmation_required",
    }
    assert decision["human_instruction"] == (
        "migrer la gouvernance, reattester les 349 revues, resynchroniser les "
        "findings puis traiter separement BUILD_MANIFEST"
    )
    assert decision["supersedes_plan_invariant"] == (
        "new_anomaly_ids - old_anomaly_ids == set()"
    )
    assert decision["operational_effect"] == (
        "conserver les anomalies nouvelles contre-revues sans les approuver et "
        "exiger une observation propre a chaque objet avant rescellement"
    )
    assert decision["retained_new_anomaly_ids"]
    assert len(decision["retained_new_anomaly_ids"]) == len(
        set(decision["retained_new_anomaly_ids"])
    )
    assert all(
        anomaly_id.startswith("1NSI-REV-")
        for anomaly_id in decision["retained_new_anomaly_ids"]
    )
    assert decision["publication_approval"] is False
    assert decision["release_acceptance"] is False
    assert decision["human_confirmation_required"] is True

    actors = provenance["actors"]
    assert actors
    actor_ids = [actor["actor_id"] for actor in actors]
    assert len(actor_ids) == len(set(actor_ids))
    forbidden_ids = {
        actor["actor_id"]
        for actor in actors
        if set(actor["roles"]) & FORBIDDEN_GOVERNANCE_REVIEW_ROLES
    }
    assert policy["integrator_id"] in forbidden_ids

    attestation_reviewers = set()
    for relative_path in SIX_P0_ATTESTATION_PATHS:
        receipt = yaml.safe_load((ROOT / relative_path).read_text(encoding="utf-8"))
        attestation_reviewers.add(receipt["reviewer_id"])
    assert attestation_reviewers <= forbidden_ids

    for actor in actors:
        assert set(actor) == {"actor_id", "roles", "evidence"}
        assert actor["roles"]
        assert actor["evidence"]
        for evidence in actor["evidence"]:
            if evidence["kind"] == "git_commit_author":
                assert set(evidence) == {"kind", "commit_sha", "author_email"}
                assert actor["actor_id"] == f"git-email:{evidence['author_email']}"
                assert _git(
                    ROOT, "show", "-s", "--format=%ae", evidence["commit_sha"]
                ) == evidence["author_email"]
            elif evidence["kind"] == "policy_integrator":
                assert set(evidence) == {"kind", "path", "field"}
                assert evidence == {
                    "kind": "policy_integrator",
                    "path": "audit/1NSI_CONTENT_REVIEW_POLICY.yaml",
                    "field": "integrator_id",
                }
                assert actor["actor_id"] == policy["integrator_id"]
            elif evidence["kind"] == "p0_review_receipt":
                assert set(evidence) == {"kind", "path", "sha256"}
                receipt_path = ROOT / evidence["path"]
                assert evidence["sha256"] == _sha(receipt_path)
                receipt = yaml.safe_load(receipt_path.read_text(encoding="utf-8"))
                assert actor["actor_id"] == receipt["reviewer_id"]
            else:
                raise AssertionError(f"preuve d'acteur inconnue: {evidence['kind']}")

    governance_reviewer_ids = {
        yaml.safe_load((ROOT / relative_path).read_text(encoding="utf-8"))[
            "reviewer_id"
        ]
        for relative_path in REVIEW_RUNS
    }
    assert not (governance_reviewer_ids & forbidden_ids)


def test_policy_matrix_covers_every_contract_reference_once(policy) -> None:
    assert policy is not None, "la politique de revue doit etre creee"
    rows = policy["capacity_matrix"]
    observed = [(row["chapter"], row["ref"]) for row in rows]
    assert len(observed) == len(set(observed))
    assert set(observed) == _contract_refs()
    assert all(row["programme_section"] and row["programme_anchor"] for row in rows)
    assert all(
        row["classification"]
        in {
            "official_capacity",
            "local_reference",
            "transversal_enrichment",
        }
        for row in rows
    )

    local = {row["ref"] for row in rows if row["classification"] == "local_reference"}
    enrichments = {
        row["ref"] for row in rows if row["classification"] == "transversal_enrichment"
    }
    assert local == {f"1NSI-TYPES-CONSTRUITS-C{i}" for i in range(1, 6)}
    assert enrichments == {
        "BO-PREAMBULE-DEMARCHE-DE-PROJET",
        "BO-PREAMBULE-COMPETENCES-METHODE",
        "BO-PREAMBULE-COMPETENCES-ORALES",
    }
    assert all(
        row["human_confirmation_required"]
        is (row["classification"] != "official_capacity")
        for row in rows
    )


def test_protocol_mutation_invalidates_all_dependency_digests(
    policy, sources, review_module
) -> None:
    original = [
        review_module.compute_dependency_digest(source, sources, ROOT, policy)
        for source in sources
    ]
    mutated = copy.deepcopy(policy)
    mutated["protocol_digest"] = "sha256:" + "0" * 64
    changed = [
        review_module.compute_dependency_digest(source, sources, ROOT, mutated)
        for source in sources
    ]
    assert len(original) == 349
    assert all(before != after for before, after in zip(original, changed, strict=True))


@pytest.mark.parametrize(
    "mutation",
    [
        "decision",
        "verdicts",
        "prohibited_transitions",
        "review_dimensions",
        "capacity_matrix",
        "scope_guard",
        "allowlist",
    ],
)
def test_protocol_digest_seals_every_governance_rule(
    policy, review_module, mutation
) -> None:
    mutated = copy.deepcopy(policy)
    if mutation == "decision":
        mutated["decision"]["release_acceptance"] = True
    elif mutation == "verdicts":
        mutated["verdicts"].reverse()
    elif mutation == "prohibited_transitions":
        mutated["prohibited_transitions"].append("silently_approved")
    elif mutation == "review_dimensions":
        mutated["review_dimensions"].reverse()
    elif mutation == "capacity_matrix":
        mutated["capacity_matrix"][0]["programme_anchor"] += " Mutation de test."
    elif mutation == "scope_guard":
        mutated["scope_guard"]["sources"][0]["status"] = "mutated"
    else:
        mutated["allowlist"].append("audit/unplanned-output.yaml")

    assert (
        review_module.compute_protocol_digest(ROOT, mutated)
        != policy["protocol_digest"]
    )


def test_protocol_payload_contains_exactly_nine_source_records(
    policy, review_module
) -> None:
    records = review_module._protocol_records(policy)
    assert len(records) == 9
    assert {record["path"] for record in records} == {
        *(item["snapshot_path"] for item in policy["official_sources"]),
        *(item["path"] for item in policy["contractual_documents"]),
    }


def test_discover_sources_is_exact_and_1nsi_only(sources) -> None:
    assert sources is not None, "le generateur de revue doit etre cree"
    assert len(sources) == 349
    assert len({item["id"] for item in sources}) == 349
    assert Counter(item["scope"] for item in sources) == {"object": 339, "contract": 10}
    assert Counter(item["status"] for item in sources if item["scope"] == "object") == {
        "verified": 163,
        "needs_review": 169,
        "manual_review": 7,
    }
    assert Counter(
        item["status"] for item in sources if item["scope"] == "contract"
    ) == {"draft": 10}
    assert all(item["path"].startswith("NSI/chapitres/1NSI-") for item in sources)
    assert all(
        "TNSI" not in item["id"] + item["chapter"] + item["path"] for item in sources
    )
    assert all(SHA256.fullmatch(item["source_sha256"]) for item in sources)
    assert all(item["source_sha256"] == _sha(ROOT / item["path"]) for item in sources)


def test_scope_guard_pins_exact_sources_and_immutable_surfaces(
    policy, sources, review_module
) -> None:
    guard = policy["scope_guard"]
    assert guard["implementation_base_sha"] == BASE_SHA
    assert guard["sources"] == [
        {"id": item["id"], "path": item["path"], "status": item["status"]}
        for item in sources
    ]
    assert guard["build_manifest"] == {
        "path": "audit/BUILD_MANIFEST.json",
        "sha256": _sha(ROOT / "audit/BUILD_MANIFEST.json"),
    }
    assert {item["path"] for item in guard["canonical_pdfs"]} == CANONICAL_PDFS
    assert all(
        item["sha256"] == _sha(ROOT / item["path"]) for item in guard["canonical_pdfs"]
    )
    assert guard["tnsi_tracked_files_count"] == 261
    assert SHA256.fullmatch(guard["tnsi_tracked_files_digest"])
    review_module.verify_scope(ROOT, policy)


def test_build_manifest_governance_uses_current_clean_base(
    policy, review_module
) -> None:
    guard = policy["scope_guard"]
    assert guard["implementation_base_sha"] == BASE_SHA
    assert guard["build_manifest"] == {
        "path": "audit/BUILD_MANIFEST.json",
        "sha256": _sha(ROOT / "audit/BUILD_MANIFEST.json"),
    }
    assert review_module.compute_protocol_digest(ROOT, policy) == policy[
        "protocol_digest"
    ]
    review_module.verify_scope(ROOT, policy)


def test_pre_ten_p0_receipts_remain_historically_sealed(review_module) -> None:
    historical_policy = yaml.safe_load(
        _git_bytes(
            ROOT,
            "show",
            f"{PRE_TEN_P0_POLICY_COMMIT}:audit/1NSI_CONTENT_REVIEW_POLICY.yaml",
        ).decode("utf-8")
    )
    assert historical_policy["scope_guard"]["implementation_base_sha"] == (
        PRE_TEN_P0_BASE_SHA
    )
    assert historical_policy["protocol_digest"] == PRE_TEN_P0_PROTOCOL_DIGEST
    assert _git(ROOT, "rev-list", "--parents", "-n", "1", PRE_TEN_P0_RECEIPTS_COMMIT).split() == [
        PRE_TEN_P0_RECEIPTS_COMMIT,
        PRE_TEN_P0_POLICY_COMMIT,
    ]
    receipt_schema = review_module._receipt_schema(ROOT)

    for relative_path, expected_digest in sorted(
        PRE_TEN_P0_RECEIPT_SEALS.items()
    ):
        receipt_bytes = _git_bytes(
            ROOT,
            "show",
            f"{PRE_TEN_P0_RECEIPTS_COMMIT}:{relative_path}",
        )
        assert "sha256:" + hashlib.sha256(receipt_bytes).hexdigest() == (
            expected_digest
        )
        receipt = yaml.safe_load(receipt_bytes.decode("utf-8"))
        Draft202012Validator(
            receipt_schema,
            format_checker=review_module.FORMAT_CHECKER,
        ).validate(receipt)
        assert receipt["protocol_digest"] == PRE_TEN_P0_PROTOCOL_DIGEST
        assert "TNSI" not in json.dumps(receipt, ensure_ascii=False)

        manifest = receipt["source_manifest"]
        historical_tools = {
            "review_tool_sha256": "scripts/review_1nsi_content.py",
            "execution_checker_sha256": "NSI/scripts/verify_python.py",
            "execution_common_sha256": "NSI/scripts/common.py",
        }
        for field, source_path in historical_tools.items():
            payload = _git_bytes(
                ROOT,
                "show",
                f"{PRE_TEN_P0_RECEIPTS_COMMIT}:{source_path}",
            )
            assert manifest[field] == (
                "sha256:" + hashlib.sha256(payload).hexdigest()
            )
        for entry in manifest["entries"]:
            payload = _git_bytes(
                ROOT,
                "show",
                f"{PRE_TEN_P0_RECEIPTS_COMMIT}:{entry['path']}",
            )
            assert entry["source_sha256"] == (
                "sha256:" + hashlib.sha256(payload).hexdigest()
            )


def test_ten_p0_policy_remains_historically_sealed() -> None:
    historical_policy = yaml.safe_load(
        _git_bytes(
            ROOT,
            "show",
            f"{PRE_ADGK_POLICY_COMMIT}:audit/1NSI_CONTENT_REVIEW_POLICY.yaml",
        ).decode("utf-8")
    )
    assert historical_policy["scope_guard"]["implementation_base_sha"] == (
        PRE_ADGK_BASE_SHA
    )
    assert historical_policy["protocol_digest"] == TEN_P0_PROTOCOL_DIGEST
    assert _git(ROOT, "rev-parse", f"{PRE_ADGK_POLICY_COMMIT}^") == (
        PRE_ADGK_BASE_SHA
    )


def test_adgk_policy_remains_historically_sealed() -> None:
    historical_policy = yaml.safe_load(
        _git_bytes(
            ROOT,
            "show",
            f"{PRE_OPTIMIZATION_POLICY_COMMIT}:audit/1NSI_CONTENT_REVIEW_POLICY.yaml",
        ).decode("utf-8")
    )
    assert historical_policy["scope_guard"]["implementation_base_sha"] == (
        PRE_OPTIMIZATION_BASE_SHA
    )
    assert historical_policy["protocol_digest"] == ADGK_PROTOCOL_DIGEST
    assert _git(ROOT, "rev-parse", f"{PRE_OPTIMIZATION_POLICY_COMMIT}^") == (
        PRE_OPTIMIZATION_BASE_SHA
    )


def test_table_optimization_policy_remains_historically_sealed() -> None:
    historical_policy = yaml.safe_load(
        _git_bytes(
            ROOT,
            "show",
            f"{PRE_PRECONDITION_POLICY_COMMIT}:audit/1NSI_CONTENT_REVIEW_POLICY.yaml",
        ).decode("utf-8")
    )
    assert historical_policy["scope_guard"]["implementation_base_sha"] == (
        PRE_PRECONDITION_BASE_SHA
    )
    assert historical_policy["protocol_digest"] == OPTIMIZATION_PROTOCOL_DIGEST
    assert _git(ROOT, "rev-parse", f"{PRE_PRECONDITION_POLICY_COMMIT}^") == (
        PRE_PRECONDITION_BASE_SHA
    )


def test_precondition_optimization_policy_remains_historically_sealed() -> None:
    historical_policy = yaml.safe_load(
        _git_bytes(
            ROOT,
            "show",
            f"{PRE_EXECUTION_RECEIPT_POLICY_COMMIT}:audit/1NSI_CONTENT_REVIEW_POLICY.yaml",
        ).decode("utf-8")
    )
    assert historical_policy["scope_guard"]["implementation_base_sha"] == (
        PRE_EXECUTION_RECEIPT_BASE_SHA
    )
    assert historical_policy["protocol_digest"] == PRECONDITION_PROTOCOL_DIGEST
    assert _git(ROOT, "rev-parse", f"{PRE_EXECUTION_RECEIPT_POLICY_COMMIT}^") == (
        PRE_EXECUTION_RECEIPT_BASE_SHA
    )


def test_table_execution_receipt_policy_remains_historically_sealed() -> None:
    historical_policy = yaml.safe_load(
        _git_bytes(
            ROOT,
            "show",
            f"{PRE_LANGUAGE_RECEIPT_POLICY_COMMIT}:audit/1NSI_CONTENT_REVIEW_POLICY.yaml",
        ).decode("utf-8")
    )
    assert historical_policy["scope_guard"]["implementation_base_sha"] == (
        PRE_LANGUAGE_RECEIPT_BASE_SHA
    )
    assert historical_policy["protocol_digest"] == EXECUTION_RECEIPT_PROTOCOL_DIGEST
    assert _git(ROOT, "rev-parse", f"{PRE_LANGUAGE_RECEIPT_POLICY_COMMIT}^") == (
        PRE_LANGUAGE_RECEIPT_BASE_SHA
    )


def test_language_execution_receipt_policy_remains_historically_sealed() -> None:
    historical_policy = yaml.safe_load(
        _git_bytes(
            ROOT,
            "show",
            f"{PRE_COPY_RECEIPT_POLICY_COMMIT}:audit/1NSI_CONTENT_REVIEW_POLICY.yaml",
        ).decode("utf-8")
    )
    assert historical_policy["scope_guard"]["implementation_base_sha"] == (
        PRE_COPY_RECEIPT_BASE_SHA
    )
    assert historical_policy["protocol_digest"] == LANGUAGE_RECEIPT_PROTOCOL_DIGEST
    assert _git(ROOT, "rev-parse", f"{PRE_COPY_RECEIPT_POLICY_COMMIT}^") == (
        PRE_COPY_RECEIPT_BASE_SHA
    )


def test_copy_receipt_policy_remains_historically_sealed() -> None:
    historical_policy = yaml.safe_load(
        _git_bytes(
            ROOT,
            "show",
            f"{PRE_SEPARATION_LOCK_POLICY_COMMIT}:audit/1NSI_CONTENT_REVIEW_POLICY.yaml",
        ).decode("utf-8")
    )
    assert historical_policy["scope_guard"]["implementation_base_sha"] == (
        PRE_SEPARATION_LOCK_BASE_SHA
    )
    assert historical_policy["protocol_digest"] == COPY_RECEIPT_PROTOCOL_DIGEST
    assert _git(ROOT, "rev-parse", f"{PRE_SEPARATION_LOCK_POLICY_COMMIT}^") == (
        PRE_SEPARATION_LOCK_BASE_SHA
    )


def test_separation_lock_policy_remains_historically_sealed() -> None:
    historical_policy = yaml.safe_load(
        _git_bytes(
            ROOT,
            "show",
            f"{PRE_LANGUAGE_TRACE_POLICY_COMMIT}:audit/1NSI_CONTENT_REVIEW_POLICY.yaml",
        ).decode("utf-8")
    )
    assert historical_policy["scope_guard"]["implementation_base_sha"] == (
        PRE_LANGUAGE_TRACE_BASE_SHA
    )
    assert historical_policy["protocol_digest"] == SEPARATION_LOCK_PROTOCOL_DIGEST
    assert _git(ROOT, "rev-parse", f"{PRE_LANGUAGE_TRACE_POLICY_COMMIT}^") == (
        PRE_LANGUAGE_TRACE_BASE_SHA
    )


def test_language_trace_policy_remains_historically_sealed() -> None:
    historical_policy = yaml.safe_load(
        _git_bytes(
            ROOT,
            "show",
            f"{PRE_SIX_P0_POLICY_COMMIT}:audit/1NSI_CONTENT_REVIEW_POLICY.yaml",
        ).decode("utf-8")
    )
    assert historical_policy["scope_guard"]["implementation_base_sha"] == (
        PRE_SIX_P0_BASE_SHA
    )
    assert historical_policy["protocol_digest"] == LANGUAGE_TRACE_PROTOCOL_DIGEST
    assert _git(ROOT, "rev-parse", f"{PRE_SIX_P0_POLICY_COMMIT}^") == (
        PRE_SIX_P0_BASE_SHA
    )


def test_counter_review_policy_migration_invalidates_exactly_six_receipts(
    policy, sources, review_module
) -> None:
    assert policy["scope_guard"]["implementation_base_sha"] == BASE_SHA
    assert policy["protocol_digest"] == COUNTER_REVIEW_PROTOCOL_DIGEST
    assert review_module.compute_protocol_digest(ROOT, policy) == (
        COUNTER_REVIEW_PROTOCOL_DIGEST
    )

    historical_policy = yaml.safe_load(
        _git_bytes(
            ROOT,
            "show",
            f"{PRE_COUNTER_REVIEW_POLICY_COMMIT}:audit/1NSI_CONTENT_REVIEW_POLICY.yaml",
        ).decode("utf-8")
    )
    assert historical_policy["scope_guard"]["implementation_base_sha"] == (
        PRE_COUNTER_REVIEW_BASE_SHA
    )
    assert historical_policy["protocol_digest"] == ACTOR_PROVENANCE_PROTOCOL_DIGEST
    assert _git(
        ROOT, "rev-parse", f"{PRE_COUNTER_REVIEW_POLICY_COMMIT}^"
    ) == PRE_COUNTER_REVIEW_BASE_SHA

    sources_by_id = {source["id"]: source for source in sources}
    stale_receipts = set()
    current_tool_hashes = {
        "review_tool_sha256": _sha(MODULE_PATH),
        "execution_checker_sha256": _sha(ROOT / "NSI/scripts/verify_python.py"),
        "execution_common_sha256": _sha(ROOT / "NSI/scripts/common.py"),
    }

    for relative_path in sorted(REVIEW_RUNS):
        receipt = yaml.safe_load(
            _git_bytes(
                ROOT,
                "show",
                f"{PRE_ACTOR_PROVENANCE_RECEIPTS_COMMIT}:{relative_path}",
            ).decode("utf-8")
        )
        assert receipt["protocol_digest"] == SIX_P0_PROTOCOL_DIGEST
        manifest = receipt["source_manifest"]
        assert receipt["protocol_digest"] != policy["protocol_digest"]
        for field, current_digest in current_tool_hashes.items():
            assert manifest[field] == current_digest

        dependency_mismatches = set()
        for entry in manifest["entries"]:
            source = sources_by_id[entry["id"]]
            assert entry["path"] == source["path"]
            assert entry["source_sha256"] == _sha(ROOT / source["path"])
            if entry["dependency_digest"] != (
                review_module.compute_dependency_digest(
                    source,
                    sources,
                    ROOT,
                    policy,
                )
            ):
                dependency_mismatches.add(entry["id"])

        assert dependency_mismatches == set(receipt["assignment"]["source_ids"])
        for review in receipt["reviews"]:
            source = sources_by_id[review["id"]]
            allowed_paths = review_module._allowed_fact_paths(
                source, sources, ROOT, policy
            )
            payload = review["payload"]
            facts = [
                fact
                for dimension in payload["dimensions"].values()
                for fact in dimension["facts"]
            ] + [anomaly["fact"] for anomaly in payload["anomalies"]]
            for fact in facts:
                _assert_historical_fact(
                    fact, allowed_paths, PRE_ACTOR_PROVENANCE_RECEIPTS_COMMIT
                )
        stale_receipts.add(relative_path)

    assert stale_receipts == REVIEW_RUNS

    execution_receipt_path = (
        "NSI/chapitres/1NSI-RESEAUX/validations/"
        "1NSI-RES-COURS-C3.execution.json"
    )
    historical_receipt = _git_bytes(
        ROOT,
        "show",
        f"{PRE_ACTOR_PROVENANCE_RECEIPTS_COMMIT}:{execution_receipt_path}",
    )
    assert hashlib.sha256(historical_receipt).digest() != hashlib.sha256(
        (ROOT / execution_receipt_path).read_bytes()
    ).digest()


def test_policy_migration_invalidates_only_review_envelopes(
    policy, sources, review_module
) -> None:
    assert policy["protocol_digest"] != PRE_BUILD_MANIFEST_PROTOCOL_DIGEST
    sources_by_id = {source["id"]: source for source in sources}
    receipt_schema = review_module._receipt_schema(ROOT)

    for relative_path in sorted(REVIEW_RUNS):
        receipt = yaml.safe_load(
            _git_bytes(
                ROOT,
                "show",
                f"{PRE_ACTOR_PROVENANCE_RECEIPTS_COMMIT}:{relative_path}",
            ).decode("utf-8")
        )
        schema_errors = sorted(
            Draft202012Validator(
                receipt_schema,
                format_checker=review_module.FORMAT_CHECKER,
            ).iter_errors(receipt),
            key=lambda error: tuple(str(part) for part in error.path),
        )
        assert not schema_errors, (relative_path, schema_errors)
        assert receipt["protocol_digest"] == SIX_P0_PROTOCOL_DIGEST
        assert receipt["protocol_digest"] != policy["protocol_digest"]
        assert "TNSI" not in json.dumps(receipt, ensure_ascii=False)

        source_ids = receipt["assignment"]["source_ids"]
        assert [entry["id"] for entry in receipt["source_manifest"]["entries"]] == (
            source_ids
        )
        assert [review["id"] for review in receipt["reviews"]] == source_ids
        for entry in receipt["source_manifest"]["entries"]:
            source = sources_by_id[entry["id"]]
            assert entry["path"] == source["path"]
            historical_source = _git_bytes(
                ROOT,
                "show",
                f"{PRE_ACTOR_PROVENANCE_RECEIPTS_COMMIT}:{source['path']}",
            )
            assert entry["source_sha256"] == (
                "sha256:" + hashlib.sha256(historical_source).hexdigest()
            )
            assert entry["dependency_digest"] != review_module.compute_dependency_digest(
                source, sources, ROOT, policy
            )

        for review in receipt["reviews"]:
            source = sources_by_id[review["id"]]
            payload = review["payload"]
            anomalies = payload["anomalies"]
            allowed_paths = review_module._allowed_fact_paths(
                source, sources, ROOT, policy
            )
            for dimension_name, dimension in payload["dimensions"].items():
                expected_ids = [
                    anomaly["id"]
                    for anomaly in anomalies
                    if anomaly["dimension"] == dimension_name
                ]
                assert dimension["anomaly_ids"] == expected_ids
                assert (dimension["verdict"] == "issue") == bool(expected_ids)
                for fact in dimension["facts"]:
                    _assert_historical_fact(
                        fact, allowed_paths, PRE_ACTOR_PROVENANCE_RECEIPTS_COMMIT
                    )
            for anomaly in anomalies:
                _assert_historical_fact(
                    anomaly["fact"],
                    allowed_paths,
                    PRE_ACTOR_PROVENANCE_RECEIPTS_COMMIT,
                )


def test_all_review_receipts_match_current_governance_before_sealing(
    policy, sources, review_module
) -> None:
    configs = list(GOVERNANCE_REVIEW_CONFIG.values())
    reviewer_ids = [config["reviewer_id"] for config in configs]
    review_run_ids = [config["review_run_id"] for config in configs]
    assert len(reviewer_ids) == len(set(reviewer_ids)) == 6
    assert len(review_run_ids) == len(set(review_run_ids)) == 6
    assert not (set(reviewer_ids) & PRE_GOVERNANCE_REVIEWER_IDS)
    assert not (set(review_run_ids) & PRE_GOVERNANCE_REVIEW_RUN_IDS)
    actor_provenance = yaml.safe_load(
        ACTOR_PROVENANCE_PATH.read_text(encoding="utf-8")
    )
    forbidden_reviewer_ids = {
        actor["actor_id"]
        for actor in actor_provenance["actors"]
        if set(actor["roles"]) & FORBIDDEN_GOVERNANCE_REVIEW_ROLES
    }
    assert not (set(reviewer_ids) & forbidden_reviewer_ids)

    sources_by_id = {source["id"]: source for source in sources}
    receipt_schema = review_module._receipt_schema(ROOT)
    covered_ids = []
    current_anomaly_ids = []
    execution_debt = {}
    for relative_path, config in GOVERNANCE_REVIEW_CONFIG.items():
        receipt = yaml.safe_load((ROOT / relative_path).read_text(encoding="utf-8"))
        schema_errors = sorted(
            Draft202012Validator(
                receipt_schema,
                format_checker=review_module.FORMAT_CHECKER,
            ).iter_errors(receipt),
            key=lambda error: tuple(str(part) for part in error.path),
        )
        assert not schema_errors, (relative_path, schema_errors)
        assert receipt["reviewer_id"] == config["reviewer_id"]
        assert receipt["review_run_id"] == config["review_run_id"]
        assert receipt["reviewer_model"] == GOVERNANCE_REVIEWER_MODEL
        assert receipt["protocol_digest"] == policy["protocol_digest"]
        assert receipt["reviewed_at"] == config["reviewed_at"]
        assert datetime.fromisoformat(config["reviewed_at"]) > datetime.fromisoformat(
            config["previous_reviewed_at"]
        )
        assert "TNSI" not in json.dumps(receipt, ensure_ascii=False)

        expected_sources = sorted(
            (sources_by_id[source_id] for source_id in receipt["assignment"]["source_ids"]),
            key=lambda source: source["id"],
        )
        expected_ids = [source["id"] for source in expected_sources]
        assert receipt["assignment"] == {
            "scope": expected_sources[0]["scope"],
            "chapters": sorted({source["chapter"] for source in expected_sources}),
            "source_ids": expected_ids,
        }
        covered_ids.extend(expected_ids)
        manifest = receipt["source_manifest"]
        assert manifest["review_tool_sha256"] == _sha(MODULE_PATH)
        assert manifest["execution_checker_sha256"] == _sha(
            ROOT / "NSI/scripts/verify_python.py"
        )
        assert manifest["execution_common_sha256"] == _sha(
            ROOT / "NSI/scripts/common.py"
        )
        assert manifest["entries"] == [
            {
                "id": source["id"],
                "path": source["path"],
                "source_sha256": _sha(ROOT / source["path"]),
                "dependency_digest": review_module.compute_dependency_digest(
                    source, sources, ROOT, policy
                ),
            }
            for source in expected_sources
        ]
        assert [review["id"] for review in receipt["reviews"]] == expected_ids

        for review in receipt["reviews"]:
            source = sources_by_id[review["id"]]
            assert review["chapter"] == source["chapter"]
            assert review["scope"] == source["scope"]
            payload = review["payload"]
            anomalies = payload["anomalies"]
            current_anomaly_ids.extend(anomaly["id"] for anomaly in anomalies)
            allowed_paths = review_module._allowed_fact_paths(
                source, sources, ROOT, policy
            )
            for dimension_name, dimension in payload["dimensions"].items():
                expected_anomaly_ids = [
                    anomaly["id"]
                    for anomaly in anomalies
                    if anomaly["dimension"] == dimension_name
                ]
                assert dimension["anomaly_ids"] == expected_anomaly_ids
                assert (dimension["verdict"] == "issue") == bool(
                    expected_anomaly_ids
                )
                for fact in dimension["facts"]:
                    review_module._validate_fact(fact, allowed_paths, ROOT)
            for anomaly in anomalies:
                review_module._validate_fact(anomaly["fact"], allowed_paths, ROOT)

            observation = review_module.execution_observation(source, ROOT)
            if observation is None:
                continue
            assert observation["fresh_verdict"] == "pass", source["id"]
            if observation["anomalies"]:
                execution_debt[source["id"]] = observation["anomalies"]
            else:
                assert observation["matches_receipt"] is True, source["id"]

    assert len(covered_ids) == len(set(covered_ids)) == 349
    assert set(covered_ids) == set(sources_by_id)
    assert len(current_anomaly_ids) == len(set(current_anomaly_ids))
    previous_anomaly_ids = {
        anomaly["id"]
        for relative_path in REVIEW_RUNS
        for review in yaml.safe_load(
            _git_bytes(
                ROOT,
                "show",
                f"{PRE_SIX_P0_RECEIPTS_COMMIT}:{relative_path}",
            ).decode("utf-8")
        )["reviews"]
        for anomaly in review["payload"]["anomalies"]
    }
    observed_anomaly_ids = set(current_anomaly_ids)
    actor_provenance = yaml.safe_load(
        ACTOR_PROVENANCE_PATH.read_text(encoding="utf-8")
    )
    retained_new_anomaly_ids = set(
        actor_provenance["decision"]["retained_new_anomaly_ids"]
    )
    assert previous_anomaly_ids - observed_anomaly_ids == SIX_RESOLVED_P0_IDS
    assert observed_anomaly_ids - previous_anomaly_ids == retained_new_anomaly_ids
    assert execution_debt == EXPECTED_EXECUTION_DEBT


def test_sealed_current_governance_receipts_cover_all_349_reviews(
    review_module,
) -> None:
    assert set(CURRENT_RECEIPT_SEALS) == REVIEW_RUNS
    assert _git(
        ROOT, "rev-list", "--parents", "-n", "1", RECEIPTS_COMMIT
    ).split() == [RECEIPTS_COMMIT, POLICY_COMMIT]

    covered_ids = []
    for relative_path, expected_digest in sorted(CURRENT_RECEIPT_SEALS.items()):
        sealed_bytes = _git_bytes(ROOT, "show", f"{RECEIPTS_COMMIT}:{relative_path}")
        assert review_module.sha256_bytes(sealed_bytes) == expected_digest
        assert (ROOT / relative_path).read_bytes() == sealed_bytes
        receipt = yaml.safe_load(sealed_bytes.decode("utf-8"))
        config = GOVERNANCE_REVIEW_CONFIG[relative_path]
        assert {
            "reviewer_id": receipt["reviewer_id"],
            "review_run_id": receipt["review_run_id"],
            "reviewer_model": receipt["reviewer_model"],
        } == {
            "reviewer_id": config["reviewer_id"],
            "review_run_id": config["review_run_id"],
            "reviewer_model": GOVERNANCE_REVIEWER_MODEL,
        }
        assert [review["id"] for review in receipt["reviews"]] == receipt[
            "assignment"
        ]["source_ids"]
        covered_ids.extend(receipt["assignment"]["source_ids"])

    assert len(covered_ids) == len(set(covered_ids)) == 349


def test_sealed_current_governance_observations_are_unique_per_chapter(
    review_module,
) -> None:
    seen = {}
    duplicates = []
    for relative_path in sorted(CURRENT_RECEIPT_SEALS):
        receipt = yaml.safe_load(
            _git_bytes(ROOT, "show", f"{RECEIPTS_COMMIT}:{relative_path}").decode(
                "utf-8"
            )
        )
        for review in receipt["reviews"]:
            for dimension in ("scientific", "pedagogical"):
                for fact in review["payload"]["dimensions"][dimension]["facts"]:
                    normalised = review_module._normalise_observation(
                        fact["observation"]
                    )
                    key = (review["chapter"], normalised)
                    if normalised and key in seen:
                        duplicates.append((seen[key], review["id"]))
                    seen[key] = review["id"]

    assert not duplicates, f"observations dupliquees: {duplicates}"


def test_findings_only_differ_on_reattested_payload_or_provenance(
    policy, sources, review_module
) -> None:
    document = yaml.safe_load(FINDINGS_PATH.read_text(encoding="utf-8"))
    contract_relative = CONTRACT_RECEIPT_PATH.relative_to(ROOT).as_posix()
    contract_config = GOVERNANCE_REVIEW_CONFIG[contract_relative]
    stale_header = {
        key: document[key]
        for key in (
            "review_run_id",
            "review_receipt_path",
            "review_receipt_sha256",
            "sealing_commit_sha",
        )
    } != {
        "review_run_id": contract_config["review_run_id"],
        "review_receipt_path": contract_relative,
        "review_receipt_sha256": CURRENT_RECEIPT_SEALS[contract_relative],
        "sealing_commit_sha": RECEIPTS_COMMIT,
    }

    findings = review_module.load_findings(FINDINGS_PATH)
    findings_by_id = {finding["id"]: finding for finding in findings}
    sources_by_id = {source["id"]: source for source in sources}
    assert len(findings_by_id) == len(findings) == 349
    assert set(findings_by_id) == set(sources_by_id)

    stale_reviews = []
    for relative_path, expected_digest in sorted(CURRENT_RECEIPT_SEALS.items()):
        receipt = yaml.safe_load(
            _git_bytes(ROOT, "show", f"{RECEIPTS_COMMIT}:{relative_path}").decode(
                "utf-8"
            )
        )
        expected_provenance = {
            "reviewer_id": receipt["reviewer_id"],
            "review_run_id": receipt["review_run_id"],
            "reviewer_model": receipt["reviewer_model"],
            "integrator_id": policy["integrator_id"],
            "review_receipt_path": relative_path,
            "review_receipt_sha256": expected_digest,
            "sealing_commit_sha": RECEIPTS_COMMIT,
        }
        for review in receipt["reviews"]:
            source = sources_by_id[review["id"]]
            finding = findings_by_id[review["id"]]
            assert {
                "id": finding["id"],
                "scope": finding["scope"],
                "chapter": finding["chapter"],
                "source_path": finding["source_path"],
                "source_status": finding["source_status"],
                "capacity_refs": finding["capacity_refs"],
            } == {
                "id": source["id"],
                "scope": source["scope"],
                "chapter": source["chapter"],
                "source_path": source["path"],
                "source_status": source["status"],
                "capacity_refs": source.get("capacity_refs", []),
            }
            if finding["provenance"] != expected_provenance or {
                "dimensions": finding["dimensions"],
                "anomalies": finding["anomalies"],
            } != review["payload"]:
                stale_reviews.append(review["id"])

    assert not stale_header and not stale_reviews, (
        f"findings obsoletes: header={stale_header}, entries={stale_reviews}"
    )


def test_scope_guard_base_is_strict_full_commit(policy, review_module) -> None:
    base_sha = policy["scope_guard"]["implementation_base_sha"]
    assert re.fullmatch(r"[0-9a-f]{40}", base_sha)
    assert _git(ROOT, "rev-parse", "--verify", f"{base_sha}^{{commit}}") == base_sha

    for invalid in ("867e105", "g" * 40, "0" * 40):
        with pytest.raises(
            review_module.ReviewValidationError, match="implementation_base_sha"
        ):
            review_module._changed_paths(ROOT, invalid)

    mutated = copy.deepcopy(policy)
    mutated["scope_guard"]["implementation_base_sha"] = "0" * 40
    with pytest.raises(
        review_module.ReviewValidationError, match="implementation_base_sha"
    ):
        review_module.verify_scope(ROOT, mutated, changed_paths=[])


def test_changed_paths_uses_nul_records_and_rejects_option_injection(
    tmp_path, review_module
) -> None:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "Nexus Tests")
    _git(tmp_path, "config", "user.email", "nexus-tests@example.invalid")
    unusual = tmp_path / "line\nbreak.txt"
    unusual.write_text("initial\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "base")
    base_sha = _git(tmp_path, "rev-parse", "HEAD")
    unusual.write_text("changed\n", encoding="utf-8")

    assert review_module._changed_paths(tmp_path, base_sha) == ["line\nbreak.txt"]

    injected = tmp_path / "injected.diff"
    with pytest.raises(
        review_module.ReviewValidationError, match="implementation_base_sha"
    ):
        review_module._changed_paths(tmp_path, f"--output={injected}")
    assert not injected.exists()


@pytest.mark.parametrize(
    "surface", ["source_path", "source_status", "manifest", "pdf", "tnsi"]
)
def test_verify_scope_rejects_every_guard_drift(policy, review_module, surface) -> None:
    mutated = copy.deepcopy(policy)
    guard = mutated["scope_guard"]
    if surface == "source_path":
        guard["sources"][0]["path"] += ".moved"
    elif surface == "source_status":
        guard["sources"][0]["status"] = "approved"
    elif surface == "manifest":
        guard["build_manifest"]["sha256"] = "sha256:" + "0" * 64
    elif surface == "pdf":
        guard["canonical_pdfs"][0]["sha256"] = "sha256:" + "0" * 64
    else:
        guard["tnsi_tracked_files_digest"] = "sha256:" + "0" * 64
    with pytest.raises(review_module.ReviewValidationError, match="scope"):
        review_module.verify_scope(ROOT, mutated)


def test_verify_scope_rejects_changed_path_outside_allowlist(
    policy, review_module
) -> None:
    review_module.verify_scope(
        ROOT, policy, changed_paths=sorted(REVIEW_OUTPUTS | REVIEW_RUNS)
    )
    review_module.verify_scope(ROOT, policy, changed_paths=sorted(ALLOWED_FILES))
    with pytest.raises(review_module.ReviewValidationError, match="allowlist"):
        review_module.verify_scope(
            ROOT,
            policy,
            changed_paths=["NSI/chapitres/TNSI-ALGORITHMIQUE/contrat.yaml"],
        )


def _schema_entry(index: int) -> dict:
    digest = "sha256:" + f"{index + 1:064x}"[-64:]
    fact = {
        "path": f"NSI/chapitres/1NSI-TEST/cours/OBJ-{index:03d}.tex",
        "line_start": 1,
        "line_end": 1,
        "excerpt_sha256": digest,
        "fact_type": "source_statement",
        "observation": f"Observation specifique {index}.",
    }
    dimension = {
        "verdict": "pass",
        "justification": f"Justification specifique {index}.",
        "facts": [fact],
        "anomaly_ids": [],
    }
    return {
        "id": f"1NSI-TEST-{index:03d}",
        "scope": "object",
        "chapter": "1NSI-TEST",
        "source_path": fact["path"],
        "source_status": "needs_review",
        "source_sha256": digest,
        "contract_path": "NSI/chapitres/1NSI-TEST/contrat.yaml",
        "capacity_refs": [],
        "protocol_digest": digest,
        "dependency_digest": digest,
        "dependency_digests": {
            key: digest
            for key in (
                "protocol",
                "source",
                "contract",
                "linked_objects",
                "help",
                "correction",
                "receipt",
                "python",
            )
        },
        "provenance": {
            "reviewer_id": "independent-reviewer",
            "review_run_id": "unit-run",
            "reviewer_model": "unit-model",
            "integrator_id": "integrator",
            "review_receipt_path": "audit/reviews/1nsi/runs/2026-08-10-contracts.yaml",
            "review_receipt_sha256": digest,
            "sealing_commit_sha": "1" * 40,
        },
        "dimensions": {
            "scientific": copy.deepcopy(dimension),
            "pedagogical": copy.deepcopy(dimension),
        },
        "anomalies": [],
        "execution_observation": None,
        "publication_approval": False,
        "human_confirmation_required": True,
    }


def test_schema_is_closed_and_requires_exactly_349_entries() -> None:
    assert SCHEMA_PATH.is_file(), "le schema de revue doit etre cree"
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert schema["additionalProperties"] is False
    assert schema["properties"]["entries"]["minItems"] == 349
    assert schema["properties"]["entries"]["maxItems"] == 349
    assert schema["$defs"]["entry"]["additionalProperties"] is False
    assert schema["$defs"]["fact"]["additionalProperties"] is False
    assert schema["$defs"]["provenance"]["additionalProperties"] is False
    assert set(schema["$defs"]["provenance"]["required"]) == {
        "reviewer_id",
        "review_run_id",
        "reviewer_model",
        "integrator_id",
        "review_receipt_path",
        "review_receipt_sha256",
        "sealing_commit_sha",
    }

    document = {
        "artifact_type": "1nsi_content_reviews",
        "schema_version": 1,
        "manual": "1NSI",
        "protocol_digest": "sha256:" + "1" * 64,
        "publication_approval": False,
        "human_confirmation_required": True,
        "entries": [_schema_entry(index) for index in range(349)],
    }
    Draft202012Validator(schema).validate(document)


def test_schema_rejects_approval_and_unknown_properties() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    document = {
        "artifact_type": "1nsi_content_reviews",
        "schema_version": 1,
        "manual": "1NSI",
        "protocol_digest": "sha256:" + "1" * 64,
        "publication_approval": True,
        "human_confirmation_required": True,
        "entries": [_schema_entry(index) for index in range(349)],
        "unexpected": "forbidden",
    }
    errors = list(Draft202012Validator(schema).iter_errors(document))
    assert len(errors) >= 2


def test_review_run_receipt_schema_is_closed_and_validates_yaml(sealed_review) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    receipt_schema = schema["$defs"]["review_run_receipt"]
    assert receipt_schema["additionalProperties"] is False
    assert receipt_schema["properties"]["assignment"]["additionalProperties"] is False
    review_schema = receipt_schema["properties"]["reviews"]["items"]
    assert review_schema["additionalProperties"] is False
    assert set(review_schema["required"]) == {"id", "chapter", "scope", "payload"}
    assert review_schema["properties"]["payload"]["additionalProperties"] is False
    manifest_schema = receipt_schema["properties"]["source_manifest"]
    assert manifest_schema["additionalProperties"] is False
    assert (
        manifest_schema["properties"]["entries"]["items"]["additionalProperties"]
        is False
    )
    assert set(manifest_schema["required"]) == {
        "review_tool_sha256",
        "execution_checker_sha256",
        "execution_common_sha256",
        "entries",
    }
    wrapper = {
        "$schema": schema["$schema"],
        "$ref": "#/$defs/review_run_receipt",
        "$defs": schema["$defs"],
    }
    Draft202012Validator.check_schema(wrapper)
    parsed = yaml.safe_load(sealed_review["receipt_path"].read_text(encoding="utf-8"))
    Draft202012Validator(wrapper).validate(parsed)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("source", "source scellee"),
        ("dependency", "dependance scellee"),
        ("review_tool", "outil de revue"),
        ("execution_checker", "verificateur d'execution"),
        ("execution_common", "support d'execution"),
    ],
)
def test_rejects_post_sealing_source_manifest_mutation(
    sealed_review, review_module, mutation, message
) -> None:
    root = sealed_review["root"]
    source = sealed_review["sources"][0]
    if mutation == "source":
        path = root / source["path"]
        path.write_text(
            path.read_text(encoding="utf-8") + "Mutation source.\n", encoding="utf-8"
        )
    elif mutation == "dependency":
        path = root / "NSI/chapitres/1NSI-UNIT/contrat.yaml"
        path.write_text(
            path.read_text(encoding="utf-8") + "mutation: true\n", encoding="utf-8"
        )
    elif mutation == "review_tool":
        path = root / "scripts/review_1nsi_content.py"
        path.write_text(
            path.read_text(encoding="utf-8") + "# mutation\n", encoding="utf-8"
        )
    elif mutation == "execution_checker":
        path = root / "NSI/scripts/verify_python.py"
        path.write_text(
            path.read_text(encoding="utf-8") + "# mutation\n", encoding="utf-8"
        )
    else:
        path = root / "NSI/scripts/common.py"
        path.write_text(
            path.read_text(encoding="utf-8") + "# mutation\n", encoding="utf-8"
        )

    finding = _finding(
        source,
        provenance=sealed_review["provenance"],
        root=root,
    )
    with pytest.raises(review_module.ReviewValidationError, match=message):
        review_module.validate_findings(
            [finding], [source], root, sealed_review["policy"], require_complete=True
        )


def test_review_receipt_manifest_covers_exact_assignment_and_excludes_itself(
    sealed_review, review_module
) -> None:
    receipt = sealed_review["receipt"]
    assert {entry["id"] for entry in receipt["source_manifest"]["entries"]} == set(
        receipt["assignment"]["source_ids"]
    )
    for source in sealed_review["sources"]:
        manifest = review_module.dependency_manifest(
            source, sealed_review["sources"], sealed_review["root"]
        )
        dependency_paths = {
            record["path"] for records in manifest.values() for record in records
        }
        assert (
            sealed_review["provenance"]["review_receipt_path"] not in dependency_paths
        )

    mutated = copy.deepcopy(receipt)
    mutated["source_manifest"]["entries"].pop()
    _reseal_review_receipt(sealed_review, mutated)
    source = sealed_review["sources"][0]
    finding = _finding(
        source,
        provenance=sealed_review["provenance"],
        root=sealed_review["root"],
    )
    with pytest.raises(
        review_module.ReviewValidationError, match="manifest.*affectation"
    ):
        review_module.validate_findings(
            [finding],
            [source],
            sealed_review["root"],
            sealed_review["policy"],
            require_complete=True,
        )


def test_review_receipt_is_parsed_and_indexed_once_per_validation_run(
    sealed_review, review_module, monkeypatch
) -> None:
    review_module._REVIEW_RECEIPT_CACHE.clear()
    calls = 0
    original = review_module._read_sealed_review_receipt

    def counted(*args, **kwargs):
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(review_module, "_read_sealed_review_receipt", counted)
    findings = [
        _finding(
            source,
            provenance=sealed_review["provenance"],
            root=sealed_review["root"],
        )
        for source in sealed_review["sources"]
    ]
    review_module.validate_findings(
        findings,
        sealed_review["sources"],
        sealed_review["root"],
        sealed_review["policy"],
        require_complete=True,
    )
    assert calls == 1


def test_verifier_and_receipt_schema_are_loaded_only_from_requested_root(
    tmp_path, review_module
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    _install_review_support(first)
    _install_review_support(second)
    first_module = review_module._verify_module(first)
    second_module = review_module._verify_module(second)

    assert first_module is review_module._verify_module(first.resolve())
    assert first_module is not second_module
    assert Path(first_module.__file__).resolve().is_relative_to(first.resolve())
    assert Path(second_module.__file__).resolve().is_relative_to(second.resolve())
    assert Path(first_module.ROOT).resolve() == (first / "NSI").resolve()

    (first / "audit/schemas/v1/1nsi-content-review.schema.json").unlink()
    review_module._REVIEW_RECEIPT_CACHE.clear()
    with pytest.raises(
        review_module.ReviewValidationError, match="schema.*introuvable"
    ):
        review_module._receipt_schema(first)


def test_verifier_cache_is_invalidated_by_checker_or_common_digest(
    tmp_path, review_module
) -> None:
    _install_review_support(tmp_path)
    first = review_module._verify_module(tmp_path)

    verifier_path = tmp_path / "NSI/scripts/verify_python.py"
    verifier_path.write_text(
        verifier_path.read_text(encoding="utf-8") + "# checker mutation\n",
        encoding="utf-8",
    )
    after_checker = review_module._verify_module(tmp_path)
    assert after_checker is not first

    common_path = tmp_path / "NSI/scripts/common.py"
    common_path.write_text(
        common_path.read_text(encoding="utf-8") + "# common mutation\n",
        encoding="utf-8",
    )
    after_common = review_module._verify_module(tmp_path)
    assert after_common is not after_checker


def test_accepts_finding_with_git_sealed_review_receipt(
    sealed_review, review_module
) -> None:
    source = sealed_review["sources"][0]
    finding = _finding(
        source,
        provenance=sealed_review["provenance"],
        root=sealed_review["root"],
    )

    validated = review_module.validate_findings(
        [finding],
        [source],
        sealed_review["root"],
        sealed_review["policy"],
        require_complete=True,
    )

    assert validated[0]["provenance"] == sealed_review["provenance"]


def test_accepts_finding_exactly_equal_to_sealed_review_payload(
    sealed_review, review_module
) -> None:
    finding = _seal_finding_payload_with_anomalies(sealed_review)
    source = sealed_review["sources"][0]

    validated = review_module.validate_findings(
        [finding],
        [source],
        sealed_review["root"],
        sealed_review["policy"],
        require_complete=True,
    )

    assert validated[0]["dimensions"] == finding["dimensions"]
    assert validated[0]["anomalies"] == finding["anomalies"]


@pytest.mark.parametrize(
    "mutation",
    ["verdict", "justification", "facts", "anomaly_ids", "anomalies"],
)
def test_rejects_finding_payload_different_from_sealed_review(
    sealed_review, review_module, mutation
) -> None:
    finding = _seal_finding_payload_with_anomalies(sealed_review)
    source = sealed_review["sources"][0]
    if mutation == "verdict":
        finding["dimensions"]["pedagogical"]["verdict"] = "not_applicable"
    elif mutation == "justification":
        finding["dimensions"]["scientific"]["justification"] += " Mutation."
    elif mutation == "facts":
        fact = copy.deepcopy(finding["dimensions"]["scientific"]["facts"][0])
        fact["observation"] = "Fait ajoute uniquement au finding."
        finding["dimensions"]["scientific"]["facts"].append(fact)
    elif mutation == "anomaly_ids":
        finding["dimensions"]["scientific"]["anomaly_ids"].reverse()
    else:
        finding["anomalies"][0]["consequence"] += " Mutation."

    with pytest.raises(review_module.ReviewValidationError, match="payload scelle"):
        review_module.validate_findings(
            [finding],
            [source],
            sealed_review["root"],
            sealed_review["policy"],
            require_complete=True,
        )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("run", "review_run_id"),
        ("reviewer", "reviewer_id"),
        ("model", "reviewer_model"),
        ("protocol", "protocol_digest"),
        ("source_not_assigned", "source non assignee"),
        ("review_absent", "review absente"),
        ("review_duplicated", "review dupliquee"),
        ("assignment_chapter", "chapitre d'affectation"),
        ("assignment_scope", "scope d'affectation"),
        ("review_chapter", "chapitre de review"),
        ("review_scope", "scope de review"),
        ("schema_extra", "schema du recu"),
    ],
)
def test_rejects_review_receipt_not_bound_to_current_finding(
    sealed_review, review_module, mutation, message
) -> None:
    receipt = copy.deepcopy(sealed_review["receipt"])
    source = sealed_review["sources"][0]
    if mutation == "run":
        receipt["review_run_id"] = "another-run"
    elif mutation == "reviewer":
        receipt["reviewer_id"] = "another-reviewer"
    elif mutation == "model":
        receipt["reviewer_model"] = "another-model"
    elif mutation == "protocol":
        receipt["protocol_digest"] = "sha256:" + "0" * 64
    elif mutation == "source_not_assigned":
        receipt["assignment"]["source_ids"].remove(source["id"])
    elif mutation == "review_absent":
        receipt["reviews"] = [
            review for review in receipt["reviews"] if review["id"] != source["id"]
        ]
    elif mutation == "review_duplicated":
        receipt["reviews"].append(copy.deepcopy(receipt["reviews"][0]))
    elif mutation == "assignment_chapter":
        receipt["assignment"]["chapters"] = ["1NSI-OTHER"]
    elif mutation == "assignment_scope":
        receipt["assignment"]["scope"] = "contract"
    elif mutation == "review_chapter":
        receipt["reviews"][0]["chapter"] = "1NSI-OTHER"
    elif mutation == "review_scope":
        receipt["reviews"][0]["scope"] = "contract"
    else:
        receipt["unexpected"] = "forbidden"
    _reseal_review_receipt(sealed_review, receipt)
    finding = _finding(
        source,
        provenance=sealed_review["provenance"],
        root=sealed_review["root"],
    )

    with pytest.raises(review_module.ReviewValidationError, match=message):
        review_module.validate_findings(
            [finding],
            [source],
            sealed_review["root"],
            sealed_review["policy"],
            require_complete=True,
        )


def test_review_receipt_rejects_invalid_reviewed_at_format(
    sealed_review, review_module
) -> None:
    receipt = copy.deepcopy(sealed_review["receipt"])
    receipt["reviewed_at"] = "2026-08-10"
    _reseal_review_receipt(sealed_review, receipt)
    source = sealed_review["sources"][0]
    finding = _finding(
        source,
        provenance=sealed_review["provenance"],
        root=sealed_review["root"],
    )

    with pytest.raises(
        review_module.ReviewValidationError, match="reviewed_at|date-time"
    ):
        review_module.validate_findings(
            [finding],
            [source],
            sealed_review["root"],
            sealed_review["policy"],
            require_complete=True,
        )


@pytest.mark.parametrize("malformed", ["finding", "fact", "anomaly"])
def test_malformed_finding_types_raise_normalized_validation_error(
    sealed_review, review_module, malformed
) -> None:
    source = sealed_review["sources"][0]
    finding = _finding(
        source,
        provenance=sealed_review["provenance"],
        root=sealed_review["root"],
    )
    findings = [finding]
    if malformed == "finding":
        findings = [None]
    elif malformed == "fact":
        finding["dimensions"]["scientific"]["facts"] = [None]
    else:
        finding["anomalies"] = [None]

    with pytest.raises(review_module.ReviewValidationError):
        review_module.validate_findings(
            findings,
            [source],
            sealed_review["root"],
            sealed_review["policy"],
            require_complete=True,
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("path", None),
        ("path", []),
        ("line_start", None),
        ("line_start", "1"),
        ("line_start", []),
        ("line_start", True),
        ("line_start", 0),
        ("line_end", "1"),
        ("line_end", False),
        ("line_end", 0),
        ("excerpt_sha256", None),
        ("excerpt_sha256", []),
        ("excerpt_sha256", "not-a-digest"),
        ("fact_type", None),
        ("fact_type", []),
        ("fact_type", True),
        ("fact_type", "unknown_type"),
        ("observation", None),
        ("observation", []),
        ("observation", True),
        ("observation", ""),
    ],
)
def test_validate_fact_normalizes_malformed_field_boundaries(
    sealed_review, review_module, field, value
) -> None:
    source = sealed_review["sources"][0]
    fact = _fact(source, "Observation valide.", root=sealed_review["root"])
    fact[field] = value

    with pytest.raises(review_module.ReviewValidationError):
        review_module._validate_fact(fact, {source["path"]}, sealed_review["root"])


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("path", "recu de revue"),
        ("extra_run_path", "recu de revue"),
        ("digest", "digest du recu"),
        ("commit", "commit de scellement"),
        ("not_in_commit", "absent du commit"),
        ("not_ancestor", "ancetre"),
        ("worktree_drift", "octets du recu"),
    ],
)
def test_rejects_unsealed_review_receipt(
    sealed_review, review_module, mutation, message
) -> None:
    root = sealed_review["root"]
    provenance = copy.deepcopy(sealed_review["provenance"])
    if mutation == "path":
        provenance["review_receipt_path"] = "audit/1NSI_CONTENT_REVIEWS.json"
    elif mutation == "extra_run_path":
        path = root / "audit/reviews/1nsi/runs/2026-08-10-unplanned.yaml"
        path.write_text("run_id: unplanned\n", encoding="utf-8")
        _git(root, "add", path.relative_to(root).as_posix())
        _git(root, "commit", "-q", "-m", "seal unplanned receipt")
        provenance["review_receipt_path"] = path.relative_to(root).as_posix()
        provenance["review_receipt_sha256"] = _sha(path)
        provenance["sealing_commit_sha"] = _git(root, "rev-parse", "HEAD")
        sealed_review["policy"]["allowlist"].append(provenance["review_receipt_path"])
    elif mutation == "digest":
        provenance["review_receipt_sha256"] = "sha256:" + "0" * 64
    elif mutation == "commit":
        provenance["sealing_commit_sha"] = "0" * 40
    elif mutation == "not_in_commit":
        path = root / "audit/reviews/1nsi/runs/2026-08-10-algorithms.yaml"
        path.write_text("run_id: not-committed\n", encoding="utf-8")
        provenance["review_receipt_path"] = path.relative_to(root).as_posix()
        provenance["review_receipt_sha256"] = _sha(path)
    elif mutation == "not_ancestor":
        tree = _git(root, "rev-parse", "HEAD^{tree}")
        provenance["sealing_commit_sha"] = _git(
            root, "commit-tree", tree, input_text="unrelated seal\n"
        )
    else:
        sealed_review["receipt_path"].write_text("run_id: modified\n", encoding="utf-8")

    source = sealed_review["sources"][0]
    finding = _finding(source, provenance=provenance, root=root)
    with pytest.raises(review_module.ReviewValidationError, match=message):
        review_module.validate_findings(
            [finding], [source], root, sealed_review["policy"], require_complete=True
        )


@pytest.mark.parametrize(
    ("dimension_name", "verdict"),
    [
        ("scientific", "human_confirmation_required"),
        ("pedagogical", "not_applicable"),
    ],
)
def test_dimension_with_anomaly_requires_issue_verdict(
    sealed_review, review_module, dimension_name, verdict
) -> None:
    source = sealed_review["sources"][0]
    finding = _finding(
        source,
        provenance=sealed_review["provenance"],
        root=sealed_review["root"],
    )
    anomaly_id = "1NSI-REV-UNIT-DIMENSION"
    finding["dimensions"][dimension_name]["verdict"] = verdict
    finding["dimensions"][dimension_name]["anomaly_ids"] = [anomaly_id]
    finding["anomalies"] = [
        {
            "id": anomaly_id,
            "severity": "P1",
            "dimension": dimension_name,
            "fact": copy.deepcopy(finding["dimensions"][dimension_name]["facts"][0]),
            "consequence": "Consequence dimensionnelle de test.",
            "expected_action": "Action dimensionnelle de test.",
        }
    ]

    with pytest.raises(review_module.ReviewValidationError, match="verdict issue"):
        review_module.validate_findings(
            [finding],
            [source],
            sealed_review["root"],
            sealed_review["policy"],
            require_complete=True,
        )


def _approved_release_fixture(policy) -> tuple[dict, dict]:
    approved_policy = copy.deepcopy(policy)
    approved_policy["decision"].update(
        {
            "publication_approval": True,
            "human_confirmation_required": False,
            "release_acceptance": True,
        }
    )
    entries = []
    for index, scoped_source in enumerate(policy["scope_guard"]["sources"]):
        entry = _schema_entry(index)
        entry.update(
            {
                "id": scoped_source["id"],
                "scope": "contract"
                if scoped_source["id"].startswith("contract:")
                else "object",
                "chapter": scoped_source["path"].split("/")[2],
                "source_path": scoped_source["path"],
                "source_status": scoped_source["status"],
                "contract_path": (
                    scoped_source["path"]
                    if scoped_source["id"].startswith("contract:")
                    else f"NSI/chapitres/{scoped_source['path'].split('/')[2]}/contrat.yaml"
                ),
                "protocol_digest": policy["protocol_digest"],
                "publication_approval": True,
                "human_confirmation_required": False,
            }
        )
        entry["dependency_digests"]["protocol"] = policy["protocol_digest"]
        entries.append(entry)
    document = {
        "artifact_type": "1nsi_content_reviews",
        "schema_version": 1,
        "manual": "1NSI",
        "protocol_digest": policy["protocol_digest"],
        "publication_approval": True,
        "human_confirmation_required": False,
        "entries": entries,
    }
    return approved_policy, document


def test_release_gate_can_pass_only_fully_approved_clean_document(
    policy, review_module
) -> None:
    approved_policy, document = _approved_release_fixture(policy)
    assert review_module.release_gate_allows(document, approved_policy) is True


@pytest.mark.parametrize(
    "blocker",
    [
        "policy_publication_false",
        "policy_human_confirmation",
        "document_publication_false",
        "document_human_confirmation",
        "entry_publication_false",
        "entry_human_confirmation",
        "entry_anomaly",
        "entry_issue",
        "entry_human_verdict",
    ],
)
def test_release_gate_rejects_every_document_or_entry_blocker(
    policy, review_module, blocker
) -> None:
    approved_policy, document = _approved_release_fixture(policy)
    entry = document["entries"][0]
    if blocker == "policy_publication_false":
        approved_policy["decision"]["publication_approval"] = False
    elif blocker == "policy_human_confirmation":
        approved_policy["decision"]["human_confirmation_required"] = True
    elif blocker == "document_publication_false":
        document["publication_approval"] = False
    elif blocker == "document_human_confirmation":
        document["human_confirmation_required"] = True
    elif blocker == "entry_publication_false":
        entry["publication_approval"] = False
    elif blocker == "entry_human_confirmation":
        entry["human_confirmation_required"] = True
    elif blocker == "entry_anomaly":
        entry["anomalies"] = [{"id": "1NSI-REV-RELEASE"}]
    elif blocker == "entry_issue":
        entry["dimensions"]["scientific"]["verdict"] = "issue"
    else:
        entry["dimensions"]["pedagogical"]["verdict"] = "human_confirmation_required"

    assert review_module.release_gate_allows(document, approved_policy) is False


@pytest.mark.parametrize("mutation", ["empty", "missing", "duplicate", "unknown"])
def test_release_gate_requires_exact_scope_guard_id_set(
    policy, review_module, mutation
) -> None:
    approved_policy, document = _approved_release_fixture(policy)
    if mutation == "empty":
        document["entries"] = []
    elif mutation == "missing":
        document["entries"].pop()
    elif mutation == "duplicate":
        document["entries"][-1] = copy.deepcopy(document["entries"][0])
    else:
        document["entries"][-1]["id"] = "1NSI-UNKNOWN"

    assert review_module.release_gate_allows(document, approved_policy) is False


def test_release_gate_rejects_malformed_structure_and_missing_bwrap(
    policy, review_module, monkeypatch, tmp_path
) -> None:
    approved_policy, document = _approved_release_fixture(policy)
    document["entries"][0]["dimensions"].pop("pedagogical")
    assert review_module.release_gate_allows(document, approved_policy) is False

    _approved_policy, complete = _approved_release_fixture(policy)
    monkeypatch.setattr(review_module, "BWRAP_PATH", tmp_path / "missing-bwrap")
    assert review_module.release_gate_allows(complete, _approved_policy) is False


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("digest_supplied", "digest"),
        ("verdict_without_evidence", "preuve"),
        ("pass_with_issue", "verdict issue"),
        ("tnsi_path", "TNSI"),
        ("approval", "approval"),
        ("unknown_ref", "reference"),
        ("reviewer_integrator", "integrateur"),
        ("incomplete_provenance", "provenance"),
        ("bad_excerpt_digest", "extrait"),
        ("evidence_outside_graph", "dependances"),
        ("unknown_field", "champ inconnu"),
    ],
)
def test_reject_invalid_finding(
    sealed_review, review_module, mutation, message
) -> None:
    root = sealed_review["root"]
    policy = sealed_review["policy"]
    source = sealed_review["sources"][0]
    finding = _finding(source, provenance=sealed_review["provenance"], root=root)
    if mutation == "digest_supplied":
        finding["source_sha256"] = source["source_sha256"]
    elif mutation == "verdict_without_evidence":
        finding["dimensions"]["scientific"]["facts"] = []
    elif mutation == "pass_with_issue":
        finding["dimensions"]["scientific"]["anomaly_ids"] = ["1NSI-REV-UNIT"]
        finding["anomalies"] = [
            {
                "id": "1NSI-REV-UNIT",
                "severity": "P0",
                "dimension": "scientific",
                "fact": finding["dimensions"]["scientific"]["facts"][0],
                "consequence": "Consequence de test.",
                "expected_action": "Action de test.",
            }
        ]
    elif mutation == "tnsi_path":
        finding["source_path"] = "NSI/chapitres/TNSI-ALGORITHMIQUE/contrat.yaml"
    elif mutation == "approval":
        finding["publication_approval"] = True
    elif mutation == "unknown_ref":
        finding["capacity_refs"] = ["UNKNOWN-CAPACITY"]
    elif mutation == "reviewer_integrator":
        finding["provenance"]["reviewer_id"] = "integrator"
    elif mutation == "incomplete_provenance":
        finding["provenance"].pop("reviewer_model")
    elif mutation == "evidence_outside_graph":
        outside = root / "outside.txt"
        outside.write_text("preuve hors graphe\n", encoding="utf-8")
        fact = finding["dimensions"]["scientific"]["facts"][0]
        fact["path"] = "outside.txt"
        fact["excerpt_sha256"] = _excerpt_digest(outside)
    elif mutation == "unknown_field":
        finding["approved"] = True
    else:
        finding["dimensions"]["scientific"]["facts"][0]["excerpt_sha256"] = (
            "sha256:" + "0" * 64
        )
    with pytest.raises(review_module.ReviewValidationError, match=message):
        review_module.validate_findings(
            [finding],
            [source],
            root,
            policy,
            require_complete=True,
        )


def test_rejects_missing_and_duplicate_findings(policy, sources, review_module) -> None:
    selected = [item for item in sources if item["scope"] == "object"][:2]
    with pytest.raises(review_module.ReviewValidationError, match="manquante"):
        review_module.validate_findings(
            [_finding(selected[0])], selected, ROOT, policy, require_complete=True
        )
    with pytest.raises(review_module.ReviewValidationError, match="doublon"):
        review_module.validate_findings(
            [_finding(selected[0]), _finding(selected[0])],
            selected,
            ROOT,
            policy,
            require_complete=True,
        )


def test_rejects_normalized_duplicate_observations(
    sealed_review, review_module
) -> None:
    selected = sealed_review["sources"]
    findings = [
        _finding(
            item,
            provenance=sealed_review["provenance"],
            root=sealed_review["root"],
        )
        for item in selected
    ]
    findings[0]["dimensions"]["scientific"]["facts"][0]["observation"] = (
        "Meme fait ancre."
    )
    findings[1]["dimensions"]["scientific"]["facts"][0]["observation"] = (
        "  meme   FAIT ancre "
    )
    receipt = copy.deepcopy(sealed_review["receipt"])
    findings_by_id = {finding["id"]: finding for finding in findings}
    for review in receipt["reviews"]:
        finding = findings_by_id[review["id"]]
        review["payload"] = {
            "dimensions": copy.deepcopy(finding["dimensions"]),
            "anomalies": copy.deepcopy(finding["anomalies"]),
        }
    _reseal_review_receipt(sealed_review, receipt)
    for finding in findings:
        finding["provenance"] = copy.deepcopy(sealed_review["provenance"])
    with pytest.raises(review_module.ReviewValidationError, match="observation"):
        review_module.validate_findings(
            findings,
            selected,
            sealed_review["root"],
            sealed_review["policy"],
            require_complete=True,
        )


def test_generate_register_is_deterministic_with_fixture(
    sealed_review, review_module
) -> None:
    selected = sealed_review["sources"]
    findings = [
        _finding(
            item,
            provenance=sealed_review["provenance"],
            root=sealed_review["root"],
        )
        for item in selected
    ]
    first = review_module.generate_register(
        findings,
        sealed_review["root"],
        sealed_review["policy"],
        sources=selected,
        require_complete=True,
    )
    second = review_module.generate_register(
        copy.deepcopy(findings),
        sealed_review["root"],
        sealed_review["policy"],
        sources=selected,
        require_complete=True,
    )
    assert first == second
    assert first["publication_approval"] is False
    assert first["human_confirmation_required"] is True
    assert len(first["entries"]) == 2
    assert all(
        SHA256.fullmatch(entry["dependency_digest"]) for entry in first["entries"]
    )


@pytest.mark.parametrize(
    "dependency_class",
    [
        "protocol",
        "source",
        "contract",
        "linked_objects",
        "help",
        "correction",
        "receipt",
        "python",
    ],
)
def test_real_dependency_mutation_changes_required_class_digest(
    tmp_path, policy, review_module, dependency_class
) -> None:
    chapter = tmp_path / "NSI/chapitres/1NSI-UNIT"
    paths = {
        "source": chapter / "exercices/1NSI-UNIT-EX-001.tex",
        "contract": chapter / "contrat.yaml",
        "linked_objects": chapter / "exercices/1NSI-UNIT-LINKED.tex",
        "help": chapter / "methodes/1NSI-UNIT-HELP.tex",
        "correction": chapter / "corriges/1NSI-UNIT-CORR.tex",
        "receipt": chapter / "validations/1NSI-UNIT-EX-001.execution.json",
        "python": chapter / "code/example.py",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["contract"].write_text(
        "chapitre: 1NSI-UNIT\nstatut: draft\ncapacites: []\n", encoding="utf-8"
    )
    paths["source"].write_text(
        '% META: {"id":"1NSI-UNIT-EX-001","chapitre":"1NSI-UNIT",'
        '"type_objet":"exercice","status":"verified"}\n'
        "Code publie : \\texttt{code/example.py}.\n",
        encoding="utf-8",
    )
    paths["linked_objects"].write_text("Objet lie.\n", encoding="utf-8")
    paths["help"].write_text("Aide liee.\n", encoding="utf-8")
    paths["correction"].write_text("Corrige lie.\n", encoding="utf-8")
    paths["receipt"].write_text(
        json.dumps({"verdict": "pass", "details": {"checks": []}}), encoding="utf-8"
    )
    paths["python"].write_text("print(42)\n", encoding="utf-8")

    def source_record(
        object_id: str, key: str, object_type: str, metadata: dict
    ) -> dict:
        path = paths[key]
        return {
            "id": object_id,
            "scope": "object",
            "chapter": "1NSI-UNIT",
            "path": path.relative_to(tmp_path).as_posix(),
            "status": "verified",
            "type": object_type,
            "capacity_refs": [],
            "metadata": metadata,
            "source_sha256": _sha(path),
        }

    source = source_record(
        "1NSI-UNIT-EX-001",
        "source",
        "exercice",
        {"corrige_tex": paths["correction"].relative_to(tmp_path / "NSI").as_posix()},
    )
    sources = [
        source,
        source_record(
            "1NSI-UNIT-LINKED",
            "linked_objects",
            "exercice",
            {"exercice_ref": source["id"]},
        ),
        source_record(
            "1NSI-UNIT-HELP",
            "help",
            "coup_de_pouce",
            {"exercice_ref": source["id"]},
        ),
        source_record(
            "1NSI-UNIT-CORR",
            "correction",
            "corrige",
            {"exercice_ref": source["id"]},
        ),
    ]
    mutable_policy = copy.deepcopy(policy)
    before = review_module.dependency_class_digests(
        source, sources, tmp_path, mutable_policy
    )
    before_aggregate = review_module.aggregate_dependency_digest(before)

    if dependency_class == "protocol":
        mutable_policy["protocol_digest"] = "sha256:" + "f" * 64
    else:
        paths[dependency_class].write_text(
            paths[dependency_class].read_text(encoding="utf-8") + "mutation\n",
            encoding="utf-8",
        )

    after = review_module.dependency_class_digests(
        source, sources, tmp_path, mutable_policy
    )
    assert after[dependency_class] != before[dependency_class]
    assert review_module.aggregate_dependency_digest(after) != before_aggregate


def test_dependency_graph_contains_bidirectional_help_correction_and_receipt(
    sources, review_module
) -> None:
    exercise = next(item for item in sources if item["id"] == "1NSI-TC-EX-001")
    manifest = review_module.dependency_manifest(exercise, sources, ROOT)
    assert set(manifest) == {
        "source",
        "contract",
        "linked_objects",
        "help",
        "correction",
        "receipt",
        "python",
    }
    assert any(
        item["path"].endswith("1NSI-TC-EX-001-CDP.tex") for item in manifest["help"]
    )
    assert any(
        item["path"].endswith("1NSI-TC-CO-001.tex") for item in manifest["correction"]
    )
    assert any(
        item["path"].endswith("1NSI-TC-EX-001.execution.json")
        for item in manifest["receipt"]
    )
    linked_paths = {item["path"] for item in manifest["linked_objects"]}
    assert {item["path"] for item in manifest["help"]} <= linked_paths
    assert {item["path"] for item in manifest["correction"]} <= linked_paths


def test_dependency_graph_detects_declared_python_file(tmp_path, review_module) -> None:
    chapter = tmp_path / "NSI" / "chapitres" / "1NSI-UNIT"
    source_path = chapter / "cours" / "1NSI-UNIT-COURS-C1.tex"
    python_path = chapter / "code" / "example.py"
    contract_path = chapter / "contrat.yaml"
    source_path.parent.mkdir(parents=True)
    python_path.parent.mkdir(parents=True)
    contract_path.write_text("chapitre: 1NSI-UNIT\nstatut: draft\n", encoding="utf-8")
    python_path.write_text("print(42)\n", encoding="utf-8")
    source_path.write_text(
        '% META: {"id":"1NSI-UNIT-COURS-C1","chapitre":"1NSI-UNIT",'
        '"type_objet":"cours","status":"needs_review"}\n'
        "Code publie : \\texttt{code/example.py}.\n",
        encoding="utf-8",
    )
    source = {
        "id": "1NSI-UNIT-COURS-C1",
        "scope": "object",
        "chapter": "1NSI-UNIT",
        "path": source_path.relative_to(tmp_path).as_posix(),
        "status": "needs_review",
        "type": "cours",
        "metadata": {},
    }
    manifest = review_module.dependency_manifest(source, [source], tmp_path)
    assert manifest["python"] == [
        {
            "path": python_path.relative_to(tmp_path).as_posix(),
            "sha256": _sha(python_path),
        }
    ]


@pytest.mark.parametrize(
    ("object_id", "receipt_stem"),
    [
        ("1NSI-TC-TD1", "07_td1_station_meteo"),
        ("1NSI-TC-TD2", "07_td2_classement_esport"),
    ],
)
def test_receipt_resolution_uses_real_source_stem_for_td(
    sources, review_module, object_id, receipt_stem
) -> None:
    source = next(item for item in sources if item["id"] == object_id)
    manifest = review_module.dependency_manifest(source, sources, ROOT)

    assert manifest["receipt"] == [
        {
            "path": (
                "NSI/chapitres/1NSI-TYPES-CONSTRUITS/validations/"
                f"{receipt_stem}.execution.json"
            ),
            "sha256": _sha(
                ROOT
                / "NSI/chapitres/1NSI-TYPES-CONSTRUITS/validations"
                / f"{receipt_stem}.execution.json"
            ),
        }
    ]
    observation = review_module.execution_observation(source, ROOT)
    assert observation["receipt_sha256"] == manifest["receipt"][0]["sha256"]
    assert "missing_receipt" not in observation["anomalies"]


def test_receipt_resolution_rejects_distinct_id_and_stem_candidates(
    tmp_path, review_module
) -> None:
    chapter = tmp_path / "NSI/chapitres/1NSI-UNIT"
    source_path = chapter / "cours/source-stem.tex"
    validations = chapter / "validations"
    source_path.parent.mkdir(parents=True)
    validations.mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        "chapitre: 1NSI-UNIT\nstatut: draft\ncapacites: []\n", encoding="utf-8"
    )
    source_path.write_text(
        '% META: {"id":"META-ID","chapitre":"1NSI-UNIT",'
        '"type_objet":"cours","status":"verified"}\n'
        "% BEGIN-TRACE\n% print(2)\n% EXPECTED\n% 2\n% END-TRACE\n",
        encoding="utf-8",
    )
    for name in ("META-ID", "source-stem"):
        (validations / f"{name}.execution.json").write_text(
            json.dumps({"verdict": "pass", "details": {"checks": []}}),
            encoding="utf-8",
        )
    source = {
        "id": "META-ID",
        "scope": "object",
        "chapter": "1NSI-UNIT",
        "path": source_path.relative_to(tmp_path).as_posix(),
        "status": "verified",
        "type": "cours",
        "capacity_refs": [],
        "metadata": {},
    }

    with pytest.raises(review_module.ReviewValidationError, match="candidats de recu"):
        review_module.dependency_manifest(source, [source], tmp_path)


def test_confined_python_cannot_write_outside_sandbox(tmp_path, review_module) -> None:
    escaped = tmp_path / "escaped.txt"
    rc, _out, err = review_module._confined_python(
        f"open({str(escaped)!r}, 'w').write('escape')\n", timeout=2
    )

    assert rc != 0
    assert not escaped.exists()
    assert "No such file" in err or "Read-only" in err
    rc, _out, _err = review_module._confined_python(
        f"open({str(ROOT / 'AGENTS.md')!r}).read()\n", timeout=2
    )
    assert rc != 0, "le depot ne doit pas etre monte dans le sandbox"


def test_confined_python_has_no_network(review_module) -> None:
    rc, out, err = review_module._confined_python(
        "import socket\n"
        "try:\n"
        "    socket.create_connection(('1.1.1.1', 53), timeout=0.2)\n"
        "except OSError:\n"
        "    print('network-blocked')\n"
        "else:\n"
        "    raise RuntimeError('network available')\n",
        timeout=2,
    )

    assert rc == 0, err
    assert out.strip() == "network-blocked"


def test_cgroup_tasksmax_bounds_fork_bomb(review_module) -> None:
    rc, out, err = review_module._confined_python(
        "import os, signal, time\n"
        "children = []\n"
        "for _ in range(64):\n"
        "    try:\n"
        "        child = os.fork()\n"
        "    except OSError:\n"
        "        print(f'tasks-bounded:{len(children)}', flush=True)\n"
        "        break\n"
        "    if child == 0:\n"
        "        time.sleep(30)\n"
        "        os._exit(0)\n"
        "    children.append(child)\n"
        "else:\n"
        "    print('tasks-unbounded', flush=True)\n"
        "for child in children:\n"
        "    os.kill(child, signal.SIGKILL)\n"
        "for child in children:\n"
        "    os.waitpid(child, 0)\n",
        timeout=5,
    )

    assert rc == 0, err
    assert "tasks-unbounded" not in out
    count = int(out.strip().removeprefix("tasks-bounded:"))
    assert 1 <= count < 16


def test_cgroup_memorymax_bounds_aggregate_children(review_module) -> None:
    started = time.monotonic()
    rc, out, err = review_module._confined_python(
        "import os, time\n"
        "children = []\n"
        "for _ in range(4):\n"
        "    child = os.fork()\n"
        "    if child == 0:\n"
        "        block = bytearray(70 * 1024 * 1024)\n"
        "        for index in range(0, len(block), 4096):\n"
        "            block[index] = 1\n"
        "        print('allocated', flush=True)\n"
        "        time.sleep(30)\n"
        "        os._exit(0)\n"
        "    children.append(child)\n"
        "for child in children:\n"
        "    os.waitpid(child, 0)\n",
        timeout=8,
    )

    assert rc != 0
    assert err != "timeout", f"la limite memoire agregee n'a pas arrete l'unite: {out}"
    assert time.monotonic() - started < 8


@pytest.mark.parametrize(
    ("timeout", "runtime_property"),
    [(0.2, "RuntimeMaxSec=1s"), (2.2, "RuntimeMaxSec=3s"), (30, "RuntimeMaxSec=31s")],
)
def test_systemd_run_bounds_runtime_and_stop_policy(
    review_module, timeout, runtime_property
) -> None:
    command = review_module._systemd_run_command(
        "nexus-review-test-properties", ["/usr/bin/true"], timeout=timeout
    )
    properties = {
        command[index + 1]
        for index, argument in enumerate(command[:-1])
        if argument == "--property"
    }

    assert runtime_property in properties
    assert "KillMode=control-group" in properties
    assert "SendSIGKILL=yes" in properties
    assert "TimeoutStopSec=1s" in properties


@pytest.mark.parametrize("failure_mode", ["returncode", "exception", "empty_show"])
def test_terminate_systemd_unit_reports_control_failures(
    review_module, monkeypatch, failure_mode
) -> None:
    calls = []

    def failing_systemctl(*arguments):
        calls.append(arguments)
        if failure_mode == "exception":
            raise review_module.ReviewValidationError("bus indisponible")
        if failure_mode == "returncode":
            return subprocess.CompletedProcess(arguments, 1, "", "failure")
        if arguments[0] == "show":
            return subprocess.CompletedProcess(arguments, 0, "", "")
        return subprocess.CompletedProcess(arguments, 0, "", "")

    monkeypatch.setattr(review_module, "_systemctl", failing_systemctl)
    monkeypatch.setattr(review_module.time, "sleep", lambda _duration: None)

    with pytest.raises(review_module.ReviewValidationError, match="arret.*systemd"):
        review_module._terminate_systemd_unit("nexus-review-test-failure")

    assert calls[0] == (
        "kill",
        "--kill-whom=all",
        "nexus-review-test-failure",
    )
    assert ("reset-failed", "nexus-review-test-failure") in calls


class _TimeoutThenReapProcess:
    pid = 424242
    returncode = None

    def __init__(self, *, persistent: bool) -> None:
        self.persistent = persistent
        self.communicate_calls = 0

    def communicate(self, _payload=None, *, timeout=None):
        self.communicate_calls += 1
        if self.communicate_calls == 1 or (
            self.persistent and self.communicate_calls == 2
        ):
            raise subprocess.TimeoutExpired("sandbox", timeout, output="partial")
        self.returncode = -9
        return "reaped", ""


@pytest.mark.parametrize("persistent", [False, True])
def test_run_confined_reaps_local_process_before_cleanup_error(
    review_module, monkeypatch, persistent
) -> None:
    process = _TimeoutThenReapProcess(persistent=persistent)
    signals = []
    monkeypatch.setattr(review_module, "_ensure_systemd_user_cgroup", lambda: None)
    monkeypatch.setattr(
        review_module, "_bwrap_command", lambda command, with_ruff=False: command
    )
    monkeypatch.setattr(
        review_module,
        "_systemd_run_command",
        lambda unit, command, timeout=None: command,
    )
    monkeypatch.setattr(
        review_module.subprocess, "Popen", lambda *args, **kwargs: process
    )
    monkeypatch.setattr(
        review_module,
        "_terminate_systemd_unit",
        lambda _unit: (_ for _ in ()).throw(
            review_module.ReviewValidationError("cleanup indisponible")
        ),
    )
    monkeypatch.setattr(
        review_module.os,
        "killpg",
        lambda pid, sent_signal: signals.append((pid, sent_signal)),
    )

    started = time.monotonic()
    with pytest.raises(
        review_module.ReviewValidationError, match="cleanup indisponible"
    ):
        review_module._run_confined(
            ["/usr/bin/true"], "", timeout=0.01, unit_name="nexus-review-test-reap"
        )

    assert time.monotonic() - started < 1
    assert signals[0] == (process.pid, review_module.signal.SIGTERM)
    if persistent:
        assert signals[-1] == (process.pid, review_module.signal.SIGKILL)
        assert process.communicate_calls == 3
    else:
        assert process.communicate_calls == 2


def test_run_confined_reaps_nonzero_process_before_cleanup_error(
    review_module, monkeypatch
) -> None:
    process = _TimeoutThenReapProcess(persistent=False)
    process.communicate = lambda _payload=None, timeout=None: ("", "failed")
    process.returncode = 1
    signals = []
    reaps = []
    monkeypatch.setattr(review_module, "_ensure_systemd_user_cgroup", lambda: None)
    monkeypatch.setattr(
        review_module, "_bwrap_command", lambda command, with_ruff=False: command
    )
    monkeypatch.setattr(
        review_module,
        "_systemd_run_command",
        lambda unit, command, timeout=None: command,
    )
    monkeypatch.setattr(
        review_module.subprocess, "Popen", lambda *args, **kwargs: process
    )
    monkeypatch.setattr(
        review_module,
        "_terminate_systemd_unit",
        lambda _unit: (_ for _ in ()).throw(
            review_module.ReviewValidationError("cleanup indisponible")
        ),
    )
    monkeypatch.setattr(
        review_module.os,
        "killpg",
        lambda pid, sent_signal: signals.append((pid, sent_signal)),
    )

    original_communicate = process.communicate

    def recording_communicate(_payload=None, timeout=None):
        reaps.append(timeout)
        return original_communicate(_payload, timeout=timeout)

    process.communicate = recording_communicate
    with pytest.raises(
        review_module.ReviewValidationError, match="cleanup indisponible"
    ):
        review_module._run_confined(
            ["/usr/bin/false"], "", timeout=0.1, unit_name="nexus-review-test-error"
        )

    assert signals == [(process.pid, review_module.signal.SIGTERM)]
    assert len(reaps) >= 2
    assert all(timeout is not None for timeout in reaps[1:])


def test_confined_python_timeout_collects_unit_and_children(review_module) -> None:
    unit_name = f"nexus-review-test-{uuid.uuid4().hex}"
    started = time.monotonic()
    rc, out, err = review_module._confined_python(
        "import os, time\n"
        "child = os.fork()\n"
        "if child == 0:\n"
        "    time.sleep(60)\n"
        "else:\n"
        "    print(child, flush=True)\n"
        "    time.sleep(60)\n",
        timeout=0.3,
        unit_name=unit_name,
    )

    assert rc != 0
    assert err == "timeout"
    assert time.monotonic() - started < 5
    assert out.strip().isdigit(), "le processus enfant a bien demarre avant le timeout"
    observed = subprocess.run(
        [
            str(review_module.SYSTEMCTL_PATH),
            "--user",
            "show",
            "--property=LoadState",
            "--value",
            unit_name,
        ],
        capture_output=True,
        text=True,
    )
    assert observed.returncode == 0
    assert observed.stdout.strip() == "not-found"


def test_runtime_max_collects_unit_when_cleanup_channel_is_unavailable(
    review_module, monkeypatch
) -> None:
    review_module._ensure_systemd_user_cgroup()
    unit_name = f"nexus-review-test-{uuid.uuid4().hex}"
    original_cleanup = review_module._terminate_systemd_unit
    try:
        monkeypatch.setattr(
            review_module,
            "_terminate_systemd_unit",
            lambda _unit: (_ for _ in ()).throw(
                review_module.ReviewValidationError("cleanup simule indisponible")
            ),
        )
        started = time.monotonic()
        with pytest.raises(
            review_module.ReviewValidationError, match="cleanup simule indisponible"
        ):
            review_module._confined_python(
                "import time\ntime.sleep(60)\n",
                timeout=0.2,
                unit_name=unit_name,
            )
        assert time.monotonic() - started < 2

        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            observed = subprocess.run(
                [
                    str(review_module.SYSTEMCTL_PATH),
                    "--user",
                    "show",
                    "--property=LoadState",
                    "--value",
                    unit_name,
                ],
                capture_output=True,
                text=True,
            )
            if observed.returncode == 0 and observed.stdout.strip() == "not-found":
                break
            time.sleep(0.05)
        else:
            pytest.fail(f"RuntimeMaxSec n'a pas collecte {unit_name}")
    finally:
        monkeypatch.setattr(review_module, "_terminate_systemd_unit", original_cleanup)
        original_cleanup(unit_name)


def test_missing_bwrap_is_a_hard_validation_error(
    review_module, monkeypatch, tmp_path
) -> None:
    monkeypatch.setattr(review_module, "BWRAP_PATH", tmp_path / "missing-bwrap")
    with pytest.raises(
        review_module.ReviewValidationError, match="bwrap.*indisponible"
    ):
        review_module._confined_python("print(1)\n")


def test_missing_systemd_user_cgroup_is_a_hard_validation_error(
    review_module, monkeypatch, tmp_path
) -> None:
    review_module._SYSTEMD_PREFLIGHT_CACHE.clear()
    monkeypatch.setattr(
        review_module, "SYSTEMD_RUN_PATH", tmp_path / "missing-systemd-run"
    )
    with pytest.raises(
        review_module.ReviewValidationError, match="systemd.*cgroup.*indisponible"
    ):
        review_module._confined_python("print(1)\n")


def test_check_object_uses_confined_ruff_wrapper(tmp_path, review_module) -> None:
    _install_review_support(tmp_path)
    tex = tmp_path / "listing.tex"
    tex.write_text(
        "\\begin{python}\nvalue = 1\nprint(value)\n\\end{python}\n",
        encoding="utf-8",
    )

    verifier = review_module._verify_module(tmp_path)
    result = verifier.check_object(tex, no_ruff=False)

    assert result == {
        "verdict": "verified",
        "checks": [{"type": "ruff", "index": 0, "pass": True, "detail": ""}],
    }


def test_discover_sources_normalizes_malformed_contract_type(
    tmp_path, review_module
) -> None:
    contract = tmp_path / "NSI/chapitres/1NSI-UNIT/contrat.yaml"
    contract.parent.mkdir(parents=True)
    contract.write_text("- malformed\n", encoding="utf-8")

    with pytest.raises(review_module.ReviewValidationError, match="contrat"):
        review_module.discover_sources(tmp_path)


def test_execution_observation_reruns_without_writing_receipt(
    tmp_path, review_module
) -> None:
    _install_review_support(tmp_path)
    chapter = tmp_path / "NSI" / "chapitres" / "1NSI-UNIT"
    source_path = chapter / "exercices" / "1NSI-UNIT-EX-001.tex"
    receipt_path = chapter / "validations" / "1NSI-UNIT-EX-001.execution.json"
    source_path.parent.mkdir(parents=True)
    receipt_path.parent.mkdir(parents=True)
    source_path.write_text(
        '% META: {"id":"1NSI-UNIT-EX-001","chapitre":"1NSI-UNIT",'
        '"type_objet":"exercice","status":"verified"}\n'
        "% BEGIN-TRACE\n% print(1 + 1)\n% EXPECTED\n% 2\n% END-TRACE\n",
        encoding="utf-8",
    )
    receipt = {
        "objet_id": "1NSI-UNIT-EX-001",
        "gate": "sympy",
        "verdict": "pass",
        "details": {
            "checks": [{"type": "trace", "index": 0, "pass": True, "detail": ""}]
        },
        "reviewer": "verify_python.py",
        "created_at": "2026-08-10T00:00:00+00:00",
    }
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    before = receipt_path.read_bytes()
    source = {
        "id": "1NSI-UNIT-EX-001",
        "scope": "object",
        "chapter": "1NSI-UNIT",
        "path": source_path.relative_to(tmp_path).as_posix(),
        "status": "verified",
    }

    observation = review_module.execution_observation(source, tmp_path)

    assert observation["fresh_verdict"] == "pass"
    assert observation["receipt_verdict"] == "pass"
    assert observation["matches_receipt"] is True
    assert observation["anomalies"] == []
    assert SHA256.fullmatch(observation["check_digest"])
    assert receipt_path.read_bytes() == before

    receipt["details"]["checks"][0]["pass"] = False
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    divergent = review_module.execution_observation(source, tmp_path)
    assert divergent["matches_receipt"] is False
    assert divergent["anomalies"] == ["execution_receipt_diverged"]

    receipt_path.unlink()
    missing = review_module.execution_observation(source, tmp_path)
    assert missing["matches_receipt"] is False
    assert missing["anomalies"] == ["missing_receipt"]

    source_path.write_text(
        source_path.read_text(encoding="utf-8").replace(
            "% 2\n% END-TRACE", "% 3\n% END-TRACE"
        ),
        encoding="utf-8",
    )
    failed = review_module.execution_observation(source, tmp_path)
    assert failed["fresh_verdict"] == "fail"
    assert failed["anomalies"] == ["fresh_execution_failed"]


@pytest.mark.parametrize(
    ("anomaly_code", "severity", "dimension"),
    [
        ("fresh_execution_failed", "P0", "scientific"),
        ("missing_receipt", "P1", "traceability"),
        ("execution_receipt_diverged", "P1", "traceability"),
    ],
)
def test_execution_anomaly_severity_matches_failure_class(
    sealed_review, review_module, anomaly_code, severity, dimension
) -> None:
    anomaly = review_module._execution_anomaly(
        sealed_review["sources"][0],
        {"anomalies": [anomaly_code]},
        sealed_review["root"],
    )
    assert anomaly["severity"] == severity
    assert anomaly["dimension"] == dimension


def test_generate_register_marks_receipt_divergence_as_p1_traceability(
    tmp_path, policy, review_module
) -> None:
    _install_review_support(tmp_path)
    chapter = tmp_path / "NSI" / "chapitres" / "1NSI-UNIT"
    source_path = chapter / "exercices" / "1NSI-UNIT-EX-001.tex"
    receipt_path = chapter / "validations" / "1NSI-UNIT-EX-001.execution.json"
    source_path.parent.mkdir(parents=True)
    receipt_path.parent.mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        "chapitre: 1NSI-UNIT\nstatut: draft\n", encoding="utf-8"
    )
    source_path.write_text(
        '% META: {"id":"1NSI-UNIT-EX-001","chapitre":"1NSI-UNIT",'
        '"type_objet":"exercice","status":"verified"}\n'
        "% BEGIN-TRACE\n% print(1 + 1)\n% EXPECTED\n% 2\n% END-TRACE\n",
        encoding="utf-8",
    )
    receipt_path.write_text(
        json.dumps(
            {
                "verdict": "pass",
                "details": {
                    "checks": [
                        {"type": "trace", "index": 0, "pass": False, "detail": "old"}
                    ]
                },
            }
        ),
        encoding="utf-8",
    )
    source = {
        "id": "1NSI-UNIT-EX-001",
        "scope": "object",
        "chapter": "1NSI-UNIT",
        "path": source_path.relative_to(tmp_path).as_posix(),
        "status": "verified",
        "type": "exercice",
        "capacity_refs": [],
        "metadata": {},
        "source_sha256": _sha(source_path),
    }
    review_receipt = tmp_path / "audit/reviews/1nsi/runs/2026-08-10-contracts.yaml"
    review_receipt.parent.mkdir(parents=True)
    review_receipt.write_text(
        yaml.safe_dump(
            _review_run_receipt(
                review_module,
                policy,
                [source],
                tmp_path,
                review_run_id="unit-run",
                reviewer_id="independent-reviewer",
                reviewer_model="unit-model",
            ),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "Nexus Tests")
    _git(tmp_path, "config", "user.email", "nexus-tests@example.invalid")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "seal execution review")
    before = receipt_path.read_bytes()
    fact = {
        "path": source["path"],
        "line_start": 1,
        "line_end": 1,
        "excerpt_sha256": _excerpt_digest(source_path),
        "fact_type": "source_statement",
        "observation": "Observation de fixture propre a l'objet unitaire.",
    }
    finding = {
        "id": source["id"],
        "scope": source["scope"],
        "chapter": source["chapter"],
        "source_path": source["path"],
        "source_status": source["status"],
        "capacity_refs": [],
        "provenance": {
            "reviewer_id": "independent-reviewer",
            "review_run_id": "unit-run",
            "reviewer_model": "unit-model",
            "integrator_id": "integrator",
            "review_receipt_path": review_receipt.relative_to(tmp_path).as_posix(),
            "review_receipt_sha256": _sha(review_receipt),
            "sealing_commit_sha": _git(tmp_path, "rev-parse", "HEAD"),
        },
        "dimensions": {
            "scientific": {
                "verdict": "pass",
                "justification": "Fixture scientifique initialement sans anomalie.",
                "facts": [copy.deepcopy(fact)],
                "anomaly_ids": [],
            },
            "pedagogical": {
                "verdict": "pass",
                "justification": "Fixture pedagogique initialement sans anomalie.",
                "facts": [{**fact, "observation": "Observation pedagogique unitaire."}],
                "anomaly_ids": [],
            },
        },
        "anomalies": [],
    }
    sealed_run = yaml.safe_load(review_receipt.read_text(encoding="utf-8"))
    sealed_run["reviews"][0]["payload"] = {
        "dimensions": copy.deepcopy(finding["dimensions"]),
        "anomalies": copy.deepcopy(finding["anomalies"]),
    }
    review_receipt.write_text(
        yaml.safe_dump(sealed_run, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    _git(tmp_path, "add", review_receipt.relative_to(tmp_path).as_posix())
    _git(tmp_path, "commit", "-q", "-m", "reseal execution review payload")
    finding["provenance"]["review_receipt_sha256"] = _sha(review_receipt)
    finding["provenance"]["sealing_commit_sha"] = _git(tmp_path, "rev-parse", "HEAD")

    document = review_module.generate_register(
        [finding], tmp_path, policy, sources=[source], require_complete=True
    )

    entry = document["entries"][0]
    assert entry["dimensions"]["scientific"]["verdict"] == "pass"
    assert entry["dimensions"]["scientific"]["anomaly_ids"] == []
    assert entry["anomalies"][0]["severity"] == "P1"
    assert entry["anomalies"][0]["dimension"] == "traceability"
    assert entry["execution_observation"]["matches_receipt"] is False
    assert receipt_path.read_bytes() == before


def test_summary_counts_and_details_anomalies_by_severity_and_dimension(
    review_module,
) -> None:
    document = {
        "protocol_digest": "sha256:" + "1" * 64,
        "entries": [
            {
                "id": "1NSI-SUMMARY-001",
                "dimensions": {
                    "scientific": {"verdict": "issue"},
                    "pedagogical": {"verdict": "pass"},
                },
                "anomalies": [
                    {
                        "id": "1NSI-REV-SCIENCE",
                        "severity": "P0",
                        "dimension": "scientific",
                        "expected_action": "Corriger le resultat calcule.",
                    },
                    {
                        "id": "1NSI-REV-TRACE",
                        "severity": "P1",
                        "dimension": "traceability",
                        "expected_action": "Regenerer le recu concordant.",
                    },
                ],
            },
            {
                "id": "1NSI-SUMMARY-002",
                "dimensions": {
                    "scientific": {"verdict": "pass"},
                    "pedagogical": {"verdict": "issue"},
                },
                "anomalies": [
                    {
                        "id": "1NSI-REV-PEDAGOGIE",
                        "severity": "P2",
                        "dimension": "pedagogical",
                        "expected_action": "Clarifier la consigne eleve.",
                    }
                ],
            },
        ],
    }

    summary = review_module.render_summary(document)

    assert "## Anomalies" in summary
    assert "- P0: 1" in summary
    assert "- P1: 1" in summary
    assert "- P2: 1" in summary
    assert "- scientific: 1" in summary
    assert "- pedagogical: 1" in summary
    assert "- traceability: 1" in summary
    assert "1NSI-REV-TRACE" in summary
    assert "Regenerer le recu concordant." in summary
    assert "approved" not in summary.casefold()


def test_cli_exposes_required_modes(policy, review_module, monkeypatch) -> None:
    result = subprocess.run(
        [sys.executable, str(MODULE_PATH), "--help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    for flag in (
        "--findings",
        "--output-json",
        "--output-summary",
        "--check",
        "--verify-scope",
        "--release-gate",
    ):
        assert flag in result.stdout
    assert review_module.main(["--verify-scope"]) == 0
    calls = []
    monkeypatch.setattr(
        review_module, "verify_scope", lambda root, loaded: calls.append(root)
    )
    assert review_module.main(["--release-gate"]) != 0
    assert calls == [ROOT]


def test_contract_findings_are_exactly_the_ten_sealed_contract_reviews(
    policy, sources, review_module
) -> None:
    assert FINDINGS_PATH.is_file(), "les findings des contrats doivent etre crees"
    receipt_relative = CONTRACT_RECEIPT_PATH.relative_to(ROOT).as_posix()
    receipt_digest = CURRENT_RECEIPT_SEALS[receipt_relative]
    config = GOVERNANCE_REVIEW_CONFIG[receipt_relative]
    document = yaml.safe_load(FINDINGS_PATH.read_text(encoding="utf-8"))
    assert {
        key: document[key]
        for key in (
            "artifact_type",
            "schema_version",
            "manual",
            "review_run_id",
            "review_receipt_path",
            "review_receipt_sha256",
            "sealing_commit_sha",
        )
    } == {
        "artifact_type": "1nsi_content_review_findings",
        "schema_version": 1,
        "manual": "1NSI",
        "review_run_id": config["review_run_id"],
        "review_receipt_path": receipt_relative,
        "review_receipt_sha256": receipt_digest,
        "sealing_commit_sha": RECEIPTS_COMMIT,
    }

    findings = [
        finding
        for finding in review_module.load_findings(FINDINGS_PATH)
        if finding["scope"] == "contract"
    ]
    contracts = [source for source in sources if source["scope"] == "contract"]
    assert len(findings) == len(contracts) == 10
    assert {finding["id"] for finding in findings} == {
        source["id"] for source in contracts
    }
    assert all(finding["scope"] == "contract" for finding in findings)
    assert "TNSI" not in json.dumps(findings, ensure_ascii=False)

    validated = review_module.validate_findings(
        findings, sources, ROOT, policy, require_complete=False
    )
    receipt = yaml.safe_load(CONTRACT_RECEIPT_PATH.read_text(encoding="utf-8"))
    reviews_by_id = {review["id"]: review for review in receipt["reviews"]}
    sources_by_id = {source["id"]: source for source in contracts}
    expected_provenance = {
        "reviewer_id": config["reviewer_id"],
        "review_run_id": config["review_run_id"],
        "reviewer_model": GOVERNANCE_REVIEWER_MODEL,
        "integrator_id": policy["integrator_id"],
        "review_receipt_path": receipt_relative,
        "review_receipt_sha256": receipt_digest,
        "sealing_commit_sha": RECEIPTS_COMMIT,
    }
    for finding in validated:
        source = sources_by_id[finding["id"]]
        assert finding["chapter"] == source["chapter"]
        assert finding["source_path"] == source["path"]
        assert finding["source_status"] == source["status"] == "draft"
        assert finding["capacity_refs"] == source["capacity_refs"]
        assert finding["provenance"] == expected_provenance
        assert {
            "dimensions": finding["dimensions"],
            "anomalies": finding["anomalies"],
        } == reviews_by_id[finding["id"]]["payload"]

    scientific = Counter(
        finding["dimensions"]["scientific"]["verdict"] for finding in validated
    )
    pedagogical = Counter(
        finding["dimensions"]["pedagogical"]["verdict"] for finding in validated
    )
    anomalies = [anomaly for finding in validated for anomaly in finding["anomalies"]]
    assert scientific == Counter({"issue": 7, "pass": 3})
    assert pedagogical == Counter({"pass": 6, "issue": 4})
    assert len(anomalies) == len({anomaly["id"] for anomaly in anomalies}) == 20
    assert {
        "1NSI-REV-PM-C3-SOURCE",
        "1NSI-REV-TABLES-R2-ORIGINE",
        "1NSI-REV-TC-PUPLETS-NOMMES",
        "1NSI-REV-TC-ITERATION-TABLEAU",
    } <= {anomaly["id"] for anomaly in anomalies}
    assert Counter(anomaly["severity"] for anomaly in anomalies) == Counter(
        {"P0": 3, "P1": 14, "P2": 3}
    )


def test_historical_contract_receipt_remains_git_sealed(
    sources, review_module
) -> None:
    receipt_relative = CONTRACT_RECEIPT_PATH.relative_to(ROOT).as_posix()
    sealed_bytes = _git_bytes(
        ROOT, "show", f"{CONTRACT_RECEIPT_COMMIT}:{receipt_relative}"
    )
    assert review_module.sha256_bytes(sealed_bytes) == CONTRACT_RECEIPT_SHA256

    receipt = yaml.safe_load(sealed_bytes.decode("utf-8"))
    errors = list(
        Draft202012Validator(
            review_module._receipt_schema(ROOT),
            format_checker=review_module.FORMAT_CHECKER,
        ).iter_errors(receipt)
    )
    assert not errors
    contracts = [source for source in sources if source["scope"] == "contract"]
    assert receipt["protocol_digest"] == PRE_BUILD_MANIFEST_PROTOCOL_DIGEST
    assert {
        "reviewer_id": receipt["reviewer_id"],
        "review_run_id": receipt["review_run_id"],
        "reviewer_model": receipt["reviewer_model"],
    } == {
        "reviewer_id": "019feb3f-cd89-7242-9a84-6fafbc77e0d8",
        "review_run_id": "1nsi-contracts-2026-08-10-plato-reattestation-v2",
        "reviewer_model": "codex-inherited-gpt5",
    }
    assert receipt["assignment"] == {
        "scope": "contract",
        "chapters": [source["chapter"] for source in contracts],
        "source_ids": [source["id"] for source in contracts],
    }
    assert [review["id"] for review in receipt["reviews"]] == [
        source["id"] for source in contracts
    ]


def test_algorithm_review_receipt_matches_current_sources_before_sealing(
    policy, sources, review_module
) -> None:
    receipt = yaml.safe_load(ALGORITHM_RECEIPT_PATH.read_text(encoding="utf-8"))
    schema_errors = sorted(
        Draft202012Validator(
            review_module._receipt_schema(ROOT),
            format_checker=review_module.FORMAT_CHECKER,
        ).iter_errors(receipt),
        key=lambda error: tuple(str(part) for part in error.path),
    )
    assert not schema_errors, schema_errors

    algorithm_chapters = {
        "1NSI-ALGO-DICHO-GLOUTON-KNN",
        "1NSI-ALGO-PARCOURS-TRIS",
    }
    algorithm_sources = sorted(
        (
            source
            for source in sources
            if source["scope"] == "object"
            and source["chapter"] in algorithm_chapters
        ),
        key=lambda source: source["id"],
    )
    assert len(algorithm_sources) == 40
    expected_ids = [source["id"] for source in algorithm_sources]
    expected_assignment = {
        "scope": "object",
        "chapters": sorted(algorithm_chapters),
        "source_ids": expected_ids,
    }
    expected_manifest = [
        {
            "id": source["id"],
            "path": source["path"],
            "source_sha256": _sha(ROOT / source["path"]),
            "dependency_digest": review_module.compute_dependency_digest(
                source, sources, ROOT, policy
            ),
        }
        for source in algorithm_sources
    ]
    expected_reviews = [
        {
            "id": source["id"],
            "chapter": source["chapter"],
            "scope": source["scope"],
        }
        for source in algorithm_sources
    ]

    mismatches = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            mismatches.append(message)

    config = GOVERNANCE_REVIEW_CONFIG[
        ALGORITHM_RECEIPT_PATH.relative_to(ROOT).as_posix()
    ]

    require(
        receipt["protocol_digest"] == policy["protocol_digest"],
        "protocol_digest different de la policy courante",
    )
    require(
        receipt["reviewer_id"] == config["reviewer_id"],
        f"reviewer_id attendu: {config['reviewer_id']}",
    )
    require(
        receipt["reviewer_id"] not in PRE_GOVERNANCE_REVIEWER_IDS,
        "le reviewer doit etre nouveau parmi les revues de gouvernance precedentes",
    )
    require(
        receipt["reviewer_id"] != policy["integrator_id"],
        "le reviewer doit etre distinct de l'integrateur",
    )
    require(
        receipt["review_run_id"] == config["review_run_id"],
        f"review_run_id attendu: {config['review_run_id']}",
    )
    require(
        receipt["review_run_id"] not in PRE_GOVERNANCE_REVIEW_RUN_IDS,
        "le review_run_id de gouvernance doit etre nouveau",
    )
    require(
        receipt["reviewer_model"] == GOVERNANCE_REVIEWER_MODEL,
        f"reviewer_model attendu: {GOVERNANCE_REVIEWER_MODEL}",
    )
    require(
        receipt["assignment"] == expected_assignment,
        "affectation algorithmique incomplete ou non ordonnee",
    )

    manifest = receipt["source_manifest"]
    require(
        manifest["review_tool_sha256"] == _sha(MODULE_PATH),
        "hash de l'outil de revue obsolete",
    )
    require(
        manifest["execution_checker_sha256"]
        == _sha(ROOT / "NSI" / "scripts" / "verify_python.py"),
        "hash du verificateur d'execution obsolete",
    )
    require(
        manifest["execution_common_sha256"]
        == _sha(ROOT / "NSI" / "scripts" / "common.py"),
        "hash du support d'execution obsolete",
    )
    require(
        manifest["entries"] == expected_manifest,
        "manifeste des sources ou dependances algorithmiques obsolete",
    )

    observed_reviews = [
        {
            "id": review["id"],
            "chapter": review["chapter"],
            "scope": review["scope"],
        }
        for review in receipt["reviews"]
    ]
    require(
        observed_reviews == expected_reviews,
        "reviews algorithmiques incompletes ou non ordonnees",
    )
    require(
        "TNSI" not in json.dumps(receipt, ensure_ascii=False),
        "le recu algorithmique contient une reference TNSI",
    )

    sources_by_id = {source["id"]: source for source in algorithm_sources}
    seen_observations: dict[tuple[str, str], str] = {}
    for review in receipt["reviews"]:
        source = sources_by_id.get(review["id"])
        if source is None:
            continue
        payload = review["payload"]
        anomalies = payload["anomalies"]
        anomaly_ids = [anomaly["id"] for anomaly in anomalies]
        require(
            len(anomaly_ids) == len(set(anomaly_ids)),
            f"anomalies dupliquees pour {source['id']}",
        )
        allowed_paths = review_module._allowed_fact_paths(
            source, sources, ROOT, policy
        )
        payload_facts = []
        for dimension_name, dimension in payload["dimensions"].items():
            expected_anomaly_ids = [
                anomaly["id"]
                for anomaly in anomalies
                if anomaly["dimension"] == dimension_name
            ]
            require(
                dimension["anomaly_ids"] == expected_anomaly_ids,
                f"liens d'anomalies incoherents pour {source['id']}:{dimension_name}",
            )
            require(
                (dimension["verdict"] == "issue") == bool(expected_anomaly_ids),
                f"verdict incoherent pour {source['id']}:{dimension_name}",
            )
            for fact in dimension["facts"]:
                payload_facts.append(fact)
                try:
                    review_module._validate_fact(fact, allowed_paths, ROOT)
                except review_module.ReviewValidationError as error:
                    mismatches.append(f"preuve invalide pour {source['id']}: {error}")
                normalised = review_module._normalise_observation(
                    fact["observation"]
                )
                key = (source["chapter"], normalised)
                if normalised and key in seen_observations:
                    mismatches.append(
                        "observation normalisee dupliquee: "
                        f"{seen_observations[key]} / {source['id']}"
                    )
                seen_observations[key] = source["id"]
        for anomaly in anomalies:
            require(
                anomaly["dimension"] in payload["dimensions"],
                f"dimension d'anomalie sans verdict pour {source['id']}",
            )
            payload_facts.append(anomaly["fact"])
            try:
                review_module._validate_fact(anomaly["fact"], allowed_paths, ROOT)
            except review_module.ReviewValidationError as error:
                mismatches.append(
                    f"preuve d'anomalie invalide pour {source['id']}: {error}"
                )

        observation = review_module.execution_observation(source, ROOT)
        if observation is None:
            continue
        require(
            observation["fresh_verdict"] == "pass",
            f"execution fraiche en echec pour {source['id']}",
        )
        require(
            observation["matches_receipt"] is True,
            f"recu d'execution divergent pour {source['id']}",
        )
        require(
            observation["anomalies"] == [],
            f"anomalie d'execution pour {source['id']}: "
            f"{observation['anomalies']}",
        )
        require(
            any(
                fact["fact_type"] == "computed_result"
                and observation["check_digest"] in fact["observation"]
                for fact in payload_facts
            ),
            f"preuve computed_result fraiche absente pour {source['id']}",
        )

    assert not mismatches, "\n" + "\n".join(mismatches)


def test_algorithm_review_resolved_anomalies_are_absent_from_canonical_outputs(
    policy, review_module
) -> None:
    resolved_ids = SIX_RESOLVED_P0_IDS | {
        "1NSI-REV-ADGK-C2-DOCSTRING-OPTIMALITE",
        "1NSI-REV-AGT-C2-BORNE-TERMINAISON",
        "1NSI-REV-AGT-QCM-Q2-AMBIGU",
        "1NSI-REV-ADGK-C2-CONTRADICTION",
        "1NSI-REV-AGT-C3-CAS-LIMITE-TERMINAISON",
    }
    json_path = ROOT / "audit" / "1NSI_CONTENT_REVIEWS.json"
    summary_path = ROOT / "audit" / "1NSI_CONTENT_REVIEW_SUMMARY.md"

    findings_text = FINDINGS_PATH.read_text(encoding="utf-8")
    json_text = json_path.read_text(encoding="utf-8")
    summary_text = summary_path.read_text(encoding="utf-8")
    for anomaly_id in resolved_ids:
        assert anomaly_id not in findings_text
        assert anomaly_id not in json_text
        assert anomaly_id not in summary_text

    findings = review_module.load_findings(FINDINGS_PATH)
    document = json.loads(json_text)
    register_anomalies = [
        anomaly for entry in document["entries"] for anomaly in entry["anomalies"]
    ]
    assert len(register_anomalies) == 279
    assert Counter(anomaly["severity"] for anomaly in register_anomalies) == Counter(
        {"P0": 140, "P1": 132, "P2": 7}
    )

    assert len(findings) == len(document["entries"]) == 349
    assert "Entries: 349" in summary_text
    assert "- Total: 279" in summary_text
    assert "- P0: 140" in summary_text
    assert "- P1: 132" in summary_text
    assert "- P2: 7" in summary_text
    assert review_module.release_gate_allows(document, policy) is False


def test_historical_algorithm_c3_receipt_remains_git_sealed(review_module) -> None:
    receipt_relative = ALGORITHM_RECEIPT_PATH.relative_to(ROOT).as_posix()
    sealed_bytes = _git_bytes(
        ROOT, "show", f"{ALGORITHM_RECEIPT_COMMIT}:{receipt_relative}"
    )
    assert review_module.sha256_bytes(sealed_bytes) == ALGORITHM_RECEIPT_SHA256
    receipt_parents = _git(
        ROOT, "rev-list", "--parents", "-n", "1", ALGORITHM_RECEIPT_COMMIT
    ).split()
    assert receipt_parents == [
        ALGORITHM_RECEIPT_COMMIT,
        ALGORITHM_SOURCE_COMMIT,
    ]

    receipt = yaml.safe_load(sealed_bytes.decode("utf-8"))
    assert {
        "reviewer_id": receipt["reviewer_id"],
        "review_run_id": receipt["review_run_id"],
        "reviewer_model": receipt["reviewer_model"],
    } == {
        "reviewer_id": C3_REVIEWER_ID,
        "review_run_id": ALGORITHM_REVIEW_RUN_ID,
        "reviewer_model": ALGORITHM_REVIEWER_MODEL,
    }
    reviews_by_id = {review["id"]: review for review in receipt["reviews"]}
    assert len(reviews_by_id) == 40


def test_object_findings_exhaustively_cover_all_339_sources(
    policy, sources, review_module
) -> None:
    findings = review_module.load_findings(FINDINGS_PATH)
    object_sources = [source for source in sources if source["scope"] == "object"]
    object_findings = [finding for finding in findings if finding["scope"] == "object"]

    assert len(object_sources) == 339
    assert len(object_findings) == 339
    assert {finding["id"] for finding in object_findings} == {
        source["id"] for source in object_sources
    }
    assert Counter(finding["chapter"] for finding in object_findings) == Counter(
        source["chapter"] for source in object_sources
    )
    assert {
        finding["provenance"]["review_receipt_path"] for finding in object_findings
    } == OBJECT_REVIEW_RUNS
    assert (
        len({finding["provenance"]["review_run_id"] for finding in object_findings})
        == len(OBJECT_REVIEW_RUNS)
        == 5
    )
    assert len(
        {finding["provenance"]["reviewer_id"] for finding in object_findings}
    ) == len(OBJECT_REVIEW_RUNS)
    assert all(
        finding["provenance"]["reviewer_id"] != policy["integrator_id"]
        for finding in object_findings
    )
    assert "TNSI" not in json.dumps(object_findings, ensure_ascii=False)

    sources_by_id = {source["id"]: source for source in object_sources}
    for finding in object_findings:
        source = sources_by_id[finding["id"]]
        assert finding["source_path"] == source["path"]
        assert finding["source_status"] == source["status"]
        assert set(finding["dimensions"]) == {"scientific", "pedagogical"}

    validated = review_module.validate_findings(
        findings, sources, ROOT, policy, require_complete=True
    )
    assert len(validated) == 349
