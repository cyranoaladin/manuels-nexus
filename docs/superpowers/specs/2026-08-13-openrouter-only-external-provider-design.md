# Exclusivité OpenRouter pour les appels LLM externes

**Date :** 13 août 2026
**Statut :** spécification approuvée, non implémentée, contrat fermé après revue
**Décision humaine :** approche B — exclusivité réelle
**Base de conception :** `a21a1787229844c1d9c3616c0c3213c7095fa9dc`
**Décision de publication inchangée :** **NO-GO**

## 1. Décision

OpenRouter devient l'unique passerelle autorisée pour tout appel LLM externe,
actif ou nouveau, du dépôt.

Cette décision porte sur la destination réseau et le client utilisés, pas sur
l'auteur du modèle choisi dans le catalogue OpenRouter. Un identifiant de
modèle OpenRouter peut contenir un espace de noms d'auteur ; il ne permet jamais
d'appeler directement l'API de cet auteur.

Le contrat est fermé :

- un appel LLM externe passe exclusivement par
  `POST https://openrouter.ai/api/v1/chat/completions` ;
- l'authentification utilise `Authorization: Bearer <OPENROUTER_API_KEY>` ;
- chaque requête nomme exactement un modèle fourni par `OPENROUTER_MODEL` ;
- aucun SDK, endpoint, secret ou repli d'un fournisseur direct n'est admis ;
- aucun endpoint LLM local ou configurable arbitrairement n'est admis ;
- l'absence de clé sélectionne le comportement local déterministe lorsqu'un
  appelant en possède un ; elle n'ouvre aucune connexion ;
- la présence d'une clé sans modèle est une erreur explicite avant réseau ;
- les consultations Chutes cessent ;
- les preuves historiques Chutes, les verdicts déjà produits et les anciens
  documents de décision ne sont ni réécrits, ni déplacés, ni renommés.

