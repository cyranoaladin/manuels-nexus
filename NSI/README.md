# Manuels NSI Première & Terminale — Noyau de production

Production agentique de deux manuels NSI d'accompagnement différencié (Nexus Réussite),
par **restructuration certifiée** du corpus propriétaire `cyranoaladin/NSI` (tier T0,
114 capacités, 445 tests) selon la méthodologie éprouvée du manuel de mathématiques.

## Démarrage

```bash
git submodule add https://github.com/cyranoaladin/NSI corpus_nsi   # ou clone local
make setup && cp .env.example .env
make referentiel            # programme_nsi_2019.yaml -> referentiel/*.json
claude                      # lit CLAUDE.md + DIRECTIVES_EN_COURS.md, démarre la mission
```

## Cartographie

| Chemin | Contenu |
|---|---|
| `CLAUDE.md` / `DIRECTIVES_EN_COURS.md` | Règles de l'agent + check-list persistante inter-sessions |
| `CAHIER_DES_CHARGES.md` / `PROMPT_MISSION_AUTONOME.md` | Exigences + mission |
| `docs/08_specificites_nsi.md` | Document maître : audit du corpus, table de transposition, gates NSI |
| `corpus_nsi/` | Dépôt NSI en submodule — SOURCE T0, lecture seule |
| `scripts/harvest_nsi.py` + `scripts/md2nexus.lua` | Récolte et transposition séquence → chapitre |
| `scripts/verify_python.py` | Gate d'exécution (VERIFY pytest + traces + ruff) |
| `gabarits/nexus-code.tex`, `nexus-figures-nsi.tex` | Extensions NSI de la charte Nexus |
| `chapitres/1NSI-TYPES-CONSTRUITS/` | Chapitre pilote |

La charte Nexus (cls, icônes, palette) est synchronisée depuis `manuel-maths` : ne modifier
que les fichiers d'extension NSI, jamais le tronc commun.
