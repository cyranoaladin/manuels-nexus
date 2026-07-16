# Scrapers existants dans le corpus NSI

## Inventaire (corpus_nsi/scrapping_NSI/)

| Script | Usage | Transposabilite |
|---|---|---|
| scraper_eduscol.py | Ressources officielles NSI depuis Eduscol STI | Couplage fort (netpolicy, provenance, archive_security). Import en l'etat non possible sans adapter les chemins. |
| scraper_nsi_v2.py | Scraper generique sites NSI | Meme couplage. |
| netpolicy.py | Conformite robots.txt, politesse reseau, throttle | Module reutilisable (peu de deps). |
| provenance.py | Tracabilite SHA256 + licence des ressources telechargees | Module reutilisable. |

## Decision

Les scrapers du corpus sont trop couples a leur module parent pour un import direct :
imports croise entre `scrapping_NSI.*` et `scripts.*` du depot source.

**Repli documente** : utiliser `scripts/crawl.py` (generique) pour le LOT 1 web.
Les scrapers du corpus restent une reference pour les URLs cibles (Eduscol, sujets ECE)
et les regles de politesse (netpolicy).

Si necessaire, copier `netpolicy.py` et `provenance.py` dans `scripts/` et adapter
les imports de `scraper_eduscol.py` -- a faire uniquement si le LOT 1 web est critique
pour un chapitre donne.
