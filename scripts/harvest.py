import requests
import json
import os
import argparse

API_KEY = os.environ.get("EUROPEANA_API_KEY")
OUTPUT_PATH = os.path.join("data", "harvested", "record_ids.json")

QUERY_TEMPLATES = {
    "title": "title:*{value}*",
    "creator": "dc_creator:*{value}*",
    "subject": "dc_subject:*{value}*",
    "provider": 'edm_provider:"{value}"',
    "country": 'edm_country:"{value}"',
    "type": 'TYPE:"{value}"'
}

def harvest_records(field, value, rows=200):
    if API_KEY is None:
        raise ValueError("Please set the EUROPEANA_API_KEY environment variable.")

    if field not in QUERY_TEMPLATES:
        raise ValueError(f"Unsupported query field: {field}")
    
    query = QUERY_TEMPLATES[field].format(value=value)

    url = "https://api.europeana.eu/record/v2/search.json"
    params = {
        "query": query,
        "rows": rows,
        "profile": "rich",
        "wskey": API_KEY
    }

    print(f"Fetching record list from Europeana…\nQuery: {query}\nRows: {rows}")
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
    parser = argparse.ArgumentParser(description="Harvest Europeana record IDs.")

    parser.add_argument(
        "-f", "--field",
        required=True,
        choices=QUERY_TEMPLATES.keys(),
        help="Metadata field to query."
    )

    parser.add_argument(
        "-v", "--value",
        required=True,
        help="Query value."
    )

    parser.add_argument(
        "-r", "--rows",
        type=int,
        default=200,
        help="Maximum number of records to fetch."
    )

    args = parser.parse_args()

    harvest_records(args.field, args.value, args.rows)