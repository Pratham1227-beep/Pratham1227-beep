"""Scrape the public contribution calendar (no API token needed) and write
data/contributions.json with the raw days + derived stats."""
import json
import os
import re
import sys
from collections import OrderedDict
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup

USER = os.environ.get("GH_USER", "Pratham1227-beep")
URL = f"https://github.com/users/{USER}/contributions"

r = requests.get(URL, headers={"User-Agent": "profile-readme-bot"}, timeout=30)
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")

tips = {t.get("for"): t.get_text(" ", strip=True) for t in soup.find_all("tool-tip")}
days = []
for td in soup.select("td.ContributionCalendar-day"):
    d = td.get("data-date")
    if not d:
        continue
    tip = tips.get(td.get("id"), "")
    m = re.match(r"(\d+)\s+contribution", tip)
    count = int(m.group(1)) if m else 0
    days.append({"date": d, "count": count, "level": int(td.get("data-level", 0))})

if not days:
    sys.exit("no contribution cells found — GitHub markup may have changed")
days.sort(key=lambda x: x["date"])

total = sum(x["count"] for x in days)
best = max(days, key=lambda x: x["count"])

longest = cur = 0
prev = None
for x in days:
    dd = date.fromisoformat(x["date"])
    if x["count"] > 0:
        cur = cur + 1 if prev and dd - prev == timedelta(days=1) else 1
        longest = max(longest, cur)
        prev = dd
    else:
        cur = 0
        prev = dd if prev is None else prev
# current streak: walk back from the last day (today may still be empty)
streak = 0
for x in reversed(days):
    if x["count"] > 0:
        streak += 1
    elif x is days[-1]:
        continue
    else:
        break

months = OrderedDict()
for x in days:
    months[x["date"][:7]] = months.get(x["date"][:7], 0) + x["count"]

os.makedirs("data", exist_ok=True)
json.dump({"user": USER, "total": total, "current_streak": streak, "longest_streak": longest,
           "best_day": best, "months": months, "days": days},
          open("data/contributions.json", "w"), indent=1)
print(f"{USER}: {total} contributions, streak {streak}, longest {longest}, {len(days)} days")
