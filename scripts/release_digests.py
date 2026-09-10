#!/usr/bin/env python3
"""Algèbre canonique des empreintes de release — implémentation unique.

Ce module remplace `CONTENT_SOURCE_CLOSURE_DIGEST`, dont la construction était
circulaire : il agrégeait neuf artefacts de `audit/`, dont `BLOCKER_TAXONOMY.json`,
qui change précisément *parce que* le reçu humain existe. Une empreinte censée
authentifier une décision ne peut pas dépendre de cette décision.

Quatre empreintes indépendantes sont définies ici, et une seule fois. Le packet,
le validateur de reçu, le gate et les tests appellent tous ces fonctions ; aucun
producteur ne recopie une valeur littérale.

Stratification (une couche ne lit que des couches strictement inférieures) :

    L0  sources sur disque (.tex, .json de contenu, gabarits, styles)
    L1  OBJECT_SET_DIGEST, PEDAGOGICAL_CONTENT_DIGEST, BUILD_SOURCE_CLOSURE_DIGEST
    L2  ACCEPTANCE_EVIDENCE_BUNDLE_DIGEST   (preuves *pré-décision* uniquement)
    L3  packet d'acceptation
    L4  reçu humain
    L5  artefacts dérivés du reçu (transitions de maturité, levée de bloqueurs)

`assert_acyclic()` vérifie mécaniquement qu'aucune entrée de L0..L3 n'appartient
à L4 ou L5.

Découpage pédagogique / gouvernance
-----------------------------------
Chaque objet porte une ligne `% META: {...}`. Les clés de *pure gouvernance*
(maturité, provenance, liaison au reçu) sont exclues de
`PEDAGOGICAL_CONTENT_DIGEST` : une transition de statut ne doit pas déplacer
l'empreinte du contenu didactique. Toute autre clé — y compris une clé nouvelle
et inconnue — est réputée pédagogique (fail-closed) : on ne peut pas faire sortir
un champ du périmètre en l'inventant.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "audit/INVENTAIRE_COLLECTION.json"

# --- Périmètre explicite (exigence §4.1.B : inclusions/exclusions déclarées) ---

#: Clés `% META:` de pure gouvernance. Exclues de PEDAGOGICAL_CONTENT_DIGEST.
#: Elles décrivent la maturité, la provenance ou la liaison à une décision
#: humaine — jamais ce que l'objet enseigne ni ce qui est imprimé.
GOVERNANCE_META_KEYS: frozenset[str] = frozenset({
    "status",
    "origin",
    "status_history",
    "release_acceptance",
    "acceptance_closure_digest",
    "acceptance_receipt_digest",
    "mode_creation",
    "sources_inspiration",
    "genere_depuis",
    "version",
    # Une approbation retiree parce que le contenu a change est une donnee de
    # gouvernance : elle dit qui a valide quoi, jamais ce que l'objet enseigne.
    # La classer pedagogique ferait bouger l'empreinte du contenu au moment
    # meme ou l'on constate qu'il n'a pas bouge.
    "approval_state",
})

#: Artefacts de preuve *antérieurs* à toute décision humaine. Un artefact qui
#: change parce qu'un reçu existe n'a pas sa place ici (c'était le défaut de
#: BLOCKER_TAXONOMY dans l'ancienne closure).
ACCEPTANCE_EVIDENCE_ARTIFACTS: tuple[str, ...] = (
    "audit/SEMANTIC_ALIGNMENT_AUDIT.json",
    "audit/QCM_QUALITY_AUDIT.json",
    "audit/RELEASE_OBJECT_BATCH_AUDIT.json",
    "audit/CHAPTER_PEDAGOGICAL_QUALITY.json",
    "audit/EDITORIAL_QUALITY_AUDIT.json",
    "audit/SOLUTIONS_COMPLETENESS_AUDIT.json",
    "audit/FIGURES_QUALITY_AUDIT.json",
    "audit/HUMAN_REVIEW_QUEUE.json",
    "audit/RELEASE_RAW_REASONS.json",
)

#: Artefacts interdits dans toute empreinte de niveau <= L3 : ils dépendent de
#: la décision humaine qu'ils sont censés authentifier.
DECISION_DEPENDENT_ARTIFACTS: frozenset[str] = frozenset({
    "audit/RELEASE_OWNER_DECISION_RECEIPT.json",
    "audit/RELEASE_OWNER_DECISION_RECEIPT.md",
    "audit/BLOCKER_TAXONOMY.json",
    "audit/BLOCKER_TAXONOMY.md",
    "audit/RELEASE_MATURITY_TRANSITION_AUDIT.json",
    "audit/RELEASE_MATURITY_TRANSITION_AUDIT.md",
    "audit/CERTIFIED_UNSIGNED_RELEASE_CANDIDATES.json",
})


class DigestScopeError(RuntimeError):
    """Une empreinte de niveau <= L3 tente d'ingérer un artefact post-décision."""


