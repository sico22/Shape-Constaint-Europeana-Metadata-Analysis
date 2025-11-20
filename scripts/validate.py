import os
import rdflib
from rdflib import Namespace
from rdflib.namespace import DC, DCTERMS, SKOS
from pyshacl import validate
import pandas as pd

### Paths
DATA_PATH = os.path.join("data", "harvested", "merged.ttl")
SHAPES_PATH = os.path.join("shapes", "europeana_shapes.ttl")
OUTPUT_CSV = os.path.join("results", "validation_results.csv")

os.makedirs("results", exist_ok=True)

### Namespaces
EDM = Namespace("http://www.europeana.eu/schemas/edm/")
ORE = Namespace("http://www.openarchives.org/ore/terms/")

MANDATORY_FIELDS = {
    "title": [DC.title, SKOS.prefLabel],
    "creator": [DC.creator],
    "description": [DC.description],
    "language": [DC.language],
    "type": [DC.type],
    "year": [DC.date, DCTERMS.created],
}

AGG_FIELDS = {
    "dataProvider": EDM.dataProvider,
    "provider": EDM.provider,
    "country": EDM.country,
    "rights": EDM.rights,
    "isShownBy": EDM.isShownBy,
}


def compute_tier(filled, total):
    ratio = filled / total
    if ratio >= 0.75:
        return "Tier 1 (>75%)"
    elif ratio >= 0.50:
        return "Tier 2 (>50%)"
    elif ratio >= 0.25:
        return "Tier 3 (>25%)"
    return "Tier 4 (<25%)"


def main():
    print("Loading RDF...")
    g = rdflib.Graph()
    g.parse(DATA_PATH, format="turtle")

    print("Loading SHACL shapes...")
    sh = rdflib.Graph()
    sh.parse(SHAPES_PATH, format="turtle")

    print("Running SHACL validation...")
    conforms, _, _ = validate(
        g,
        shacl_graph=sh,
        inference="rdfs",
        allow_infos=True,
        allow_warnings=True
    )
    print("SHACL Conforms:", conforms)

    results = []

    print("Computing metadata completeness...")

    for proxy in g.subjects(EDM.europeanaProxy, rdflib.Literal("false")):
        record_uri = str(proxy)

        completeness = {}
        filled = 0
        total = 0

        for field, predicates in MANDATORY_FIELDS.items():
            has_value = False
            for p in predicates:
                if (proxy, p, None) in g:
                    has_value = True
                    break
            completeness[field] = has_value
            filled += has_value
            total += 1

        aggs = list(g.objects(proxy, ORE.proxyIn))
        if aggs:
            agg = aggs[0]
            for field, pred in AGG_FIELDS.items():
                has_value = (agg, pred, None) in g
                completeness[field] = has_value
                filled += has_value
                total += 1
        else:
            for field in AGG_FIELDS:
                completeness[field] = False
                total += 1

        tier = compute_tier(filled, total)

        results.append({
            "record_uri": record_uri,
            "filled_fields": filled,
            "total_fields": total,
            "tier": tier,
            "missing_fields": ", ".join([k for k, v in completeness.items() if not v])
        })

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_CSV, index=False)
    print("Saved:", OUTPUT_CSV)


if __name__ == "__main__":
    main()
