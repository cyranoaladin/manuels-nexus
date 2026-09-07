#!/usr/bin/env python3
"""Re-lie les trois qualifications 1SPE-TRIGO à leur source courante.

La décision humaine du 2026-08-23 sur les extensions facultatives de
1SPE-TRIGONOMETRIE porte `invalidate_on_source_change: true` : dès que la
source bouge, la qualification devient périmée. Les trois sources ont bougé —
uniquement par restauration d'accents. Le Release Owner a tranché :

    ACCEPT_ACCENT_ONLY_QUALIFICATION_REBIND

Ce producteur applique cette décision, et rien d'autre.

CE QU'IL DIT
    « la qualification qui portait sur ce contenu reste applicable au même
    contenu dont seule l'accentuation orthographique a été corrigée. »

CE QU'IL NE DIT PAS
    « le contenu est désormais approuvé ». Les quatre revues restent
    `PENDING`, les objets restent `needs_review`, la dette reste bloquante.

CE QU'IL VÉRIFIE AVANT D'ÉCRIRE, POUR CHACUN DES TROIS OBJETS
    1. l'objet est l'un des trois nommés — rien d'autre n'hérite ;
    2. la version qualifiée est retrouvable dans l'historique Git par son
       empreinte, jamais lue depuis un rapport ;
    3. dépouillées de leurs accents, les deux versions sont identiques au bit
       près ;
    4. la META est identique champ par champ, valeur par valeur ;
    5. chaque bloc `% BEGIN-VERIFY` est identique à l'octet ;
    6. le corps hors META est identique une fois les accents retirés ;
    7. la fiche porte toujours `status: needs_review` ;
    8. le packet de revue est intact ;
    9. la substance de la décision est inchangée : quatre revues `PENDING`,
       `content_approval` faux, `release_blocking` vrai.

Une seule de ces conditions qui manque, et l'objet sort du lot.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import diacritic_requalification as req  # noqa: E402
import evidence_freshness as freshness  # noqa: E402

DECISION = "ACCEPT_ACCENT_ONLY_QUALIFICATION_REBIND"
DECISION_JSON = ROOT / "audit/HUMAN_DECISION_1SPE_TRIGO_OPTIONAL_EXTENSIONS_2026-08-23.json"
DISPOSITIONS = ROOT / "audit/ANOMALY_DISPOSITIONS.yaml"
OUTPUT_JSON = ROOT / "audit/TRIGO_ACCENT_REBIND_RECEIPT.json"
OUTPUT_MD = ROOT / "audit/TRIGO_ACCENT_REBIND_RECEIPT.md"

#: Périmètre nominatif et fermé. Un objet absent de ce tuple ne peut pas
#: hériter de la décision, quelle que soit la nature de son changement.
AUTHORIZED_OBJECT_IDS = ("1SPE-TRIGO-ME-003", "1SPE-TRIGO-ME-004", "1SPE-TRIGO-ME-005")

VERIFY_OPEN = "% BEGIN-VERIFY"
VERIFY_CLOSE = "% END-VERIFY"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


#: Versions historiques d'un fichier, indexées par empreinte. Le parcours de
#: l'historique lance un `git show` par révision : le refaire à chaque appel
#: rendait la suite de mutations inutilisable (cinq minutes pour dix-sept
#: cas). Le cache ne change aucun verdict, il évite de relire le même passé.
_HISTORIQUE: dict[str, dict[str, str]] = {}


def _versions_historiques(relative: str) -> dict[str, str]:
    if relative in _HISTORIQUE:
        return _HISTORIQUE[relative]
    revisions = subprocess.run(
        ["git", "log", "--all", "--format=%H", "--", relative],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split()
    versions: dict[str, str] = {}
    for revision in revisions:
        blob = subprocess.run(
            ["git", "show", f"{revision}:{relative}"], cwd=ROOT, capture_output=True
        )
        if blob.returncode:
            continue
        try:
            text = blob.stdout.decode("utf-8")
        except UnicodeDecodeError:
            continue
        versions.setdefault(_sha256_text(text), text)
    _HISTORIQUE[relative] = versions
    return versions


def _blob_with_digest(relative: str, digest: str) -> str | None:
    """La version dont le sha256 est `digest`, cherchée dans l'historique."""
    return _versions_historiques(relative).get(digest)


