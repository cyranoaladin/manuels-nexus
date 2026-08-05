# LOT-4 — Rapport de production : Exercices + Corriges + CDP

## Chapitre : TSPE-SUITES-LIMITES

### Inventaire : 50 exercices, 50 corriges, 18 CDP

### Couverture par capacite et parcours

| Capacite | Exercices | P1 | P2 | P3 | CDP |
|----------|-----------|----|----|----|----|
| C1 | EX-001 a EX-007 | 001,002,003 | 004,005 | 006,007 | 001,002,003 |
| C2 | EX-008 a EX-014 | 008,009,010 | 011,012 | 013,014 | 008,009,010 |
| C3 | EX-015 a EX-021 | 015,016,017 | 018,019 | 020,021 | 015,016,017 |
| C4 | EX-022 a EX-028 | 022,023,024 | 025,026 | 027,028 | 022,023,024 |
| C5 | EX-029 a EX-035 | 029,030,031 | 032,033 | 034,035 | 029,030,031 |
| C6 | EX-036 a EX-042 | 036,037,038 | 039,040 | 041,042 | 036,037,038 |
| C7 | EX-043 a EX-050 | 043,044 | 045,046,047 | 048,049,050 | — |

### Totaux

| Parcours | Nombre |
|----------|--------|
| Parcours 1 | 20 exercices |
| Parcours 2 | 15 exercices |
| Parcours 3 | 15 exercices |
| CDP | 18 fichiers |

### Verification

- Tous les exercices ont un bloc BEGIN-VERIFY/END-VERIFY avec assertions SymPy.
- Tous les corriges ont un bloc BEGIN-VERIFY/END-VERIFY.
- Les META headers sont au format JSON.
- Couverture 100% des 7 capacites sur les 3 parcours.

### Types d'exercices

- P1 : calculs directs, applications de formules, recurrences guidees
- P2 : demonstrations partiellement guidees, modelisation, Bernoulli
- P3 : type bac (suites recurrentes completes, preuves epsilon-N, Cesaro, sommes de series)

### Points ouverts

- Verification SymPy via make verify a effectuer.
- Similarite via make similarity a effectuer.

## Audit de reprise — 2026-08-05

50 exercices (parcours1:20, parcours2:15, parcours3:15) + 19 coups de pouce +
50 corriges, couverture C1-C7 complete. SymPy : 0 FAIL. Spot-check manuel
(EX-001/CO-001 et autres) : corrects, coherents avec l'enonce. R3 (anti-
similarite) non automatisable ici : pas de DB/pgvector configuree dans cet
environnement (cf. `terminale/collection-v1` ROADMAP) ; mode ex-nihilo deja
valide en LOT 1 rend ce check moins critique (sources_inspiration: [] partout,
pas de corpus externe reutilise). Statut : valide.

## Correctif critique — 2026-08-05 (audit approfondi post-mode-autonome)

En poursuivant l'audit sur le chapitre 2, un balayage retroactif du chapitre 1
a revele **3 defauts P0 non detectes par la premiere passe SymPy**, tous du
meme type : du texte de brouillon ("auto-correction en direct") laisse dans
le contenu final, ET dans un cas (CO-021) un bloc VERIFY qui testait une
formule erronee auto-coherente avec l'erreur du corrige — donc "verified"
sans etre correct. Ceci confirme qu'un verdict SymPy OK ne suffit pas si le
bloc VERIFY lui-meme encode la meme erreur que le contenu : necessite une
relecture humaine des demonstrations et corriges a enjeu, pas seulement le
badge [OK].

1. **TSPE-SUITLIM-CO-033** (Bernoulli/q^n, exercice sur $n \times 0{,}9^n$) :
   l'exercice demandait de deduire $u_n \leq 9n/(9+n)$ (qui tend vers $9$, pas
   $0$) — la methode proposee ne pouvait pas aboutir a la conclusion demandee.
   Le corrige contenait des traces explicites de l'echec ("Mais on veut
   montrer -> 0... Corrigeons", "Ceci ne donne pas 0"). **Corrige** :
   exercice et corrige reecrits avec la bonne methode (Bernoulli d'ordre 2 via
   le binome, $\binom{n}{2}a^2$), qui aboutit correctement a $u_n \to 0$.
2. **07_td_fil_rouge.tex, partie C** (convergence via $v_n = u_n^2-3$) :
   l'enonce affirmait $v_{n+1} = (u_n-1)^2(u_n^2-3)/(u_n+1)^2$ (facteur
   $(u_n-1)^2$ inexistant) et des bornes $|v_{n+1}|\leq \frac14|v_n|$,
   $|v_n|\leq 2/4^n$ non coherentes avec le calcul reel. Le corrige avait deja
   recalcule la bonne formule ($v_{n+1}=-2v_n/(u_n+1)^2$, bornes en
   $\frac12$ et $2/2^n$) mais laissait tout le brouillon visible et l'enonce
   n'avait jamais ete corrige en consequence. **Corrige** : enonce aligne sur
   la formule exacte, corrige nettoye, bloc VERIFY ajoute.
3. **TSPE-SUITLIM-CO-021** (suite arithmetico-geometrique, emprunt) : la
   question 4 concluait "$u_n \to -\infty$ donc l'emprunt n'est jamais
   rembourse (la dette croitra)" — **contradiction logique directe** (une
   suite qui tend vers $-\infty$ finit forcement par etre $\leq 0$, donc le
   capital restant du s'annule : l'emprunt EST rembourse). La question 5
   redecouvrait explicitement cette contradiction en cours de redaction
   ("Contradiction avec le resultat precedent. Revoyons :") avant d'aboutir
   au bon rang $n_0=21$ par un raisonnement circulaire et confus. Le bloc
   VERIFY du fichier testait une formule differente de celle du corrige
   ($-600000+800000\times1{,}02^n$ au lieu de $600000-400000\times1{,}02^n$),
   coincidant seulement en $n=0$ : verdict OK obtenu sur une verification qui
   ne portait pas sur le bon objet. **Corrige** : question 4 et 5 entierement
   reecrites (raisonnement correct et lineaire), bloc VERIFY corrige et
   etendu (teste desormais la vraie formule + les 3 cas de la question 5).

Verification post-correctif : `make verify` toujours 0 FAIL (116 OK / 26
REVIEW), `make chapter` toujours 36 pages, compilation propre.
