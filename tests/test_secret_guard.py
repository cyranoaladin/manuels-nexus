from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_no_committed_secrets as secrets


def test_detects_public_ip_but_allows_placeholders_and_private_ips(tmp_path: Path) -> None:
    public_file = tmp_path / "scripts" / "public.py"
    placeholder_file = tmp_path / "README.md"
    private_file = tmp_path / "scripts" / "private.py"
    local_env = tmp_path / ".env.rag"
    public_file.parent.mkdir(parents=True)
    public_ip = "88.99." + "254.59"
    public_file.write_text(f"ssh root@{public_ip}\n", encoding="utf-8")
    placeholder_file.write_text("ssh <user>@<host>\n", encoding="utf-8")
    private_file.write_text("service http://127.0.0.1:8000\n", encoding="utf-8")
    local_env.write_text(f"RAG_SSH_HOST={public_ip}\n", encoding="utf-8")

    errors = secrets.scan_paths([public_file, placeholder_file, private_file, local_env], tmp_path)

    assert errors == [f"scripts/{public_file.name}: adresse IP publique en clair -> {public_ip}"]


def test_detects_token_like_assignments_without_flagging_examples(tmp_path: Path) -> None:
    secret_file = tmp_path / ".env.example"
    safe_file = tmp_path / ".env.safe"
    constant_file = tmp_path / "scripts" / "constants.py"
    constant_file.parent.mkdir(parents=True)
    secret_file.write_text("RAG_API_KEY=abc1234567890secret\n", encoding="utf-8")
    safe_file.write_text("RAG_API_KEY=<token Bearer pour l'API>\n", encoding="utf-8")
    constant_file.write_text('CONCRETE_TOKENS = {"trace", "table"}\n', encoding="utf-8")

    errors = secrets.scan_paths([secret_file, safe_file, constant_file], tmp_path)

    assert errors == [f"{secret_file.name}: secret potentiel dans RAG_API_KEY"]


def test_blank_secret_assignments_do_not_consume_next_line(tmp_path: Path) -> None:
    env_example = tmp_path / ".env.rag.example"
    env_example.write_text(
        "RAG_API_KEY=\n"
        "RAG_COLLECTION=nsi_corpus\n"
        "LOCAL_LLM_API_KEY=\n",
        encoding="utf-8",
    )

    errors = secrets.scan_paths([env_example], tmp_path)

    assert errors == []


def test_allows_documented_public_rag_host_only_in_env_example(tmp_path: Path) -> None:
    public_ip = "88.99." + "254.59"
    env_example = tmp_path / ".env.rag.example"
    script_file = tmp_path / "scripts" / "config.py"
    script_file.parent.mkdir(parents=True)
    env_example.write_text(f"RAG_SSH_HOST={public_ip}\n", encoding="utf-8")
    script_file.write_text(f"RAG_SSH_HOST={public_ip}\n", encoding="utf-8")

    errors = secrets.scan_paths([env_example, script_file], tmp_path)

    assert errors == [f"scripts/{script_file.name}: adresse IP publique en clair -> {public_ip}"]


def test_secret_guard_scans_tooling_not_pedagogical_corpus(tmp_path: Path) -> None:
    public_ip = "88.99." + "254.59"
    script_file = tmp_path / "scripts" / "config.py"
    support_file = tmp_path / "03_progressions" / "supports" / "terminale" / "T12" / "cours.md"
    script_file.parent.mkdir(parents=True)
    support_file.parent.mkdir(parents=True)
    script_file.write_text(f"RAG_SSH_HOST = '{public_ip}'\n", encoding="utf-8")
    support_file.write_text(f"Route externe d'exemple : {public_ip}\n", encoding="utf-8")

    errors = secrets.scan_paths([script_file, support_file], tmp_path)

    assert errors == [f"scripts/config.py: adresse IP publique en clair -> {public_ip}"]
