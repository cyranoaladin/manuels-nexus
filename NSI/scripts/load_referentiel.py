"""Charge referentiel/*.json dans la table capacites (source de vérité, R7)."""
import json

from common import ROOT, db_connect


def main() -> None:
    files = sorted((ROOT / "referentiel").glob("capacites_*.json"))
    with db_connect() as conn, conn.cursor() as cur:
        for f in files:
            data = json.loads(f.read_text(encoding="utf-8"))
            for cap in data["capacites"]:
                cur.execute("""
                    INSERT INTO capacites (id, niveau, theme, libelle_bo, libelle_eleve,
                                           demonstration_exigible, algo_bo, bo_reference)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (id) DO UPDATE SET libelle_bo=EXCLUDED.libelle_bo,
                        libelle_eleve=EXCLUDED.libelle_eleve""",
                    (cap["id"], data["niveau"], data["theme"], cap["libelle_bo"],
                     cap["libelle_eleve"], cap.get("demonstration_exigible", False),
                     cap.get("algo_bo"), data["bo_reference"]))
        conn.commit()
    print(f"{len(files)} fichiers de référentiel chargés.")


if __name__ == "__main__":
    main()
