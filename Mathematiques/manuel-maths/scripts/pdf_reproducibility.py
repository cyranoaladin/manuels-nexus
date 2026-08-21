"""Contrat partagé d'identité de trailer PDF déterministe Nexus."""

import hashlib
from collections.abc import Mapping


PDF_TRAILER_ID_SCHEME = "nexus-pdf-trailer-id/v1"
# Version de génération du PRODUCTEUR. Le préimage capture déjà le corps du
# master et les digests de la classe/charte canoniques : toute évolution du
# rendu passant par l'un des deux change donc l'identité. Cette constante
# couvre le cas résiduel — une évolution du producteur qui changerait le PDF
# SANS toucher au master ni aux gabarits (options de compilation, séquence de
# passes, post-traitement canonique). Elle DOIT être incrémentée dans ce cas,
# et seulement dans ce cas.
PDF_TRAILER_PRODUCER_SCHEMA_VERSION = 1


def pdf_trailer_identity(
    *,
    manual: str,
    variant: str,
    body: str,
    sources: Mapping[str, str],
) -> str:
    """Identité de trailer PDF DÉTERMINISTE et SENSIBLE AUX SOURCES.

    LuaTeX tire sinon les deux éléments de ``/ID`` au hasard à chaque
    exécution (même sous ``SOURCE_DATE_EPOCH``), ce qui suffit à casser la
    reproductibilité binaire du PDF alors que tout le reste est identique.

    L'identité est le condensé du couple (manuel, variante), du corps du
    master assemblé et du condensé de CHAQUE source que ce master nomme.
    Conséquences voulues :

    * mêmes entrées ⇒ même identité, donc PDF byte-identique ;
    * toute source pertinente modifiée ⇒ identité déterministement
      différente ;
    * deux manuels/variantes ⇒ identités distinctes (jamais une constante
      globale partagée).

    Aucun aléa, aucune horloge : le résultat ne dépend que des sources.
    """
    payload = [
        PDF_TRAILER_ID_SCHEME,
        f"producer_schema_version={PDF_TRAILER_PRODUCER_SCHEMA_VERSION}",
        f"manual={manual}",
        f"variant={variant}",
        "body=" + hashlib.sha256(body.encode("utf-8")).hexdigest(),
    ]
    for relative_path in sorted(sources):
        payload.append(f"{relative_path}\t{sources[relative_path]}")
    digest = hashlib.sha256("\n".join(payload).encode("utf-8")).hexdigest()
    return digest[:32].upper()
