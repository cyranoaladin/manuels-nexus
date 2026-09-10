#!/usr/bin/env python3
"""Enveloppe de fraîcheur commune aux artefacts d'audit.

Un artefact peut rester valable après un changement de HEAD : ce qui compte
n'est pas le commit, ce sont les octets que le producteur a réellement lus. À
l'inverse, un artefact régénéré sur un HEAD ancien ne devient pas courant parce
qu'on l'affirme.

Quatre champs, et une seule façon de les interpréter :

    EVIDENCE_HEAD         le HEAD au moment du calcul, pour la traçabilité
    INPUT_DIGEST          empreinte des entrées telles qu'elles étaient alors
    CURRENT_INPUT_DIGEST  empreinte des mêmes entrées maintenant
    FRESHNESS_STATUS      CURRENT_BY_INPUT_DIGEST, STALE_INPUTS_CHANGED,
                          STALE_INPUT_ARTIFACT_IS_ITSELF_STALE,
                          ou UNVERIFIABLE_NO_DECLARED_INPUTS

`CURRENT_BY_INPUT_DIGEST` est la seule valeur qui autorise à présenter
l'artefact comme l'état courant, et elle ne se déclare pas : elle se recalcule.

LA FRAÎCHEUR SE PROPAGE.

L'empreinte d'entrée prouve « ces octets n'ont pas changé depuis ma lecture ».
Elle ne prouve pas « ces octets décrivaient le dépôt courant ». La différence
n'apparaît que sur les artefacts dérivés, et c'est là qu'elle coûte cher :
ce sont eux qu'on cite.

Le cas qui l'a révélée : la réconciliation des populations mathématiques
déclarait `CURRENT_BY_INPUT_DIGEST` en lisant un `DIMENSION_MATHEMATICS.json`
non régénéré depuis l'écriture de soixante-deux objets. Son enveloppe était
honnête, son verdict faux. Un artefact dont une entrée porte elle-même une
enveloppe périmée est désormais `STALE_INPUT_ARTIFACT_IS_ITSELF_STALE`.

Une entrée sans enveloppe — un `.tex`, un `.yaml` de contrat — n'est pas
pénalisée : n'ayant rien à déclarer, elle ne peut pas être périmée.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]

CURRENT = "CURRENT_BY_INPUT_DIGEST"
STALE = "STALE_INPUTS_CHANGED"
STALE_TRANSITIVE = "STALE_INPUT_ARTIFACT_IS_ITSELF_STALE"
UNVERIFIABLE = "UNVERIFIABLE_NO_DECLARED_INPUTS"


def head_sha(root: Path = ROOT) -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def digest_paths(paths: Iterable[str], root: Path = ROOT) -> str:
    """Empreinte ordonnée d'un ensemble de chemins déclarés."""
    accumulator = hashlib.sha256()
    for relative in sorted(set(paths)):
        accumulator.update(relative.encode("utf-8"))
        accumulator.update(b"\x00")
        candidate = root / relative
        if candidate.is_file():
            accumulator.update(hashlib.sha256(candidate.read_bytes()).digest())
        else:
            accumulator.update(b"ABSENT")
        accumulator.update(b"\x00")
    return "sha256:" + accumulator.hexdigest()


def stamp(input_paths: Iterable[str], root: Path = ROOT) -> dict[str, Any]:
    """Enveloppe à inscrire dans un artefact au moment de sa production."""
    paths = sorted(set(input_paths))
    return {
        "EVIDENCE_HEAD": head_sha(root),
        "INPUT_PATHS": paths,
        "INPUT_DIGEST": digest_paths(paths, root),
    }


