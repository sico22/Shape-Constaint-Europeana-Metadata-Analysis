import rdflib
import pandas as pd
import os

DATA_PATH = "data/harvested/merged.ttl"
OUTPUT_CSV = "results/sparql_metrics.csv"

os.makedirs("results", exist_ok=True)

def run_query(g, q):
    """Run a SPARQL query and return results as Python list."""
    return list(g.query(q))

def count_query(g, q):
    """Return a single COUNT(*) result."""
    try:
        return int(list(g.query(q))[0][0])
    except:
        return 0

PREFIXES = """
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX edm: <http://www.europeana.eu/schemas/edm/>
    PREFIX ore: <http://www.openarchives.org/ore/terms/>
"""

def compute_sparql_metrics():

    print("Loading merged RDF...")
    g = rdflib.Graph()
    g.parse(DATA_PATH, format="turtle")
    print("Graph loaded with", len(g), "triples")

    metrics = {}

    COMPLETENESS_QUERIES = {
        "missing_title": PREFIXES + """
            SELECT (COUNT(*) AS ?count) WHERE {
                ?proxy edm:europeanaProxy "false" .
                FILTER NOT EXISTS { ?proxy dc:title ?t }
            }
        """,

        "missing_creator": PREFIXES + """
            SELECT (COUNT(*) AS ?count) WHERE {
                ?proxy edm:europeanaProxy "false" .
                FILTER NOT EXISTS { ?proxy dc:creator ?c }
            }
        """,

        "missing_description": PREFIXES + """
            SELECT (COUNT(*) AS ?count) WHERE {
                ?proxy edm:europeanaProxy "false" .
                FILTER NOT EXISTS { ?proxy dc:description ?d }
            }
        """,

        "missing_language": PREFIXES + """
            SELECT (COUNT(*) AS ?count) WHERE {
                ?proxy edm:europeanaProxy "false" .
                FILTER NOT EXISTS { ?proxy dc:language ?lang }
            }
        """,

        "missing_rights": PREFIXES + """
            SELECT (COUNT(*) AS ?count) WHERE {
                ?proxy edm:europeanaProxy "false" .
                FILTER NOT EXISTS { ?proxy edm:rights ?r }
            }
        """,

        "missing_isShownBy": PREFIXES + """
            SELECT (COUNT(*) AS ?count) WHERE {
                ?proxy edm:europeanaProxy "false" .
                FILTER NOT EXISTS { ?proxy edm:isShownBy ?img }
            }
        """,

        "missing_aggregation": PREFIXES + """
            SELECT (COUNT(*) AS ?count) WHERE {
                ?cho a edm:ProvidedCHO .
                FILTER NOT EXISTS { ?agg edm:aggregatedCHO ?cho }
            }
        """
    }

    print("\nComputing completeness metrics...")
    for name, query in COMPLETENESS_QUERIES.items():
        metrics[name] = count_query(g, query)
        print(f"{name}: {metrics[name]}")

    CONSISTENCY_QUERIES = {
        "invalid_language_codes": PREFIXES + """
            SELECT (COUNT(*) AS ?count) WHERE {
                ?proxy edm:europeanaProxy "false" .
                ?proxy dc:language ?lang .
                FILTER (!REGEX(?lang, "^[a-z]{2}$"))
            }
        """,

        "invalid_rights_uris": PREFIXES + """
            SELECT (COUNT(*) AS ?count) WHERE {
                ?proxy edm:europeanaProxy "false" .
                ?proxy edm:rights ?rights .
                FILTER (!STRSTARTS(STR(?rights), "http"))
            }
        """,

        "nonstandard_dc_type": PREFIXES + """
            SELECT (COUNT(*) AS ?count) WHERE {
                ?proxy edm:europeanaProxy "false" .
                ?proxy dc:type ?type .
                FILTER (?type NOT IN ("IMAGE", "TEXT", "VIDEO", "SOUND"))
            }
        """
    }

    print("\nComputing consistency metrics...")
    for name, query in CONSISTENCY_QUERIES.items():
        metrics[name] = count_query(g, query)
        print(f"{name}: {metrics[name]}")

    print("\nComputing frequency statistics...")

    STAT_QUERIES = {
        "languages_distribution": PREFIXES + """
            SELECT ?lang (COUNT(*) AS ?count)
            WHERE { 
                ?proxy edm:europeanaProxy "false" .
                ?proxy dc:language ?lang .
            }
            GROUP BY ?lang
        """,

        "countries_distribution": PREFIXES + """
            SELECT ?c (COUNT(*) AS ?count)
            WHERE { 
                ?proxy edm:europeanaProxy "false" .
                ?proxy edm:country ?c .
            }
            GROUP BY ?c
        """,

        "providers_distribution": PREFIXES + """
            SELECT ?p (COUNT(*) AS ?count)
            WHERE { 
                ?proxy edm:europeanaProxy "false" .
                ?proxy edm:provider ?p .
            }
            GROUP BY ?p
        """,

        "years_distribution": PREFIXES + """
            SELECT ?y (COUNT(*) AS ?count)
            WHERE { 
                ?proxy edm:europeanaProxy "false" .
                ?proxy dc:date ?y .
            }
            GROUP BY ?y
        """
    }

    for name, q in STAT_QUERIES.items():
        rows = run_query(g, q)
        metrics[name] = {str(row[0]): int(row[1]) for row in rows}
        print(f"{name}: {len(rows)} entries")

    flat = []
    for k, v in metrics.items():
        if isinstance(v, dict):
            for key, val in v.items():
                flat.append({"metric": f"{k}:{key}", "value": val})
        else:
            flat.append({"metric": k, "value": v})

    df = pd.DataFrame(flat)
    df.to_csv(OUTPUT_CSV, index=False)
    print("\nSaved SPARQL metrics to:", OUTPUT_CSV)


if __name__ == "__main__":
    compute_sparql_metrics()
