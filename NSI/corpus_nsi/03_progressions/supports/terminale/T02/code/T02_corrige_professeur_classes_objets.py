"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

class Compte:
    def __init__(self, solde):
        if solde < 0:
            raise ValueError("solde initial invalide")
        self.solde = solde
    def deposer(self, montant):
        if montant <= 0:
            raise ValueError("montant invalide")
        self.solde += montant
    def retirer(self, montant):
        if montant <= 0 or montant > self.solde:
            raise ValueError("retrait invalide")
        self.solde -= montant

def creer_compte(solde):
    if solde is None:
        raise ValueError("solde initial invalide")
    return Compte(solde)
