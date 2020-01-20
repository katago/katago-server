import logging

import pandas as pd

logger = logging.getLogger(__name__)


class PandasUtilsService:
    @staticmethod
    def print_data_frame(x, level=logging.DEBUG):
        pd.set_option("display.max_rows", len(x))
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", 2000)
        pd.set_option("display.float_format", "{:20,.3f}".format)
        pd.set_option("display.max_colwidth", -1)
        logger.log(level, "-----> \n" + x.to_string())
        pd.reset_option("display.max_rows")
        pd.reset_option("display.max_columns")
        pd.reset_option("display.width")
        pd.reset_option("display.float_format")
        pd.reset_option("display.max_colwidth")
