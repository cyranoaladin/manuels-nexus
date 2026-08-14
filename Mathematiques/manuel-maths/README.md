# Manuel de mathématiques différencié — Noyau de production

Dépôt de production agentique d'un manuel de mathématiques conforme aux programmes officiels français, structuré pour la pédagogie différenciée (Nexus Réussite).

## Démarrage rapide

```bash
make setup                      # environnement + base de données
cp .env.example .env            # renseigner DATABASE_URL ; OpenRouter est optionnel
make crawl                      # collecte des sources actives du registre
make ingest && make index       # normalisation + indexation pgvector
```

## Accès LLM externe

La classification peut utiliser OpenRouter seulement si `OPENROUTER_API_KEY` et
`OPENROUTER_MODEL` sont tous deux renseignés. L'unique endpoint LLM autorisé est
`POST https://openrouter.ai/api/v1/chat/completions` ; aucun endpoint ni modèle
de repli n'est implicite. Sans clé, `make ingest` conserve la classification
locale déterministe et n'ouvre aucune connexion. Une clé sans modèle provoque
une erreur avant réseau.

Toute réponse distante reste consultative et doit être vérifiée localement :
elle ne vaut ni source officielle, ni validation disciplinaire, pédagogique ou
humaine. Aucun secret ni donnée personnelle ne doit être envoyé. Un smoke test
OpenRouter éventuel est lancé et vérifié par un humain uniquement, jamais par
la CI ni automatiquement.

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
| `.claude/commands/` | Commandes d'agent versionnées du projet |
