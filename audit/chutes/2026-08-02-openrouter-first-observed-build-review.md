# Revue indépendante OpenRouter — premier build observé 1SPE

Date : 2026-08-02

Périmètre : revue adversariale anonymisée du design reliant un assembleur
LuaLaTeX réel, ses marqueurs ordonnés, son `.fls`, son préflight PDF et le
manifeste Phase 0.

## Stratégie de coût et de confidentialité

Un seul appel a été effectué avec `qwen/qwen3.7-flash`, température `0` et une
sortie plafonnée. Le prompt était court, abstrait et ne contenait ni secret, ni
donnée personnelle, ni extrait de manuel. Le routage demandait le fournisseur
le moins cher.

La requête a activé le cache de réponse OpenRouter avec une durée d'une heure.
Le cache n'a pas été réutilisé pour ce premier appel. Le cache de prompt est
laissé au mécanisme automatique du fournisseur ; aucun préfixe volumineux ou
contenu du dépôt n'a été envoyé.

Mesure renvoyée par l'API :

- 207 jetons d'entrée ;
- 2 283 jetons de sortie, raisonnement inclus ;
- coût total observé : 0,000303 USD ;
- tarif catalogue observé au moment de l'appel : 0,03 USD par million de jetons
  d'entrée et 0,13 USD par million de jetons de sortie.

La clé API n'est ni consignée, ni transmise aux outils du dépôt, ni suivie par
Git. Le fichier local `.env` qui la contient est ignoré et limité aux droits du
propriétaire. Comme la clé a été exposée dans la conversation, sa rotation reste
recommandée.

## Risques signalés et disposition locale

### Actifs transitifs et environnement

La combinaison marqueurs + `.fls` n'est pas une preuve hermétique de tous les
effets externes possibles. Disposition : ne revendiquer que l'observation des
entrées déclarées et ouvertes, capturer les versions d'outils, puis tester les
chemins imbriqués, normalisés et symboliques.

### Reproductibilité limitée au même hôte

Deux compilations identiques sur la même machine ne prouvent pas l'identité sur
un autre système. Disposition : nommer cette limite dans le design et ne pas en
faire un gate de publication cross-plateforme.

### Provenance Git par ancêtre

L'acceptation d'un SHA ancêtre peut devenir trop permissive si elle est isolée.
Disposition : exiger cumulativement branche, existence de l'objet Git, relation
d'ancêtre, digests source/modèle et identité du PDF ; ajouter des tests de rejet
pour SHA non ancêtre et dérives.

### Fenêtre entre préflight et reçu

Le PDF ou ses preuves pourraient changer entre le contrôle et l'enregistrement.
Disposition : écrire atomiquement, vérifier les fraîcheurs, recalculer les
digests et rejeter toute modification pendant la transaction.

### Contournement par CLI optionnelle

Un mode d'enregistrement explicite peut être omis par un producteur ou une CI.
Disposition : conserver le gate release bloquant pour tout PDF canonique sans
build observé valide et représenter l'intégration comme partielle tant que tous
les producteurs requis ne sont pas raccordés.

## Conclusion

La revue ne valide aucune décision scientifique, éditoriale ou de publication.
Ses cinq risques sont traduits en invariants et tests dans la spécification
locale. La décision finale reste fondée sur les sources, les builds et les gates
du dépôt.
