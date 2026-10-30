"""Hand-authored neofetch-style info card -> info-card.svg
STATIC=1 emits the finished frame (for local previews)."""
import os

STATIC = os.environ.get("STATIC") == "1"
W, H = 490, 372
BG, FG, DIM = "#0d1117", "#c9d1d9", "#6e7681"
KEY, ACC, GRN = "#58a6ff", "#39d353", "#d2a8ff"

USER = "pratham@amtics"
rows = [
    ("OS", "B.Tech · AI / ML"),
    ("Uni", "AMTICS · Uka Tarsadia University"),
    ("Loc", "Surat, Gujarat, India"),
    ("Role", "Secretary · ACM AMTICS Chapter '26"),
    ("Stack", "Python · JavaScript · Streamlit"),
    ("Focus", "Machine learning · applied AI"),
]
highlights = [
    ("product-substitution-system", "knowledge-graph reasoning"),
    ("ai-study-pal", "AI study assistant"),
    ("test-score-predictor", "classic ML"),
]


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


css = ""
if not STATIC:
    css = ("<style>.l{opacity:0;animation:in .45s ease-out forwards}"
           "@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}"
           ".cur{animation:blink 1s steps(2) infinite}@keyframes blink{50%{opacity:0}}</style>")
else:
    css = "<style>.l{opacity:1}</style>"

out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Pratham info card">', css,
       f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>',
       f'<rect width="{W}" height="30" rx="10" fill="#161b22"/><rect y="20" width="{W}" height="10" fill="#161b22"/>',
       '<circle cx="18" cy="15" r="5" fill="#ff5f56"/><circle cx="36" cy="15" r="5" fill="#ffbd2e"/><circle cx="54" cy="15" r="5" fill="#27c93f"/>',
       f'<text x="{W/2}" y="19" text-anchor="middle" font-size="11" fill="{DIM}" font-family="ui-monospace,Menlo,Consolas,\'DejaVu Sans Mono\',monospace">neofetch — {USER}</text>',
       '<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'DejaVu Sans Mono\',monospace" font-size="13">']

y, step, i = 62, 24, 0


def line(inner, y, i):
    d = 0.15 + i * 0.22
    st = "" if STATIC else f' style="animation-delay:{d:.2f}s"'
    out.append(f'<text class="l" x="24" y="{y}"{st} xml:space="preserve">{inner}</text>')


line(f'<tspan fill="{ACC}" font-weight="bold">{USER}</tspan>', y, i); y += 18; i += 1
line(f'<tspan fill="{DIM}">{"─" * 40}</tspan>', y, i); y += step; i += 1
for k, v in rows:
    line(f'<tspan fill="{KEY}" font-weight="bold">{k:<7}</tspan><tspan fill="{FG}">{esc(v)}</tspan>', y, i); y += step; i += 1
y += 6
line(f'<tspan fill="{GRN}" font-weight="bold">Highlights</tspan>', y, i); y += step; i += 1
for name, desc in highlights:
    line(f'<tspan fill="{ACC}">▸ </tspan><tspan fill="{FG}">{esc(name)}</tspan><tspan fill="{DIM}"> — {esc(desc)}</tspan>', y, i); y += step - 3; i += 1
y += 10
sw = ["#ff5f56", "#ffbd2e", "#27c93f", "#58a6ff", "#d2a8ff", "#39d353", "#c9d1d9", "#6e7681"]
blocks = "".join(f'<rect x="{24 + n * 22}" y="{y - 11}" width="18" height="14" rx="3" fill="{c}"/>' for n, c in enumerate(sw))
st = "" if STATIC else f' style="animation-delay:{0.15 + i * 0.22:.2f}s"'
out.append(f'<g class="l"{st}>{blocks}</g>')
out.append(f'<rect class="cur" x="{24 + 8 * 22 + 6}" y="{y - 12}" width="8" height="16" fill="{ACC}"/>')
out.append("</g></svg>")
open("info-card.svg", "w").write("\n".join(out))
print("wrote info-card.svg, last y =", y)
