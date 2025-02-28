import os
import re
import requests
import shutil
import time
import random
from bs4 import BeautifulSoup

OUTPUT_DIR = "/output"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
]

def extract_directory_name(filename):
    match = re.search(r'_gif_ - (.*?) - Adult GIF -', filename)
    return match.group(1) if match else "Unknown"

def normalize_url(url):
    if url.startswith("//"):
        return "https:" + url
    elif not url.startswith("http"):
        return None
    return url

def download_file(url, save_path):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    for _ in range(5):
        try:
            response = requests.get(url, headers=headers, stream=True)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)
                print(f"Downloaded: {url}")
                return
            elif response.status_code == 429:
                time.sleep(random.randint(5, 15))
        except Exception as e:
            print(f"Error downloading {url}: {e}")
        time.sleep(random.uniform(1, 3))

def process_html_file(html_file, target_types):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    valid_extensions = {".gif", ".webm", ".mp4"} if "all" in target_types else {f".{ext}" for ext in target_types}
    media_links = [normalize_url(a['href']) for a in soup.find_all('a', href=True) if any(a['href'].endswith(ext) for ext in valid_extensions)]
    media_links = [link for link in media_links if link]

    directory_name = extract_directory_name(os.path.basename(html_file))
    save_directory = os.path.join(OUTPUT_DIR, directory_name)
    os.makedirs(save_directory, exist_ok=True)

    for link in media_links:
        download_file(link, os.path.join(save_directory, os.path.basename(link)))
