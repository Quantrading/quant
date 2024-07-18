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
from .user_def_stock_data import user_def_stock_data
class custom_stock_pool_rotation:
    def __init__(self,trader_tool='ths',exe='C:/同花顺软件/同花顺/xiadan.exe',tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qq='1029762153@qq.com',open_set='否',qmt_path='D:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55009640',qmt_account_type='STOCK',name='customize_trading_strategies'):
        '''
        自定义股票池轮动模型
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
        self.user_models=user_def_stock_data()
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
        if mean_5>mean_10:
            score+=25
        if mean_10>mean_20:
            score+=25
        if mean_20>mean_30:
            score+=25
        if mean_30>mean_60:
            score+=25
        return score
    def dea_user_def_models(self):
        '''
        处理自定义轮动股票池
        '''
        with open(r'{}\自定义股票池轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        user=text['是否开启自定义函数']
        user_def_list=text['自定义函数']
        if user=='是':
            print('开启自定义函数选股**********************************')
            for func in user_def_list:
                func="self.user_models.{}".format(func)
        else:
            print('不开启自定义函数选股***********************************')
        trend=text['是否开启趋势轮动']
        n=text['跌破N日均线卖出']
        min_score=text['均线最低分数']
        try:
            df=pd.read_excel(r'{}\自定义轮动股票池\自定义轮动股票池.xlsx'.format(self.path),dtype='object')
        except:
            df=pd.read_csv(r'{}\自定义轮动股票池\自定义轮动股票池.csv'.format(self.path),dtype='object')
        if df.shape[0]>0:
            try:
                df['证券代码']=df['可转债代码']
            except:
                try:
                    df['证券代码']=df['股票代码']
                except:
                    try:
                        df['证券代码']=df['基金代码']
                    except:
                        try:
                            df['证券代码']=df['代码']
                        except:
                            try:
                                df['证券代码']=df['code']
                            except:
                                try:
                                    df['证券代码']=df['证券代码']
                                except:
                                    df['证券代码']=df['转债代码']
            df['证券代码']=df['证券代码'].apply(lambda x :str(x)[:6])
            df['证券代码']=df['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
            stock_list=df['证券代码'].tolist()
            score_list=[]
            line_list=[]
            if trend=='是':
                for stock in stock_list:
                    try:
                        hist=self.data.get_hist_data_em(stock=stock)
                        models=shape_analysis(df=hist)
                        shape=models.get_down_mean_line_sell(n=n)
                        if shape=='是':
                            line_list.append('是')
                        else:
                            line_list.append('不是')
                        score=self.mean_line_models(df=hist)
                        score_list.append(score)
                    except:
                        line_list.append('是')
                        score_list.append(0)
                df['趋势']=line_list
                df['得分']=score_list
                df=df[df['趋势']=='不是']
                df=df[df['得分']>=min_score]
            else:
                df=df
            trader_df=df
            trader_df['证券代码']=trader_df['证券代码'].astype(str)
            hold_df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
            hold_df['证券代码']=hold_df['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
            if hold_df.shape[0]>0:
                hold_df['证券代码']=hold_df['证券代码'].astype(str)
                hold_stock_list=hold_df['证券代码'].tolist()
            else:
                print('没有持股数据）））））））））））））')
                hold_stock_list=[]
            trader_df['证券代码']=trader_df['证券代码'].astype(str)
            def select_data(stock):
                if str(stock) in hold_stock_list:
                    return '持股超过限制'
                else:
                    return '没有持股'
            trader_df['持股检查']=trader_df['证券代码'].apply(select_data)
            trader_df=trader_df[trader_df['持股检查'] !='持股超过限制']
            trader_df.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
        else:
            df=pd.DataFrame()
            df.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
    def get_buy_sell_stock(self):
        '''
        获取买卖数据
        '''
        with open('{}\自定义股票池轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        trend=text['是否开启趋势轮动']
        n=text['跌破N日均线卖出']
        hold_min_score=text['持有均线最低分']
        buy_num=text['买入前N']
        hold_limit=text['持有限制']
        hold_rank=text['持有排名前N']
        sell_rank=text['跌出排名卖出N']
        df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        try:
            del df['Unnamed: 0']
        except:
            pass
        trader_df=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path),dtype='object')
        trader_df['证券代码']=trader_df['证券代码'].astype(str)
        try:
            del trader_df['Unnamed: 0']
        except:
            pass
        sell_list=[]
        if trader_df.shape[0]>0:
            df1=df[df['可用余额']>=10]
            if df1.shape[0]>0:
                df['证券代码']=df['证券代码'].astype(str)
                df1['证券代码']=df1['证券代码'].apply(lambda x:'0'*(6-len(str(x)))+str(x))
                hold_stock_list=df['证券代码'].tolist()
                def select_stock(x):
                    '''
                    选择股票
                    '''
                    if x in hold_stock_list:
                        return '持股'
                    else:
                        return "持股不足"
                #卖出列表
                #持股列表
                trader_df['选择']=trader_df['证券代码'].apply(select_stock)
                trader_df['证券代码']=trader_df['证券代码'].apply(lambda x:'0'*(6-len(str(x)))+str(x))
                trader_df=trader_df[trader_df['选择']=='持股不足']
                hold_stock_list=df1['证券代码'].tolist()
                #对持有的可转债做均线分析
                if trend=='是':
                    for stock in hold_stock_list:
                        try:
                            bond_data=self.data.get_hist_data_em(stock=stock)
                            socre=self.mean_line_models(df=bond_data)
                            if socre<hold_min_score:
                                print('{} {}分数不符合最低{}分'.format(stock,socre,hold_min_score))
                                sell_list.append(stock)
                            else:
                                print('{}符合最低分{}'.format(stock,hold_min_score))
                        except:
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
                            except:
                                pass
                else:
                    #存在轮动
                    stock_list=trader_df['证券代码'].tolist()
                    for stock in hold_stock_list:
                        if stock in stock_list:
                            if stock in stock_list[:hold_rank]:
                                print('{}持股在股票池并且在排名前{}不卖出'.format(stock,hold_rank))
                            elif stock in stock[:sell_rank]:
                                print('{}持股在股票池并且在排名前{}不卖出'.format(stock,sell_rank))
                            else:
                                print('{}持股在股票池并且在排名 {}外 卖出'.format(stock,sell_rank))
                                sell_list.append(stock)
                        else:
                            print('{}不在股票池直接卖出'.format(stock))
                            sell_list.append(stock)
                sell_df=pd.DataFrame()
                sell_list=list(set(sell_list))
                sell_df['证券代码']=sell_list
                sell_df['交易状态']='未卖'
                if sell_df.shape[0]>0:
                    print('卖出*****************')
                    print(sell_df)
                    sell_df=sell_df[['证券代码','交易状态']]
                    sell_df['证券代码']=sell_df['证券代码'].apply(lambda x:'0'*(6-len(str(x)))+str(x))
                    sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
                else:
                    print('没有卖出的可转债')
                    sell_df=pd.DataFrame()
                    sell_df['证券代码']=None
                    sell_df['交易状态']=None
                    sell_df['策略名称']=self.name
                    sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
                hold_num=df1.shape[0]
                if hold_num>0:
                    av_buy_num=hold_limit-hold_num
                    av_buy_num=av_buy_num+sell_df.shape[0]
                    if av_buy_num>=hold_limit:
                        av_buy_num=hold_limit
                    else:
                        av_buy_num=av_buy_num
                    buy_df=trader_df[:av_buy_num]
                else:
                    buy_df=trader_df[:buy_num]
                buy_df['交易状态']='未买'
                print('买入*****************')
                print(buy_df)
                buy_df=buy_df[['证券代码','交易状态']]
                buy_df['证券代码']=buy_df['证券代码'].apply(lambda x:'0'*(6-len(str(x)))+str(x))
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
            print('没有轮动股票池保存仓位')
    def get_time_rotation(self):
        '''
        轮动方式
        '''
        with open('{}/自定义股票池轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        now_date=''.join(str(datetime.now())[:10].split('-'))
        now_time=time.localtime()                               
        trader_type=text['轮动方式']                               
        trader_wday=text['每周轮动时间']                               
        moth_trader_time=text['每月轮动时间']
        specific_time=text['特定时间']
        year=now_time.tm_year
        moth=now_time.tm_mon
        wday=now_time.tm_wday
        daily=now_time.tm_mday
        if trader_type=='每天':
            print('轮动方式每天')
            return True
        elif trader_type=='每周':
            if trader_wday==wday:
                return True
            elif trader_wday<wday:
                print('安周轮动 目前星期{} 轮动时间星期{} 目前时间大于轮动时间不轮动'.format(wday+1,trader_wday+1))
                return False
            else:
                print('安周轮动 目前星期{} 轮动时间星期{} 目前时间小于轮动时间不轮动'.format(wday+1,trader_wday+1))
                return False
        elif trader_type=='每月轮动时间':
            stats=''
            for date in moth_trader_time:
                data=''.join(data.split('-'))
                if int(moth_trader_time)==int(date):
                    print('安月轮动 目前{} 轮动时间{} 目前时间等于轮动时间轮动'.format(now_date,date))
                    stats=True
                    break
                elif int(moth_trader_time)<int(date):
                    print('安月轮动 目前{} 轮动时间{} 目前时间小于轮动时间轮动'.format(now_date,date))
                    stats=False
                else:
                    print('安月轮动 目前{} 轮动时间{} 目前时间大于轮动时间轮动'.format(now_date,date))
                    stats=False
            return stats
        else:
            #特别时间
            stats=''
            for date in specific_time:
                data=''.join(data.split('-'))
                if int(specific_time)==int(date):
                    print('安月轮动 目前{} 轮动时间{} 目前时间等于轮动时间轮动'.format(now_date,date))
                    stats=True
                    break
                elif int(specific_time)<int(date):
                    print('安月轮动 目前{} 轮动时间{} 目前时间小于轮动时间轮动'.format(now_date,date))
                    stats=False
                else:
                    print('安月轮动 目前{} 轮动时间{} 目前时间大于轮动时间轮动'.format(now_date,date))
                    stats=False
            return stats               
    def updata_all_data(self):
        '''
        更新全部数据
        '''
        with open(r'{}/自定义股票池轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        if self.get_time_rotation()==True:
            print("今天{} 是轮动时间".format(datetime.now()))
            self.save_position()
            self.save_balance()
            self.dea_user_def_models()
            self.get_buy_sell_stock()
        else:
            print("今天{} 不是是轮动时间".format(datetime.now()))





                            
