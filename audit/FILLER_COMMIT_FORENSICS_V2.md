# Forensique de `533d1919`, normalisation corrigee

Supersede `audit/FILLER_COMMIT_FORENSICS.json`.

L'analyse precedente comparait des corps portant encore l'identifiant de l'objet, et ne confrontait les creations qu'aux corps anterieurs au commit : une banque recopiee quinze fois a l'interieur du meme commit passait pour quinze creations originales.

## Classification

| classe | objets |
| --- | --- |
| `PREEXISTING_AUTHENTIC_CONTENT` | 281 |
| `FILLER_COPY` | 2747 |
| `GENUINE_NEW_AUTHORING` | 35 |
| `FORMAT_ONLY` | 20 |
| `METADATA_ONLY` | 720 |
| `UNKNOWN` | 0 |

- mutations pedagogiques : `3803`
- copies d'un corps anterieur : `2645`
- copies creees dans le commit : `102`
- groupes sans original demontrable : `16`
