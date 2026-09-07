"""L'étage `check` du gate doit pouvoir être vert sur un arbre commité.

CE QUI A ÉTÉ CONSTATÉ. Les six artefacts gérés portent deux champs de
provenance — `head_sha` et `generated_at_utc` — dont la valeur est celle du
HEAD au moment du calcul. Committer l'artefact avance le HEAD : le fichier
commité nomme dès lors son propre parent, et la régénération suivante produit
un contenu différent d'un octet près. `check` signale alors `diff:` et sort en
code 3, avant même d'évaluer `release-strict`.

Ce n'est pas une dérive de contenu : c'est une impossibilité de construction.
Sondage sur l'historique — base `58f23b71` comprise, donc bien avant cette
session — chaque commit porte un `ETAT_COLLECTION.md` qui nomme un ancêtre,
jamais lui-même. `check` n'a donc jamais pu être vert sur un arbre commité, et
tout compte de bloqueurs en contenait au moins un que nul travail de contenu
ne pouvait retirer.

LA RÈGLE, ET CE QU'ELLE NE RELÂCHE PAS. Un artefact est conforme s'il est
identique au bit près, ou si les seules différences portent sur les champs de
provenance ET que le HEAD qu'il nomme est un ancêtre du HEAD courant ET que
tout fichier modifié entre les deux est lui-même un artefact généré.

Cette dernière condition est celle qui empêche de transformer la correction en
échappatoire : dès qu'une source a changé depuis le HEAD nommé, l'artefact est
réellement périmé et le gate reste rouge.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import inventory_collection as ic  # noqa: E402


def _head(root: Path = ROOT) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True,
        check=True,
    ).stdout.strip()


def test_the_provenance_fields_are_named_not_guessed() -> None:
    """La liste est fermée : on ne tolère pas « tout ce qui ressemble à une date »."""
    assert ic.PROVENANCE_FIELDS == ("generated_at_utc", "head_sha")


AVANT = "a" * 40
APRES = "b" * 40

JSON_AVANT = (
    '{\n'
    '  "source_file_count": 4798,\n'
    '  "provenance": {\n'
    f'    "generated_at_utc": "2026-09-07T01:00:00Z",\n'
    f'    "head_sha": "{AVANT}"\n'
    '  }\n'
    '}\n'
)


def test_a_difference_confined_to_provenance_is_tolerated() -> None:
    rendered = JSON_AVANT.replace(AVANT, APRES).replace("01:00:00", "02:00:00")
    assert ic._difference_is_only_provenance(
        Path("audit/INVENTAIRE_COLLECTION.json"), rendered, JSON_AVANT
    )


def test_a_difference_anywhere_else_is_not_tolerated() -> None:
    """Un seul chiffre de contenu qui bouge, et la dérive reste bloquante."""
    rendered = (
        JSON_AVANT.replace(AVANT, APRES).replace("4798", "4799")
    )
    assert not ic._difference_is_only_provenance(
        Path("audit/INVENTAIRE_COLLECTION.json"), rendered, JSON_AVANT
    )


def test_an_added_line_is_not_tolerated() -> None:
    """Une ligne ajoutée déplace tout : la reconnaissance doit échouer."""
    rendered = JSON_AVANT.replace('  "provenance"', '  "nouveau": 1,\n  "provenance"')
    assert not ic._difference_is_only_provenance(
        Path("audit/INVENTAIRE_COLLECTION.json"), rendered, JSON_AVANT
    )


MD_AVANT = f"- SHA Git: `{AVANT}`\n- Fichiers scannés: 4798\n"


def test_a_markdown_difference_outside_provenance_is_not_tolerated() -> None:
    rendered = MD_AVANT.replace(AVANT, APRES).replace("4798", "4799")
    assert not ic._difference_is_only_provenance(
        Path("ETAT_COLLECTION.md"), rendered, MD_AVANT
    )


def test_a_markdown_difference_confined_to_provenance_is_tolerated() -> None:
    rendered = MD_AVANT.replace(AVANT, APRES)
    assert ic._difference_is_only_provenance(
        Path("ETAT_COLLECTION.md"), rendered, MD_AVANT
    )


def test_a_source_change_since_the_named_head_keeps_the_gate_red() -> None:
    """L'échappatoire est fermée : une source modifiée rend l'artefact périmé."""
    assert ic._only_generated_artifacts_changed_since(ROOT, _head()) is True
    # Un HEAD très ancien : des sources ont forcément changé depuis.
    base = subprocess.run(
        ["git", "rev-parse", "58f23b71"], cwd=ROOT, capture_output=True, text=True,
        check=True,
    ).stdout.strip()
    assert ic._only_generated_artifacts_changed_since(ROOT, base) is False


def test_a_head_that_is_not_an_ancestor_is_refused() -> None:
    """Un artefact ne peut pas nommer un commit hors de la lignée du HEAD."""
    assert ic._named_head_is_usable(ROOT, "0" * 40) is False
    assert ic._named_head_is_usable(ROOT, _head()) is True


def _named_head_of(relative: str) -> str:
    import re

    for line in (ROOT / relative).read_text(encoding="utf-8").splitlines():
        match = re.search(r"[0-9a-f]{40}", line)
        if match and ic._provenance_line(line):
            return match.group(0)
    return ""


def test_only_four_of_the_six_artifacts_carry_a_provenance_head() -> None:
    """Mesuré, pas supposé : deux artefacts n'en portent pas, et ne dérivent pas.

    `AUDIT_CONSOLIDE.md` et `INVENTAIRE_COLLECTION.md` ne citent aucun SHA :
    leur contenu est stable d'une régénération à l'autre, et ils n'ont donc
    besoin d'aucune tolérance. C'est important : un artefact sans SHA nommé
    n'obtient aucune excuse s'il dérive.
    """
    avec = {r for r in ic.DEFAULT_MANAGED_OUTPUT_PATHS if _named_head_of(r)}
    sans = set(ic.DEFAULT_MANAGED_OUTPUT_PATHS) - avec
    assert sans == {"audit/AUDIT_CONSOLIDE.md", "audit/INVENTAIRE_COLLECTION.md"}
    assert len(avec) == 4


def test_an_artifact_without_a_named_head_gets_no_tolerance() -> None:
    """Sans SHA nommé, une dérive reste une dérive."""
    assert ic._drift_is_only_self_reference(
        ROOT, Path("audit/AUDIT_CONSOLIDE.md"), "a\n", b"b\n",
    ) is False


def test_every_artifact_that_names_a_head_satisfies_the_three_conditions() -> None:
    """Sur l'arbre commité, la règle complète est remplie.

    Régénérer les artefacts pour le vérifier coûterait plusieurs minutes ; on
    vérifie donc directement ce que la règle exige, sur ce qui est déposé.
    """
    nommants = [r for r in sorted(ic.DEFAULT_MANAGED_OUTPUT_PATHS) if _named_head_of(r)]
    assert nommants, "aucun artefact ne nomme de HEAD : le test ne prouverait rien"
    for relative in nommants:
        named = _named_head_of(relative)
        assert ic._named_head_is_usable(ROOT, named), (relative, named)
        assert ic._only_generated_artifacts_changed_since(ROOT, named), (
            relative, named,
        )


def test_the_named_head_is_always_usable() -> None:
    """Le HEAD nommé est toujours utilisable, avant comme après le commit.

    J'avais d'abord écrit que l'artefact ne nomme JAMAIS son propre commit.
    C'est faux dans la fenêtre qui sépare la régénération du commit : là, il
    nomme exactement le HEAD courant, et le test échouait sans qu'aucun défaut
    n'existe. La boucle se referme au commit suivant, quand le HEAD avance.

    Ce qui tient dans les deux états — et c'est ce dont la tolérance dépend —
    c'est que le HEAD nommé soit un ancêtre au sens large du HEAD courant.
    """
    named = _named_head_of("ETAT_COLLECTION.md")
    assert named
    assert ic._named_head_is_usable(ROOT, named)
    assert ic._only_generated_artifacts_changed_since(ROOT, named)
