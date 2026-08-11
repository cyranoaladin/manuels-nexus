"""Corrigé professeur TP P10 réseaux, protocoles et paquets. Statut pédagogique: needs_review."""
from __future__ import annotations
import ipaddress


def decrementer_ttl(paquet: dict) -> dict:
    ttl = int(paquet["ttl"])
    copie = dict(paquet)
    copie["ttl"] = max(0, ttl - 1)
    copie["etat"] = "supprimé" if copie["ttl"] == 0 else "transmis"
    return copie


def decision_route(destination: str, reseau_local: str, passerelle: str) -> str:
    adresse = ipaddress.ip_address(destination)
    reseau = ipaddress.ip_network(reseau_local, strict=False)
    return "local" if adresse in reseau else passerelle


def port_service(url: str) -> int:
    if url.startswith("https://"):
        return 443
    if url.startswith("http://"):
        return 80
    raise ValueError("protocole non pris en charge")
