# -*- coding: utf-8 -*-
"""
Script de Scraping Spécifique Éduscol NSI avec Extraction & Tri de ZIP.

Description: Ce script extrait les ressources officielles NSI depuis Éduscol,
             télécharge les fichiers et gère l'extraction automatique
             ainsi que le tri intelligent des archives ZIP (sujets d'examens, codes).

Utilise netpolicy pour la conformité robots.txt et la politesse réseau,
et provenance pour la traçabilité de l'origine des ressources.
"""

from __future__ import annotations

import os
import shutil
import zipfile
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT_DIR = Path(__file__).resolve().parents[1]

from bs4 import BeautifulSoup
from scrapping_NSI.netpolicy import (
    DEFAULT_USER_AGENT,
    DomainThrottle,
    RobotsCache,
    build_session,
    polite_get,
)
from scrapping_NSI.provenance import compute_sha256, guess_license, write_provenance_record

from scripts.archive_security import ArchiveSecurityError, safe_extract_zip

# URLs racines officielles de la spécialité NSI sur Eduscol STI
EDUSCOL_NSI_URLS = [
    "https://sti.eduscol.education.fr/formations/bac-voie-generale/specialite-nsi-numerique-et-sciences-informatiques",
    "https://sti.eduscol.education.fr/referentiels-par-competences-bac-scientifique/specialite-nsi-numerique-et-sciences-informatiques",
]

EDUSCOL_DELAY = float(os.getenv("NSI_EDUSCOL_DELAY", "1.2"))


def clean_name(name: str) -> str:
    """Nettoie une chaîne pour en faire un nom de fichier valide."""
    keepcharacters = (".", "_", "-", " ")
    cleaned = "".join(c for c in name if c.isalnum() or c in keepcharacters).strip()
    return cleaned if cleaned else "ressource_sans_nom"


def extract_and_sort_zip(zip_path: str, base_dest_dir: str) -> None:
    """Extrait une archive ZIP et trie son contenu par extension.

    Le ZIP est extrait via le garde Lot 3 avant tri: zip-slip, volume
    décompressé, nombre de fichiers et ratio de compression sont bloqués.
    """
    temp_extraction_dir = os.path.join(base_dest_dir, "_temp_zip_extraction")

    try:
        print(f"  [ZIP] Décompression de l'archive : {os.path.basename(zip_path)}...")
        safe_extract_zip(Path(zip_path), Path(temp_extraction_dir))

        compteur_fichiers = 0
        for root, _, files in os.walk(temp_extraction_dir):
            for file in files:
                chemin_source = os.path.join(root, file)

                if file.startswith(".") or "__MACOSX" in chemin_source:
                    continue

                ext = os.path.splitext(file)[1].lower().strip(".")
                if not ext:
                    ext = "sans_extension"

                if ext in ["py", "pyw"]:
                    categorie = "01_Codes_Python"
                elif ext in ["pdf"]:
                    categorie = "02_Sujets_et_Cours_PDF"
                elif ext in ["docx", "doc", "odt"]:
                    categorie = "03_Documents_Texte"
                elif ext in ["png", "jpg", "jpeg", "gif", "svg"]:
                    categorie = "04_Images_et_Graphiques"
                elif ext in ["html", "css", "js"]:
                    categorie = "05_Ressources_Web"
                elif ext in ["csv", "json", "xml", "txt"]:
                    categorie = "06_Donnees_et_Configuration"
                else:
                    categorie = f"07_Autres_{ext.upper()}"

                dossier_cible = os.path.join(base_dest_dir, "Archives_Extraites_Triees", categorie)
                os.makedirs(dossier_cible, exist_ok=True)

                chemin_destination = os.path.join(dossier_cible, file)

                if os.path.exists(chemin_destination):
                    nom_base, extension = os.path.splitext(file)
                    counter = 1
                    while os.path.exists(chemin_destination):
                        chemin_destination = os.path.join(
                            dossier_cible, f"{nom_base}_doublon_{counter}{extension}"
                        )
                        counter += 1

                shutil.move(chemin_source, chemin_destination)
                compteur_fichiers += 1

        print(f"  [ZIP] Extraction réussie : {compteur_fichiers} fichiers triés et classés.")

    except ArchiveSecurityError as exc:
        print(f"  [Erreur ZIP] Archive refusée pour raison de sécurité : {exc}")
        raise
    except zipfile.BadZipFile:  # pragma: no cover
        print(f"  [Erreur ZIP] L'archive {os.path.basename(zip_path)} semble corrompue.")
    except Exception as e:  # pragma: no cover
        print(f"  [Erreur ZIP] Échec lors du traitement de l'archive : {e}")
    finally:
        if os.path.exists(temp_extraction_dir):
            shutil.rmtree(temp_extraction_dir)