def _meta(text: str) -> dict[str, Any] | None:
    premiere = text.split("\n", 1)[0]
    if not premiere.startswith("% META:"):
        return None
    try:
        charge = json.loads(premiere[len("% META:"):])
    except ValueError:
        return None
    return charge if isinstance(charge, dict) else None


def _verify_blocks(text: str) -> list[str]:
    """Les blocs de vérification, dans l'ordre, tels quels."""
    blocs: list[str] = []
    reste = text
    while VERIFY_OPEN in reste:
        _, apres = reste.split(VERIFY_OPEN, 1)
        if VERIFY_CLOSE not in apres:
            blocs.append(apres)
            break
        bloc, reste = apres.split(VERIFY_CLOSE, 1)
        blocs.append(bloc)
    return blocs


def _body_without_meta(text: str) -> str:
    lignes = text.splitlines()
    return "\n".join(lignes[1:]) if lignes and lignes[0].startswith("% META:") else text


#: Le fichier de dispositions fait plus de cent soixante mille lignes : le
#: relire à chaque appel coûtait une quinzaine de secondes, et rendait la
#: suite de mutations impraticable. Le cache est indexé sur l'empreinte du
#: fichier : dès qu'il change — et `apply_rebind` le change — il est relu.
_DISPOSITIONS_CACHE: tuple[str, dict[str, Any]] | None = None


def _dispositions() -> dict[str, Any]:
    global _DISPOSITIONS_CACHE
    octets = DISPOSITIONS.read_bytes()
    empreinte = hashlib.sha256(octets).hexdigest()
    if _DISPOSITIONS_CACHE is None or _DISPOSITIONS_CACHE[0] != empreinte:
        charge = yaml.safe_load(octets.decode("utf-8"))["dispositions"]
        _DISPOSITIONS_CACHE = (empreinte, charge)
    return _DISPOSITIONS_CACHE[1]


