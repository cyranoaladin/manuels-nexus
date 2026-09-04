# MATRICE D'AUDIT DES STYLES ET DIVERGENCES DE CHARTE (MATHS vs NSI)

Ce document recense les divergences byte-à-byte entre les fichiers de gabarits des Mathématiques et de la NSI.

| Nom Composant | Hash Maths (SHA-256) | Hash NSI (SHA-256) | Statut de Synchronisation | Version Déclarée |
| :--- | :---: | :---: | :--- | :--- |
| `book_master.tex` | `ABSENT` | `a16442c965c3` | **Exclusif NSI** | `N/A` |
| `chapitre_master.tex` | `82c0ae2dfd98` | `b64379616544` | **Divergent (Fork détecté)** | `Non spécifiée` |
| `logo_nexus.png` | `81855d6817f9` | `81855d6817f9` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-boites-v6.sty` | `cd59d965d615` | `cd59d965d615` | **100% Identique (Byte-per-byte)** | `\ProvidesPackage{\@currpath\@currname}[2` |
| `nexus-charte-v6.sty` | `d42b1df562e7` | `d42b1df562e7` | **100% Identique (Byte-per-byte)** | `\ProvidesPackage{\@currpath\@currname}[2` |
| `nexus-code.tex` | `16e74594ae51` | `27a6bb961ea9` | **Divergent (Fork détecté)** | `Non spécifiée` |
| `nexus-couverture.sty` | `7debbf9f9b82` | `7debbf9f9b82` | **100% Identique (Byte-per-byte)** | `\ProvidesPackage{\@currpath\@currname}[2` |
| `nexus-decor.sty` | `2ecc021fe98c` | `2ecc021fe98c` | **100% Identique (Byte-per-byte)** | `\ProvidesPackage{\@currpath\@currname}[2` |
| `nexus-exercices-v6.sty` | `2c6aacc7fe27` | `2c6aacc7fe27` | **100% Identique (Byte-per-byte)** | `\ProvidesPackage{\@currpath\@currname}[2` |
| `nexus-figures-bib.sty` | `aca44416f30e` | `aca44416f30e` | **100% Identique (Byte-per-byte)** | `\ProvidesPackage{\@currpath\@currname}[2` |
| `nexus-figures-nsi.tex` | `2c7b764764e3` | `2c7b764764e3` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-figures.tex` | `de1339903782` | `de1339903782` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-icons.tex` | `42af1195dda2` | `42af1195dda2` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-manuel-v5.cls` | `5481ac50897d` | `5481ac50897d` | **100% Identique (Byte-per-byte)** | `\ProvidesClass{\@currpath\@currname}[202` |
| `nexus-manuel.cls` | `42deffecf8e0` | `42deffecf8e0` | **100% Identique (Byte-per-byte)** | `\ProvidesClass{\@currpath\@currname}[202` |
| `nexus-margin-json.lua` | `b145020dd183` | `b145020dd183` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-margin-layout.lua` | `ef3234db7d05` | `ef3234db7d05` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-margin-rail.tex` | `04cb45a5f879` | `04cb45a5f879` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-margin-shipout.lua` | `2c2bd1b3b98d` | `2c2bd1b3b98d` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-pages-froides.sty` | `5d478c0ec370` | `5d478c0ec370` | **100% Identique (Byte-per-byte)** | `\ProvidesPackage{\@currpath\@currname}[2` |
| `nexus-pont-v6.sty` | `964afdd31c79` | `964afdd31c79` | **100% Identique (Byte-per-byte)** | `\ProvidesPackage{\@currpath\@currname}[2` |
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
