# corpus_nsi — SOURCE T0 (lecture seule)

Ce dossier doit contenir le dépôt cyranoaladin/NSI :
    git submodule add https://github.com/cyranoaladin/NSI corpus_nsi
ou, en local :
    git clone /chemin/vers/NSI corpus_nsi

Le pipeline (harvest, referentiel) lit ce dossier et n'y écrit JAMAIS.
Les statuts needs_review des séquences se propagent aux objets du manuel (F08).
