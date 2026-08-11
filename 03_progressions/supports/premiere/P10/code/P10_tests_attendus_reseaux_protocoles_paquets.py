"""Tests attendus TP P10. Statut pédagogique: needs_review."""
from __future__ import annotations
import importlib
import os

MODULE = importlib.import_module(os.environ.get("TP_MODULE", "P10_starter_reseaux_protocoles_paquets"))


def test_nominal_ttl_route_ports() -> None:
    assert MODULE.decrementer_ttl({"ttl": 3, "ip_dst": "192.168.1.5"}) == {"ttl": 2, "ip_dst": "192.168.1.5", "etat": "transmis"}
    assert MODULE.decision_route("192.168.1.42", "192.168.1.0/24", "192.168.1.1") == "local"
    assert MODULE.decision_route("10.0.0.5", "192.168.1.0/24", "192.168.1.1") == "192.168.1.1"
    assert MODULE.port_service("https://example.org") == 443


def test_limites_ttl_zero_http() -> None:
    assert MODULE.decrementer_ttl({"ttl": 1}) == {"ttl": 0, "etat": "supprimé"}
    assert MODULE.port_service("http://example.org") == 80


def test_entrees_invalides() -> None:
    try:
        MODULE.port_service("ftp://example.org")
    except ValueError:
        return
    raise AssertionError("ValueError attendue")


if __name__ == "__main__":
    test_nominal_ttl_route_ports()
    test_limites_ttl_zero_http()
    test_entrees_invalides()
    print("tests attendus OK")
