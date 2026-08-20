from pathlib import Path
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
import json
import re
import requests

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "profile-config.json").read_text(encoding="utf-8"))
USERNAME = CFG["username"]
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = ROOT / "data" / "contributions.json"

response = requests.get(
    URL,
    timeout=25,
    headers={
        "User-Agent": "Mozilla/5.0 GitHub-profile-art/1.0",
        "Accept": "text/html,application/xhtml+xml",
    },
)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

days = []
for cell in soup.select("[data-date]"):
    raw_date = cell.get("data-date")
    if not raw_date or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_date):
        continue
    try:
        level = int(cell.get("data-level", "0"))
    except ValueError:
        level = 0

    label = cell.get("aria-label", "")
    cid = cell.get("id")
    if cid:
        tip = soup.find("tool-tip", attrs={"for": cid})
        if tip:
            label = tip.get_text(" ", strip=True)

    m = re.search(r"([\d,]+)\s+contributions?", label, flags=re.I)
    count = int(m.group(1).replace(",", "")) if m else 0
    days.append({"date": raw_date, "count": count, "level": max(0, min(level, 4))})

# De-duplicate if GitHub emits more than one data-date element.
by_date = {d["date"]: d for d in days}
days = [by_date[k] for k in sorted(by_date)]
if not days:
    raise RuntimeError("No contribution cells were parsed; GitHub's markup may have changed.")

def calc_streak(items):
    dates = {datetime.strptime(d["date"], "%Y-%m-%d").date(): d["count"] for d in items}
    today = date.today()
    cursor = today if dates.get(today, 0) else today - timedelta(days=1)
    streak = 0
    while dates.get(cursor, 0) > 0:
        streak += 1
        cursor -= timedelta(days=1)
    return streak

longest = 0
run = 0
for d in days:
    if d["count"] > 0:
        run += 1
        longest = max(longest, run)
    else:
        run = 0

best = max(days, key=lambda d: d["count"])
payload = {
    "username": USERNAME,
    "updated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "total": sum(d["count"] for d in days),
    "current_streak": calc_streak(days),
    "longest_streak": longest,
    "best_day": best,
    "days": days,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(f"wrote {OUT} ({len(days)} days, {payload['total']} contributions)")
