"""Starter TP P10 réseaux, protocoles et paquets. Statut pédagogique: needs_review."""
from __future__ import annotations


def decrementer_ttl(paquet: dict) -> dict:
    copie = dict(paquet)
    copie["ttl"] = paquet.get("ttl", 0)
    copie["etat"] = "transmis"
    return copie


def decision_route(destination: str, reseau_local: str, passerelle: str) -> str:
    if destination.startswith(reseau_local.split("/")[0]):
        return destination
    return passerelle


def port_service(url: str) -> int:
    return len(url)
