from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from logic import (BUDGET, GOA, MAX_PER_TEAM, PLAYERS, SQUAD_SIZE, STAT_COLS,
                   entry_total, points_table, validate)
from ui import CSS, chips_html, hero_html, pitch_html, tiles_html

IST = ZoneInfo("Asia/Kolkata")
DEADLINE = datetime(2026, 10, 10, 19, 25, tzinfo=IST)  # entries close 5 min before kickoff
ENTRY_COLS = ["time", "handle", "captain", "cost", "players"]
ENTRIES_CSV, STATS_CSV = Path("entries.csv"), Path("stats.csv")

st.set_page_config(page_title="ISL Fantasy: Goa vs Chennaiyin", page_icon="⚽", layout="centered")
# ---------- Google Login ----------
if not st.user.is_logged_in:
    st.title("⚽ ISL Fantasy")
    st.write("Sign in with Google to continue.")

    st.button(
        "Continue with Google",
        on_click=st.login,
        args=["google"],
        type="primary"
    )

    st.stop()

# Authenticated user's identity
user_email = st.user.email
user_name = st.user.name
st.markdown(CSS, unsafe_allow_html=True)


# ---------- storage: Google Sheets if configured, else local CSV ----------
def _secret(key, default=None):
    """Read a Streamlit secret; returns default if there is no secrets file."""
    try:
        return st.secrets[key]
    except Exception:
        return default


@st.cache_resource
def get_sheet():
    sa, sid = _secret("gcp_service_account"), _secret("sheet_id")
    if sa and sid:
        import gspread
        gc = gspread.service_account_from_dict(dict(sa))
        return gc.open_by_key(sid)
    return None


def _ws(name):
    sh = get_sheet()
    try:
        return sh.worksheet(name)
    except Exception:
        return sh.add_worksheet(title=name, rows=500, cols=12)


def load_entries() -> pd.DataFrame:
    if get_sheet():
        rows = _ws("entries").get_all_records()
        return pd.DataFrame(rows, columns=ENTRY_COLS) if rows else pd.DataFrame(columns=ENTRY_COLS)
    return pd.read_csv(ENTRIES_CSV) if ENTRIES_CSV.exists() else pd.DataFrame(columns=ENTRY_COLS)


def save_entry(row: list):
    if get_sheet():
        ws = _ws("entries")
        if not ws.get_all_values():
            ws.append_row(ENTRY_COLS)
        ws.append_row(row)
    else:
        df = pd.DataFrame([row], columns=ENTRY_COLS)
        df.to_csv(ENTRIES_CSV, mode="a", header=not ENTRIES_CSV.exists(), index=False)


def default_stats() -> pd.DataFrame:
    df = pd.DataFrame({"player": PLAYERS["player"]})
    for c in STAT_COLS:
        df[c] = 0
    return df


def load_stats() -> pd.DataFrame:
    base = default_stats()
    saved = None
    if get_sheet():
        rows = _ws("stats").get_all_records()
        saved = pd.DataFrame(rows) if rows else None
    elif STATS_CSV.exists():
        saved = pd.read_csv(STATS_CSV)
    if saved is None or saved.empty:
        return base
    merged = base[["player"]].merge(saved, on="player", how="left").fillna(0)
    for c in STAT_COLS:
        merged[c] = merged[c].astype(int)
    return merged[["player"] + STAT_COLS]


def save_stats(df: pd.DataFrame):
    df = df.copy()
    for c in STAT_COLS:
        df[c] = df[c].astype(int)
    if get_sheet():
        ws = _ws("stats")
        ws.clear()
        ws.update([df.columns.tolist()] + df.values.tolist())
    else:
        df.to_csv(STATS_CSV, index=False)


# ---------- UI ----------
st.markdown(hero_html(), unsafe_allow_html=True)
st.caption("Free to play. Not affiliated with the ISL or either club.")

tab_play, tab_board, tab_admin = st.tabs(["Pick your XI", "Leaderboard", "Admin"])