def _stale_input_artifacts(
    paths: Iterable[str],
    root: Path,
    seen: frozenset[str],
) -> list[str]:
    """Entrees qui portent elles-memes une enveloppe et ne sont pas courantes.

    `seen` coupe les cycles : deux artefacts qui se citent l'un l'autre ne
    doivent pas faire boucler l'evaluation.
    """
    stale: list[str] = []
    for relative in sorted(set(paths)):
        if relative in seen or not str(relative).endswith(".json"):
            continue
        candidate = root / relative
        if not candidate.is_file():
            continue
        try:
            payload = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        envelope = payload.get("freshness") if isinstance(payload, dict) else None
        if not isinstance(envelope, dict) or not envelope:
            continue
        verdict = assess(envelope, root, _seen=seen | {relative})
        if verdict["FRESHNESS_STATUS"] not in (CURRENT, UNVERIFIABLE):
            stale.append(str(relative))
    return stale


def assess(
    envelope: dict[str, Any],
    root: Path = ROOT,
    *,
    _seen: frozenset[str] = frozenset(),
) -> dict[str, Any]:
    """Fraîcheur d'un artefact déjà produit, recalculée sur le dépôt courant.

    Un producteur qui lit le dépôt entier ne peut pas être déclaré courant sur
    la seule stabilité de ses fichiers d'entrée : sa mesure décrit un état du
    dépôt, et tout commit peut l'avoir déplacée. Pour ceux-là, la fraîcheur se
    juge sur le HEAD d'observation.
    """
    if envelope.get("WHOLE_REPOSITORY_INPUT"):
        observed = set(envelope.get("OBSERVATION_HEADS") or [])
        current = head_sha(root)
        return {
            "EVIDENCE_HEAD": envelope.get("EVIDENCE_HEAD"),
            "CURRENT_HEAD": current,
            "OBSERVATION_HEADS": sorted(observed),
            "INPUT_DIGEST": envelope.get("INPUT_DIGEST"),
            "CURRENT_INPUT_DIGEST": digest_paths(
                envelope.get("INPUT_PATHS") or [], root
            ),
            "FRESHNESS_STATUS": (
                CURRENT if observed == {current} and current
                else STALE if observed
                else UNVERIFIABLE
            ),
        }
    paths = envelope.get("INPUT_PATHS") or []
    if not paths:
        return {
            "EVIDENCE_HEAD": envelope.get("EVIDENCE_HEAD"),
            "INPUT_DIGEST": envelope.get("INPUT_DIGEST"),
            "CURRENT_INPUT_DIGEST": None,
            "FRESHNESS_STATUS": UNVERIFIABLE,
        }
    current = digest_paths(paths, root)
    stale_inputs = _stale_input_artifacts(paths, root, _seen)
    if current != envelope.get("INPUT_DIGEST"):
        status = STALE
    elif stale_inputs:
        status = STALE_TRANSITIVE
    else:
        status = CURRENT
    return {
        "EVIDENCE_HEAD": envelope.get("EVIDENCE_HEAD"),
        "CURRENT_HEAD": head_sha(root),
        "INPUT_DIGEST": envelope.get("INPUT_DIGEST"),
        "CURRENT_INPUT_DIGEST": current,
        "STALE_INPUTS": stale_inputs,
        "FRESHNESS_STATUS": status,
    }


def assess_artifact(path: Path, root: Path = ROOT) -> dict[str, Any]:
    payload = json.loads((root / path).read_text(encoding="utf-8"))
    return assess(
        payload.get("freshness") or {}, root, _seen=frozenset({str(path)})
    )


# ---------------------------------------------------------------------------
# Trois digests, parce qu'une preuve ne depend pas de tout
# ---------------------------------------------------------------------------
#
# Un digest unique confondait deux questions distinctes : « le contenu
# enseigne a-t-il change ? » et « le rendu a-t-il change ? ». Changer une
# couleur de charte perimait alors la validation scientifique d'un chapitre,
# et un manifeste de livre -- qui decide de la liste et de l'ordre des
# chapitres -- n'entrait dans aucun digest alors qu'il decide du contenu.
#
#   CONTENT_SEMANTIC_DIGEST   ce que l'eleve et le professeur lisent
#   RENDER_SOURCE_DIGEST      la facon dont cela s'imprime
#   TOOLCHAIN_DIGEST          le dispositif qui reconstruit
#
# Dependances des preuves :
#   scientifique / pedagogique   CONTENT
#   visuelle / D7                CONTENT + RENDER
#   reproductibilite / release   les trois

