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

Le JSON régénéré par `make release-toolchain` dans
`validations/release-1spe/toolchain.json` est la seule source de vérité sur
l'exécution contrôlée. Le tableau suivant est l'instantané initial du
26 juillet 2026 ; il devient historique dès qu'un outil est mis à niveau :

| Composant | Instantané initial du 26 juillet 2026 | Exigence de release |
|---|---|---|
| Python | 3.12.3, conforme | 3.12.x |
| Java | 21.0.11, conforme | 21 minimum |
| LuaLaTeX | TeX Live 2023, bloquant | TeX Live 2026 minimum |
| Tagged PDF | porte non démontrée, bloquante | smoke-test LuaLaTeX + veraPDF PDF/UA-1 |
| veraPDF | absent, bloquant | CLI 1.30.1, profil `ua1`, rapport `mrr` |
| Poppler | 24.02.0, conforme | 24.02.0 minimum |
| Ghostscript | 10.02.1, conforme | 10.02 minimum |

TeX Live 2026 est un prérequis, jamais une preuve de capacité à lui seul. Le
contrôleur ne certifie `latex.tagged_pdf` qu'après avoir compilé, dans un
répertoire temporaire isolé, un document minimal dont `\DocumentMetadata`
active `pdfstandard=ua-1` et `tagging=on`, constaté la présence du PDF, puis
obtenu le code `0` de `verapdf -f ua1 --format mrr`. Les sources et sorties de
ce smoke-test sont supprimées automatiquement et aucun chemin temporaire
n'entre dans le rapport. Chaque PDF de production devra encore réussir sa
propre validation PDF/UA-1.

Chaque binaire est résolu une seule fois en chemin absolu avant les contrôles,
sans suivre le dernier lien symbolique : l'identité du lanceur trouvée par
`PATH` reste donc l'`argv[0]` des commandes de version et du smoke-test.
Celui-ci lance LuaLaTeX et veraPDF depuis son répertoire temporaire avec une
liste blanche d'environnement. Seul le `PATH` du parent est repris, après
avoir placé en tête le répertoire du Java 21 résolu et supprimé les doublons.
`JAVACMD` désigne exactement ce Java ; aucun `JAVA_HOME`, `JAVACMD` ou réglage
Java parent n'est hérité. Aucun `JAVA_OPTS` n'est transmis : un
`JAVA_TOOL_OPTIONS` de confiance, consommé directement par la JVM, redirige
`java.io.tmpdir` et `user.home` sous le temporaire et désactive PerfData avec
`-XX:-UsePerfData`. Ses chemins sont guillemetés afin de rester valides s'ils
contiennent des espaces. `LANG=C`, `LC_ALL=C` et `TZ=UTC` sont fixés.
`HOME`, `TMPDIR`, les trois répertoires XDG,
`TEXMFHOME`, `TEXMFVAR`, `TEXMFCONFIG`, `TEXMFCACHE` et `VARTEXFONTS`
pointent eux aussi vers des sous-répertoires éphémères. Cette politique sert
à `java -version`, à `verapdf --version` comme à la validation ; le smoke-test
ne démarre jamais si Java 21 n'est pas prouvé. Aucune autre variable du parent
— option TeX/Kpathsea, option Java ou secret — n'est transmise.

Le préflight ne tente aucune installation :

```bash
make release-toolchain
```

Il écrit un rapport déterministe dans
`validations/release-1spe/toolchain.json`. Un code retour `0` signifie que
tout le contrat d'outillage a été prouvé (`certified`). Le code `2` signifie
`blocked` et énumère les outils absents ou insuffisants. Ce code `2` est un
diagnostic honnête de l'exécution contrôlée, jamais un succès implicite. Même
si le manifeste est inaccessible ou invalide, l'ancien rapport est remplacé
atomiquement par un rapport `blocked` déterministe. Le fichier final reçoit
explicitement le mode documentaire `0644`.

Après mise à niveau explicite de l'environnement, relancer le préflight puis
la suite complète :

```bash
make release-toolchain
make release-test
```

## Baseline immuable 1SPE

La capture de départ distingue trois repères qui ne doivent jamais être
confondus :

- `origin.commit_sha` est l'origine historique immuable et conserve sa preuve
  de tests historique, sans prétendre l'avoir rejouée ;
- `current.commit_sha` est le snapshot préflight épinglé et sa preuve de tests
  directe ;
- `capture_context.capture_head_commit` est le HEAD réellement observé au
  moment où les deux artefacts sont générés. Il identifie le commit du code de
  capture ; le commit documentaire qui ajoute ensuite les artefacts est donc
  nécessairement son successeur.

Le périmètre versionné
[`release/baseline-scope-1spe.json`](release/baseline-scope-1spe.json) définit
explicitement l'univers, ses exclusions et l'unique catégorie de chaque
chemin. Chaque exclusion porte une justification contrôlée. La génération est
bloquée par tout chemin candidat non classé, tout double classement ou toute
règle qui capte un chemin hors univers. Indépendamment de cette déclaration,
chaque chemin réellement modifié entre l'origine et le snapshot courant doit
être classé exactement une fois ou correspondre à une exclusion justifiée.
Les objets Git exclus ou non classés ne sont pas lus.

La commande de référence est :

```bash
.venv/bin/python scripts/capture_initial_state_1spe.py \
  --root . \
  --json validations/release-1spe/baseline.json \
  --markdown validations/release-1spe/baseline.md
```

Les deux sorties sont exclusivement publiées sous
`validations/release-1spe/`. Leurs composants sont contrôlés sans suivre les
liens symboliques et la paire est restaurée intégralement si sa seconde
publication échoue. Le JSON est validé à la fois par le schéma fermé, par un
contrôleur de formats RFC 3339 et par les invariants croisés (inventaires,
compteurs, chaîne de remédiation, preuves de tests et attestations). Les
résumés de tests sont dérivés de leurs compteurs et refusent tout caractère de
contrôle. Le chemin et le SHA-256 du manifeste, les compteurs candidats ainsi
que les compteurs de chemins exclus sont revérifiés ; ces derniers sont
adossés à la liste triée des exclusions et à leurs justifications.

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
