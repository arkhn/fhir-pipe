import time
import numpy as np
import multiprocessing as mp

import fhirpipe_clean

from fhirpipe_clean import set_global_config
from fhirpipe_clean.config import Config

from fhirpipe_clean.extract.mapping import get_resources, prune_fhir_resource
from fhirpipe_clean.extract.mapping import get_identifier_table
from fhirpipe_clean.extract.sql import find_cols_and_joins, build_sql_query, build_squash_rules, run_sql_query
from fhirpipe_clean.transform.transform import squash_rows, create_fhir_object

import logging

if __name__ == "__main__":
  logging.basicConfig(filename='fhirpipe.log', level=logging.INFO)

  project = "Mimic"
  mock_pyrog_mapping = "test/integration/fixtures/graphql_mimic.json"

  set_global_config(Config(path="config.yml"))

  print("testing")

  resources = get_resources(project, from_file=mock_pyrog_mapping)
  print("resources: ", [r["name"] for r in resources])

  # Load mapping rules
  resource_structure = [r for r in resources if r["name"] == "Patient"][0]

  print(len(resource_structure["attributes"]))
  resource_structure = prune_fhir_resource(resource_structure)
  print(len(resource_structure["attributes"]))

  # Get main table
  main_table = get_identifier_table(resource_structure)
  print("main_table", main_table)

  # Extract cols and joins
  cols, joins = find_cols_and_joins(resource_structure)

  # Build the sql query
  sql_query = build_sql_query(cols, joins, main_table)
  print(sql_query)

  # Build squash rules
  squash_rules = build_squash_rules(cols, joins, main_table)

  # Run the sql query
  print("Launching query...")
  df = run_sql_query(sql_query)
  #for row in rows[10:30]:
  #  print(row)
  print("Before squash: ", len(df))

  # Apply join rule to merge some lines from the same resource
  print("Squashing rows...")
  start = time.time()
  df = squash_rows(df, squash_rules)
  for row in df[10:30]:
   print(row)
  print("After squash: ", len(df))
  print("squash duration: ", time.time() - start)
  print(df)

  start = time.time()

  def create_resource(chunk):
    res = []
    for _, row in chunk.iterrows():
      res.append(create_fhir_object(row, resource_structure, "Patient"))
    return res
  
  n_workers = mp.cpu_count()
  pool = mp.Pool(n_workers)
  fhir_objects_chunks = pool.map(create_resource, np.array_split(df, n_workers))
  pool.close()
  pool.join()

  for o in fhir_objects_chunks[0][:5]:
    print(o)
  print(len(fhir_objects_chunks[0]))
  
  print("obj creation duration: ", time.time() - start)

  # Save instances in fhirstore
  # print("Saving in fhirstore...")
  # for fhir_objects in fhir_objects_chunks:
  #   save_many(fhir_objects)

  # print(round((time.time() - start_time), 2), "seconds\n", flush=True)