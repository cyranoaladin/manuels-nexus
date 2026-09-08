# NSI — conserver la portée des preuves dans le dashboard historique

Lot QA ciblé du 8 septembre 2026. `chapter_readiness.py` demeure un dashboard historique non autoritaire : cette correction ne le transforme pas en gate de release.

Un receipt NSI courant pouvait être correctement lié à sa source, son implémentation et ses dépendances tout en ne certifiant que l'exécution de quelques assertions. Le dashboard rangeait pourtant son verdict dans `scientific_review`, même lorsque le receipt portait `certifies_documentary_claims=false`. Dans le chapitre historique, les sommes du barème auraient ainsi contribué au compteur de revue scientifique des dates et attributions.

Après le binder existant, le dashboard conserve désormais ces verdicts dans `execution_review`. Il ne leur accorde aucun crédit dans `scientific_review` et expose `documentary_review=REQUIRES_CURRENT_INDEPENDENT_REVIEW`. Ce champ ne prétend pas consulter ni clôturer la dimension documentaire du registre de revue courant. Les verdicts mathématiques qui ne déclarent pas cette limitation conservent leur périmètre précédent. Une erreur d'exécution reste un constat bloquant et intervient dans le score historique ; la séparation ne la rend pas muette.

Les quatre régressions utilisent un receipt réellement produit par le writer NSI dans une fixture temporaire. Le cas intact conserve un crédit d'exécution seul. Les mutations vérifient qu'un échec reste visible, qu'une source modifiée ne conserve aucun crédit et qu'une déclaration documentaire fabriquée est refusée par le binder. Aucun texte de manuel ni receipt du corpus n'est modifié.

Le premier essai de tests avait une fixture incomplète : elle ne possédait pas le contrat nécessaire au résolveur de capacités. Ses quatre erreurs n'étaient donc pas des preuves du défaut. Après ajout du contrat vide de cette fixture, les tests ont été rejoués contre le code antérieur lu depuis Git et chargé dans un module temporaire : **4 FAILED**, notamment parce que le pass ou le fail NSI entrait dans `scientific_review`. Le plugin de cette observation réside dans `/tmp/nexus_old_dashboard_test_plugin.py`, le journal dans `/tmp/tnsi-documentary-dashboard-effective-red.log`. Aucun fichier du dépôt n'a été restauré pour ce replay.

Avec le code corrigé :

```text
python -m pytest tests/test_documentary_execution_scope.py tests/test_current_scientific_receipt_binding.py -q
python -m ruff check scripts/chapter_readiness.py tests/test_documentary_execution_scope.py --select F,E9
git diff --check
```

Résultat observé : **30 PASS en 1,54 s**, Ruff et contrôle des blancs réussis. Aucun seuil n'est changé et aucun skip/xfail n'est ajouté. Les anciens indicateurs éditoriaux du dashboard, explicitement non autoritaires, ne sont pas promus en exigences de release.

La séparation reste à appliquer aux autres consommateurs identifiés, notamment `build_programme_content_validation.py` et la dette couplée NSI. Ce lot ne les certifie pas. La proposition de registration documentaire des quinze sources TNSI reste hors du ledger global, avec ses dépendances courantes à relire selon leur portée.

## Digests du lot

- `scripts/chapter_readiness.py` : `223f7153e4c7faf510cf62757c5b02be8473a428f5e6ff07aa8c2c063dd07f8c`

- `tests/test_documentary_execution_scope.py` : `9ddb3a169349ae758812f421f4d3c1be51ad1f52979ee19bb5e2da3bb635d354`

- `scripts/scientific_receipt_binding.py` : `1bf80892f2c2719b20ff26b6de0d13e2b2f904f662a4b1051e8add0ef0aff367`

- `NSI/scripts/execution_protocol.py` : `71c6ee70eb91f1869c17b4087f35da75018a7e848e1038ec338a5c99810f95e5`

- Version antérieure du dashboard effectivement chargée depuis Git : `208b5159f58be2bccf51ae4c804eff3bc8f9ca2e438e1075497335f9990515f0`.

## Contre-revue indépendante

Codex `/root`, sur HEAD `3d523e887` et les quatre digests ci-dessus, a lu le diff complet, le traitement des receipts et des constats bloquants dans `analyser`, les quatre nouveaux tests et la portée de leurs fixtures canoniques. Le routage intervient après le contrôle existant de source et de méthode ; modifier artificiellement `certifies_documentary_claims` en `true` ne crée pas un crédit scientifique, car le binder refuse cette altération de protocole. La séparation conserve aussi les échecs d'exécution parmi les blocages et dans le calcul du score historique.

Rejeu indépendant : **30 PASS**, sans échec ni skip, en 1,56 s, pour les quatre tests de portée et les vingt-six tests de liaison scientifique existants. Les quatre empreintes de la note correspondent aux fichiers vérifiés. Les fixtures restent temporaires et aucun programme non lu du corpus n'est exécuté.

Verdict : correction du dashboard `VALIDATED_BY_EVIDENCE` dans cette portée. Ce contrôle ne devient ni autorité de release ni mesure de fermeture documentaire ; il ne lit pas le registre courant des revues indépendantes. Les autres consumers identifiés, ainsi que les compteurs globaux et les anciens receipts du corpus, restent hors de ce lot. Aucune approbation humaine n'est attribuée.

JUnit local : `/tmp/nexus-root-nsi-dashboard-scope.xml`, SHA256 `702cb9be0aba13824985cfddfdce4ba8b845119386c234ffd97e274bd491442a`.
