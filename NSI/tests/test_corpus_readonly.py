"""Vérifie qu'aucun script du dépôt n'ouvre un chemin sous CORPUS_NSI en écriture."""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"

# Patterns dangereux : écriture vers le corpus
WRITE_PATTERNS = [
    r"\.write_text\(",
    r"\.write_bytes\(",
    r"open\([^)]*['\"]w['\"]",
    r"open\([^)]*['\"]a['\"]",
    r"open\([^)]*mode\s*=\s*['\"]w",
    r"open\([^)]*mode\s*=\s*['\"]a",
    r"shutil\.copy\(",
    r"shutil\.copy2\(",
    r"shutil\.copytree\(",
    r"shutil\.move\(",
    r"os\.rename\(",
    r"os\.remove\(",
    r"os\.unlink\(",
    r"\.mkdir\(",
    r"\.rmdir\(",
    r"shutil\.rmtree\(",
]

# Identifiers that reference the corpus source
CORPUS_REFS = ["CORPUS_NSI", "corpus_nsi", "CORPUS"]


def test_no_writes_to_corpus():
    """Aucun script ne doit écrire dans le corpus source."""
    violations = []
    for py in sorted(SCRIPTS_DIR.glob("*.py")):
        text = py.read_text(encoding="utf-8")
        lines = text.splitlines()
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for pat in WRITE_PATTERNS:
                if re.search(pat, line):
                    # Check if this write targets the corpus
                    # Look at context: previous lines for variable assignment
                    context = "\n".join(lines[max(0, i - 5):i])
                    for ref in CORPUS_REFS:
                        if ref in context and "harvest_dir" not in context and "_harvest" not in context:
                            violations.append(f"{py.name}:{i}: {stripped[:100]}")

    # Also check: harvest_nsi.py copies FROM corpus TO _harvest, never the reverse
    harvest = SCRIPTS_DIR / "harvest_nsi.py"
    if harvest.exists():
        text = harvest.read_text(encoding="utf-8")
        # shutil.copy2(src, dest) — src must be from corpus, dest must be _harvest
        for m in re.finditer(r"shutil\.(copy2?|copytree)\(([^,]+),\s*([^)]+)\)", text):
            dest = m.group(3).strip()
            if "CORPUS" in dest or "corpus_nsi" in dest:
                violations.append(f"harvest_nsi.py: write destination is corpus: {m.group(0)[:80]}")

    assert not violations, "Writes to corpus detected:\n" + "\n".join(violations)


if __name__ == "__main__":
    test_no_writes_to_corpus()
    print("OK — aucune écriture vers le corpus détectée.")
