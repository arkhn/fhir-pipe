import pandas as pd
import numpy as np
import logging

import scripts


class CleaningScript:
    def __init__(self, name: str):
        self.name = name
        self.script = scripts.get_script(name)
        self.columns = []

    def __eq__(self, operand) -> bool:
        return self.name == operand.name

    def apply(self, df: pd.DataFrame, pk_column: str):
        def clean_and_log(val, id=None, col=None):
            try:
                return self.script(val)
            except Exception as e:
                logging.error(f"{self.name}: Error cleaning {col} (at id = {id}): {e}")

        for col in self.columns:
            yield col, np.vectorize(clean_and_log)(df[col], id=df[pk_column], col=col)
