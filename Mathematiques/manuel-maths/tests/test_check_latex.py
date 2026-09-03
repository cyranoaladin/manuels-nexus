import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_latex import compile_tex_files  # noqa: E402


def test_compile_tex_files_returns_nonzero_when_pdflatex_fails(tmp_path):
    source = tmp_path / "objet.tex"
    source.write_text(r"\section{Objet invalide}", encoding="utf-8")
    calls = []

    def failing_runner(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=1, stdout="! Undefined control sequence.", stderr="")

    code = compile_tex_files([source], tmp_path, runner=failing_runner)

    assert code == 1
    assert calls
    assert calls[0][0][0] == "lualatex"
    assert "-interaction=nonstopmode" in calls[0][0]
    assert "-halt-on-error" in calls[0][0]


def test_l_enveloppe_monte_l_objet_sous_la_charte_reelle() -> None:
    """R6 doit verifier l'objet sous le runtime que le manuel utilise vraiment.

    L'enveloppe montait l'objet sous la seule classe, sans la charte. Aucun
    objet du corpus ne pouvait donc employer un composant de la charte : le
    gate declarait rouge un contenu que le manuel assemble compose tres bien.
    Le defaut se payait en plomberie -- sept corriges avaient du rendre leur
    propre composant disponible, ce qui est une bequille, pas une preuve.
    """

    import check_latex

    enveloppe = check_latex._wrapper(
        ROOT / "chapitres/1SPE-PROBA-COND/corriges/1SPE-PROBCOND-CO-019.tex",
        ROOT,
    )

    assert "nexus-charte" in enveloppe, (
        "l'enveloppe R6 doit charger la charte, comme le manuel assemble"
    )
    assert enveloppe.index("nexus-charte") < enveloppe.index(r"\begin{document}")


def test_aucun_corrige_ne_charge_lui_meme_un_composant_de_la_charte() -> None:
    """Une fois l'enveloppe reparee, la plomberie doit disparaitre.

    Un objet du corpus qui charge un `.sty` de la charte contourne le runtime
    canonique : il compilerait meme si la charte cessait de fournir le
    composant, et le gate ne verrait plus rien.
    """

    coupables = [
        chemin
        for chemin in sorted((ROOT / "chapitres").rglob("*.tex"))
        if "nexus-arbres.sty" in chemin.read_text(encoding="utf-8")
    ]

    assert coupables == [], (
        "ces objets chargent eux-memes un composant de la charte : "
        + ", ".join(str(c.relative_to(ROOT)) for c in coupables)
    )
