# MATRICE D'AUDIT DES STYLES ET DIVERGENCES DE CHARTE (MATHS vs NSI)

Ce document recense les divergences byte-à-byte entre les fichiers de gabarits des Mathématiques et de la NSI.

| Nom Composant | Hash Maths (SHA-256) | Hash NSI (SHA-256) | Statut de Synchronisation | Version Déclarée |
| :--- | :---: | :---: | :--- | :--- |
| `book_master.tex` | `ABSENT` | `f87778d8a860` | **Exclusif NSI** | `N/A` |
| `chapitre_master.tex` | `82c0ae2dfd98` | `b64379616544` | **Divergent (Fork détecté)** | `Non spécifiée` |
| `logo_nexus.png` | `81855d6817f9` | `81855d6817f9` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-boites-v6.sty` | `9511791f55a4` | `9511791f55a4` | **100% Identique (Byte-per-byte)** | `% nexus-boites-v6.sty — Jeu d'encadrés é` |
| `nexus-charte-v6.sty` | `2803c47bbf78` | `2803c47bbf78` | **100% Identique (Byte-per-byte)** | `% nexus-charte-v6.sty — Charte v6 « coll` |
| `nexus-code.tex` | `16e74594ae51` | `27a6bb961ea9` | **Divergent (Fork détecté)** | `Non spécifiée` |
| `nexus-couverture.sty` | `78db1260b601` | `78db1260b601` | **100% Identique (Byte-per-byte)** | `% Corrige la couverture v4 : logo posé s` |
| `nexus-decor.sty` | `6d17052a776d` | `6d17052a776d` | **100% Identique (Byte-per-byte)** | `% nexus-decor.sty — Motifs de contour de` |
| `nexus-exercices-v6.sty` | `efa293301d5e` | `efa293301d5e` | **100% Identique (Byte-per-byte)** | `% nexus-exercices-v6.sty — Pages d'exerc` |
| `nexus-figures-bib.sty` | `b3e5ca321321` | `b3e5ca321321` | **100% Identique (Byte-per-byte)** | `\ProvidesPackage{gabarits/nexus-figures-` |
| `nexus-figures-nsi.tex` | `2c7b764764e3` | `2c7b764764e3` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-figures.tex` | `de1339903782` | `de1339903782` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-icons.tex` | `42af1195dda2` | `42af1195dda2` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-manuel-v5.cls` | `25657507c963` | `25657507c963` | **100% Identique (Byte-per-byte)** | `% nexus-manuel-v5.cls — Maquette éditori` |
| `nexus-manuel.cls` | `141c5ce27931` | `141c5ce27931` | **100% Identique (Byte-per-byte)** | `% nexus-manuel.cls v4.1 — Classe du manu` |
| `nexus-margin-json.lua` | `b145020dd183` | `b145020dd183` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-margin-layout.lua` | `ef3234db7d05` | `ef3234db7d05` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-margin-rail.tex` | `6ffc96378d2d` | `6ffc96378d2d` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-margin-shipout.lua` | `694123b346ee` | `694123b346ee` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-pages-froides.sty` | `95c0c3595066` | `95c0c3595066` | **100% Identique (Byte-per-byte)** | `% Remplace les pages froides austères de` |
| `nexus-pont-v6.sty` | `2dc54e28f4c6` | `2dc54e28f4c6` | **100% Identique (Byte-per-byte)** | `% nexus-pont-v6.sty — Pont v4.1/v5 → v6 ` |
| `nexus-signatures.tex` | `bbf81c1368d7` | `bbf81c1368d7` | **100% Identique (Byte-per-byte)** | `% Kit v4.1 : décors 100% géométriques, d` |
| `objet_standalone.tex` | `c9c4c06915ff` | `c9c4c06915ff` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `specimen-pont-v6.tex` | `1496c0e09d0e` | `ABSENT` | **Exclusif Mathématiques** | `% specimen-pont-v6.tex — Vérifie le pont` |
| `specimen-v6.tex` | `a1b55799f72a` | `ABSENT` | **Exclusif Mathématiques** | `% specimen-v6.tex — Spécimen de la chart` |
| `specimen.tex` | `902b89b959d4` | `a3dccdf4ceb7` | **Divergent (Fork détecté)** | `% specimen.tex v4.0 — 10 pages represent` |

## Synthèse des Divergences Majeures

Nombre total de fichiers de style divergents identifiés : **3**

- `chapitre_master.tex` : Maths (`82c0ae2dfd98`) vs NSI (`b64379616544`). Nécessite unification dans la source canonique.
- `nexus-code.tex` : Maths (`16e74594ae51`) vs NSI (`27a6bb961ea9`). Nécessite unification dans la source canonique.
- `specimen.tex` : Maths (`902b89b959d4`) vs NSI (`a3dccdf4ceb7`). Nécessite unification dans la source canonique.
