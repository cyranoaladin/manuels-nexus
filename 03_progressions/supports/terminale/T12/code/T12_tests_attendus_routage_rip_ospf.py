"""Tests attendus TP T12. Statut pédagogique: needs_review."""
from __future__ import annotations
import importlib, os
MODULE = importlib.import_module(os.environ.get("TP_MODULE", "T12_starter_routage_rip_ospf"))
ROUTES = [("192.168.1.0/24", "local"), ("192.168.0.0/16", "lan"), ("0.0.0.0/0", "box")]


def test_nominal_ttl_route_port() -> None:
    assert MODULE.decrementer_ttl(2) == (1, "forward")
    assert MODULE.decrementer_ttl(1) == (0, "drop")
    assert MODULE.choisir_route("192.168.1.42", ROUTES) == "local"
    assert MODULE.port_application("HTTPS") == 443


def test_limite_route_defaut_http() -> None:
    assert MODULE.choisir_route("8.8.8.8", ROUTES) == "box"
    assert MODULE.port_application("HTTP") == 80


def test_invalide_ttl_negatif() -> None:
    try:
        MODULE.decrementer_ttl(-1)
    except ValueError:
        return
    raise AssertionError("ValueError attendue")

if __name__ == "__main__":
    test_nominal_ttl_route_port(); test_limite_route_defaut_http(); test_invalide_ttl_negatif(); print("tests attendus OK")
