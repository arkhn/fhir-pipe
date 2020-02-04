from uuid import uuid4
import logging

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


def create_fhir_object(row, resource_mapping):
    # Identify the fhir object
    fhir_object = {"id": str(uuid4()), "resourceType": resource_mapping["fhirType"]}

    # The first node has a different structure so iterate outside the
    # dfs_create_fhir function
    for attr in resource_mapping["attributes"]:
        rec_create_fhir_object(fhir_object, attr, row)

    return fhir_object


def build_fhir_leaf_attribute(structure, row, indices):
    # TODO simplify (for instance, force merging script when several inputs)
    cols_to_fetch = ([], [])
    for inp in structure["inputs"]:

        # If a sql location is provided, then a sql value has been returned
        if inp["sqlValue"]:
            sql = inp["sqlValue"]
            col_name = build_col_name(sql["table"], sql["column"], sql["owner"])
            if inp["script"]:
                # If there is a cleaning script, we fetch the value in the cleaned column
                col_name = new_col_name(inp["script"], col_name)
            cols_to_fetch[0].append(col_name)

        # Else retrieve the static value
        else:
            cols_to_fetch[1].append(inp["staticValue"])

    if structure["mergingScript"]:
        result = row[new_col_name(structure["mergingScript"], cols_to_fetch)]
    else:
        result = [row[c] for c in cols_to_fetch[0]]
        result.extend(cols_to_fetch[1])

    # Unlist
    if isinstance(result, list) and len(result) == 1:
        result = result[0]

    if isinstance(result, tuple):
        for ind in indices:
            result = result[ind]

    if isinstance(result, tuple):
        if not all([el == result[0] for el in result[1:]]):
            raise Exception(f"Cannot have as input a list with different values ({result}).")
        result = result[0]

    return result


def rec_create_fhir_object(fhir_obj, structure, row, indices=[]):
    if isinstance(structure, dict):
        # If there are some inputs, we can build the objects to output
        if "inputs" in structure.keys() and structure["inputs"]:
            result = build_fhir_leaf_attribute(structure, row, indices)
            fhir_obj[structure["name"]] = result

        # Otherwise, we can recurse on children
        else:
            is_array = structure["fhirType"] == "array"

            fhir_obj[structure["name"]] = [] if is_array else dict()

            for attr in structure["children"]:
                if is_array:
                    create_fhir_list(fhir_obj, attr, structure["name"], row, indices)
                else:
                    rec_create_fhir_object(fhir_obj[structure["name"]], attr, row, indices)

    # If the current object is a list, we can repeat the same steps as above for each item
    elif isinstance(fhir_obj, list) and len(fhir_obj) > 0:
        children = []
        for child_spec in fhir_obj:
            children.append(rec_create_fhir_object(dict(), child_spec, row, indices))

        fhir_obj[structure["name"]] = children

    # Remove the attribute if it is null or has no children
    prune_empty_attributes(fhir_obj, structure["name"])


def prune_empty_attributes(fhir_obj, key):
    if isinstance(fhir_obj[key], (dict, list)) and not fhir_obj[key]:
        del fhir_obj[key]
    elif fhir_obj[key] is None:
        del fhir_obj[key]


def create_fhir_list(fhir_obj, attr, name, row, indices):
    index = 0
    while True:
        try:
            child = {}
            rec_create_fhir_object(child, attr, row, indices + [index])
            child = list(child.values())[0]
            if index > 0 and child == fhir_obj[name][-1]:
                break
            fhir_obj[name].append(child)
            index += 1
        except IndexError:
            break
