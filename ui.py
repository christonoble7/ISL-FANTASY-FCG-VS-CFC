"""Look and feel: Goa orange vs Chennaiyin blue, fantasy-app style, responsive.

HTML strings are kept free of blank lines and indentation so Streamlit's markdown
renderer does not turn them into code blocks.
"""
import html

from logic import BUDGET, CFC, GOA, LIMITS

GOA_C, CFC_C = "#F26A1B", "#1F4FD8"

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&display=swap');
.block-container{max-width:760px;padding:1rem .8rem 4rem}
.stApp{background:radial-gradient(900px 380px at 0% 0%,rgba(242,106,27,.16),transparent 60%),radial-gradient(900px 380px at 100% 0%,rgba(31,79,216,.20),transparent 60%),#0E1530}
.hero{position:relative;display:flex;border-radius:18px;overflow:hidden;margin:.2rem 0 .6rem;box-shadow:0 8px 24px rgba(0,0,0,.35)}
.hero .side{flex:1;padding:18px 8px 16px;text-align:center;color:#fff;font-family:'Barlow Condensed',sans-serif;font-weight:800;font-size:clamp(22px,7vw,38px);line-height:1}
.hero .side small{display:block;margin-top:6px;font-size:12px;font-weight:600;opacity:.9;letter-spacing:.04em}
.hero .goa{background:linear-gradient(135deg,#ff8a3d,#e5530a)}
.hero .cfc{background:linear-gradient(135deg,#3d7bff,#1244c9)}
.hero .vs{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:40px;height:40px;line-height:36px;border-radius:50%;background:#0E1530;color:#fff;border:2px solid #fff;text-align:center;font-family:'Barlow Condensed',sans-serif;font-weight:800;font-size:16px}
.kick{text-align:center;color:#b8c3ea;font-size:13px;margin-bottom:.6rem}
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:.4rem 0}
.tile{background:#161f42;border:1px solid #26325f;border-radius:12px;padding:8px 4px;text-align:center}
.tile b{display:block;font-family:'Barlow Condensed',sans-serif;font-size:26px;line-height:1.1;color:#fff}
.tile span{font-size:12px;color:#9fb0e6}
.tile.over b{color:#ff6b6b}
.bar{height:10px;background:#1b2550;border-radius:6px;overflow:hidden;margin:6px 0 10px}
.bar .fill{height:100%;border-radius:6px;background:linear-gradient(90deg,#F26A1B,#1F4FD8)}
.bar .fill.over{background:#ff4d4d}
.pitch{position:relative;border-radius:18px;padding:14px 4px 12px;margin:8px 0 12px;border:2px solid rgba(255,255,255,.28);background:repeating-linear-gradient(0deg,#1d8a47 0 44px,#22a056 44px 88px);overflow:hidden}
.pitch:before{content:"";position:absolute;left:22%;right:22%;top:0;height:13%;border:2px solid rgba(255,255,255,.28);border-top:none}
.pitch:after{content:"";position:absolute;left:22%;right:22%;bottom:0;height:13%;border:2px solid rgba(255,255,255,.28);border-bottom:none}
.prow{position:relative;z-index:1;display:flex;justify-content:center;flex-wrap:wrap;gap:clamp(2px,2vw,14px);margin:7px 0}
.slot{position:relative;width:clamp(60px,18vw,92px);text-align:center}
.shirt{width:clamp(38px,11vw,54px);height:clamp(38px,11vw,54px);margin:0 auto;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-family:'Barlow Condensed',sans-serif;font-weight:800;font-size:clamp(12px,3.4vw,16px);border:2px solid #fff;box-shadow:0 3px 8px rgba(0,0,0,.35)}
.shirt.goa{background:linear-gradient(145deg,#ff8a3d,#e5530a)}
.shirt.cfc{background:linear-gradient(145deg,#3d7bff,#1244c9)}
.shirt.empty{background:rgba(255,255,255,.10);border:2px dashed rgba(255,255,255,.55);box-shadow:none}
.pname{margin-top:4px;padding:1px 5px;border-radius:6px;background:rgba(8,12,30,.65);color:#fff;font-size:clamp(10px,2.8vw,12px);font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pprice{font-size:11px;color:#fff;opacity:.95}
.cap{position:absolute;top:-5px;right:calc(50% - 34px);width:20px;height:20px;border-radius:50%;background:#fff;color:#0E1530;font-weight:800;font-size:12px;line-height:20px;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,.4)}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 10px}
.chip{font-size:12px;padding:3px 10px;border-radius:999px;border:1px solid}
.chip.ok{color:#42e3a0;border-color:#42e3a066;background:#42e3a018}
.chip.bad{color:#ff7b7b;border-color:#ff7b7b66;background:#ff7b7b18}
.stButton>button{width:100%;border-radius:12px;font-weight:700;padding:.7rem 1rem}
@media (max-width:480px){.block-container{padding:.6rem .5rem 4rem}}
</style>"""


def hero_html() -> str:
    return (
        '<div class="hero">'
        '<div class="side goa">FC GOA<small>The Gaurs</small></div>'
        '<div class="vs">VS</div>'
        '<div class="side cfc">CHENNAIYIN<small>Marina Machans</small></div>'
        '</div>'
        '<div class="kick">Saturday 10 October, 7:30 PM IST, Fatorda Stadium</div>'
    )


def tiles_html(n: int, spent: float, squad: int = 11) -> str:
    left = BUDGET - spent
    over = " over" if left < -1e-9 else ""
    pct = min(100.0, max(0.0, spent / BUDGET * 100))
    fill = "fill over" if over else "fill"
    return (
        '<div class="tiles">'
        f'<div class="tile"><b>{n}/{squad}</b><span>Players</span></div>'
        f'<div class="tile"><b>{spent:g}</b><span>Spent (Cr)</span></div>'
        f'<div class="tile{over}"><b>{left:g}</b><span>Left (Cr)</span></div>'
        '</div>'
        f'<div class="bar"><div class="{fill}" style="width:{pct:.0f}%"></div></div>'
    )


def short_name(name: str) -> str:
    parts = name.split()
    if len(parts) == 1 or len(parts[-1]) == 1:
        return name
    return f"{parts[0][0]}. {parts[-1]}"


def pitch_html(chosen, captain) -> str:
    """Draw the picked XI on a pitch: FWD at the top, GK at the bottom."""
    rows = []
    for pos in ("FWD", "MID", "DEF", "GK"):
        sub = chosen[chosen["pos"] == pos]
        slots = []
        for _, r in sub.iterrows():
            cls = "goa" if r["team"] == GOA else "cfc"
            cap = '<div class="cap">C</div>' if r["player"] == captain else ""
            slots.append(
                f'<div class="slot">{cap}<div class="shirt {cls}">{pos}</div>'
                f'<div class="pname">{html.escape(short_name(r["player"]))}</div>'
                f'<div class="pprice">{r["price"]:g} Cr</div></div>'
            )
        for _ in range(max(0, LIMITS[pos][0] - len(sub))):
            slots.append(
                f'<div class="slot"><div class="shirt empty">+</div>'
                f'<div class="pname">{pos}</div><div class="pprice">&nbsp;</div></div>'
            )
        rows.append('<div class="prow">' + "".join(slots) + "</div>")
    return '<div class="pitch">' + "".join(rows) + "</div>"


def chips_html(checks) -> str:
    chips = "".join(
        f'<span class="chip {"ok" if ok else "bad"}">{"✓" if ok else "✗"} {html.escape(msg)}</span>'
        for ok, msg in checks
    )
    return f'<div class="chips">{chips}</div>'
