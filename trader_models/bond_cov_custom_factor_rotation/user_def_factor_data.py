from trader_tool.stock_data import stock_data
from trader_tool.bond_cov_data import bond_cov_data
from trader_tool.etf_fund_data import etf_fund_data
from qmt_trader.qmt_trader_ths import qmt_trader_ths
from qmt_trader.qmt_data import qmt_data
from trader_tool.shape_analysis import shape_analysis
from trader_tool.ths_rq import ths_rq
import pandas as pd
from tqdm import tqdm
import numpy as np
import json
from trader_tool import jsl_data
import empyrical
from trader_tool.unification_data import unification_data
import os
from trader_tool.analysis_models import analysis_models
'''
# 计算多因子得分 和 排名(score总分越大越好，rank总排名越小越好)，gourby trade_date,一天里面的对应数据按照规定的ascending=False 给分，#Fales 表示，值小给的分数高
df['price_score']= df.loc[df['filter'] == False,'close'].groupby('trade_date').rank(ascending=False) #价格得分
df[' prem_score' ]= df.loc[df['filter'] == False,'conv_prem' ].groupby('trade_date').rank(ascending=False)# 溢价率得分
df['resi_score']= df.loc[df['filter']== False,'remain_size']. groupby('trade_date').rank(ascending=False) #剩余规模得分
w1= 1 w2=1 w3=1
df[' score']= df.price_score *w1 + df. prem_score *w2 + df. resi_score *w3 #计算总分，权重为价格:溢价率=1:2#df['score']= df.price_score *1 #计算总分，权重为价格:溢价率=1:2
df[' rank'] = df. groupby('trade_date')[' score' ]. rank('first'， ascending-False)#按总分从高到低计算排名#计算每日信号采样信号持仓状态 code_group = df.groupby ('code')
df['time_return']= code_group.pct_chg.shift(-1) #计算标的每日回报 df.loc[(df['rank'] <= hold_num),'signal']=1#标记信号
df.dropna(subset=['signal']，inplace=True)#删除没有标记的行 df. sort_values(by='trade_date',inplace=True)#按日期排序
'''
class user_def_factor_data:
    def __init__(self):
        '''
        自定义因子框架
        '''
        self.stock_data=stock_data()
        self.bond_cov_data=bond_cov_data()
        self.ths_rq=ths_rq()
        self.analysis_models=analysis_models()
        data=unification_data(trader_tool='ths')
        self.data=data.get_unification_data()
        self.path=os.path.dirname(os.path.abspath(__file__))
    def get_cov_bond_var(self,stock='110052',n=5):
        '''
        可转债5波动率
        程序必须有返回值
        '''
        try:
            df=self.bond_cov_data.get_cov_bond_hist_data(stock=stock)
            var_5=df['close'].rolling(5).std().tolist()[-1]
            return "可转债",var_5
        except:
            return "可转债",None
    def get_stock_5_return(self,stock='600031',n=5):
        '''
        股票5日收益率
        程序必须有返回值
        '''
        try:
            df=self.stock_data.get_stock_hist_data_em(stock=stock)
            return_5=df['涨跌幅'].rolling(5).sum().tolist()[-1]
            return '股票',return_5
        except:
            return '股票',None
    def get_cov_bond_return(self,stock='110052',n=5):
        '''
        可转债5日收益率
        程序必须有返回值
        '''
        try:
            df=self.bond_cov_data.get_cov_bond_hist_data(stock=stock)
            return_5=df['涨跌幅'].rolling(5).sum().tolist()[-1]
            return '可转债',return_5
        except:
            return '可转债',None
    def get_cov_bond_score(self,stock='110052'):
        try:
            df=self.data.get_hist_data_em(stock=stock)
            score=self.analysis_models.mean_line_models(df)
            return '可转债',score
        except:
            print(stock,'计算失败')
            return '可转债',None
    def get_cov_bond_5_zf(self,stock='110052'):
        '''
        5日振幅
        '''
        try:
            df=self.data.get_hist_data_em(stock=stock)
            score=df['振幅'].rolling(5).mean().tolist()[-1]
            return '可转债',score
        except:
            print(stock,'计算失败')
            return '可转债',None
    def get_cov_bond_demon_stock(self,stock='110052',daily=120,volatility=18):
        '''
        可转债妖股，最近60天巨大波动
        '''
        try:
            df=self.data.get_hist_data_em(stock=stock)[-daily:60]
            df=df[df['振幅']>=volatility]
            if df.shape[0]>0:
                return '可转债','是'
            else:
                return '可转债','不是'
        except:
            print(stock,'计算失败')
            return '可转债',None
    def cacal_double_low_data(self):
        '''
        衍生因子的计算双低
        '''
        df=pd.read_excel(r'{}\全部因子数据\全部因子数据.xlsx'.format(self.path))
        df['转债价格']=df['转债价格'].astype(float)
        df['转股溢价率']=df['转股溢价率'].astype(float)
        df['双低']=df['转股溢价率']+df['转债价格']
        df.to_excel(r'{}\全部因子数据\全部因子数据.xlsx'.format(self.path))


        
