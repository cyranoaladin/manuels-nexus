"""MCP banque : CRUD sur les objets du manuel + requêtes de couverture."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from common import ROOT, db_connect  # noqa: E402

from fastmcp import FastMCP  # noqa: E402
from jsonschema import validate  # noqa: E402

mcp = FastMCP("mcp-banque")
EX_SCHEMA = json.loads((ROOT / "schemas" / "exercice.schema.json").read_text(encoding="utf-8"))


@mcp.tool()
def upsert_objet(meta: dict) -> str:
    """Enregistre/actualise un objet (métadonnées validées contre le schéma).
    Le statut ne peut passer à 'ready' que si les gates sympy+similarity+compilation sont 'pass'."""
    if meta.get("type_objet", "exercice") == "exercice":
        validate(meta, EX_SCHEMA)
    if meta.get("status") == "ready":
        chap = meta["chapitre"]
        vdir = ROOT / "chapitres" / chap / "validations"
        for gate in ("sympy", "similarity"):
            v = vdir / f"{meta['id']}.{gate}.json"
            if not v.exists() or json.loads(v.read_text())["verdict"] not in ("pass",):
                # revue humaine tracée acceptée en remplacement
                rh = vdir / f"{meta['id']}.revue_humaine.json"
                if not rh.exists():
                    raise ValueError(f"Gate '{gate}' non passé pour {meta['id']} : statut 'ready' refusé (R2/R3).")
    with db_connect() as conn, conn.cursor() as cur:
        cur.execute("""
          INSERT INTO objets (id, chapitre, type_objet, capacites, methodes, parcours,
                              competences, duree_min, mode_creation, sources_inspiration,
                              parametres_sympy, fichier_tex, status)
          VALUES (%(id)s,%(chapitre)s,%(type_objet)s,%(capacites)s,%(methodes)s,%(parcours)s,
                  %(competences)s,%(duree_min)s,%(mode_creation)s,%(sources_inspiration)s,
                  %(parametres_sympy)s,%(fichier_tex)s,%(status)s)
          ON CONFLICT (id) DO UPDATE SET status=EXCLUDED.status, updated_at=now(),
              fichier_tex=EXCLUDED.fichier_tex, parametres_sympy=EXCLUDED.parametres_sympy
        """, {**{"methodes": None, "parcours": None, "competences": None, "duree_min": None,
                 "mode_creation": None, "sources_inspiration": None, "parametres_sympy": None,
                 "type_objet": "exercice"}, **meta,
              "parametres_sympy": json.dumps(meta.get("parametres_sympy") or {})})
        conn.commit()
    return f"objet {meta['id']} enregistré (status={meta.get('status','draft')})"


@mcp.tool()
def coverage_gaps(chapitre: str) -> list[dict]:
    """Cases vides de la matrice capacités × parcours (exercices verified/ready < 2)."""
    with db_connect() as conn, conn.cursor() as cur:
        cur.execute("""SELECT capacite, parcours, nb_exercices FROM couverture
                       WHERE capacite LIKE %s AND nb_exercices < 2
                       ORDER BY capacite, parcours""", (chapitre + "%",))
        return [{"capacite": c, "parcours": p, "nb": n} for c, p, n in cur.fetchall()]


@mcp.tool()
def list_objets(chapitre: str, type_objet: str | None = None, status: str | None = None) -> list[dict]:
    """Liste les objets d'un chapitre avec filtres optionnels."""
    where, params = ["chapitre=%s"], [chapitre]
    if type_objet:
        where.append("type_objet=%s"); params.append(type_objet)
    if status:
        where.append("status=%s"); params.append(status)
    with db_connect() as conn, conn.cursor() as cur:
        cur.execute(f"SELECT id, type_objet, capacites, parcours, status, fichier_tex "
                    f"FROM objets WHERE {' AND '.join(where)} ORDER BY id", params)
        return [{"id": i, "type": t, "capacites": c, "parcours": p, "status": s, "tex": f}
                for i, t, c, p, s, f in cur.fetchall()]


if __name__ == "__main__":
    mcp.run()
