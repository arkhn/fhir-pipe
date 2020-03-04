import pandas as pd
import numpy as np
import logging

import scripts


class MergingScript:
    def __init__(self, name: str):
        self.name = name
        self.script = scripts.get_script(name)
        self.columns = []
        self.static_values = []

    def __eq__(self, operand) -> bool:
        return self.name == operand.name

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
