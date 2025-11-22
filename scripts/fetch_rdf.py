import os
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep

API_KEY = "oryelediovat"
INPUT_PATH = os.path.join("data", "harvested", "record_ids.json")
OUTPUT_DIR = os.path.join("data", "harvested", "rdf")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_single_rdf(record_id, retries=3):
    """Download RDF for a single record."""
    safe_id = record_id.replace("/", "_")  
    out_path = os.path.join(OUTPUT_DIR, f"{safe_id}.rdf")

    url = f"https://api.europeana.eu/record/v2/{record_id}.rdf"
    params = {
        "wskey": API_KEY,
        "profile": "rich"
    }



    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
                return f"[OK] {record_id}"

            else:
                error_msg = f"[ERROR {response.status_code}] {record_id}"
                sleep(0.5)
        except Exception as e:
            error_msg = f"[EXCEPTION] {record_id} - {e}"
            sleep(0.5)

    return error_msg


def fetch_all_rdf(max_workers=10):
    if not API_KEY:
        raise ValueError("EUROPEANA_API_KEY is not set.")

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        record_ids = json.load(f)

    print(f"Fetching RDF for {len(record_ids)} records…")

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_single_rdf, rid): rid for rid in record_ids}
        for future in as_completed(futures):
            results.append(future.result())
            print(results[-1]) 

    print("\nDone.")
    return results


if __name__ == "__main__":
    fetch_all_rdf()
