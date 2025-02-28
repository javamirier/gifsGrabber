import os
import time
import threading
import requests
from flask import Flask, render_template, request, redirect, url_for
from downloader import process_html_file

app = Flask(__name__)
OUTPUT_DIR = "/output"

def download_page(url):
    """Downloads the HTML page and saves it locally."""
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            filename = url.split("/")[-1] + ".html"
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(response.text)
            return filepath
        else:
            print(f"Failed to download page: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading page: {e}")
        return None

def background_monitor(url, target_types):
    """Monitors the page every 3 hours and redownloads new media."""
    while True:
        print(f"Rechecking {url} for new media...")
        html_file = download_page(url)
        if html_file:
            process_html_file(html_file, target_types)
        else:
            print(f"Page {url} might have expired. Stopping monitoring.")
            break
        time.sleep(10800)  # 3 hours

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        target_types = request.form.getlist("media_types")

        if url:
            html_file = download_page(url)
            if html_file:
                process_html_file(html_file, target_types)

                # Start background monitoring in a separate thread
                thread = threading.Thread(target=background_monitor, args=(url, target_types))
                thread.daemon = True
                thread.start()

                return redirect(url_for("index"))

    return render_template("index.html")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    app.run(host="0.0.0.0", port=5000)
