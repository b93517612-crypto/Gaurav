# RAS Downloader Bot

Simple Python script that:
- Reads a .txt file for URLs
- Downloads matching files (pdf/mp4/etc)
- Sends them to a Telegram group using a bot

## Setup (local)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Export your environment variables:
```bash
export BOT_TOKEN=123456:ABC-...
export CHAT_ID=-1001234567890
export SOURCE_TXT="RAS Foundation Nirmal Batch 1_0 _Recorded From Studio_.txt"
```
Run:
```bash
python bot_worker.py
```

## Deployment (Render)
1. Push this repo to GitHub.
2. Create a Background Worker on Render.
3. Build: `pip install -r requirements.txt`
4. Start: `python bot_worker.py`
5. Add env vars: BOT_TOKEN, CHAT_ID, SOURCE_TXT.
