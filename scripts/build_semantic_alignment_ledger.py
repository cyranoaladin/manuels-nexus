#!/usr/bin/env python3
"""Ou va chaque cellule que la mesure laisse en « identite declaree, alignement non etabli ».

`build_true_pedagogical_coverage.py` classe chaque couple (capacite, role)
parmi quatre etats. L'un d'eux, `SEMANTICALLY_VALIDATED_CONTENT`, est defini
comme « au moins une preuve separee atteste que le corps sert cet UID » -- mais
ce producteur n'a que trois entrees (resolveur d'identite, ledger de clones,
sources) et ne consulte aucun artefact de preuve. L'etat est donc INATTEIGNABLE
par construction : aucune entree ne peut le produire. Les 371 cellules 1SPE
restent indefiniment en `DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED`,
et le gate qui les lit reste rouge sans jamais dire pourquoi.

CE REGISTRE NE REND AUCUNE CELLULE VERTE.

Il ne fabrique pas la preuve manquante : il ROUTE. Pour chaque cellule laissee
dans cet etat, il dit ce que la machine peut DEMONTRER et ce qu'elle ne peut
pas, exactement comme `build_manual_review_disposition_ledger.py` route les
objets que l'oracle SymPy laisse en revue manuelle.

    DEFAUT_ETABLI
        la machine demontre une CONTRADICTION. Un artefact de preuve
        independant contredit l'attribution declaree : la relation EX/CO est
        structurellement en echec, le ledger de clones marque une fausse copie,
        la preuve QCM independante contredit la cle declaree, ou deux capacites
        soeurs du meme chapitre sont creditees par un corps identique -- la
        signature meme du P0 fondateur.

    JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS
        defaut terminal EXPLICITE. Seul le META rattache le corps a la
        capacite ; etablir que ce corps sert vraiment cette capacite est un
        jugement pedagogique. C'est un RESULTAT LEGITIME, pas une lacune de
        mesure.

L'objectif n'est pas DEFAUT_ETABLI = 0 -- une revue humaine est un resultat
legitime -- mais UNKNOWN = 0 : toute cellule tombe dans exactement une branche.

CE QUE CE REGISTRE S'INTERDIT.

Le depot REFUSE de deduire un alignement semantique d'une preuve structurelle.
`build_ex_co_graph.py` le dit dans son propre verdict : meme quand tout
concorde, `semantic_alignment` vaut `INVALIDATED_BY_STRUCTURAL_EVIDENCE`. Ce
registre respecte ce refus : aucune branche ne certifie POSITIVEMENT un
alignement. Il n'y a donc pas de disposition « aligne ».

Il s'interdit egalement, comme `capacity_identity.py` :

* toute liste blanche, tout solveur par identifiant d'objet ;
* toute valeur attendue codee en dur ;
* toute regle nommant un chapitre ou un objet particulier ;
* tout appariement par ressemblance lexicale entre le libelle d'une capacite
  et le corps d'un objet -- ce serait precisement le defaut que la campagne
  combat.

Chaque disposition se deduit de ce que la cellule CONTIENT et de ce que les
artefacts de preuve DISENT, jamais de qui elle est.

PEREMPTION. Chaque objet rattache porte le sha256 de son corps. Un dossier de
revue humaine se perime des que le contenu change : un registre qui ne bouge
pas quand le corps bouge ne prouve rien.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "audit/SEMANTIC_ALIGNMENT_LEDGER.json"
OUTPUT_MD = ROOT / "audit/SEMANTIC_ALIGNMENT_LEDGER.md"

CLONE_LEDGER = ROOT / "audit/P0_CONTENT_CLONE_LEDGER.json"
EX_CO_GRAPH = ROOT / "audit/EX_CO_GRAPH.json"
OFFICIAL_COVERAGE = ROOT / "audit/OFFICIAL_PROGRAM_COVERAGE_2026_2027.json"
QCM_EVIDENCE = ROOT / "audit/QCM_INDEPENDENT_EVIDENCE_V2.json"

CORPORA = (
    ROOT / "Mathematiques/manuel-maths/chapitres",
    ROOT / "NSI/chapitres",
)

#: Seul etat routable : les autres ne portent aucun corps a juger.
ROUTED_CELL_STATE = "DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED"

DEFAUT = "DEFAUT_ETABLI"
HUMAIN = "JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS"
DISPOSITIONS = (DEFAUT, HUMAIN)

EX_CO_CAPACITY_CONTRADICTION = "EX_CO_CAPACITY_CONTRADICTION"
EX_CO_STRUCTURAL_FAILURE = "EX_CO_STRUCTURAL_FAILURE"
CLONE_FALSE_COPY = "CLONE_FALSE_COPY"
QCM_KEY_CONTRADICTED = "QCM_KEY_CONTRADICTED_BY_INDEPENDENT_EVIDENCE"
SIBLING_SHARED_BODY = "SIBLING_CAPACITIES_SHARE_ONE_BODY"


class SemanticAlignmentError(RuntimeError):
    """La mesure ne peut pas etre produite sans inventer une preuve."""


# -- modules soeurs, charges sans dupliquer leur definition du corps --------


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _coverage_module():
    return _load("true_pedagogical_coverage", "scripts/build_true_pedagogical_coverage.py")


def _clone_module():
    """Le corps d'un objet a UNE definition dans le depot, pas deux.

    La reutiliser ici garantit que le sha256 du registre est comparable a
    `exact_body_digest` du ledger de clones ; en recopier la formule laisserait
    les deux definitions diverger en silence.
    """

    return _load("p0_content_clone_ledger", "scripts/build_p0_content_clone_ledger.py")


def _digest(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _set_digest(values: Any) -> str:
    return _digest(_canonical(sorted(values)))


def _resolve_path(relative: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute():
        return candidate
    return ROOT / relative


# -- libelles contractuels et atomes officiels ------------------------------


def _student_wordings(chapters: list[str], corpora: tuple[Path, ...]) -> dict[str, str]:
    """Libelle eleve de chaque capacite, indexe par cle EXACTE (chapitre, code).

    Aucune approximation : le code du contrat est lu tel quel, jamais devine.
    """

    wordings: dict[str, str] = {}
    wanted = set(chapters)
    for corpus in corpora:
        if not corpus.is_dir():
            continue
        for directory in sorted(corpus.iterdir()):
            if directory.name not in wanted:
                continue
            contract = directory / "contrat.yaml"
            if not contract.is_file():
                continue
            document = yaml.safe_load(contract.read_text(encoding="utf-8")) or {}
            for entry in document.get("capacites") or []:
                if not isinstance(entry, dict):
                    continue
                code = str(entry.get("code") or "").strip()
                if not code:
                    continue
                libelle = entry.get("libelle_eleve")
                wordings[f"{directory.name}::{code}"] = (
                    str(libelle).strip() if libelle else ""
                )
    return wordings


def _official_atoms(
    coverage_rows: list[dict[str, Any]], resolver, scope: str
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, str]]]:
    """Atomes officiels rattaches, par egalite exacte d'alias pleinement qualifie.

    `resolve_collection_alias` n'admet ni code local nu ni suffixe : un atome
    qui ne se rattache a aucune capacite contractuelle reste NOMME, jamais
    absorbe en silence.
    """

    by_capacity: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    unattached: list[dict[str, str]] = []
    for row in coverage_rows:
        if row.get("manual") != scope:
            continue
        alias = str(row.get("contract_capacity") or "").strip()
        atom = {
            "atom_id": str(row.get("atom_id") or ""),
            "obligation_type": row.get("obligation_type"),
            "official_section": row.get("official_section"),
            "official_page_or_anchor": row.get("official_page_or_anchor"),
            "official_wording_or_short_paraphrase": row.get(
                "official_wording_or_short_paraphrase"
            ),
            "coverage_status": row.get("coverage_status"),
        }
        if not alias:
            unattached.append(
                {"atom_id": atom["atom_id"], "contract_capacity": "", "reason": "alias vide"}
            )
            continue
        try:
            resolution = resolver.resolve_collection_alias(alias)
        except Exception as exc:  # resolveur charge separement
            unattached.append(
                {
                    "atom_id": atom["atom_id"],
                    "contract_capacity": alias,
                    "reason": str(exc),
                }
            )
            continue
        by_capacity[resolution.identity.uid].append(atom)
    for uid in by_capacity:
        by_capacity[uid].sort(key=lambda entry: entry["atom_id"])
    return dict(by_capacity), sorted(
        unattached, key=lambda row: (row["contract_capacity"], row["atom_id"])
    )


# -- corps rattache et son sha256 ------------------------------------------


def _tex_body_sha(path: Path, clone) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    return _digest(clone.pedagogical_body(text))


def _qcm_body_sha(path: Path, question_id: str) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    for question in payload.get("questions") or []:
        if isinstance(question, dict) and str(question.get("id") or "") == question_id:
            return _digest(_canonical(question))
    raise SemanticAlignmentError(
        f"question QCM introuvable {question_id} dans {path}"
    )


def _body_of(reference: str, clone) -> dict[str, Any]:
    """Corps courant de l'objet designe, avec son sha256.

    Une reference QCM porte la question apres un `#` : le corps juge est alors
    la question elle-meme, pas le fichier entier -- sans quoi une cellule se
    perimerait a chaque retouche d'une question voisine.
    """

    relative, _, question_id = reference.partition("#")
    path = _resolve_path(relative)
    if not path.is_file():
        raise SemanticAlignmentError(f"objet credite introuvable: {reference}")
    if question_id:
        return {
            "path": relative,
            "question_id": question_id,
            "body_kind": "qcm_question",
            "body_sha256": _qcm_body_sha(path, question_id),
        }
    return {
        "path": relative,
        "question_id": None,
        "body_kind": "pedagogical_body",
        "body_sha256": _tex_body_sha(path, clone),
    }


# -- canaux de preuve -------------------------------------------------------


def _false_copies(clone_ledger: dict[str, Any]) -> dict[str, str]:
    found: dict[str, str] = {}
    for group in clone_ledger.get("groups") or []:
        selection = group.get("canonical_selection") or {}
        for path in selection.get("false_copy_paths") or []:
            found[path] = str(group.get("clone_group_id") or "")
    return found


def _ex_co_structural_failures(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    failures: dict[str, dict[str, Any]] = {}
    for relation in graph.get("relations") or []:
        if relation.get("structural_status") != "FAIL":
            continue
        correction_id = str(relation.get("correction_id") or "")
        if correction_id:
            failures[correction_id] = relation
    return failures


def _qcm_contradictions(evidence: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Questions dont la preuve INDEPENDANTE contredit la cle declaree.

    Le contrat d'independance de l'artefact garantit que le solveur n'a jamais
    vu la cle : c'est ce qui fait de la contradiction une demonstration, et non
    une opinion.
    """

    contradicted: dict[str, dict[str, Any]] = {}
    for question in evidence.get("questions") or []:
        verification = question.get("verification")
        if not isinstance(verification, dict):
            continue
        matches = verification.get("declared_key_matches_computation")
        verdict = verification.get("answer_key_verdict")
        if matches is False or verdict == "FAIL":
            source = str(question.get("source_path") or "")
            key = f"{source}#{question.get('question_id')}"
            contradicted[key] = {
                "declared_key": verification.get("declared_key"),
                "computed_unique_answer": verification.get("computed_unique_answer"),
                "answer_key_verdict": verdict,
                "declared_key_matches_computation": matches,
                "evidence_digest": question.get("evidence_digest"),
            }
    return contradicted


