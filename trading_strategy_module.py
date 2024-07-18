'''
开发自己的策略
自定义交易策略模块
模式一改变买入股票文件夹买入股票数据就可以，卖出股票文件夹卖出股票数据就可以
只需要证券代码，交易状态就可以
买入股票文件夹数据格式
证券代码 交易状态
600031   未买
600111   未买
卖出股票文件夹格式
证券代码 交易状态
600031   未卖
600111   未卖
交易模式2
直接参考trader_strategy.py开发成一个完整的框架
'''
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
class trading_strategy_module:
    def __init__(self,trader_tool='qmt',exe='C:/同花顺软件/同花顺/xiadan.exe',tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qq='1029762153@qq.com',open_set='否',qmt_path='D:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55009640',qmt_account_type='STOCK',name='customize_trading_strategies',trader_type='全部'):
        '''
        分析模型
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
        self.trader.connect()
        self.trader_type=trader_type
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
        trader_type=self.trader_type
        def select_del_stock_list(x):
            if str(x)[:6] in del_stock_list:
                return '是'
            else:
                return '否'
        df=self.trader.position()
        try:
            if df==False:
                print('获取持股失败')
        except Exception as e:
            print("运行错误:",e)
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
        if mean_5>mean_10:
            score+=25
        if mean_10>mean_20:
            score+=25
        if mean_20>mean_30:
            score+=25
        if mean_30>mean_60:
            score+=25
        return score
    def get_del_buy_sell_data(self):
        '''
        处理交易股票池买入股票
        '''
        with open(r'分析配置.json',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        limit=text['持股限制']
        n=text['自定义交易品种跌破N日均线卖出']
        df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        df1=df[df['可用余额']>=10]
        hold_stock_list=df['证券代码'].tolist()
        trader_df=self.ths_rq.get_hot_stock_rank()[:20]
        print('自定义交易股票池****************')
        print(trader_df)
        if trader_df.shape[0]>0:
            trader_df['证券代码']=trader_df['证券代码'].astype(str)
            def select_data(stock):
                if stock in hold_stock_list:
                    try:
                        num=df1[df1['证券代码']==stock]['可用余额'].tolist()[-1]
                        if float(num)>=float(limit):
                            return '持股超过限制'
                        else:
                            return '持股不足'
                    except Exception as e:
                        print("运行错误:",e)
                        return '持股超过限制'
                else:
                    return '没有持股'
            trader_df['持股检查']=trader_df['证券代码'].apply(select_data)
            trader_df=trader_df[trader_df['持股检查'] !='持股超过限制']
            hold_stock_list=trader_df['证券代码'].tolist()
            sell_list=[]
            mean_score_list=[]
            for stock in hold_stock_list:
                try:
                    hist_df=self.data.get_hist_data_em(stock=stock)
                    score=self.mean_line_models(df=hist_df)
                    mean_score_list.append(score)
                    models=shape_analysis(df=hist_df)
                    mean_line=models.get_down_mean_line_sell(n=n)
                    if mean_line=='是':
                        sell_list.append('是')
                    else:
                        sell_list.append('不是')
                except Exception as e:
                    print("运行错误:",e)
                    print('{}有问题--处理交易股票池买入股票'.format(stock))
                    mean_score_list.append(None)
                    sell_list.append('是')
            trader_df['跌破均线']=sell_list
            trader_df['均线得分']=mean_score_list
            trader_df=trader_df[trader_df['跌破均线']=='不是']  
            trader_df=trader_df.sort_values(by='均线得分',ascending=False)
            trader_df.to_excel(r'买入股票\买入股票.xlsx')
            print(trader_df)
            return trader_df
        else:
            print('-处理交易股票池买入股票,买入文件没有数据')
    def get_buy_sell_stock(self):
        '''
        获取买卖数据
        '''
        with open('分析配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        buy_num=text['买入前N']
        hold_limit=text['持有限制']
        df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        hold_min_score=text['自定义交易品种持有分数']
        df1=df[df['可用余额']>=10]
        hold_stock_list=df['证券代码'].tolist()
        def select_stock(x):
            '''
            选择股票
            '''
            if x in hold_stock_list:
                return '持股不足'
            else:
                return "持股不足"
        try:
            del df['Unnamed: 0']
        except Exception as e:
            print("运行错误:",e)
        trader_df=pd.read_excel(r'买入股票\买入股票.xlsx',dtype='object')
        try:
            del trader_df['Unnamed: 0']
        except Exception as e:
            print("运行错误:",e)
        sell_df=pd.read_excel(r'卖出股票\卖出股票.xlsx')
        if sell_df.shape[0]>0:
            sell_df['证券代码']=sell_df['证券代码'].astype(str)
            sell_list=sell_df['证券代码'].tolist()
        else:
            print('卖出文件没有数据')
            sell_list=[]
        if trader_df.shape[0]>0:
            trader_df['选择']=trader_df['证券代码'].apply(select_stock)
            trader_df=trader_df[trader_df['选择']=='持股不足']
            if df1.shape[0]>0:
                #卖出列表
                
                #持股列表
                hold_stock_list=df['证券代码'].tolist()
                #对持有的可转债做均线分析
                for stock in hold_stock_list:
                    try:
                        bond_data=self.data.get_hist_data_em(stock=stock)
                        socre=self.mean_line_models(df=bond_data)
                        if socre<hold_min_score:
                            print('{} {}分数不符合最低{}分'.format(stock,socre,hold_min_score))
                            sell_list.append(stock)
                        else:
                            pass
                    except Exception as e:
                        print("运行错误:",e)
                        print('{}卖出数据有问题'.format(stock))
                #跌破均线分析
                n=text['自定义交易品种跌破N日均线卖出']
                for stock in hold_stock_list:
                        try:
                            hist_df=self.data.get_hist_data_em(stock=stock)
                            models=shape_analysis(df=hist_df)
                            mean_line=models.get_down_mean_line_sell(n=n)
                            if mean_line=='是':
                                sell_list.append(stock)
                                print('{}跌破均线'.format(stock))
                            else:
                                pass
                        except Exception as e:
                            print("运行错误:",e)
                sell_df=pd.DataFrame()
                sell_df['证券代码']=sell_list
                sell_df['交易状态']='未卖'
                if sell_df.shape[0]>0:
                    print('卖出*****************')
                    print(sell_df)
                    sell_df['策略名称']=self.name
                    sell_df=sell_df[['证券代码','交易状态']]
                    sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
                else:
                    print('没有卖出的可转债')
                    sell_df['证券代码']=[None]
                    sell_df['交易状态']=[None]
                    sell_df['策略名称']=self.name
                    sell_df=sell_df[['证券代码','交易状态']]
                    sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
                hold_num=df1.shape[0]
                if hold_num>0:
                    av_buy_num=hold_limit-hold_num
                    av_buy_num=av_buy_num+sell_df.shape[0]
                    buy_df=trader_df[:av_buy_num]
                else:
                    buy_df=trader_df[:buy_num]
                buy_df['交易状态']='未买'
                print('买入*****************')
                print(buy_df)
                buy_df=buy_df[['证券代码','交易状态']]
                buy_df.to_excel(r'买入股票\买入股票.xlsx')
                return buy_df
            else:
                buy_df=trader_df[:hold_limit]
                buy_df['交易状态']='未买'
                print('买入*****************')
                print(buy_df)
                buy_df=buy_df[['证券代码','交易状态']]
                buy_df.to_excel(r'买入股票\买入股票.xlsx')
                return buy_df
        else:
            print('买入股票文件没有数据')
    def update_all_data(self):
        '''
        更新策略数据
        '''
        print(self.save_position())
        print(self.save_balance())
        self.get_del_buy_sell_data()
        self.get_buy_sell_stock()
if __name__=='__main__':
    models=trading_strategy_module()
    models.update_all_data()