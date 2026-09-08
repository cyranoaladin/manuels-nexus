# TNSI — exercices et évaluation A, revue documentaire résiduelle

Lot D1 du 8 septembre 2026, après le lot C `cb7213745`, préparé par Codex `review_forensics`. Portée : `WORKTREE_BOUND_BY_INPUT_DIGESTS`, avec les empreintes ci-dessous. Les six sources ont été lues entièrement : deux énoncés, leurs deux corrigés, l'évaluation A et son corrigé. La contre-revue indépendante des corrections reste nécessaire. Cette note n'est ni une approbation humaine ni une clôture du chapitre.

## Corrections et preuves documentaires

Les formulations indéterminées « premiers ordinateurs à programme enregistré » deviennent un repère précis : l'exécution du premier programme du Manchester Baby en 1948. La [source conservée par Manchester](https://curation.cs.manchester.ac.uk/computer50/www.computer50.org/mark1/new.baby.html) précise le 21 juin et la nature électronique à programme enregistré. Le corrigé explique que ce repère ne fait pas disparaître les machines programmables antérieures. Le [texte de Turing, paragraphe 6](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf) soutient le repère de 1936 ; la [rétrospective institutionnelle DARPA](https://www.darpa.mil/news/features/arpanet) situe les premiers nœuds d'ARPANET en 1969. Les réponses donnent donc l'ordre 1936, 1948, 1969. Elles répondent aux trois événements effectivement demandés, sans faire passer une comparaison de constantes Python pour une preuve historique.

Dans EX002, l'affirmation non bornée sur des milliers d'applications est remplacée par une situation de deux applications compatibles sur la même machine. Le corrigé distingue l'illustration d'une polyvalence et une conclusion sur l'histoire entière. Il utilise le Mark I, [livré en 1944](https://chsi.harvard.edu/harvard-ibm-mark-1-about), dont Harvard décrit la [commande par instructions sur bande et différents usages](https://chsi.harvard.edu/harvard-ibm-mark-1-function). Le matériel n'était donc pas uniformément monotâche avant le smartphone. Les accents et l'erreur grammaticale « le logiciel […] déterminé » sont corrigés.

Le choix de deux couches parmi les quatre proposées est conservé ; le corrigé donne désormais les quatre possibilités, afin qu'un élève ayant choisi machine virtuelle ou compilateur dispose aussi d'une réponse. Les rôles sont bornés :

