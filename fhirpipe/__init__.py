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


def setup_logging():
    filename = None
    if global_config and global_config.get("logging"):
        filename = global_config["logging"].get("filename")
    else:
        logging.warning("Logging configuration not found, logging on stdout...")

    logging.basicConfig(
        filename=filename, format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG,
    )
