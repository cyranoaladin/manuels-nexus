# Correction C3 et gouvernance BUILD_MANIFEST

## Perimetre

Cette passe reste strictement limitee a 1NSI. Elle corrige le P0
`1NSI-REV-AGT-C3-CAS-LIMITE-TERMINAISON`, puis restaure une gouvernance
coherente du manifeste de build et des 349 qualifications 1NSI. Aucune source,
aucun statut et aucun livrable TNSI ne doit etre modifie.

Le SHA initial immuable de la passe est
`5fa8946872e3263049be1b3c0cdf78203596e581`. Le controle final exige qu'aucun
chemin TNSI suivi ou non suivi n'ait change depuis ce SHA. Les surfaces
protegees sont `NSI/chapitres/TNSI-*`, `NSI/referentiel/capacites_TNSI_*`,
`NSI/docs/11_perimetre_terminale.md`,
`NSI/sources/txt/BO2019_NSI_terminale.txt` et tout eventuel
`NSI/build/MANUEL_TNSI*`. Cette preuve s'ajoute au fingerprint TNSI de la policy
et ne depend donc pas du futur SHA de base de gouvernance.

Le refus de publication demeure contractuel : la remise au vert de la portee
de revue ne vaut ni publication, ni validation globale du manuel.

## Probleme C3

La preuve du tri par selection conclut a partir d'une derniere iteration
`i=n-2`. Cette iteration n'existe pas lorsque `n <= 1`, alors que le code traite
correctement ces deux cas. La preuve doit donc distinguer explicitement :

- `n <= 1`, tableau deja trie et boucle externe non executee ;
- `n >= 2`, derniere iteration `i=n-2`, puis application de l'invariant.

La propriete de terminaison doit aussi quantifier exactement la boucle externe
par `max(n-1, 0)` iterations. La correction reste textuelle et minimale ;
l'algorithme Python ne change pas.

## Strategie de correction

Un test de regression lit la source LaTeX publiee et exige les deux cas, la
borne exacte et la conclusion conditionnelle. Il est execute avant la
correction pour obtenir un echec cible, puis apres la correction avec les tests
algorithmiques et les controles des 40 objets du lot.

La correction disciplinaire et sa preuve sont commitees ensemble. Un relecteur
independant, distinct de l'integrateur et des relecteurs precedents, reexamine
ensuite les 40 objets algorithmiques, les preuves et les executions. Son recu
est scelle dans un commit d'audit separe. Les findings et sorties derivees sont
resynchronises dans un troisieme commit. En l'absence de nouvelle anomalie, les
totaux attendus deviennent 260 anomalies : 141 P0, 116 P1 et 3 P2.

## Dette BUILD_MANIFEST

Le manifeste de build a ete invalide apres les modifications de sources. Son
hash courant ne correspond plus au hash epingle dans
`audit/1NSI_CONTENT_REVIEW_POLICY.yaml`, ce qui rend `--verify-scope` rouge.
Modifier uniquement ce hash est insuffisant : le digest du protocole change,
donc chaque `dependency_digest` et chacun des six recus deviennent obsoletes.

La migration doit partir d'un nouveau `implementation_base_sha` propre. Ce SHA
est pris apres la cloture complete de C3, y compris sa documentation, ses
preuves de revue et son inventaire. Ainsi, toutes les modifications anterieures
sont absorbees dans la nouvelle base et seules les surfaces explicitement
autorisees changent pendant la migration.

## Migration de gouvernance

La policy est migree atomiquement avec :

- le nouveau `implementation_base_sha` ;
- le SHA-256 courant de `audit/BUILD_MANIFEST.json` ;
- le nouveau `protocol_digest` calcule par l'outil canonique ;
- les constantes et tests de portee correspondants.

Les sept PDF canoniques restent epingles a leurs octets courants, meme si le
manifeste invalide ne les atteste plus comme builds courants. Le fingerprint
TNSI reste inchange et sert uniquement de garde contre une modification hors
perimetre.

Le changement de protocole invalide necessairement les six recus. Une migration
mecanique qui conserverait les anciennes identites tout en reecrivant les
enveloppes est interdite. Six relecteurs independants reattestent les lots
`contracts`, `algorithms`, `systems-web`, `language-project`,
`data-basics-tables` et `types-construits` sur les sources courantes. Chaque
relecteur fournit une nouvelle identite, un nouveau `review_run_id`, verifie les
faits et ancres de son lot et relance les controles executables applicables.

Les six recus sont ensuite scelles ensemble, car ils attestent un protocole
unique. Un commit suivant reconstruit la provenance et les payloads des 349
findings depuis ces blobs scelles, puis regenere le JSON et la synthese.

Les six `reviewer_id` doivent etre deux a deux distincts, differents de
l'integrateur et absents des six recus anterieurs. Les six `review_run_id`
doivent egalement etre deux a deux distincts et nouveaux. Ces contraintes sont
verifiees par un test canonique avant scellement.

## Transitions rouges bornees

La migration comporte deux etats rouges temporaires, chacun ferme par le commit
suivant :

1. apres le commit de policy, les six recus doivent echouer uniquement sur le
   nouveau protocole ou les digests de dependances associes ; la portee, le
   manifeste, les PDF et TNSI doivent deja etre coherents ;
2. apres le scellement des six recus, les findings doivent echouer uniquement
   sur leur ancienne provenance ou leurs anciens payloads ; les recus eux-memes
   doivent etre valides et scelles.

Un test de transition execute apres chaque commit enumere les erreurs attendues
et interdit toute erreur supplementaire. Le commit d'integration des 349
findings ferme la seconde transition et doit remettre toute la suite de revue
au vert.

## Invariants et tests

La migration est acceptee seulement si :

- les six recus respectent le schema ferme et couvrent exactement 349 sources ;
- chaque recu porte le protocole et les digests de dependances courants ;
- les six reviewers sont deux a deux distincts, differents de l'integrateur et
  des anciens reviewers, avec six runs deux a deux distincts et nouveaux ;
- chaque finding reproduit exactement le payload de son recu scelle ;
- les commits et hashes de scellement sont verifies par `git show` ;
- `review_1nsi_content.py --verify-scope` retourne 0 ;
- `pytest -q NSI/tests/test_1nsi_content_reviews.py`,
  `cd NSI && pytest -q tests` et `pytest -q tests/test_inventory_collection.py`
  retournent 0 ;
- `inventory_collection.py --check`, `--validate-model` et `--fail-on-new`
  retournent 0 ;
- `inventory_collection.py --release-strict` reste rouge pour les blocages
  reels restants avec le code 7, sans erreur d'inventaire ;
- `git diff --quiet 5fa8946872e3263049be1b3c0cdf78203596e581 --`
  sur les cinq surfaces TNSI protegees retourne 0 ;
- `git status --porcelain --` sur ces memes surfaces ne retourne aucune ligne,
  ce qui couvre aussi les fichiers non suivis, puis le controle final exige un
  worktree entierement propre.

## Atomicite

Les commits restent separes par responsabilite : documentation, regression et
correction C3, recu de revue C3, registre C3, inventaire eventuel, policy de
gouvernance, six recus migres, registre des 349 qualifications, inventaire
eventuel. Aucun commit ne melange correction disciplinaire et migration de
gouvernance.
