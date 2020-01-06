from uuid import uuid4

from fhirpipe.utils import build_col_name, new_col_name
from fhirpipe.load.fhirstore import find_fhir_resource


def create_resource(chunk, resource_structure):
    res = []
    for _, row in chunk.iterrows():
        res.append(create_fhir_object(row, resource_structure))
    return res


def create_fhir_object(row, resource_structure):
    # Identify the fhir object
    fhir_object = {"id": str(uuid4()), "resourceType": resource_structure["name"]}

    # The first node has a different structure so iterate outside the
    # dfs_create_fhir function
    for attr in resource_structure["attributes"]:
        rec_create_fhir_object(fhir_object, attr, row)

    return fhir_object


def rec_create_fhir_object(fhir_obj, attribute_structure, row):
    if isinstance(attribute_structure, dict):
        # If there are some inputs, we can build the objects to output
        if (
            "inputColumns" in attribute_structure.keys()
            and attribute_structure["inputColumns"]
        ):
            cols_to_fetch = ([], [])
            for input_col in attribute_structure["inputColumns"]:

                # If a sql location is provided, then a sql value has been returned
                if input_col["table"] and input_col["column"]:
                    col_name = build_col_name(
                        input_col["table"], input_col["column"], input_col["owner"]
                    )
                    if input_col["script"]:
                        # If there is a cleaning script, we fetch the value in the cleaned column
                        col_name = new_col_name(input_col["script"], col_name)
                    cols_to_fetch[0].append(col_name)

                # Else retrieve the static value
                else:
                    cols_to_fetch[1].append(input_col["staticValue"])

            if attribute_structure["mergingScript"]:
                result = row[
                    new_col_name(attribute_structure["mergingScript"], cols_to_fetch)
                ]
            else:
                result = [row[c] for c in cols_to_fetch[0]]
                result.extend(cols_to_fetch[1])

            # Unlist
            if len(result) == 1:
                result = result[0]

            fhir_obj[attribute_structure["name"]] = result

        # Otherwise, we can recurse on children
        else:
            if attribute_structure["type"] == "list":
                fhir_obj[attribute_structure["name"]] = []
                for attr in attribute_structure["attributes"]:
                    child = {}
                    rec_create_fhir_object(child, attr, row)
                    fhir_obj[attribute_structure["name"]].append(child)

            elif attribute_structure["type"].startswith("list"):
                fhir_obj[attribute_structure["name"]] = []
                for attr in attribute_structure["attributes"]:
                    child = {}
                    rec_create_fhir_object(child, attr, row)
                    values = list(child.values())
                    if len(values) == 1:
                        values = values[0]
                    fhir_obj[attribute_structure["name"]].append(values)

            else:
                fhir_obj[attribute_structure["name"]] = dict()
                for attr in attribute_structure["attributes"]:
                    rec_create_fhir_object(
                        fhir_obj[attribute_structure["name"]], attr, row
                    )

                # If the object is a Reference, to we give it to bind_reference
                if attribute_structure["type"].startswith("Reference"):
                    bind_reference(
                        fhir_obj[attribute_structure["name"]], attribute_structure
                    )

    # If the current object is a list, we can repeat the same steps as above for each item
    elif isinstance(fhir_obj, list) and len(fhir_obj) > 0:
        children = []
        for child_spec in fhir_obj:
            children.append(rec_create_fhir_object(dict(), child_spec, row))

        fhir_obj[attribute_structure["name"]] = children


def bind_reference(fhir_object, fhir_spec):
    """
    Analyse a reference and replace the provided identifier
    with official FHIR uri if the resource reference exists.

    args:
        fhir_object: the fhir object to parse

    return:
        a fhir_object where valid references are now FHIR uris
    """

    # First we check that the reference has been provided
    if fhir_object and fhir_object["identifier"]["value"]:
        identifier = fhir_object["identifier"]["value"]

        # Collect all the resource_types which could be referenced
        try:
            s = fhir_spec["type"]
            resource_types = s[s.find("(") + 1 : s.find(")")].split("|")
        except AttributeError:
            raise ReferenceError(
                f"No FHIR Resource type provided for the reference {fhir_spec['name']}"
            )

        # Search for a fhir instance among the listed
        # resources and exit when one is found
        fhir_uri = None
        for resource_type in resource_types:
            fhir_uri = find_fhir_resource(resource_type, identifier)
            if fhir_uri is not None:
                break

        # If an instance was found, replace the provided
        # identifier with FHIR id found
        if fhir_uri is not None:
            fhir_object["identifier"]["value"] = fhir_uri
