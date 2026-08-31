#!/usr/bin/env python3
"""Identite canonique d'une capacite, resolue par egalite, jamais par ressemblance.

Une capacite n'est pas un numero. `C1` seul ne designe rien : chaque chapitre
de la collection en possede un. L'identite d'une capacite est le triplet

    (manuel, chapitre, code local)

et rien de moins. Deux capacites qui portent le meme code local dans deux
chapitres differents sont deux capacites differentes.

CE QUE CE MODULE INTERDIT.

Le defaut qu'il repare extrayait un jeton local d'une reference pleinement
qualifiee : `TSPE-CONCLGN-C1` etait lu comme `C1`. Or dans
`TSPE-PROBABILITES` cette reference designe la capacite locale `C10`, tandis
que `C1` designe une autre capacite du meme chapitre. L'extraction faisait
donc crediter le contenu d'une capacite a sa voisine.

Aucune relation d'identite ne peut donc reposer ici sur :

* un suffixe (`...-C1` vaut `C1`) ;
* une inclusion (`contains("C1")`) ;
* une expression reguliere qui extrait un `C<n>` final ;
* la proximite lexicale de deux chaines.

QUATRE REGLES, TOUTES EXACTES.

`REF_EXACT`
    La chaine declaree est EGALE a la `ref_capacite` d'une capacite du
    contrat du chapitre. C'est le cas de `P-ALGO-01A` et de
    `TSPE-CONCLGN-C1`.

`LOCAL_IN_SCOPE`
    La chaine declaree est EGALE au code local d'une capacite du contrat DU
    CHAPITRE DE L'OBJET. Jamais d'un autre : la portee est le chapitre.

`SCOPED_QUALIFIED`
    La chaine declaree est EGALE a `f"{chapitre}-{code local}"`. La partie
    qualifiante est presente et nomme le chapitre de l'objet lui-meme. Ce
    n'est pas un suffixe reconnu : c'est une egalite avec une clef construite
    dans la portee de l'objet.

`PREREQUISITE_NOT_CAPACITY`
    La chaine designe un prerequis declare par le contrat. Un prerequis
    n'est pas une capacite du chapitre et ne credite rien.

En dehors de ces quatre cas, la resolution ECHOUE. Il n'y a pas de
« meilleur effort » : une capacite mal resolue fabrique soit une lacune
inexistante, soit un credit vole a la capacite voisine, et ces deux erreurs
coutent aussi cher l'une que l'autre.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CORPORA = (
    ROOT / "Mathematiques" / "manuel-maths" / "chapitres",
    ROOT / "NSI" / "chapitres",
)
UNPUBLISHED = ("_harvest",)

REF_EXACT = "REF_EXACT"
LOCAL_IN_SCOPE = "LOCAL_IN_SCOPE"
SCOPED_QUALIFIED = "SCOPED_QUALIFIED"
PREREQUISITE = "PREREQUISITE_NOT_CAPACITY"
RULES = (REF_EXACT, LOCAL_IN_SCOPE, SCOPED_QUALIFIED, PREREQUISITE)


class CapacityIdentityError(Exception):
    """Echec de resolution. Toujours bloquant, jamais rattrape."""


class AmbiguousCapacityIdentity(CapacityIdentityError):
    """La chaine designe plusieurs capacites distinctes."""


class UnresolvedCapacityIdentity(CapacityIdentityError):
    """La chaine ne designe aucune capacite du contrat."""


def normalise(raw: Any) -> str:
    """Normalisation SURE : espaces de bord uniquement.

    La casse n'est pas normalisee et la partie qualifiante n'est jamais
    retiree. `TSPE-CONCLGN-C1` ne devient pas `C1` : le qualifiant PORTE de
    l'information d'identite, et l'oter est precisement le defaut repare ici.
    """

    return str(raw).strip()


@dataclass(frozen=True)
class CapacityIdentity:
    """Identite pleinement qualifiee d'une capacite contractuelle."""

    manual: str
    chapter: str
    local_code: str
    official_ref: str | None

    @property
    def uid(self) -> str:
        return f"{self.manual}::{self.chapter}::{self.local_code}"


@dataclass(frozen=True)
class Resolution:
    identity: CapacityIdentity
    rule: str


def manual_of(chapter: str) -> str:
    for prefix in ("TEXPERTES", "TEXP", "TCOMPL", "TNSI", "TSPE", "1NSI", "1SPE"):
        if chapter.startswith(prefix):
            return "TEXPERTES" if prefix in {"TEXP", "TEXPERTES"} else prefix
    return "UNKNOWN"


