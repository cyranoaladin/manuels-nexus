"""LOT R — Récolte T0 : identifie et transpose les contenus du dépôt NSI (CORPUS_NSI)
couvrant les capacités d'un chapitre du manuel.

Pipeline adapté à la structure réelle du corpus :
- Découverte des séquences par contracts/*.yml (source structurée, prioritaire)
- Matching capacité↔séquence par identifiants de substance (contrats), scoring lexical en repli
- Récolte : .md renommés en clair, code/ tel quel, fiches cours, contrat, verdicts de substance
- Dédoublonnage insensible à la casse (P07_tp vs P07_TP)
- Conversion pandoc + md2nexus.lua → .candidate.tex
- Rapport de transposition enrichi (verdicts de substance, statuts de revue humaine)
"""
import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from common import CORPUS_NSI, ROOT, write_json

CORPUS = CORPUS_NSI
SUPPORTS = CORPUS / "03_progressions" / "supports"
CONTRACTS_DIR = SUPPORTS / "contracts"
FICHES_COURS_DIR = CORPUS / "03_progressions" / "fiches_cours"
SUBSTANCE_DIR = CORPUS / "substance_reviews" / "campaign"
HUMAN_REVIEW_CSV = CORPUS / "human_review_register.csv"

# Mapping type réel → nom clair dans _harvest
TYPE_RENAME = {
    "cours": "cours.md",
    "trace": "trace.md",
    "td": "td.md",
    "tp": "tp.md",
    "corrige": "corrige.md",
    "evaluation": "evaluation.md",
    "bareme": "bareme.md",
    "remediation": "remediation.md",
    "version_amenagee": "version_amenagee.md",
}

STOP = {"les", "des", "une", "un", "de", "du", "la", "le", "et", "en",
        "d'un", "d'une", "dans", "par", "sur"}

# Canon sequences (root-level, different structure)
CANON_ROOTS = [
    CORPUS / "premiere" / "sequences",
    CORPUS / "terminale" / "sequences",
]


def keywords(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-zà-ÿ]{4,}", text.lower()) if w not in STOP}


def load_contrat(chap: str) -> dict:
    return yaml.safe_load(
        (ROOT / "chapitres" / chap / "contrat.yaml").read_text(encoding="utf-8")
    )


def load_contracts() -> dict[str, dict]:
    """Charge tous les contrats de séquence depuis contracts/*.yml.
    Retourne {seq_id: contract_data}."""
    contracts = {}
    if not CONTRACTS_DIR.exists():
        return contracts
    for f in sorted(CONTRACTS_DIR.glob("*_contract.yml")):
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        seq_id = data.get("sequence", f.stem.replace("_contract", ""))
        data["_contract_path"] = str(f)
        contracts[seq_id] = data
    return contracts


def find_sequence_dir(seq_id: str) -> Path | None:
    """Trouve le répertoire de la séquence dans supports/premiere/ ou supports/terminale/."""
    for level in ("premiere", "terminale"):
        d = SUPPORTS / level / seq_id
        if d.exists() and d.is_dir():
            return d
    return None


KNOWN_TYPES = [
    "corrige_professeur", "version_amenagee", "tests_attendus",
    "cours", "trace", "td", "tp", "corrige", "evaluation",
    "bareme", "remediation", "starter",
]


def parse_sequence_files(seq_dir: Path, seq_id: str) -> dict[str, Path]:
    """Parse les fichiers d'une séquence, dédoublonne par (type, slug) insensible à la casse.
    Préfère le fichier le plus long (plus de contenu)."""
    files_by_key: dict[str, list[Path]] = {}
    prefix = seq_id.lower() + "_"
    for f in seq_dir.iterdir():
        if f.is_dir() or not f.name.endswith(".md"):
            continue
        name_lower = f.name.lower()
        if not name_lower.startswith(prefix):
            continue
        rest = name_lower[len(prefix):-3]  # strip prefix and .md
        # Match against known types (longest first to catch multi-word types)
        ftype = None
        slug = None
        for t in KNOWN_TYPES:
            if rest.startswith(t + "_"):
                ftype = t
                slug = rest[len(t) + 1:]
                break
            elif rest == t:
                ftype = t
                slug = ""
                break
        if ftype is None:
            continue
        key = f"{ftype}|{slug}"
        files_by_key.setdefault(key, []).append(f)

    # Dédoublonnage : garder le fichier le plus long par clé
    result = {}
    for key, paths in files_by_key.items():
        best = max(paths, key=lambda p: p.stat().st_size)
        result[key] = best
    return result


def classify_files(parsed: dict[str, Path]) -> dict[str, list[Path]]:
    """Classe les fichiers par type (cours, td, tp, etc.), séparant principal et complément."""
    by_type: dict[str, list[Path]] = {}
    for key, path in parsed.items():
        ftype = key.split("|")[0]
        # Normalize type
        norm = ftype
        if norm == "corrige_professeur":
            continue  # handled via code/ directory
        by_type.setdefault(norm, []).append(path)
    return by_type


