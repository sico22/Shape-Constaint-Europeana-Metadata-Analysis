import os
from rdflib import Graph, URIRef

RDF_DIR = os.path.join("data", "harvested", "rdf")
OUTPUT_FILE = os.path.join("data", "harvested", "merged.ttl")

def clean_uri(uri):
    """Remove illegal whitespace from URIs."""
    if isinstance(uri, URIRef):
        cleaned = uri.strip()
        if cleaned != uri:
            return URIRef(cleaned)
    return uri

def merge_rdf():
    g = Graph()

    rdf_files = [f for f in os.listdir(RDF_DIR) if f.endswith(".rdf")]
    print(f"Merging {len(rdf_files)} RDF files into a single graph…")

    for fname in rdf_files:
        path = os.path.join(RDF_DIR, fname)
        try:
            g.parse(path)
            print(f"[OK] added {fname}")
        except Exception as e:
            print(f"[ERROR] could not parse {fname}: {e}")

    print("\n🔧 Cleaning malformed URIs…")

    cleaned_graph = Graph()
    count_fixed = 0

    for s, p, o in g:
        new_s = clean_uri(s)
        new_p = clean_uri(p)
        new_o = clean_uri(o)

        if (new_s != s or new_p != p or new_o != o):
            count_fixed += 1

        cleaned_graph.add((new_s, new_p, new_o))

    print(f"Fixed {count_fixed} malformed URIs")

    print(f"\nSerializing merged graph to {OUTPUT_FILE} …")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    cleaned_graph.serialize(OUTPUT_FILE, format="turtle")

    print("Done. Graph saved safely.")

if __name__ == "__main__":
    merge_rdf()
