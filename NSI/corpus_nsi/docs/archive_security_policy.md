# Politique de sécurité des archives

Les archives ZIP et TAR sont traitées comme non fiables.

Règles obligatoires :

- destination officielle jamais modifiée avant succès complet ;
- staging `.part` toujours nettoyé après échec ;
- archive refusée si un membre sort de la destination cible ;
- protection zip-slip sur les chemins Unix, Windows et UNC ;
- protection zip-bomb avec limite de 500 Mo décompressés ;
- refus si le nombre de membres dépasse 10 000 ;
- refus si un ratio de décompression suspect dépasse 100x ;
- symlink refusé ;
- hardlink refusé ;
- permissions dangereuses non restaurées ;
- aucune extraction de secrets ;
- aucun fichier officiel partiellement écrit en cas d'échec.

Le commit de staging remplace la destination uniquement après validation et
copie complète de tous les flux. Les échecs de validation ou de lecture
laissent la destination officielle dans son état initial.
