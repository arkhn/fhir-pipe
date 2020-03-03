from typing import TypeVar, Dict
import pandas as pd
import numpy as np
import logging

import scripts

T = TypeVar("T", bound="CleaningScript")


class CleaningScript:
    def __init__(self, name: str):
        self.name = name
        self.script = scripts.get_script(name)
        self.columns = []

    def apply(self, df: pd.DataFrame, pk_column: str):
        def clean_and_log(val, id=None, col=None):
            try:
                return self.script(val)
            except Exception as e:
                logging.error(f"{self.name}: Error cleaning {col} (at id = {id}): {e}")

        for col in self.columns:
            yield col, np.vectorize(clean_and_log)(df[col], id=df[pk_column], col=col)


def get_cleaning_scripts(resource_mapping) -> Dict[str, CleaningScript]:
    cleaning_scripts = {}

    for attribute in resource_mapping["attributes"]:
        for input in attribute["inputs"]:
            if input["script"]:
                script_name = input["script"]
                if script_name not in cleaning_scripts:
                    cleaning_scripts[script_name] = CleaningScript(script_name)

    return cleaning_scripts
