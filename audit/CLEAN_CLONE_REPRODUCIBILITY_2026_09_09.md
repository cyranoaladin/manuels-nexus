# Reconstruction depuis un clone propre — 9 septembre 2026

Constat. Ce document n'approuve aucune publication.

## Protocole

Clone `git clone https://github.com/cyranoaladin/manuels-nexus.git` au commit
`c59ce806e91eef55a22ddc568ac2a407a2d37f13`, dans un répertoire neuf. **Aucun fichier n'a été
copié depuis la machine de développement.** L'environnement Python est
construit hors du clone, à partir du seul `requirements-ci-audit.txt`.

Le clone ne contient ni `.worktrees/`, ni `Fiches_cours_exercices/`, ni
`HGGSP/`, ni `_SAUVEGARDES_HGGSP/`, ni `.venv` — vérifié.

## Ce qui fonctionne

**Déterminisme : PROUVÉ.** Deux exécutions successives de
`scripts/inventory_collection.py`, même commit et même environnement,
produisent des artefacts **identiques au bit près** :

| Artefact | SHA-256 |
|---|---|
| `audit/INVENTAIRE_COLLECTION.json` | `4a686e28ad35bb44…` |
| `ETAT_COLLECTION.md` | `edc781da82bb3a8a…` |
| `audit/MATRICE_LIVRABLES.yaml` | `bb116c21eaef64cd…` |
| `audit/ECARTS_ET_CONTRADICTIONS.yaml` | `d105eb84a63dc966…` |

L'horodatage `generated_at_utc` n'est pas une horloge murale : il dérive de
`SOURCE_DATE_EPOCH` ou, à défaut, de la date du commit observé. Le contenu
pédagogique inventorié est identique à celui commité ; les seuls écarts sont
`head_sha` et cet horodatage, tous deux liés au commit et non à la machine.

**Assemblage et compilation : FONCTIONNELS.** Le clone produit un manuel
complet sans aucune ressource extérieure :

- `MANUEL_1SPE_eleve.pdf`, **381 pages**, 2.8M
- `qpdf --check` : aucune erreur de syntaxe ni d'encodage de flux
- polices **incorporées**, métadonnées de collection correctes
- date de création déterministe, non horodatée à l'exécution

## Ce qui ne fonctionne pas, et qui bloque la release

**Trois PDF distincts portent le même nom de manuel.** Pour la seule édition
élève de 1SPE :

| Artefact | Pages | SHA-256 | État |
|---|---:|---|---|
| Recompilé depuis les sources courantes | **381** | `0ea2e23abdeb5b44…` | courant |
| `build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf`, **versionné** | 371 | `f3b8ec66584bda2a…` | périmé de 10 pages |
| `MANUELS_PDF_PUBLICATION/01_Maths_1re_Spe_Eleve.pdf` | 371 | `c23140a53c25c584…` | périmé, **et distinct du précédent** |

Les deux artefacts périmés ont le même nombre de pages mais des empreintes
différentes : ce ne sont pas la même compilation, et aucun ne correspond aux
sources. La recompilation, elle, est reproductible : deux passages successifs
depuis le clone donnent la même empreinte `0ea2e23abdeb5b44`.

**Le dépôt versionne ses artefacts de build.** 36 PDF sont suivis par Git, dont
les sorties de `build/`. Un PDF périmé voyage donc avec les sources et peut
être pris pour le livrable. C'est arrivé pendant cet audit : un `git checkout`
du répertoire de travail a remplacé une compilation fraîche par la version
commitée, ce qui a d'abord fait croire à six pages blanches finales
inexistantes. Vérification refaite sur la bonne compilation : la quatrième de
couverture est correctement composée en page 381, et il reste sept pages sans
texte (2, 4, 6, 12, 358, 362, 370), aux positions attendues de versos dans une
mise en page recto-verso.

**La chaîne déclarée n'est pas respectée par la machine courante.**
`scripts/check_toolchain.py` relève 3 blocages sur 10 contrôles : TeX Live
2023 contre 2026 exigé, `verapdf` absent, et donc balisage Tagged PDF non
prouvable. Le PDF ci-dessus porte d'ailleurs `Tagged: no`. Une reconstruction
faite ici le serait avec un moteur inférieur de trois versions à l'exigence et
sans validation d'accessibilité PDF/UA-1.

## Limites documentées, non bloquantes

Sept modules tiers importés par `ingest.py`, `crawl.py`, `index.py` et
`common.py` ne sont pas déclarés : `FlagEmbedding`, `anthropic`, `bs4`,
`httpx`, `pgvector`, `psycopg`, `trafilatura`. Ils appartiennent au
pipeline RAG d'ingestion de corpus, hors de la chaîne de fabrication des
manuels, et leur absence n'empêche ni l'inventaire, ni l'assemblage, ni la
compilation.

Deux annotations de provenance nomment des chemins absents d'un clone :
`source_yaml` dans les référentiels NSI, et les chemins de `site-packages`
du registre de warnings. Vérifié : `source_yaml` n'est lu par aucun script, et
`tests/test_root_pytest_warning_ledger.py` passe dans le clone propre. Ce sont
des données enregistrées, pas des entrées de build.

## Verdict

La reproductibilité **du dispositif** est établie : un clone propre inventorie,
assemble et compile, de façon déterministe, sans dépendance cachée à la machine
de développement.

La reproductibilité **de la release** ne l'est pas : la chaîne d'outillage
déclarée n'est pas disponible ici, et les PDF publiés ne correspondent plus aux
sources. `PRODUCTION_READY` ne peut donc pas être prononcé.
