# Pipeline de substance

## Doctrine

System A est l'autorité mécanique. `scripts/check_substance_anchors.py` valide le
schéma, les fichiers, les ancres et les citations, puis applique son veto. Il ne
promeut jamais un verdict.

System B est un proposeur. `scripts/substance_judge.py` peut proposer
`needs_content` ou `needs_review`, au format `substance_verdict.schema.json`, avec
trois preuves structurées (`file`, `anchor`, `quote`). Il ne peut jamais produire
un statut `validated_pedagogy`.

Une promotion pédagogique exige en plus une confirmation humaine conforme à
`reviewer_confirmation.schema.json`, dont le hash correspond au verdict A.

## Matching des citations

Une preuve proposée par B est acceptée seulement si A retrouve la citation dans
la section ancrée. La comparaison conserve la casse et tolère uniquement les
variations d'espaces.

## Publication

Tant qu'aucune confirmation humaine n'est tracée, les compteurs publiables restent
à zéro : `covered = 0`, `validated_* = 0`, `published = 0`.