def _contested_claims(coverage: dict[str, Any]) -> dict[tuple[str, str, str], list[dict[str, Any]]]:
    """Objets qui REVENDIQUENT une cellule alors que la machine les recuse.

    Un corrige qui declare `C1` tout en corrigeant un exercice de `C2` ne
    credite rien -- la mesure le retire deja. Mais sa revendication reste une
    contradiction demontree PORTANT SUR LA CELLULE `C1` : l'oublier laisserait
    un defaut prouve sans destinataire.
    """

    claims: dict[tuple[str, str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for blocker in coverage.get("ex_co_relationship_blockers") or []:
        path = str(blocker.get("correction_path") or "")
        chapter = _chapter_of(path)
        if chapter is None:
            continue
        for capacity in blocker.get("correction_capacities") or []:
            claims[(chapter, str(capacity), "corriges")].append(blocker)
    return dict(claims)


def _chapter_of(relative: str) -> str | None:
    parts = Path(relative).parts
    if "chapitres" not in parts:
        return None
    index = parts.index("chapitres") + 1
    return parts[index] if index < len(parts) else None


# -- construction -----------------------------------------------------------


def build_ledger(
    *,
    scope: str = "1SPE",
    coverage: dict[str, Any] | None = None,
    resolver=None,
    corpora: tuple[Path, ...] = CORPORA,
    clone_ledger: dict[str, Any] | None = None,
    ex_co_graph: dict[str, Any] | None = None,
    official_coverage: dict[str, Any] | None = None,
    qcm_evidence: dict[str, Any] | None = None,
    **coverage_kwargs: Any,
) -> dict[str, Any]:
    coverage_producer = _coverage_module()
    clone = _clone_module()
    identity = _load("capacity_identity", "scripts/capacity_identity.py")
    resolver = resolver or identity.CapacityIdentityResolver.from_corpora(corpora)

    if clone_ledger is None:
        clone_ledger = json.loads(CLONE_LEDGER.read_text(encoding="utf-8"))
    if coverage is None:
        coverage = coverage_producer.build_coverage(
            resolver=resolver,
            clone_ledger=clone_ledger,
            corpora=corpora,
            **coverage_kwargs,
        )
    if ex_co_graph is None:
        ex_co_graph = (
            json.loads(EX_CO_GRAPH.read_text(encoding="utf-8"))
            if EX_CO_GRAPH.is_file()
            else {}
        )
    if official_coverage is None:
        official_coverage = (
            json.loads(OFFICIAL_COVERAGE.read_text(encoding="utf-8"))
            if OFFICIAL_COVERAGE.is_file()
            else {}
        )
    if qcm_evidence is None:
        qcm_evidence = (
            json.loads(QCM_EVIDENCE.read_text(encoding="utf-8"))
            if QCM_EVIDENCE.is_file()
            else {}
        )

    cells = [
        row
        for row in coverage["rows"]
        if row["manual"] == scope and row["state"] == ROUTED_CELL_STATE
    ]
    chapters = sorted({row["chapter"] for row in cells})
    wordings = _student_wordings(chapters, corpora)
    atoms_by_capacity, unattached_atoms = _official_atoms(
        official_coverage.get("rows") or [], resolver, scope
    )
    false_copies = _false_copies(clone_ledger)
    structural_failures = _ex_co_structural_failures(ex_co_graph)
    qcm_contradictions = _qcm_contradictions(qcm_evidence)
    contested = _contested_claims(coverage)

    # Premiere passe : le corps courant de chaque objet rattache.
    bodies: dict[tuple[str, str], dict[str, Any]] = {}
    for cell in cells:
        for object_id, reference in zip(
            cell["valid_object_ids"], cell["valid_object_paths"], strict=True
        ):
            key = (object_id, reference)
            if key not in bodies:
                bodies[key] = {"object_id": object_id, **_body_of(reference, clone)}

    # Deuxieme passe : un corps IDENTIQUE partage par deux objets DISTINCTS
    # credites a deux capacites SOEURS du meme chapitre. Un seul objet qui
    # declare plusieurs capacites n'est pas ce defaut : une evaluation couvre
    # legitimement tout un chapitre. Le defaut, c'est DEUX corps identiques
    # attribues a DEUX capacites differentes -- au plus une des deux
    # attributions peut etre juste.
    shared: dict[tuple[str, str], dict[str, set[str]]] = collections.defaultdict(
        lambda: collections.defaultdict(set)
    )
    for cell in cells:
        for object_id, reference in zip(
            cell["valid_object_ids"], cell["valid_object_paths"], strict=True
        ):
            body = bodies[(object_id, reference)]
            bucket = shared[(cell["chapter"], body["body_sha256"])]
            bucket[reference].add(cell["canonical_capacity_uid"])
    sibling_conflicts: dict[tuple[str, str], dict[str, Any]] = {}
    for (chapter, sha), by_reference in shared.items():
        if len(by_reference) < 2:
            continue
        capacities = {uid for uids in by_reference.values() for uid in uids}
        if len(capacities) < 2:
            continue
        sibling_conflicts[(chapter, sha)] = {
            "chapter": chapter,
            "body_sha256": sha,
            "capacity_uids": sorted(capacities),
            "object_references": sorted(by_reference),
        }

    records: list[dict[str, Any]] = []
    for cell in sorted(
        cells, key=lambda row: (row["chapter"], row["capacity"], row["role"])
    ):
        uid = cell["canonical_capacity_uid"]
        actual_body = [
            bodies[(object_id, reference)]
            for object_id, reference in zip(
                cell["valid_object_ids"], cell["valid_object_paths"], strict=True
            )
        ]
        actual_body.sort(key=lambda entry: (entry["path"], entry["object_id"]))

        evidence: list[dict[str, Any]] = []
        for entry in actual_body:
            reference = entry["path"] + (
                f"#{entry['question_id']}" if entry["question_id"] else ""
            )
            if entry["path"] in false_copies:
                evidence.append(
                    {
                        "channel": CLONE_FALSE_COPY,
                        "artifact": "audit/P0_CONTENT_CLONE_LEDGER.json",
                        "field": "groups[].canonical_selection.false_copy_paths",
                        "object_id": entry["object_id"],
                        "path": entry["path"],
                        "clone_group_id": false_copies[entry["path"]],
                    }
                )
            relation = structural_failures.get(entry["object_id"])
            if relation is not None:
                evidence.append(
                    {
                        "channel": EX_CO_STRUCTURAL_FAILURE,
                        "artifact": "audit/EX_CO_GRAPH.json",
                        "field": "relations[].structural_status",
                        "object_id": entry["object_id"],
                        "path": entry["path"],
                        "classifications": list(relation.get("classifications") or []),
                        "exercise_id": relation.get("exercise_id"),
                    }
                )
            contradiction = qcm_contradictions.get(reference)
            if contradiction is not None:
                evidence.append(
                    {
                        "channel": QCM_KEY_CONTRADICTED,
                        "artifact": "audit/QCM_INDEPENDENT_EVIDENCE_V2.json",
                        "field": "questions[].verification",
                        "object_id": entry["object_id"],
                        "path": reference,
                        **contradiction,
                    }
                )
            conflict = sibling_conflicts.get((cell["chapter"], entry["body_sha256"]))
            if conflict is not None:
                evidence.append(
                    {
                        "channel": SIBLING_SHARED_BODY,
                        "artifact": "scripts/build_semantic_alignment_ledger.py",
                        "field": "actual_body[].body_sha256",
                        "object_id": entry["object_id"],
                        "path": entry["path"],
                        **conflict,
                    }
                )
        for blocker in contested.get(
            (cell["chapter"], cell["capacity"], cell["role"]), []
        ):
            evidence.append(
                {
                    "channel": EX_CO_CAPACITY_CONTRADICTION,
                    "artifact": "audit/TRUE_PEDAGOGICAL_COVERAGE.json",
                    "field": "ex_co_relationship_blockers[]",
                    "classification": blocker.get("classification"),
                    "object_id": blocker.get("correction_id"),
                    "path": blocker.get("correction_path"),
                    "correction_capacities": list(
                        blocker.get("correction_capacities") or []
                    ),
                    "exercise_id": blocker.get("exercise_id"),
                    "exercise_capacities": list(
                        blocker.get("exercise_capacities") or []
                    ),
                }
            )

        evidence.sort(key=lambda row: _canonical(row))
        atoms = atoms_by_capacity.get(uid, [])
        if evidence:
            disposition = DEFAUT
            channels = sorted({str(row["channel"]) for row in evidence})
            because = (
                "la machine demontre une contradiction sur cette cellule : "
                + " ; ".join(channels)
                + ". Preuves citees : "
                + " ; ".join(
                    sorted({f"{row['artifact']}::{row['field']}" for row in evidence})
                )
                + ". Au plus une des attributions en conflit peut etre juste ; "
                "aucune n'est corrigee ici."
            )
        else:
            disposition = HUMAIN
            because = (
                "aucun artefact de preuve ne contredit cette cellule, et aucun "
                "n'atteste non plus que le corps la serve : seul le META "
                f"rattache {len(actual_body)} corps a {uid}. "
                "L'identite declaree est resolue par egalite exacte "
                "(scripts/capacity_identity.py) et la couverture de reponses "
                "n'etablit qu'une COUVERTURE "
                "(audit/EX_CO_GRAPH.json::relations[].semantic_alignment = "
                "INVALIDATED_BY_STRUCTURAL_EVIDENCE). Etablir que ce corps "
                "sert cette capacite est un jugement pedagogique, pas un "
                "calcul : c'est un resultat terminal, pas une lacune de mesure."
            )

        records.append(
            {
                "cell_id": f"{cell['chapter']}/{cell['capacity']}/{cell['role']}",
                "manual": cell["manual"],
                "chapter": cell["chapter"],
                "official_capacity": {
                    "canonical_uid": uid,
                    "local_code": cell["capacity"],
                    "official_ref": _official_ref(resolver, cell["chapter"], cell["capacity"]),
                    "student_wording": wordings.get(
                        f"{cell['chapter']}::{cell['capacity']}", ""
                    ),
                    "student_wording_source": (
                        f"{cell['chapter']}/contrat.yaml::capacites[code={cell['capacity']}]"
                        ".libelle_eleve"
                    ),
                    "official_atoms": atoms,
                    "official_atom_ids": [atom["atom_id"] for atom in atoms],
                    "official_atoms_source": (
                        "audit/OFFICIAL_PROGRAM_COVERAGE_2026_2027.json::"
                        "rows[].contract_capacity"
                    ),
                },
                "pedagogical_role": cell["role"],
                "actual_body": actual_body,
                "actual_body_digest": _set_digest(
                    [f"{entry['path']}::{entry['body_sha256']}" for entry in actual_body]
                ),
                "semantic_alignment": {
                    "disposition": disposition,
                    "because": because,
                    "evidence": evidence,
                },
            }
        )

    by_disposition = collections.Counter(
        record["semantic_alignment"]["disposition"] for record in records
    )
    unknown = sum(
        1 for record in records
        if record["semantic_alignment"]["disposition"] not in DISPOSITIONS
    )
    per_chapter: dict[str, dict[str, int]] = collections.defaultdict(
        lambda: collections.defaultdict(int)
    )
    for record in records:
        per_chapter[record["chapter"]][record["semantic_alignment"]["disposition"]] += 1
    by_channel: collections.Counter = collections.Counter()
    for record in records:
        for row in record["semantic_alignment"]["evidence"]:
            by_channel[str(row["channel"])] += 1

    return {
        "artifact_type": "semantic_alignment_ledger",
        "schema_version": 1,
        "generated_by": "scripts/build_semantic_alignment_ledger.py",
        "scope": scope,
        "approves_nothing": True,
        "closes_no_gate": False,
        "gate_effect": (
            "sur decision humaine du 2026-09-02, la matrice de campagne lit "
            "ces dispositions : une cellule routee vers l'humain ne bloque "
            "plus l'axe machine, tandis qu'un DEFAUT_ETABLI ou une cellule "
            "non routee le bloque toujours. C'est la regle de l'oracle SymPy "
            "-- la machine est complete quand il ne lui reste rien a classer, "
            "jamais quand plus aucune science humaine n'est requise. Aucun "
            "contenu n'est approuve pour autant : human_closure_status reste "
            "PENDING, publication_approval reste false, release-strict reste "
            "rouge."
        ),
        "routed_cell_state": ROUTED_CELL_STATE,
        "doctrine": {
            "no_positive_semantic_certification": (
                "aucune branche n'atteste POSITIVEMENT qu'un corps sert une "
                "capacite ; le depot refuse de deduire un alignement semantique "
                "d'une preuve structurelle, d'une transcription ou d'un META"
            ),
            "no_lexical_matching": (
                "aucune disposition ne repose sur la ressemblance entre le "
                "libelle d'une capacite et le corps d'un objet"
            ),
            "no_object_whitelist": (
                "aucune disposition n'est attachee a un identifiant d'objet : "
                "chacune se deduit de ce que la cellule CONTIENT et de ce que "
                "les artefacts de preuve DISENT"
            ),
            "objective": "UNKNOWN = 0, jamais DEFAUT_ETABLI = 0",
            "staleness": (
                "chaque corps rattache porte son sha256 : un dossier de revue "
                "se perime des que le contenu change"
            ),
        },
        "dispositions": {
            DEFAUT: (
                "la machine DEMONTRE une contradiction : un artefact de preuve "
                "independant recuse l'attribution declaree"
            ),
            HUMAIN: (
                "defaut terminal explicite : seul le META rattache le corps a "
                "la capacite ; etablir qu'il la sert est un jugement "
                "pedagogique. Resultat legitime, pas lacune"
            ),
        },
        "evidence_channels": {
            EX_CO_CAPACITY_CONTRADICTION: (
                "audit/TRUE_PEDAGOGICAL_COVERAGE.json::"
                "ex_co_relationship_blockers[] -- un corrige revendique cette "
                "capacite tout en corrigeant un objet qui n'en releve pas"
            ),
            EX_CO_STRUCTURAL_FAILURE: (
                "audit/EX_CO_GRAPH.json::relations[].structural_status = FAIL "
                "-- la relation exercice/corrige est structurellement en echec"
            ),
            CLONE_FALSE_COPY: (
                "audit/P0_CONTENT_CLONE_LEDGER.json::"
                "groups[].canonical_selection.false_copy_paths"
            ),
            QCM_KEY_CONTRADICTED: (
                "audit/QCM_INDEPENDENT_EVIDENCE_V2.json::questions[]."
                "verification -- la preuve independante contredit la cle "
                "declaree"
            ),
            SIBLING_SHARED_BODY: (
                "deux objets DISTINCTS de corps identique (meme sha256) "
                "credites a deux capacites soeurs du meme chapitre : la "
                "signature du P0 fondateur. Un objet unique declarant "
                "plusieurs capacites n'est pas ce defaut"
            ),
        },
        "counts": {
            "cells_examined": len(records),
            "SEMANTIC_ROUTING_UNRESOLVED": unknown,
            "SEMANTIC_CERTIFICATION_PENDING": by_disposition.get(HUMAIN, 0),
            "UNKNOWN": unknown,
            **{name: by_disposition.get(name, 0) for name in DISPOSITIONS},
        },
        "evidence_counts_by_channel": dict(sorted(by_channel.items())),
        "per_chapter": {
            chapter: dict(sorted(counts.items()))
            for chapter, counts in sorted(per_chapter.items())
        },
        "official_atom_attachment": {
            "capacities_with_atoms": sum(
                1
                for record in records
                if record["official_capacity"]["official_atom_ids"]
            ),
            "capacities_without_atoms": sum(
                1
                for record in records
                if not record["official_capacity"]["official_atom_ids"]
            ),
            "unattached_official_atoms": len(unattached_atoms),
            "unattached_official_atom_rows": unattached_atoms,
            "rule": (
                "rattachement par egalite exacte d'alias pleinement qualifie "
                "(capacity_identity.resolve_collection_alias) ; un atome dont "
                "l'alias ne designe aucune capacite contractuelle reste nomme"
            ),
        },
        "records_digest": _set_digest(
            [
                f"{record['cell_id']}::{record['semantic_alignment']['disposition']}"
                f"::{record['actual_body_digest']}"
                for record in records
            ]
        ),
        "defauts_etablis": [
            record
            for record in records
            if record["semantic_alignment"]["disposition"] == DEFAUT
        ],
        "records": records,
    }


def _official_ref(resolver, chapter: str, code: str) -> str | None:
    for identity in resolver.capacities_of(chapter):
        if identity.local_code == code:
            return identity.official_ref
    return None


# -- rendu ------------------------------------------------------------------


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_md(payload: dict[str, Any]) -> str:
    counts = payload["counts"]
    lines = [
        "# Registre d'alignement sémantique",
        "",
        "Ce registre **n'approuve rien** et ne rend aucune cellule verte. Il route",
        "les cellules que la mesure laisse en",
        f"`{payload['routed_cell_state']}` : pour chacune, il dit ce que la machine",
        "peut démontrer et ce qu'elle ne peut pas.",
        "",
        "L'objectif n'est pas `DEFAUT_ETABLI = 0` — une revue humaine est un",
        "résultat légitime — mais `UNKNOWN = 0`.",
        "",
        f"- portée : `{payload['scope']}`",
        f"- cellules examinées : `{counts['cells_examined']}`",
        f"- `SEMANTIC_ROUTING_UNRESOLVED` : `{counts.get('SEMANTIC_ROUTING_UNRESOLVED', 0)}`",
        f"- `SEMANTIC_CERTIFICATION_PENDING` : `{counts.get('SEMANTIC_CERTIFICATION_PENDING', 0)}`",
        f"- `DEFAUT_ETABLI` : `{counts['DEFAUT_ETABLI']}`",
        f"- `JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS` : "
        f"`{counts['JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS']}`",
        f"- `UNKNOWN` : `{counts['UNKNOWN']}`",
        "",
        "| Chapitre | DEFAUT_ETABLI | JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS | Total |",
        "|---|---:|---:|---:|",
    ]
    for chapter, per in payload["per_chapter"].items():
        defaut = per.get("DEFAUT_ETABLI", 0)
        humain = per.get("JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS", 0)
        lines.append(f"| `{chapter}` | {defaut} | {humain} | **{defaut + humain}** |")
    lines += ["", "## Défauts établis", ""]
    if not payload["defauts_etablis"]:
        lines += [
            "Aucun. Les canaux de preuve disponibles ne contredisent aucune",
            "cellule de cette portée. Ce n'est pas un satisfecit : cela signifie",
            "que l'alignement sémantique reste, pour toutes ces cellules, un",
            "jugement pédagogique humain.",
            "",
        ]
    else:
        lines += ["| Cellule | Canaux | Preuve |", "|---|---|---|"]
        for record in payload["defauts_etablis"]:
            channels = sorted(
                {row["channel"] for row in record["semantic_alignment"]["evidence"]}
            )
            proofs = sorted(
                {
                    f"{row['artifact']}::{row['field']}"
                    for row in record["semantic_alignment"]["evidence"]
                }
            )
            lines.append(
                f"| `{record['cell_id']}` | {', '.join(channels)} | "
                f"{', '.join(proofs)} |"
            )
        lines.append("")
    lines += [
        "## Ce que ce registre s'interdit",
        "",
        "- aucune liste blanche, aucun solveur par identifiant d'objet ;",
        "- aucune valeur attendue codée en dur, aucune règle nommant un chapitre ;",
        "- aucun appariement par ressemblance lexicale entre le libellé d'une",
        "  capacité et le corps d'un objet ;",
        "- aucune certification **positive** d'alignement sémantique.",
        "",
        "Chaque corps rattaché porte son `sha256` : le dossier se périme dès que",
        "le contenu change.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="comparer sans écrire")
    arguments = parser.parse_args(argv)

    payload = build_ledger()
    targets = ((OUTPUT_JSON, render_json(payload)), (OUTPUT_MD, render_md(payload)))
    stale: list[str] = []
    for path, rendered in targets:
        if arguments.check:
            current = path.read_text(encoding="utf-8") if path.is_file() else ""
            if current != rendered:
                stale.append(str(path.relative_to(ROOT)))
            continue
        path.write_text(rendered, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    for name in stale:
        print(f"STALE: {name}")
    if not arguments.check:
        print(json.dumps(payload["counts"], ensure_ascii=False, sort_keys=True))
    return 1 if stale else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
