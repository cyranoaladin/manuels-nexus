# Exclusivité OpenRouter pour les appels LLM externes

**Date :** 13 août 2026
**Statut :** spécification approuvée, non implémentée
**Décision humaine :** approche B — exclusivité réelle
**Base de conception :** `a21a1787229844c1d9c3616c0c3213c7095fa9dc`
**Décision de publication inchangée :** **NO-GO**

## 1. Décision

OpenRouter devient l'unique passerelle autorisée pour tout appel LLM externe,
actif ou nouveau, du dépôt.

Cette décision porte sur le chemin réseau et les clients utilisés, pas sur
l'auteur du modèle choisi dans le catalogue OpenRouter. Un identifiant de
modèle OpenRouter peut donc contenir un espace de noms d'auteur ; cela ne
permet jamais d'appeler directement l'API de cet auteur.

Le contrat est le suivant :

- un appel LLM externe passe exclusivement par
  `https://openrouter.ai/api/v1/chat/completions` ;
- l'authentification utilise `Authorization: Bearer <OPENROUTER_API_KEY>` ;
- chaque requête nomme explicitement un unique modèle configuré par
  `OPENROUTER_MODEL` ;
- aucun SDK, endpoint, secret ou mécanisme de repli d'un fournisseur direct
  n'est admis ;
- l'absence de clé sélectionne l'heuristique locale et n'ouvre aucune
  connexion ;
- la présence d'une clé sans modèle est une erreur de configuration explicite ;
- les consultations Chutes cessent ;
- les preuves historiques Chutes et les anciens documents de décision ne sont
  ni réécrits, ni déplacés, ni renommés.

