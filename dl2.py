import sys
import re
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm  # Fortschrittsanzeige

# Funktion, die den Download-Link erstellt
def steamtape_get_dl_link(link):
    try:
        if "/e/" in link:
            link = link.replace("/e/", "/v/")

        response = requests.get(link)
        response.raise_for_status()  # Fehler bei ungültiger HTTP-Antwort
        html_source = response.text

        # Regulärer Ausdruck, um den Token zu extrahieren
        norobot_link_pattern = re.compile(r"document\.getElementById\('norobotlink'\)\.innerHTML = (.+?);")
        norobot_link_matcher = norobot_link_pattern.search(html_source)

        if norobot_link_matcher:
            norobot_link_content = norobot_link_matcher.group(1)

            token_pattern = re.compile(r"token=([^&']+)")
            token_matcher = token_pattern.search(norobot_link_content)

            if token_matcher:
                token = token_matcher.group(1)

                # BeautifulSoup, um den versteckten Link zu finden
                soup = BeautifulSoup(html_source, 'html.parser')
                div_element = soup.select_one("div#ideoooolink[style='display:none;']")

                if div_element:
                    streamtape = div_element.get_text()
                    full_url = f"https:/{streamtape}&token={token}"
                    return f"{full_url}&dl=1s"

    except Exception as exception:
        print(f"An error occurred: {exception}")

    return None

# Funktion, die das Video herunterlädt
def download_video(url, filename="video.mp4"):
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            # Gesamtgröße der Datei in Bytes
            total_size = int(response.headers.get('content-length', 0))
            # Fortschrittsanzeige mit tqdm
            with open(filename, "wb") as file, tqdm(
                desc=f"Lädt {filename}",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    progress_bar.update(len(chunk))
        print(f"Video erfolgreich heruntergeladen: {filename}")
    except Exception as e:
        print(f"Fehler beim Herunterladen: {e}")

# Hauptteil des Skripts
if __name__ == "__main__":
    # Prüfen, ob die URL als Argument übergeben wurde
    if len(sys.argv) != 2:
        print("Verwendung: python dl.py <url>")
        sys.exit(1)

    # URL aus den Argumenten lesen
    video_url = sys.argv[1]

    # Download-Link abrufen
    download_link = steamtape_get_dl_link(video_url)

    if download_link:
        print(f"Download gestartet von: {download_link}")
        # Video herunterladen
        download_video(download_link)
    else:
        print("Kein Download-Link gefunden oder es ist ein Fehler aufgetreten.")
