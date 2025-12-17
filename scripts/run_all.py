import subprocess
import argparse
import sys

def run_step(description, command):
    print("\n" + "="*60)
    print(f"STEP: {description}")
    print("="*60)

    print(f"Running: {command}")
    process = subprocess.run(command, shell=True)

    if process.returncode != 0:
        print(f"\nERROR: Step '{description}' failed.")
        sys.exit(1)

    print(f"Completed: {description}")


def main(field, value, rows):
    # 1. Harvest
    run_step(
        "Harvesting record IDs",
        f'py harvest.py -f {field} -v "{value}" -r {rows}'
    )

    # 2. Fetch RDF files
    run_step(
        "Fetching RDF files",
        "py fetch_rdf.py"
    )

    # 3. Merge RDF
    run_step(
        "Merging RDF files",
        "py merge_graph.py"
    )

    # 4. Validate metadata and compute tiers
    run_step(
        "Running SHACL validation + metadata completeness",
        "py validate.py"
    )

    # 5. SPARQL evaluation
    run_step(
        "SPARQL metadata quality metrics",
        "py sparql_metrics.py"
    )


    print("\nALL STEPS COMPLETED SUCCESSFULLY!\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run full metadata quality workflow.")

    parser.add_argument(
        "-f", "--field",
        required=True,
        help="Metadata field to query (title, subject, creator, provider, type, country)."  
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
        help="Number of records to request from Europeana."
    )

    args = parser.parse_args()

    main(args.field, args.value, args.rows)
