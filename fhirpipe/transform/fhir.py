from uuid import uuid4
import math
import copy
import logging

from fhirpipe.utils import build_col_name, new_col_name
from fhirpipe.load.fhirstore import find_fhir_resource


def create_resource(chunk, resource_structure):
    res = []
    for _, row in chunk.iterrows():
        try:
            res.append(create_fhir_object(row, resource_structure))
        except Exception as e:
            # If cannot build the fhir object, a warning has been logged
            # and we try to generate the next one
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
    cols_to_fetch = ([], [])
    for inp in attribute_structure["inputs"]:

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

    if attribute_structure["mergingScript"]:
        result = row[new_col_name(attribute_structure["mergingScript"], cols_to_fetch)]
    else:
        result = [row[c] for c in cols_to_fetch[0]]
        result.extend(cols_to_fetch[1])

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

            fhir_obj[attribute_structure["name"]] = [] if is_array else dict()

            for attr in attribute_structure["children"]:
                if is_array:
                    child = {}
                    rec_create_fhir_object(child, attr, row)
                    # If this obj parent was an array, we know that it will have only
                    # one child and we take it to append it directly to the parent's children
                    child = list(child.values())[0]

                    # Here, we have a dict where leaves can be list, we want to convert that to
                    # a list of dict where leaves are atomic values
                    n_elements = min_length_leave(child)
                    if n_elements == math.inf:
                        n_elements = 1

                    child = dl_2_ld(child, n_elements)

                    fhir_obj[attribute_structure["name"]].extend(child)
                else:
                    rec_create_fhir_object(
                        fhir_obj[attribute_structure["name"]], attr, row
                    )

            # TODO bind references only after having loading all the resource?
            # If the object is a Reference, to we give it to bind_reference
            if attribute_structure["fhirType"].startswith("Reference"):
                bind_reference(fhir_obj[attribute_structure["name"]])

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
            if not length in [1, min_l, math.inf]:
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
                for child in val:
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
                            "You cannot create a non-list attribute with a list of different values."
                        )

                fhir_obj[key] = val[0]


def bind_reference(fhir_object):
    """
    Analyse a reference and replace the provided identifier
    with official FHIR uri if the resource reference exists.

    args:
        fhir_object: the fhir object to parse

    return:
        a fhir_object where valid references are now FHIR uris
    """
    # TODO think again about how to bind references

    # First we check that the reference has been provided
    if fhir_object and fhir_object["identifier"]["value"]:
        # get id
        identifier = fhir_object["identifier"]["value"]
        # get referenced type (URI)
        uri = fhir_object["identifier"]["system"]

        # Search for the fhir instance
        fhir_uri = find_fhir_resource(uri, identifier)

        # If an instance was found, replace the provided
        # identifier with FHIR id found
        if fhir_uri is not None:
            fhir_object["identifier"]["value"] = fhir_uri
