import akshare as ak
import pandas as pd
import StockConstant
import numpy as np
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)

class DataPuller():
    A_STOCK_FILTER_START_STRING = ['600', '00', '603', '601', '605']

    def __init__(self):
        pass

    def pullAllStockData(self):
        stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
        return stock_zh_a_spot_em_df

    def pullAStockData(self):
        stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
        stock_zh_a_spot_em_df_filter = pd.concat([stock_zh_a_spot_em_df[stock_zh_a_spot_em_df.代码.str.startswith(start_str)] for start_str in self.A_STOCK_FILTER_START_STRING], axis=0)
        return stock_zh_a_spot_em_df_filter

    def pullIndexData(self):
        stock_zh_index_spot_df = ak.stock_zh_index_spot()
        return stock_zh_index_spot_df

    def pullFundData(self):
        """
        输入参数: str symbol="LOF基金"; choice of {"封闭式基金", "ETF基金", "LOF基金"}
        """
        return ak.fund_etf_category_sina(symbol="ETF基金")
