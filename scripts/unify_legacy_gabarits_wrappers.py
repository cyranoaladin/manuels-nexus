#!/usr/bin/env python3
"""Transform legacy gabarits in Mathematiques/ and NSI/ into thin wrappers pointing to gabarits/common/."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

WRAPPERS_MAP = {
    "nexus-boites-v6.sty": ("nexus-boites.sty", "nexus-boites-v6", "Package"),
    "nexus-charte-v6.sty": ("nexus-charte.sty", "nexus-charte-v6", "Package"),
    "nexus-couverture.sty": ("nexus-couverture.sty", "nexus-couverture", "Package"),
    "nexus-decor.sty": ("nexus-decor.sty", "nexus-decor", "Package"),
    "nexus-exercices-v6.sty": ("nexus-exercices.sty", "nexus-exercices-v6", "Package"),
    "nexus-figures-bib.sty": ("nexus-figures-bib.sty", "nexus-figures-bib", "Package"),
    "nexus-manuel-v5.cls": ("nexus-manuel.cls", "nexus-manuel-v5", "Class"),
    "nexus-manuel.cls": ("nexus-manuel.cls", "nexus-manuel", "Class"),
    "nexus-pages-froides.sty": ("nexus-pages-froides.sty", "nexus-pages-froides", "Package"),
    "nexus-pont-v6.sty": ("nexus-pont.sty", "nexus-pont-v6", "Package"),
}

DIRS = [
    REPO_ROOT / "Mathematiques/manuel-maths/gabarits",
    REPO_ROOT / "NSI/gabarits",
]

for d in DIRS:
    for filename, (target_common, pkg_name, kind) in WRAPPERS_MAP.items():
        filepath = d / filename
        target_name = target_common.removesuffix(".sty").removesuffix(".cls")
        macro = "RequirePackage" if kind == "Package" else "input"
        provides_macro = "ProvidesPackage" if kind == "Package" else "ProvidesClass"
        macro_target = f"gabarits/common/{target_common}" if kind == "Class" else f"gabarits/common/{target_name}"
        rel_target = f"../../gabarits/common/{target_common}" if kind == "Class" else f"../../gabarits/common/{target_name}"
        local_target = target_common if kind == "Class" else target_name

        compat_def = "\\def\\nxVBaseCompatibility{1}\n" if pkg_name == "nexus-manuel-v5" else ""
        charte_req_1 = "\n  \\RequirePackage{gabarits/common/nexus-charte}" if pkg_name == "nexus-manuel-v5" else ""
        charte_req_2 = "\n    \\RequirePackage{../../gabarits/common/nexus-charte}" if pkg_name == "nexus-manuel-v5" else ""
        charte_req_3 = "\n    \\RequirePackage{nexus-charte}" if pkg_name == "nexus-manuel-v5" else ""

        content = f"""% Redirection canonique vers gabarits/common/{target_common}
\\NeedsTeXFormat{{LaTeX2e}}
\\{provides_macro}{{{pkg_name}}}[2026/07/20 v6.0 Wrapper Compatibilite {pkg_name} - Canonique]
{compat_def}\\IfFileExists{{gabarits/common/{target_common}}}{{%
  \\{macro}{{{macro_target}}}{charte_req_1}%
}}{{%
  \\IfFileExists{{../../gabarits/common/{target_common}}}{{%
    \\{macro}{{{rel_target}}}{charte_req_2}%
  }}{{%
    \\{macro}{{{local_target}}}{charte_req_3}%
  }}%
}}
"""
        filepath.write_text(content, encoding="utf-8")
        print(f"Updated wrapper: {filepath.relative_to(REPO_ROOT)}")

print("Done unifying legacy gabarits wrappers!")
