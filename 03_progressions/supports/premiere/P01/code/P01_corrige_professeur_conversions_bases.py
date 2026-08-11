"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

def convert_base(value):
    if value is None or value < 0:
        raise ValueError("entier naturel attendu")
    if value == 0:
        binary = "0"
    else:
        n = value
        bits = []
        while n > 0:
            bits.append(str(n % 2))
            n //= 2
        binary = "".join(reversed(bits))
    digits = "0123456789ABCDEF"
    if value == 0:
        hexa = "0"
    else:
        n = value
        out = []
        while n > 0:
            out.append(digits[n % 16])
            n //= 16
        hexa = "".join(reversed(out))
    return {"decimal": value, "binary": binary, "hex": hexa}