def assess(root: Path = ROOT) -> dict[str, Any]:
    """Trie les trois objets nommés : couverts, exclus, et pourquoi."""
    decision = json.loads(DECISION_JSON.read_text(encoding="utf-8"))
    dispositions = _dispositions()
    par_objet = {str(o.get("object_id")): o for o in decision.get("objects") or []}
    disposition_par_objet = {
        str(record.get("object_id")): (fingerprint, record)
        for fingerprint, record in dispositions.items()
        if str(record.get("object_id")) in AUTHORIZED_OBJECT_IDS
    }

    # La substance de la décision doit être intacte : re-lier n'a le droit de
    # toucher qu'à l'empreinte de la source.
    substance: list[str] = []
    if decision.get("review_state") != "PENDING":
        substance.append("review_state n'est plus PENDING")
    if decision.get("required_reviews") != {
        "scientific": "PENDING", "pedagogical": "PENDING",
        "editorial": "PENDING", "variant": "PENDING",
    }:
        substance.append("les quatre revues ne sont plus toutes PENDING")
    if decision.get("content_approval") is not False:
        substance.append("content_approval n'est plus faux")
    if decision.get("release_blocking") is not True:
        substance.append("release_blocking n'est plus vrai")
    if decision.get("source_status") != "needs_review":
        substance.append("source_status n'est plus needs_review")

    couverts: list[dict[str, Any]] = []
    exclus: list[dict[str, Any]] = []

    for object_id in AUTHORIZED_OBJECT_IDS:
        refus: list[str] = list(substance)
        objet = par_objet.get(object_id)
        if objet is None:
            exclus.append({"object_id": object_id,
                           "refus": ["objet absent de la décision humaine"]})
            continue
        relative = str(objet.get("source_path"))
        chemin = root / relative
        courant = chemin.read_text(encoding="utf-8") if chemin.is_file() else None
        if courant is None:
            refus.append("source absente du dépôt")

        qualifie_sha = str(objet.get("current_source_sha", ""))
        avant = _blob_with_digest(relative, qualifie_sha)
        if avant is None:
            refus.append("version qualifiée introuvable dans l'historique")

        classe = None
        if avant is not None and courant is not None:
            classe = req.recompute_change_class(avant, courant)
            if classe == req.UNCHANGED:
                refus.append("source inchangée : rien à re-lier")
            elif classe != req.ACCENT_ONLY:
                refus.append(f"changement {classe}, hors du périmètre")

            meta_avant, meta_apres = _meta(avant), _meta(courant)
            if meta_avant is None or meta_apres is None:
                refus.append("META illisible")
            elif meta_avant != meta_apres:
                differences = sorted(
                    champ for champ in set(meta_avant) | set(meta_apres)
                    if meta_avant.get(champ) != meta_apres.get(champ)
                )
                refus.append(f"META modifiée : {differences}")

            if _verify_blocks(avant) != _verify_blocks(courant):
                refus.append("bloc de vérification modifié")

            if req.strip_accents(_body_without_meta(avant)) != req.strip_accents(
                _body_without_meta(courant)
            ):
                refus.append("corps modifié au-delà des accents")

        if courant is not None:
            meta = _meta(courant) or {}
            if meta.get("status") != "needs_review":
                refus.append(f"statut {meta.get('status')} : re-lier ne promeut rien")
            if meta.get("id") != object_id:
                refus.append("identifiant META incohérent")

        paquet = root / str(objet.get("current_packet_path", ""))
        if not paquet.is_file():
            refus.append("packet de revue absent")
        elif hashlib.sha256(paquet.read_bytes()).hexdigest() != str(
            objet.get("current_packet_sha256", "")
        ):
            refus.append("packet de revue modifié après qualification")

        empreinte, record = disposition_par_objet.get(object_id, (None, None))
        if empreinte is None:
            refus.append("aucune disposition ne porte cet objet")
        elif str(record.get("method_source_sha")) != qualifie_sha:
            refus.append("disposition et décision divergent sur la source qualifiée")

        entree = {
            "object_id": object_id,
            "source": relative,
            "anomaly_fingerprint": empreinte,
            "old_qualification_fingerprint": qualifie_sha,
            "new_qualification_fingerprint": _sha256_text(courant) if courant else None,
            "recomputed_change_class": classe,
            "meta_identical": classe is not None and _meta(avant) == _meta(courant),
            "verify_blocks_identical": (
                classe is not None and _verify_blocks(avant) == _verify_blocks(courant)
            ),
            "body_identical_without_accents": (
                classe is not None
                and req.strip_accents(_body_without_meta(avant))
                == req.strip_accents(_body_without_meta(courant))
            ),
        }
        if refus:
            entree["refus"] = sorted(set(refus))
            exclus.append(entree)
        else:
            couverts.append(entree)

    couverts.sort(key=lambda e: e["object_id"])
    exclus.sort(key=lambda e: e["object_id"])
    return {"covered": couverts, "excluded": exclus}


def build_receipt(reviewer: str, decision: str, root: Path = ROOT) -> dict[str, Any]:
    verdict = assess(root)
    couverts = verdict["covered"]
    receipt = {
        "artifact_type": "trigo_accent_rebind_receipt",
        "schema_version": 1,
        "generated_by": "scripts/build_trigo_accent_rebind.py",
        "approves_no_content": True,
        "promotes_no_status": True,
        "REVIEWER_IDENTITY": reviewer,
        "DECISION": decision,
        "OBJECT_IDS": [e["object_id"] for e in couverts],
        "OLD_QUALIFICATION_FINGERPRINTS": [
            e["old_qualification_fingerprint"] for e in couverts
        ],
        "NEW_QUALIFICATION_FINGERPRINTS": [
            e["new_qualification_fingerprint"] for e in couverts
        ],
        "ANOMALY_FINGERPRINTS": [e["anomaly_fingerprint"] for e in couverts],
        "ACCENT_ONLY_FORENSICS_DIGEST": req.payload_digest(couverts),
        "PEDAGOGICAL_CONTENT_UNCHANGED": bool(couverts) and all(
            e["meta_identical"]
            and e["verify_blocks_identical"]
            and e["body_identical_without_accents"]
            and e["recomputed_change_class"] == req.ACCENT_ONLY
            for e in couverts
        ),
        "scope": (
            "Re-liaison de la qualification 1SPE-TRIGO au texte courant, dont "
            "seule l'accentuation a changé. La décision humaine du 2026-08-23 "
            "reste entière : quatre revues PENDING, objets `needs_review`, "
            "dette bloquante. N'approuve aucun contenu, ne promeut aucun statut."
        ),
        "authorized_object_ids": list(AUTHORIZED_OBJECT_IDS),
        "inheritance": "aucun objet hors de OBJECT_IDS n'hérite de cette décision",
        "covered": couverts,
        "excluded": verdict["excluded"],
    }
    receipt["freshness"] = freshness.stamp(
        ["audit/HUMAN_DECISION_1SPE_TRIGO_OPTIONAL_EXTENSIONS_2026-08-23.json",
         "audit/ANOMALY_DISPOSITIONS.yaml"],
        root=root,
    )
    return receipt


