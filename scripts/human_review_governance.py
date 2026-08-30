#!/usr/bin/env python3
"""Contrat de revue humaine des chapitres geles (Manuels Nexus).

Cette machine ne rend jamais un verdict. Elle sait seulement :

* enumerer l'ensemble gele des objets publishables d'un chapitre ;
* deriver les digests canoniques (OBJECT_SET, SEMANTIC_REVIEW, REVIEW_RENDER,
  PROGRAMME_AUTHORITY, PACKET) ;
* preparer les deux packets humains A et B ;
* valider un recu humain reellement recu et refuser toute mutation ;
* calculer la fraicheur (CURRENT / STALE) d'un recu ;
* deriver l'etat de revue d'un chapitre sans jamais l'approuver.

Le contrat de reference est audit/HUMAN_REVIEW_GOVERNANCE.yaml.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = Path("audit/HUMAN_REVIEW_GOVERNANCE.yaml")
RECEIPT_SCHEMA_PATH = Path("audit/schemas/v1/human-review-receipt.schema.json")
#: Sources d'autorite programme, par ordre de preseance. La premiere est celle
#: qu'utilise le producteur canonique du gel Suites ; la seconde n'existe que
#: dans le WIP non commite et ne peut donc pas lier un gel reproductible.
PROGRAMME_AUTHORITY_SOURCES = (
    Path("audit/OFFICIAL_PROGRAM_AUTHORITY_2026_2027.yaml"),
    Path("audit/OFFICIAL_AUTHORITIES_2026_2027.json"),
)
#: Cle du manuel dans chaque source, quand elle differe de l'identifiant local.
AUTHORITY_MANUAL_ALIASES = {"TEXP": ("TEXPERTES",), "TSPE": ("TSPE_2026_2027", "TSPE")}
REVIEW_ROOT = Path("audit/reviews/human")

META_RE = re.compile(r"^% META:\s*(\{.*\})\s*$", re.MULTILINE)
#: Un objet peut en inclure d'autres : l'inclusion transitive est publiee, donc
#: elle appartient a l'ensemble gele et doit etre couverte par la revue.
INPUT_RE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
RFC3339_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)

def _exclusion_allowlist(root: Path) -> tuple[frozenset[str], frozenset[str]]:
    """Allowlist explicite des champs exclus du digest semantique.

    L'exclusion n'est pas une convention du code : elle est declaree dans
    audit/HUMAN_REVIEW_GOVERNANCE.yaml et verrouillee par le schema du contrat.
    Elargir l'exclusion exige donc de modifier le contrat ET son schema, jamais
    seulement le code. Aucune exclusion implicite n'est possible.
    """

    document = yaml.safe_load(
        (root / POLICY_PATH).read_text(encoding="utf-8")
    )
    allowlist = document["digests"]["semantic_review_digest"][
        "governance_exclusion_allowlist"
    ]
    return (
        frozenset(allowlist["meta_fields"]),
        frozenset(allowlist["contract_fields"]),
    )


#: Champs purement de gouvernance : ils sont ce que la revue fait evoluer. Les
#: inclure dans le digest semantique rendrait tout recu STALE au moment exact de
#: la promotion qu'il autorise. Toute autre donnee reste dans le digest.
GOVERNANCE_META_FIELDS, GOVERNANCE_CONTRACT_FIELDS = _exclusion_allowlist(ROOT)

#: Racines de manuels connues, dans l'ordre de resolution.
MANUAL_ROOTS: dict[str, tuple[str, str]] = {
    "1SPE": ("Mathematiques/manuel-maths", "MATH"),
    "TSPE": ("Mathematiques/manuel-maths", "MATH"),
    "TCOMPL": ("Mathematiques/manuel-maths", "MATH"),
    "TEXP": ("Mathematiques/manuel-maths", "MATH"),
    "1NSI": ("NSI", "NSI"),
    "TNSI": ("NSI", "NSI"),
}

STYLE_ONLY_SUFFIXES = frozenset({".cls", ".sty"})


class HumanReviewViolation(ValueError):
    """Levee des qu'une regle du contrat de revue humaine est enfreinte."""


# --------------------------------------------------------------------------
# Primitives deterministes
# --------------------------------------------------------------------------