class CapacityIdentityResolver:
    """Table autoritaire derivee des contrats. Aucune inference lexicale."""

    def __init__(self, contracts: dict[str, dict[str, Any]]) -> None:
        self._chapters = contracts

    # -- construction ----------------------------------------------------

    @classmethod
    def from_corpora(cls, corpora: tuple[Path, ...] = CORPORA):
        contracts: dict[str, dict[str, Any]] = {}
        for corpus in corpora:
            if not corpus.is_dir():
                continue
            for directory in sorted(corpus.iterdir()):
                contract = directory / "contrat.yaml"
                if not contract.is_file():
                    continue
                contracts[directory.name] = cls._read_contract(
                    directory.name, contract
                )
        return cls(contracts)

    @staticmethod
    def _read_contract(chapter: str, path: Path) -> dict[str, Any]:
        document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        manual = manual_of(chapter)
        by_local: dict[str, CapacityIdentity] = {}
        by_ref: dict[str, CapacityIdentity] = {}
        for entry in document.get("capacites") or []:
            code = normalise(entry.get("code"))
            if not code:
                raise CapacityIdentityError(f"{chapter}: capacite sans code")
            if code in by_local:
                raise AmbiguousCapacityIdentity(
                    f"{chapter}: code local {code} declare deux fois"
                )
            reference = entry.get("ref_capacite")
            reference = normalise(reference) if reference else None
            identity = CapacityIdentity(manual, chapter, code, reference)
            by_local[code] = identity
            if reference is not None:
                # Un alias doit etre un-vers-un. Deux capacites qui
                # partageraient une meme reference officielle rendraient tout
                # credit indecidable : on echoue plutot que de choisir.
                if reference in by_ref:
                    raise AmbiguousCapacityIdentity(
                        f"{chapter}: reference {reference} partagee par "
                        f"{by_ref[reference].local_code} et {code}"
                    )
                by_ref[reference] = identity
        # Une reference qui vaut aussi un code local rendrait la meme chaine
        # resoluble vers deux capacites differentes.
        for reference, identity in by_ref.items():
            other = by_local.get(reference)
            if other is not None and other.local_code != identity.local_code:
                raise AmbiguousCapacityIdentity(
                    f"{chapter}: {reference} est a la fois la reference de "
                    f"{identity.local_code} et le code local de "
                    f"{other.local_code}"
                )
        prerequisites = {
            normalise(entry.get("code"))
            for entry in (document.get("prerequis") or [])
            if entry.get("code")
        }
        return {"local": by_local, "ref": by_ref, "prerequisites": prerequisites}

    # -- resolution ------------------------------------------------------

    @property
    def chapters(self) -> tuple[str, ...]:
        return tuple(sorted(self._chapters))

    def capacities_of(self, chapter: str) -> tuple[CapacityIdentity, ...]:
        contract = self._chapters.get(chapter)
        if contract is None:
            return ()
        return tuple(contract["local"][code] for code in contract["local"])

    def resolve(self, chapter: str, raw: Any) -> Resolution:
        """Resout une declaration DANS LA PORTEE de son chapitre.

        Jamais globalement : `C1` ne peut designer que le `C1` du chapitre de
        l'objet qui le declare.
        """

        contract = self._chapters.get(chapter)
        if contract is None:
            raise UnresolvedCapacityIdentity(f"chapitre sans contrat: {chapter}")
        value = normalise(raw)
        if not value:
            raise UnresolvedCapacityIdentity(f"{chapter}: declaration vide")

        candidates: list[Resolution] = []
        identity = contract["ref"].get(value)
        if identity is not None:
            candidates.append(Resolution(identity, REF_EXACT))
        identity = contract["local"].get(value)
        if identity is not None:
            candidates.append(Resolution(identity, LOCAL_IN_SCOPE))
        prefix = f"{chapter}-"
        if value.startswith(prefix):
            identity = contract["local"].get(value[len(prefix) :])
            if identity is not None:
                candidates.append(Resolution(identity, SCOPED_QUALIFIED))

        distinct = {resolution.identity for resolution in candidates}
        if len(distinct) > 1:
            raise AmbiguousCapacityIdentity(
                f"{chapter}: {value} designe "
                f"{sorted(item.local_code for item in distinct)}"
            )
        if candidates:
            return candidates[0]
        if value in contract["prerequisites"]:
            placeholder = CapacityIdentity(manual_of(chapter), chapter, value, None)
            return Resolution(placeholder, PREREQUISITE)
        raise UnresolvedCapacityIdentity(f"{chapter}: {value} ne designe aucune capacite")

    def resolve_codes(self, chapter: str, raws: list[Any]) -> tuple[str, ...]:
        """Codes locaux credites. Les prerequis ne creditent rien."""

        codes: list[str] = []
        for raw in raws:
            resolution = self.resolve(chapter, raw)
            if resolution.rule == PREREQUISITE:
                continue
            if resolution.identity.local_code not in codes:
                codes.append(resolution.identity.local_code)
        return tuple(codes)


def build_alias_map() -> dict[str, Any]:
    """Table d'alias autoritaire, derivee des contrats et un-vers-un."""

    resolver = CapacityIdentityResolver.from_corpora()
    rows: list[dict[str, Any]] = []
    for chapter in resolver.chapters:
        for identity in resolver.capacities_of(chapter):
            rows.append(
                {
                    "canonical_uid": identity.uid,
                    "manual": identity.manual,
                    "chapter": identity.chapter,
                    "local_scoped_key": f"{identity.chapter}-{identity.local_code}",
                    "local_code": identity.local_code,
                    "official_ref": identity.official_ref,
                }
            )
    uids = [row["canonical_uid"] for row in rows]
    if len(set(uids)) != len(uids):
        raise AmbiguousCapacityIdentity("uid canonique duplique")
    return {
        "artifact_type": "capacity_alias_map",
        "schema_version": 1,
        "generated_by": "scripts/capacity_identity.py",
        "identity_rule": (
            "une capacite est identifiee par (manuel, chapitre, code local) ; "
            "aucune relation d'identite ne repose sur un suffixe, une "
            "inclusion ou une extraction de jeton"
        ),
        "resolution_rules": list(RULES),
        "normalisation": "espaces de bord uniquement ; le qualifiant n'est jamais retire",
        "count": len(rows),
        "chapters": len(resolver.chapters),
        "alias_digest": "sha256:"
        + hashlib.sha256(
            json.dumps(sorted(uids), separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "entries": rows,
    }


OUTPUT = ROOT / "audit/CAPACITY_ALIAS_MAP.json"


def render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    rendered = render(build_alias_map())
    if arguments.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
        if current != rendered:
            print(f"STALE: {OUTPUT.relative_to(ROOT)}")
            return 1
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}: {json.loads(rendered)['count']} capacites")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
