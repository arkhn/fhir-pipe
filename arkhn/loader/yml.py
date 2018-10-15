import yaml


def load(filename, path='Resources/Administration/'):
    if '.yml' not in filename:
        filename += '.yml'
    with open(path+filename, 'r') as stream:
        try:
            data = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return data