def _sha(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _merkle(entries: Iterable[tuple[str, bytes]]) -> str:
    """Empreinte stable et ordonnée d'une suite (nom, charge utile)."""
    acc = hashlib.sha256()
    for name, payload in sorted(entries):
        acc.update(name.encode("utf-8"))
        acc.update(b"\x00")
        acc.update(hashlib.sha256(payload).digest())
        acc.update(b"\x00")
    return "sha256:" + acc.hexdigest()


# --- Lecture des objets canoniques -------------------------------------------

def load_canonical_objects(root: Path = ROOT) -> list[dict[str, Any]]:
    """Objets canoniques déclarés par l'inventaire, triés par identifiant."""
    inventory = json.loads((root / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8"))
    objects: list[dict[str, Any]] = []
    for manual, mval in inventory.get("manuals", {}).items():
        for chapter, cval in mval.get("chapters", {}).items():
            for obj in cval.get("objects", []):
                objects.append({
                    "id": obj["id"],
                    "path": obj["path"],
                    "manual": manual,
                    "chapter": chapter,
                    "status": obj.get("status"),
                })
    objects.sort(key=lambda o: o["id"])
    return objects


def split_meta(meta: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Sépare une ligne META en (pédagogique, gouvernance).

    Fail-closed : une clé inconnue est classée pédagogique.
    """
    pedagogical = {k: v for k, v in meta.items() if k not in GOVERNANCE_META_KEYS}
    governance = {k: v for k, v in meta.items() if k in GOVERNANCE_META_KEYS}
    return pedagogical, governance


def read_object_payload(root: Path, rel_path: str) -> tuple[dict[str, Any], str]:
    """Retourne (meta, corps) pour un objet. Le corps exclut la ligne META."""
    text = (root / rel_path).read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if not lines or not lines[0].startswith("% META:"):
        raise ValueError(f"objet sans ligne '% META:' : {rel_path}")
    meta = json.loads(lines[0][len("% META:"):].strip())
    return meta, "\n".join(lines[1:])


# --- L1 ----------------------------------------------------------------------

def object_set_digest(root: Path = ROOT) -> str:
    """Empreinte du seul *ensemble* d'identifiants couverts (aucun contenu)."""
    ids = sorted(o["id"] for o in load_canonical_objects(root))
    return _sha("\n".join(ids).encode("utf-8"))


def pedagogical_content_digest(root: Path = ROOT) -> str:
    """Empreinte de la charge didactique réellement soumise à acceptation.

    Inclut : le corps de chaque objet (cours, méthodes, exercices, corrigés,
    QCM, remédiations, évaluations, annexes, figures, barèmes) et les clés META
    pédagogiques. Exclut : GOVERNANCE_META_KEYS.

    Invariant : une transition de maturité ne déplace pas cette valeur.
    """
    entries: list[tuple[str, bytes]] = []
    for obj in load_canonical_objects(root):
        meta, body = read_object_payload(root, obj["path"])
        pedagogical, _ = split_meta(meta)
        canonical = json.dumps(pedagogical, sort_keys=True, ensure_ascii=False)
        entries.append((obj["id"], (canonical + "\n" + body).encode("utf-8")))
    return _merkle(entries)


def build_source_closure_digest(root: Path = ROOT) -> str:
    """Empreinte des octets de toutes les entrées réelles du build.

    Contrairement à PEDAGOGICAL_CONTENT_DIGEST, cette valeur *bouge*
    légitimement lors d'une transition de métadonnées.
    """
    entries: list[tuple[str, bytes]] = []
    for obj in load_canonical_objects(root):
        entries.append((obj["path"], (root / obj["path"]).read_bytes()))
    for pattern in ("gabarits/**/*.tex", "gabarits/**/*.sty", "gabarits/**/*.cls"):
        for path in sorted(root.glob(pattern)):
            if path.is_file():
                entries.append((str(path.relative_to(root)), path.read_bytes()))
    return _merkle(entries)


# --- L2 ----------------------------------------------------------------------

def acceptance_evidence_bundle_digest(root: Path = ROOT) -> str:
    """Empreinte immuable des preuves *pré-décision*.

    Ne contient ni le reçu humain, ni un artefact qui change parce que le reçu
    existe. Toute tentative d'en ajouter un lève DigestScopeError.
    """
    assert_acyclic()
    entries: list[tuple[str, bytes]] = []
    for rel in ACCEPTANCE_EVIDENCE_ARTIFACTS:
        path = root / rel
        if not path.is_file():
            raise FileNotFoundError(f"preuve d'acceptation absente : {rel}")
        entries.append((rel, path.read_bytes()))
    return _merkle(entries)


# --- Acyclicité (§4.2) -------------------------------------------------------

def digest_dependency_graph() -> dict[str, list[str]]:
    """Graphe explicite des dépendances entre empreintes, par couche."""
    return {
        "OBJECT_SET_DIGEST": ["L0:inventory"],
        "PEDAGOGICAL_CONTENT_DIGEST": ["L0:object_bodies", "L0:pedagogical_meta"],
        "BUILD_SOURCE_CLOSURE_DIGEST": ["L0:object_bytes", "L0:templates"],
        "ACCEPTANCE_EVIDENCE_BUNDLE_DIGEST": list(ACCEPTANCE_EVIDENCE_ARTIFACTS),
        "PACKET": [
            "OBJECT_SET_DIGEST",
            "PEDAGOGICAL_CONTENT_DIGEST",
            "ACCEPTANCE_EVIDENCE_BUNDLE_DIGEST",
        ],
        "RECEIPT": ["PACKET"],
        "MATURITY_TRANSITION": ["RECEIPT"],
    }


def count_digest_dependency_cycles() -> int:
    """Nombre de cycles dans le graphe des empreintes. Doit valoir 0."""
    graph = digest_dependency_graph()
    colour: dict[str, int] = {}
    cycles = 0

    def visit(node: str) -> None:
        nonlocal cycles
        state = colour.get(node, 0)
        if state == 1:
            cycles += 1
            return
        if state == 2:
            return
        colour[node] = 1
        for dep in graph.get(node, []):
            if dep in graph:
                visit(dep)
        colour[node] = 2

    for node in graph:
        visit(node)
    return cycles


def assert_acyclic() -> None:
    """Refuse toute preuve d'acceptation dépendant de la décision à authentifier."""
    contaminated = sorted(set(ACCEPTANCE_EVIDENCE_ARTIFACTS) & DECISION_DEPENDENT_ARTIFACTS)
    if contaminated:
        raise DigestScopeError(
            "ACCEPTANCE_EVIDENCE_BUNDLE contient des artefacts post-décision : "
            + ", ".join(contaminated)
        )
    if count_digest_dependency_cycles() != 0:
        raise DigestScopeError("DIGEST_DEPENDENCY_CYCLES != 0")


def compute_all(root: Path = ROOT) -> dict[str, str]:
    """Les quatre empreintes canoniques, calculées par cette seule implémentation."""
    return {
        "OBJECT_SET_DIGEST": object_set_digest(root),
        "PEDAGOGICAL_CONTENT_DIGEST": pedagogical_content_digest(root),
        "BUILD_SOURCE_CLOSURE_DIGEST": build_source_closure_digest(root),
        "ACCEPTANCE_EVIDENCE_BUNDLE_DIGEST": acceptance_evidence_bundle_digest(root),
    }


if __name__ == "__main__":
    print(json.dumps(compute_all(), indent=2))
