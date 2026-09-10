#!/usr/bin/env python3
"""Inventaire HGGSP en lecture seule, bibliothèque standard Python >= 3.10.

Aucun déplacement, suppression, extraction, téléchargement ou exécution des scripts
du dossier analysé. Le rapport est créé dans un NOUVEAU dossier situé hors de la
racine analysée. Les liens symboliques sont répertoriés mais non suivis.
Les empreintes de référence sont celles de l'archive livrée édition 1.0 ; une
empreinte différente n'est pas, à elle seule, la preuve d'une corruption.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import struct
import sys

REFERENCES = {
    'HGGSP_2027_Manuel_Cycle_terminal.pdf': ('V01', 156, 'c9a7f0f4028df745ce6d218a326aa5412546929bd24593289b9e734c8ae8453c'),
    'HGGSP_2027_Niveau_1_Premiere.pdf': ('V02', 95, '33de880c6e3ecbbfa4c3a8f71d9ebba9ca5c790c35bccaff26c0d031fd5539b7'),
    'HGGSP_2027_Compagnon_Autocorrection.pdf': ('V03', 82, '5308c454cacf6036639142207cc4061aadbb4450d22a46b744e84e2e4d985732'),
    'HGGSP_2027_Epreuves_blanches_et_corriges.pdf': ('V04', 46, '17bf7aefdf1cdb335d10c6562b4f601856dd5d0ad402df7fed68ea1aa50adbb4'),
    'HGGSP_2027_Epreuves_Sujets_seuls.pdf': ('V05', 18, 'ca56399dc6b6ea058281d2446753e4e7c48d16c693f0fad2d4742e1a0bedef3d'),
}
# Covers from the user's listing: names only, not validated images.
COUVERTURES = {
    'V01': 'couverture_manuel_cycle_terminal_HGGSP.png',
    'V02': 'couverture_manuel_premiere_EDS_NP_HGGSP.png',
    'V03': 'couverture_autocorrection_HGGSP.png',
    'V04': 'couverture_epreuves_blanches_et_corriges_HGGSP.png',
    'V05': 'couverture_epreuves_blanches_HGGSP.png',
}
SOURCES_ATTENDUES = (
    [f'sources/chapitres/P{i:02}.md' for i in range(1, 6)]
    + [f'sources/chapitres/T{i:02}.md' for i in range(1, 7)]
    + ['sources/banques/banque_pedagogique.json',
       'sources/referentiel/programme.json',
       'sources/referentiel/registre_sources.json',
       'sources/examens/examens_originaux.json',
       'sources/annexes/references.md',
       'sources/methodes/01_module00.md',
       'sources/methodes/02_module00_corrige.md',
       'production/build.py', 'production/assemble.py',
       'production/verifier.py', 'production/style.tex',
       'production/style.css', 'MANIFESTE_SHA256.json']
)

def scan(root: Path) -> tuple[list[dict], list[str]]:
    entries: list[dict] = []
    errors: list[str] = []
    def onerror(error: OSError) -> None:
        errors.append(str(error))
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=onerror):
        base = Path(directory)
        for name in list(dirs):
            p = base / name
            if p.is_symlink():
                entries.append({'chemin': p.relative_to(root).as_posix(), 'type': 'lien_symbolique_non_suivi'})
                dirs.remove(name)
        for name in files:
            p = base / name
            item: dict = {'chemin': p.relative_to(root).as_posix(), 'nom': name}
            try:
                s0 = p.lstat()
                if stat.S_ISLNK(s0.st_mode):
                    item['type'] = 'lien_symbolique_non_suivi'
                elif not stat.S_ISREG(s0.st_mode):
                    item['type'] = 'fichier_special_non_lu'
                else:
                    # O_NOFOLLOW prevents following a replaced final component.
                    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
                    fd = os.open(p, flags)
                    with os.fdopen(fd, 'rb') as f:
                        opened = os.fstat(f.fileno())
                        if (s0.st_dev, s0.st_ino) != (opened.st_dev, opened.st_ino):
                            raise OSError('Fichier remplacé avant lecture')
                        h = hashlib.sha256()
                        header = b''
                        while chunk := f.read(1024 * 1024):
                            if not header:
                                header = chunk[:24]
                            h.update(chunk)
                        ended = os.fstat(f.fileno())
                    s1 = p.lstat()
                    stable = all((x.st_ino, x.st_dev, x.st_size, x.st_mtime_ns, x.st_ctime_ns)
                                 == (s0.st_ino, s0.st_dev, s0.st_size, s0.st_mtime_ns, s0.st_ctime_ns)
                                 for x in (ended, s1))
                    item.update(type='fichier', taille_octets=s0.st_size,
                                sha256=h.hexdigest() if stable else None,
                                stable_pendant_lecture=stable)
                    if not stable:
                        errors.append(f'Fichier modifié pendant lecture : {p}')
                    if name.lower().endswith('.png'):
                        if len(header) >= 24 and header[:8] == b'\x89PNG\r\n\x1a\n' and header[12:16] == b'IHDR':
                            w, hh = struct.unpack('>II', header[16:24])
                            item['png'] = {'largeur_px': w, 'hauteur_px': hh,
                                'ppi_effectifs_si_etire_sur_A4': [round(w / (210 / 25.4), 1), round(hh / (297 / 25.4), 1)],
                                'ecart_ratio_A4_pourcent': round(abs((w / hh) / (210 / 297) - 1) * 100, 2) if hh else None,
                                'limite': 'En-tête uniquement ; ni contrôle visuel, ni décodage complet, ni validation imprimeur.'}
                        else:
                            item['png'] = {'erreur': 'En-tête PNG invalide ou incomplet'}
            except (OSError, ValueError) as exc:
                item['erreur'] = str(exc)
                errors.append(f'{p}: {exc}')
            entries.append(item)
    return sorted(entries, key=lambda x: x['chemin']), errors

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('dossier', type=Path, help='Dossier HGGSP à analyser, récursivement')
    ap.add_argument('--sortie', type=Path, help='Nouveau dossier de rapport, obligatoirement extérieur au dossier analysé')
    args = ap.parse_args()
    root = args.dossier.expanduser().resolve(strict=True)
    if not root.is_dir():
        ap.error('La racine doit être un dossier.')
    now = datetime.now(timezone.utc)
    out = (args.sortie.expanduser() if args.sortie else root.parent / ('AUDIT_HGGSP_' + now.strftime('%Y%m%dT%H%M%S_%fZ'))).resolve()
    if out == root or root in out.parents:
        ap.error('Le rapport doit être créé hors du dossier analysé.')
    if out.exists():
        ap.error('Le dossier de sortie existe déjà ; choisir un nouveau nom pour ne rien écraser.')
    entries, errors = scan(root)
    byname: dict = defaultdict(list)
    byhash: dict = defaultdict(list)
    for item in entries:
        if item.get('type') == 'fichier':
            byname[item['nom']].append(item)
            if item.get('sha256') and item['taille_octets']:
                byhash[item['sha256']].append(item['chemin'])
    volumes = []
    for name, (vid, pages, expected) in REFERENCES.items():
        candidates = byname[name]
        volumes.append({'id': vid, 'nom_attendu': name, 'nombre_fichiers_de_ce_nom': len(candidates),
            'pages_reference_1_0_non_recomptees_localement': pages,
            'candidats': [{'chemin': x['chemin'], 'sha256': x.get('sha256'),
                'comparaison_reference': 'IDENTIQUE_EDITION_1_0' if x.get('sha256') == expected else 'DIFFERENT_OU_LECTURE_INSTABLE_A_EXAMINER'} for x in candidates],
            'nom_couverture_dans_liste_initiale': COUVERTURES[vid],
            'couvertures_de_ce_nom': [x['chemin'] for x in byname[COUVERTURES[vid]]],
            'attribution_couverture': 'NON_VALIDEE_VISUELLEMENT',
            'limite': 'Le nom et le hash ne valident pas une nouvelle édition. Une différence peut être une mise à jour légitime.'})
    source_status = []
    for suffix in SOURCES_ATTENDUES:
        matches = [e['chemin'] for e in entries if e.get('type') == 'fichier'
                   and (e['chemin'] == suffix or e['chemin'].endswith('/' + suffix))]
        source_status.append({'chemin_relatif_attendu': suffix, 'trouves': matches})
    duplicates = [{'sha256': h, 'chemins': paths, 'interpretation': 'Copies identiques ; aucune suppression automatique recommandée.'}
                  for h, paths in byhash.items() if len(paths) > 1]
    report = {'date_utc': now.isoformat(), 'racine_analysee': str(root),
              'type': 'INVENTAIRE_LECTURE_SEULE_SANS_VALIDATION_PEDAGOGIQUE',
              'fichiers_reguliers': sum(e.get('type') == 'fichier' for e in entries),
              'volumes': volumes, 'sources_attendues': source_status,
              'copies_identiques': duplicates, 'erreurs': errors, 'inventaire': entries,
              'limites': ['Les liens symboliques ne sont pas suivis.',
                         'Aucun script du projet exécuté, aucun fichier déplacé ou modifié.',
                         'Le contenu des archives n’est pas développé par ce script.',
                         'Les PDF ne sont pas rendus et leur pagination n’est pas recomptée.',
                         'Aucune couverture n’est validée à partir de ses seuls pixels.',
                         'Les noms recherchés sont ceux de l’édition livrée ; un renommage légitime peut nécessiter un rapprochement manuel.']}
    out.mkdir(parents=True, exist_ok=False)
    (out/'AUDIT_LOCAL.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# Audit local HGGSP — inventaire en lecture seule', '',
             f'Exécution UTC : {now.isoformat()}', f'Racine : `{root}`', '',
             f'Fichiers réguliers : {report["fichiers_reguliers"]}. Erreurs de lecture : {len(errors)}.', '',
             '## Volumes', '| Volume | Fichiers de ce nom | Identiques à la référence 1.0 |', '|---|---:|---:|']
    for v in volumes:
        lines.append(f'| {v["id"]} — `{v["nom_attendu"]}` | {v["nombre_fichiers_de_ce_nom"]} | {sum(x["comparaison_reference"]=="IDENTIQUE_EDITION_1_0" for x in v["candidats"])} |')
    missing = [s['chemin_relatif_attendu'] for s in source_status if not s['trouves']]
    lines += ['', '## Sources non repérées sous les noms attendus', '',
              '\n'.join('- `' + x + '`' for x in missing) if missing else 'Tous les chemins de sources recherchés ont un correspondant.', '',
              '## Limites', '', '\n'.join('- ' + x for x in report['limites']), '',
              'Le fichier AUDIT_LOCAL.json contient les empreintes, les chemins et les dimensions PNG. Ce rapport ne constitue pas un bon à tirer.']
    (out/'AUDIT_LOCAL.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(f'Rapports créés : {out}')
    print(f'PDF attendus repérés : {sum(bool(v["candidats"]) for v in volumes)}/5')
    print(f'Sources recherchées non repérées : {len(missing)}')
    return 2 if errors else 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(f'Échec : {exc}', file=sys.stderr)
        raise SystemExit(2)
