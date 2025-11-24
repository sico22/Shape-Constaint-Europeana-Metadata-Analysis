import requests
import json
import os

API_KEY = "oryelediovat"
OUTPUT_PATH = os.path.join("data", "harvested", "record_ids.json")

def harvest_records(rows=200):
    if API_KEY is None:
        raise ValueError("Please set the EUROPEANA_API_KEY environment variable.")

    query = "title:*"

    url = "https://api.europeana.eu/record/v2/search.json"
    params = {
        "query": query,
        "rows": rows,
        "profile": "rich",
        "wskey": API_KEY
    }

    print("Fetching record list from Europeana…")
    resp = requests.get(url, params=params)

    if resp.status_code != 200:
        raise RuntimeError(f"Europeana API error: {resp.status_code} - {resp.text}")

    data = resp.json()

    if "items" not in data:
        raise RuntimeError("Unexpected Europeana API response structure.")

    record_ids = [item["id"].lstrip("/") for item in data["items"]]

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(record_ids, f, indent=2)

    print(f"Saved {len(record_ids)} image record IDs to {OUTPUT_PATH}")

if __name__ == "__main__":
    harvest_records(200)