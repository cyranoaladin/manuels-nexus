# TNSI — adaptation aménagée et accroche contractuelle

Lot D2 du 8 septembre 2026, préparé par Codex `review_forensics`, avec les sources D1 désormais committées sous `246a8afd0`. Portée : `WORKTREE_BOUND_BY_INPUT_DIGESTS`. Les deux sources modifiées et les quatre sources parentes de l'adaptation ont été lues entièrement. La contre-revue indépendante des corrections reste à effectuer ; aucune approbation humaine n'est créée.

## Adaptation et résolution indépendante

Le META de `TNSI-HIST-AM-EXTRAIT` déclare `derive_de` EX001 et EX002. Son premier exercice proposait pourtant 1936, 1971 et 1989, alors que le parent EX001 et son corrigé portent 1936, 1948 et 1969. Les anciens événements n'étaient pas tous faux, mais la relation de dérivation était inexacte : un simple allègement ne justifiait pas leur substitution. L'adaptation retrouve les trois événements du parent courant.

L'association correcte est : article de Turing → B, 1936 ; premier programme du Manchester Baby → A, 1948 ; mise en service d'ARPANET → C, 1969. La réponse B reste fournie comme amorce. L'ordre demandé est 1936 < 1948 < 1969 ; l'événement le plus ancien est l'article de Turing. Le [texte de Turing, paragraphe 6](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf), la [source Manchester](https://curation.cs.manchester.ac.uk/computer50/www.computer50.org/mark1/new.baby.html) et la [source DARPA](https://www.darpa.mil/news/features/arpanet) justifient séparément ces repères. Leur véracité ne découle pas du test de correspondance avec le parent.

L'ancien second exercice associait la polyvalence d'un smartphone au principe du programme enregistré puis enchaînait sur l'universalité, sans distinguer illustration et argument général. Il omettait aussi les rôles des couches et la contrainte demandés dans le parent courant. L'adaptation conserve maintenant des tâches brèves et fermées, chacune avec une seule action :

