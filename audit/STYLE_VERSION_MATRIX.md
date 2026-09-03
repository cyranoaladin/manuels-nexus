# MATRICE D'AUDIT DES STYLES ET DIVERGENCES DE CHARTE (MATHS vs NSI)

Ce document recense les divergences byte-à-byte entre les fichiers de gabarits des Mathématiques et de la NSI.

| Nom Composant | Hash Maths (SHA-256) | Hash NSI (SHA-256) | Statut de Synchronisation | Version Déclarée |
| :--- | :---: | :---: | :--- | :--- |
| `book_master.tex` | `ABSENT` | `a16442c965c3` | **Exclusif NSI** | `N/A` |
| `chapitre_master.tex` | `82c0ae2dfd98` | `b64379616544` | **Divergent (Fork détecté)** | `Non spécifiée` |
| `logo_nexus.png` | `81855d6817f9` | `81855d6817f9` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-boites-v6.sty` | `2185848e26ea` | `2185848e26ea` | **100% Identique (Byte-per-byte)** | `\ProvidesPackage{nexus-boites-v6}[2026/0` |
| `nexus-charte-v6.sty` | `90391485645c` | `90391485645c` | **100% Identique (Byte-per-byte)** | `\ProvidesPackage{nexus-charte-v6}[2026/0` |
| `nexus-code.tex` | `16e74594ae51` | `27a6bb961ea9` | **Divergent (Fork détecté)** | `Non spécifiée` |
| `nexus-couverture.sty` | `57327021b50f` | `57327021b50f` | **100% Identique (Byte-per-byte)** | `\ProvidesPackage{nexus-couverture}[2026/` |
| `nexus-decor.sty` | `1b23d537120e` | `1b23d537120e` | **100% Identique (Byte-per-byte)** | `\ProvidesPackage{nexus-decor}[2026/07/20` |
| `nexus-exercices-v6.sty` | `25b72f131634` | `25b72f131634` | **100% Identique (Byte-per-byte)** | `\ProvidesPackage{nexus-exercices-v6}[202` |
| `nexus-figures-bib.sty` | `d441187e66d4` | `d441187e66d4` | **100% Identique (Byte-per-byte)** | `\ProvidesPackage{nexus-figures-bib}[2026` |
| `nexus-figures-nsi.tex` | `2c7b764764e3` | `2c7b764764e3` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-figures.tex` | `de1339903782` | `de1339903782` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-icons.tex` | `42af1195dda2` | `42af1195dda2` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-manuel-v5.cls` | `5e1d7fdb2588` | `5e1d7fdb2588` | **100% Identique (Byte-per-byte)** | `\ProvidesClass{nexus-manuel-v5}[2026/07/` |
| `nexus-manuel.cls` | `90ea5ae521bc` | `90ea5ae521bc` | **100% Identique (Byte-per-byte)** | `\ProvidesClass{nexus-manuel}[2026/07/20 ` |
| `nexus-margin-json.lua` | `b145020dd183` | `b145020dd183` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-margin-layout.lua` | `ef3234db7d05` | `ef3234db7d05` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-margin-rail.tex` | `6ffc96378d2d` | `6ffc96378d2d` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-margin-shipout.lua` | `694123b346ee` | `694123b346ee` | **100% Identique (Byte-per-byte)** | `Non spécifiée` |
| `nexus-pages-froides.sty` | `4ecc02468ab1` | `4ecc02468ab1` | **100% Identique (Byte-per-byte)** | `\ProvidesPackage{nexus-pages-froides}[20` |
| `nexus-pont-v6.sty` | `7345dbceca06` | `7345dbceca06` | **100% Identique (Byte-per-byte)** | `\ProvidesPackage{nexus-pont-v6}[2026/07/` |
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
