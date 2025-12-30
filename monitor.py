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

def send_pushover(title, message):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": PUSHOVER_TOKEN,
            "user": PUSHOVER_USER,
            "title": title,
            "message": message,
            "priority": 1
        },
        timeout=20
    )

# 🧪 TEST MODE (manual trigger)
if os.getenv("TEST_NOTIFY") == "1":
    send_pushover(
        "🧪 Test Alert",
        "This is a TEST notification.\nYour alerts are working correctly."
    )
    print("Test notification sent")
    exit(0)

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
    current_shows = get_shows()

    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w") as f:
            json.dump(current_shows, f)
        print("Baseline created")
        return

    with open(STATE_FILE) as f:
        old_shows = json.load(f)

    if len(current_shows) > len(old_shows):
        send_pushover(
            "🚨 New Shows Added!",
            f"New showtimes detected.\n\nOld: {len(old_shows)}\nNew: {len(current_shows)}\n\nOpen BookMyShow now!"
        )

    with open(STATE_FILE, "w") as f:
        json.dump(current_shows, f)

if __name__ == "__main__":
    main()
