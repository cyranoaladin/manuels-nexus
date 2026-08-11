#!/usr/bin/env python3
"""System B: propose substance verdicts, then lets System A veto them.

Doctrine: pertinence lexicale + jugement LLM. This script proposes
`needs_content` or `needs_review`; it never emits `validated_pedagogy`.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import re
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.check_substance_anchors import citation_status, parse_sections  # noqa: E402
from scripts.rag_core import resolve_env_file  # noqa: E402

ROOT = _REPO_ROOT
ENV_FILE = resolve_env_file(ROOT)

# Collections whose hits count as internal substance proof.
# source_type on each hit must also be "nsi_corpus" (KIND).
INTERNAL_COVERAGE_COLLECTIONS = {"nsi_corpus", "nsi_corpus_v2"}


def is_internal_collection(name: str) -> bool:
    """Barrier A predicate: collection must be in the internal allowlist."""
    return name in INTERNAL_COVERAGE_COLLECTIONS


def is_internal_hit(hit: dict[str, Any]) -> bool:
    """Barrier B predicate: hit must have source_type == 'nsi_corpus' (KIND).

    Fail-closed: any non-validable form (non-dict hit, non-dict metadata,
    missing source_type) returns False without raising.
    """
    if not isinstance(hit, dict):
        return False
    metadata = hit.get("metadata")
    if not isinstance(metadata, dict):
        return False
    return str(metadata.get("source_type", "")) == "nsi_corpus"


PROGRAMME = ROOT / "00_programmes_officiels" / "programme_nsi_2019.yaml"
OUTPUT_DIR = ROOT / "01_build_reports"
MAX_CANDIDATES_PER_ROLE = 1

ROLE_SPECS = {
    "proof_course": {
        "result_key": "proof_course",
        "label": "enseigne",
        "doc_types": ["cours", "fiche_cours", "cours_eleve", "trace"],
    },
    "proof_practice": {
        "result_key": "proof_practice",
        "label": "fait pratiquer",
        "doc_types": ["td", "tp", "starter_code", "code"],
    },
    "proof_correction": {
        "result_key": "proof_correction",
        "label": "permet de se corriger",
        "doc_types": ["corrige", "corrige_code", "tests_code", "evaluation"],
    },
}

BOILERPLATE_PATTERNS = [
    "objectif o1",
    "identifier précisément la représentation",
    "identifier précisément la structure",
]

JUDGE_SYSTEM_PROMPT = """Juge pédagogique NSI. Tu reçois une capacité officielle et un extrait de cours.
Décide si l'extrait enseigne cette capacité. Réponds UNIQUEMENT en JSON sans markdown :
{"taught": true ou false, "citation": "copie EXACTE d'une phrase de l'extrait", "justification": "1 phrase"}
IMPORTANT : la citation doit être copiée mot pour mot de l'extrait, pas inventée."""


Evidence = dict[str, Any]


def load_env(path: Path | str) -> dict[str, str]:
    env_path = Path(path)
    env: dict[str, str] = {}
    if not env_path.exists():
        print(f"ERREUR: {env_path} introuvable", file=sys.stderr)
        raise SystemExit(1)
    for line in env_path.read_text(encoding="utf-8").splitlines():
        item = line.strip()
        if not item or item.startswith("#") or "=" not in item:
            continue
        key, _, value = item.partition("=")
        env[key.strip()] = value.strip()
    return env


def load_programme() -> list[dict[str, str]]:
    try:
        import yaml
    except ImportError:
        print("ERREUR: pip install pyyaml", file=sys.stderr)
        raise SystemExit(1)
    with PROGRAMME.open(encoding="utf-8") as handle:
        programme = yaml.safe_load(handle)
    capacities: list[dict[str, str]] = []
    for level in ("premiere", "terminale"):
        for capacity in programme["programmes"].get(level, []):
            capacities.append(
                {
                    "id": str(capacity["id"]),
                    "intitule": str(capacity.get("capacite_attendue", [""])[0]),
                    "rubrique": str(capacity.get("rubrique", "")),
                    "contenu": str(capacity.get("contenu", "")),
                    "niveau": str(capacity["niveau"]),
                }
            )
    return capacities


