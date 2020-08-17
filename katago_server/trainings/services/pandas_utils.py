import logging

import pandas

logger = logging.getLogger(__name__)


class PandasUtilsService:
    """
    This helper allows debug logs of pandas dataframe
    """

    @staticmethod
    def print_data_frame(x, level=logging.DEBUG):
        pandas.set_option("display.max_rows", len(x))
        pandas.set_option("display.max_columns", None)
        pandas.set_option("display.width", 2000)
        pandas.set_option("display.float_format", "{:20,.3f}".format)
        pandas.set_option("display.max_colwidth", None)
        logger.log(level, "-----> \n" + x.to_string())
        pandas.reset_option("display.max_rows")
        pandas.reset_option("display.max_columns")
        pandas.reset_option("display.width")
        pandas.reset_option("display.float_format")
        pandas.reset_option("display.max_colwidth")
