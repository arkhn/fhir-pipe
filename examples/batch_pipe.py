import time
import random
import shutil
import glob

import arkhn

# Launch timer
start_time = time.time()

# Define config variables
database = 'Crossway'
resource = 'Patient'

# Load data
data = arkhn.loader.json.load(database, resource)
patient = data

# Build the sql query
sql_query, squash_rules, graph = arkhn.parser.build_sql_query(database, patient)
print(sql_query)

# Remove owner with MIMIC
# sql_query = sql_query.replace("ICSF.", "")

# Run it
print("Launching query batch per batch...")

batch_size = 100000

offset = arkhn.log.get("pipe.processing.offset", default=0)

for batch_idx, offset, rows in arkhn.sql.batch_run(
    sql_query, batch_size, offset=offset
):
    print("Running batch {} offset {}...".format(batch_idx, offset))
    # Rm None values
    for i, row in enumerate(rows):
        rows[i] = [e if e is not None else "" for e in row]

    # Apply OneToMany joins
    rows = arkhn.sql.apply_joins(rows, squash_rules)

    # Hydrate FHIR objects
    json_rows = []
    for row in rows:
        if i % 1000 == 0:
            progression = round(i / len(rows) * 100, 2)
            print("batch {} %".format(progression))
        tree = dict()
        for a in patient['attributes']:
            arkhn.parser.dfs_create_fhir(tree, a, list(row))
        tree, n_leafs = arkhn.parser.clean_fhir(tree)
        # TODO: think about it
        tree["id"] = int(random.random() * 10e10)
        json_rows.append(tree)

    # Write to file
    arkhn.parser.write_to_file(
        json_rows, "fhir_data/tmp/samples.{}.json".format(offset)
    )

    # Log offset to restart in case of a crash
    arkhn.log.set("pipe.processing.offset", offset)

# Rm tmp
arkhn.log.rm("pipe.processing.offset")

print("Merging batches...", end="")
with open("fhir_data/samples.json", "wb") as merged_file:
    for batch_filename in glob.glob("fhir_data/tmp/samples.*.json"):
        with open(batch_filename, "rb") as batch_file:
            shutil.copyfileobj(batch_file, merged_file)

# TODO rm tmp files

print("done")

print(round((time.time() - start_time), 2), "seconds")
