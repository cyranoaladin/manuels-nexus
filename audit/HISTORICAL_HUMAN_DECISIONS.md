# Décisions humaines historiques

Ces décisions ont réellement eu lieu et sont conservées. Elles n'autorisent plus aucune release courante.

- `HISTORICAL_RECEIPT_CAN_AUTHORIZE_CURRENT_RELEASE` : `False`

## HHD-2026-09-06-001

- Relecteur : `abenrhouma`
- Décision d'origine : `ACCEPT_FROZEN_RELEASE_CONTENT` (`APPROVED`)
- Statut courant : `HISTORICAL_HUMAN_DECISION`
- Raison de non-applicabilité : `NON_AUTHORITATIVE_FOR_CURRENT_RELEASE_DUE_TO_INVALID_CONTENT_BINDING_AND_POST_ACCEPTANCE_CONTENT_MUTATION`
- HEAD accepté : `2e51a9be56ee704da1389876611c55b1dac76e2c`
- Empreinte alors déclarée : `sha256:9b3ccf9a81c5520fbb7e03b7b2d3e7bf2057a02834b6d908bf3be5f49f3b553f`

### Erreur de conception de l'empreinte

L'empreinte agrégeait neuf artefacts de audit/, dont BLOCKER_TAXONOMY.json qui bascule OPEN -> RESOLVED dès que le reçu existe. Une preuve ne peut pas dépendre de la décision qu'elle authentifie. De plus l'empreinte ne couvrait aucun octet de contenu pédagogique malgré son nom.

Cycle constaté : RECEIPT -> BLOCKER_TAXONOMY.json → BLOCKER_TAXONOMY.json -> CONTENT_SOURCE_CLOSURE_DIGEST → CONTENT_SOURCE_CLOSURE_DIGEST -> RECEIPT

### Mutation pédagogique postérieure

- Objet : `NSI/chapitres/TNSI-PROJET/projet/TNSI-PROJET-ANNUEL.tex`
- Commit : `e76064c5` — [STATUS] apply digest-bound publication maturity transitions

Ajout d'un bloc \remarque{} de 10 lignes sur le périmètre d'exigibilité, dans un commit dont le contrat était limité à la maturité.
