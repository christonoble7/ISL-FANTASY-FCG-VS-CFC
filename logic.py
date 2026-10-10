"""Game rules, player prices and scoring for the FC Goa vs Chennaiyin FC fantasy game."""
import pandas as pd

BUDGET = 100.0
SQUAD_SIZE = 11
MAX_PER_TEAM = 7
# position: (min, max) players in the XI
LIMITS = {"GK": (1, 1), "DEF": (3, 5), "MID": (2, 5), "FWD": (1, 3)}

GOA, CFC = "FC Goa", "Chennaiyin FC"

_RAW = [
    # ---- FC Goa ----
    (GOA, "Bob Jackson Raj", "GK", 6.0),
    (GOA, "Lara Sharma", "GK", 5.5),
    (GOA, "Lionel Rymmei", "GK", 5.0),
    (GOA, "Sandesh Jhingan", "DEF", 8.5),
    (GOA, "Alex Zalaya", "DEF", 8.5),
    (GOA, "Ronney Willson", "DEF", 8.0),
    (GOA, "Aakash Sangwan", "DEF", 7.5),
    (GOA, "Saveme Tariang", "DEF", 6.5),
    (GOA, "Nim Dorjee", "DEF", 6.5),
    (GOA, "Sitroy Carvalho", "DEF", 5.5),
    (GOA, "Akash Singh", "DEF", 5.5),
    (GOA, "Rudra Ved", "DEF", 5.0),
    (GOA, "Alexander Vallejo", "MID", 10.5),
    (GOA, "Vellington Fernandes", "MID", 10.0),
    (GOA, "Franchu", "MID", 10.0),
    (GOA, "Udanta Singh", "MID", 9.0),
    (GOA, "Harsh Patre", "MID", 8.5),
    (GOA, "Tomba Singh", "MID", 8.0),
    (GOA, "Prachit Gaonkar", "MID", 6.0),
    (GOA, "Mervin Fernandes", "MID", 6.0),
    (GOA, "Jorge Ortiz", "FWD", 11.5),
    (GOA, "Christian Borrego", "FWD", 11.5),
    (GOA, "Muhammed Nemil", "FWD", 9.5),
    (GOA, "Isak Ralte", "FWD", 8.5),
    (GOA, "Haodamlian Vaiphei", "FWD", 6.5),
    (GOA, "KC Malsawmsanga", "FWD", 6.0),
    # ---- Chennaiyin FC ----
    (CFC, "Mohammad Nawaz", "GK", 6.0),
    (CFC, "Samik Mitra", "GK", 5.5),
    (CFC, "Malhar Mohol", "GK", 5.0),
    (CFC, "Nuno Reis", "DEF", 8.5),
    (CFC, "Emmanuel Imanishimwe", "DEF", 8.0),
    (CFC, "Laldinpuia Pachuau", "DEF", 6.5),
    (CFC, "Namgyal Bhutia", "DEF", 6.0),
    (CFC, "Harmandeep Singh", "DEF", 6.0),
    (CFC, "Saheef Muhammed", "DEF", 6.0),
    (CFC, "Vignesh Dakshinamurthy", "DEF", 5.5),
    (CFC, "Dippendu Biswas", "DEF", 5.0),  # verify: reported move to Mohun Bagan
    (CFC, "Nikola Stojanovic", "MID", 10.5),
    (CFC, "Madih Talal", "MID", 10.0),
    (CFC, "Bryce Miranda", "MID", 8.5),
    (CFC, "Ayush Dev Chhetri", "MID", 8.0),
    (CFC, "Glan Martins", "MID", 7.0),  # verify: reported move to Mohun Bagan
    (CFC, "Klusner Pereira", "MID", 7.0),
    (CFC, "Lalriathpuia Chawngthu", "MID", 6.5),
    (CFC, "Nitishkumar Yengkhom", "MID", 6.5),
    (CFC, "Maheson Tongbram", "MID", 6.0),
    (CFC, "Jiteshwor Singh", "MID", 6.0),
    (CFC, "S Prakadeswaran", "MID", 5.5),
    (CFC, "Ramon Souza", "FWD", 11.5),
    (CFC, "Brison Fernandes", "FWD", 9.5),
    (CFC, "Irfan Yadwad", "FWD", 8.5),
    (CFC, "Vivek S", "FWD", 7.0),
    (CFC, "Shubham Rawat", "FWD", 6.0),
]

# Names to hide from the game (e.g. confirmed departures). Edit this set.
EXCLUDED = set()

PLAYERS = pd.DataFrame(_RAW, columns=["team", "player", "pos", "price"])
PLAYERS = PLAYERS[~PLAYERS["player"].isin(EXCLUDED)].reset_index(drop=True)

STAT_COLS = ["goals", "assists", "clean_sheet", "saves", "yellow", "red", "own_goal", "played_60"]


def validate(selected: pd.DataFrame, captain):
    """Return a list of (ok, message) checks for a chosen XI."""
    checks = []
    n = len(selected)
    checks.append((n == SQUAD_SIZE, f"{n}/{SQUAD_SIZE} players picked"))

    cost = float(selected["price"].sum()) if n else 0.0
    checks.append((cost <= BUDGET + 1e-9, f"Budget: {cost:g} / {BUDGET:g} Cr"))

    for pos, (lo, hi) in LIMITS.items():
        c = int((selected["pos"] == pos).sum()) if n else 0
        rng = f"{lo}" if lo == hi else f"{lo}-{hi}"
        checks.append((lo <= c <= hi, f"{pos}: {c} (need {rng})"))

    for team in (GOA, CFC):
        c = int((selected["team"] == team).sum()) if n else 0
        checks.append((c <= MAX_PER_TEAM, f"{team}: {c} (max {MAX_PER_TEAM})"))

    cap_ok = bool(captain) and n > 0 and captain in set(selected["player"])
    checks.append((cap_ok, "Captain chosen" if cap_ok else "Pick a captain from your XI"))
    return checks


def player_points(pos: str, r) -> int:
    """Fantasy points for one player from a stats row."""
    goal_pts = {"FWD": 6, "MID": 7, "DEF": 8, "GK": 8}[pos]
    pts = r["goals"] * goal_pts + r["assists"] * 4
    if pos in ("GK", "DEF"):
        pts += r["clean_sheet"] * 4
    elif pos == "MID":
        pts += r["clean_sheet"] * 1
    if pos == "GK":
        pts += (r["saves"] // 3) * 2
    pts -= r["yellow"] * 1 + r["red"] * 3 + r["own_goal"] * 2
    pts += r["played_60"] * 2
    return int(pts)


def points_table(stats: pd.DataFrame) -> dict:
    """Map player name -> points. Players missing from stats score 0."""
    out = {}
    pos_map = dict(zip(PLAYERS["player"], PLAYERS["pos"]))
    for _, r in stats.iterrows():
        if r["player"] in pos_map:
            out[r["player"]] = player_points(pos_map[r["player"]], r)
    return out


def entry_total(player_names, captain, pts: dict) -> int:
    """Sum of points, with the captain counted twice."""
    total = sum(pts.get(p, 0) for p in player_names)
    return total + pts.get(captain, 0)
