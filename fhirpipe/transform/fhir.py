from uuid import uuid4
import logging
import numpy as np

from fhirpipe.utils import build_col_name, new_col_name


def create_resource(chunk, resource_mapping):
    res = []
    for _, row in chunk.iterrows():
        try:
            res.append(create_fhir_object(row, resource_mapping))
        except Exception as e:
            # If cannot build the fhir object, a warning has been logged
            # and we try to generate the next one
            logging.error(f"create_fhir_object failed with: {e}")
            continue
    return res


def create_fhir_object(row, mapping):
    path_value_map = build_path_value_map(row, mapping)

    # Identify the fhir object
    fhir_object = {"id": str(uuid4()), "resourceType": mapping["definition"]["type"]}

    # Fill the object
    for path in sorted(path_value_map):
        fill_fhir_object(fhir_object, path, path_value_map[path])

    # Remove duplicates in fhir object
    fhir_object = clean_fhir_object(fhir_object)

    return fhir_object


def build_path_value_map(row, mapping):
    """ In this funcion, we build a intermediate object which is a map from path to values
    to put in the fhir object.
    The complexity lies in distributing the joined columns (which can now contain several values)
    on different paths.
    For instance, instead of having a path-value:
        {"patient.medication.0.name": (med0, med1, med2)},
    we want
        {
            "patient.medication.0.name": med0,
            "patient.medication.1.name": med1,
            "patient.medication.2.name": med2,
        }
    """
    path_value_map = {}
    for attr in mapping["attributes"]:
        if "inputs" in attr and attr["inputs"]:
            val = fetch_values_from_dataframe(row, attr["inputs"], attr["mergingScript"])
            if isinstance(val, tuple):
                if len(val) == 1:
                    insert_in_map(path_value_map, attr["path"], val[0])
                else:
                    split_path = attr["path"].split(".")
                    position_ind = get_position_last_index(split_path)

                    if position_ind is None:
                        insert_in_map(path_value_map, attr["path"], val)
                        continue

                    split_path[position_ind] = int(split_path[position_ind])
                    for val in val:
                        while ".".join(str(s) for s in split_path) in path_value_map:
                            split_path[position_ind] += 1

                        path = ".".join(str(s) for s in split_path)
                        insert_in_map(path_value_map, path, val)

            else:
                insert_in_map(path_value_map, attr["path"], val)

    return path_value_map


def fetch_values_from_dataframe(row, mapping_inputs, merging_script):
    if len(mapping_inputs) == 1:
        input = mapping_inputs[0]
        if input["sqlValue"]:
            sql = input["sqlValue"]
            column_name = build_col_name(sql["table"], sql["column"], sql["owner"])
            if input["script"]:
                column_name = new_col_name(input["script"], column_name)
            return row[column_name]
        else:
            return input["staticValue"]

    else:
        if not merging_script:
            raise ValueError(
                "You need to provide a merging script for attributes with several inputs."
            )

        cols_to_fetch = ([], [])
        for input in mapping_inputs:
            # Else retrieve the static value
            if input["sqlValue"]:
                sql = input["sqlValue"]
                column_name = build_col_name(sql["table"], sql["column"], sql["owner"])
                if input["script"]:
                    column_name = new_col_name(input["script"], column_name)
                cols_to_fetch[0].append(column_name)

            # Else retrieve the static value
            else:
                cols_to_fetch[1].append(input["staticValue"])

        return row[new_col_name(merging_script, cols_to_fetch)]


def fill_fhir_object(fhir_object, path, value):
    cur_location = fhir_object
    path = path.split(".")
    for i in range(len(path) - 1):
        step = path[i]
        if step.isdigit():
            step = int(step)
            if step >= len(cur_location):
                cur_location.append([] if path[i + 1].isdigit() else {})
        else:
            if step not in cur_location:
                cur_location[step] = [] if path[i + 1].isdigit() else {}
        cur_location = cur_location[step]

    cur_location[path[-1]] = value


def clean_fhir_object(fhir_obj):
    """ Remove duplicate list elements from fhir object
    """
    if isinstance(fhir_obj, dict):
        for key in fhir_obj:
            fhir_obj[key] = clean_fhir_object(fhir_obj[key])
        return fhir_obj

    elif isinstance(fhir_obj, list):
        to_rm = []
        for i in range(len(fhir_obj)):
            for j in range(i + 1, len(fhir_obj)):
                if fhir_obj[i] == fhir_obj[j]:
                    to_rm.append(i)
                    break
        return list(np.delete(fhir_obj, to_rm))

    else:
        return fhir_obj


def get_position_last_index(path):
    for i, step in enumerate(path[::-1]):
        if step.isdigit():
            return len(path) - 1 - i


def insert_in_map(path_value_map, path, val):
    if isinstance(val, tuple):
        assert all(
            [v == val[0] for v in val]
        ), "Trying to insert several different values in a non-list attribute"
        insert_in_map(path_value_map, path, val[0])

    elif val:
        path_value_map[path] = val
