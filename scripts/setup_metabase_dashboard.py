"""Idempotent script to setup unified Metabase Dashboard with all 4 sample charts."""

from pathlib import Path
import os
import requests
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

url = os.getenv("METABASE_SITE_URL", "http://localhost:3000").rstrip("/")
username = os.getenv("METABASE_USERNAME", "")
password = os.getenv("METABASE_PASSWORD", "")

session = requests.Session()
login_res = session.post(f"{url}/api/session", json={"username": username, "password": password})
if not login_res.ok:
    print(f"Login to Metabase failed: {login_res.text}")
    exit(1)

token = login_res.json()["id"]
headers = {"X-Metabase-Session": token, "Content-Type": "application/json"}

# 1. Enable static embedding globally in Metabase
session.put(f"{url}/api/setting/enable-embedding-static", headers=headers, json={"value": True})

# 2. Enable embedding on individual sample cards (ID 40, 41, 42, 43)
for card_id in [40, 41, 42, 43]:
    session.put(
        f"{url}/api/card/{card_id}",
        headers=headers,
        json={"enable_embedding": True, "embedding_type": "signed"},
    )

# 3. Find or Create Dashboard: "Dashboard Indikator Strategis Publik"
dash_name = "Dashboard Indikator Strategis Publik"
dash_list = session.get(f"{url}/api/dashboard", headers=headers).json()
existing_dash = next((d for d in dash_list if d.get("name") == dash_name), None)

if existing_dash:
    dash_id = existing_dash["id"]
else:
    create_res = session.post(
        f"{url}/api/dashboard",
        headers=headers,
        json={
            "name": dash_name,
            "description": "Visualisasi terpadu indikator makro ekonomi, fiskal, dan kesejahteraan sosial.",
        },
    )
    dash_id = create_res.json()["id"]

# Enable embedding for the dashboard
session.put(
    f"{url}/api/dashboard/{dash_id}",
    headers=headers,
    json={
        "name": dash_name,
        "description": "Visualisasi terpadu indikator makro ekonomi, fiskal, dan kesejahteraan sosial.",
        "enable_embedding": True,
        "embedding_type": "signed",
    },
)

# 4. Populate 4 cards with balanced grid layout (24 columns total width)
cards_payload = {
    "cards": [
        {
            "id": -1,
            "card_id": 43,  # Angka Kemiskinan (Scalar/KPI)
            "row": 0,
            "col": 0,
            "size_x": 6,
            "size_y": 6,
            "series": [],
            "visualization_settings": {},
            "parameter_mappings": [],
        },
        {
            "id": -2,
            "card_id": 40,  # Tren Inflasi Bulanan (Line Chart)
            "row": 0,
            "col": 6,
            "size_x": 18,
            "size_y": 6,
            "series": [],
            "visualization_settings": {},
            "parameter_mappings": [],
        },
        {
            "id": -3,
            "card_id": 41,  # Realisasi PAD per Bakorwil (Bar Chart)
            "row": 6,
            "col": 0,
            "size_x": 12,
            "size_y": 8,
            "series": [],
            "visualization_settings": {},
            "parameter_mappings": [],
        },
        {
            "id": -4,
            "card_id": 42,  # Komposisi PDRB Sektoral (Pie Chart)
            "row": 6,
            "col": 12,
            "size_x": 12,
            "size_y": 8,
            "series": [],
            "visualization_settings": {},
            "parameter_mappings": [],
        },
    ]
}

session.put(f"{url}/api/dashboard/{dash_id}/cards", headers=headers, json=cards_payload)

# Verify
final_dash = session.get(f"{url}/api/dashboard/{dash_id}", headers=headers).json()
print(f"Metabase Dashboard successfully configured! ID: {dash_id}, Name: '{dash_name}'")
print(f"Dashboard URL: {url}/dashboard/{dash_id}")
