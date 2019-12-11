import pandas as pd
from uuid import uuid4

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

def create_fhir_object(row, resource_structure, resource_name):
    # Identify the fhir object
    fhir_object = {"id": str(uuid4()), "resourceType": resource_name}

    # The first node has a different structure so iterate outside the
    # dfs_create_fhir function
    for attr in resource_structure["attributes"]:
        rec_create_fhir_object(fhir_object, attr, row)

    return fhir_object

def rec_create_fhir_object(fhir_obj, fhir_spec, row):
    if isinstance(fhir_spec, dict):
        if "inputColumns" in fhir_spec.keys() and fhir_spec["inputColumns"]:
            for input_col in fhir_spec["inputColumns"]:
                # If a sql location is provided, then a sql value has been returned
                if input_col["table"] and input_col["column"]:
                    script_name = input_col["script"]
                    # TODO what about table names?
                    val = row[input_col["column"].lower()]
                    if script_name is not None:
                        # TODO clean and import cleaning script usage
                        #val = scripts.get_script(script_name)(val)
                        pass
                # Else retrieve the static value
                else:
                    val = input_col["staticValue"]

                fhir_obj[fhir_spec["name"]] = val
        
        else:
            fhir_obj[fhir_spec["name"]] = dict()
            for attr in fhir_spec["attributes"]:
                rec_create_fhir_object(fhir_obj[fhir_spec["name"]], attr, row)

            # TODO reference
            # If the object is a Reference, to we give it to bind_reference
            # if fhir_spec["type"].startswith("Reference"):
            #     bind_reference(fhir_obj[fhir_spec["name"]], fhir_spec)

    elif isinstance(fhir_obj, list) and len(fhir_obj) > 0:
        children = []
        for child_spec in fhir_obj:
            children.append(rec_create_fhir_object(dict(), child_spec, row))
        
        fhir_obj[fhir_spec["name"]] = children