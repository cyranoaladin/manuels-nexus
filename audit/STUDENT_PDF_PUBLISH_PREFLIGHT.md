# Préflight publication — variantes élève

Contrôle read-only des six PDF élève canoniques présents dans les répertoires de build. L'ancien hub `MANUELS_PDF_PUBLICATION` est explicitement exclu.

## Résultat

- PDF contrôlés : 6 / 6
- `TEACHER_ONLY_CONTENT_LEAK` : 0 document(s)
- `PDF_METADATA_INCOMPLETE` : 0 document(s)
- `PDF_NAVIGATION_MISSING` : 0 document(s)
- Release candidate admissible : **false**

## Par manuel

- `1SPE` : PASS; marqueurs=0; signets=76; Title=True; Author=True.
- `TSPE` : PASS; marqueurs=0; signets=108; Title=True; Author=True.
- `TCOMPL` : PASS; marqueurs=0; signets=36; Title=True; Author=True.
- `TEXPERTES` : PASS; marqueurs=0; signets=20; Title=True; Author=True.
- `1NSI` : PASS; marqueurs=0; signets=51; Title=True; Author=True.
- `TNSI` : PASS; marqueurs=0; signets=36; Title=True; Author=True.

## Décision

Les PDF Math observés sont des artefacts périmés et ne peuvent pas être empaquetés. Le gate doit être rejoué après reconstruction au `FINAL_SOURCE_SHA`; seuls des builds dont la provenance correspond exactement à ce SHA peuvent devenir release candidates.
