"""MCP sympy : exécution sandbox de scripts de vérification mathématique."""
import subprocess
import sys
import tempfile
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("mcp-sympy")


@mcp.tool()
def verify(script: str, timeout: int = 30) -> dict:
    """Exécute un script Python (SymPy/NumPy disponibles) en mode isolé (-I).
    Le script doit lever AssertionError en cas d'échec. Retourne {verdict, output}."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(script)
        path = f.name
    try:
        proc = subprocess.run([sys.executable, "-I", path], capture_output=True,
                              text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"verdict": "fail", "output": "timeout"}
    finally:
        Path(path).unlink(missing_ok=True)
    return {"verdict": "pass" if proc.returncode == 0 else "fail",
            "output": (proc.stdout + proc.stderr)[-3000:]}


if __name__ == "__main__":
    mcp.run()
