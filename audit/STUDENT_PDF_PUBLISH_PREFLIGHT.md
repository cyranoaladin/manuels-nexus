# Préflight publication — variantes élève

Contrôle read-only des six PDF élève canoniques présents dans les répertoires de build. L'ancien hub `MANUELS_PDF_PUBLICATION` est explicitement exclu.

## Résultat

- PDF contrôlés : 6 / 6
- `TEACHER_ONLY_CONTENT_LEAK` : 4 document(s)
- `PDF_METADATA_INCOMPLETE` : 4 document(s)
- `PDF_NAVIGATION_MISSING` : 4 document(s)
- Release candidate admissible : **false**

## Par manuel

- `1SPE` : TEACHER_ONLY_CONTENT_LEAK, PDF_METADATA_INCOMPLETE, PDF_NAVIGATION_MISSING; marqueurs=9; signets=0; Title=False; Author=False.
- `TSPE` : TEACHER_ONLY_CONTENT_LEAK, PDF_METADATA_INCOMPLETE, PDF_NAVIGATION_MISSING; marqueurs=11; signets=0; Title=False; Author=False.
- `TCOMPL` : TEACHER_ONLY_CONTENT_LEAK, PDF_METADATA_INCOMPLETE, PDF_NAVIGATION_MISSING; marqueurs=9; signets=0; Title=False; Author=False.
- `TEXPERTES` : TEACHER_ONLY_CONTENT_LEAK, PDF_METADATA_INCOMPLETE, PDF_NAVIGATION_MISSING; marqueurs=5; signets=0; Title=False; Author=False.
- `1NSI` : PASS; marqueurs=0; signets=103; Title=True; Author=True.
- `TNSI` : PASS; marqueurs=0; signets=93; Title=True; Author=True.

## Décision

Les PDF Math observés sont des artefacts périmés et ne peuvent pas être empaquetés. Le gate doit être rejoué après reconstruction au `FINAL_SOURCE_SHA`; seuls des builds dont la provenance correspond exactement à ce SHA peuvent devenir release candidates.
