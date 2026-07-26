# Manuel de mathématiques différencié — Noyau de production

Dépôt de production agentique d'un manuel de mathématiques conforme aux programmes officiels français, structuré pour la pédagogie différenciée (Nexus Réussite).

## Démarrage rapide

```bash
make setup                      # environnement + base de données
cp .env.example .env            # renseigner DATABASE_URL et ANTHROPIC_API_KEY
make crawl                      # collecte des sources actives du registre
make ingest && make index       # normalisation + indexation pgvector
claude                          # lancer Claude Code : lire CLAUDE.md, démarrer LOT 0
```

## Environnement de release

L'environnement de développement courant permet de rédiger et de lancer les
tests, mais il ne constitue pas à lui seul une chaîne de fabrication certifiée.
Une release des manuels 1SPE exige le contrat reproductible
[`release/toolchain.yaml`](release/toolchain.yaml) :

- Python 3.12.x ;
- Java 21 minimum ;
- LuaLaTeX de TeX Live 2026 minimum, avec le contrat Tagged PDF activé ;
- veraPDF CLI 1.30.1, profil PDF/UA-1 (`ua1`) et rapports `mrr` ;
- les commandes Poppler `pdfinfo`, `pdffonts`, `pdftotext` et `pdftoppm`
  en version 24.02.0 minimum ;
- Ghostscript 10.02 minimum.

Le contrôle versionné dans
`validations/release-1spe/toolchain.json` distingue l'état observé de la cible :

| Composant | Environnement courant contrôlé | Exigence de release |
|---|---|---|
| Python | 3.12.3, conforme | 3.12.x |
| Java | 21.0.11, conforme | 21 minimum |
| LuaLaTeX | TeX Live 2023, bloquant | TeX Live 2026 minimum |
| Tagged PDF | porte non démontrée, bloquante | contrat activé sous TeX Live 2026 |
| veraPDF | absent, bloquant | CLI 1.30.1, profil `ua1`, rapport `mrr` |
| Poppler | 24.02.0, conforme | 24.02.0 minimum |
| Ghostscript | 10.02.1, conforme | 10.02 minimum |

La version minimale TeX Live 2026 est le seuil de capacité retenu pour le
Tagged PDF. Elle ne certifie pas à elle seule un document : les PDF produits
doivent encore réussir la validation PDF/UA-1 avec la version épinglée de
veraPDF.

Le préflight ne tente aucune installation :

```bash
make release-toolchain
```

Il écrit un rapport déterministe dans
`validations/release-1spe/toolchain.json`. Un code retour `0` signifie que
tout le contrat d'outillage a été prouvé (`certified`). Le code `2` signifie
`blocked` et énumère les outils absents ou insuffisants. Ce code `2` est un
diagnostic honnête de l'environnement courant, jamais un succès implicite.

Après mise à niveau explicite de l'environnement, relancer le préflight puis
la suite complète :

```bash
make release-toolchain
make release-test
```

## Cartographie du dépôt

| Chemin | Contenu |
|---|---|
| `CLAUDE.md` | Instructions opératoires de l'agent (à lire en premier) |
| `CAHIER_DES_CHARGES.md` | Exigences et critères d'acceptation |
| `docs/` | Conception pédagogique, workflow, architecture, guide agents, conventions LaTeX |
| `sources/registry.yaml` | Registre des sources web (tiers, licences, politiques d'usage) |
| `referentiel/` | Capacités du programme officiel (source de vérité) |
| `schemas/` | Schémas JSON des objets (exercice, chunk, contrat, validation) |
| `db/schema.sql` | Schéma PostgreSQL (corpus, banque, validations) |
| `scripts/` | Pipeline : crawl, ingest, index, verify, similarity, coverage, assemble |
| `mcp/` | Serveurs MCP FastMCP (corpus, banque, sympy, latex) |
| `prompts/` | Prompts systèmes des agents de composition |
| `gabarits/` | Classe LaTeX `nexus-manuel.cls` + macros + gabarit chapitre |
| `chapitres/` | Un dossier par chapitre (objets .tex + validations + rapports LOT) |
| `.claude/commands/` | Slash commands Claude Code |
