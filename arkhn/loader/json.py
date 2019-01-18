import json

from arkhn.config import Config


def load(database, resource):
    """
    Return a yml resource in a dict format
    :param project: software folder (ex: CW)
    :param filename: name of the resource
    :param path: path of the resource in the folder
    :return: a dict object
    """

    with open('graphql_response.json', "r") as stream:
        data = json.load(stream)['data']['database']
        assert data['name'] == database
        response = None
        for r in data['resources']:
            if r['name'] == resource:
                response = r
                break

        return response