- Le système d'exploitation gère des ressources et des services communs. Le [texte de Ritchie et Thompson, sections 3.5 et 5](https://www.nokia.com/bell-labs/about/dennis-m-ritchie/cacm.html) décrit protection, processus et partage. Le système ne supprime pas la compatibilité ni le besoin de mémoire.
- La machine virtuelle d'exécution est illustrée par la JVM. L'[introduction du chapitre 2 et la section 2.1 de la spécification Oracle](https://docs.oracle.com/javase/specs/jvms/se25/html/jvms-2.html) distinguent une machine abstraite, ses réalisations et le format intermédiaire indépendant du matériel. Le corrigé ne confond pas toute machine virtuelle avec une machine universelle de Turing.
- Le navigateur traite l'interface HTML/CSS et peut exécuter JavaScript. La [documentation MDN de Mozilla, définition des trois langages et exécution dans le navigateur](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/What_is_JavaScript) soutient cette distinction. HTML et CSS ne sont pas présentés comme du code JavaScript, et la compatibilité reste explicite.
- Le compilateur traduit un langage source vers une cible. [IBM, Fortran](https://www.ibm.com/history/fortran) décrit la traduction vers le code machine ; [Oracle, commande javac, section Description](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html) décrit la compilation vers des fichiers de classes exécutables par la JVM. Ces deux exemples documentent les cibles citées, sans imposer une cible unique à tous les compilateurs.

La contrainte du capteur absent porte sur une mesure faite avec ce capteur : un logiciel ne crée pas un dispositif physique absent. Une donnée fournie par un autre appareil ou une estimation serait un autre cas. Mémoire, compatibilité du processeur et interfaces constituent d'autres réponses acceptées.

L'évaluation A ne demande plus de justifier une évolution uniforme de machines initialement recâblées vers un matériel devenu générique. Elle demande un couple d'exemples situés et la distinction entre invariant et évolution. Le corrigé compare Mark I et applications compatibles en 2008, documentées par le [communiqué Apple du 14 juillet 2008](https://www.apple.com/newsroom/2008/07/14iPhone-App-Store-Downloads-Top-10-Million-in-First-Weekend/). Les deux machines sont programmables ; les modalités de programmation et les couches changent. Pour la diversification après 1980, l'[annonce Apple de 2007](https://www.apple.com/newsroom/2007/01/09Apple-Reinvents-the-Phone-with-iPhone/) fournit un exemple de smartphone sans en revendiquer la primauté.

Le rattachement à C1/C2 reste celui du contrat et de la rubrique Histoire du [BO de Terminale NSI](https://www.education.gouv.fr/bo/19/Special8/MENE1921247A.htm). La réponse sur 1936 explique le repère conceptuel demandé sans réécrire le libellé officiel. Aucune capacité officielle, quantité d'exercices ou approbation historique n'est modifiée.

## Oracles, corrections et régression

Les quatre objets EX001/CO001/EX002/CO002 sont documentaires. Les tris de listes de dates et `assert True` sont retirés. Le vérificateur les classe `manual_review` et ne leur attribue aucune preuve documentaire par exécution. Les receipts historiques restent dans Git et dans leur répertoire ; leur liaison au contenu corrigé est refusée avec `SOURCE_DIGEST_CHANGED`.

Les deux blocs de l'évaluation ne vérifient désormais que le barème annoncé : 4 + 3 + 3 = 10 ; 5 + 5 = 10 ; total 20. Chacun atteint réellement trois assertions dans le confinement canonique, réseau désactivé. `certifies_documentary_claims=false` demeure explicite. Les réponses ont été relues en regard de chaque demande, notamment l'exemple ancien/récent et la limite demandée en exercice 2 ; les cinq valeurs du barème correspondent au sujet et au corrigé.

Six tests ajoutés ont d'abord échoué : trois objets obtenaient un crédit d'exécution pour des constantes ou une tautologie, le quatrième gardait son ancien digest de source, et les deux blocs d'évaluation ne contrôlaient pas leur barème. Après correction, les six réussissent. Les tests des évaluations changent une composante tout en conservant le total attendu : le bloc devient effectivement rouge. Aucun test de mots ou de dates ne remplace la lecture documentaire.

Commandes observées :

```text
python -m pytest NSI/tests/test_tnsi_history_remaining_sources.py -q
python -m ruff check NSI/tests/test_tnsi_history_remaining_sources.py --select F,E9
git diff --check
```

Résultat : **6 PASS en 0,70 s**, Ruff et contrôle des blancs réussis. Le journal RED de développement est `/tmp/tnsi-history-d1-red.log`. Les tests se reproduisent sans ce journal ; le recours au commit de reprise pour les anciens receipts suit les tests documentaires précédents, avec historique complet dans les workflows concernés. Aucun skip ni xfail n'est ajouté.

## Limites

La version aménagée, sa relation précise avec ses parents et l'accroche contractuelle demeurent hors de ce lot et demandent encore une correction. Les statuts source `generated` ne sont pas promus. Aucun artefact global du chapitre, receipt courant, packet humain, PDF ou build final n'est régénéré. Les résultats exécutables limités au barème ne clôturent pas les dimensions scientifiques ou pédagogiques à la place d'une contre-revue indépendante.

## Empreintes relues

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/exercices/TNSI-HIST-EX-001.tex` : `1856c7480e8d256d1b9102ead714972742ef5de5d99230120098f6f8c6dd4495`

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/corriges/TNSI-HIST-CO-001.tex` : `6cdd710decce1c9ca6d89d3592f9f03e8c78398c8123df740571733da4fa20a8`

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/exercices/TNSI-HIST-EX-002.tex` : `9eb8b6d78a667307a3e857fe398022a552c6ec7375c9c898cf547fc25b69f872`

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/corriges/TNSI-HIST-CO-002.tex` : `73c83f831d574f1fb7f52956f3773381fd22ca504d2369b90f6ca36c9077f06e`

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/evaluations/TNSI-HIST-EVAL-A.tex` : `c61da9ec1cd676baf73bf32a6e21c5b73374e116e0e030d78abe040111ff3099`

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/evaluations/TNSI-HIST-EVAL-A-corrige.tex` : `4bda791dec9e47eab015ab71041852b892a81ad1988494ad2e9334ca841f692b`

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/contrat.yaml` : `a0fe58ea6033423ee35d8ad401310e43945bafc0dc2375f04787023333dc5f48`

- `NSI/tests/test_tnsi_history_remaining_sources.py` : `fdacd6b95aac66e3079aa45bc1a23a374c55f3ff74cc0859bce82b7aeb49be93`

- `NSI/scripts/verify_python.py` : `66ef29b688bc64c81122db9604382d92fef741092ada14441855f1a0d2591675`

- `NSI/scripts/execution_protocol.py` : `71c6ee70eb91f1869c17b4087f35da75018a7e848e1038ec338a5c99810f95e5`

- `NSI/scripts/common.py` : `37822308dace9072c0bedccc3d73c4646dc9010aa859a64591a1fa7ad7338e53`

- `scripts/review_1nsi_content.py` : `e91ff3ae8aff09573a136c9e292b3975e316b9ba78d013ecdcc925c70935686f`

- `scripts/scientific_receipt_binding.py` : `1bf80892f2c2719b20ff26b6de0d13e2b2f904f662a4b1051e8add0ef0aff367`

- `NSI/sources/txt/BO2019_NSI_terminale.txt` : `3cfce30c85fdc7ab78eb9acb39e43bcb33d6205e0c4205d4cb499f80c097f15b`

- `audit/official_program_coverage/TNSI.json` : `95608c6e9cbd5b42077d3d2a7056fe58e24c03c4d7ea57930f06dc3410b24b34`

## Contre-revue indépendante du lot D1

Codex `/root`, sur HEAD `5f64fdb77` avec sources de travail liées aux 15 empreintes ci-dessus, a relu intégralement les six TeX, les six tests, la rubrique officielle Histoire et les deux capacités du contrat. Les questions ont été confrontées aux réponses, y compris les quatre choix de couches logicielles proposés pour les deux réponses attendues. Les lectures documentaires antérieures de Turing (§6), Manchester, DARPA, Harvard, IBM, Ritchie/Thompson et Apple 2008 restent pertinentes ; aucune nouvelle priorité historique n'est déduite de ces exemples.

Les documents supplémentaires ont été ouverts et lus aux passages utiles : spécification JVM chapitre 2 et §2.1 (machine abstraite, format indépendant et réalisation), description de `javac` (source vers fichiers de classes), définition HTML/CSS/JavaScript et exécution dans le navigateur chez Mozilla, annonce Apple datée du 9 janvier 2007. La correspondance des affirmations documentaires et des exemples est soutenue dans cette portée. L'absence de capteur concerne la mesure au moyen de ce capteur ; elle n'interdit pas une donnée externe ou une estimation.

Les six tests ont été réexécutés : **6 PASS, 0 échec, 0 skip**, en 0,66 s. Les 15 empreintes ont été recomparées aux fichiers relus. Le contrôle exécutable du barème vérifie uniquement les sommes des valeurs déclarées dans le bloc : la correspondance avec les points imprimés a été lue manuellement et ne doit pas être présentée comme une extraction automatique. Les réponses historiques ne reçoivent aucun crédit d'exécution. La grammaire corrigée et les limites ajoutées préservent les deux capacités sans réécrire la source officielle.

Verdict de cette contre-revue : `VALIDATED_BY_EVIDENCE` pour le contenu documentaire, la cohérence des réponses et la correction éditoriale de ces six objets dans la portée décrite. Les statuts sources `generated`, l'adaptation aménagée encore en chantier, les preuves dépendantes à reconstruire et l'approbation humaine restent distincts ; le chapitre n'est pas déclaré fermé.

JUnit local : `/tmp/nexus-root-tnsi-history-d1.xml`, SHA256 `5ee63b159688fbfafc5301e8f4961c83ce3a539d8add7c58372e952249f3ad5a`.
