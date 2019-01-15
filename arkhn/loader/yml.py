import yaml

from arkhn.config import Config


def load(project, filename, path="Identification/Individuals/"):
    """
    Return a yml resource in a dict format
    :param project: software folder (ex: CW)
    :param filename: name of the resource
    :param path: path of the resource in the folder
    :return: a dict object
    """
    # TODO Add a tool to infer path from filename
    # Load the path of the fhir-mapping repo from the configuration
    config = Config("filesystem")
    mapping_path = config.mapping

    full_path = "{}/{}/resources/{}".format(mapping_path, project, path)

    if ".yml" not in filename:
        filename += ".yml"
    with open(full_path + filename, "r") as stream:
        try:
            data = yaml.load(stream)
            return data
        except yaml.YAMLError as exc:
            print(exc)