#: Ce qui decide de ce qui est LU : objets, contrats, capacites, referentiels,
#: textes officiels, manifestes de livres, et la logique d'assemblage qui
#: choisit les objets, leur ordre et la variante eleve ou professeur.
CONTENT_SEMANTIC_GLOBS = (
    "Mathematiques/manuel-maths/chapitres/**",
    "NSI/chapitres/**",
    "Mathematiques/manuel-maths/referentiel/**",
    "NSI/referentiel/**",
    "NSI/manifests/**",
    "Mathematiques/manuel-maths/manifests/**",
    "docs/programmes/**",
    "Mathematiques/manuel-maths/sources/txt/**",
    "NSI/sources/**",
    "Mathematiques/manuel-maths/scripts/assemble*.py",
    "NSI/scripts/assemble*.py",
    "gabarits/common/chapitre_master.tex",
    "Mathematiques/manuel-maths/gabarits/chapitre_master.tex",
    "NSI/gabarits/book_master.tex",
    "NSI/gabarits/chapitre_master.tex",
)

#: Ce qui decide de la FORME : classes, styles, charte, polices, logos,
#: couvertures, composition des marges. Rien de cela ne change un enonce.
RENDER_SOURCE_GLOBS = (
    "gabarits/**/*.cls", "gabarits/**/*.sty", "gabarits/**/*.lua",
    "gabarits/**/*.otf", "gabarits/**/*.png",
    "gabarits/common/nexus-*.tex",
    "Mathematiques/manuel-maths/gabarits/**/*.cls",
    "Mathematiques/manuel-maths/gabarits/**/*.sty",
    "Mathematiques/manuel-maths/gabarits/**/*.lua",
    "Mathematiques/manuel-maths/gabarits/**/*.otf",
    "Mathematiques/manuel-maths/gabarits/**/*.png",
    "Mathematiques/manuel-maths/gabarits/nexus-*.tex",
    "NSI/gabarits/**/*.cls", "NSI/gabarits/**/*.sty", "NSI/gabarits/**/*.lua",
    "NSI/gabarits/**/*.otf", "NSI/gabarits/**/*.png",
    "NSI/gabarits/nexus-*.tex",
)

#: Ce qui decide de la RECONSTRUCTION : dependances figees, outillage epingle,
#: workflows, configuration deterministe.
TOOLCHAIN_GLOBS = (
    "requirements-ci-audit.txt",
    "pyproject.toml",
    "Mathematiques/manuel-maths/release/**",
    ".github/workflows/**",
)


