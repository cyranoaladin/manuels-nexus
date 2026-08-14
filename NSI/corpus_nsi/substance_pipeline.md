# Pipeline de substance

## Doctrine

System A est l'autorité mécanique. `scripts/check_substance_anchors.py` valide le
schéma, les fichiers, les ancres et les citations, puis applique son veto. Il ne
promeut jamais un verdict.

System B est un proposeur. `scripts/substance_judge.py` peut proposer
`needs_content` ou `needs_review`, au format `substance_verdict.schema.json`, avec
trois preuves structurées (`file`, `anchor`, `quote`). Il ne peut jamais produire
un statut `validated_pedagogy`.

`scripts/run_substance_judge.py` reste un pré-jugement déterministe hors réseau
et n'importe pas le client externe.

## Transports et configuration

La recherche de candidats utilise exclusivement `RAG_API_BASE_URL`, son Bearer
RAG et les barrières de collection. Elle reste distincte du jugement LLM.
OpenRouter est l'unique passerelle LLM externe ; seul le client partagé
`nexus_external/openrouter_client.py` porte l'endpoint fixe
`https://openrouter.ai/api/v1/chat/completions`.

Les deux paramètres LLM sont `OPENROUTER_API_KEY` et `OPENROUTER_MODEL`, lus
depuis l'environnement puis, pour les valeurs absentes, depuis `.env.rag`. Aucun
modèle n'est implicite. Sans clé, `substance_judge.py` n'effectue aucun appel
LLM et conserve son résultat conservateur ; sa recherche RAG peut néanmoins
utiliser `RAG_API_BASE_URL` lorsqu'elle est configurée. Une clé présente sans
modèle provoque une erreur avant réseau LLM, sans repli fournisseur. La
campagne distante exige les deux valeurs.

Aucun secret ni donnée personnelle ne doit être transmis. Tout extrait est
autorisé et anonymisé si nécessaire avant l'appel ; toute réponse est validée
localement et reste soumise à une revue humaine.

## Journal comptable de campagne

`substance_reviews/campaign/_usage_log.json` conserve les objets historiques de
schéma v1, avec leurs champs, valeurs et ordre relatif inchangés. Ils ne sont ni
convertis ni recalculés.

Chaque complétion OpenRouter réussie ajoute une entrée v2 distincte contenant
`schema_version: 2`, `provider: openrouter`, la capacité, la séquence, la
tentative et la date, puis le modèle, le `generation_id`, les compteurs de
tokens/cache et `cost_usd` copiés exactement depuis la réponse validée. Un même
`generation_id` est remplacé sans doublon ; les autres générations et toutes
les entrées v1 sont préservées. Une entrée d'échec n'invente ni identifiant de
génération, ni tokens, ni coût. Les totaux du run somment uniquement ses entrées
v2 réussies. L'écriture relit et fusionne le journal sous verrou, puis le
remplace atomiquement afin de préserver les écritures concurrentes.

Une promotion pédagogique exige en plus une confirmation humaine conforme à
`reviewer_confirmation.schema.json`, dont le hash correspond au verdict A.
Ni une réponse OpenRouter, ni une entrée comptable v2, ni un gate mécanique ne
peut promouvoir `covered`, `published` ou un statut `validated_*`.

## Matching des citations

Une preuve proposée par B est acceptée seulement si A retrouve la citation dans
la section ancrée. La comparaison conserve la casse et tolère uniquement les
variations d'espaces.

## Publication

Tant qu'aucune confirmation humaine n'est tracée, les compteurs publiables restent
à zéro : `covered = 0`, `validated_* = 0`, `published = 0`.
