from uuid import uuid4
import math
import copy
import logging

from fhirpipe.utils import build_col_name, new_col_name


def create_resource(chunk, resource_structure):
    res = []
    for _, row in chunk.iterrows():
        try:
            res.append(create_fhir_object(list(row), resource_structure))
        except Exception as e:
            # If cannot build the fhir object, a warning has been logged
            # and we try to generate the next one
            print(e)
            continue
    return res


def create_fhir_object(row, resource_structure):
    # Identify the fhir object
    fhir_object = {"id": str(uuid4()), "resourceType": resource_structure["fhirType"]}

    # The first node has a different structure so iterate outside the
    # dfs_create_fhir function
    for attr in resource_structure["attributes"]:
        rec_create_fhir_object(fhir_object, attr, row)

    # Unlist leaves
    unlist_dict(fhir_object)

    return fhir_object


def build_fhir_leaf_attribute(attribute_structure, row):
    if attribute_structure["mergingScript"]:
        result = [row.pop(0)]
    else:
        result = []
        for inp in attribute_structure["inputs"]:
            if "sqlValue" in inp and inp["sqlValue"]:
                result.append(row.pop(0))
            else:
                result.append(inp["staticValue"])

    # Unlist
    if len(result) == 1:
        result = result[0]

    return result


def rec_create_fhir_object(fhir_obj, attribute_structure, row):
    if isinstance(attribute_structure, dict):
        # If there are some inputs, we can build the objects to output
        if "inputs" in attribute_structure.keys() and attribute_structure["inputs"]:
            result = build_fhir_leaf_attribute(attribute_structure, row)
            fhir_obj[attribute_structure["name"]] = result

        # Otherwise, we can recurse on children
        else:
            is_array = attribute_structure["fhirType"] == "array"
            # 1. The object is a list, so we parse a list
            # and insert it
            if is_array:
                fhir_obj_list = list()
                for attr in attribute_structure["children"]:
                    if len(row) > 0 and isinstance(row[0], list):
                        join_rows = row.pop(0)
                        join_rows_remaining = []
                        for i, join_row in enumerate(join_rows):
                            fhir_obj_list_el = dict()
                            rec_create_fhir_object(fhir_obj_list_el, attr, join_row)
                            fhir_obj_list.append(list(fhir_obj_list_el.values())[0])
                            # Not everything has been consumed: we need to
                            # keep what's remaining
                            if len(join_row) > 0:
                                join_rows_remaining.append(join_row)
                        # If there are remaining elements, we put them back
                        if len(join_rows_remaining) > 0:
                            row.insert(0, join_rows_remaining)
                    else:
                        fhir_obj_list_el = dict()
                        rec_create_fhir_object(fhir_obj_list_el, attr, row)
                        fhir_obj_list.append(list(fhir_obj_list_el.values())[0])
                fhir_obj[attribute_structure["name"]] = fhir_obj_list
            # 2. We keep the layer and recreate the fhir architecture as is
            else:
                fhir_obj[attribute_structure["name"]] = dict()
                for attr in attribute_structure["children"]:
                    rec_create_fhir_object(
                        fhir_obj[attribute_structure["name"]], attr, row
                    )
    # If the current object is a list, we can repeat the same steps as above for each item
    elif isinstance(fhir_obj, list) and len(fhir_obj) > 0:
        children = []
        for child_spec in fhir_obj:
            children.append(rec_create_fhir_object(dict(), child_spec, row))

        fhir_obj[attribute_structure["name"]] = children

def min_length_leave(fhir_obj):
    """ Helper function to compute the length of the leaf attributes that are lists
    in the input dict representing a fhir object
    """
    min_l = math.inf
    for val in fhir_obj.values():
        if isinstance(val, dict):
            length = min_length_leave(val)
        else:
            if isinstance(val, list) and not isinstance(val[0], dict):
                length = len(val)
            else:
                length = math.inf

        # We check that all the list leaves have the same length
        if min_l != math.inf:
            if length not in [1, min_l, math.inf]:
                logging.warning(
                    f"Failed to create obj {fhir_obj} because of "
                    "inconsistant lengths in child leaves."
                )
                raise Exception("Inconsistant lengths in child leaves.")

        min_l = length if length < min_l else min_l
    return min_l


def dl_2_ld(dl, len):
    """ Helper function to convert a dictionary of lists to a list of dictionaries.
    """
    ld = []
    for i in range(len):
        res = copy.deepcopy(dl)
        select_index_in_dl(res, i)
        ld.append(res)
    return ld


def select_index_in_dl(dl, ind):
    """ Helper function transform a dictionary of lists to a dictionary where leaves
    are atomic values by taking the value at index ind each time we have a list leaf.
    """
    for key, val in dl.items():
        if isinstance(val, dict):
            select_index_in_dl(val, ind)
        else:
            if isinstance(val, list) and not isinstance(val[0], dict):
                if len(val) > 1:
                    dl[key] = val[ind]
                else:
                    dl[key] = val[0]


def unlist_dict(fhir_obj):
    """ Helper function to un-list all the leaves after having created the fhir object.
    """
    for key, val in fhir_obj.items():
        if isinstance(val, dict):
            unlist_dict(val)

        elif isinstance(val, list):
            if isinstance(val[0], dict):
                # Remove duplicates primary types (where the only field is value)
                if len(val) > 1 and list(val[0].keys()) == ["value"]:
                    fhir_obj[key] = [{"value": v} for v in {d["value"] for d in val}]
                # And recurse
                for child in fhir_obj[key]:
                    unlist_dict(child)
            else:
                if len(val) > 1:
                    # We check that if we have a list for an attribute that cannot have a list,
                    # all the elements in this list are the same and take this as a value.
                    if not all([el == val[0] for el in val[1:]]):
                        logging.warning(
                            f"Failed to create obj {fhir_obj} because you cannot create "
                            "a non-list attribute with a list of different values."
                        )
                        raise Exception(
                            "Cannot create non-list attribute with list of different values."
                        )
                fhir_obj[key] = val[0]
