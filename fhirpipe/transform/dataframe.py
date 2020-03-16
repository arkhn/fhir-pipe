from typing import List

from fhirpipe.utils import new_col_name
from fhirpipe.analyze.concept_map import ConceptMap
from fhirpipe.analyze.cleaning_script import CleaningScript
from fhirpipe.analyze.merging_script import MergingScript


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
    df,
    cleaning_scripts: List[CleaningScript],
    concept_maps: List[ConceptMap],
    merging_scripts: List[MergingScript],
    primary_key_column,
):

    for cleaning_script in cleaning_scripts:
        for col, cleaned_values in cleaning_script.apply(df, str(primary_key_column)):
            df[new_col_name(cleaning_script.name, col)] = cleaned_values

    for concept_map in concept_maps:
        for col, mapped_values in concept_map.apply(df, str(primary_key_column)):
            df[new_col_name(concept_map.id, col)] = mapped_values

    for merging_script in merging_scripts:
        col, merged_values = merging_script.apply(df, str(primary_key_column))
        df[new_col_name(merging_script.name, col)] = merged_values
