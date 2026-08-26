# Codex side-car handoff — gel Suites et poursuite T3

## Provenance

- Branche d'intégration (lecture seule) : `audit/adversarial-reconciliation-2026`
- Base d'intégration : `10cb5f07772842d6630d2a2f78531f6900371023`
- Branche Codex : `codex/t2-current-audit-continue`
- HEAD de contenu et de gates couvert par ce handoff :
  `f65538d9750fc291ead944011d06f38ded31054b`
- Candidat 1SPE-SUITES gelé pour revue humaine :
  `c667f12b1792f31981b6b5894c8c604df1bce634`
- Nombre de commits dans la side-car depuis la base d'intégration : 198
- Push : aucun
- Merge : aucun
- Nouvelle extension de baseline : aucune depuis le jalon autorisé des treize
- Oracle D7 modifié : non
- Approbation humaine matérialisée : aucune

Le SHA du commit documentaire qui contient ce fichier n'est pas une nouvelle
source de contenu. Les preuves Suites restent liées au candidat `c667f12b` ; les
gates globaux courants sont liés au HEAD de contenu `f65538d`.

## Liste de commits et ordre d'intégration

La liste complète et ordonnée est définie sans ambiguïté par :

```text
git log --reverse --format='%H %s' \
  10cb5f07772842d6630d2a2f78531f6900371023..f65538d9750fc291ead944011d06f38ded31054b
```

L'ordre de cherry-pick est exactement cet ordre topologique. Le dernier delta,
postérieur au gel du contenu Suites, est :

1. `fe8f4a8b` `[AUDIT] Add exact Suites review freeze producer`
2. `80ee391c` `[AUDIT] Freeze exact Suites human review source`
3. `cfff896a` `[AUDIT] Derive Suites human gate contract fail closed`
4. `0d2eb702` `[AUDIT] Record incomplete Suites human review governance`
5. `c1814cbe` `[LATEX] Fix Variables aléatoires remediation line break`
6. `00fee5ac` `[AUDIT] Consigner les warnings pytest racine`
7. `d542ad00` `[AUDIT] Consigner les warnings layout 1SPE`
8. `8fb48197` `[AUDIT] Add neutral Suites human review packet producer`
9. `ced0b740` `[AUDIT] Publish neutral Suites role review packets`
10. `691b6354` `[MATH] Correct diversification standard deviation`
11. `cc319840` `[LATEX] Use runtime-safe method box in Bernoulli course`
12. `61c16d88` `[AUDIT] Separate Suites content freeze from build envelope`
13. `93687821` `[AUDIT] Cartographier le runtime complet de la charte`
14. `d785a4ed` `[AUDIT] Refresh empty build manifest after T3 sources`
15. `f65538d9` `[AUDIT] Refresh canonical inventory after T3 fixes`

Les commits source de ce delta sont `c1814cbe`, `691b6354` et `cc319840`.
Les autres commits produisent des tests, des ledgers, des packets ou des
artefacts dérivés. Les trois commits source doivent être intégrés avant les
rafraîchissements `d785a4ed` et `f65538d9`.

## Gel et packets 1SPE-SUITES

- Ensemble gelé : 161 objets, sans modification de source après `c667f12b`.
- Digest de l'ensemble :
  `sha256:67d8006298299b44029de8ba8f85b500d9b3619997a0c596e63c20e1cffeee2d`.
- Digest d'autorité programme :
  `sha256:58dc6df881f4f4e6fc6a934ca1837077639dff13da483b587c7a260b70b0a0e1`.
- Packets neutres : EXPERT_MATHEMATIQUE et
  EXPERT_PROGRAMME_PEDAGOGIE.
- Les packets n'enregistrent aucun verdict et ne constituent aucun receipt.
- État des deux revues : `PENDING_UNASSIGNED`.
- État humain QCM : `HUMAN_APPROVAL_PENDING_NO_AUTO_APPROVAL`.

Le dépôt impose les deux rôles de revue et interdit l'auto-approbation, mais ne
définit pas complètement le contrat exécutable d'un receipt d'approbation :
identité, cumul de rôles, granularité, binding SHA/PDF, staleness des dépendances
partagées et autorité des transitions en masse restent non spécifiés. Toute
matérialisation d'une approbation est donc arrêtée en mode fail-closed.

## Corrections T3 après gel

- `1SPE-VARALEA-FR-R2` : formule de probabilités totales sortie de la ligne ;
  le build ciblé de remédiation est propre.
- `1SPE-VARALEA-CO-048` : P0 scientifique corrigé. L'écart-type exact vaut
  environ `3 943,60 €`, donc `3 944 €` à l'euro près, et non `3 946 €`.
- Cours Bernoulli Variables aléatoires : environnement de méthode remplacé par
  le contrat réellement fourni par la classe active ; le chapitre complet
  compile de nouveau.

Ces changements ne touchent aucune source de 1SPE-SUITES.

## Preuves et artefacts exclus

Les PDF de chapitre servant au packet sont des dérivés locaux ignorés. Ils ne
sont ni des PDF de publication ni une preuve D7. Les PDF suivis historiques et
les enveloppes de build intermédiaires doivent être régénérés après intégration ;
ils ne doivent pas être cherry-pickés comme attestation du nouveau HEAD.

Artefacts de preuve principaux :

- `audit/1SPE_SUITES_REVIEW_SOURCE_FREEZE.json`
- `audit/HUMAN_REVIEW_GATE_CONTRACT_1SPE_SUITES.{json,md}`
- `audit/1SPE_SUITES_EXPERT_MATHEMATIQUE_NEUTRAL_REVIEW_PACKET.{json,md}`
- `audit/1SPE_SUITES_EXPERT_PROGRAMME_PEDAGOGIE_NEUTRAL_REVIEW_PACKET.{json,md}`
- `audit/ROOT_PYTEST_WARNING_LEDGER.json`
- `audit/LATEX_LAYOUT_WARNING_LEDGER.json`
- `audit/CANONICAL_STYLE_RUNTIME_REGISTRY.{json,md}`
- `audit/STYLE_CONSUMER_GRAPH.{json,md}`
- `audit/STYLE_DUPLICATE_FORENSICS.{json,md}`

## Gates ouverts

- 1SPE-SUITES : machine content review PASS, mais science, pédagogie et
  éditorial restent non complets sans les vrais receipts exigés.
- Les 15 atoms Suites restent `FULL = 0/15`.
- Les cinq dettes `RESIDUAL_13` du chapitre restent ouvertes.
- `PREVIOUS_89` dans Suites : intersection vide.
- `release-strict` doit rester rouge jusqu'à fermeture réelle de la dette de
  publication.
- La revue visuelle finale, la charte/D7, le prépresse et les douze builds A/B
  restent distincts des revues humaines de contenu.
- La side-car n'est ni publish-ready, ni print-ready, ni distribution-ready.

## Reprise recommandée

1. Examiner les trois commits source du delta.
2. Rejouer leurs tests ciblés et les builds affectés.
3. Intégrer les producteurs/tests de preuve.
4. Régénérer les rapports, le manifeste et l'inventaire au HEAD d'intégration.
5. Ne matérialiser aucun receipt humain tant que le contrat de gouvernance
   incomplet n'a pas une autorité canonique explicite.
6. Ne jamais reprendre un PDF intermédiaire comme preuve de release.
