import psycopg2


def run(query):
    output_row = None

    with psycopg2.connect(host="localhost", port=5432, database="cw_local", user="postgres",
                          password="postgres") as connection: 
        with connection.cursor() as cursor:
            cursor.execute(query)
            output_row = cursor.fetchall()

        connection.commit()

    return output_row


def apply_joins(rows, squash_rules):
    """
    Apply the OneToMany joins to have a single result with a list.
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
    for rule in squash_rules:
        one_cols, many_cols = rule
        hash_dict = {}
        for row in rows:
            # Build an identifier for the 'left' part of the join
            hash_key = hash(''.join(take(row, one_cols)))
            if hash_key not in hash_dict:
                hash_dict[hash_key] = {
                    'one': {
                        'before': take(row, range(many_cols[0]-1)),
                        'after':  take(row, range(many_cols[-1]+1, len(row)))
                    },
                    'many': []
                }
            hash_dict[hash_key]['many'].append(take(row, many_cols))

        # Reformat
        print(hash_dict)
        # Imagine you have rows like this (O = One, M = Many, x = other)
        # O O O O x M M M x x
        # After reformating you will have this kind of structure:
        # O O O O x [[M M M], x x
        #            [M M M]]

        new_rows = []
        for hash_key, item in hash_dict.items():
            new_row = item['one']['before'] + [item['many']] + item['one']['after']
            new_rows.append(new_row)

        return new_rows # TODO: n>1 rules



def take(l, indices):
    took = []
    for i, e in enumerate(l):
        if i in indices:
            took.append(e)
    return took


def leave(l, indices):
    took = []
    for i, e in enumerate(l):
        if i not in indices:
            took.append(e)
    return took