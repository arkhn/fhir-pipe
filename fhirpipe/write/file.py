import json


def write_to_file(rows, filename):
    with open(filename, "w+") as f:
        for row in rows:
            f.write("{}\n".format(json.dumps(row)))
