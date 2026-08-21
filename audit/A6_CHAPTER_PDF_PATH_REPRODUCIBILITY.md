# A6 — diagnostic de reproductibilité inter-racines du producteur chapitre

## Statut

Le candidat A6 `bcac52aa9d0f5385b470410320b082ae6f3bd321` est
**disqualifié**. Le producteur chapitre ne génère pas encore un PDF
byte-identique lorsque la racine absolue du dépôt change.

## Reproduction réelle

- chapitre : `TCOMPL-CALCULS-AIRES` ;
- variante : `complet` ;
- environnement : `SOURCE_DATE_EPOCH=1785962466`,
  `FORCE_SOURCE_DATE=1`, `TZ=UTC`, `LC_ALL=C.UTF-8`, `LANG=C.UTF-8`,
  `PYTHONHASHSEED=0` ;
- racine A :
  `/home/alaeddine/Documents/Manuels_Nexus/.worktrees/pre-a6-a6-context-mismatches` ;
- racine B : `/tmp/nexus-a6-fresh-a.gDIXtd/repo` ;
- pages A/B : `18` / `18` ;
- taille A/B : `135629` / `135629` octets ;
- SHA-256 PDF A :
  `a40e6eecbb7fd16698d9fceb8a5a1ce6d146323c08d34833d80fada933106655` ;
- SHA-256 PDF B :
  `1b167af59c413a0f542d289d2f684db441c114ac649ce3ef478d10479e3c9722` ;
- SHA-256 master `.tex` A/B :
  `557e593d7e2f5fbe242e22598bdc55b3083c12a1509cebd0fc9dc96d763d1420` ;
- SHA-256 texte `pdftotext` A/B :
  `413bc17e0fb76d144fa5266eb81d1ce47960146176d273b33df6416b76bdfc3c` ;
- trailer `/ID` A :
  `b6aeee2d370f3cd814c8b98f37f02d6f` deux fois ;
- trailer `/ID` B :
  `e50520b9de597b1ab4ce88868e6ec582` deux fois ;
- octets différents : `58` ;
- SHA-256 QDF brut A :
  `5f48b49d135ca9a03321a91e8c29764aec38bcb0ee0bbf3315651e97daeaba41` ;
- SHA-256 QDF brut B :
  `c48e8cff0ba9419ff587940f4dbfe0fa2cad71b4740911270cfbb92148e4d64f` ;
- SHA-256 QDF après neutralisation du seul champ `/ID`, A/B :
  `dd95ff541ef8f30fdc31b040c5b785aab035dc2ebe2fcc25645bd3ec5f6d4405`.

Les masters sont identiques, les textes sont identiques et les QDF deviennent
byte-identiques après neutralisation du trailer. Deux compilations successives
dans Fresh A ont également redonné le même PDF B. Le signal dépend donc de la
racine absolue, pas d'une instabilité aléatoire intra-racine.

## Cause racine

`Mathematiques/manuel-maths/scripts/assemble.py` exécute LuaLaTeX sans injecter
de `\pdfvariable trailerid`. Sous l'environnement reproductible A4, LuaTeX
stabilise le résultat dans une racine donnée mais dérive encore son `/ID` d'une
donnée liée au chemin. Le producteur de manuel possède déjà le contrat A4
d'identité déterministe ; le producteur chapitre ne l'applique pas.

La correction autorisée doit réutiliser ce contrat partagé et exclure de sa
préimage les chemins absolus, le cwd, les sorties de build, les anciens PDF,
le run ID, l'horloge murale et Git HEAD. Aucune baseline, aucun oracle visuel,
aucun statut et aucune source pédagogique ne sont concernés.

## TDD RED

Le test `test_chapter_pdf_is_path_independent_across_absolute_git_roots`
construit un petit dépôt Git suivi, le clone sous deux racines absolues
`root-A` et `root-B`, puis compile le même chapitre `TCOMPL-TEST`, variante
`complet`, avec le producteur réel et l'environnement A4. Il vérifie d'abord
pages, texte et QDF neutralisé, puis exige l'égalité finale des octets PDF.
Avant correctif, cette dernière assertion est l'unique échec observé.

Reproduction RED exécutée au HEAD de plan
`3f21f8c8178aad14c55804943d301dbd95d7cc38` :

```text
python -m pytest -q Mathematiques/manuel-maths/tests/test_assemble_engine.py -k 'path_independent'
1 failed, 1 deselected
```

- racine fixture A :
  `/tmp/pytest-of-alaeddine/pytest-540/test_chapter_pdf_is_path_indep0/root-A` ;
- racine fixture B :
  `/tmp/pytest-of-alaeddine/pytest-540/test_chapter_pdf_is_path_indep0/root-B` ;
- commit Git fixture A/B :
  `d94e53f83e6aabf44665926e1a7cebff6a4ed22d` ;
- pages A/B : `2` / `2` ;
- taille A/B : `10087` / `10087` octets ;
- SHA-256 PDF A :
  `d1d1467badb8630732d28849753a123c82e94fe4732c3b7788a3ee1d00c732a8` ;
- SHA-256 PDF B :
  `2957d5bab769fad707214beff96ba2d79c24048b829df5384574609503c2e8e4` ;
- SHA-256 texte A/B :
  `b39826554b70f89b764822bd52c29f451faba9454659733365b1b826d88e7c93` ;
- trailer `/ID` A :
  `aaa24ba370beb87d324264c17c1bf0c2` deux fois ;
- trailer `/ID` B :
  `9d59c3c28d0099a76f279413c3daf97e` deux fois ;
- octets différents : `60` ;
- SHA-256 QDF neutralisé A/B :
  `7e004aa99ba660ea7a025cf536bf1d5d16193d9b6f7ec252d2ced1038a26d1a1`.

Les trois assertions préparatoires (pages, texte, QDF neutralisé) passent ;
l'échec porte exclusivement sur `bytes_a == bytes_b` et affiche les deux SHA
PDF ainsi que les deux trailers.