def canonical_json(payload: Any) -> str:
    """Serialisation canonique : cles triees, UTF-8, sans espace superflu."""

    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest_payload(payload: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def digest_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def normalise_text(text: str) -> str:
    """Normalise un source texte sans en alterer la substance semantique."""

    lines = [line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def load_policy(root: Path = ROOT) -> dict[str, Any]:
    return yaml.safe_load((root / POLICY_PATH).read_text(encoding="utf-8"))


def repository_source_sha(root: Path = ROOT) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


# --------------------------------------------------------------------------
# Resolution du manuel et de son assembleur
# --------------------------------------------------------------------------


def manual_of_chapter(chapter_id: str) -> str:
    for prefix in MANUAL_ROOTS:
        if chapter_id.startswith(prefix + "-"):
            return prefix
    raise HumanReviewViolation(f"Manuel indeterminable pour le chapitre {chapter_id!r}")


def discipline_of_manual(manual_id: str) -> str:
    return MANUAL_ROOTS[manual_id][1]


def chapter_directory(chapter_id: str, root: Path = ROOT) -> Path:
    manual_root = root / MANUAL_ROOTS[manual_of_chapter(chapter_id)][0]
    chapter_dir = manual_root / "chapitres" / chapter_id
    if not chapter_dir.is_dir():
        raise HumanReviewViolation(f"Chapitre introuvable : {chapter_dir}")
    return chapter_dir


def _load_assembler(manual_id: str, root: Path = ROOT) -> Any:
    scripts_dir = root / MANUAL_ROOTS[manual_id][0] / "scripts"
    module_path = scripts_dir / "assemble_manuel.py"
    if not module_path.is_file():
        raise HumanReviewViolation(f"Assembleur introuvable : {module_path}")
    spec = importlib.util.spec_from_file_location(
        f"_nexus_assembler_{manual_id}", module_path
    )
    if spec is None or spec.loader is None:
        raise HumanReviewViolation(f"Assembleur non chargeable : {module_path}")
    module = importlib.util.module_from_spec(spec)
    inserted = str(scripts_dir)
    # L'assembleur importe ses voisins par nom court (common, pdf_integrity).
    # Ces noms sont partages entre les manuels : les laisser dans sys.modules
    # ferait resoudre l'assembleur NSI vers le common des mathematiques.
    preexisting = set(sys.modules)
    sys.path.insert(0, inserted)
    # Le module doit figurer dans sys.modules AVANT son execution : @dataclass
    # resout ses annotations via sys.modules[cls.__module__], et un module
    # absent y vaut None. L'assembleur NSI, qui declare une dataclass, echouait
    # ainsi sur "'NoneType' object has no attribute '__dict__'" et rendait ses
    # dix-sept chapitres impossibles a gouverner.
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        if sys.path and sys.path[0] == inserted:
            sys.path.pop(0)
        sys.modules.pop(spec.name, None)
        for name in set(sys.modules) - preexisting:
            origin = getattr(sys.modules[name], "__file__", None)
            if origin and Path(origin).parent == scripts_dir:
                del sys.modules[name]
    return module


@dataclass(frozen=True)
class VariantRules:
    """Regles de variante affectant le contenu eleve/professeur."""

    order: tuple[tuple[str, str], ...]
    eleve_excludes: tuple[str, ...]
    eleve_allowed_types: tuple[str, ...]

    def as_payload(self) -> dict[str, Any]:
        return {
            "assembly_rules": [list(rule) for rule in self.order],
            "eleve_excluded_sections": list(self.eleve_excludes),
            "eleve_allowed_types": list(self.eleve_allowed_types),
        }


def variant_rules(manual_id: str, root: Path = ROOT) -> VariantRules:
    module = _load_assembler(manual_id, root)
    try:
        order = tuple((str(a), str(b)) for a, b in module.ORDER)
        excludes = tuple(sorted(str(item) for item in module.ELEVE_EXCLUDES))
        allowed = tuple(sorted(str(item) for item in module.ELEVE_ALLOWED_TYPES))
    except AttributeError as error:  # pragma: no cover - assembleur non conforme
        raise HumanReviewViolation(
            f"Assembleur {manual_id} sans constantes de variante exploitables"
        ) from error
    return VariantRules(order=order, eleve_excludes=excludes, eleve_allowed_types=allowed)


# --------------------------------------------------------------------------
# Enumeration de l'ensemble gele
# --------------------------------------------------------------------------


@dataclass
class ChapterObject:
    object_id: str
    object_type: str
    section: str
    path: str
    capabilities: tuple[str, ...]
    meta: dict[str, Any]
    source_sha256: str
    included_by: str | None = None
    student_visible: bool = False
    teacher_visible: bool = False
    student_index: int | None = None
    teacher_index: int | None = None

    def identity_payload(self) -> dict[str, Any]:
        return {
            "object_id": self.object_id,
            "object_type": self.object_type,
            "section": self.section,
            "path": self.path,
        }

    def semantic_payload(self) -> dict[str, Any]:
        return {
            "object_id": self.object_id,
            "object_type": self.object_type,
            "section": self.section,
            "path": self.path,
            "capabilities": list(self.capabilities),
            "included_by": self.included_by,
            "meta": self.meta,
            "source_sha256": self.source_sha256,
            "student_visible": self.student_visible,
            "teacher_visible": self.teacher_visible,
            "student_index": self.student_index,
            "teacher_index": self.teacher_index,
        }


def _read_meta(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    matches = META_RE.findall(text)
    if len(matches) != 1:
        raise HumanReviewViolation(f"META absente ou ambigue : {path}")
    payload = json.loads(matches[0])
    if not isinstance(payload, dict):
        raise HumanReviewViolation(f"META non-objet : {path}")
    return payload


def _semantic_meta(meta: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in meta.items() if key not in GOVERNANCE_META_FIELDS}


def _semantic_source(path: Path, meta: dict[str, Any]) -> str:
    """Source normalise dont la ligne META est reduite a ses champs semantiques."""

    text = normalise_text(path.read_text(encoding="utf-8"))
    canonical_meta = "% META: " + canonical_json(_semantic_meta(meta))
    return META_RE.sub(lambda _match: canonical_meta, text, count=1)


def _capabilities(meta: dict[str, Any]) -> tuple[str, ...]:
    for key in ("capacites_codes", "capacites", "capacite"):
        value = meta.get(key)
        if isinstance(value, list):
            return tuple(sorted(str(item) for item in value))
        if isinstance(value, str):
            return (value,)
    return ()


def _glob_rule(chapter_dir: Path, section: str, pattern: str) -> list[Path]:
    suffix = pattern + ".tex" if pattern.endswith("*") else f"{pattern}.tex"
    return sorted((chapter_dir / section).glob(suffix))


def assembly_sequence(
    chapter_dir: Path,
    rules: VariantRules,
    variant: str,
    object_types: dict[Path, str],
) -> list[Path]:
    """Replique l'ordre d'assemblage reel pour une variante donnee."""

    if variant not in {"eleve", "professeur"}:
        raise HumanReviewViolation(f"Variante inconnue : {variant}")
    student = variant == "eleve"
    files: list[Path] = []
    for section, pattern in rules.order:
        if student and section in rules.eleve_excludes:
            continue
        candidates = _glob_rule(chapter_dir, section, pattern)
        if section == "exercices":
            files += [path for path in candidates if not path.name.endswith("-CDP.tex")]
            files += [path for path in candidates if path.name.endswith("-CDP.tex")]
        elif section == "evaluations" and student:
            files += [path for path in candidates if "corrige" not in path.name]
        else:
            files += candidates
    if student:
        files = [
            path
            for path in files
            if object_types.get(path, "") in rules.eleve_allowed_types
        ]
    seen: set[Path] = set()
    ordered: list[Path] = []
    for path in files:
        if path not in seen:
            seen.add(path)
            ordered.append(path)
    return ordered


def _inclusion_edges(
    objects: dict[Path, "ChapterObject"], manual_root: Path
) -> dict[Path, Path]:
    """Arete d'inclusion : quel objet en insere un autre par \\input."""

    edges: dict[Path, Path] = {}
    for parent_path in objects:
        text = parent_path.read_text(encoding="utf-8")
        for match in INPUT_RE.finditer(text):
            target = match.group(1).strip()
            if not target.endswith(".tex"):
                target += ".tex"
            for candidate in (manual_root / target, parent_path.parent / target):
                resolved = candidate.resolve()
                if resolved in objects and resolved != parent_path:
                    edges.setdefault(resolved, parent_path)
                    break
    return edges


def _expand_inclusions(
    sequence: list[Path], included_by: dict[Path, Path]
) -> list[Path]:
    """Insere chaque objet inclus juste apres l'objet qui l'insere."""

    children: dict[Path, list[Path]] = {}
    for child, parent in included_by.items():
        children.setdefault(parent, []).append(child)
    for values in children.values():
        values.sort()

    expanded: list[Path] = []

    def emit(path: Path) -> None:
        expanded.append(path)
        for child in children.get(path, ()):
            emit(child)

    for path in sequence:
        emit(path)
    return expanded


def enumerate_objects(
    chapter_id: str,
    root: Path = ROOT,
    rules: VariantRules | None = None,
) -> list[ChapterObject]:
    """Enumere l'ensemble exact et immuable des objets publishables."""

    chapter_dir = chapter_directory(chapter_id, root)
    manual_id = manual_of_chapter(chapter_id)
    rules = rules or variant_rules(manual_id, root)
    sections = {section for section, _ in rules.order}

    objects: dict[Path, ChapterObject] = {}
    object_types: dict[Path, str] = {}
    for section in sorted(sections):
        section_dir = chapter_dir / section
        if not section_dir.is_dir():
            continue
        for path in sorted(section_dir.rglob("*.tex")):
            meta = _read_meta(path)
            object_id = meta.get("id")
            object_type = meta.get("type_objet")
            if not isinstance(object_id, str) or not object_id:
                raise HumanReviewViolation(f"META.id invalide : {path}")
            if not isinstance(object_type, str) or not object_type:
                raise HumanReviewViolation(f"META.type_objet invalide : {path}")
            object_types[path] = object_type
            objects[path.resolve()] = ChapterObject(
                object_id=object_id,
                object_type=object_type,
                section=section,
                path=path.relative_to(root).as_posix(),
                capabilities=_capabilities(meta),
                meta=_semantic_meta(meta),
                source_sha256=digest_bytes(_semantic_source(path, meta).encode("utf-8")),
            )

    manual_root = chapter_dir.parents[1]
    included_by = _inclusion_edges(objects, manual_root)
    for path, parent in included_by.items():
        objects[path].included_by = objects[parent].object_id

    for variant in ("eleve", "professeur"):
        sequence = _expand_inclusions(
            [
                item.resolve()
                for item in assembly_sequence(chapter_dir, rules, variant, object_types)
            ],
            included_by,
        )
        for index, path in enumerate(sequence):
            entry = objects.get(path)
            if entry is None:  # pragma: no cover - un .tex assemble sans META
                raise HumanReviewViolation(f"Objet assemble hors inventaire : {path}")
            if variant == "eleve":
                entry.student_visible = True
                entry.student_index = index
            else:
                entry.teacher_visible = True
                entry.teacher_index = index

    ordered = sorted(objects.values(), key=lambda entry: (entry.object_id, entry.path))
    identifiers = [entry.object_id for entry in ordered]
    duplicates = sorted({name for name in identifiers if identifiers.count(name) > 1})
    if duplicates:
        raise HumanReviewViolation(f"object_id dupliques : {duplicates}")
    return ordered


# --------------------------------------------------------------------------
# Sources semantiques annexes
# --------------------------------------------------------------------------


def contract_payload(chapter_id: str, root: Path = ROOT) -> dict[str, Any]:
    path = chapter_directory(chapter_id, root) / "contrat.yaml"
    if not path.is_file():
        raise HumanReviewViolation(f"Contrat de chapitre absent : {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise HumanReviewViolation(f"Contrat de chapitre non-objet : {path}")
    return {key: value for key, value in data.items() if key not in GOVERNANCE_CONTRACT_FIELDS}


def qcm_payload(chapter_id: str, root: Path = ROOT) -> dict[str, Any]:
    qcm_dir = chapter_directory(chapter_id, root) / "qcm"
    sources = sorted(qcm_dir.glob("*.json")) if qcm_dir.is_dir() else []
    return {
        path.relative_to(root).as_posix(): json.loads(path.read_text(encoding="utf-8"))
        for path in sources
    }


def qcm_question_ids(chapter_id: str, root: Path = ROOT) -> list[str]:
    identifiers: list[str] = []
    for source, payload in sorted(qcm_payload(chapter_id, root).items()):
        for question in payload.get("questions", []):
            identifiers.append(f"{source}#{question.get('id')}")
    return identifiers


def programme_mapping_payload(chapter_id: str, root: Path = ROOT) -> dict[str, Any]:
    """Referentiel de capacites officiel rattache au chapitre."""

    manual_id = manual_of_chapter(chapter_id)
    referentiel = root / MANUAL_ROOTS[manual_id][0] / "referentiel"
    if not referentiel.is_dir():
        return {}
    theme = chapter_id[len(manual_id) + 1 :]
    candidates = {
        f"capacites_{manual_id}_{theme}.json",
        f"capacites_{manual_id}_{theme.replace('-', '_')}.json",
    }
    if manual_id == "TEXP":
        candidates |= {
            f"capacites_TEXPERTES_{theme}.json",
            f"capacites_TEXPERTES_{theme.replace('-', '_')}.json",
        }
    payload: dict[str, Any] = {}
    for name in sorted(candidates):
        path = referentiel / name
        if path.is_file():
            payload[path.relative_to(root).as_posix()] = json.loads(
                path.read_text(encoding="utf-8")
            )
    return payload


def _authority_keys(manual_id: str) -> tuple[str, ...]:
    return (manual_id, *AUTHORITY_MANUAL_ALIASES.get(manual_id, ()))


def programme_authority_payload(chapter_id: str, root: Path = ROOT) -> dict[str, Any]:
    """Autorite programme applicable, lue dans la source de plus haute preseance.

    Le packet enregistre quelle source a ete lue : lier un gel a un artefact non
    commite le rendrait irreproductible.
    """

    manual_id = manual_of_chapter(chapter_id)
    for source in PROGRAMME_AUTHORITY_SOURCES:
        path = root / source
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        document = (
            json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)
        )
        namespace = document.get("programme_d_enseignement") or {
            key: value.get("PROGRAMME_D_ENSEIGNEMENT")
            for key, value in document.get("manuals", {}).items()
        }
        for key in _authority_keys(manual_id):
            entry = namespace.get(key)
            if entry is not None:
                return {
                    "authority_source": source.as_posix(),
                    "manual": key,
                    "PROGRAMME_D_ENSEIGNEMENT": entry,
                }
    raise HumanReviewViolation(
        f"Autorite programme introuvable pour {manual_id} dans "
        + ", ".join(item.as_posix() for item in PROGRAMME_AUTHORITY_SOURCES)
    )


def programme_authority_digest(chapter_id: str, root: Path = ROOT) -> str:
    return digest_payload(
        {
            "algorithm": "NEXUS_PROGRAMME_AUTHORITY_DIGEST_V1",
            "authority": programme_authority_payload(chapter_id, root),
        }
    )


# --------------------------------------------------------------------------
# Digests contractuels
# --------------------------------------------------------------------------


def object_set_digest(objects: list[ChapterObject]) -> str:
    return digest_payload(
        {
            "algorithm": "NEXUS_OBJECT_SET_DIGEST_V1",
            "objects": [entry.identity_payload() for entry in objects],
        }
    )


@dataclass
class ChapterScope:
    """Vue semantique gelee d'un chapitre, independante de tout rendu."""

    chapter_id: str
    manual_id: str
    discipline: str
    objects: list[ChapterObject]
    contract: dict[str, Any]
    qcm: dict[str, Any]
    programme_mapping: dict[str, Any]
    programme_authority: dict[str, Any]
    rules: VariantRules

    @property
    def object_count(self) -> int:
        return len(self.objects)

    @property
    def object_ids(self) -> tuple[str, ...]:
        return tuple(entry.object_id for entry in self.objects)

    @property
    def object_set_digest(self) -> str:
        return object_set_digest(self.objects)

    @property
    def programme_authority_digest(self) -> str:
        return digest_payload(
            {
                "algorithm": "NEXUS_PROGRAMME_AUTHORITY_DIGEST_V1",
                "authority": self.programme_authority,
            }
        )

    def semantic_payload(self) -> dict[str, Any]:
        return {
            "algorithm": "NEXUS_SEMANTIC_REVIEW_DIGEST_V1",
            "chapter_id": self.chapter_id,
            "manual_id": self.manual_id,
            "object_set_digest": self.object_set_digest,
            "objects": [entry.semantic_payload() for entry in self.objects],
            "contract": self.contract,
            "qcm": self.qcm,
            "programme_mapping": self.programme_mapping,
            "programme_authority": self.programme_authority,
            "assembly_order": {
                "eleve": [
                    entry.object_id
                    for entry in sorted(
                        (item for item in self.objects if item.student_index is not None),
                        key=lambda item: item.student_index or 0,
                    )
                ],
                "professeur": [
                    entry.object_id
                    for entry in sorted(
                        (item for item in self.objects if item.teacher_index is not None),
                        key=lambda item: item.teacher_index or 0,
                    )
                ],
            },
            "variant_rules": self.rules.as_payload(),
        }

    @property
    def semantic_review_digest(self) -> str:
        return digest_payload(self.semantic_payload())

    def unassembled_object_ids(self) -> list[str]:
        return [
            entry.object_id
            for entry in self.objects
            if not entry.student_visible and not entry.teacher_visible
        ]


def build_scope(chapter_id: str, root: Path = ROOT) -> ChapterScope:
    manual_id = manual_of_chapter(chapter_id)
    rules = variant_rules(manual_id, root)
    return ChapterScope(
        chapter_id=chapter_id,
        manual_id=manual_id,
        discipline=discipline_of_manual(manual_id),
        objects=enumerate_objects(chapter_id, root, rules),
        contract=contract_payload(chapter_id, root),
        qcm=qcm_payload(chapter_id, root),
        programme_mapping=programme_mapping_payload(chapter_id, root),
        programme_authority=programme_authority_payload(chapter_id, root),
        rules=rules,
    )


def render_digest(render_paths: list[str], root: Path = ROOT) -> str:
    """Digest des rendus examines, strictement disjoint du digest semantique."""

    entries = []
    for relative in sorted(set(render_paths)):
        path = root / relative
        if not path.is_file():
            raise HumanReviewViolation(f"Rendu introuvable : {relative}")
        entries.append({"path": relative, "sha256": digest_bytes(path.read_bytes())})
    return digest_payload(
        {"algorithm": "NEXUS_REVIEW_RENDER_DIGEST_V1", "renders": entries}
    )


# --------------------------------------------------------------------------
# Packets humains
# --------------------------------------------------------------------------


def roles_for(discipline: str, policy: dict[str, Any]) -> tuple[str, str]:
    entry = policy["roles"][discipline]
    return entry["review_a"], entry["review_b"]


def packet_digest(packet: dict[str, Any], policy: dict[str, Any]) -> str:
    excluded = set(policy["digests"]["packet_digest"]["excludes"])
    payload = {key: value for key, value in packet.items() if key not in excluded}
    payload["algorithm"] = "NEXUS_REVIEW_PACKET_DIGEST_V1"
    return digest_payload(payload)


def source_freeze_path(chapter_id: str, root: Path = ROOT) -> Path:
    """Chemin conventionnel du gel de source d'un chapitre."""

    return root / "audit" / f"{chapter_id.replace('-', '_')}_REVIEW_SOURCE_FREEZE.json"


def load_source_freeze(
    chapter_id: str, root: Path = ROOT, path: Path | None = None
) -> dict[str, Any] | None:
    """Gel de source canonique reconnu par l'humain, s'il existe.

    Le digest de ce gel n'est pas le meme objet que OBJECT_SET_DIGEST : il est
    produit par un autre generateur et couvre d'autres champs. Les deux sont
    portes cote a cote dans le packet, jamais confondus.
    """

    candidate = path or source_freeze_path(chapter_id, root)
    if not candidate.is_file():
        return None
    payload = json.loads(candidate.read_text(encoding="utf-8"))
    return {
        "artifact": candidate.name,
        "schema_version": payload.get("schema_version"),
        "source_sha": payload.get("source_sha"),
        "chapter_object_set_digest": payload.get("chapter_object_set_digest"),
        "chapter_objects": payload.get("counts", {}).get("chapter_objects"),
        "generator": "scripts/build_1spe_suites_review_source_freeze.py",
        "relation_to_object_set_digest": (
            "digest distinct : autre generateur, autres champs couverts ; "
            "les deux doivent porter le meme nombre d'objets"
        ),
    }


def build_packet(
    scope: ChapterScope,
    role: str,
    policy: dict[str, Any],
    render_paths: list[str] | None = None,
    root: Path = ROOT,
    source_freeze: dict[str, Any] | None = None,
) -> dict[str, Any]:
    review_a, review_b = roles_for(scope.discipline, policy)
    if role == review_a:
        controls = policy["packet_a_controls"]["minimum_controls"]
        letter = "A"
    elif role == review_b:
        controls = policy["packet_b_controls"]["minimum_controls"]
        letter = "B"
    else:
        raise HumanReviewViolation(
            f"Role {role!r} non prevu pour la discipline {scope.discipline}"
        )

    renders = sorted(set(render_paths or []))
    packet: dict[str, Any] = {
        "artifact_type": "human_review_packet",
        "human_review_receipt_schema_version": policy["human_review_receipt_schema_version"],
        "packet_letter": letter,
        "chapter_id": scope.chapter_id,
        "manual_id": scope.manual_id,
        "discipline": scope.discipline,
        "review_role": role,
        "reviewer_assignment": "PENDING_UNASSIGNED",
        "verdict": None,
        "verdict_state": "PENDING_UNASSIGNED",
        "object_count": scope.object_count,
        "object_set_digest": scope.object_set_digest,
        "semantic_review_digest": scope.semantic_review_digest,
        "review_render_digest": render_digest(renders, root),
        "render_paths": renders,
        "render_evidence": "PRESENT" if renders else "ABSENT",
        "programme_authority_digest": scope.programme_authority_digest,
        "programme_authority": scope.programme_authority,
        "minimum_controls": list(controls),
        "reviewer_must_examine_current_content_not_only_diffs": True,
        "objects": [entry.identity_payload() for entry in scope.objects],
        "qcm_question_ids": qcm_question_ids(scope.chapter_id, root),
        "capabilities": sorted(
            {
                capability
                for entry in scope.objects
                for capability in entry.capabilities
            }
        ),
        "unassembled_object_ids": scope.unassembled_object_ids(),
        "attestation_template": policy["attestation"]["machine_format"],
        "permitted_verdicts": list(policy["verdicts"]),
        "repository_source_sha": repository_source_sha(root),
    }
    if source_freeze is not None:
        if source_freeze.get("chapter_objects") != scope.object_count:
            raise HumanReviewViolation(
                "le gel de source canonique et l'enumeration ne portent pas le "
                f"meme nombre d'objets : {source_freeze.get('chapter_objects')} "
                f"contre {scope.object_count}"
            )
        packet["canonical_source_freeze"] = source_freeze
    packet["packet_digest"] = packet_digest(packet, policy)
    return packet


# --------------------------------------------------------------------------
# Validation d'un recu humain
# --------------------------------------------------------------------------


def _receipt_validator(root: Path = ROOT) -> Draft202012Validator:
    schema = json.loads((root / RECEIPT_SCHEMA_PATH).read_text(encoding="utf-8"))
    return Draft202012Validator(schema)


def assert_human_identity(receipt: dict[str, Any], policy: dict[str, Any]) -> None:
    """Test B : aucun agent automatise ne peut porter un role de revue."""

    if receipt.get("reviewer_is_human") is not True:
        raise HumanReviewViolation("reviewer_is_human doit valoir true")
    haystack = " ".join(
        str(receipt.get(key, ""))
        for key in ("reviewer_name", "reviewer_identity_reference", "recorded_by_reviewer")
    )
    for pattern in policy["forbidden_reviewer_identity_patterns"]:
        if re.search(pattern, haystack):
            raise HumanReviewViolation(
                f"Identite de reviewer non humaine detectee (motif {pattern!r})"
            )


def validate_receipt(
    receipt: dict[str, Any],
    scope: ChapterScope,
    packet: dict[str, Any],
    policy: dict[str, Any],
    root: Path = ROOT,
) -> None:
    """Refuse tout recu qui ne lie pas exactement le chapitre gele revu."""

    errors = sorted(
        _receipt_validator(root).iter_errors(receipt), key=lambda error: error.path
    )
    if errors:
        raise HumanReviewViolation(
            "Recu non conforme au schema : "
            + "; ".join(f"{list(error.path)}: {error.message}" for error in errors)
        )

    if not RFC3339_RE.fullmatch(receipt["review_timestamp"]):
        raise HumanReviewViolation("review_timestamp doit etre un instant RFC3339 date-time")

    # Test K : verdict inconnu.
    if receipt["verdict"] not in policy["verdicts"]:
        raise HumanReviewViolation(f"Verdict inconnu : {receipt['verdict']!r}")

    # Test B : reviewer humain.
    assert_human_identity(receipt, policy)

    if receipt["chapter_id"] != scope.chapter_id:
        raise HumanReviewViolation("chapter_id du recu hors perimetre")
    if receipt["manual_id"] != scope.manual_id:
        raise HumanReviewViolation("manual_id du recu hors perimetre")

    review_a, review_b = roles_for(scope.discipline, policy)
    if receipt["review_role"] not in {review_a, review_b}:
        raise HumanReviewViolation(
            f"Role {receipt['review_role']!r} hors contrat pour {scope.discipline}"
        )
    if receipt["review_role"] != packet["review_role"]:
        raise HumanReviewViolation("Role du recu different du role du packet")

    # Test C : object_set_digest.
    if receipt["object_set_digest"] != scope.object_set_digest:
        raise HumanReviewViolation("object_set_digest ne correspond pas au chapitre gele")
    if receipt["object_count"] != scope.object_count:
        raise HumanReviewViolation("object_count ne correspond pas au chapitre gele")

    # Test D : semantic_review_digest.
    if receipt["semantic_review_digest"] != scope.semantic_review_digest:
        raise HumanReviewViolation("semantic_review_digest ne correspond pas au contenu revu")

    # Test E : packet digest.
    if receipt["packet_digest"] != packet["packet_digest"]:
        raise HumanReviewViolation("packet_digest ne correspond pas au packet emis")
    if receipt["review_render_digest"] != packet["review_render_digest"]:
        raise HumanReviewViolation("review_render_digest ne correspond pas au packet emis")

    if receipt["programme_authority_digest"] != scope.programme_authority_digest:
        raise HumanReviewViolation("programme_authority_digest ne correspond pas a l'autorite")

    # Test F : APPROVED exige blocking_findings vide.
    findings = receipt["blocking_findings"]
    if receipt["verdict"] == "APPROVED" and findings:
        raise HumanReviewViolation("APPROVED interdit avec des blocking_findings")
    if receipt["verdict"] == "CHANGES_REQUESTED" and not findings:
        raise HumanReviewViolation("CHANGES_REQUESTED exige au moins un finding identifiable")

    # Test J : aucun finding ne peut viser un objet hors ensemble gele.
    known = set(scope.object_ids) | {entry.path for entry in scope.objects}
    known |= set(qcm_question_ids(scope.chapter_id, root))
    for finding in findings:
        if finding["object_ref"] not in known:
            raise HumanReviewViolation(
                f"blocking_finding hors ensemble gele : {finding['object_ref']!r}"
            )
    for comment in receipt["comments"]:
        reference = comment.get("object_ref")
        if reference is not None and reference not in known:
            raise HumanReviewViolation(
                f"commentaire hors ensemble gele : {reference!r}"
            )

    expected_attestation = policy["attestation"]["machine_format"].format(
        chapter_id=scope.chapter_id,
        object_set_digest=scope.object_set_digest,
        packet_digest=packet["packet_digest"],
        review_role=receipt["review_role"],
        verdict=receipt["verdict"],
    )
    normalised = " ".join(receipt["attestation_text"].split())
    if " ".join(expected_attestation.split()) not in normalised:
        raise HumanReviewViolation(
            "attestation_text ne contient pas l'attestation machine deterministe attendue"
        )


def assert_independent_reviews(
    receipt_a: dict[str, Any], receipt_b: dict[str, Any]
) -> None:
    """Test A : deux identites humaines distinctes, deux decisions distinctes."""

    if receipt_a["review_role"] == receipt_b["review_role"]:
        raise HumanReviewViolation("Les deux recus portent le meme role")
    if (
        receipt_a["reviewer_identity_reference"]
        == receipt_b["reviewer_identity_reference"]
    ):
        raise HumanReviewViolation(
            "La meme identite humaine ne peut pas satisfaire les deux roles"
        )
    if receipt_a["review_id"] == receipt_b["review_id"]:
        raise HumanReviewViolation("Les deux recus portent le meme review_id")


# --------------------------------------------------------------------------
# Fraicheur
# --------------------------------------------------------------------------


CONTENT_CURRENT = "CURRENT"
CONTENT_STALE = "HISTORICAL_STALE"
RENDER_CURRENT = "RENDER_CURRENT"
RENDER_STALE = "RENDER_STALE"


def receipt_freshness(
    receipt: dict[str, Any],
    scope: ChapterScope,
    current_render_digest: str | None = None,
) -> dict[str, str]:
    """Fraicheur d'un recu : contenu et rendu sont deux autorites disjointes."""

    content = (
        CONTENT_CURRENT
        if receipt["semantic_review_digest"] == scope.semantic_review_digest
        and receipt["object_set_digest"] == scope.object_set_digest
        and receipt["programme_authority_digest"] == scope.programme_authority_digest
        else CONTENT_STALE
    )
    if current_render_digest is None:
        render = RENDER_CURRENT
    else:
        render = (
            RENDER_CURRENT
            if receipt["review_render_digest"] == current_render_digest
            else RENDER_STALE
        )
    return {"content_state": content, "visual_state": render}


def classify_change(paths: list[str]) -> str:
    """STYLE_ONLY si aucun chemin ne peut porter de contenu semantique."""

    return (
        "STYLE_ONLY"
        if paths and all(Path(path).suffix in STYLE_ONLY_SUFFIXES for path in paths)
        else "SEMANTIC_CANDIDATE"
    )


# --------------------------------------------------------------------------
# Etat de revue d'un chapitre
# --------------------------------------------------------------------------


def chapter_review_dir(chapter_id: str, root: Path = ROOT) -> Path:
    return root / REVIEW_ROOT / chapter_id


def load_receipts(chapter_id: str, root: Path = ROOT) -> list[dict[str, Any]]:
    directory = chapter_review_dir(chapter_id, root) / "receipts"
    if not directory.is_dir():
        return []
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(directory.glob("*.json"))
    ]


def evaluate_state(
    chapter_id: str,
    policy: dict[str, Any],
    root: Path = ROOT,
    scope: ChapterScope | None = None,
    receipts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Etat de revue derive, sans aucune auto-approbation possible."""

    scope = scope or build_scope(chapter_id, root)
    receipts = load_receipts(chapter_id, root) if receipts is None else receipts
    review_a, review_b = roles_for(scope.discipline, policy)

    per_role: dict[str, dict[str, Any]] = {}
    for role in (review_a, review_b):
        matching = [item for item in receipts if item.get("review_role") == role]
        if not matching:
            per_role[role] = {"state": "PENDING_UNASSIGNED", "verdict": None}
            continue
        latest = max(matching, key=lambda item: item["review_timestamp"])
        freshness = receipt_freshness(latest, scope)
        state = (
            latest["verdict"]
            if freshness["content_state"] == CONTENT_CURRENT
            else CONTENT_STALE
        )
        per_role[role] = {
            "state": state,
            "verdict": latest["verdict"],
            "review_id": latest["review_id"],
            "reviewer_identity_reference": latest["reviewer_identity_reference"],
            "content_state": freshness["content_state"],
        }

    approved = all(entry["state"] == "APPROVED" for entry in per_role.values())
    independent = None
    if approved:
        references = {
            entry.get("reviewer_identity_reference") for entry in per_role.values()
        }
        independent = len(references) == 2 and None not in references

    qcm_ids = qcm_question_ids(chapter_id, root)
    if not qcm_ids:
        qcm_gate = "NOT_APPLICABLE"
    elif approved and independent:
        qcm_gate = "SATISFIED"
    else:
        qcm_gate = "PENDING"

    return {
        "chapter_id": chapter_id,
        "manual_id": scope.manual_id,
        "discipline": scope.discipline,
        "object_count": scope.object_count,
        "object_set_digest": scope.object_set_digest,
        "semantic_review_digest": scope.semantic_review_digest,
        "programme_authority_digest": scope.programme_authority_digest,
        "review_a": {"role": review_a, **per_role[review_a]},
        "review_b": {"role": review_b, **per_role[review_b]},
        "independence": independent,
        "qcm_question_count": len(qcm_ids),
        "qcm_human_approval": qcm_gate,
        "human_content_approval": "APPROVED"
        if approved and independent and qcm_gate in {"SATISFIED", "NOT_APPLICABLE"}
        else "PENDING",
        "visual_authority": "INDEPENDENT_D7_GATE",
        "publication_approval": False,
    }


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(payload) + "\n", encoding="utf-8")


def _pretty(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def command_packets(args: argparse.Namespace) -> int:
    policy = load_policy(ROOT)
    scope = build_scope(args.chapter, ROOT)
    review_a, review_b = roles_for(scope.discipline, policy)
    directory = chapter_review_dir(args.chapter, ROOT)
    freeze = load_source_freeze(
        args.chapter, ROOT, Path(args.freeze) if args.freeze else None
    )
    for letter, role in (("A", review_a), ("B", review_b)):
        packet = build_packet(
            scope, role, policy, args.render or [], ROOT, source_freeze=freeze
        )
        _pretty(directory / f"packet-{letter}-{role}.json", packet)
        print(f"packet {letter} ({role}) : {packet['packet_digest']}")
    state = evaluate_state(args.chapter, policy, ROOT, scope=scope)
    _pretty(directory / "REVIEW_STATE.json", state)
    print(canonical_json(state))
    return 0


def command_state(args: argparse.Namespace) -> int:
    policy = load_policy(ROOT)
    print(
        json.dumps(
            evaluate_state(args.chapter, policy, ROOT), indent=2, ensure_ascii=False
        )
    )
    return 0


def command_digests(args: argparse.Namespace) -> int:
    scope = build_scope(args.chapter, ROOT)
    print(
        json.dumps(
            {
                "chapter_id": scope.chapter_id,
                "object_count": scope.object_count,
                "object_set_digest": scope.object_set_digest,
                "semantic_review_digest": scope.semantic_review_digest,
                "programme_authority_digest": scope.programme_authority_digest,
                "repository_source_sha": repository_source_sha(ROOT),
                "unassembled_object_ids": scope.unassembled_object_ids(),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


def command_validate(args: argparse.Namespace) -> int:
    policy = load_policy(ROOT)
    scope = build_scope(args.chapter, ROOT)
    packet = json.loads(Path(args.packet).read_text(encoding="utf-8"))
    receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    try:
        validate_receipt(receipt, scope, packet, policy, ROOT)
    except HumanReviewViolation as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OK: recu conforme au contrat de revue humaine")
    return 0


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    packets = sub.add_parser("packets", help="emettre les packets humains A et B")
    packets.add_argument("chapter")
    packets.add_argument("--render", action="append", help="chemin d'un rendu examine")
    packets.add_argument("--freeze", help="gel de source canonique a lier au packet")
    packets.set_defaults(func=command_packets)

    state = sub.add_parser("state", help="etat de revue derive du chapitre")
    state.add_argument("chapter")
    state.set_defaults(func=command_state)

    digests = sub.add_parser("digests", help="digests canoniques du chapitre gele")
    digests.add_argument("chapter")
    digests.set_defaults(func=command_digests)

    validate = sub.add_parser("validate", help="valider un recu humain recu")
    validate.add_argument("chapter")
    validate.add_argument("--packet", required=True)
    validate.add_argument("--receipt", required=True)
    validate.set_defaults(func=command_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
