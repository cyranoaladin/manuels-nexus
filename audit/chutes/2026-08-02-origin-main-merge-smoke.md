# Chutes — smoke test de résolution de merge

Date : 2026-08-02

Périmètre : résolution des conflits entre `origin/main` et
`finalisation/collection-v1`, limitée à l'état de collection généré et à
l'oracle visuel de la maquette V5.

## Disponibilité

La liste des modèles a répondu et annoncé 12 modèles réellement disponibles.
Une consultation indépendante a ensuite été tentée avec
`Qwen/Qwen3-32B-TEE` afin d'auditer la conservation de la source générée,
de la décision humaine de baseline premium et du statut NO-GO.

## Résultat

L'appel a été refusé avant inférence avec un statut HTTP 402 pour quota de
compte épuisé. Aucun texte de modèle, avis indépendant ou décision
disciplinaire n'a été produit.

Les détails financiers et l'adresse contenus dans l'erreur brute ne sont pas
recopiés dans le dépôt. Aucun secret ni donnée personnelle n'a été transmis.

## Disposition

Statut : `blocked_external_quota`.

Chutes restant consultatif, la résolution est fondée sur les preuves locales :

- `ETAT_COLLECTION.md` reste dérivé par `inventory_collection.py` et
  conserve explicitement le gate `release-strict` rouge ;
- la décision humaine du 31 juillet 2026 approuve les hashes premium des
  douze pages concernées ;
- le checker, son test de contrat et les PNG suivis doivent porter les mêmes
  empreintes ;
- les tests et gates locaux doivent confirmer l'absence de régression avant
  création du commit à deux parents.
