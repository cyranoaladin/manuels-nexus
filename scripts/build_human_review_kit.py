#!/usr/bin/env python3
"""Le dossier que les relecteurs ouvrent — index, vues lisibles, formulaire.

Vingt verdicts attendent des personnes. Ce qui les attendait jusqu'ici était un
JSON de quarante kilo-octets et une vue Markdown où les formules s'écrivaient
`$\\dfrac{5\\pi}{6}$`. Un relecteur de mathématiques ne doit pas décoder du TeX
pour juger une copie : il doit VOIR π, les fractions et les racines comme le
manuel les imprime.

Ce module ne crée aucune autorité parallèle. Le paquet JSON reste l'autorité ;
la vue Markdown reste produite par son producteur. Il assemble un dossier :

* un INDEX des dix chapitres, avec pour chacun ses deux rôles, son condensat
  sémantique, ce qui demande de l'attention et son état de revue ;
* pour chaque chapitre et chaque rôle, une page qui RÉAFFICHE la vue existante
  avec ses mathématiques rendues -- le TeX canonique est confié à MathJax, on
  n'en fabrique pas une seconde version textuelle ;
* le formulaire de verdict, et la commande exacte qui l'enregistre.

Ce module ne nomme aucun relecteur et n'en déduit aucun : les identités
viennent du responsable humain, jamais de Git, jamais de la machine.

Métriques : `CHAPTERS`, `VIEWS_WRITTEN`, `PENDING_VERDICTS`.
Métrique bloquante : `CHAPTERS_WITHOUT_BOTH_ROLES`.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT  # noqa: E402

KIT = ROOT / "audit/HUMAN_REVIEW_KIT_1SPE"
JSON_TARGET = KIT / "INDEX.json"
GENERATED_BY = "scripts/build_human_review_kit.py"

REVIEWS = ROOT / "audit/reviews/human"
ROLES = ("A-EXPERT_MATHEMATIQUE", "B-EXPERT_PROGRAMME_PEDAGOGIE")
# L'ordre de lecture recommandé par la direction de production.
READING_ORDER = (
    "1SPE-PROBA-COND",
    "1SPE-SUITES",
    "1SPE-TRIGONOMETRIE",
    "1SPE-VARIABLES-ALEATOIRES",
    "1SPE-DERIVATION-GLOBAL",
    "1SPE-DERIVATION-LOCAL",
    "1SPE-SECOND-DEGRE",
    "1SPE-EXPONENTIELLE",
    "1SPE-PRODUIT-SCALAIRE",
    "1SPE-GEOMETRIE-REPEREE",
)

# MathJax rend le TeX canonique dans le navigateur : la source reste la source,
# et le relecteur lit des mathématiques. Aucune seconde version textuelle.
MATHJAX = (
    '<script>window.MathJax={tex:{inlineMath:[["$","$"]],'
    'displayMath:[["\\\\[","\\\\]"]],processEscapes:true},'
    'options:{skipHtmlTags:["script","noscript","style","textarea","pre"]}};'
    "</script>\n"
    '<script id="MathJax-script" async '
    'src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>'
)

STYLE = """
body{font:16px/1.6 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
max-width:52rem;margin:2rem auto;padding:0 1.2rem;color:#1a1a1a}
h1{font-size:1.6rem}h2{font-size:1.25rem;margin-top:2.2rem;
border-bottom:1px solid #ddd;padding-bottom:.3rem}
h3{font-size:1.05rem;margin-top:1.6rem}
code{background:#f4f4f6;padding:.1em .3em;border-radius:3px;font-size:.9em}
table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.92rem}
th,td{border:1px solid #ddd;padding:.4rem .6rem;text-align:left}
th{background:#f7f7f9}
blockquote{border-left:3px solid #c8102e;margin:1rem 0;padding:.4rem 1rem;
background:#fbf5f6}
.mandatory{background:#fff4e5;border-left:3px solid #d97706;padding:.6rem 1rem}
.form{background:#f7f7f9;border:1px solid #ddd;padding:1rem;border-radius:4px}
"""


class KitError(RuntimeError):
    """Une preuve manque : le dossier ne peut pas être assemblé."""


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def _markdown_to_html(text: str) -> str:
    """Un rendu volontairement minimal : titres, tables, listes, citations.

    Les formules ne sont PAS touchées -- elles traversent telles quelles et
    c'est MathJax qui les rend. Passer un moteur Markdown complet sur du TeX
    reviendrait à laisser un tiers réinterpréter les mathématiques.
    """

    out: list[str] = []
    in_table = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if all(set(cell) <= set("-: ") for cell in cells):
                continue
            tag = "th" if not in_table else "td"
            if not in_table:
                out.append("<table>")
                in_table = True
            out.append(
                "<tr>"
                + "".join(f"<{tag}>{_inline(cell)}</{tag}>" for cell in cells)
                + "</tr>"
            )
            continue
        if in_table:
            out.append("</table>")
            in_table = False
        if not line.strip():
            continue
        if line.startswith("#"):
            level = min(len(line) - len(line.lstrip("#")), 6)
            out.append(f"<h{level}>{_inline(line.lstrip('# '))}</h{level}>")
        elif line.startswith(">"):
            out.append(f"<blockquote>{_inline(line.lstrip('> '))}</blockquote>")
        elif line.lstrip().startswith(("- ", "* ")):
            out.append(f"<p style='margin:.2rem 0 .2rem 1.2rem'>• "
                       f"{_inline(line.lstrip('-* '))}</p>")
        else:
            out.append(f"<p>{_inline(line)}</p>")
    if in_table:
        out.append("</table>")
    return "\n".join(out)


# Une première version appariait les marqueurs en les remplaçant par des octets
# de contrôle littéraux, invisibles dans la source -- après une campagne passée
# à retirer des caractères de contrôle d'une couche de texte, c'était une ironie
# qu'il valait mieux ne pas laisser dormir dans un fichier. L'appariement se
# fait maintenant par découpage, sans sentinelle du tout.
def _pair(text: str, marker: str, opening: str, closing: str) -> str:
    """Remplace les marqueurs APPARIÉS ; un marqueur seul est laissé tel quel."""

    if text.count(marker) < 2:
        return text
    parts = text.split(marker)
    rebuilt = parts[0]
    for index, part in enumerate(parts[1:], start=1):
        rebuilt += (opening if index % 2 else closing) + part
    if len(parts) % 2 == 0:
        # Nombre impair de marqueurs : la dernière balise ouverte est refermée.
        rebuilt += closing
    return rebuilt


def _inline(text: str) -> str:
    """Échappe le HTML sans jamais toucher aux délimiteurs mathématiques."""

    pieces: list[str] = []
    for index, chunk in enumerate(text.split("$")):
        if index % 2:
            # Contenu mathématique : intact, entre ses dollars.
            pieces.append(f"${chunk}$")
            continue
        safe = html.escape(chunk)
        safe = _pair(safe, "**", "<strong>", "</strong>")
        safe = _pair(safe, "`", "<code>", "</code>")
        pieces.append(safe)
    return "".join(pieces)


def verdict_form(chapter: str, role: str, packet: dict[str, Any]) -> str:
    letter, _, name = role.partition("-")
    packet_path = f"audit/reviews/human/{chapter}/packet-{role}.json"
    receipt_path = f"audit/reviews/human/{chapter}/receipt-{role}.json"
    return f"""
<h2>Votre verdict</h2>
<div class="form">
<p>Le verdict ne se saisit pas dans cette page : elle est dérivée et sans
autorité. Trois commandes, dans cet ordre.</p>
<p><strong>1. Obtenir le brouillon</strong> — tous les condensats sont
pré-remplis ; ne restent que les champs qui vous appartiennent.</p>
<p><code>python3 scripts/human_review_governance.py draft {chapter} \\
--packet {packet_path} \\
--out {receipt_path}</code></p>
<p><strong>2. Renseigner, et rien d'autre</strong> :
<code>reviewer_name</code>, <code>reviewer_identity_reference</code>,
<code>review_timestamp</code> (RFC 3339),
<code>verdict</code> parmi
{", ".join(f"<code>{v}</code>" for v in packet["permitted_verdicts"])},
<code>comments</code>. Un <code>CHANGES_REQUESTED</code> exige au moins un
constat dans <code>blocking_findings</code> ; un <code>APPROVED</code> n'en
admet aucun.</p>
<p><strong>3. Valider</strong> — le contrôle refuse un verdict sans identité,
sans rôle, sans condensat, ou sur un paquet périmé.</p>
<p><code>python3 scripts/human_review_governance.py validate {chapter} \\
--packet {packet_path} \\
--receipt {receipt_path}</code></p>
<p>Le chapitre reçoit <strong>deux</strong> verdicts, par
<strong>deux personnes distinctes</strong> : le contrôle refuse deux rôles
signés par la même identité. Une même personne peut en revanche prendre
plusieurs chapitres.</p>
<p>Condensat sémantique que votre approbation lie :
<code>{packet["semantic_review_digest"]}</code></p>
</div>
"""


def page(title: str, body: str) -> str:
    return (
        "<!DOCTYPE html><html lang=\"fr\"><head><meta charset=\"utf-8\">"
        f"<title>{html.escape(title)}</title>"
        f"<style>{STYLE}</style>{MATHJAX}</head><body>\n{body}\n</body></html>\n"
    )


def chapter_entry(chapter: str) -> dict[str, Any]:
    directory = REVIEWS / chapter
    state = _load(directory / "REVIEW_STATE.json") or {}
    entry: dict[str, Any] = {
        "chapter": chapter,
        "semantic_digest": state.get("semantic_review_digest"),
        "object_count": state.get("object_count"),
        "qcm_question_count": state.get("qcm_question_count"),
        "roles": [],
    }
    for role in ROLES:
        packet = _load(directory / f"packet-{role}.json")
        if packet is None:
            continue
        key = "review_a" if role.startswith("A-") else "review_b"
        review = state.get(key) or {}
        entry["roles"].append(
            {
                "role": role,
                "packet": f"audit/reviews/human/{chapter}/packet-{role}.json",
                "source_view": f"audit/reviews/human/{chapter}/view-{role}.md",
                "kit_view": f"audit/HUMAN_REVIEW_KIT_1SPE/{chapter}-{role}.html",
                "objects": packet.get("object_count"),
                "state": review.get("state"),
                "verdict": review.get("verdict"),
            }
        )
    return entry


def barème_facts(chapter: str) -> dict[str, Any]:
    proposal = _load(ROOT / "audit/1SPE_BAREME_COMMENTARY_PROPOSAL.json") or {}
    mandatory = _load(
        ROOT / "audit/1SPE_ASSESSMENT_BAREME_TRANSCRIPTION.json"
    ) or {}
    rows = [
        question
        for assessment in proposal.get("assessments", [])
        if assessment["chapter"] == chapter
        for exercise in assessment["exercises"]
        for question in exercise["questions"]
    ]
    human_ids = {
        row["object_id"] for row in mandatory.get("human_decision_packet", [])
    }
    chapter_mandatory = [
        row["object_id"]
        for row in mandatory.get("human_decision_packet", [])
        if row["chapter"] == chapter
    ]
    return {
        "assessment_questions": len(rows),
        "judgement_required": sum(
            1 for row in rows if row["verdict"] != "PROPOSED"
        ),
        "mandatory_decisions": chapter_mandatory,
        "has_mandatory_decision": bool(chapter_mandatory and human_ids),
    }


def build(write: bool = True) -> dict[str, Any]:
    chapters = [name for name in READING_ORDER if (REVIEWS / name).is_dir()]
    missing = [name for name in READING_ORDER if name not in chapters]
    if missing:
        raise KitError(f"chapitres absents du dossier de revue : {missing}")

    entries: list[dict[str, Any]] = []
    written = 0
    if write:
        KIT.mkdir(parents=True, exist_ok=True)
    for order, chapter in enumerate(chapters, start=1):
        entry = chapter_entry(chapter)
        entry["reading_order"] = order
        entry["bareme"] = barème_facts(chapter)
        entries.append(entry)
        if not write:
            continue
        for role in entry["roles"]:
            source = ROOT / role["source_view"]
            if not source.is_file():
                raise KitError(f"vue source absente : {role['source_view']}")
            packet = _load(ROOT / role["packet"])
            body = _markdown_to_html(source.read_text(encoding="utf-8"))
            body += verdict_form(chapter, role["role"], packet)
            (ROOT / role["kit_view"]).write_text(
                page(f"{chapter} — {role['role']}", body), encoding="utf-8"
            )
            written += 1

    incomplete = [row for row in entries if len(row["roles"]) != len(ROLES)]
    pending = sum(
        1 for row in entries for role in row["roles"] if role["verdict"] is None
    )
    payload = {
        "artifact_type": "human_review_kit_1spe",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "approves_nothing": True,
        "the_json_packet_remains_the_authority": (
            "Ces pages sont dérivées et sans autorité. Toute divergence se "
            "tranche en faveur du paquet JSON canonique."
        ),
        "no_reviewer_is_named_here": (
            "Aucune identité n'est créée ni déduite : elles viennent du "
            "responsable humain, jamais de Git, jamais de la machine."
        ),
        "the_unit_of_decision_is_the_chapter": (
            "Dix chapitres, deux rôles, vingt verdicts. Les items d'attention "
            "dirigent la lecture ; ils ne sont pas des signatures."
        ),
        "chapters": entries,
        "summary": {
            "CHAPTERS": len(entries),
            "VIEWS_WRITTEN": written,
            "EXPECTED_VERDICTS": len(entries) * len(ROLES),
            "PENDING_VERDICTS": pending,
            "CHAPTERS_WITHOUT_BOTH_ROLES": len(incomplete),
            "CHAPTERS_WITH_MANDATORY_DECISION": sum(
                1 for row in entries if row["bareme"]["has_mandatory_decision"]
            ),
            "ASSESSMENT_QUESTIONS": sum(
                row["bareme"]["assessment_questions"] for row in entries
            ),
            "BAREME_JUDGEMENTS_REQUIRED": sum(
                row["bareme"]["judgement_required"] for row in entries
            ),
        },
    }
    if write:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (KIT / "INDEX.html").write_text(render_index(payload), encoding="utf-8")
    return payload


def render_index(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = [
        "<h1>Revue humaine — Nexus 1SPE</h1>",
        f"<blockquote>{payload['the_unit_of_decision_is_the_chapter']}</blockquote>",
        f"<blockquote>{payload['the_json_packet_remains_the_authority']}</blockquote>",
        f"<blockquote>{payload['no_reviewer_is_named_here']}</blockquote>",
        "<h2>Ce qui est attendu</h2>",
        "<table><tr><th>Grandeur</th><th>Valeur</th></tr>",
    ]
    for name, value in summary.items():
        rows.append(f"<tr><td><code>{name}</code></td><td>{value}</td></tr>")
    rows += [
        "</table>",
        "<h2>Les dix chapitres, dans l'ordre de lecture recommandé</h2>",
        "<table><tr><th>#</th><th>Chapitre</th><th>Objets</th>"
        "<th>Questions d'évaluation</th><th>Jugements de barème</th>"
        "<th>Expert mathématique</th><th>Expert programme / pédagogie</th></tr>",
    ]
    for entry in payload["chapters"]:
        cells = {row["role"][0]: row for row in entry["roles"]}
        mandatory = (
            " <span class='mandatory'>DÉCISION OBLIGATOIRE</span>"
            if entry["bareme"]["has_mandatory_decision"]
            else ""
        )
        links = []
        for letter in ("A", "B"):
            role = cells.get(letter)
            if role is None:
                links.append("—")
                continue
            name = Path(role["kit_view"]).name
            links.append(
                f"<a href='{name}'>ouvrir</a> · "
                f"<code>{role['state'] or 'PENDING'}</code>"
            )
        rows.append(
            f"<tr><td>{entry['reading_order']}</td>"
            f"<td><code>{entry['chapter']}</code>{mandatory}</td>"
            f"<td>{entry['object_count']}</td>"
            f"<td>{entry['bareme']['assessment_questions']}</td>"
            f"<td>{entry['bareme']['judgement_required']}</td>"
            f"<td>{links[0]}</td><td>{links[1]}</td></tr>"
        )
    rows += [
        "</table>",
        "<h2>Deux personnes distinctes par chapitre</h2>",
        "<p>Le contrôle refuse deux rôles signés par la même identité. Une "
        "même personne peut en revanche prendre plusieurs chapitres.</p>",
        "<h2>Les deux décisions obligatoires</h2>",
        "<p>Les barèmes des deux évaluations de géométrie repérée ne se "
        "dérivent d'aucune source : le sujet ne value aucune question "
        "individuellement, et répartir son total est un jugement pédagogique. "
        "Ils apparaissent en tête de la section barème de la vue programme et "
        "pédagogie du chapitre <code>1SPE-GEOMETRIE-REPEREE</code>.</p>",
    ]
    return page("Revue humaine — Nexus 1SPE", "\n".join(rows))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ne rien écrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build(write=not arguments.check)
    except KitError as error:
        print(f"HUMAN-REVIEW-KIT-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        print(f"écrit {KIT.relative_to(ROOT)}/INDEX.html et ses vues")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    return 1 if payload["summary"]["CHAPTERS_WITHOUT_BOTH_ROLES"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
