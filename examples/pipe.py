import json
import time
import random

import arkhn

# Launch timer
start_time = time.time()

# Define config variables
project = 'CW'
resource = 'patient'

# Load data
data = arkhn.loader.load(project, resource)
patient = data['fhir']
info = data['info']

# Build the sql query
sql_query, squash_rules, graph = arkhn.parser.build_sql_query(project, patient, info)
print(sql_query)

# Remove owner with MIMIC
sql_query = sql_query.replace('ICSF.', '')

# Run it
print('Launching query...')
rows = arkhn.sql.run(sql_query)

# Fix: replace None values with ''
non_none_rows = []
for row in rows:
    el_list = list(map(lambda x: x if x is not None else '', row))
    non_none_rows.append(el_list)
rows = non_none_rows

print(len(rows), 'results')
# Print cols if you want
# for i, row in enumerate(rows):
#     if i < 10:
#         print(row)


# Apply join rule to merge some lines fomr the same resource
rows = arkhn.sql.apply_joins(rows, squash_rules)


# Build a fhir object for each resource instance
json_rows = []
for i, row in enumerate(rows):
    if i % 3000 == 0:
        progression = round(i / len(rows) * 100, 2)
        print('PROGRESS... {} %'.format(progression))
    row = list(row)
    tree = arkhn.parser.dfs_create_fhir(project, patient, row)
    tree, n_leafs = arkhn.parser.clean_fhir(tree)
    tree['id'] = int(random.random() * 10e10)
    json_rows.append(tree)
    # print('Entity with', n_leafs, 'elems')
    # print(json.dumps(tree, indent=2, ensure_ascii=False))

# Uncomment to write to file
arkhn.parser.write_to_file(json_rows, 'fhir_data/samples.json')

print(round((time.time() - start_time), 2), 'seconds')