def load_substance_verdicts(capacity_ids: list[str]) -> dict[str, dict]:
    """Charge les verdicts de substance pour les capacités données."""
    verdicts = {}
    if not SUBSTANCE_DIR.exists():
        return verdicts
    for cap_id in capacity_ids:
        f = SUBSTANCE_DIR / f"{cap_id}_substance_review.json"
        if f.exists():
            data = json.loads(f.read_text(encoding="utf-8"))
            caps = data.get("capacities", [])
            for c in caps:
                if c.get("capacity_id") == cap_id:
                    verdicts[cap_id] = {
                        "verdict": c.get("verdict", "unknown"),
                        "justification": c.get("justification", ""),
                        "scientific_flags": c.get("scientific_flags", []),
                    }
                    break
    return verdicts


def load_human_review(seq_id: str) -> list[dict]:
    """Extrait les lignes du human_review_register.csv pour une séquence."""
    if not HUMAN_REVIEW_CSV.exists():
        return []
    rows = []
    with open(HUMAN_REVIEW_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if seq_id.lower() in (r.get("sequence", "") or r.get("ressource", "")).lower():
                rows.append(dict(r))
    return rows


def find_fiches_cours(seq_id: str) -> list[Path]:
    """Trouve les fiches de cours associées à une séquence."""
    fiches = []
    for level in ("premiere", "terminale"):
        d = FICHES_COURS_DIR / level / seq_id
        if d.exists():
            fiches.extend(sorted(d.glob("*.md")))
    return fiches


def match_sequences_by_contract(
    contracts: dict[str, dict],
    chap_contrat: dict,
    mapping: dict[str, list[str]],
) -> list[str]:
    """Identifie les séquences par le mapping explicite chapitre→séquences.
    Le mapping est donné par docs/09. En repli, utilise les capacités officielles des contrats."""
    chap_id = chap_contrat["chapitre"]
    theme = chap_contrat.get("theme", "")

    # Priorité 1 : mapping explicite
    if chap_id in mapping:
        return mapping[chap_id]

    # Priorité 2 : matching par capacités officielles dans les contrats
    chap_caps = set()
    for cap in chap_contrat.get("capacites", []):
        ref = cap.get("ref_capacite", "")
        if ref:
            chap_caps.add(ref)

    matched = []
    for seq_id, contract in contracts.items():
        contract_caps = set(contract.get("capacites_officielles", []))
        if contract_caps & chap_caps:
            matched.append(seq_id)

    if matched:
        return matched

    # Priorité 3 : scoring lexical sur le thème du contrat
    theme_kw = keywords(theme + " " + " ".join(
        c.get("libelle_eleve", "") for c in chap_contrat.get("capacites", [])
    ))
    scores = []
    for seq_id, contract in contracts.items():
        text = contract.get("theme", "") + " " + " ".join(
            contract.get("notions_exigibles", [])
        )
        kw = keywords(text)
        sc = len(kw & theme_kw) / max(1, len(theme_kw))
        if sc > 0.15:
            scores.append((sc, seq_id))
    scores.sort(reverse=True)
    return [sid for _, sid in scores[:4]]


def load_mapping() -> dict[str, list[str]]:
    """Charge le mapping chapitre→séquences depuis docs/09 s'il existe."""
    mapping_file = ROOT / "docs" / "09_mapping_sequences_chapitres.md"
    mapping: dict[str, list[str]] = {}
    if not mapping_file.exists():
        return mapping
    text = mapping_file.read_text(encoding="utf-8")
    # Parse lines like: | 1NSI-TYPES-CONSTRUITS | P04 |
    for line in text.splitlines():
        if "|" not in line or line.strip().startswith("|---"):
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]
        if len(parts) >= 2:
            chap = parts[0]
            if chap.startswith("1NSI-") or chap.startswith("TNSI-"):
                seq_ids = re.findall(r"[PT]\d{2}", parts[1])
                if seq_ids:
                    mapping[chap] = seq_ids
    return mapping


