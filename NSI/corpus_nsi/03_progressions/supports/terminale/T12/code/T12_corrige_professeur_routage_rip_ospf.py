"""Corrigé professeur TP T12 routage. Statut pédagogique: needs_review."""
from __future__ import annotations
from ipaddress import ip_address, ip_network


def decrementer_ttl(ttl: int) -> tuple[int, str]:
    if ttl < 0:
        raise ValueError("TTL invalide")
    nouveau = ttl - 1
    return nouveau, "drop" if nouveau <= 0 else "forward"


def choisir_route(destination: str, routes: list[tuple[str, str]]) -> str:
    if not routes:
        raise ValueError("routes absentes")
    ip = ip_address(destination)
    candidates = [(ip_network(prefix), passerelle) for prefix, passerelle in routes if ip in ip_network(prefix)]
    if not candidates:
        return "default"
    network, passerelle = max(candidates, key=lambda item: item[0].prefixlen)
    return passerelle


def port_application(protocole: str) -> int:
    if not protocole:
        raise ValueError("protocole absent")
    ports = {"HTTP": 80, "HTTPS": 443}
    return ports[protocole.upper()]