def scrape_eduscol_nsi(
    *,
    provenance_path: Path | None = None,
) -> None:
    print("====================================================================")
    print("DÉMARRAGE DU SCRAPER ÉDUSCOL NSI - RESSOURCES INSTITUTIONNELLES")
    print("====================================================================")

    session = build_session(user_agent=DEFAULT_USER_AGENT)
    robots = RobotsCache(user_agent=DEFAULT_USER_AGENT, session=session)
    throttle = DomainThrottle()

    dossier_principal = os.path.join("ressources_nsi_extraites", "Eduscol_Officiel")
    dossier_zip_bruts = os.path.join(dossier_principal, "Archives_ZIP_Brutes")

    os.makedirs(dossier_principal, exist_ok=True)
    os.makedirs(dossier_zip_bruts, exist_ok=True)

    for page_url in EDUSCOL_NSI_URLS:
        print(f"\n[Analyse Page] Exploration de : {page_url}")

        response, error, blocked = polite_get(
            session, page_url, robots=robots, throttle=throttle,
            min_delay=EDUSCOL_DELAY,
        )

        if blocked:
            print(f"  [Robots] {error}")
            continue
        if error:
            print(f"  [Erreur] {error}")
            continue
        if response is None:
            print("  [Erreur] Réponse vide inattendue")
            continue
        if response.status_code != 200:
            print(f"  [Erreur] Impossible d'accéder à la page (Code : {response.status_code})")
            continue

        page_html = response.text
        soup = BeautifulSoup(page_html, "html.parser")
        liens = soup.find_all("a")

        print(f"  {len(liens)} liens détectés. Recherche de documents officiels...")
        fichiers_telecharges = 0

        for lien in liens:
            href = lien.get("href")
            texte_lien = lien.text.strip()
            if not href:
                continue

            href_lower = href.lower()
            is_file = href_lower.endswith((".pdf", ".zip", ".docx", ".xlsx"))
            is_drupal_download = (
                "/download" in href_lower or "fichier" in href_lower or "file" in href_lower
            )

            if is_file or is_drupal_download:
                url_absolue = urljoin(page_url, href)

                parsed_path = urlparse(url_absolue).path.lower()
                if ".zip" in parsed_path or ".zip" in href_lower:
                    ext = ".zip"
                elif ".docx" in parsed_path or ".docx" in href_lower:
                    ext = ".docx"
                elif ".xlsx" in parsed_path or ".xlsx" in href_lower:
                    ext = ".xlsx"
                else:
                    ext = ".pdf"

                nom_propre = clean_name(texte_lien) if texte_lien else clean_name(
                    os.path.basename(parsed_path)
                )
                if not nom_propre or nom_propre == "download":
                    nom_propre = "ressource_officielle"

                nom_fichier_final = f"{nom_propre[:60]}{ext}"

                if ext == ".zip":
                    chemin_local = os.path.join(dossier_zip_bruts, nom_fichier_final)
                else:
                    chemin_local = os.path.join(dossier_principal, nom_fichier_final)

                if os.path.exists(chemin_local):
                    if ext == ".zip":
                        extract_and_sort_zip(chemin_local, dossier_principal)
                    continue

                print(f"  [Téléchargement] -> {nom_fichier_final}")

                file_resp, file_error, file_blocked = polite_get(
                    session, url_absolue, robots=robots, throttle=throttle,
                    min_delay=EDUSCOL_DELAY, stream=True,
                )

                if file_blocked:
                    print(f"    [Robots] {file_error}")
                    continue
                if file_error:
                    print(f"    [Erreur requête] {file_error}")
                    continue
                if file_resp is None:
                    print("    [Erreur requête] Réponse fichier vide inattendue")
                    continue

                if file_resp.status_code == 200:
                    with open(chemin_local, "wb") as f:
                        for chunk in file_resp.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                    fichiers_telecharges += 1

                    if provenance_path:
                        sha = compute_sha256(Path(chemin_local))
                        content_type = file_resp.headers.get("content-type", "")
                        write_provenance_record(
                            provenance_path,
                            sha256=sha,
                            filename=nom_fichier_final,
                            source_url=url_absolue,
                            site_name="Éduscol STI",
                            page_url=page_url,
                            http_status=200,
                            content_type=content_type,
                            byte_count=os.path.getsize(chemin_local),
                            robots_allowed=True,
                            license_guess=guess_license(page_html),
                        )

                    if ext == ".zip":
                        extract_and_sort_zip(chemin_local, dossier_principal)
                else:
                    print(f"    [Échec] Statut HTTP {file_resp.status_code}")

        print(f"[Fin de Page] Terminée. {fichiers_telecharges} nouveaux fichiers traités.")

    print("\n====================================================================")
    print("PROCESSUS ÉDUSCOL TERMINÉ. Les archives ont été décompressées et triées.")
    print(f"Consultez le dossier : '{dossier_principal}'")
    print("====================================================================")


if __name__ == "__main__":
    provenance = Path(os.getenv("NSI_PROVENANCE_FILE", "provenance.jsonl"))
    scrape_eduscol_nsi(provenance_path=provenance)