def _tree_blobs(root: Path, commit: str) -> dict[str, str]:
    """Chemins suivis et identifiant de blob, en UN seul appel a Git.

    `git ls-tree -r` donne deja « mode type sha<TAB>chemin » : interroger Git
    fichier par fichier coutait neuf mille processus par digest.
    """
    try:
        completed = subprocess.run(
            ["git", "ls-tree", "-r", commit],
            cwd=root, capture_output=True, text=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return {}
    blobs: dict[str, str] = {}
    for ligne in completed.stdout.splitlines():
        entete, _, chemin = ligne.partition("\t")
        morceaux = entete.split()
        if chemin and len(morceaux) >= 3:
            blobs[chemin] = morceaux[2]
    return blobs


def _glob_regex(motif: str) -> re.Pattern[str]:
    """Traduit un motif de chemin en expression reguliere.

    `**` traverse les repertoires, `*` s'arrete au separateur. Python 3.12 n'a
    pas `PurePath.full_match` : la traduction est explicite plutot que
    dependante d'une version.
    """
    morceaux, i = [], 0
    while i < len(motif):
        if motif.startswith("**/", i):
            morceaux.append("(?:[^/]+/)*")
            i += 3
        elif motif.startswith("**", i):
            morceaux.append(".*")
            i += 2
        elif motif[i] == "*":
            morceaux.append("[^/]*")
            i += 1
        elif motif[i] == "?":
            morceaux.append("[^/]")
            i += 1
        else:
            morceaux.append(re.escape(motif[i]))
            i += 1
    return re.compile("".join(morceaux) + r"\Z")


_MOTIFS = None


def classify(path: str) -> set[str]:
    """Les familles de digest auxquelles un chemin appartient."""
    global _MOTIFS
    if _MOTIFS is None:
        _MOTIFS = {
            "CONTENT": [_glob_regex(m) for m in CONTENT_SEMANTIC_GLOBS],
            "RENDER": [_glob_regex(m) for m in RENDER_SOURCE_GLOBS],
            "TOOLCHAIN": [_glob_regex(m) for m in TOOLCHAIN_GLOBS],
        }
    return {
        nom for nom, motifs in _MOTIFS.items()
        if any(motif.match(path) for motif in motifs)
    }


#: Calculer sur l'ARBRE DE TRAVAIL et non sur un commit. Indispensable pour
#: eprouver le modele par mutation : une mutation non commitee doit deja se
#: voir, sinon le digest ne protege que ce qui est deja fige.
WORKTREE = "WORKTREE"


def _worktree_blob(root: Path, path: str) -> str:
    """Identifiant de blob Git d'un fichier de l'arbre de travail.

    Recalcule la meme empreinte que `git rev-parse <commit>:<path>` --
    sha1 de « blob <taille>\\0 » suivi du contenu -- pour que les deux modes
    soient comparables. Les melanger donnerait deux digests differents pour un
    contenu identique, et rendrait toute mutation indetectable.
    """
    fichier = root / path
    if not fichier.is_file():
        return "ABSENT"
    contenu = fichier.read_bytes()
    entete = f"blob {len(contenu)}\0".encode()
    return hashlib.sha1(entete + contenu).hexdigest()  # noqa: S324


def _family_digest(root: Path, commit: str, famille: str) -> str:
    blobs = _tree_blobs(root, "HEAD" if commit == WORKTREE else commit)
    if commit == WORKTREE:
        blobs = {chemin: _worktree_blob(root, chemin) for chemin in blobs}
    lignes = [
        f"{chemin}:{blob}"
        for chemin, blob in sorted(blobs.items())
        if famille in classify(chemin)
    ]
    empreinte = hashlib.sha256("\n".join(lignes).encode("utf-8")).hexdigest()
    return f"sha256:{empreinte}"


def content_semantic_digest(root: Path = ROOT, commit: str = "HEAD") -> str:
    """Empreinte de tout ce qui peut changer ce qui est enseigne ou lu."""
    return _family_digest(root, commit, "CONTENT")


def render_source_digest(root: Path = ROOT, commit: str = "HEAD") -> str:
    """Empreinte de tout ce qui change le rendu imprime."""
    return _family_digest(root, commit, "RENDER")


def toolchain_digest(root: Path = ROOT, commit: str = "HEAD") -> str:
    """Empreinte du dispositif de reconstruction."""
    return _family_digest(root, commit, "TOOLCHAIN")


def source_digests(root: Path = ROOT, commit: str = "HEAD") -> dict[str, str]:
    return {
        "CONTENT_SEMANTIC_DIGEST": content_semantic_digest(root, commit),
        "RENDER_SOURCE_DIGEST": render_source_digest(root, commit),
        "TOOLCHAIN_DIGEST": toolchain_digest(root, commit),
    }


class AmbiguousReleaseTag(Exception):
    """Plusieurs tags de release designent le meme candidat.

    Prendre le premier reviendrait a choisir la release au hasard de l'ordre
    alphabetique. Le controle echoue, et un humain tranche.
    """


def release_tag_identity(root: Path = ROOT, commit: str = "HEAD") -> dict[str, Any]:
    """Identite complete d'un tag de release.

    Un tag ANNOTE est un objet Git distinct du commit qu'il reference : les
    deux n'ont pas le meme SHA. Les confondre sous un unique RELEASE_TAG_SHA
    rendait impossible de dire lequel on citait.

        RELEASE_TAG_NAME        le nom, tel qu'un humain le lit
        RELEASE_TAG_OBJECT_SHA  l'objet tag lui-meme (None si tag leger)
        RELEASE_COMMIT_SHA      le commit reference
        RELEASE_TREE_SHA        l'arbre de ce commit -- le contenu publie
    """
    vide: dict[str, Any] = {
        "RELEASE_TAG_NAME": None,
        "RELEASE_TAG_OBJECT_SHA": None,
        "RELEASE_COMMIT_SHA": None,
        "RELEASE_TREE_SHA": None,
    }
    try:
        completed = subprocess.run(
            ["git", "tag", "--points-at", commit, "--list", "release/*"],
            cwd=root, capture_output=True, text=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return vide
    tags = sorted(nom for nom in completed.stdout.split() if nom)
    if not tags:
        return vide
    if len(tags) > 1:
        raise AmbiguousReleaseTag("AMBIGUOUS_RELEASE_TAG : " + ", ".join(tags))
    nom = tags[0]

    def rev(expression: str) -> str | None:
        try:
            sortie = subprocess.run(
                ["git", "rev-parse", expression],
                cwd=root, capture_output=True, text=True, check=True,
            )
        except (OSError, subprocess.CalledProcessError):
            return None
        return sortie.stdout.strip() or None

    objet = rev(nom)
    commit_sha = rev(f"{nom}^{{commit}}")
    return {
        "RELEASE_TAG_NAME": nom,
        # Un tag leger pointe directement le commit : il n'y a pas d'objet tag.
        "RELEASE_TAG_OBJECT_SHA": objet if objet != commit_sha else None,
        "RELEASE_COMMIT_SHA": commit_sha,
        "RELEASE_TREE_SHA": rev(f"{nom}^{{tree}}"),
    }


def provenance(
    audited_source_sha: str | None = None,
    root: Path = ROOT,
) -> dict[str, Any]:
    """Provenance d'un rapport, sans identite trompeuse.

    Le commit qui CONTIENT le rapport n'existe pas encore quand le rapport se
    genere : le nommer REPORT_COMMIT_SHA etait faux. Ce qui est connu est le
    commit DEPUIS lequel on genere. Le commit d'introduction se retrouve apres
    coup :

        git log -1 --format=%H -- <chemin du rapport>
    """
    depuis = head_sha(root)
    identite: dict[str, Any] = {
        "AUDITED_SOURCE_SHA": audited_source_sha or depuis,
        "REPORT_GENERATED_FROM_SHA": depuis,
        **source_digests(root),
        "freshness_rule": (
            "Une preuve de contenu reste courante tant que "
            "CONTENT_SEMANTIC_DIGEST n'a pas change. Le commit qui publie un "
            "rapport ne perime rien."
        ),
    }
    try:
        identite.update(release_tag_identity(root))
    except AmbiguousReleaseTag as exc:
        identite["RELEASE_TAG_IDENTITY_ERROR"] = str(exc)
    return identite


def semantically_current(
    observed_commit: str | None = None,
    observed_digest: str | None = None,
    root: Path = ROOT,
) -> bool:
    """La preuve de CONTENU decrit-elle les sources courantes ?

    Repond par le digest de contenu. Un commit observe ne sert qu'a retrouver
    le digest d'alors, jamais a etre compare a HEAD.
    """
    if observed_digest is None:
        if observed_commit is None:
            return False
        observed_digest = content_semantic_digest(root, observed_commit)
    return observed_digest == content_semantic_digest(root)
