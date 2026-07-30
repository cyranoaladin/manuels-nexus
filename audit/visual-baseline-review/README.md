# Revue des divergences visuelles de la maquette V5

Ce dossier documente les différences sans modifier l'oracle de hashes.

- `contact-sheet.png` présente, pour chaque page, l'ancienne image, la nouvelle
  image puis le diff.
- `pages/page-XX/` contient les trois PNG pleine résolution et la métrique
  ImageMagick `AE`.
- `manifest.json` porte les hashes, métriques, boîtes englobantes, outils et
  verdicts proposés.

Les cinq tests échouent tous sur le contrôle fail-fast du premier hash
non conforme. L'analyse exhaustive montre huit pages réellement différentes :
1, 7, 8, 9, 10, 11, 12 et 15. La page 13 n'est pas divergente : son PNG courant
et son rendu PDF ont le hash
`2edeb64a24a83e38a88a0aefab83e54452eec3c9270cbeee3dc3afefb201af23`.

La zone modifiée est toujours la bande latérale de 71 pixels qui contient
l'onglet. Aucun hash de référence n'a été actualisé.
