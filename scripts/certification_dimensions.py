#!/usr/bin/env python3
"""Socle commun des quatre dimensions de certification sans producteur.

Le contrat expose sept dimensions et exige les sept `passed` pour
`publication_eligible`. Quatre — `mathematics`, `regulation`, `print`,
`visual` — n'étaient assignées nulle part : elles restaient `not_covered`, et
`release-strict` était insatisfiable par construction.

Ce module ne rend aucune dimension verte. Il fournit l'enveloppe de preuve que
le contrat exige (§18) : chaque producteur doit déclarer sa portée, son statut,
le HEAD sur lequel la preuve a été calculée, l'empreinte de ses entrées, sa
version et ses constats. Le gate compare ensuite `evidence_head` au HEAD
candidat : une preuve ancienne ne peut pas verdir une dimension.

`NOT_APPLICABLE` n'est jamais synonyme de `PASS`. Une dimension hors champ pour
une cible donnée le déclare cible par cible, et le statut global reste
`failed` dès qu'un constat bloquant subsiste.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]

STATUSES = ("passed", "failed", "not_covered")


def current_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def relative_paths(paths: Iterable[Path], root: Path = ROOT) -> list[str]:
    """Chemins déclarés, relatifs au dépôt quand c'est possible."""
    out = []
    for path in sorted(set(paths)):
        try:
            out.append(str(path.relative_to(root)))
        except ValueError:
            out.append(str(path))
    return out


def digest_inputs(paths: Iterable[Path], root: Path = ROOT) -> str:
    """Empreinte ordonnée des entrées réellement lues par un producteur.

    Les entrées sont nommées relativement à `root` : c'est ce nom que le gate
    réutilisera pour revérifier la fraîcheur, et les deux calculs doivent
    porter sur exactement la même chaîne.
    """
    acc = hashlib.sha256()
    for path in sorted(paths):
        try:
            rel = str(path.relative_to(root))
        except ValueError:
            # Entrée hors de la racine : on la nomme telle quelle plutôt que
            # d'échouer.
            rel = str(path)
        acc.update(rel.encode("utf-8"))
        acc.update(b"\x00")
        if path.is_file():
            acc.update(hashlib.sha256(path.read_bytes()).digest())
        else:
            acc.update(b"ABSENT")
        acc.update(b"\x00")
    return "sha256:" + acc.hexdigest()


@dataclass
class Finding:
    """Un constat bloquant ou non, toujours rattaché à une cible précise."""

    target: str
    code: str
    detail: str
    blocking: bool = True


@dataclass
class DimensionEvidence:
    """Enveloppe de preuve exigée par le contrat (§18)."""

    dimension: str
    scope: str
    producer: str
    producer_version: str
    evidence_head: str
    input_digest: str
    input_paths: list[str] = field(default_factory=list)
    coverage: dict[str, Any] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    not_applicable_targets: dict[str, str] = field(default_factory=dict)

    @property
    def status(self) -> str:
        """`passed` seulement en l'absence de constat bloquant.

        Un producteur qui n'a rien pu mesurer ne renvoie pas `passed` : il doit
        avoir déclaré un constat bloquant ou une couverture nulle.
        """
        if any(f.blocking for f in self.findings):
            return "failed"
        if not self.coverage.get("targets_examined"):
            return "failed"
        return "passed"

    def to_payload(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "scope": self.scope,
            "producer": self.producer,
            "producer_version": self.producer_version,
            "status": self.status,
            "evidence_head": self.evidence_head,
            "input_digest": self.input_digest,
            "input_paths": self.input_paths,
            "coverage": self.coverage,
            "not_applicable_targets": self.not_applicable_targets,
            "blocking_findings": sum(1 for f in self.findings if f.blocking),
            "findings": [asdict(f) for f in self.findings],
        }


def render_evidence(evidence: DimensionEvidence) -> dict[str, Any]:
    """Le contenu de la preuve, sans la deposer.

    Separer le calcul de la publication n'est pas une elegance : un `build()`
    qui ecrit publie tout ce qui l'appelle, y compris un test au milieu d'une
    mutation, et un `--check` qui ecrit efface la derive qu'il mesure.
    """
    return {
        "artifact_type": "certification_dimension_evidence",
        "schema_version": 1,
        **evidence.to_payload(),
    }


def write_evidence(evidence: DimensionEvidence, output: Path) -> dict[str, Any]:
    payload = render_evidence(evidence)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def evidence_is_fresh(payload: dict[str, Any], root: Path = ROOT) -> bool:
    """Une preuve est fraîche tant que ses entrées déclarées n'ont pas bougé.

    On ne compare pas au HEAD git : committer l'artefact de preuve déplace le
    HEAD et invaliderait la preuve à l'instant même où on l'enregistre. Ce qui
    compte est que les octets mesurés soient toujours ceux du dépôt — d'où la
    revérification de `input_digest` sur les chemins que le producteur déclare
    avoir lus.
    """
    paths = payload.get("input_paths") or []
    if not paths:
        return False
    recomputed = digest_inputs([root / p for p in paths], root)
    return recomputed == payload.get("input_digest")
