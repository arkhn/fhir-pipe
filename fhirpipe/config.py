import os
import yaml

DEFAULT_CONFIG_PATH = "config.yml"


class Config:
    """
    Config is used to load the config of config.yml conveniently in an object
    """

    def __init__(self, path=DEFAULT_CONFIG_PATH, key=None):
        self._dict = {}
        self._config = {}
        config_path = path
        if not os.path.isabs(config_path):
            config_path = os.path.join(os.path.dirname(__file__), config_path)
        with open(config_path) as config_file:
            config = yaml.safe_load(config_file)
            if key is not None:
                config = config[key]
            self._config = config

        for attr, node in self._config.items():
            if not isinstance(node, (int, float, str, list)) and node is not None:
                node = ConfigNode(node)
                self._dict[attr] = node.to_dict()
            else:
                self._dict[attr] = node

            setattr(self, attr, node)

    def to_dict(self):
        return self._dict


class ConfigNode:
    """
    Attribute element (possibly recursive) of the Config class
    """

    def __init__(self, node):
        self._dict = {}
        for k, v in node.items():
            if not isinstance(v, (int, float, str, list)) and v is not None:
                v = ConfigNode(v)
                self._dict[k] = v.to_dict()
            else:
                self._dict[k] = v

            setattr(self, k, v)

    def to_dict(self):
        return self._dict
