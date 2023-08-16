import re
import requests
import csv

def extract_video_code(url):
    pattern = r"/(\d+)/?$"  # Assumim que el video es troba als digits al final dels links
    matches = re.findall(pattern, url)
    if matches:
        return matches[-1]  # Troba el darrer resultat
    else:
        return None

def extract_video_codes(urls):
    video_codes = []
    for url in urls:
        video_code = extract_video_code(url)
        if video_code:
            video_codes.append(video_code)
    return video_codes

def generate_video_urls(video_codes):
    video_urls = []
    for code in video_codes:
        url = f"http://dinamics.ccma.cat/pvideo/media.jsp?media=video&version=0s&idint={code}"
        video_urls.append(url)
    return video_urls
# Extraccio de les URL, fent servir User Agent de navegador per evitar resposta negativa del servidor
def extract_media_urls(url):
    print("Fetching content from:", url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    print("Response status code:", response.status_code)
    content = response.text

    # Extraccio de valors "programa" i "titol" fent servir expressions regulars
    programa_match = re.search(r'"programa":"([^"]+)"', content)
    programa = programa_match.group(1) if programa_match else None

    title_match = re.search(r'"titol":"([^"]+)"', content)
    title = title_match.group(1) if title_match else None

    mp4_urls = re.findall(r'"file":"(https?://[^"]+\.mp4)","label":"([^"]+)"', content)
    vtt_urls = re.findall(r'"subtitols":\[\{"text":"([^"]+)"[^}]+"url":"((?!sprite\.vtt).+\.vtt)"', content)

    last_720p_url = None
    last_480p_url = None

    # Cerca i troba els links pels videos en 480p i 720p, filtrant per evitar repeticions
    for mp4_url in mp4_urls:
        label = mp4_url[1]
        link = mp4_url[0]
        if label == "720p":
            last_720p_url = link
        elif label == "480p":
            last_480p_url = link

    return programa, title, [last_720p_url, last_480p_url], vtt_urls

# El script consulta els links estandards de TV3Alacarta dins el fitxer links per extreure els links de descarrega
file_path = "links.txt"
with open(file_path, "r") as file:
    html_urls = file.read().splitlines()

video_codes = extract_video_codes(html_urls)
video_urls = generate_video_urls(video_codes)

output_file = 'links-fitxers.csv'
with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "Quality", "Link", "File Name"])

    for video_url in video_urls:
        programa, title, mp4_urls, vtt_urls = extract_media_urls(video_url)

        for i, mp4_url in enumerate(mp4_urls):
            label = "720p" if i == 0 else "480p"
            link = mp4_url
            file_name = link.split("/")[-1]
            file_extension = file_name.split(".")[-1]
            name = f"{programa} - {title}.{file_extension}"
            writer.writerow([name, label, link, file_name])

        for vtt_url in vtt_urls:
            label = vtt_url[0]
            link = vtt_url[1].split('"')[0]
            file_name = link.split("/")[-1]
            file_extension = file_name.split(".")[-1]
            name = f"{programa} - {title}.{file_extension}"
            writer.writerow([name, label, link, file_name])

print("Extraccio completada, links disponibles a", output_file)
