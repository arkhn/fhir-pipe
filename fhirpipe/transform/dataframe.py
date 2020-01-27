import numpy as np

import scripts

from fhirpipe.utils import new_col_name


def squash_rows(df, squash_rules, parent_cols=[]):
    """
    Apply the OneToMany joins to have a single result with a list in it from
    a list of "flat" results.

    args:
        rows (list<str>): all the results returned from a sql query
        squash_rules (tuple<list>): which columns should serve as identifier to
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
    table, child_rules = squash_rules

    new_cols = [col for col in df.columns if col.startswith(f"{table}.")]
    pivot_cols = parent_cols + new_cols

    to_squash = [
        col
        for col in df.columns
        if any([col.startswith(f"{rule[0]}.") for rule in child_rules])
    ]

    if not to_squash:
        return df

    for child_rule in child_rules:
        df = squash_rows(df, child_rule, pivot_cols)

    df = (
        df.groupby(pivot_cols, as_index=False)
        .apply(lambda x: x.drop_duplicates())
        .groupby(pivot_cols, as_index=False)
        .agg(tuple)
    )

    return df


def apply_scripts(df, cleaning_scripts, merging_scripts):

    for cleaning_script, columns in cleaning_scripts.items():
        for col in columns:
            func = scripts.get_script(cleaning_script)
            df[new_col_name(cleaning_script, col)] = np.vectorize(func)(df[col])

    for merging_script, cols_and_values in merging_scripts.items():
        for cols, statics in cols_and_values:
            func = scripts.get_script(merging_script)
            args = [df[k] for k in cols] + statics
            df[new_col_name(merging_script, (cols, statics))] = np.vectorize(func)(
                *args
            )
