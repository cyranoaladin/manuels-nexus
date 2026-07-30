# Revue des divergences visuelles de la maquette V5

Ce dossier documente les différences sans modifier l'oracle de hashes.

## Planches-contact

- [Planche complète haute résolution](contact-sheet-full.png) :
  `3879 × 15024`, triptyques à la résolution native des pages.
- [Zooms haute résolution](contact-sheet-zooms.png) :
  `2076 × 7392`, crops `320 × 400` agrandis ×2 autour des bboxes.
- [Planche historique](contact-sheet.png) :
  version compacte conservée pour traçabilité.

Chaque ligne présente l'ancienne image, la nouvelle image puis le diff.

## Preuves par page

`pages/page-XX/` contient :

- `old.png`, extrait du commit-oracle `60d0460` ;
- `new.png`, identique au PNG suivi au HEAD ;
- `diff.png`, visualisation ImageMagick ;
- `ae.txt`, nombre absolu de pixels modifiés.

`manifest.json` porte les hashes complets des trois images, les pourcentages,
les bboxes, les versions de LuaTeX/Poppler/ImageMagick/Pillow, les versions et
empreintes SHA-256 des dix fichiers de polices incorporés, les mesures de
couche textuelle et les preuves de rerastérisation.

Les cinq tests échouent tous sur le contrôle fail-fast du premier hash
non conforme. L'analyse exhaustive montre huit pages réellement différentes :
1, 7, 8, 9, 10, 11, 12 et 15. La page 13 n'est pas divergente : son PNG courant
et son rendu PDF ont le hash
`2edeb64a24a83e38a88a0aefab83e54452eec3c9270cbeee3dc3afefb201af23`.

La zone modifiée est toujours la bande latérale de 71 pixels qui contient
l'onglet. L'extérieur de chaque bbox est identique pixel à pixel. Une
rerastérisation fraîche à 150 dpi du PDF courant donne `AE=0` face aux huit
images `new.png`. Le commit `f071d37` remplace l'onglet fixe de 16 mm par une
longueur calculée sur le libellé avec 6 mm de marge et recentre le texte : la
cause est donc une modification de source démontrée, pas une dérive
d'environnement.

Aucun hash de référence n'a été actualisé. Le verdict reste une proposition
Codex soumise à décision humaine page par page.
