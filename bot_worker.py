import os
import re
import requests
from pathlib import Path
from urllib.parse import urlsplit
import time

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
SOURCE_TXT = os.environ.get("SOURCE_TXT", "RAS Foundation Nirmal Batch 1_0 _Recorded From Studio_.txt")
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; downloader/1.0)"}
URL_RE = re.compile(r"https?://[^\s)'"]+", re.IGNORECASE)

def extract_urls_from_file(path):
    p = Path(path)
    if not p.exists():
        print("Source file not found:", path)
        return []
    txt = p.read_text(encoding="utf-8", errors="ignore")
    return URL_RE.findall(txt)

def safe_filename_from_url(url):
    p = urlsplit(url).path
    name = Path(p).name
    return name if name else "file"

def download_stream(url, out_path, chunk_size=1024*32, max_retries=3):
    for attempt in range(max_retries):
        try:
            with requests.get(url, headers=HEADERS, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
            return True
        except Exception as e:
            print(f"[download error] attempt {attempt+1} for {url}: {e}")
            time.sleep(2)
    return False

def send_file_to_telegram(file_path, caption=None):
    if not BOT_TOKEN or not CHAT_ID:
        print("Missing BOT_TOKEN or CHAT_ID in environment.")
        return False, "missing token/chat_id"

    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(file_path, "rb") as fd:
        files = {"document": (file_path.name, fd)}
        data = {"chat_id": CHAT_ID}
        if caption:
            data["caption"] = caption
        try:
            resp = requests.post(api_url, data=data, files=files, timeout=180)
            return resp.ok, resp.text
        except Exception as e:
            return False, str(e)

def main():
    urls = extract_urls_from_file(SOURCE_TXT)
    print(f"Found {len(urls)} URLs in {SOURCE_TXT}")
    allowed_ext = (".pdf", ".mp4", ".mkv", ".webm", ".pptx", ".zip")
    for url in urls:
        fname = safe_filename_from_url(url)
        ext = Path(fname).suffix.lower()
        if ext and ext not in allowed_ext:
            print("Skipping (extension not allowed):", url)
            continue
        out_path = DOWNLOAD_DIR / fname
        if out_path.exists() and out_path.stat().st_size > 100:
            print("Already downloaded:", out_path)
        else:
            print("Downloading:", url)
            ok = download_stream(url, out_path)
            if not ok:
                print("Download failed for:", url)
                continue
        print("Sending to Telegram:", out_path.name)
        ok, resp = send_file_to_telegram(out_path, caption=f"Sent: {out_path.name}")
        print("Telegram response ok:", ok)
        if ok:
            try:
                out_path.unlink()
            except Exception:
                pass
        else:
            print("Telegram send failed, response:", resp)
        time.sleep(1)

if __name__ == "__main__":
    main()
