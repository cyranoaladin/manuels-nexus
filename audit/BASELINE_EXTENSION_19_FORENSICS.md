# Forensics — extension conditionnelle de baseline 19

## Verdict

`PRECONDITIONS_FAILED_NO_MATERIALIZATION`.

La baseline `audit/ANOMALIES_BASELINE.json`, sa politique et son historique
n'ont pas été modifiés. Le lot observé à `b8840aa5` contenait bien dix-neuf
empreintes signalées par `fail-on-new`, mais l'une d'elles,
`0fba13a5fd65d5f3`, appartenait à `invalid_statuses`.

Le contrat `TNSI-PROJET` utilisait `needs_review`, valeur inconnue pour un
contrat. La correction déterministe vers l'état canonique non approuvé
`draft` a fermé `0fba13a5fd65d5f3` et `cb731c9234414174`, puis créé la seule
dette de contrat valide `bd63d2a316c26b0c`.

Après recalcul, le jeu normalisé `NEW` contient donc dix-huit empreintes, pas
dix-neuf.

## Trois remplacements proposés

Les trois paires proposées ne satisfont pas le contrat de migration mécanique.
Dans chaque cas, la même source physique a changé d'identité et de rôle
programme : une ancienne capacité obligatoire est devenue une extension
facultative explicitement étiquetée « Vers la Terminale ». Les corps ont aussi
été modifiés. Elles sont donc classées `SUBSTANTIVE_CHANGE`, avec :

- `2766a51faf11b384` résolu et `2e189d4bed9a9520` nouvelle dette ;
- `6d992d972010d877` résolu et `265dbdeec1fc2b62` nouvelle dette ;
- `94c720f2a573ff30` résolu et `e79a0d7257787b02` nouvelle dette.

`MIGRATED_NEW = 0` et `TRUE_NEW = 18` après la correction obligatoire du
contrat TNSI.

## Algèbre d'ensembles recalculée

- baseline active : `6541` ;
- état actif courant : `2237` ;
- différence brute courante hors baseline : `116` ;
- dette déjà gouvernée `EXPECTED_REVIEW_DEBT` : `89` ;
- migrations historiques déjà approuvées : `9` ;
- `NEW` normalisé restant : `18` ;
- résolutions hors paires déjà approuvées : `4411` ;
- inchangés : `2121` ;
- delta actif global : `-4304`.

Le mécanisme canonique d'update remplacerait `baseline.active` par l'état
courant et archiverait les `4411` résolutions. Cette opération excède très
largement l'autorisation conditionnelle `16 + 3` et ne peut pas être
matérialisée sous cette décision.

## Garde-fous

- aucune wildcard ;
- aucune baseline update ;
- aucune qualification `approved` ;
- aucune réduction de sévérité ;
- `release_acceptance` reste `false` ;
- aucun oracle D7 modifié.

Le registre JSON compagnon contient les dix-neuf lignes du candidat initial,
les comparaisons des trois paires et l'état recalculé après correction.
