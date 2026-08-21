import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "buyers.db"

# Synthetic but geographically realistic buyer/industry facilities across
# major sugarcane-producing states. In production this table would be
# populated from a real registry of mills, distilleries, paper plants and
# CBG/biogas plants (lat/lon geocoded).
SEED_BUYERS = [
    # name, industry_key, state, lat, lon, capacity_tons_per_day
    ("Renuka Cogen Plant",        "cogeneration",       "Maharashtra",   19.9975, 73.7898, 500),
    ("Godavari Biorefineries",    "cogeneration",       "Maharashtra",   18.9333, 74.9167, 450),
    ("Bajaj Hindusthan Cogen",    "cogeneration",       "Uttar Pradesh", 27.8974, 78.0880, 600),
    ("Triveni Engineering Cogen", "cogeneration",       "Uttar Pradesh", 29.3462, 79.4159, 400),
    ("EID Parry Cogen",           "cogeneration",       "Tamil Nadu",    11.6643, 78.1460, 350),
    ("KCP Sugar Cogen",           "cogeneration",       "Andhra Pradesh",16.5062, 80.6480, 300),

    ("Bannari Amman Paper Mills", "paper_pulp",         "Tamil Nadu",    11.4064, 77.7180, 250),
    ("Seshasayee Paper & Boards", "paper_pulp",          "Tamil Nadu",   11.3410, 77.7172, 300),
    ("West Coast Paper Mills",    "paper_pulp",          "Karnataka",    15.3647, 75.1240, 280),
    ("Star Paper Mills",          "paper_pulp",          "Uttar Pradesh",29.9457, 79.2890, 220),
    ("Ballarpur Industries",      "paper_pulp",          "Maharashtra",  19.8480, 79.3540, 260),

    ("Praj Ethanol Plant",        "ethanol_distillery", "Maharashtra",   18.5204, 73.8567, 200),
    ("Balrampur Chini Distillery","ethanol_distillery", "Uttar Pradesh", 27.4297, 82.1830, 250),
    ("Bannari Amman Distillery",  "ethanol_distillery", "Tamil Nadu",    11.1085, 77.3411, 180),
    ("Shree Renuka Distillery",   "ethanol_distillery", "Karnataka",     16.8302, 74.5090, 220),
    ("Dhampur Sugar Distillery",  "ethanol_distillery", "Uttar Pradesh", 29.3110, 78.5140, 190),
    ("Rajshree Sugars Distillery","ethanol_distillery", "Tamil Nadu",    10.7905, 77.1400, 150),

    ("Nova Biogas Plant",         "biogas_cbg",         "Maharashtra",   19.2183, 72.9781, 60),
    ("Adani CBG Plant",           "biogas_cbg",         "Gujarat",       22.4707, 70.0577, 90),
    ("Indian Oil CBG Unit",       "biogas_cbg",         "Uttar Pradesh", 26.8467, 80.9462, 80),
    ("Punjab Biogas Cooperative", "biogas_cbg",         "Punjab",        30.9010, 75.8573, 55),
    ("TN Agro Biogas Plant",      "biogas_cbg",         "Tamil Nadu",    10.9601, 78.0766, 50),
    ("Karnataka CBG Facility",    "biogas_cbg",         "Karnataka",     15.8497, 74.4977, 65),
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS buyers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            industry_key TEXT NOT NULL,
            state TEXT,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            capacity_tons_per_day REAL
        )
    """)
    cur.execute("SELECT COUNT(*) FROM buyers")
    count = cur.fetchone()[0]
    if count == 0:
        cur.executemany(
            "INSERT INTO buyers (name, industry_key, state, lat, lon, capacity_tons_per_day) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            SEED_BUYERS,
        )
        conn.commit()
    conn.close()


def get_buyers_by_industry(industry_key: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM buyers WHERE industry_key = ?", (industry_key,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_all_buyers():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM buyers")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
