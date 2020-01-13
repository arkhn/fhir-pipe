from fhirpipe.utils import build_col_name, new_col_name
from fhirpipe.load.fhirstore import find_fhir_resource


def create_resource(chunk, resource_structure, pk):
    res = []
    for _, row in chunk.iterrows():
        res.append(create_fhir_object(row, resource_structure, pk))
    return res


def create_fhir_object(row, resource_structure, pk):
    # Identify the fhir object
    fhir_object = {"id": row[pk], "resourceType": resource_structure["fhirType"]}

    # The first node has a different structure so iterate outside the
    # dfs_create_fhir function
    for attr in resource_structure["attributes"]:
        rec_create_fhir_object(fhir_object, attr, row)

    return fhir_object


def build_fhir_attribute(attribute_structure, row):
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
            result = build_fhir_attribute(attribute_structure, row)
            fhir_obj[attribute_structure["name"]] = result

        # Otherwise, we can recurse on children
        else:
            is_array = attribute_structure["fhirType"] == "array"

            fhir_obj[attribute_structure["name"]] = [] if is_array else dict()

            for attr in attribute_structure["children"]:
                if is_array:
                    child = {}
                    rec_create_fhir_object(child, attr, row)
                    child = list(child.values())
                    fhir_obj[attribute_structure["name"]].append(child)
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
    # Need to load resources in
    # First we check that the reference has been provided
    if fhir_object and fhir_object["identifier"]["value"]:
        # get id
        identifier = fhir_object["identifier"]["value"]
        # get referenced type (URI)
        resource_type = fhir_object["identifier"]["system"]

        # Search for the fhir instance
        fhir_uri = find_fhir_resource(resource_type, identifier)

        # If an instance was found, replace the provided
        # identifier with FHIR id found
        if fhir_uri is not None:
            fhir_object["identifier"]["value"] = fhir_uri