def validate_receipt(receipt: dict[str, Any], root: Path = ROOT) -> list[str]:
    """Recalcule la preuve du receipt au lieu de la relire."""
    violations: list[str] = []
    if receipt.get("DECISION") != DECISION:
        violations.append("décision non reconnue")
    if not receipt.get("PEDAGOGICAL_CONTENT_UNCHANGED"):
        violations.append("contenu pédagogique non prouvé inchangé")
    hors_perimetre = set(receipt.get("OBJECT_IDS") or []) - set(AUTHORIZED_OBJECT_IDS)
    if hors_perimetre:
        violations.append(f"objets hors périmètre : {sorted(hors_perimetre)}")
    recalcul = assess(root)
    if [e["object_id"] for e in recalcul["covered"]] != list(receipt.get("OBJECT_IDS") or []):
        violations.append("le recalcul ne retrouve pas le même lot")
    if req.payload_digest(recalcul["covered"]) != receipt.get(
        "ACCENT_ONLY_FORENSICS_DIGEST"
    ):
        violations.append("empreinte de forensics divergente")
    return violations


def apply_rebind(receipt: dict[str, Any], root: Path = ROOT) -> int:
    """Réécrit l'empreinte de source sur toute la chaîne qui la porte.

    Trois artefacts la portent, et ils doivent rester d'accord : le packet de
    revue, la décision humaine, la disposition. En rebinder un seul laisserait
    la chaîne incohérente, ce que le gate signalerait aussitôt — et à juste
    titre. L'ordre suit les dépendances : le packet d'abord, car la décision
    scelle son empreinte ; la décision ensuite, car la disposition scelle la
    sienne.

    Rien d'autre n'est touché : les quatre revues restent `PENDING`, le statut
    reste `needs_review`, la dette reste bloquante.
    """
    import baseline_qualification as _baseline_qualification  # noqa: PLC0415
    from inventory_collection import _control_digest  # noqa: PLC0415

    violations = validate_receipt(receipt, root)
    if violations:
        raise ValueError(f"receipt invalide : {violations}")

    provenance = {
        "receipt": "audit/TRIGO_ACCENT_REBIND_RECEIPT.json",
        "decision": receipt["DECISION"],
        "reviewer_identity": receipt["REVIEWER_IDENTITY"],
        "change_class": req.ACCENT_ONLY,
    }
    couverts = {e["object_id"]: e for e in receipt["covered"]}
    decision = json.loads(DECISION_JSON.read_text(encoding="utf-8"))
    applique = 0
    empreintes_packet: dict[str, str] = {}

    for objet in decision.get("objects") or []:
        entree = couverts.get(str(objet.get("object_id")))
        if entree is None:
            continue
        nouvelle = entree["new_qualification_fingerprint"]

        # 1. Le packet de revue porte l'empreinte du texte qu'il fait relire.
        chemin_packet = root / str(objet["current_packet_path"])
        packet = json.loads(chemin_packet.read_text(encoding="utf-8"))
        if packet.get("current_source_sha") != entree["old_qualification_fingerprint"]:
            raise ValueError(
                f"packet non aligné sur la qualification : {entree['object_id']}"
            )
        packet["current_source_sha"] = nouvelle
        chemin_packet.write_text(
            json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        empreintes_packet[entree["object_id"]] = hashlib.sha256(
            chemin_packet.read_bytes()
        ).hexdigest()

        # 2. La décision scelle la source ET l'empreinte du packet.
        objet["current_source_sha"] = nouvelle
        objet["current_packet_sha256"] = empreintes_packet[entree["object_id"]]
        objet["requalification"] = dict(
            provenance, previous_source_sha=entree["old_qualification_fingerprint"]
        )
        applique += 1

    decision["control_digest"] = "sha256:" + "0" * 64
    decision["control_digest"] = _control_digest(decision)
    DECISION_JSON.write_text(
        json.dumps(decision, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # 3. La disposition scelle la source, le packet et le fichier de décision.
    nouveau_sha_decision = "sha256:" + hashlib.sha256(
        DECISION_JSON.read_bytes()
    ).hexdigest()
    document = yaml.safe_load(DISPOSITIONS.read_text(encoding="utf-8"))
    records = document["dispositions"]
    for entree in receipt["covered"]:
        record = records[entree["anomaly_fingerprint"]]
        record["method_source_sha"] = entree["new_qualification_fingerprint"]
        record["review_packet_sha"] = empreintes_packet[entree["object_id"]]
        record["qualification_policy_digest"] = nouveau_sha_decision
        # Le schéma des dispositions nomme déjà ce champ, et le décrit
        # exactement : « re-liaison d'une qualification existante au texte
        # courant, sous une décision humaine nommée ; ne promeut aucun statut
        # et n'approuve aucun contenu ». Inventer un champ voisin aurait
        # dupliqué une notion qui existe.
        record["requalification"] = dict(
            provenance,
            previous_method_source_sha=entree["old_qualification_fingerprint"],
        )
        # `qualification_digest` scelle les champs qui donnent son sens à la
        # qualification, dont `qualification_policy_digest` qui vient de
        # changer. Le laisser tel quel rendrait le registre incohérent avec
        # lui-même — le gate le dit, et il a raison.
        record["qualification_digest"] = _baseline_qualification.qualification_digest(
            record
        )
    document["control_digest"] = "sha256:" + "0" * 64
    texte = yaml.safe_dump(document, allow_unicode=True, sort_keys=True, width=100)
    relu = yaml.safe_load(texte)
    relu["control_digest"] = _control_digest(relu)
    DISPOSITIONS.write_text(
        yaml.safe_dump(relu, allow_unicode=True, sort_keys=True, width=100),
        encoding="utf-8",
    )
    return applique


def render_markdown(receipt: dict[str, Any]) -> str:
    lignes = [
        "# Receipt — re-liaison accentuelle des extensions 1SPE-TRIGO",
        "",
        f"- `REVIEWER_IDENTITY` : `{receipt['REVIEWER_IDENTITY']}`",
        f"- `DECISION` : `{receipt['DECISION']}`",
        f"- `OBJECT_IDS` : {', '.join(f'`{i}`' for i in receipt['OBJECT_IDS'])}",
        f"- `ACCENT_ONLY_FORENSICS_DIGEST` : `{receipt['ACCENT_ONLY_FORENSICS_DIGEST']}`",
        f"- `PEDAGOGICAL_CONTENT_UNCHANGED` : `{receipt['PEDAGOGICAL_CONTENT_UNCHANGED']}`",
        "",
        receipt["scope"],
        "",
        "| Objet | Ancienne empreinte | Nouvelle empreinte | Classe |",
        "|---|---|---|---|",
    ]
    for entree in receipt["covered"]:
        lignes.append(
            f"| `{entree['object_id']}` | `{entree['old_qualification_fingerprint'][:16]}…` "
            f"| `{entree['new_qualification_fingerprint'][:16]}…` "
            f"| {entree['recomputed_change_class']} |"
        )
    if receipt["excluded"]:
        lignes += ["", f"## Exclus ({len(receipt['excluded'])})", ""]
        for entree in receipt["excluded"]:
            lignes.append(
                f"- `{entree['object_id']}` : {', '.join(entree['refus'])}"
            )
    lignes.append("")
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved-by", required=True)
    parser.add_argument("--decision", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)

    if args.decision != DECISION:
        print(f"décision non reconnue: {args.decision}")
        return 2

    receipt = build_receipt(args.approved_by, args.decision)
    OUTPUT_JSON.write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    OUTPUT_MD.write_text(render_markdown(receipt), encoding="utf-8")

    applique = apply_rebind(receipt) if args.apply else 0
    print(json.dumps({
        "OBJECT_IDS": receipt["OBJECT_IDS"],
        "PEDAGOGICAL_CONTENT_UNCHANGED": receipt["PEDAGOGICAL_CONTENT_UNCHANGED"],
        "EXCLUDED": len(receipt["excluded"]),
        "APPLIED": applique,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
