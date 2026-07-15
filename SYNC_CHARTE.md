# Synchronisation de la charte Nexus (tronc commun)

## Source de verite

Le projet `Mathematiques/manuel-maths/` est la source de verite pour les fichiers du tronc commun.
Toute evolution de la charte se fait cote maths, puis se propage aux autres manuels.

## Fichiers du tronc commun (4 gabarits + 2 docs)

| Fichier | Source | Destination(s) |
|---|---|---|
| `gabarits/nexus-manuel.cls` | manuel-maths | NSI/gabarits/ |
| `gabarits/nexus-icons.tex` | manuel-maths | NSI/gabarits/ |
| `gabarits/nexus-figures.tex` | manuel-maths | NSI/gabarits/ |
| `gabarits/nexus-signatures.tex` | manuel-maths | NSI/gabarits/ |
| `docs/06_charte_graphique.md` | manuel-maths | NSI/docs/ |
| `docs/07_ligne_editoriale.md` | manuel-maths | NSI/docs/ |

## Fichiers d'extension NSI (ne touchent jamais au tronc)

- `NSI/gabarits/nexus-code.tex`
- `NSI/gabarits/nexus-figures-nsi.tex`

## Commande de synchronisation

```bash
cd ~/Documents/Manuels_Nexus
rsync -av --checksum \
  Mathematiques/manuel-maths/gabarits/{nexus-manuel.cls,nexus-icons.tex,nexus-figures.tex,nexus-signatures.tex} \
  NSI/gabarits/
rsync -av --checksum \
  Mathematiques/manuel-maths/docs/{06_charte_graphique.md,07_ligne_editoriale.md} \
  NSI/docs/
```

## Regle

Les extensions NSI (`nexus-code.tex`, `nexus-figures-nsi.tex`) ne modifient jamais les fichiers du tronc.
La classe `nexus-manuel.cls` charge les extensions via `\InputIfFileExists` : l'absence d'un fichier
d'extension ne casse pas la compilation cote maths.