1. Processeur et écran : matériel ; messagerie et système d'exploitation : logiciel. Le processeur est l'amorce fournie.
2. Dans la situation annoncée, le programme utilisé change. Aucun processeur n'est remplacé. Cela décrit la situation, sans prouver une propriété universelle de toute machine.
3. Le mot attendu est « programmables ». Le Mark I, [livré en 1944](https://chsi.harvard.edu/harvard-ibm-mark-1-about), exécutait des [instructions sur bande pour plusieurs calculs](https://chsi.harvard.edu/harvard-ibm-mark-1-function). Le fait ancien est fourni pour alléger la recherche documentaire ; l'élève en tire une conclusion bornée.
4. Système d'exploitation → B, ressources et services ; compilateur → A, traduction. Les [sections 3.5 et 5 du texte de Ritchie et Thompson](https://www.nokia.com/bell-labs/about/dennis-m-ritchie/cacm.html) et [l'histoire de Fortran par IBM](https://www.ibm.com/history/fortran) soutiennent les deux rôles. Le parent laisse choisir deux couches parmi quatre ; l'adaptation sélectionne deux possibilités recevables et ferme le format de réponse.
5. Des ressources suffisantes et des interfaces compatibles restent nécessaires. L'autre proposition nie toute contrainte et est fausse. Cette exigence est celle du parent corrigé, dont le raisonnement et les limites ont été relus au lot D1.

Les cinq étapes ne constituent pas un quota. Elles rétablissent les composantes concrètes perdues dans la dérivation : changement de programme, exemple ancien, rôles des logiciels et contrainte. Le classement initial aide à identifier les objets avant ces tâches. La recherche d'exemples et la rédaction ouverte du parent deviennent une information fournie et des choix fermés, conformément aux aménagements déclarés. Il n'est pas affirmé que l'élève réalise exactement le même degré d'autonomie que dans EX002.

## Accroche : portée réelle et correction

L'accroche affirmait une place centrale du logiciel que le matériel seul ne pouvait offrir aux débuts. Cette présentation réintroduisait l'opposition historiquement trompeuse corrigée dans les objets. Elle est remplacée par une invitation à situer les repères documentés et à comparer programmes, couches logicielles et contraintes matérielles. La référence à Turing en 1936 reste documentée. Le contrat conserve ses capacités, prérequis, temps et statut historique ; un commentaire explicite indique que la correction d'accroche n'a reçu aucune nouvelle approbation humaine.

La portée a été vérifiée dans les producteurs, sans déduire l'absence d'usage d'un seul grep : `NSI/scripts/assemble_manuel.py` construit son contexte depuis le manifeste et les fichiers TeX, puis appelle `NSI/scripts/assemble.py::render_book_master_from_files`. Cette fonction écrit le titre du manifeste, un label et les entrées TeX ; elle ne charge pas `situation_accroche`. Les deux assembleurs mathématiques qui l'utilisent concernent leur propre corpus. `build_human_review_reading_views.py` lit ce champ mais utilise exclusivement les chapitres et packets 1SPE. Aucune impression actuelle de cette accroche NSI n'est donc établie par ces chemins canoniques. Le contrat demeure néanmoins une source dépendante des revues : son changement invalide les liaisons concernées et ne doit pas être ignoré sous prétexte que l'accroche n'est pas assemblée.

## Régression, dépendances et limites

Quatre tests concernent l'adaptation. Ils comparent le jeu de repères proposé à celui du corrigé parent, vérifient la résolution unique des identifiants parents et confirment l'absence de crédit d'exécution pour la prose. Deux tests ont échoué avant correction à cause des jeux de repères différents, deux ont réussi. Après correction : **4 PASS en 0,10 s**. Une mutation temporaire change un repère dans les choix et fait échouer la comparaison. Ce test ne prouve ni la date d'un événement ni sa bonne association à une lettre ; ces points sont lus et résolus ci-dessus.

```text
python -m pytest NSI/tests/test_tnsi_history_adapted_bindings.py -q
python -m ruff check NSI/tests/test_tnsi_history_adapted_bindings.py --select F,E9
git diff --check
```

Ruff et le contrôle des blancs réussissent. Aucun oracle factice, skip ou xfail n'est ajouté. Aucun autre corpus n'est exécuté et aucun receipt n'est réécrit. Le journal RED de développement est `/tmp/tnsi-history-d2-red.log` ; les tests n'en dépendent pas.

Le changement de `contrat.yaml` survient après la vérification des quinze digests du lot D1. La note D1 conserve sa valeur d'observation antérieure et ne devient pas silencieusement courante sur cette nouvelle dépendance. La présente note contient les digests courants des parents et du contrat pour permettre une contre-revue de ce delta avant toute inscription dans le ledger courant. La signature historique du contrat ne s'étend pas à ce texte corrigé par écriture d'agent.

Ce lot ne certifie pas la qualité globale du chapitre ni son rendu. Les tableaux, espacements, pages et variantes PDF restent à inspecter selon le workflow final. Les statuts `generated` et les gates humains ne sont pas levés. La contre-revue indépendante du contenu actuel et la liaison de toutes ses dépendances restent des étapes distinctes.

## Empreintes relues

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/amenagee/TNSI-HIST-AM-EXTRAIT.tex` : `5424a96969a5e6b621c657e73bb378529bb29594e9b53ef756257b3d1d029504`

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/contrat.yaml` : `9cdb38486e36c3efeb9bce64076a125743212b31d6539fb9c740294b37cd99d7`

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/exercices/TNSI-HIST-EX-001.tex` : `1856c7480e8d256d1b9102ead714972742ef5de5d99230120098f6f8c6dd4495`

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/corriges/TNSI-HIST-CO-001.tex` : `6cdd710decce1c9ca6d89d3592f9f03e8c78398c8123df740571733da4fa20a8`

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/exercices/TNSI-HIST-EX-002.tex` : `9eb8b6d78a667307a3e857fe398022a552c6ec7375c9c898cf547fc25b69f872`

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/corriges/TNSI-HIST-CO-002.tex` : `73c83f831d574f1fb7f52956f3773381fd22ca504d2369b90f6ca36c9077f06e`

- `NSI/tests/test_tnsi_history_adapted_bindings.py` : `f185f9b207b7a06deff0511af8bae57c483e8036aeedcbf01a2813880342b858`

- `NSI/scripts/assemble_manuel.py` : `240ab4a124e79efbbe315dd17a829f5cfaaec4a3e40abcab3315d2f2df19b9cd`

- `NSI/scripts/assemble.py` : `11abfe4ced9d51a69e110be3051c820fcee4d6c1c3581553c297dec74b40cbac`

- `scripts/build_human_review_reading_views.py` : `9e1c63da88cd4a0a2ed48e891bb435b80c41c35cf2acb992d2d739d07c0bdb3e`

- `NSI/scripts/verify_python.py` : `66ef29b688bc64c81122db9604382d92fef741092ada14441855f1a0d2591675`

- `NSI/scripts/execution_protocol.py` : `71c6ee70eb91f1869c17b4087f35da75018a7e848e1038ec338a5c99810f95e5`

- `NSI/sources/txt/BO2019_NSI_terminale.txt` : `3cfce30c85fdc7ab78eb9acb39e43bcb33d6205e0c4205d4cb499f80c097f15b`

- `audit/official_program_coverage/TNSI.json` : `95608c6e9cbd5b42077d3d2a7056fe58e24c03c4d7ea57930f06dc3410b24b34`

## Contre-revue indépendante du lot D2

Codex `/root`, sur HEAD `b5631c9ec` avec les quatorze empreintes de travail ci-dessus, a relu l'intégralité de l'adaptation, le delta et le texte du contrat, les quatre tests et les quatre sources parentes lues au lot D1. Les trois événements et leurs associations ont été résolus indépendamment : Turing B/1936, Baby A/1948, ARPANET C/1969, puis ordre croissant et Turing le plus ancien. Les documents primaires pertinents ont déjà été lus lors des lots A, B et D1 ; aucune vérité historique n'est déduite de l'égalité des jeux de dates.

Pour le second exercice, les catégories sont matériel/logiciel/matériel/logiciel ; seul le programme change dans la situation donnée ; le Mark I permet de retenir « programmables ». Le système d'exploitation correspond au rôle B, le compilateur au rôle A. L'exécution conserve les exigences de ressources et de compatibilité. Le guidage réduit effectivement la tâche de recherche et de rédaction, sans prétendre établir la même autonomie que le parent. Les réponses fournies sont des amorces explicites. La nouvelle accroche propose cette comparaison sans réintroduire de causalité historique non démontrée.

Les **4 tests passent**, sans échec ni skip, en 0,11 s ; les quatorze digests ont été comparés aux sources. La mutation de l'année détecte une divergence entre adaptation et parent, mais ne détecterait pas à elle seule une permutation erronée des associations ; cette dimension a été lue ci-dessus. Le statut humain historique du contrat n'approuve pas l'accroche corrigée.

Verdict : `VALIDATED_BY_EVIDENCE` pour les corrections scientifiques, documentaires, pédagogiques et éditoriales décrites, sans approbation humaine. La relecture du delta d'accroche permet de le comprendre dans le contexte D1 ; elle ne réassocie automatiquement ni les autres preuves de chapitre ni leur ancien digest de dépendances. Cette étape doit être enregistrée explicitement lors de la reconstruction de la vue courante. Aucun PDF, rendu ou contrôle complet de publication n'est certifié ici.

JUnit local : `/tmp/nexus-root-tnsi-history-d2.xml`, SHA256 `23e2986f8a107c9912c6055d365e7a1318a2227e8a23bbbb874edd7e8f7d6b94`.
