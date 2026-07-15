"""MCP latex : compilation pdflatex d'un objet ou d'un chapitre, erreurs parsées."""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from common import ROOT  # noqa: E402

from fastmcp import FastMCP  # noqa: E402

mcp = FastMCP("mcp-latex")
ERR = re.compile(r"^! (.+)$|^l\.(\d+)", re.M)


@mcp.tool()
def compile_object(tex_relpath: str) -> dict:
    """Compile un objet .tex isolé (englobé dans le gabarit standalone). Retourne
    {ok, errors[], pdf_path}. À appeler avant tout commit d'un .tex (règle R6)."""
    obj = ROOT / tex_relpath
    if not obj.exists():
        return {"ok": False, "errors": [f"fichier introuvable : {tex_relpath}"]}
    build = ROOT / "build" / "objets"
    build.mkdir(parents=True, exist_ok=True)
    wrapper = (ROOT / "gabarits" / "objet_standalone.tex").read_text(encoding="utf-8")
    wrapped = build / (obj.stem + "_sa.tex")
    wrapped.write_text(wrapper.replace("%%OBJ%%", str(obj.relative_to(ROOT))), encoding="utf-8")
    proc = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                           f"-output-directory={build}", str(wrapped)],
                          capture_output=True, text=True, cwd=ROOT)
    errors = [" ".join(filter(None, m.groups())) for m in ERR.finditer(proc.stdout)]
    return {"ok": proc.returncode == 0, "errors": errors[:20],
            "pdf_path": str(build / (wrapped.stem + ".pdf")) if proc.returncode == 0 else None}


@mcp.tool()
def compile_chapter(chap: str, variant: str = "complet") -> dict:
    """Assemble et compile un chapitre complet via scripts/assemble.py."""
    proc = subprocess.run([sys.executable, "scripts/assemble.py", "--chap", chap,
                           "--variant", variant], capture_output=True, text=True, cwd=ROOT)
    return {"ok": proc.returncode == 0, "log": proc.stdout[-3000:]}


if __name__ == "__main__":
    mcp.run()
