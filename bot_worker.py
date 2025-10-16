import os, re, requests, time
from pathlib import Path
from urllib.parse import urlsplit

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
SOURCE_TXT = input("Enter path of your .txt file: ").strip()

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0"}
URL_RE = re.compile(r"(https?://[^\s]+|www\.[^\s]+)", re.IGNORECASE)

def extract_urls_from_file(path):
    p = Path(path)
    if not p.exists():
        print("❌ File not found:", path)
        return []
    txt = p.read_text(encoding="utf-8", errors="ignore")
    urls = URL_RE.findall(txt)
    print(f"✅ Found {len(urls)} URLs")
    return urls

def safe_filename_from_url(url):
    name = Path(urlsplit(url).path).name or "file"
    return name

def download_stream(url, out_path):
    if url.startswith("www."):
        url = "https://" + url
    try:
        with requests.get(url, headers=HEADERS, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    if chunk:
                        f.write(chunk)
        return True
    except Exception as e:
        print("❌ Download error:", e)
        return False

def send_to_telegram(file_path):
    api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(file_path, "rb") as f:
        data = {"chat_id": CHAT_ID}
        files = {"document": f}
        r = requests.post(api, data=data, files=files)
        print("📤 Sent to Telegram:", file_path.name, "→", r.ok)

def main():
    urls = extract_urls_from_file(SOURCE_TXT)
    allowed_ext = (".pdf", ".mp4", ".mkv", ".webm")
    for url in urls:
        name = safe_filename_from_url(url)
        ext = Path(name).suffix.lower()
        if ext not in allowed_ext:
            continue
        out = DOWNLOAD_DIR / name
        print(f"⬇️  Downloading {url}")
        if download_stream(url, out):
            send_to_telegram(out)
            out.unlink(missing_ok=True)
        time.sleep(1)

if __name__ == "__main__":
    main()
