from uuid import uuid4
import logging
import numpy as np
from collections import defaultdict

from fhirpipe.utils import build_col_name, new_col_name


def recursive_defaultdict():
    return defaultdict(recursive_defaultdict)


def create_resource(chunk, resource_mapping):
    res = []
    for _, row in chunk.iterrows():
        try:
            res.append(create_instance(row, resource_mapping))
        except Exception as e:
            assert False
            # If cannot build the fhir object, a warning has been logged
            # and we try to generate the next one
            logging.error(f"create_instance failed with: {e}")
            continue

    return res


def create_instance(row, mapping):
    # Modify the data structure so that it is easier to use
    path_attributes_map = {attr["path"]: attr for attr in mapping["attributes"]}

    # Build path value map
    fhir_object = build_fhir_object(row, path_attributes_map)

    # Identify the fhir object
    fhir_object["id"] = str(uuid4())
    fhir_object["resourceType"] = mapping["definition"]["type"]

    # Remove duplicates in fhir object
    fhir_object = clean_fhir_object(fhir_object)

    return fhir_object


def build_fhir_object(row, path_attributes_map, index=None):
    fhir_object = recursive_defaultdict()
    arrays_done = set()

    for path, attr in path_attributes_map.items():
        if attr["inputs"]:

            split_path = path.split(".")
            position_ind = get_position_first_index(split_path)

            if position_ind is None:
                val = fetch_values_from_dataframe(row, attr["inputs"], attr["mergingScript"])
                if isinstance(val, tuple):
                    if len(val) == 1:
                        insert_in_fhir_object(fhir_object, path, val[0])
                    elif index is not None:
                        insert_in_fhir_object(fhir_object, path, val[index])
                    else:
                        insert_in_fhir_object(fhir_object, path, val)
                else:
                    insert_in_fhir_object(fhir_object, path, val)

            else:
                # Handle array case
                array_path = ".".join(split_path[: position_ind + 1])
                if array_path in arrays_done:
                    continue
                attributes_in_array = {
                    remove_root_path(path, position_ind + 1): attr
                    for path, attr in path_attributes_map.items()
                    if path.startswith(array_path)
                }
                array = handle_array_attributes(attributes_in_array, row)
                if array:
                    insert_in_fhir_object(fhir_object, ".".join(split_path[: position_ind]), array)
                arrays_done.add(array_path)

    return fhir_object


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


def handle_array_attributes(attributes_in_array, row):
    # Check lengths
    length = 1
    for attr in attributes_in_array.values():
        val = fetch_values_from_dataframe(row, attr["inputs"], attr["mergingScript"])
        if not isinstance(val, tuple) or len(val) == 1:
            continue
        assert length == 1 or len(val) == length, "mismatch in array lengths"
        length = len(val)

    array = []
    for index in range(length):
        element = build_fhir_object(row, attributes_in_array, index=index)
        if element:
            array.append(element)

    return array


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


def insert_in_fhir_object(fhir_object, path, value):
    if isinstance(value, tuple):
        assert all(
            [v == value[0] for v in value]
        ), "Trying to insert several different values in a non-list attribute"
        val = value[0]
    elif isinstance(value, list) or value is not None:
        val = value
    else:
        return

    cur_location = fhir_object
    path = path.split(".")
    for step in path[:-1]:
        cur_location = cur_location[step]

    if isinstance(val, list):
        if path[-1] not in cur_location:
            cur_location[path[-1]] = []
        cur_location[path[-1]].extend(val)
    else:
        cur_location[path[-1]] = val


def get_position_first_index(path):
    for i, step in enumerate(path):
        if step.isdigit():
            return i


def remove_root_path(path, index_end_root):
    split_path = path.split(".")[index_end_root:]
    return ".".join(split_path)
