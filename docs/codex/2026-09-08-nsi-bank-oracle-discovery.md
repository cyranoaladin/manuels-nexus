# NSI — oracles des banques et extraits aménagés

Observation de développement du 8 septembre 2026. Le writer canonique `NSI/scripts/verify_python.py` ne parcourait pas trois répertoires appartenant au corpus : `banque_ecrite`, `banque_pratique` et `amenagee`. Un chapitre avec un oracle correct dans `cours` et un oracle faux dans chacun de ces répertoires pouvait retourner zéro en ignorant ce dernier.

Les trois mutations ont été exécutées séparément avant la correction : chacune a montré ce faux succès. Les trois répertoires sont maintenant ajoutés à la liste existante. Les mêmes mutations deviennent rouges au niveau du gate, ce qui fait réussir les tests de régression. Dans chaque même fixture, l’oracle faux est ensuite remplacé par une assertion correcte : le gate retourne alors zéro. Cette vérification exclut un échec forcé pour toute nouvelle banque. Les règles d'exécution, de confinement, de comparaison du code et de liaison des digests sont conservées.

L'inventaire statique observé contient 563 fichiers TeX dans le périmètre élargi : 18 fichiers de banque écrite, 8 de banque pratique et 17 extraits aménagés s'ajoutent aux 520 fichiers de l'ancien périmètre. Les marqueurs VERIFY, TRACE ou Python publié apparaissent dans 18, 8 et 10 de ces fichiers respectivement, soit 36 fichiers concernés. Les sept autres extraits aménagés restent découverts, sans preuve exécutable inventée. `qcm` et `coups_de_pouce`, également présents dans l'arborescence, ne contenaient aucun de ces marqueurs lors de cette observation.

Cet inventaire décrit une découverte, pas une campagne d'exécution du corpus. Aucun PASS supplémentaire ni nouvelle review scientifique ne se déduit de ces nombres. Aucun receipt du corpus n'a été généré par ce lot ; les nouveaux objets découverts devront être lus puis exécutés. Le changement du digest du vérificateur invalide normalement la méthode des receipts dépendants : ils ne sont pas rafraîchis implicitement.

Commandes observées :

```text
python -m pytest NSI/tests/test_verify_python_protocol.py -q -k canonical_bank_and_adapted
python -m pytest NSI/tests/test_verify_python_protocol.py NSI/tests/test_verify_python.py tests/test_current_scientific_receipt_binding.py tests/test_manual_assembler_import_isolation.py -q
```

La première commande a montré 3 échecs avant correction, puis 3 PASS après correction. La seconde a produit 67 PASS. Aucun skip ni xfail n'a été ajouté. Les tests emploient des fichiers temporaires avec un code connu ; aucune source non lue des nouvelles banques n'a été exécutée.

Les tests de confinement antérieurs restent inchangés : la liste des répertoires ne modifie ni l'isolation du réseau ni le lancement des programmes. Cette note n'est pas une revue documentaire des affirmations historiques, une approbation humaine ou une preuve de release.

Contre-revue `/root` : lecture du diff et du parcours effectif de `main`, qui découvre les fichiers avant exécution et compare encore leur ensemble en fin de contrôle. Les trois ajouts utilisent ce même parcours ; aucun traitement particulier ne leur accorde un PASS. La famille ciblée a produit 67 PASS en 6,11 s. Après renforcement demandé lors de la contre-revue, chaque nouvelle fixture vérifie successivement un oracle faux puis un oracle vrai dans le même répertoire : les trois tests passent, avec des retours respectivement non nuls puis nuls. Ce dernier contrôle a été réexécuté par `/root` : 3 PASS en 1,52 s, 26 tests non sélectionnés. Aucun de ces résultats n'est une exécution des banques réelles.

L'inventaire indépendant de `/root` retrouve 520 anciens fichiers, puis 18, 8 et 17 fichiers dans les trois répertoires ajoutés, avec respectivement 18, 8 et 10 fichiers portant les marqueurs examinés. Les 18 QCM et 24 coups de pouce observés n'en portent pas. La découverte statique et la validation des programmes restent deux mesures distinctes. Verdict de revue du changement de périmètre : `VALIDATED_BY_EVIDENCE`, sans approbation humaine et sans clôture des sources nouvellement découvertes.