def convert_md(md: Path, out_tex: Path) -> bool:
    lua = ROOT / "scripts" / "md2nexus.lua"
    cmd = ["pandoc", str(md), "-f", "markdown", "-t", "latex",
           "--lua-filter", str(lua), "-o", str(out_tex)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode == 0


def harvest(chap: str) -> int:
    contrat = load_contrat(chap)
    chap_dir = ROOT / "chapitres" / chap
    harvest_dir = chap_dir / "_harvest"
    if harvest_dir.exists():
        shutil.rmtree(harvest_dir)
    harvest_dir.mkdir(parents=True)

    contracts = load_contracts()
    if not contracts:
        print("Aucun contrat trouvé dans le corpus — angle mort global.")
        write_json(chap_dir / "rapport_transposition.json", {
            "chapitre": chap, "sequences": [], "capacites": {
                c["code"]: {"sources_T0": [], "angle_mort": "corpus indisponible"}
                for c in contrat["capacites"]
            }
        })
        return 1

    mapping = load_mapping()
    matched_seqs = match_sequences_by_contract(contracts, contrat, mapping)

    if not matched_seqs:
        print(f"Aucune séquence trouvée pour {chap}.")
        write_json(chap_dir / "rapport_transposition.json", {
            "chapitre": chap, "sequences": [], "capacites": {
                c["code"]: {"sources_T0": [], "angle_mort": "aucune séquence matchée"}
                for c in contrat["capacites"]
            }
        })
        return 1

    # Collecter les identifiants de capacités officielles des séquences matchées
    all_cap_ids = []
    for sid in matched_seqs:
        if sid in contracts:
            all_cap_ids.extend(contracts[sid].get("capacites_officielles", []))

    # Charger verdicts de substance et revues humaines
    verdicts = load_substance_verdicts(all_cap_ids)

    rapport = {"chapitre": chap, "sequences": [], "capacites": {}}
    converted, failed = 0, 0

    for seq_id in matched_seqs:
        seq_dir = find_sequence_dir(seq_id)
        if seq_dir is None:
            print(f"  WARN: séquence {seq_id} introuvable dans supports/")
            continue

        dest = harvest_dir / seq_id
        dest.mkdir(exist_ok=True)

        # Parse et classifie les fichiers
        parsed = parse_sequence_files(seq_dir, seq_id)
        by_type = classify_files(parsed)

        entry = {
            "seq_id": seq_id,
            "path": str(seq_dir.relative_to(CORPUS)),
            "contract": contracts.get(seq_id, {}).get("theme", ""),
            "capacites_officielles": contracts.get(seq_id, {}).get("capacites_officielles", []),
            "fichiers": [],
        }

        # Copier les .md avec renommage clair
        for ftype, paths in sorted(by_type.items()):
            for i, src in enumerate(sorted(paths)):
                if "complement" in src.name.lower():
                    suffix = "_complement"
                elif len(paths) > 1 and i > 0:
                    suffix = f"_{i}"
                else:
                    suffix = ""

                clear_name = f"{ftype}{suffix}.md"
                shutil.copy2(src, dest / clear_name)

                # Conversion pandoc
                tex_name = clear_name.replace(".md", ".candidate.tex")
                ok = convert_md(src, dest / tex_name)
                converted += ok
                failed += (not ok)
                entry["fichiers"].append({
                    "original": src.name,
                    "renamed": clear_name,
                    "converted": bool(ok),
                })

        # Copier le dossier code/ tel quel
        code_dir = seq_dir / "code"
        if code_dir.exists() and code_dir.is_dir():
            shutil.copytree(code_dir, dest / "code", dirs_exist_ok=True)
            entry["fichiers"].append({"original": "code/", "renamed": "code/", "converted": None})

        # Copier les fiches de cours
        fiches = find_fiches_cours(seq_id)
        for fiche in fiches:
            shutil.copy2(fiche, dest / fiche.name)
            ok = convert_md(fiche, dest / (fiche.stem + ".candidate.tex"))
            converted += ok
            failed += (not ok)
            entry["fichiers"].append({
                "original": f"fiches_cours/{fiche.name}",
                "renamed": fiche.name,
                "converted": bool(ok),
            })

        # Copier le contrat YAML
        if seq_id in contracts:
            contract_path = Path(contracts[seq_id]["_contract_path"])
            shutil.copy2(contract_path, dest / f"{seq_id}_contract.yml")
            entry["fichiers"].append({
                "original": contract_path.name,
                "renamed": f"{seq_id}_contract.yml",
                "converted": None,
            })

        # Verdicts de substance
        seq_caps = contracts.get(seq_id, {}).get("capacites_officielles", [])
        entry["verdicts_substance"] = {
            cap: verdicts.get(cap, {"verdict": "non évalué"})
            for cap in seq_caps
        }

        # Revue humaine
        entry["human_review"] = load_human_review(seq_id)

        rapport["sequences"].append(entry)

    # Rapport par capacité du chapitre
    for cap in contrat["capacites"]:
        cap_code = cap["code"]
        sources = []
        for entry in rapport["sequences"]:
            sources.append({
                "seq_id": entry["seq_id"],
                "fichiers_count": len(entry["fichiers"]),
                "capacites_officielles": entry["capacites_officielles"],
                "verdicts": entry.get("verdicts_substance", {}),
            })
        rapport["capacites"][cap_code] = {
            "libelle": cap.get("libelle_eleve", ""),
            "sources_T0": sources,
            "angle_mort": None if sources else "aucune source T0 identifiée",
        }

    rapport["conversion"] = {"ok": converted, "echecs": failed}
    write_json(chap_dir / "rapport_transposition.json", rapport)

    # Résumé
    n_seq = len(rapport["sequences"])
    n_files = sum(len(e["fichiers"]) for e in rapport["sequences"])
    manquants = [c for c, v in rapport["capacites"].items() if v["angle_mort"]]
    print(f"{n_seq} séquences récoltées ({n_files} fichiers), "
          f"{converted} conversions pandoc ({failed} échecs), "
          f"angles morts : {manquants or 'aucun'}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chap", required=True)
    args = ap.parse_args()
    sys.exit(harvest(args.chap))
