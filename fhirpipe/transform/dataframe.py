from typing import List

import pandas as pd

from fhirpipe.analyze.attribute import Attribute


def clean_data(
    df, attributes: List[Attribute], primary_key_column,
):
    """ Apply scripts and concept maps.
    """
    cleaned_df = pd.DataFrame()
    df_pk_col = df[primary_key_column.dataframe_column_name()]
    for attribute in attributes:
        cols_for_attr = []
        df_col = None
        for col in attribute.columns:
            df_col_name = col.dataframe_column_name()
            df_col = df[df_col_name]
            cols_for_attr.append(df_col_name)

            # Apply cleaning script
            if col.cleaning_script:
                df_col = col.cleaning_script.apply(df_col, df_pk_col)

            # Apply concept map
            if col.concept_map:
                df_col = col.concept_map.apply(df_col, df_pk_col)

        # Apply merging script
        if attribute.merging_script:
            df_col = attribute.merging_script.apply(
                [df[col] for col in cols_for_attr], attribute.static_inputs, df_pk_col
            )

        if df_col is not None:
            cleaned_df[attribute] = df_col

    return cleaned_df


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

    # TODO what if we merge several columns from different tbales?
    new_cols = [col for col in df.columns if col.columns and col.columns[0].table == table]
    pivot_cols = parent_cols + new_cols

    to_squash = [
        col
        for col in df.columns
        if any([col.columns and col.columns[0].table == rule[0] for rule in child_rules])
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
