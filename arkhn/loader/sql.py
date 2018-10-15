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