# ===== PLAY =====
with tab_play:
    closed = datetime.now(IST) >= DEADLINE
    if closed:
        st.error("Entries are closed for this match.")
    else:
        st.info(f"Entries close at {DEADLINE.strftime('%I:%M %p')} IST, before kickoff.")

    with st.expander("How it works"):
        st.markdown(
            f"""
- Pick **{SQUAD_SIZE} players** from both squads for **{BUDGET:g} Cr or less**
- Exactly 1 GK, 3 to 5 DEF, 2 to 5 MID, 1 to 3 FWD
- **Max {MAX_PER_TEAM}** players from one team
- Your **captain scores double points**

**Points:** goal (FWD +6, MID +7, DEF/GK +8), assist +4,
clean sheet (GK/DEF +4, MID +1), every 3 saves (GK) +2,
yellow card -1, red card -3, own goal -2, played 60+ minutes +2
"""
        )

    handle = st.text_input("Your Twitter/X handle", placeholder="@yourhandle")

    label_to_player, picked = {}, []
    for pos, title in [("GK", "Goalkeeper (pick 1)"), ("DEF", "Defenders (3 to 5)"),
                       ("MID", "Midfielders (2 to 5)"), ("FWD", "Forwards (1 to 3)")]:
        sub = PLAYERS[PLAYERS["pos"] == pos].sort_values("price", ascending=False)
        labels = []
        for _, r in sub.iterrows():
            dot = "🟠" if r["team"] == GOA else "🔵"
            lab = f"{dot} {r['player']} ({r['price']:g} Cr)"
            label_to_player[lab] = r["player"]
            labels.append(lab)
        sel = st.multiselect(title, labels, key=f"sel_{pos}",
                             max_selections=1 if pos == "GK" else None,
                             placeholder="Tap to choose")
        picked += [label_to_player[s] for s in sel]

    chosen = PLAYERS[PLAYERS["player"].isin(picked)]
    spent = float(chosen["price"].sum()) if len(chosen) else 0.0

    captain = st.selectbox("Captain (2x points)", ["Choose a captain"] + picked)
    captain = None if captain == "Choose a captain" else captain

    st.markdown(tiles_html(len(chosen), spent, SQUAD_SIZE), unsafe_allow_html=True)
    st.markdown(pitch_html(chosen, captain), unsafe_allow_html=True)

    checks = validate(chosen, captain)
    st.markdown(chips_html(checks), unsafe_allow_html=True)

    handle_ok = handle.strip() not in ("", "@")
    if not handle_ok:
        st.caption("Add your handle to submit.")
    all_ok = all(ok for ok, _ in checks) and handle_ok

    if st.button("Lock in my team", type="primary", disabled=closed or not all_ok):
        if datetime.now(IST) >= DEADLINE:  # re-check so a late click can't slip through
            st.error("Entries just closed.")
        else:
            h = handle.strip()
            h = h if h.startswith("@") else "@" + h
            save_entry([datetime.now(IST).isoformat(timespec="seconds"), h, captain,
                        round(spent, 1), "|".join(picked)])
            st.success(f"Team locked in for {h}. You can resubmit before the deadline to change it.")
            st.balloons()

# ===== LEADERBOARD =====
with tab_board:
    if st.button("Refresh scores"):
        st.rerun()
    st.caption(f"Updated {datetime.now(IST).strftime('%I:%M:%S %p')} IST")
    entries = load_entries()
    pts = points_table(load_stats())
    if entries.empty:
        st.write("No teams yet. Be the first to pick your XI.")
    elif not pts or all(v == 0 for v in pts.values()):
        st.write(f"{entries['handle'].str.lower().nunique()} teams entered. Scores appear after the match.")
    else:
        entries = entries.copy()
        entries["key"] = entries["handle"].str.lower()
        entries = entries.sort_values("time").drop_duplicates("key", keep="last")  # latest entry counts
        entries["points"] = [entry_total(str(p).split("|"), c, pts)
                             for p, c in zip(entries["players"], entries["captain"])]
        board = entries.sort_values("points", ascending=False)[["handle", "captain", "points"]]
        board.insert(0, "rank", range(1, len(board) + 1))
        st.dataframe(board, hide_index=True, use_container_width=True)

# ===== ADMIN =====
with tab_admin:
    pw_set = _secret("admin_password")
    if not pw_set:
        st.warning("Set `admin_password` in Streamlit secrets to use this tab.")
    elif st.text_input("Admin password", type="password") == pw_set:
        st.write("Enter match stats per player, then save.")
        edited = st.data_editor(load_stats(), hide_index=True, use_container_width=True, disabled=["player"])
        if st.button("Save stats"):
            save_stats(edited)
            st.success("Stats saved. Leaderboard updated.")
        st.download_button("Download all entries (CSV)", load_entries().to_csv(index=False), "entries.csv")
