# Topologie des branches — Réconciliation

## Doctrine

main = source de vérité unique. Tout travail passe par une branche dédiée et
intègre main via Pull Request GitHub. Aucun push direct sur main.

## Chronologie

| Événement | SHA | Date |
|-----------|-----|------|
| main avant réconciliation | 0d886e0 | 2026-06-29 |
| lot1/substance-gouvernance (avant ff) | e06eb2b | 2026-06-29 |
| lot3-post-merge-hardening | 0e3484c | 2026-06-29 |
| Fast-forward lot1 ← lot3 | 0e3484c | 2026-06-30 |
| PR #3 merge → main | 069eabf | 2026-06-30 |

## Opérations

1. `git fetch --all --prune`
2. Vérification : lot1 est ancêtre de lot3 (fast-forward possible)
3. `git merge --ff-only origin/lot3-post-merge-hardening` sur lot1
4. Push lot1/substance-gouvernance (e06eb2b → 0e3484c)
5. PR #2 (lot3-post-merge-hardening → main) fermée comme redondante
6. PR #3 (lot1/substance-gouvernance → main) créée, CI verte, mergée via GitHub
7. main mis à jour : 0d886e0 → 069eabf

## Vérifications

- Aucune modification pédagogique (03_progressions, premiere, terminale, 02_modeles_documents) dans les diffs
- CI quality : SUCCESS sur 0e3484c (PR #3) et 069eabf (main post-merge)
- GitGuardian : PASS