L'API de référence est la
[création d'une chat completion OpenRouter](https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion).
Le catalogue
[`GET /api/v1/models`](https://openrouter.ai/docs/api/api-reference/models/list-all-models-and-their-properties)
est réservé à un smoke test humain. Il ne fait pas partie du chemin de
production et ne doit jamais être appelé par la CI.

## 2. Problème constaté

L'état de départ contient trois incohérences structurelles.

### 2.1 Autorités actives encore orientées vers Chutes

Quatre autorités ou guides actifs demandent encore de consulter Chutes :

1. `AGENTS.md` ;
2. `.agents/skills/nexus-manual-quality/SKILL.md` ;
3. `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md` ;
4. `README.md`.

Une modification limitée à un script laisserait donc le workflow contractuel
en contradiction avec la décision humaine.

### 2.2 Deux appels directs Anthropic identiques

Les fichiers suivants sont identiques à la base de conception :

- `Mathematiques/manuel-maths/scripts/ingest.py` ;
- `NSI/scripts/ingest.py`.

Leur fonction `classify()` :

- lit `ANTHROPIC_API_KEY` ;
- importe le SDK `anthropic` à la demande ;
- appelle directement un modèle Anthropic ;
- limite déjà le fragment transmis à 3 000 caractères ;
- utilise déjà une heuristique locale lorsque la clé est absente.

Cette duplication est le seul appel LLM direct observé dans le code actif. Il
n'existe aucun client OpenRouter partagé à la racine.

### 2.3 Configuration et documentation durables divergentes

Les dépendances, exemples d'environnement et documents opérationnels citent
encore Anthropic, sa clé ou son Batch API. `httpx>=0.27` est toutefois déjà
présent dans les exigences Mathématiques et NSI et déjà utilisé par les deux
pipelines de collecte. La migration n'exige donc pas un nouveau SDK LLM.

## 3. Objectifs

Le lot d'implémentation devra :

1. établir une seule frontière réseau LLM, testable et partagée ;
2. préserver le mode local sans coût et sans réseau ;
3. faire déléguer les deux ingestions à la même classification ;
4. supprimer les dépendances et configurations Anthropic directes actives ;
5. aligner les quatre autorités actives et les guides opérationnels durables ;
6. empêcher tout retour silencieux à Chutes ou à un fournisseur direct ;
7. garantir des tests CI entièrement hors réseau ;
8. préserver les historiques et la traçabilité existante ;
9. ne modifier aucun contrat métier, contenu scolaire, PDF ou gate de
   publication.

## 4. Périmètre exact

### 4.1 Code partagé à créer

- `scripts/openrouter_client.py` : frontière HTTP OpenRouter, validation du
  protocole et erreurs expurgées ;
- `scripts/openrouter_classification.py` : heuristique locale, construction du
  prompt, interprétation et validation de la classification.

### 4.2 Appelants à migrer

- `Mathematiques/manuel-maths/scripts/ingest.py` ;
- `NSI/scripts/ingest.py`.

Les deux scripts doivent rester des adaptateurs minces et déléguer toute la
logique de classification au module racine. Ils ne doivent contenir ni endpoint
LLM, ni client fournisseur, ni logique de sélection de modèle.

Leurs docstrings et commentaires actifs deviennent eux aussi
fournisseur-neutres ou OpenRouter-only. Le point d'extension vision encore non
implémenté reste hors périmètre fonctionnel : il ne doit plus annoncer un futur
appel direct à Claude et ne reçoit aucune implémentation dans ce lot.

Leur chargement du module partagé doit fonctionner depuis les commandes
existantes `make ingest`. Une résolution déterministe de la racine du dépôt à
partir de `__file__` est admise ; elle ne doit dépendre ni du répertoire courant
ni d'un `PYTHONPATH` fourni manuellement. La même adaptation doit être utilisée
dans les deux fichiers afin de ne pas recréer deux comportements.

### 4.3 Configuration et dépendances actives à migrer

- `Mathematiques/manuel-maths/.env.example` ;
- `NSI/.env.example` ;
- `Mathematiques/manuel-maths/requirements.txt` ;
- `NSI/requirements.txt`.

Pour leur configuration LLM, les exemples d'environnement remplacent la
variable Anthropic par les deux variables suivantes :

```dotenv
OPENROUTER_API_KEY=
OPENROUTER_MODEL=
```

Les autres variables non LLM, notamment la connexion à la base de données,
restent inchangées. Les exemples ne contiennent aucune valeur ressemblant à
une vraie clé. La dépendance `anthropic` est supprimée ; `httpx` existant est
conservé.

### 4.4 Autorités et documentation actives à aligner

Les quatre autorités actives sont obligatoirement mises à jour :

- `AGENTS.md` ;
- `.agents/skills/nexus-manual-quality/SKILL.md` ;
- `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md` ;
- `README.md`.

Les occurrences opérationnelles actives identifiées doivent également être
alignées, sans réécriture éditoriale sans rapport :

- `Mathematiques/PROMPT_MISSION_AUTONOME.md` ;
- `Mathematiques/workflow_production_manuel.md` ;
- `Mathematiques/manuel-maths/README.md` ;
- `Mathematiques/manuel-maths/CAHIER_DES_CHARGES.md` ;
- `Mathematiques/manuel-maths/docs/02_workflow_production.md` ;
- `Mathematiques/manuel-maths/docs/03_architecture_technique.md` ;
- `NSI/CAHIER_DES_CHARGES.md` ;
- `NSI/docs/02_workflow_production.md` ;
- `NSI/docs/03_architecture_technique.md`.

La mise à jour décrit OpenRouter comme passerelle et
`OPENROUTER_MODEL` comme sélection explicite. Elle ne promet ni remise de prix,
ni Batch API, ni modèle par défaut, ni disponibilité permanente d'un modèle.

### 4.5 Tests à créer ou adapter

Les tests racine couvrent le client et la classification partagés. Les tests
des deux manuels prouvent la délégation des scripts d'ingestion et leur
exécution depuis leur contexte habituel.

Le nom exact des fichiers de test sera fixé par le plan d'implémentation, mais
le contrat Red de la section 11 est obligatoire.

## 5. Hors périmètre

Ce lot ne doit pas :

- choisir ou figer dans le dépôt la valeur de production de
  `OPENROUTER_MODEL` ;
- créer un routeur multi-modèles ou une liste de modèles de repli ;
- intégrer un SDK OpenRouter, OpenAI, Anthropic ou Chutes ;
- ajouter streaming, outils, embeddings, vision, cache, Batch API ou gestion de
  coûts ;
- réaliser automatiquement un `GET /api/v1/models` ;
- effectuer un appel réseau dans un test ou dans la CI ;
- modifier la logique d'extraction, de découpage, les schémas de chunks ou le
  contenu des corpus ;
- corriger les P0 Wave 0, les quatre dettes historiques de séparation élève ou
  un autre gate déjà rouge ;
- produire une expertise disciplinaire, une approbation ou une décision de
  publication ;
- déplacer les preuves historiques vers `audit/openrouter/` ;
- réécrire un ancien audit, plan ou spécification pour lui faire refléter la
  politique présente.

## 6. Architecture cible

```text
ingest Mathématiques ─┐
                     ├─> scripts/openrouter_classification.py
ingest NSI ──────────┘       ├─ clé absente ─> heuristique locale
                             └─ clé + modèle
                                    │
                                    v
                         scripts/openrouter_client.py
                                    │
                                    v
                    POST openrouter.ai/api/v1/chat/completions
```

### 6.1 `scripts/openrouter_client.py`

Le module possède une responsabilité unique : transformer une demande de chat
en requête HTTP OpenRouter et retourner le contenu textuel de la première
réponse.

Son interface publique doit permettre l'injection d'un transport `httpx`, afin
que `httpx.MockTransport` remplace intégralement le réseau dans les tests. Les
paramètres métier restent explicites : clé, modèle, messages et limite de
sortie.

Le client :

- utilise une constante interne pour l'URL HTTPS exacte ;
- envoie `Content-Type: application/json` et le Bearer attendu ;
- inclut toujours le champ JSON `model` ;
- effectue une requête non streamée ;
- applique un timeout borné sur toutes les phases HTTP ;
- refuse un modèle vide avant tout appel ;
- exige une réponse HTTP réussie ;
- extrait uniquement `choices[0].message.content` si c'est une chaîne non vide ;
- lève des erreurs applicatives stables et expurgées pour la configuration, le
  transport, le statut HTTP et le protocole de réponse ;
- ne journalise ni en-têtes, ni clé, ni prompt, ni réponse brute ;
- n'effectue aucun nouvel essai implicite dans ce premier lot.

Le timeout recommandé est de 30 secondes au plus par requête. Sa valeur doit
être centralisée et injectable en test, jamais désactivée.

### 6.2 `scripts/openrouter_classification.py`

Le module porte les deux chemins de classification et constitue l'interface
appelée par les ingestions.

Il expose conceptuellement :

- une fonction pure d'heuristique locale ;
- une fonction de classification qui interprète l'environnement et choisit le
  chemin local ou OpenRouter ;
- une fonction pure de décodage et de validation de la sortie du modèle.

Le dictionnaire retourné conserve le contrat actuel. Par exemple, la valeur
conservatrice est :

```json
{
  "chunk_type": "autre",
  "niveau": null,
  "theme": null,
  "capacites": [],
  "difficulte": null
}
```

`chunk_type` accepte les valeurs actuelles `cours`, `methode`, `exercice`,
`corrige`, `activite`, `evaluation`, `erreur_type` et `autre`. `niveau` accepte
`2GT`, `1SPE`, `TSPE`, `TEXP` ou `null`. `theme` est une chaîne ou `null`,
`capacites` une liste et `difficulte` l'entier 1, 2 ou 3, ou `null`. Aucun type
du schéma de chunk n'est modifié.

Le prompt conserve le rôle actuel de classification, la limite de sortie
actuelle de 200 tokens et la consigne de réponse JSON. Seuls les 3 000 premiers
caractères du fragment sont transmis. L'heuristique peut examiner localement le
fragment sans l'envoyer.

Une réponse textuelle entourée d'une clôture Markdown JSON peut être nettoyée
comme aujourd'hui. Un JSON de classification non décodable produit le résultat
conservateur historique `chunk_type: autre` avec les autres valeurs vides ; ce
repli est local et ne déclenche aucun autre fournisseur. En revanche, une
réponse API sans contenu conforme au protocole, une erreur réseau ou un statut
HTTP en échec interrompt l'appel avec une erreur expurgée : le pipeline ne
doit pas basculer silencieusement d'un mode distant commencé vers un mode local.

### 6.3 Matrice de configuration

| `OPENROUTER_API_KEY` | `OPENROUTER_MODEL` | Comportement |
|---|---|---|
| absente ou vide | absente, vide ou renseignée | heuristique locale, zéro réseau |
| présente | absente ou vide | erreur explicite avant tout réseau |
| présente | présente | un POST OpenRouter avec ce modèle exact |

La présence isolée d'un modèle ne doit jamais provoquer un appel. Aucun autre
nom de variable de clé LLM n'est interprété.

## 7. Flux détaillé

Pour chaque chunk :

1. l'ingestion appelle la fonction partagée avec le texte brut ;
2. la fonction lit une vue injectée de l'environnement ;
3. sans clé, elle retourne immédiatement l'heuristique locale ;
4. avec clé, elle exige un modèle non vide ;
5. elle construit le prompt avec au plus 3 000 caractères de contenu ;
6. le client envoie un seul POST avec le modèle exact ;
7. le client valide l'enveloppe OpenRouter et retourne le texte ;
8. la couche classification nettoie, parse et normalise le JSON ;
9. l'ingestion assemble le record existant ;
10. le schéma de chunk existant valide le record avant écriture.

Il n'existe aucune branche vers Chutes, Anthropic direct ou une autre API LLM.

## 8. Erreurs et observabilité

Les erreurs exposées doivent distinguer au minimum :

- configuration incomplète ;
- timeout ou transport indisponible ;
- authentification ou autorisation refusée ;
- limitation de débit ;
- autre statut HTTP ;
- enveloppe de réponse invalide.

Les messages peuvent contenir le type d'erreur, le statut HTTP, l'endpoint
constant et le modèle public configuré. Ils ne doivent jamais contenir :

- la clé ou le header `Authorization` ;
- le fragment source ;
- le prompt complet ;
- le corps brut d'une réponse distante ;
- une donnée personnelle ou un secret présent dans l'environnement.

Le premier lot n'ajoute pas de télémétrie distante. Une sortie locale concise
est admise si elle respecte ces règles.

## 9. Sécurité et protection des données

### 9.1 Frontière réseau fermée

L'URL n'est pas configurable par variable d'environnement dans ce lot. Elle est
fixée en HTTPS sur `openrouter.ai`, ce qui évite d'introduire une destination
arbitraire. Les redirections automatiques ne sont pas nécessaires.

### 9.2 Secrets

- les clés ne sont présentes que dans l'environnement local ou le coffre CI ;
- aucune CI de ce lot n'a besoin d'une vraie clé ;
- `.env.example` contient des valeurs vides ;
- aucune clé ne figure dans Git, les exceptions, snapshots, fixtures ou preuves ;
- les tests utilisent une valeur sentinelle et prouvent son absence des erreurs
  et logs.

### 9.3 Données transmises

- au plus 3 000 caractères du chunk sont envoyés ;
- aucun secret, donnée personnelle ou contenu élève non anonymisé n'est envoyé ;
- le modèle ne reçoit que le strict fragment nécessaire à la classification ;
- aucun fichier, manifeste complet, variable d'environnement ou métadonnée de
  machine n'est joint ;
- la sortie du modèle est une donnée non fiable, bornée, parsée puis validée
  avant toute écriture.

### 9.4 Autorité des résultats

Une réponse OpenRouter reste consultative. Elle ne vaut ni source officielle,
ni validation mathématique, ni conformité programme, ni approbation humaine.
Les sources, tests, builds et validations humaines conservent leur priorité.

## 10. Smoke test et preuves futures

Le `GET https://openrouter.ai/api/v1/models` est autorisé uniquement lors d'un
smoke test humain explicite. Il sert à vérifier qu'une clé locale est valide et
que la valeur choisie de `OPENROUTER_MODEL` apparaît dans le catalogue courant.

Ce smoke test :

- n'est jamais exécuté par Pytest ou la CI ;
- ne choisit pas automatiquement un modèle ;
- ne modifie pas la configuration ;
- n'enregistre ni clé ni réponse brute exhaustive ;
- n'est pas requis lorsque la clé est absente ;
- ne transforme pas l'indisponibilité distante en échec des gates hors réseau.

Les nouvelles consultations ou smoke tests utiles seront consignés sous
`audit/openrouter/` avec, au minimum : date, objectif, modèle explicite, nature
des données envoyées, résultat synthétique, vérification locale et décision de
retenir ou rejeter la recommandation. Les secrets et données personnelles sont
interdits dans ces preuves.

## 11. Contrat TDD

L'implémentation suit strictement Red, Green, puis Refactor.

### 11.1 Red — tests écrits avant la production

Le jalon Red doit échouer pour les raisons attendues et couvrir :

1. l'URL exacte, le POST, le Bearer, le JSON et le modèle explicite ;
2. l'injection d'un `httpx.MockTransport` sans accès réseau ;
3. la matrice complète des variables d'environnement ;
4. l'absence totale de requête lorsque la clé est absente ;
5. l'erreur avant requête lorsque la clé existe sans modèle ;
6. le timeout borné ;
7. l'extraction d'une réponse OpenRouter valide ;
8. les erreurs expurgées pour timeout, 401/403, 429, 5xx et protocole invalide ;
9. l'absence de la clé sentinelle dans exceptions et logs ;
10. la limite de 3 000 caractères transmis ;
11. la conservation de l'heuristique locale ;
12. le résultat conservateur sur JSON de classification non décodable ;
13. la délégation des deux ingestions au module racine ;
14. l'absence d'import ou dépendance `anthropic` dans le code actif ;
15. l'absence de `ANTHROPIC_API_KEY` dans la configuration active ;
16. l'absence d'instruction active appelant Chutes dans les quatre autorités ;
17. l'absence d'appel à `/api/v1/models` dans les tests et workflows CI ;
18. l'exécution des deux scripts depuis leurs commandes et répertoires prévus.

Les scans de politique utilisent une liste explicite de surfaces actives et
une liste d'exclusions historiques. Ils ne doivent pas échouer sur une preuve
ancienne qui mentionne fidèlement Chutes ou Anthropic.

### 11.2 Green — minimum de production

Le jalon Green ajoute uniquement :

- le client HTTP partagé ;
- la classification partagée ;
- les deux délégations d'ingestion ;
- la configuration et les dépendances minimales ;
- l'alignement documentaire actif ;
- les tests nécessaires pour rendre le contrat Red vert.

Aucun élargissement fonctionnel n'est admis pour obtenir Green.

### 11.3 Refactor

Après Green seulement, les doublons de prompt ou d'heuristique encore présents
peuvent être retirés. Le refactor doit conserver les mêmes tests, le même schéma
de chunk et l'absence de réseau en CI.

## 12. Gates d'acceptation

Le lot OpenRouter est acceptable lorsque :

- tous les tests ciblés sont verts avec `MockTransport` ;
- les tests prouvent qu'aucune requête réelle n'a lieu ;
- Ruff et les contrôles Python affectés sont verts ;
- les deux commandes d'ingestion chargent le module partagé dans leur contexte
  normal ;
- `anthropic` a disparu des requirements actifs et des imports de production ;
- aucune configuration active ne lit `ANTHROPIC_API_KEY` ;
- les quatre autorités prescrivent OpenRouter et n'ordonnent plus Chutes ;
- les documents opérationnels actifs ne recommandent plus un appel fournisseur
  direct ;
- les fichiers modifiés respectent l'allowlist du lot ;
- `git diff --check` est vert ;
- les répertoires `audit/chutes/**`, les audits existants et les anciens
  plans/spécifications sont inchangés ;
- `--release-strict` reste rouge pour les dettes éditoriales réelles et n'est
  ni affaibli ni requalifié.

Le smoke test humain OpenRouter est une preuve externe séparée. Son absence ne
rend pas rouges les tests hors réseau ; sa réussite ne rend pas le manuel
publiable.

## 13. Commits atomiques attendus pour l'implémentation

L'ordre recommandé est :

1. `[TESTS] verrouille la passerelle OpenRouter` — contrat Red uniquement ;
2. `[PYTHON] centralise les appels LLM via OpenRouter` — client,
   classification, ingestions, dépendances et exemples d'environnement ;
3. `[DOCS] aligne les autorites sur OpenRouter` — autorités et documentation
   opérationnelle actives ;
4. `[AUDIT] consigne le smoke OpenRouter` — uniquement si un smoke humain a
   réellement été exécuté et vérifié.

Une correction issue de revue reçoit un commit supplémentaire ciblé. Aucun
commit ne mélange cette migration avec une correction mathématique, un
changement de baseline visuelle, une migration de corpus ou un P0 Wave 0.

## 14. Préservation des historiques

Les chemins suivants sont des preuves ou décisions historiques et restent
immuables dans ce lot :

- `audit/chutes/**` ;
- les autres audits existants mentionnant Chutes ou OpenRouter ;
- les manifests de revues visuelles existants ;
- `docs/codex/**` lorsqu'il décrit un état contrôlé antérieur ;
- les anciens fichiers sous `docs/superpowers/plans/` ;
- les anciennes spécifications sous `docs/superpowers/specs/`.

Leur vocabulaire historique n'est pas une instruction active. Toute preuve
nouvelle utilise `audit/openrouter/`. Cette séparation empêche de falsifier
l'état observé à une date antérieure.

## 15. Interaction avec Wave 0

Les trois plans Green P0 approuvés — provenance programme TSPE, séparation
élève/professeur et préflight des débordements — sont indépendants du
fournisseur externe. Ils continuent à s'exécuter hors réseau et ne doivent pas
être modifiés par ce lot.

En particulier :

- la correction Programme reste un lot autonome ;
- la tâche 2 Séparation reste bloquée séparément sur quatre dettes historiques
  déjà observées sur sa base propre ;
- le lot Overflow reste empilé selon son plan approuvé ;
- aucun test Wave 0 n'est supprimé, ignoré, transformé en `skip`/`xfail` ou
  requalifié pour faciliter OpenRouter ;
- aucune consultation Chutes n'est effectuée pendant Wave 0 ;
- OpenRouter n'est pas requis pour poursuivre les travaux déterministes locaux.

La branche d'implémentation OpenRouter doit donc rester distincte des branches
Green P0 jusqu'à une décision humaine d'intégration. La migration du
fournisseur ne vaut correction d'aucun P0 et ne change pas le **NO-GO**.

## 16. Critères de réussite de la décision

La décision « OpenRouter-only » est effectivement réalisée seulement si les
quatre propriétés suivantes sont simultanément prouvées :

1. **unicité réseau** — chaque appel LLM actif atteint uniquement l'endpoint
   OpenRouter fixé ;
2. **unicité logique** — les deux ingestions utilisent la même classification
   partagée ;
3. **mode local réel** — sans clé, les mêmes entrées sont classées sans aucun
   réseau ;
4. **traçabilité honnête** — les autorités actives sont à jour et les preuves
   historiques restent intactes.

Tant que l'un de ces critères manque, le dépôt ne peut pas déclarer
l'exclusivité OpenRouter comme implémentée.
