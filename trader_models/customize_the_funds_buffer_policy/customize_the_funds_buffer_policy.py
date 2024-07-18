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
from trader_tool.dfcf_etf_data import dfcf_etf_data
#债券模型
from trader_models.custom_bond_trend_rotation_strategy.custom_bond_trend_rotation_strategy import custom_bond_trend_rotation_strategy
class customize_the_funds_buffer_policy:
    def __init__(self,trader_tool='ths',exe='C:/同花顺软件/同花顺/xiadan.exe',tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qq='1029762153@qq.com',open_set='否',qmt_path='D:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55009640',qmt_account_type='STOCK',name='customize_trading_strategies'):
        '''
        自定义资金缓冲区策略
        '''
        self.exe=exe
        self.tesseract_cmd=tesseract_cmd
        self.qq=qq
        self.trader_tool=trader_tool
        self.open_set=open_set
        self.qmt_path=qmt_path
        self.qmt_account=qmt_account
        self.qmt_account_type=qmt_account_type
        if trader_tool=='ths':
            self.trader=xgtrader(exe=self.exe,tesseract_cmd=self.tesseract_cmd,open_set=open_set)
        else:
            self.trader=qmt_trader_ths(path=qmt_path,account=qmt_account,account_type=qmt_account_type)
        self.stock_data=stock_data()
        self.bond_cov_data=bond_cov_data()
        self.ths_rq=ths_rq()
        self.path=os.path.dirname(os.path.abspath(__file__))
        self.ths_board_concept_data=ths_board_concept_data()
        self.name=name
        self.data=unification_data(trader_tool=self.trader_tool)
        self.data=self.data.get_unification_data()
        self.dfcf_etf_data=dfcf_etf_data()
        self.trader.connect()
    def save_position(self):
        '''
        保存持股数据
        '''
        with open(r'分析配置.json',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        del_df=pd.read_excel(r'{}\黑名单\黑名单.xlsx'.format(self.path),dtype='object')
        del_trader_stock=text['黑名单']
        if del_df.shape[0]>0:
            del_df['证券代码']=del_df['证券代码'].apply(lambda x : str(x).split('.')[0])
            del_df['证券代码']=del_df['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
            del_stock_list=del_df['证券代码'].tolist()
        else:
            del_stock_list=[]
        for del_stock in del_trader_stock:
            del_stock_list.append(del_stock)
        trader_type=text['交易品种']
        def select_del_stock_list(x):
            if str(x)[:6] in del_stock_list:
                return '是'
            else:
                return '否'
        df=self.trader.position()
        try:
            if df==False:
                print('获取持股失败')
        except:
            if df.shape[0]>0:
                if trader_type=='全部':
                    df=df
                else:
                    df['选择']=df['证券代码'].apply(self.trader.select_data_type)
                    df=df[df['选择']==trader_type]
                print(df)
                df=df[df['可用余额']>=10]
                df['黑名单']=df['证券代码'].apply(select_del_stock_list)
                df=df[df['黑名单']=='否']
                print('剔除黑名单**********')
                df.to_excel(r'持股数据\持股数据.xlsx')
                return df
            else:
                df=pd.DataFrame()
                df['账号类型']=None
                df['资金账号']=None
                df['证券代码']=None
                df['股票余额']=None
                df['可用余额']=None
                df['成本价']=None
                df['市值']=None
                df['选择']=None
                df['持股天数']=None
                df['交易状态']=None
                df['明细']=None
                df['证券名称']=None
                df['冻结数量']=None
                df['市价']=None	
                df['盈亏']=None
                df['盈亏比(%)']=None
                df['当日买入']=None	
                df['当日卖出']=None
                df.to_excel(r'持股数据\持股数据.xlsx')
                return df
    def save_balance(self):
        '''
        保持账户数据
        '''
        df=self.trader.balance()
        df.to_excel(r'账户数据\账户数据.xlsx')
        return df
    def mean_line_models(self,df):
        '''
        均线模型
        趋势模型
        5，10，20，30，60
        '''
        df=df
        #df=self.bond_cov_data.get_cov_bond_hist_data(stock=stock,start=start_date,end=end_date,limit=1000000000)
        df1=pd.DataFrame()
        df1['date']=df['date']
        df1['5']=df['close'].rolling(window=5).mean()
        df1['10']=df['close'].rolling(window=10).mean()
        df1['20']=df['close'].rolling(window=20).mean()
        df1['30']=df['close'].rolling(window=30).mean()
        df1['60']=df['close'].rolling(window=60).mean()
        score=0
        #加分的情况
        mean_5=df1['5'].tolist()[-1]
        mean_10=df1['10'].tolist()[-1]
        mean_20=df1['20'].tolist()[-1]
        mean_30=df1['30'].tolist()[-1]
        mean_60=df1['60'].tolist()[-1]
        #相邻2个均线进行比较
        if mean_5>mean_10:
            score+=25
        if mean_10>mean_20:
            score+=25
        if mean_20>mean_30:
            score+=25
        if mean_30>mean_60:
            score+=25
        return score
    def release_funds(self):
        '''
        释放资金给其他的策略，需要在其他策略运行前释放，可以集合竞价释放
        '''
        with open(r'{}\自定义资金缓冲区策略.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        stock_list=text['自定义标的']
        ratio=text['资金释放目标比例']
        df=self.trader.position()
        df=df[df['股票余额']>=10]
        if df.shape[0]>0:
            df['证券代码']=df['证券代码'].apply(lambda x : str(x).split('.')[0])
            df['持股检查']=df['证券代码'].apply(lambda x: '是' if x in stock_list else '不是')
            df=df[df['持股检查']=='是']
            if df.shape[0]>0:
                for stock in df['证券代码'].tolist():
                    price=self.data.get_spot_data(stock=stock)['最新价']
                    trader_type,trader_amount,price=self.trader.order_target_percent(stock=stock,
                                                        target_percent=ratio,price=price)
                    if trader_type=='sell' and trader_amount>=10:
                        self.trader.sell(security=stock,price=price,amount=trader_amount)
                        print('释放资金成功{} 数量{} 价格{}'.format(stock,trader_amount,price))
                    else:
                        print('{}不能卖出,不能T0'.format(stock))
            else:
                print('没有资金缓存股票池')
        else:
            print('缓存资金股票没有持股')
    def buy_bonds_to_deposit_funds(self):
        '''
        购买债券存入资金
        '''
        with open(r'{}\自定义资金缓冲区策略.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        stock_list=text['自定义标的']
        min_score=text['买入最低分']
        line=text['自定义交易品种跌破N日均线卖出']
        account=self.trader.balance()
        #100当手续费
        av_cash=account['可用金额'].tolist()[-1]-100
        for stock in stock_list:
            hist=self.data.get_hist_data_em(stock=stock)
            score=self.mean_line_models(df=hist)
            models=shape_analysis(df=hist)
            down_line=models.get_down_mean_line_sell(n=line)
            if score>=min_score:
                if down_line=='不是':
                    price=self.data.get_spot_data(stock=stock)['最新价']
                    trader_type,amount,price=self.trader.order_value(stock=stock,
                                                value=av_cash,price=price,trader_type='buy')
                    if trader_type=='buy' and amount>=100:
                        print('{} 缓存资金符合最低分{} 符合没有跌均线{} 买入 资金{} 数量{}'.format(stock,min_score,line,av_cash,amount))
                        self.trader.buy(security=stock,price=price,amount=amount)
                        return True
                    else:
                        print('{} 缓存资金符合最低分{} 符合没有跌均线{} 不买入 资金{} 数量{}'.format(stock,min_score,line,av_cash,amount))
                        self.run_reverse_repurchase_of_treasury_bonds_1()
                        return False
                else:
                    print('{}不符合买入均线'.format(stock))
                    self.run_reverse_repurchase_of_treasury_bonds_1()
                    return False
            else:
                print('{}不符合买入的要求最低分数'.format(stock))
                self.run_reverse_repurchase_of_treasury_bonds_1()
                return False
    def run_reverse_repurchase_of_treasury_bonds_1(self):
        '''
        国债逆回购
        '''
        with open(r'{}\自定义资金缓冲区策略.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        buy_ratio=text['国债逆回购比例']
        self.trader.reverse_repurchase_of_treasury_bonds_1(buy_ratio=buy_ratio)
                              
        