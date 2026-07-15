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
