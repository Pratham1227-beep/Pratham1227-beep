"""data/contributions.json -> contrib-heatmap.svg (53x7 rounded boxes that
slide in diagonally once, then freeze). STATIC=1 = finished frame."""
import json
import os
from datetime import date

STATIC = os.environ.get("STATIC") == "1"
d = json.load(open("data/contributions.json"))
days = d["days"]
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG, FG, DIM = "#0d1117", "#c9d1d9", "#6e7681"
CELL, GAP = 13, 3
P = CELL + GAP
LEFT, TOP = 40, 46
mx = max((x["count"] for x in days), default=0)

first = date.fromisoformat(days[0]["date"])
lead = (first.weekday() + 1) % 7          # GitHub weeks start on Sunday
weeks = (lead + len(days) + 6) // 7
W = LEFT + weeks * P + 24
H = TOP + 7 * P + 62

css = "" if STATIC else (
    "<style>.c{opacity:0;animation:s .5s ease-out forwards}"
    "@keyframes s{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}</style>")
mono = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"
out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Contribution heatmap">', css,
       f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>',
       f'<g font-family="{mono}" font-size="10" fill="{DIM}">']

for n, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
    out.append(f'<text x="10" y="{TOP + n * P + 10}">{lab}</text>')

last_month = None
for idx, x in enumerate(days):
    pos = lead + idx
    wk, dow = divmod(pos, 7)
    dt = date.fromisoformat(x["date"])
    partial_start = idx == 0 and dt.day > 10      # skip cramped first label
    if dt.month != last_month and (dow == 0 or idx == 0) and wk < weeks - 1 and not partial_start:
        out.append(f'<text x="{LEFT + wk * P}" y="{TOP - 10}">{dt.strftime("%b")}</text>')
        last_month = dt.month
    elif partial_start:
        last_month = dt.month
    lvl = x["level"]
    if lvl >= 4 and mx and x["count"] >= 0.8 * mx:
        lvl = 5
    delay = "" if STATIC else f' style="animation-delay:{(wk + dow) * 0.018:.3f}s"'
    cls = "" if STATIC else ' class="c"'
    out.append(f'<rect{cls} x="{LEFT + wk * P}" y="{TOP + dow * P}" width="{CELL}" height="{CELL}" rx="3" fill="{PALETTE[lvl]}"{delay}><title>{x["count"]} on {x["date"]}</title></rect>')
out.append("</g>")

fy = TOP + 7 * P + 28
out.append(f'<g font-family="{mono}" font-size="11">')
out.append(f'<text x="{LEFT}" y="{fy}" fill="{FG}">{d["total"]:,} contributions in the last year</text>')
out.append(f'<text x="{LEFT}" y="{fy + 18}" fill="{DIM}">current streak {d["current_streak"]}d · longest {d["longest_streak"]}d · best day {d["best_day"]["count"]}</text>')
lx = W - 24 - 6 * (CELL + 4) - 70
out.append(f'<text x="{lx}" y="{fy + 10}" fill="{DIM}" font-size="10">Less</text>')
for n, c in enumerate(PALETTE):
    out.append(f'<rect x="{lx + 30 + n * (CELL + 4)}" y="{fy}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>')
out.append(f'<text x="{lx + 34 + 6 * (CELL + 4)}" y="{fy + 10}" fill="{DIM}" font-size="10">More</text>')
out.append("</g></svg>")
open("contrib-heatmap.svg", "w").write("\n".join(out))
print("wrote contrib-heatmap.svg", W, "x", H)
