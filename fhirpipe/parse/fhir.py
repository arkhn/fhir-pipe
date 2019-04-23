import random

from fhirpipe import scripts


def _is_empty(value):
    return value is None or value == "NaN" or value == ""


def create_fhir_object(row, resource, resource_structure):
    """
    High level function which manages dfs_create_fhir to transform
    a row returned by a SQL query intro a fhir object using some structure
    instructions

    args:
        row (list): the data input from a sql query
        resource (str): the name of the fhir resource
        resource_structure (dict): the structure of the fhir object

    return:
        a dictionary with a the structure of a fhir object
    """
    # Identify the fhir object
    fhir_object = {"id": int(random.random() * 10e10), "resourceType": resource}

    # The first node has a different structure so iterate outside the
    # dfs_create_fhir function
    for attr in resource_structure["attributes"]:
        dfs_create_fhir_object(fhir_object, attr, row)

    # Then remove all empty leaves or branches
    fhir_object, n_leafs = clean_fhir(fhir_object)

    return fhir_object


def dfs_create_fhir_object(fhir_obj, fhir_spec, row):
    """
        For each instance of a Resource,
        Run through the dict/tree of a Resource (and the references to templates)
        And parse a similar dict, where we replace all occurrences of inputColumns
        with the result of the query,
        Processed by the appropriate script.

        args:
            fhir_obj (dict): the fhir obj we want to parse, which is provided empty
                before the first recursion, and gets progressively filled
            fhir_spec (dict): the FHIR spec mapping from graphql
            row: one row of the result of the SQL query

        return:
            None, but the initial dict provided as fhir_obj is now filled.
    """
    # if there are columns specified
    if "inputColumns" in fhir_spec.keys() and len(fhir_spec["inputColumns"]) > 0:
        values = []
        for inputs in fhir_spec["inputColumns"]:
            # If a sql location is provided, then a sql value has been returned
            if inputs["table"] is not None and inputs["column"] is not None:
                script_name = inputs["script"]
                value = row.pop(0)
                if script_name is not None:
                    value = scripts.get_script(script_name)(value)
                values.append(value)
            # Else retrieve the static value
            else:
                values.append(inputs["staticValue"])

        # Un-list the value if not needed
        if not fhir_spec["type"].startswith("list"):
            values = "".join(values)

        fhir_obj[fhir_spec["name"]] = values
    else:  # else iterate recursively based on 3 cases
        # 1. The object should be a list, so we parse a list
        # and insert it
        if fhir_spec["type"].startswith("list"):
            fhir_obj_list = list()
            for fhir_spec_attr in fhir_spec["attributes"]:
                if len(row) > 0 and isinstance(row[0], list):
                    join_rows = row.pop(0)
                    join_rows_remaining = []
                    for i, join_row in enumerate(join_rows):
                        fhir_obj_list_el = dict()
                        dfs_create_fhir_object(
                            fhir_obj_list_el, fhir_spec_attr, join_row
                        )
                        fhir_obj_list.append(fhir_obj_list_el)
                        # Not everything has been consumed: we need to keep what's remaining
                        if len(join_row) > 0:
                            join_rows_remaining.append(join_row)
                    # If there are remaining elements, we put them back
                    if len(join_rows_remaining) > 0:
                        row.insert(0, join_rows_remaining)
                else:
                    fhir_obj_list_el = dict()
                    dfs_create_fhir_object(fhir_obj_list_el, fhir_spec_attr, row)
                    fhir_obj_list.append(fhir_obj_list_el)
            fhir_obj[fhir_spec["name"]] = fhir_obj_list
        # 2. It's a profile: we don't keep this layer in the fhir object and put
        # all the attributes at the same layer in fhir_obj
        elif fhir_spec["isProfile"]:
            for fhir_spec_attr in fhir_spec["attributes"]:
                dfs_create_fhir_object(fhir_obj, fhir_spec_attr, row)
        # 3. We keep the layer and recreate the fhir architecture as is
        else:
            fhir_obj[fhir_spec["name"]] = dict()
            for fhir_spec_attr in fhir_spec["attributes"]:
                dfs_create_fhir_object(fhir_obj[fhir_spec["name"]], fhir_spec_attr, row)


def clean_fhir(fhir_object):
    """
    Remove all empty leaves and branches of the fhir object
    (ie: None, empty list, or nested empty things)

    args:
        fhir_object: dirty fhir object

    return:
        clean fhir object
    """
    if isinstance(fhir_object, dict):
        n_values = 0
        clean_object = {}
        for name_attr, fhir_object_attr in fhir_object.items():
            clean_attr, n_values_attr = clean_fhir(fhir_object_attr)
            if n_values_attr > 0:
                clean_object[name_attr] = clean_attr
                n_values += n_values_attr
        return clean_object, n_values

    elif isinstance(fhir_object, list):
        n_values = 0
        clean_object = []
        for fhir_object_el in fhir_object:
            clean_el, n_values_el = clean_fhir(fhir_object_el)
            if n_values_el > 0:
                clean_object.append(clean_el)
                n_values += n_values_el
        return clean_object, n_values

    else:
        if _is_empty(fhir_object):
            return fhir_object, 0
        else:
            return fhir_object, 1