def load_contract_capacity_ids(repo_root: Path, unit: str) -> list[str]:
    try:
        import yaml
    except ImportError:
        return []
    path = repo_root / "03_progressions" / "supports" / "contracts" / f"{unit}_contract.yml"
    if not path.exists():
        return []
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = payload.get("capacites_officielles", []) if isinstance(payload, dict) else []
    return [str(row).strip() for row in rows if str(row).strip()]


def _http_json(
    url: str,
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    request_headers = {"Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)
    data = json.dumps(body).encode("utf-8") if body else None
    request = urllib.request.Request(url, data=data, headers=request_headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read())
    return payload if isinstance(payload, dict) else {}


def search_rag(
    env: dict[str, str],
    query: str,
    k: int = 5,
    doc_type_filter: list[str] | None = None,
) -> list[dict[str, Any]]:
    hits = _http_json(
        env["RAG_API_BASE_URL"],
        body={"q": query, "collection": env.get("RAG_COLLECTION", "nsi_corpus"), "k": k, "include_documents": True},
        headers={"Authorization": f"Bearer {env['RAG_API_KEY']}"},
    ).get("hits", [])
    if not isinstance(hits, list):
        return []
    # Barrier B first: reject non-internal hits (guards metadata access)
    hits = [hit for hit in hits if is_internal_hit(hit)]
    # Now metadata is guaranteed dict on all remaining hits
    if doc_type_filter:
        hits = [
            hit for hit in hits
            if hit.get("metadata", {}).get("document_type", "") in doc_type_filter
        ]
    return hits


def call_llm(env: dict[str, str], capacity_text: str, section_text: str, role_label: str) -> dict[str, Any]:
    llm_url = env.get("LOCAL_LLM_BASE_URL", "")
    llm_model = env.get("LOCAL_LLM_MODEL", "qwen2.5:7b")
    if not llm_url:
        return {"taught": False, "citation": "", "justification": "LLM non configurée"}

    user_prompt = (
        f"Capacité NSI : \"{capacity_text}\"\n"
        f"Rôle : {role_label}\n\n"
        f"Extrait :\n---\n{section_text[:800]}\n---\n\n"
        f"Cette section {role_label}-t-elle cette capacité ?"
    )
    for attempt in range(2):
        try:
            data = _http_json(
                f"{llm_url}/chat/completions",
                body={
                    "model": llm_model,
                    "messages": [
                        {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0,
                },
                timeout=90,
            )
            content = data["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = re.sub(r"^```\w*\n?", "", content)
                content = re.sub(r"\n?```$", "", content)
            result = json.loads(content)
            if isinstance(result, dict) and "taught" in result:
                return result
        except (json.JSONDecodeError, KeyError):
            if attempt == 0:
                time.sleep(1)
                continue
        except Exception as exc:
            return {"taught": False, "citation": "", "justification": f"Erreur LLM: {exc}"}
    return {"taught": False, "citation": "", "justification": "JSON invalide"}


def empty_evidence(note: str = "Aucune preuve vérifiable retenue.") -> Evidence:
    return {
        "present": False,
        "file": None,
        "anchor": None,
        "quote": None,
        "teaches": False,
        "note": note,
    }


def is_boilerplate(text: str) -> bool:
    lower = text.lower()
    return any(pattern in lower for pattern in BOILERPLATE_PATTERNS)


def veto_deterministe(verdict: dict[str, Any], intitule: str, used_citations: set[str]) -> dict[str, Any]:
    """Mechanical veto: degrade only. Doctrine: pertinence lexicale + jugement LLM."""
    citation = str(verdict.get("citation", ""))
    if is_boilerplate(citation):
        verdict["taught"] = False
        verdict["veto"] = "boilerplate_detected"
        verdict["justification"] = "Citation rejetée : objectif templaté."
        return verdict

    if citation and len(citation) > 10:
        citation_words = set(re.findall(r"\w{4,}", citation.lower()))
        label_words = set(re.findall(r"\w{4,}", intitule.lower()))
        if label_words and not (citation_words & label_words):
            verdict["taught"] = False
            verdict["veto"] = "no_lexical_overlap"
            verdict["justification"] = "Citation sans mot commun avec l'intitulé."
            return verdict

    if citation:
        citation_hash = json.dumps(citation, ensure_ascii=False)
        if citation_hash in used_citations:
            verdict["taught"] = False
            verdict["veto"] = "citation_reused"
            verdict["justification"] = "Citation déjà utilisée."
            return verdict
        used_citations.add(citation_hash)

    verdict["veto"] = "passed"
    return verdict


def section_body(repo_root: Path, file_rel: str, anchor: str) -> str | None:
    source_path = repo_root / file_rel
    if not source_path.exists():
        return None
    sections = parse_sections(source_path.read_text(encoding="utf-8", errors="replace"))
    section = sections.get(anchor.lstrip("#"))
    return section.body if section else None


def quote_is_verified(repo_root: Path, file_rel: str, anchor: str, quote: str) -> bool:
    body = section_body(repo_root, file_rel, anchor)
    if body is None:
        return False
    status, _ = citation_status(quote, body)
    return status in {"exact", "normalized"}


def accepted_evidence(
    repo_root: Path,
    hit: dict[str, Any],
    llm_result: dict[str, Any],
) -> Evidence | None:
    metadata = hit.get("metadata", {})
    if not isinstance(metadata, dict):
        return None
    file_rel = str(metadata.get("path", ""))
    anchor = str(metadata.get("section_anchor") or metadata.get("anchor", ""))
    quote = str(llm_result.get("citation", ""))
    if not file_rel or not anchor or not quote:
        return None
    if not quote_is_verified(repo_root, file_rel, anchor, quote):
        return None
    return {
        "present": True,
        "file": file_rel,
        "anchor": anchor,
        "quote": quote,
        "teaches": bool(llm_result.get("taught")),
        "note": str(llm_result.get("justification", "Preuve proposée par System B."))[:400],
    }


def document_text_for_hit(repo_root: Path, hit: dict[str, Any]) -> str:
    metadata = hit.get("metadata", {})
    if isinstance(metadata, dict):
        file_rel = str(metadata.get("path", ""))
        anchor = str(metadata.get("section_anchor") or metadata.get("anchor", ""))
        if file_rel and anchor:
            body = section_body(repo_root, file_rel, anchor)
            if body:
                return body
    document = hit.get("document", "")
    return str(document)


def judge_role(
    env: dict[str, str],
    cap: dict[str, str],
    role_spec: dict[str, Any],
    repo_root: Path,
    used_citations: set[str],
) -> Evidence:
    intitule = cap["intitule"]
    query = f"{cap.get('contenu', '')} {intitule}"
    hits = search_rag(env, query, k=5, doc_type_filter=list(role_spec["doc_types"]))
    if not hits:
        hits = search_rag(env, query, k=5)
    seen_files: set[str] = set()
    for hit in hits:
        metadata = hit.get("metadata", {})
        if not isinstance(metadata, dict):
            continue
        file_rel = str(metadata.get("path", ""))
        if not file_rel or file_rel in seen_files:
            continue
        seen_files.add(file_rel)
        text = document_text_for_hit(repo_root, hit)
        if len(text.strip()) < 12:
            continue
        llm_result = call_llm(env, intitule, text, str(role_spec["label"]))
        checked = veto_deterministe(
            llm_result,
            f"{intitule} {cap.get('contenu', '')} {cap.get('rubrique', '')}",
            used_citations,
        )
        if not checked.get("taught"):
            continue
        evidence = accepted_evidence(repo_root, hit, checked)
        if evidence is not None:
            return evidence
    return empty_evidence()


def judge_capacity(
    env: dict[str, str],
    cap: dict[str, str],
    *,
    repo_root: Path = ROOT,
    used_citations: set[str] | None = None,
) -> dict[str, Any]:
    citation_set = used_citations if used_citations is not None else set()
    proofs = {
        key: judge_role(env, cap, spec, repo_root, citation_set)
        for key, spec in ROLE_SPECS.items()
    }
    present_count = sum(1 for evidence in proofs.values() if evidence.get("present"))
    verdict = "needs_review" if present_count else "needs_content"
    return {
        "capacity_id": cap["id"],
        "official_label": cap["intitule"],
        "proof_course": proofs["proof_course"],
        "proof_practice": proofs["proof_practice"],
        "proof_correction": proofs["proof_correction"],
        "verdict": verdict,
        "justification": (
            "Proposition System B : preuves mécaniquement vérifiées, relecture humaine requise."
            if present_count
            else "Proposition System B : aucune preuve vérifiable suffisante."
        ),
        "scientific_flags": ["human_review_required"],
    }


def build_review(
    env: dict[str, str],
    capacities: list[dict[str, str]],
    *,
    unit: str,
    level: str,
    repo_root: Path,
    judge_model: str,
    author_model: str = "codex-authoring-agent",
) -> dict[str, Any]:
    used_citations: set[str] = set()
    return {
        "schema_version": "1.0.0",
        "unit": unit,
        "level": level,
        "judged_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "judge_model": judge_model,
        "author_model": author_model,
        "capacities": [
            judge_capacity(env, capacity, repo_root=repo_root, used_citations=used_citations)
            for capacity in capacities
        ],
    }


def coerce_non_promoting(review: dict[str, Any]) -> dict[str, Any]:
    for capacity in review.get("capacities", []):
        if isinstance(capacity, dict) and capacity.get("verdict") == "validated_pedagogy":
            capacity["verdict"] = "needs_review"
            flags = capacity.setdefault("scientific_flags", [])
            if isinstance(flags, list) and "human_review_required" not in flags:
                flags.append("human_review_required")
    return review


def run_from_offline_fixture(fixture_path: Path, output_path: Path) -> Path:
    review = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(review, dict):
        raise ValueError("offline fixture must contain a JSON object")
    review = coerce_non_promoting(review)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"verdict écrit : {output_path}")
    return output_path


def filter_capacities(
    capacities: list[dict[str, str]],
    *,
    cap_id: str = "",
    contract_ids: list[str] | None = None,
    limit: int = 0,
) -> list[dict[str, str]]:
    selected = capacities
    if contract_ids:
        wanted = set(contract_ids)
        selected = [capacity for capacity in selected if capacity["id"] in wanted]
    if cap_id:
        selected = [capacity for capacity in selected if capacity["id"] == cap_id]
    if limit > 0:
        selected = selected[:limit]
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description="System B substance proposal writer")
    parser.add_argument("--unit", default="corpus")
    parser.add_argument("--level", choices=["premiere", "terminale"], default="premiere")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--cap-id", default="")
    parser.add_argument("--output", "--out", type=Path, default=None)
    parser.add_argument("--offline-fixture", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    output = args.output or OUTPUT_DIR / f"{args.unit}_substance_review.json"
    if args.offline_fixture is not None:
        run_from_offline_fixture(args.offline_fixture, output)
        return 0

    capacities = load_programme()
    contract_ids = load_contract_capacity_ids(ROOT, args.unit)
    capacities = filter_capacities(
        capacities,
        cap_id=args.cap_id,
        contract_ids=contract_ids or None,
        limit=args.limit,
    )
    if args.dry_run:
        for capacity in capacities:
            print(f"{capacity['id']} [{capacity['niveau']}]: {capacity['intitule']}")
        return 0
    if not capacities:
        print("ERREUR: aucune capacité à juger", file=sys.stderr)
        return 1

    env = load_env(ENV_FILE)
    # Barrier A: refuse non-internal collections before any query
    rag_col = env.get("RAG_COLLECTION", "nsi_corpus")
    if not is_internal_collection(rag_col):
        print(
            f"REFUS: RAG_COLLECTION={rag_col} n'est pas une collection "
            f"de couverture interne {sorted(INTERNAL_COVERAGE_COLLECTIONS)}",
            file=sys.stderr,
        )
        return 1
    print("Mode: pertinence lexicale + jugement LLM")
    review = build_review(
        env,
        capacities,
        unit=args.unit,
        level=args.level,
        repo_root=ROOT,
        judge_model=env.get("LOCAL_LLM_MODEL", "local-llm"),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"verdict écrit : {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
