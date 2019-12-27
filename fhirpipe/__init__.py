import yaml
import logging

global_config = None


def set_global_config(config_path):
    global global_config
    with open(config_path, "r") as stream:
        try:
            global_config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logging.error(exc)
