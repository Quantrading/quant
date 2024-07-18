from trader_tool.stock_data import stock_data
from trader_tool.bond_cov_data import bond_cov_data
from trader_tool.shape_analysis import shape_analysis
from trader_tool.analysis_models import analysis_models
import pandas as pd
from trader_tool.ths_rq import ths_rq
from tqdm import tqdm
import numpy as np
import json
from  trader_tool import jsl_data
from qmt_trader.qmt_trader_ths import qmt_trader_ths
from xgtrader.xgtrader import xgtrader
from trader_tool.ths_rq import ths_rq
from trader_tool.ths_board_concept_data import ths_board_concept_data
from trader_tool.unification_data import unification_data
import os
import pandas as pd
from datetime import datetime
import time
from trader_tool.dfcf_etf_data import dfcf_etf_data
class user_def_stock_data:
    def __init__(self):
        '''
        自定义股票池轮动模型
        '''
        self.path=os.path.dirname(os.path.abspath(__file__))
        self.ths_rq=ths_rq()
    def get_trader_stock(self):
        '''
        获取交易数据
        只需要股票池代码/证券代码
        '''
        df=self.ths_rq.get_hot_stock_rank()[:10]
        df.to_excel(r'{}\自定义轮动股票池\自定义轮动股票池.xlsx'.format(self.path))

    