"""Fonctions support pour la séquence S01 de Première.

Le module reste volontairement petit : chaque fonction illustre une notion
du cours et peut être testée sans dépendance externe.
"""

from __future__ import annotations

from typing import Callable, Dict, List

DIGITS = "0123456789ABCDEF"


def to_base(value: int, base: int) -> str:
    """Convertit un entier positif de la base 10 vers une base entre 2 et 16."""
    if value < 0:
        raise ValueError("value doit être positif")
    if base < 2 or base > 16:
        raise ValueError("base doit être comprise entre 2 et 16")
    if value == 0:
        return "0"
    digits: List[str] = []
    current = value
    while current > 0:
        current, remainder = divmod(current, base)
        digits.append(DIGITS[remainder])
    return "".join(reversed(digits))


def from_base(representation: str, base: int) -> int:
    """Convertit une représentation textuelle en base 2 à 16 vers la base 10."""
    if base < 2 or base > 16:
        raise ValueError("base doit être comprise entre 2 et 16")
    cleaned = representation.strip().upper()
    if not cleaned:
        raise ValueError("représentation vide")
    total = 0
    for char in cleaned:
        digit = DIGITS.find(char)
        if digit < 0 or digit >= base:
            raise ValueError(f"chiffre {char!r} incompatible avec la base {base}")
        total = total * base + digit
    return total


def encode_twos_complement(value: int, bits: int) -> str:
    """Encode un entier relatif en complément à deux sur un nombre de bits fixé."""
    if bits <= 0:
        raise ValueError("bits doit être strictement positif")
    minimum = -(2 ** (bits - 1))
    maximum = 2 ** (bits - 1) - 1
    if value < minimum or value > maximum:
        raise ValueError("valeur hors intervalle représentable")
    if value < 0:
        value = 2**bits + value
    return format(value, f"0{bits}b")


def decode_twos_complement(bits_value: str) -> int:
    """Décode une chaîne binaire interprétée en complément à deux."""
    if not bits_value or any(char not in "01" for char in bits_value):
        raise ValueError("chaîne binaire attendue")
    raw = int(bits_value, 2)
    bits = len(bits_value)
    sign_bit = 2 ** (bits - 1)
    if raw >= sign_bit:
        return raw - 2**bits
    return raw


def truth_table_binary(operator: Callable[[bool, bool], bool]) -> List[Dict[str, bool]]:
    """Construit la table de vérité d'un opérateur booléen binaire."""
    rows: List[Dict[str, bool]] = []
    for a in [False, True]:
        for b in [False, True]:
            rows.append({"a": a, "b": b, "result": operator(a, b)})
    return rows


def unicode_codepoints(text: str) -> List[int]:
    """Retourne les points de code Unicode des caractères d'une chaîne."""
    return [ord(char) for char in text]


def choose_container(need_order: bool, need_named_access: bool, immutable: bool) -> str:
    """Propose list, tuple ou dict selon quelques contraintes simples."""
    if need_named_access:
        return "dict"
    if immutable:
        return "tuple"
    if need_order:
        return "list"
    return "list"
