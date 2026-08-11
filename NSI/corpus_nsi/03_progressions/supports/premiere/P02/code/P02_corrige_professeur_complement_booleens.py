"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

def twos_complement_value(bits):
    if not bits or any(bit not in "01" for bit in bits):
        raise ValueError("mot binaire attendu")
    value = int(bits, 2)
    if bits[0] == "1":
        value -= 2 ** len(bits)
    return value
