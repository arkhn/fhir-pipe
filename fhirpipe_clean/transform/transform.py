import pandas as pd
import numpy as np
from uuid import uuid4

from fhirpipe_clean.utils import build_col_name, new_col_name
from fhirpipe_clean.scripts import get_script


def squash_rows(df, squash_rule, parent_cols=[]):
    """
    Apply the OneToMany joins to have a single result with a list in it from
    a list of "flat" results.

    args:
        rows (list<str>): all the results returned from a sql query
        squash_rule (tuple<list>): which columns should serve as identifier to
        merge the rows
        parent_cols (list): param used for recursive call

    Example:
        if you join people with bank accounts on guy.id = account.owner_id,
        you want at the end to have for a single guy to have a single instance
        with an attribute accounts.
        ROWS:
        GUY.NAME    ...     GUY.AGE     ACCOUNT.NAME        ACCOUNT.AMOUNT
        Robert              21          Compte courant      17654
        Robert              21          Compte d'epargne    123456789
        David               51          Ibiza summer        100

        Squash rule:
        ('GUY', 'ACCOUNT') or in terms of columns ([0, ..., 5], [6, 7])

        Output:
        GUY.NAME    ...     GUY.AGE     ACCOUNT.NAME        ACCOUNT.AMOUNT
        Robert              21        [(Compte courant   ,  17654         )
                                       (Compte d'epargne ,  123456789     )]
        David               51          Ibiza summer        100
    """
    cols, child_rules = squash_rule
    # As we work on the whole row, we add the parent left parts
    # transmitted recursively
    pivot_cols = parent_cols + cols
    to_squash = [col for col in df.columns if col not in pivot_cols]
    if not to_squash:
        return df

    for child_rule in child_rules:
        df = squash_rows(df, child_rule, pivot_cols)

    df = df.groupby(pivot_cols, as_index=False)[to_squash].agg(list)

    return df


def apply_scripts(df, cleaning_scripts, merging_scripts):
    for cleaning_script, columns in cleaning_scripts.items():
        for col in columns:
            # func to apply
            func = get_script(cleaning_script)
            df[new_col_name(cleaning_script, col)] = np.vectorize(func)(df[col])
    for merging_script, cols_and_values in merging_scripts.items():
        for cols, statics in cols_and_values:
            # func to apply
            func = get_script(merging_script)
            args = [df[k] for k in cols] + statics
            df[new_col_name(merging_script, (cols, statics))] = func(*args)


def create_fhir_object(row, resource_structure, resource_name):
    # Identify the fhir object
    fhir_object = {"id": str(uuid4()), "resourceType": resource_name}

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

            fhir_obj[attribute_structure["name"]] = result

        else:
            fhir_obj[attribute_structure["name"]] = dict()
            for attr in attribute_structure["attributes"]:
                rec_create_fhir_object(fhir_obj[attribute_structure["name"]], attr, row)

        # TODO reference
        # If the object is a Reference, to we give it to bind_reference
        # if attribute_structure["type"].startswith("Reference"):
        #     bind_reference(fhir_obj[attribute_structure["name"]], attribute_structure)

    # If the current object is a list, we can repeat the same steps as above for each item
    elif isinstance(fhir_obj, list) and len(fhir_obj) > 0:
        children = []
        for child_spec in fhir_obj:
            children.append(rec_create_fhir_object(dict(), child_spec, row))

        fhir_obj[attribute_structure["name"]] = children
