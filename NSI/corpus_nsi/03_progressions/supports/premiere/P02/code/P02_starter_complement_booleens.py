"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

def twos_complement_value(bits):
    if not bits or any(bit not in "01" for bit in bits):
        raise ValueError("mot binaire attendu")
    return int(bits, 2)

if __name__ == "__main__":
    print(twos_complement_value("11101001"))
