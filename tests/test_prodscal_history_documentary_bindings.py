"""Keep the reviewed historical aside attached to its documentary references.

These structural checks do not verify historical dates or replace source reading.
The independent review records the documents, pages read and source digests.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / (
    "Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/"
    "cours/14_C5_al_kashi.tex"
)


def historical_aside() -> str:
    return SOURCE.read_text().rsplit(r"\approfondissement{", 1)[1]


def test_historical_aside_distinguishes_geometric_relations_from_modern_notation() -> None:
    text = historical_aside()
    assert "systématisée" not in text
    assert "théorème de la généralisation de Pythagore" not in text
    assert "relations géométriques équivalentes" in text
    assert "sans notation trigonométrique" in text
    assert "12 et 13 du livre II" in text
    assert r"\emph{Éléments}" in text


def test_historical_claims_keep_precise_bibliographic_references() -> None:
    text = historical_aside()
    assert r"\emph{Miftah al-Hisab}" in text
    assert "achevé en 1427" in text
    assert "de l'angle qu'ils forment" in text
    assert "Aydin et L. Hammoudi" in text
    assert "2019, p.~1" in text
    assert "M. K. Azarian" in text
    assert "2000, p.~83--84" in text
    assert r"\footnote{" in text
