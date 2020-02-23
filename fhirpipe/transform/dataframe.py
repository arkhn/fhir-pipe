import numpy as np
import logging

import scripts

from fhirpipe.utils import new_col_name


def squash_rows(df, squash_rules, parent_cols=[]):
    """
    Apply the squash rules to have a single row for each instance. This is needed
    because joins will create several rows with the same primary key.

    args:
        df (dataframe): the original dataframe with possibly several rows for the same
            primary key.
        squash_rules (nested list): squash rules built by the Analyzer
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

        Squash rule: ['GUY', ['ACCOUNT', []]

        Output:
        GUY.NAME    ...     GUY.AGE   ACCOUNT.NAME                        ACCOUNT.AMOUNT
        Robert              21        (Compte courant, Compte d'epargne)  (17654, 123456789)
        David               51        Ibiza summer                        100
    """
    table, child_rules = squash_rules

    new_cols = [col for col in df.columns if col.startswith(f"{table}.")]
    pivot_cols = parent_cols + new_cols

    to_squash = [
        col for col in df.columns if any([col.startswith(f"{rule[0]}.") for rule in child_rules])
    ]

    if not to_squash:
        return df

    for child_rule in child_rules:
        df = squash_rows(df, child_rule, pivot_cols)

    df = (
        df.groupby(pivot_cols, as_index=False)
        .apply(lambda x: x.drop_duplicates())
        .groupby(pivot_cols, as_index=False)
        .agg(flat_tuple_agg)
    )

    return df


def flat_tuple_agg(values):
    """ We don't want tuples of tuples when squashing several times a columns.
    This function does the aggregation so that the resulting tuple isn't nested.
    """
    res = ()
    for _, val in values.iteritems():
        if isinstance(val, tuple):
            res += val
        else:
            res += (val,)
    return res


def apply_scripts(
    df, cleaning_scripts, concept_maps, dict_maps, merging_scripts, primary_key_column
):

    for cleaning_script, columns in cleaning_scripts.items():
        script = scripts.get_script(cleaning_script)
        for col in columns:
            df[new_col_name(cleaning_script, col)] = np.vectorize(clean_and_log)(
                df[col], script=script, id=df[primary_key_column], col=col
            )

    for concept_map_id, columns in concept_maps.items():
        map_title, dict_map = dict_maps[concept_map_id]
        for col in columns:
            df[new_col_name(map_title, col)] = np.vectorize(map_and_log)(
                df[col], map_title=map_title, dict_map=dict_map, id=df[primary_key_column], col=col
            )

    for merging_script, cols_and_values in merging_scripts:
        script = scripts.get_script(merging_script)
        cols, statics = cols_and_values
        args = [df[k] for k in cols] + statics
        df[new_col_name(merging_script, (cols, statics))] = np.vectorize(merge_and_log)(
            *args, script=script, id=df[primary_key_column], cols=" ".join(cols)
        )


def clean_and_log(val, script=None, id=None, col=None):
    try:
        return script(val)
    except Exception as e:
        logging.error(f"{script.__name__}: Error cleaning {col} (at id = {id}): {e}")


def map_and_log(val, map_title=None, dict_map=None, id=None, col=None):
    try:
        return dict_map[val]
    except Exception as e:
        logging.error(f"{map_title}: Error cleaning {col} (at id = {id}): {e}")


def merge_and_log(*val, script=None, id=None, cols=None):
    try:
        return script(*val)
    except Exception as e:
        logging.error(f"{script.__name__}: Error merging columns {cols} (at id = {id}): {e}")
