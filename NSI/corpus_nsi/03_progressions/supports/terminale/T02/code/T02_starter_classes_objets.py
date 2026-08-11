"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

def creer_compte(solde):
    if solde is None or solde < 0:
        raise ValueError("solde initial invalide")
    return {"solde": solde}

if __name__ == "__main__":
    print(creer_compte(20))
