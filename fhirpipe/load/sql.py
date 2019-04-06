import datetime
import psycopg2
import cx_Oracle
import logging
import fhirbase

from fhirpipe.config import Config


def save_in_fhirbase(instances):
    """
    Save instances of FHIR resources in the fhirbase
    :param instances: list of instances
    """
    config = Config("fhirbase")
    with psycopg2.connect(
        dbname=config.database, user=config.user, host=config.host, port=config.port, password=config.password
    ) as connection:
        fb = fhirbase.FHIRBase(connection)
        for instance in instances:
            fb.create(instance)


def get_connection(connection_type: str = None):
    """
    Return a sql connexion depending on the configuration provided in config.yml
    (see root of the project)
    Note: should be used in a context environment (with get_connection(c) as ...)
    :param connection_type: a string like "postgre", "oracle". See your config file
    :return: a sql connexion
    """
    sql_config = Config("sql").to_dict()
    if connection_type is None:
        connection_type = sql_config["default"]
    connection = sql_config[connection_type]
    try:
        lib = eval(connection["lib"])
    except NameError:
        logging.warning(
            f"NameError found, did you import the lib {connection['lib']} ?"
        )
        raise ImportError
    args = connection["args"]
    kwargs = connection["kwargs"]

    return lib.connect(*args, **kwargs)


def batch_run(query, batch_size, offset=0, connection=None):
    """
    Run a query batch per batch, when the query is too big
    :param query: the query to batch
    :param batch_size: the size of the batch
    :param offset: initial offset (used when restarting a job which stopped
    in the middle)
    :param connection: a connection if any already active (to avoid opening too many)
    :return: an iterator which computes and returns the results batch per batch
    """
    call_next_batch = True
    batch_idx = 0

    # Remove the ending ';' if any
    if query[-1] == ";":
        query = query[:-1]
    # A query with a limit can't be batch run
    limit_words = ["limit", "fetch next"]
    if any(limit_word in query.lower() for limit_word in limit_words):
        raise NotImplementedError(
            "You currently can't run by batch a query which already has a limit"
            "statement. Error in {}".format(query)
        )

    # Adapt the offset and limit depending of oracle or postgre db
    database_type = Config("sql").default
    if database_type == "oracle":
        offset_batch_size_instruction = " OFFSET {} ROWS FETCH NEXT {} ROWS ONLY"
    elif database_type == "postgre":
        offset_batch_size_instruction = " OFFSET {} LIMIT {}"
    else:
        raise RuntimeError(f"{database_type} is not a supported database type.")

    while call_next_batch:
        batch_query = query + offset_batch_size_instruction.format(offset, batch_size)
        batch = run(batch_query, connection)

        call_next_batch = len(batch) >= batch_size
        offset += batch_size
        batch_idx += 1

        yield batch_idx, offset, batch


def run(query, connection: str = None):
    """
    Run a sql query after opening a sql connexion
    :param connection: type of connection: "postgre", "oracle" (see config.yml)
    """
    with get_connection(connection) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

        connection.commit()

    # Replace None values with '' AND replace date with str representation
    for i, row in enumerate(rows):
        new_row = []
        for el in row:
            if el is None:
                new_row.append("")
            elif isinstance(el, datetime.datetime):
                new_row.append(str(el))
            else:
                new_row.append(el)
        rows[i] = new_row
    return rows


def apply_joins(rows, squash_rule, parent_cols=tuple()):
    """
    Apply the OneToMany joins to have a single result with a list in it from
    a list of "flat" results.
    args:
        rows (list<str>): all the results returned from a sql query
        squash_rule (tuple<list>): which columns should serve as identifier to merge
        the rows
        parent_cols (list): param used for recursive call

    Example:
        if you join people with bank accounts on guy.id = account.owner_id, you want at
        the end to have for a single guy to have a single instance with an attribute
        accounts.
        ROWS:
        GUY.NAME    ...     GUY.AGE     ACCOUNT.NAME        ACCOUNT.AMOUNT
        Robert              21          Compte courant      17654
        Robert              21          Compte d'epargne    123456789
        David               51          Ibiza summer        100

        Squash rule: ('GUY', 'ACCOUNT') or in terms of columns ([0, ..., 5], [6, 7])

        Output:
        GUY.NAME    ...     GUY.AGE     ACCOUNT.NAME        ACCOUNT.AMOUNT
        Robert              21        [(Compte courant   ,  17654            )
                                       (Compte d'epargne ,  123456789         )]
        David               51          Ibiza summer        100
    """
    cols, child_rules = squash_rule

    for child_rule in child_rules:
        rows = apply_joins(rows, child_rule, cols)

    # The dict is used to store for each unique element of pivot column, all the
    # many_cols to put together. Note that pivot.before (many) and pivot.after is used
    # to keep the order of the elems in rows, which is crucial for `dfs_create_fhir`
    new_row_dict = {}
    for row in rows:
        # a sanity check
        assert all([e in range(len(row)) for e in cols])
        # As we work on the whole row, we add the parent left parts transmitted recursively
        pivot_cols, many_cols = (
            parent_cols + cols,
            leave(range(len(row)), parent_cols + cols),
        )
        # Build an identifier for the 'left' part of the join
        hash_key = hash("".join(take(row, pivot_cols)))
        if hash_key not in new_row_dict:
            # Add the key if needed
            new_row_dict[hash_key] = {
                "pivot": {
                    "before": take(row, range(many_cols[0]))
                    if len(many_cols) > 0
                    else list(row),
                    "after": take(row, range(many_cols[-1] + 1, len(row)))
                    if len(many_cols) > 0
                    else [],
                },
                "many": [],
            }
        # Add a many part to squash
        if len(many_cols) > 0:
            new_row_dict[hash_key]["many"].append(take(row, many_cols))

    # print(new_row_dict)

    # Reformat
    # Imagine you have rows like this (P = Pivot, M = Many)
    # P P P P P  M M M  P P
    # After reformating you will have this kind of structure:
    # P P P P P [[M M M] P P
    #            [M M M]]

    new_rows = []
    for hash_key, item in new_row_dict.items():
        new_row = item["pivot"]["before"]
        new_row += [item["many"]] if len(item["many"]) > 0 else []
        new_row += item["pivot"]["after"]
        new_rows.append(new_row)

    return new_rows


def take(l, indices):
    """
    Given a list l, return the elements whose indices are in indices
    Example:
        take(['a', 'b', 'c', 'd']), [0, 2]
        Returns
        ['a', 'c']
    """
    took = []
    for i, e in enumerate(l):
        if i in indices:
            took.append(e)
    return took


def leave(l, indices):
    """
    Given a list l, return the elements whose indices are in indices
    Example:
        leave(['a', 'b', 'c', 'd']), [0, 2]
        Returns
        ['b', 'd']
    """
    took = []
    for i, e in enumerate(l):
        if i not in indices:
            took.append(e)
    return took
