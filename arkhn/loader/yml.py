import yaml


def load(project, filename, path='Identification/Individuals/'):
    # TODO: Connect to the future API
    # TODO Add a tool to infer path from filename
    full_path = '../fhir-mapping/{}/resources/{}'.format(project, path)
    if '.yml' not in filename:
        filename += '.yml'
    with open(full_path + filename, 'r') as stream:
        try:
            data = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return data