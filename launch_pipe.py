import json
import time
import random

import arkhn

# Launch timer
start_time = time.time()

# Define config variables
project = 'Crossway'
resource = 'Patient'

# Load data
resource_structure = arkhn.fetcher.get_fhir_resource(project, resource)

# Build the sql query
sql_query, squash_rules, graph = arkhn.parser.build_sql_query(project, resource_structure)
print(sql_query)

# Run it
print('Launching query...')
rows = arkhn.sql.run(sql_query)

# Fix: replace None values with ''
for i, row in enumerate(rows):
    rows[i] = [e if e is not None else '' for e in row ]

print(len(rows), 'results')
# Print cols if you want
# for i, row in enumerate(rows):
#     if i < 10:
#         print(row)


# Apply join rule to merge some lines from the same resource
rows = arkhn.sql.apply_joins(rows, squash_rules)


# Build a fhir object for each resource instance
json_rows = []
for i, row in enumerate(rows):
    if i % 3000 == 0:
        progression = round(i / len(rows) * 100, 2)
        print('PROGRESS... {} %'.format(progression))
    row = list(row)
    # The first node has a different structure so we iterate outside the
    # dfs_create_fhir function
    tree = dict()
    for attr in resource_structure['attributes']:
        arkhn.parser.dfs_create_fhir(tree, attr, row)
    tree, n_leafs = arkhn.parser.clean_fhir(tree)
    tree['id'] = int(random.random() * 10e10)
    tree['resourceType'] = resource
    json_rows.append(tree)
    # print(json.dumps(tree, indent=2, ensure_ascii=False))

# Uncomment to write to file
arkhn.parser.write_to_file(json_rows, 'fhir_data/samples.json')

print(round((time.time() - start_time), 2), 'seconds')