L'interface officielle est la
[création d'une chat completion OpenRouter](https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion).
La gestion des enveloppes d'échec suit la documentation
[Errors and Debugging](https://openrouter.ai/docs/api/reference/errors-and-debugging).
La comptabilité suit la documentation officielle
[Usage Accounting](https://openrouter.ai/docs/cookbook/administration/usage-accounting) :
les tokens, le coût et les compteurs de cache proviennent de la réponse, jamais
d'une table tarifaire locale.
Le catalogue
[`GET /api/v1/models`](https://openrouter.ai/docs/api/api-reference/models/list-all-models-and-their-properties)
est réservé à un smoke test humain et n'est jamais appelé en production, dans
Pytest ou dans la CI.

## 2. État réel inventorié

### 2.1 Instructions applicables

Les modifications à la racine, en Mathématiques et sous `NSI/` obéissent à
`AGENTS.md`. Toute modification sous `NSI/corpus_nsi/` obéit en plus au fichier
plus proche `NSI/corpus_nsi/AGENTS.md`, qui impose notamment :

- des gates de policy fail-closed ;
- la non-promotion automatique des jugements de substance ;
- la séparation entre auteur et juge ;
- l'absence de données personnelles d'élèves ;
- la distinction entre recherche RAG et validation pédagogique.

Ces deux fichiers sont lus intégralement avant le lot Red et relus si leur
contenu change avant Green.

### 2.2 Quatre appelants réseau LLM actifs

L'inventaire de la base identifie quatre appelants à migrer :

1. `Mathematiques/manuel-maths/scripts/ingest.py` appelle directement le SDK
   Anthropic pour classifier un fragment limité à 3 000 caractères ;
2. `NSI/scripts/ingest.py`, identique au précédent, fait le même appel ;
3. `NSI/corpus_nsi/scripts/judge_campaign.py` appelle directement
   `https://api.anthropic.com/v1/messages`, lit `ANTHROPIC_API_KEY` et fixe un
   modèle Anthropic ;
4. `NSI/corpus_nsi/scripts/substance_judge.py` construit son endpoint LLM à
   partir de `LOCAL_LLM_BASE_URL` et peut donc atteindre une URL arbitraire.

`NSI/corpus_nsi/scripts/run_substance_judge.py` n'appelle actuellement aucun
LLM : il produit un pré-jugement déterministe hors réseau. Il mentionne
néanmoins Anthropic et choisit par défaut un nom de modèle Claude. Il doit
rester déterministe et devenir fournisseur-neutre, sans défaut Claude.

### 2.3 Configuration et gouvernance liées

Les surfaces actives comprennent aussi :

- `.env.rag.example`, qui expose `LOCAL_LLM_*` ;
- `rag_config.example.yml`, dont la section `llm` fixe actuellement
  `engine: ollama` et un modèle local ;
- `scripts/check_rag_config.py`, qui rend ces variables obligatoires ;
- les tests de gouvernance, de secrets, de juge et de policy ;
- le `Makefile` et les commandes existantes du corpus ;
- les requirements du corpus, qui ne contiennent pas encore `httpx` ;
- les README et documents actifs qui décrivent le RAG ou les juges.

Les endpoints RAG, embedding et base vectorielle ne sont pas des endpoints LLM.
Ils restent hors migration lorsque leur usage est le retrieval existant. En
particulier, `RAG_API_BASE_URL`, `EMBEDDING_BASE_URL` et `VECTOR_DB_URL` ne sont
ni supprimés ni redirigés vers OpenRouter.

### 2.4 Collision de noms Python vérifiée

Un paquet racine nommé `scripts` existe, mais les deux manuels et le corpus NSI
possèdent aussi leur propre dossier `scripts`. Depuis leurs commandes normales,
le dossier local peut masquer le paquet racine. L'architecture initialement
envisagée sous `scripts/openrouter_*` est donc abandonnée.

## 3. Objectifs

Le lot d'implémentation devra :

1. établir une seule frontière réseau LLM, testable et partagée ;
2. préserver les modes déterministes locaux et l'absence de réseau en CI ;
3. faire déléguer les quatre appelants réseau au même client ;
4. maintenir `run_substance_judge.py` hors réseau et fournisseur-neutre ;
5. supprimer les dépendances, clés et endpoints LLM directs actifs ;
6. aligner les autorités, configurations et guides opérationnels actifs ;
7. empêcher fail-closed l'ajout d'un nouveau client fournisseur hors allowlist ;
8. préserver les endpoints RAG non-LLM et leurs barrières de collection ;
9. préserver les historiques, verdicts et preuves existants ;
10. ne modifier aucun contrat métier, contenu scolaire, PDF ou gate de
    publication.

## 4. Architecture cible

```text
ingest Mathématiques ─┐
ingest NSI ───────────┼─> nexus_external.openrouter_client
judge_campaign ───────┤          │
substance_judge ──────┘          v
                         POST OpenRouter chat/completions

run_substance_judge ─────> pré-jugement déterministe, zéro réseau
search_rag ───────────────> endpoint RAG existant, distinct du LLM
```

### 4.1 Paquet racine non ambigu

Le code partagé est créé dans :

- `nexus_external/__init__.py` ;
- `nexus_external/openrouter_client.py` ;
- `nexus_external/classification.py`.

`nexus_external` ne collisionne avec aucun dossier local existant et matérialise
la frontière des services externes. Aucun module `scripts/openrouter_*` n'est
créé.

### 4.2 Découverte déterministe de la racine Git

Les quatre appelants découvrent la racine Git à partir de leur propre
`Path(__file__).resolve()`, en remontant les parents jusqu'au premier marqueur
`.git` correspondant au checkout courant. Ils placent cette racine précise en
tête de `sys.path`, avec `sys.path.insert(0, ...)`, avant d'importer
`nexus_external`. Un chemin déjà présent plus loin dans `sys.path` est d'abord
retiré afin que la racine découverte reste prioritaire.

Après import, chaque adaptateur résout `nexus_external.__file__` et vérifie que
le module chargé se trouve exactement sous
`<racine découverte>/nexus_external/`. Une installation homonyme globale, un
autre checkout ou un paquet masqué fait échouer l'appelant avant tout réseau.

Le mécanisme :

- ne dépend pas du répertoire courant ;
- ne dépend pas d'un `PYTHONPATH` fourni manuellement ;
- échoue explicitement si la racine n'est pas trouvée ;
- n'accepte pas une racine passée par l'environnement ;
- est identique dans les quatre adaptateurs, ou factorisé seulement si cela ne
  réintroduit aucune collision.

Les commandes à préserver sont :

- Mathématiques : `make ingest` depuis `Mathematiques/manuel-maths/` ;
- NSI : `python3 scripts/ingest.py` depuis `NSI/` ;
- corpus : les commandes Python existantes depuis `NSI/corpus_nsi/`, dont
  `python -m scripts.judge_campaign` et
  `python -m scripts.substance_judge`.

Aucune nouvelle cible Makefile NSI n'est ajoutée : elle serait sans appelant et
violerait YAGNI.

### 4.3 `nexus_external/openrouter_client.py`

Le client possède une responsabilité : envoyer une chat completion OpenRouter
non streamée et retourner un résultat structuré immuable
`OpenRouterCompletion`.

`OpenRouterCompletion` contient exactement :

- `content`, contenu textuel complet de la première choice ;
- `generation_id`, champ racine `id` de la réponse ;
- `model`, champ racine `model` réellement retourné ;
- `provider`, chaîne optionnelle lorsque OpenRouter la retourne ;
- `usage`, valeur immuable structurée contenant exactement
  `prompt_tokens`, `completion_tokens`, `total_tokens`, `cost`,
  `cached_tokens` et `cache_write_tokens`.

Les appelants consomment cet objet sans accéder au JSON brut. La classification
n'utilise que `content` dans sa logique métier ; elle ignore la valeur de
`usage`, mais pas sa validation par le client. Les deux juges peuvent consigner
les identifiants et la comptabilité validés.

L'interface publique reçoit explicitement la clé, le modèle, les messages, la
limite de sortie et un transport `httpx` injectable. Les tests remplacent le
réseau par `httpx.MockTransport`.

Le client :

- fixe en code l'URL HTTPS exacte ;
- envoie `Content-Type: application/json` et le Bearer attendu ;
- inclut un unique champ `model`, jamais `models` ;
- utilise `max_completion_tokens`, et non `max_tokens` ;
- utilise `max_completion_tokens: 200` pour la classification des ingestions ;
- accepte une autre limite explicite et bornée pour les juges, sans changer le
  modèle ni l'endpoint ;
- applique un timeout borné à toutes les phases HTTP, au plus 30 secondes par
  requête dans le premier lot ;
- refuse une clé ou un modèle vide avant toute requête ;
- ne suit pas de redirection vers une autre origine ;
- ne fait aucun retry implicite dans le client partagé ;
- ne journalise ni clé, ni header, ni prompt, ni réponse brute.

### 4.4 Validation stricte de la réponse OpenRouter

Une réponse est utilisable uniquement si elle est HTTP 2xx et possède une
première choice complète avec un `message.content` textuel non vide.

Le client refuse, même sous HTTP 200 :

- un objet `error` au niveau racine ;
- un objet `error` dans la première choice ;
- `finish_reason == "error"` ;
- une choice absente ou d'un type invalide ;
- un message absent ou invalide ;
- un contenu vide ;
- tout `finish_reason` différent de `stop`, notamment `length`,
  `content_filter` ou `error` ;
- un `id` ou un `model` racine absent, vide ou non textuel ;
- un `provider` présent mais vide ou non textuel ;
- un objet `usage` absent ou invalide ;
- une enveloppe non JSON ou de forme inattendue.

Le contrat de comptabilité est unique pour tous les appelants. Les champs
`prompt_tokens`, `completion_tokens` et `total_tokens` sont des entiers non
négatifs, avec refus explicite des booléens, et
`total_tokens == prompt_tokens + completion_tokens`. `cost` est un nombre fini
non négatif, booléens refusés. `cached_tokens` et `cache_write_tokens` sont lus
depuis `usage.prompt_tokens_details` ; lorsqu'un de ces champs optionnels n'est
pas retourné par OpenRouter, il est normalisé à `0`. S'il est présent, il doit
être un entier non négatif, booléens refusés, et ne pas dépasser
`prompt_tokens`. Un objet de détails présent mais mal typé est refusé.

Le client exige donc toujours une comptabilité valide, y compris pour la
classification. Il ne lance pas de second appel à `/generation` pour réparer
une réponse. Ce choix donne un seul protocole fail-closed et garantit que le
juge comptable ne reçoit jamais une complétion dépourvue de preuve d'usage.

Les tests couvrent au minimum 400, 401, 402, 403, 408, 429 et les erreurs 5xx,
ainsi que les erreurs dans une enveloppe HTTP 200. Les catégories exposées
distinguent configuration, paiement/crédits, authentification/autorisation,
limitation de débit, timeout/transport, indisponibilité et protocole.

Les exceptions sont stables et expurgées : elles peuvent contenir la catégorie,
le statut, l'endpoint constant et le modèle public ; elles ne contiennent jamais
la clé, le prompt, le fragment, le corps brut ou les headers.

## 5. Classification partagée

### 5.1 Deux chemins explicites

`nexus_external/classification.py` expose :

- une heuristique locale pure ;
- une fonction de classification qui interprète une vue injectée de
  l'environnement ;
- une fonction pure qui parse et valide la sortie distante.

La matrice est :

| `OPENROUTER_API_KEY` | `OPENROUTER_MODEL` | Comportement |
|---|---|---|
| absente ou vide | toute valeur | heuristique locale, zéro réseau |
| présente | absente ou vide | erreur de configuration avant réseau |
| présente | présente | un POST OpenRouter avec ce modèle exact |

Aucun autre nom de variable de clé ou endpoint LLM n'est interprété.

### 5.2 Objet de classification fermé

Le JSON distant valide est un objet fermé contenant exactement les cinq clés :

- `chunk_type` : l'une de `cours`, `methode`, `exercice`, `corrige`,
  `activite`, `evaluation`, `erreur_type`, `autre` ;
- `niveau` : l'une de `2GT`, `1SPE`, `TSPE`, `TEXP`, ou `null` ;
- `theme` : une chaîne, ou `null` ;
- `capacites` : une liste de chaînes ;
- `difficulte` : l'entier 1, 2 ou 3, ou `null`.

En Python, `bool` est explicitement refusé pour `difficulte`, même s'il est un
sous-type de `int`. Une clé manquante ou supplémentaire, un type invalide, un
enum inconnu ou un JSON non décodable invalide l'objet entier. Il n'y a pas de
validation ou de fusion champ par champ.

Toute sortie invalide devient le résultat conservateur global :

```json
{
  "chunk_type": "autre",
  "niveau": null,
  "theme": null,
  "capacites": [],
  "difficulte": null
}
```

Le prompt de classification conserve sa finalité et transmet au plus les
3 000 premiers caractères du fragment. La requête utilise
`max_completion_tokens: 200`.

### 5.3 Barrière des métadonnées de confiance

Le dictionnaire distant n'est jamais étalé sur le record complet. Seules les
cinq clés validées sont retournées par la classification, puis l'ingestion
construit elle-même les métadonnées de confiance :

- `source_id` ;
- `doc_url` ;
- `doc_hash` ;
- `content_md` ;
- `usage_policy` ;
- `tier`.

Les tests injectent des sorties hostiles contenant ces noms, ou une deuxième
valeur destinée à les écraser. L'objet distant est rejeté globalement et aucune
métadonnée de provenance, de contenu ou de politique ne change.

## 6. Migration des juges du corpus NSI

### 6.1 `judge_campaign.py`

`judge_campaign.py` remplace son transport Anthropic direct par le client
OpenRouter partagé. Il lit uniquement `OPENROUTER_API_KEY` et
`OPENROUTER_MODEL`, d'abord depuis l'environnement puis, pour les valeurs
absentes, depuis le `.env.rag` local ignoré résolu par
`scripts.rag_core.resolve_env_file(ROOT)`. Il ne lit plus le `.env` générique.

Le protocole de verdict, les quatre exemples, la validation avant écriture, la
non-promotion et la séparation juge/auteur restent inchangés. La migration
adapte les messages au format Chat Completions sans affaiblir les vérifications.
Le modèle consigné dans `judge_model` est la valeur explicite
`OPENROUTER_MODEL` réellement demandée, pas une constante Claude.

Les retries métier déjà explicites dans la campagne peuvent être conservés
dans l'appelant si leurs tests en bornent le nombre et les délais. Le client
partagé, lui, reste sans retry et ne sélectionne jamais un modèle de repli.

#### 6.1.1 Journal comptable versionné

`substance_reviews/campaign/_usage_log.json` est un historique actif, mais ses
entrées existantes constituent le schéma v1 et ne sont pas migrées. La
fusion-upsert conserve chaque objet v1, ses valeurs et son ordre relatif sans
ajouter, supprimer ou renommer de champ. En particulier, aucune ancienne ligne
n'est recalculée avec les données OpenRouter.

Chaque complétion OpenRouter réussie ajoute une entrée de schéma v2 contenant :

- `schema_version: 2` et `provider: openrouter` ;
- `cap`, `seq`, l'index de tentative et `judged_at` ;
- `model` et `generation_id` issus de `OpenRouterCompletion` ;
- `prompt_tokens`, `completion_tokens`, `total_tokens`, `cached_tokens` et
  `cache_write_tokens` issus de son `usage` validé ;
- `cost_usd`, copie exacte de `usage.cost`.

Le coût n'est jamais recalculé, arrondi à partir des tokens ou obtenu depuis un
tarif de modèle. Le code ne contient plus de prix Claude, de coefficient de
cache Anthropic, de seuil de cache Anthropic ni d'alerte fondée sur un minimum
de tokens Anthropic.

Une entrée v2 réussie est identifiée de façon stable par son
`generation_id` ; rejouer l'upsert avec le même identifiant la remplace sans
duplication. Les entrées v2 d'autres générations et toutes les entrées v1 sont
préservées, y compris lorsqu'elles portent le même `cap`. Ainsi, une tentative
supplémentaire facturée garde sa propre génération et son propre coût. Une
erreur sans réponse exploitable peut être consignée comme entrée v2 d'échec,
avec `provider`, `model`, `cap`, `seq`, tentative, date et catégorie expurgée,
mais sans inventer `generation_id`, compteurs ou `cost_usd`.

Les totaux affichés pour le run courant somment seulement les entrées v2
réussies produites pendant ce run. Ils ne mélangent pas les anciens noms v1
`read`, `write`, `fresh` et `out`. La compatibilité v1 est prouvée par fixture
et comparaison profonde avant/après fusion ; la comptabilité v2 est prouvée
avec des mutations de coût et de compteurs de cache afin qu'aucune formule
locale ne puisse passer.

### 6.2 `substance_judge.py`

Seul le transport LLM de `substance_judge.py` migre vers OpenRouter. La recherche
`search_rag()` continue d'utiliser `RAG_API_BASE_URL`, son Bearer RAG et les
barrières de collection existantes. Le lot interdit de réutiliser le client
OpenRouter pour le RAG.

Les variables `LOCAL_LLM_ENGINE`, `LOCAL_LLM_BASE_URL`, `LOCAL_LLM_MODEL` et
`LOCAL_LLM_API_KEY` disparaissent de la configuration active. Aucun endpoint
local, URL configurable ou défaut `qwen` ne subsiste pour le juge LLM.

Sans clé OpenRouter, le juge retourne son résultat conservateur actuel sans
réseau. Avec une clé sans modèle, il échoue avant réseau. Une erreur distante
reste une erreur expurgée ou un verdict conservateur explicitement attribué à
l'indisponibilité, selon le contrat existant testé ; elle ne bascule vers aucun
autre fournisseur et ne promeut jamais un verdict.

### 6.3 `run_substance_judge.py`

`run_substance_judge.py` reste intégralement déterministe et hors réseau. Il ne
doit pas importer le client OpenRouter. Sa docstring, ses usages et son option
`--model` deviennent fournisseur-neutres ; aucun nom Claude n'est la valeur par
défaut. Le champ `judge_model` doit décrire honnêtement le pré-jugement
déterministe, par exemple `deterministic-prejudge`, et ne pas laisser croire à
une consultation distante.

### 6.4 Gouvernance RAG et requirements

La migration met à jour ensemble :

- `NSI/corpus_nsi/.env.rag.example` ;
- `NSI/corpus_nsi/rag_config.example.yml` ;
- `NSI/corpus_nsi/scripts/check_rag_config.py` ;
- les tests qui verrouillent cette configuration ;
- les tests de secrets concernés ;
- les documents RAG actifs ;
- `NSI/corpus_nsi/requirements.txt`.

L'exemple RAG conserve ses variables RAG, embedding, vector DB et SSH. Pour le
LLM il expose seulement :

```dotenv
OPENROUTER_API_KEY=
OPENROUTER_MODEL=
```

`check_rag_config.py` exige ces deux clés, exige que la clé d'exemple soit vide,
refuse les quatre anciennes variables `LOCAL_LLM_*` et continue de contrôler
les paramètres RAG sans les transformer.

La section locale `llm` est supprimée de `rag_config.example.yml`. Aucune
section de remplacement `external_llm` n'y est ajoutée : `.env.rag` porte déjà
les deux paramètres OpenRouter, et dupliquer modèle ou endpoint créerait une
seconde autorité. `check_rag_config.py` et
`tests/test_rag_governance_and_indexes.py` refusent explicitement toute section
`llm`, notamment `llm.engine: ollama`, toute section `external_llm`, toute clé
`LOCAL_LLM_*` et tout endpoint de chat arbitraire. Ils acceptent et préservent
les sections et variables existantes de RAG, embedding et base vectorielle ;
les URL non-LLM ne sont ni renommées ni assimilées à un endpoint de chat.

`httpx==0.28.1` est ajouté au requirements du corpus afin que ses tests isolés
puissent importer le client partagé. Cette version est compatible avec le
contrat `httpx>=0.27` des deux autres projets. Aucun SDK LLM n'est ajouté.

## 7. Données, secrets et sécurité

### 7.1 Précondition opératoire

Le code ne peut pas prouver qu'un texte libre ne contient aucune donnée
personnelle ou aucun secret. Avant d'activer OpenRouter, l'opérateur doit donc
vérifier que le fragment est autorisé, anonymisé si nécessaire, et exempt de
secret. Un contenu qui ne satisfait pas cette précondition reste en mode local
ou est rejeté ; il n'est pas transmis.

Cette règle complète, sans la remplacer, l'interdiction du plus proche
`NSI/corpus_nsi/AGENTS.md` concernant les données d'élèves.

### 7.2 Propriétés prouvables par le code

Pour la classification des ingestions, les tests prouvent que la requête ne
contient que :

- les instructions statiques de classification ;
- au plus les 3 000 premiers caractères du fragment fourni ;
- le modèle explicite et la limite de sortie.

Elle ne contient aucune variable d'environnement supplémentaire, métadonnée de
source, URL de document, hash, manifeste, chemin de machine ou fichier joint.

Pour les juges de substance, les données nécessaires sont plus larges et déjà
définies par leurs protocoles. La migration ne les étend pas. Leurs tests
prouvent que le client reçoit uniquement les messages construits par l'appelant
et aucune copie implicite de l'environnement.

### 7.3 Secrets et erreurs

- les vraies clés restent dans l'environnement ou un fichier local ignoré ;
- les exemples committés utilisent une valeur vide ;
- la CI n'a besoin d'aucune vraie clé ;
- les tests utilisent des sentinelles et prouvent leur absence des exceptions,
  logs et artefacts ;
- la clé n'est jamais écrite dans une preuve, un verdict ou un snapshot ;
- les réponses distantes restent non fiables et sont validées avant usage.

Une réponse OpenRouter reste consultative. Elle ne vaut ni source officielle,
ni validation scientifique, ni validation pédagogique, ni approbation humaine.

## 8. Surfaces actives canoniques

Le gate de politique utilise l'allowlist versionnée ci-dessous. Une surface
active ajoutant un transport LLM ou un client fournisseur en dehors de cette
liste fait échouer le gate ; le scan ne se contente pas d'une recherche négative
sur un fichier éventuellement absent.

### 8.1 Code actif autorisé

- `nexus_external/__init__.py` ;
- `nexus_external/openrouter_client.py` — seul fichier autorisé à contenir
  l'endpoint OpenRouter et à instancier le client HTTP LLM ;
- `nexus_external/classification.py` ;
- `Mathematiques/manuel-maths/scripts/ingest.py` ;
- `NSI/scripts/ingest.py` ;
- `NSI/corpus_nsi/scripts/judge_campaign.py` ;
- `NSI/corpus_nsi/scripts/substance_judge.py` ;
- `NSI/corpus_nsi/scripts/run_substance_judge.py` ;
- `NSI/corpus_nsi/scripts/check_rag_config.py` ;
- `NSI/corpus_nsi/scripts/check_rag_freshness.py` — réseau RAG seulement ;
- `NSI/corpus_nsi/scripts/ingest_nsi_corpus.py` — ingestion, embedding et vector
  DB seulement ;
- `NSI/corpus_nsi/scripts/rag_diagnose_search_timeout.py` — diagnostic RAG
  seulement ;
- `NSI/corpus_nsi/scripts/rag_ingest_server.py` — embedding et Chroma seulement ;
- `NSI/corpus_nsi/scripts/rag_query_example.py` — génération d'un exemple de
  requête RAG, sans client LLM ;
- `NSI/corpus_nsi/scripts/rag_smoke_test.py` — smoke RAG seulement.

Les quatre appelants peuvent importer le client, mais ne contiennent aucun
endpoint LLM, import de SDK fournisseur ou création de client HTTP LLM.
Les six fichiers RAG nommés peuvent instancier leur transport existant
uniquement vers les variables et endpoints non-LLM documentés. Le gate inspecte
leurs sources/destinations et refuse qu'ils deviennent une exemption générique
pour un appel de chat, de messages ou de completions.

### 8.2 Configuration, dépendances et workflows actifs

- `Mathematiques/manuel-maths/.env.example` ;
- `NSI/.env.example` ;
- `NSI/corpus_nsi/.env.rag.example` ;
- `NSI/corpus_nsi/rag_config.example.yml` ;
- `Mathematiques/manuel-maths/requirements.txt` ;
- `NSI/requirements.txt` ;
- `NSI/corpus_nsi/requirements.txt` ;
- `requirements-ci-audit.txt`, complété par `httpx==0.28.1` et sa fermeture
  transitive épinglée puisque les workflows racine installent avec `--no-deps` ;
- `pyproject.toml` ;
- `Mathematiques/manuel-maths/Makefile` ;
- `NSI/Makefile` ;
- `NSI/corpus_nsi/Makefile` ;
- `.github/workflows/ci-audit-collection.yml` ;
- `.github/workflows/ci-mathematiques.yml` ;
- `.github/workflows/ci-nsi.yml` ;
- `NSI/corpus_nsi/.github/workflows/ci.yml`.

Les Makefiles et workflows ne reçoivent aucune nouvelle cible réseau. Ils sont
scannés pour prouver que Pytest/CI n'appelle ni OpenRouter, ni le catalogue des
modèles, ni un fournisseur direct.

L'allowlist de configuration nomme les deux fichiers RAG. Un nouveau fichier de
configuration contenant une destination LLM, ou la réintroduction d'une
section LLM dans `rag_config.example.yml`, fait échouer le gate.

### 8.3 Tests actifs à créer ou adapter

- `tests/test_openrouter_client.py` ;
- `tests/test_openrouter_classification.py` ;
- `tests/test_external_provider_policy.py` ;
- `Mathematiques/manuel-maths/tests/test_ingest_openrouter.py` ;
- `NSI/tests/test_ingest_openrouter.py` ;
- `NSI/corpus_nsi/tests/test_openrouter_judges.py` ;
- `NSI/corpus_nsi/tests/test_rag_governance_and_indexes.py` ;
- `NSI/corpus_nsi/tests/test_secret_guard.py` ;
- `NSI/corpus_nsi/tests/test_substance_judge_pipeline.py` ;
- `NSI/corpus_nsi/tests/test_substance_hardened.py` ;
- `NSI/corpus_nsi/tests/test_judge_collection_barriers.py` ;
- `NSI/corpus_nsi/tests/test_policy_checker_ast.py`.

Les mutations du gate ajoutent un faux client `requests`, `urllib`, `httpx` ou
SDK fournisseur dans un nouveau fichier actif et doivent obtenir un échec.

### 8.4 Documentation active à aligner

Les quatre autorités ou guides racine sont obligatoires :

- `AGENTS.md` ;
- `.agents/skills/nexus-manual-quality/SKILL.md` ;
- `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md` ;
- `README.md`.

Les surfaces opérationnelles identifiées sont également alignées :

- `Mathematiques/PROMPT_MISSION_AUTONOME.md` ;
- `Mathematiques/workflow_production_manuel.md` ;
- `Mathematiques/manuel-maths/README.md` ;
- `Mathematiques/manuel-maths/CAHIER_DES_CHARGES.md` ;
- `Mathematiques/manuel-maths/docs/02_workflow_production.md` ;
- `Mathematiques/manuel-maths/docs/03_architecture_technique.md` ;
- `NSI/CAHIER_DES_CHARGES.md` ;
- `NSI/docs/02_workflow_production.md` ;
- `NSI/docs/03_architecture_technique.md` ;
- `NSI/corpus_nsi/README.md` ;
- `NSI/corpus_nsi/rag_connection.md` ;
- `NSI/corpus_nsi/substance_pipeline.md` ;
- `NSI/corpus_nsi/docs/enrichment_roadmap.md` lorsqu'il prescrit encore une
  campagne active.

Les formulations ne promettent ni remise, ni Batch API, ni modèle par défaut,
ni disponibilité permanente.

## 9. Exclusions historiques immuables

Le gate distingue les instructions actives des traces datées. Les chemins ou
catégories suivants sont exclus des migrations textuelles et protégés par hash
ou par diff d'allowlist :

- `audit/chutes/**` ;
- les autres fichiers existants sous `audit/**` qui relatent un état antérieur ;
- `docs/codex/**` lorsqu'il décrit un contrôle daté ;
- les anciens fichiers sous `docs/superpowers/plans/**` ;
- les anciennes spécifications sous `docs/superpowers/specs/**`, à l'exception
  du présent fichier corrigé ;
- `NSI/corpus_nsi/reports/**`, y compris explicitement
  `reports/excellence_remediation_progress.md`, même lorsqu'un rapport conserve
  une ancienne instruction Anthropic ;
- `NSI/corpus_nsi/docs/judge_campaign_plan.md`, plan daté et en lecture seule ;
- `NSI/corpus_nsi/substance_reviews/**` et tout verdict JSON déjà produit, avec
  une seule exception de conteneur :
  `substance_reviews/campaign/_usage_log.json` peut recevoir des entrées v2,
  tandis que chacun de ses objets v1 reste protégé sans migration ;
- les manifests et inventaires générés décrivant l'état antérieur ;
- les fixtures historiques qui représentent explicitement une ancienne preuve,
  sauf si elles sont l'entrée active d'un test de la nouvelle politique.

Une occurrence historique n'est pas une instruction active. Elle ne doit pas
faire échouer un scan correctement routé, et elle ne doit jamais être réécrite
pour faire croire que le passé utilisait OpenRouter.

Les nouvelles consultations ou smoke tests sont consignés sous
`audit/openrouter/`. Aucun nouvel artefact n'est écrit sous `audit/chutes/`.

## 10. Contrat TDD Red

Le jalon Red est committé avant toute modification de production. Chaque famille
échoue pour une raison attendue et aucune erreur de collecte ne masque le Red.

### 10.1 Client OpenRouter

Les tests couvrent :

1. URL exacte, POST, Bearer, JSON, `model` unique et
   `max_completion_tokens` ;
2. injection de `httpx.MockTransport` et zéro socket réel ;
3. timeout borné et redirections non suivies ;
4. extraction d'un `OpenRouterCompletion` immuable avec identifiant, modèle,
   provider optionnel et usage structuré ;
5. refus des erreurs HTTP 400, 401, 402, 403, 408, 429 et 5xx ;
6. refus d'un objet `error` racine ou dans la choice sous HTTP 200 ;
7. refus de `finish_reason: error`, `length` ou autre contenu partiel ;
8. refus d'une enveloppe, choice, message ou content mal typé ;
9. absence des clés, prompts et corps bruts dans exceptions et logs ;
10. absence de retry ou de modèle de repli implicite ;
11. refus de `usage` absent, de tokens négatifs, booléens ou incohérents, d'un
    coût négatif/non fini et de détails de cache invalides ;
12. normalisation à zéro des seuls compteurs de cache optionnels absents et
    conservation exacte de `usage.cost`.

### 10.2 Classification

Les tests couvrent :

1. la matrice complète clé/modèle ;
2. zéro requête sans clé ;
3. erreur avant requête avec clé sans modèle ;
4. limite exacte de 3 000 caractères du fragment envoyé ;
5. `max_completion_tokens: 200` ;
6. conservation de l'heuristique locale ;
7. objet valide avec exactement cinq clés ;
8. rejet global des clés manquantes, extras, enums et types invalides ;
9. rejet explicite de `True` et `False` pour `difficulte` ;
10. résultat conservateur global sur toute sortie invalide ;
11. impossibilité d'écraser les six métadonnées de confiance ;
12. absence d'environnement, chemin, URL, hash ou métadonnée ajoutés au prompt.

### 10.3 Quatre appelants et pré-jugement

Les tests couvrent :

1. la délégation des deux ingestions au paquet racine ;
2. l'exécution de `make ingest` côté Mathématiques et de
   `python3 scripts/ingest.py` côté NSI dans un scénario sans source/réseau ;
3. la délégation de `judge_campaign.py` au client commun, sans endpoint ni clé
   Anthropic ;
4. la délégation du seul transport LLM de `substance_judge.py`, sans modifier
   son transport RAG ;
5. la disparition de `LOCAL_LLM_*` et de tout endpoint LLM arbitraire ;
6. le fonctionnement déterministe de `run_substance_judge.py`, sans import
   réseau ni défaut Claude ;
7. la non-promotion des verdicts et la conservation des vetos existants ;
8. la découverte de la racine depuis chacun des quatre `__file__`, avec un
   répertoire courant différent ;
9. la priorité de cette racine dans `sys.path` et le refus d'un
   `nexus_external` chargé depuis un autre checkout ou une installation globale ;
10. l'absence d'import `anthropic` et de lecture `ANTHROPIC_API_KEY` actifs ;
11. les entrées v2 du journal : identifiants, modèle, tokens, cache et copie
    exacte du coût OpenRouter ;
12. la conservation profonde et de l'ordre relatif d'une fixture v1 lors de la
    fusion-upsert, même à `cap` identique ;
13. l'absence de tarif local, de calcul de coût Claude et d'alerte/seuil de
    cache Anthropic, verrouillée par mutations.

### 10.4 Policy, gouvernance et historique

Les tests couvrent :

1. l'allowlist canonique des surfaces actives ;
2. l'échec sur tout nouveau client fournisseur hors allowlist ;
3. la présence des fichiers scannés avant toute assertion négative ;
4. la conservation des endpoints RAG non-LLM ;
5. le contrat coordonné `.env.rag.example`, `rag_config.example.yml`,
   `check_rag_config.py` et `test_rag_governance_and_indexes.py`, incluant le
   rejet de `llm.engine: ollama`, de `LOCAL_LLM_*` et d'un endpoint arbitraire ;
6. l'absence de Chutes dans les quatre autorités actives ;
7. l'absence de `/api/v1/models` dans les tests, Makefiles et workflows CI ;
8. l'intégrité des catégories historiques protégées ;
9. l'absence de nouvelle cible Makefile NSI pour l'ingestion ;
10. l'absence de réseau réel dans toutes les suites ciblées.

Le corpus NSI n'est pas collecté par la configuration Pytest racine. Son contrat
est donc exécuté séparément :

```bash
cd NSI/corpus_nsi
python -m pytest \
  tests/test_rag_governance_and_indexes.py \
  tests/test_secret_guard.py \
  tests/test_openrouter_judges.py \
  tests/test_substance_judge_pipeline.py \
  tests/test_substance_hardened.py \
  tests/test_judge_collection_barriers.py \
  tests/test_policy_checker_ast.py
```

Le plan peut ajouter un fichier de test ciblé à cette commande, sans lancer le
réseau.

## 11. Green minimal et Refactor

### 11.1 Green

Green ajoute uniquement :

- le paquet `nexus_external` ;
- la classification partagée ;
- les quatre délégations réseau ;
- la neutralisation documentaire de `run_substance_judge.py` ;
- les requirements et exemples d'environnement nécessaires ;
- la suppression de la section LLM locale de `rag_config.example.yml` et la
  mise à jour coordonnée de `check_rag_config.py` et de ses tests ;
- le journal comptable v2 OpenRouter avec compatibilité v1 non destructive ;
- le gate de policy allowlist ;
- l'alignement des autorités et documents actifs ;
- les tests nécessaires pour rendre Red vert.

Il n'ajoute ni SDK LLM, ni nouvelle cible Makefile, ni modèle par défaut, ni
sélection automatique, ni nouvelle fonction RAG.

### 11.2 Refactor

Après Green seulement, les doublons de prompt, validation ou découverte de
racine peuvent être réduits si le refactor conserve :

- les commandes existantes ;
- les schémas de chunks et verdicts ;
- les vetos du juge ;
- les endpoints RAG ;
- l'absence de réseau en CI ;
- tous les tests de mutation du gate.

## 12. Gates d'acceptation

Le lot est acceptable lorsque :

- les tests ciblés racine sont verts avec `MockTransport` ;
- la suite ciblée séparée du corpus NSI est verte ;
- Ruff et les contrôles Python affectés sont verts ;
- les commandes des deux ingestions chargent `nexus_external` depuis leur
  contexte normal et les quatre appelants prouvent le chemin exact du module
  chargé ;
- `anthropic` a disparu des requirements/imports actifs et
  `ANTHROPIC_API_KEY` de la configuration active ;
- `LOCAL_LLM_*` a disparu de la configuration et du transport LLM actifs ;
- `rag_config.example.yml` ne contient aucune section LLM et son gate refuse
  `ollama`, une variable locale ou un endpoint de chat arbitraire sans altérer
  les endpoints RAG/embedding ;
- le seul endpoint LLM actif est dans
  `nexus_external/openrouter_client.py` ;
- les nouvelles lignes `_usage_log.json` sont v2, reprennent exactement le coût
  et les tokens OpenRouter, et les lignes v1 restent inchangées ;
- les endpoints RAG existants et leurs barrières restent inchangés ;
- les quatre autorités prescrivent OpenRouter et n'ordonnent plus Chutes ;
- le gate échoue lorsqu'un client fournisseur fictif est ajouté hors allowlist ;
- aucun test, Makefile ou workflow CI n'appelle un service LLM ou
  `/api/v1/models` ;
- les catégories historiques exclues sont octet-identiques à la base ; seule
  l'exception `_usage_log.json` peut changer, et ses objets v1 restent
  profondément identiques et dans le même ordre relatif ;
- `git diff --check` est vert ;
- `--release-strict` reste rouge pour les dettes éditoriales réelles et n'est
  ni affaibli ni requalifié.

Le smoke test humain OpenRouter est séparé. Sa réussite ne vaut ni validation
disciplinaire, ni correction P0, ni autorisation de publication.

## 13. Commits atomiques attendus

L'ordre recommandé pour l'implémentation est :

1. `[TESTS] verrouille la passerelle OpenRouter` — contrat Red uniquement ;
2. `[PYTHON] centralise les appels LLM via OpenRouter` — paquet partagé,
   quatre appelants, pré-jugement neutre, requirements et configurations ;
3. `[DOCS] aligne les autorites sur OpenRouter` — autorités et documentation
   opérationnelle actives ;
4. `[AUDIT] consigne le smoke OpenRouter` — seulement après un smoke humain
   réellement exécuté et vérifié.

Une correction issue de revue reçoit un commit ciblé supplémentaire. Aucun
commit ne mélange la migration avec une correction mathématique, une baseline
visuelle, une migration de corpus ou un P0 Wave 0.

## 14. Interaction avec Wave 0

Les trois plans Green P0 approuvés — provenance programme TSPE, séparation
élève/professeur et préflight des débordements — restent fournisseur-agnostiques
et hors réseau.

- la correction Programme reste autonome ;
- la tâche 2 Séparation reste bloquée séparément sur quatre dettes historiques
  observées sur sa base propre ;
- le lot Overflow reste empilé selon son plan approuvé ;
- aucun test Wave 0 n'est supprimé, ignoré, transformé en `skip`/`xfail` ou
  requalifié ;
- aucune consultation Chutes n'est effectuée pendant Wave 0 ;
- OpenRouter n'est pas requis pour les travaux déterministes locaux.

La branche OpenRouter reste distincte des branches Green P0 jusqu'à une décision
humaine d'intégration. Cette migration ne corrige aucun P0 et ne change pas le
**NO-GO**.

## 15. Critères de réalisation de la décision

La décision « OpenRouter-only » est implémentée seulement si les cinq propriétés
suivantes sont simultanément prouvées :

1. **unicité réseau LLM** — tout appel LLM actif atteint uniquement l'endpoint
   OpenRouter fixé ;
2. **unicité du transport** — les quatre appelants utilisent le même client
   `nexus_external` ;
3. **mode local réel** — sans clé, les chemins locaux restent sans réseau ;
4. **séparation RAG/LLM** — les endpoints RAG restent distincts et ne servent
   jamais de destination LLM ;
5. **traçabilité honnête** — les autorités actives sont à jour et les preuves,
   verdicts et rapports historiques restent intacts.

Tant qu'une propriété manque, le dépôt ne déclare pas l'exclusivité OpenRouter
comme réalisée.
