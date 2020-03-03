from typing import TypeVar, Dict
import pandas as pd
import numpy as np
import logging

import scripts

T = TypeVar("T", bound="MergingScript")


class MergingScript:
    def __init__(self, name: str):
        self.name = name
        self.script = scripts.get_script(name)
        self.columns = []
        self.static_values = []

    def apply(self, df: pd.DataFrame, pk_column: str):
        def merge_and_log(*val, id=None, cols=None):
            try:
                return self.script(*val)
            except Exception as e:
                logging.error(
                    f"{self.name}: Error merging columns {''.join(self.columns)} (at id={id}): {e}"
                )

        args = [df[col] for col in self.columns] + self.static_values
        return (
            (self.columns, self.static_values,),
            np.vectorize(merge_and_log)(*args, id=df[pk_column]),
        )


def get_merging_scripts(resource_mapping) -> Dict[str, MergingScript]:
    merging_scripts = {}

    for attribute in resource_mapping["attributes"]:
        if attribute["mergingScript"]:
            script_name = attribute["mergingScript"]
            if script_name not in merging_scripts:
                merging_scripts[script_name] = MergingScript(script_name)

    return merging_scripts
