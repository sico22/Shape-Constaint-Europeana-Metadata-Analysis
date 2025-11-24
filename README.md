
This project contains a pipeline for validating metadata records from the **Europeana Search API** against a custom **SHACL shape**. It evaluates the metadata and classifies it into tiers that can be visualized in the final CSV report.

## Pipeline
- Harvest record identifiers from Europeana Search API
- Download RDF metadata for each record
- Merge all RDF files into a single RDF graph
- Validate metadata using **pySHACL** with a custom SHACL shape
- Compute per-record metadata completeness tiers
- Produce a final CSV report for analysis

## Repository Structure
```
project/
│
├── scripts/
│   ├── harvest.py          # Extract record IDs from Europeana
│   ├── fetch_rdf.py        # Download RDF/XML for each record
│   ├── merge_graph.py      # Merge RDF files into one graph
│   └── validate.py         # Run SHACL validation and scoring
│
├── shapes/
│   └── europeana_shapes.ttl   # SHACL schema used for validation
│
├── data/
│   ├── harvested/
│   │   ├── record_ids.json   # Saved by harvest.py
│   │   ├── rdf/              # Raw RDF files downloaded
│   │   └── merged.ttl        # Final merged graph
│
└── results/
    └── validation_results.csv # Final report

```

## Requirements
- Python 3.10+ recommended
- Dependencies:
	-  `rdflib`
	- `pyshacl`
    - `requests`
    - `pandas`

## Instructions for running the evaluation
You must replace "YOUR_API_KEY_HERE" in `scripts/harvest/py` and `scripts/fetch_rdf.py` with your own Europeana API key. The key can be obtained by accessing this [link](https://apis.europeana.eu/en?gad_source=1&gad_campaignid=23090780840&gbraid=0AAAABBof25v88Sj-Rok0bFESDHgbLKWWz&gclid=CjwKCAiA24XJBhBXEiwAXElO3yWUQnrPbZS3Ofotf2RNKsj8AtMKW_Kux4xjisgBpQW5BcJBaxDxfhoChl4QAvD_BwE)

1. Harvest record IDs
	- Queries the Europeana Search API and saves the record identifiers to `data/harvested/record_ids.json`
```shell
python scripts/harvest.py
```
2. Fetch RDF metadata
	- Downloads RDF/XML for each record ID and stores them in `data/harvested/rdf/`
	- Files are saved as `{record_id}.rdf`
```shell
python scripts/fetch_rdf.py
```
3. Merge all RDF into a single graph
	- Merges all RDF/XML files into one Turtle file
	- The output can be found in `data/harvested/merged.ttl`
```shell
python scripts/merge_graph.py
```
4. Validate using SHACL
	- Runs pySHACL against `merged.ttl` using the shape defined in `shapes/europeana_shapes.ttl`
	- It also computes metadata completeness tiers based on:
		- Provider Proxy metadata (title, creator, description, language, type, year)
		- Aggregation metadata (dataProvider, provider, country, rights, isShownBy)
	- results can be found at `results/validation_results.csv`
```shell
python scripts/validate.py
```

## Results
The `results/validation_results.csv` contains the validation result in the following format:

|Field|Meaning|
|---|---|
|**record_uri**|URI of the Europeana Provider Proxy|
|**filled_fields**|Number of mandatory fields present|
|**total_fields**|Maximum possible fields|
|**tier**|Metadata quality tier (1–4)|
|**missing_fields**|Human-readable list|
### Tier interpretation
|Tier|Meaning|
|---|---|
|**Tier 1**|≥ 75% required metadata present|
|**Tier 2**|50–74%|
|**Tier 3**|25–49%|
|**Tier 4**|< 25%|
