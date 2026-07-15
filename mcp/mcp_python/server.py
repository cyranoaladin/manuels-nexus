"""MCP python : exécution sandbox de code Python (vérifications, traces, tests pytest)."""
import subprocess
import sys
import tempfile
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("mcp-python")


@mcp.tool()
def run(script: str, timeout: int = 30) -> dict:
    """Exécute un script Python en sandbox (-I, cwd temporaire, sans réseau applicatif).
    Retourne {returncode, stdout, stderr}. Utiliser pour valider tout code/trace avant
    de l'écrire dans le manuel (règle R2)."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "run.py"
        path.write_text(script, encoding="utf-8")
        try:
            proc = subprocess.run([sys.executable, "-I", str(path)], capture_output=True,
                                  text=True, timeout=timeout, cwd=tmp)
        except subprocess.TimeoutExpired:
            return {"returncode": 1, "stdout": "", "stderr": "timeout"}
    return {"returncode": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-2000:]}


@mcp.tool()
def ruff_check(code: str) -> dict:
    """Vérifie le style d'un fragment de code élève (ruff, E501/F821 ignorés)."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        p = f.name
    proc = subprocess.run(["ruff", "check", "--quiet", "--ignore", "E501,F821", p],
                          capture_output=True, text=True)
    Path(p).unlink(missing_ok=True)
    return {"ok": proc.returncode == 0, "detail": proc.stdout[-2000:]}


if __name__ == "__main__":
    mcp.run()
