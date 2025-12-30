import requests
import os
import json
from bs4 import BeautifulSoup

URL = "https://in.bookmyshow.com/movies/bengaluru/jana-nayagan/buytickets/ET00430817/20260109"
STATE_FILE = "state.json"

PUSHOVER_USER = os.getenv("PUSHOVER_USER")
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")

if not PUSHOVER_USER or not PUSHOVER_TOKEN:
    raise RuntimeError("Pushover secrets not found. Check GitHub Actions secrets.")

def send_pushover(msg):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": PUSHOVER_TOKEN,
            "user": PUSHOVER_USER,
            "message": msg,
            "title": "🎬 Jana Nayagan Alert",
            "priority": 1
        }
    )

def get_shows():
    r = requests.get(URL, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")
    shows = set()

    for a in soup.find_all("a", href=True):
        if "/buytickets/" in a["href"]:
            text = a.get_text(strip=True)
            if text:
                shows.add(text)

    return sorted(shows)

def main():
    shows = get_shows()

    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w") as f:
            json.dump(shows, f)
        return

    with open(STATE_FILE) as f:
        old = json.load(f)

    if len(shows) > len(old):
        send_pushover(
            f"🚨 NEW SHOWS ADDED!\n\n"
            f"Old: {len(old)}\n"
            f"New: {len(shows)}\n\n"
            f"Open BookMyShow now!"
        )

    with open(STATE_FILE, "w") as f:
        json.dump(shows, f)

if __name__ == "__main__":
    main()
