
This project contains a pipeline for validating metadata records from the **Europeana Search API** using **SPARQL** and **SHACL**. 

**Table of Contents:**
- [[#Pipeline|Pipeline]]
- [[#Repository Structure|Repository Structure]]
- [[#Requirements|Requirements]]
- [[#Instructions for running the evaluation|Instructions for running the evaluation]]
- [[#Results|Results]]
	- [[#Results#Tier interpretation|Tier interpretation]]
	- [[#Results#Aggregate SPARQL metrics|Aggregate SPARQL metrics]]


## Pipeline
- Harvest record identifiers from Europeana Search API using **parameterized queries**
- Download RDF metadata for each record
- Merge all RDF files into a single RDF graph
- Validate metadata using **pySHACL** with a custom SHACL shape and compute record-level completeness tiers
- Compute **SPARQL**-based metadata quality metrics 
- Produce a CSV report for each analysis
All steps can be executed through a single command.

## Repository Structure
```
project/
│
├── scripts/
│   ├── harvest.py          # Extract record IDs from Europeana
│   ├── fetch_rdf.py        # Download RDF/XML for each record
│   ├── merge_graph.py      # Merge RDF files into one graph
│   ├── sparql_metrics.py   # Compute SPARQL metadata quality metrics
│   └── validate.py         # Run SHACL validation and scoring
│   └── run_all.py          # Run the full pipeline
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
    ├── validation_results.csv # Final report
    └── sparql_metrics.csv     # Aggregate SPARQL metrics
```

## Requirements
- Python 3.10+ recommended
- A valid Europeana API key
- Dependencies:
	-  `rdflib`
	- `pyshacl`
    - `requests`
    - `pandas`

## Instructions for running the evaluation
Set your Europeana AI key as an environment variable. The key can be obtained by accessing this [link](https://apis.europeana.eu/en?gad_source=1&gad_campaignid=23090780840&gbraid=0AAAABBof25v88Sj-Rok0bFESDHgbLKWWz&gclid=CjwKCAiA24XJBhBXEiwAXElO3yWUQnrPbZS3Ofotf2RNKsj8AtMKW_Kux4xjisgBpQW5BcJBaxDxfhoChl4QAvD_BwE)
``` shell
setx EUROPEANA_API_KEY "YOUR_API_KEY_HERE"
```
**Evaluation can be carried out by running individually each step, or by running the run_all.py using the following command:**
```
py scripts/run_all.py -f title -v map -r 200
```
The previous command automatically runs all of the scripts presented below:
1. Harvest record IDs
	- Queries the Europeana Search API and saves the record identifiers to `data/harvested/record_ids.json`
	- Supported query fields include:
		- `title`
		- `subject`
		- `creator`
		- `provider`
		- `country`
		- `type`
Example for a title-based query:
```shell
py scripts/harvest.py -f title -v map -r 200
```

Example for a subject based quey:
```
python scripts/harvest.py -f subject -v archaeology -r 200
```
2. Fetch RDF metadata
	- Downloads RDF/XML for each record ID and stores them in `data/harvested/rdf/`
	- Files are saved as `{record_id}.rdf`
```shell
py scripts/fetch_rdf.py
```
3. Merge all RDF into a single graph
	- Merges all RDF/XML files into one Turtle file
	- The output can be found in `data/harvested/merged.ttl`
```shell
py scripts/merge_graph.py
```
4. Validate using SHACL
	- Runs pySHACL against `merged.ttl` using the shape defined in `shapes/europeana_shapes.ttl`
	- It also computes metadata completeness tiers based on:
		- Provider Proxy metadata (title, creator, description, language, type, year)
		- Aggregation metadata (dataProvider, provider, country, rights, isShownBy)
	- results can be found at `results/validation_results.csv`
```shell
py scripts/validate.py
```
5. Compute SPARQL metadata quality metrics
	- Computes completeness, consistency, and distribution statistics
	- Saves results to `results/sparql_metrics.csv`
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
### Aggregate SPARQL metrics
The file `results/sparql_metrics.csv` contains aggregate metadata quality metrics computed using SPARQL queries such as:
- Missing mandatory fields
- Consistency violations (e.g., invalid language codes,)
- Distributions by language, provider, country, and year