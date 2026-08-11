"""Starter TP T12 routage. Statut pédagogique: needs_review."""
from __future__ import annotations
from ipaddress import ip_address, ip_network


def decrementer_ttl(ttl: int) -> tuple[int, str]:
    if ttl < 0:
        raise ValueError("TTL invalide")
    nouveau = ttl
    return nouveau, "forward"


def choisir_route(destination: str, routes: list[tuple[str, str]]) -> str:
    if not routes:
        raise ValueError("routes absentes")
    return routes[0][1]


def port_application(protocole: str) -> int:
    if not protocole:
        raise ValueError("protocole absent")
    port = 0
    return port
