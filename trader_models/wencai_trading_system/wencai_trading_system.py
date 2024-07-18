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
from trader_tool.xueqie_data import xueqie_data
from datetime import datetime
import time
import pywencai
class wencai_trading_system:
    def __init__(self,trader_tool='qmt',exe='C:/同花顺软件/同花顺/xiadan.exe',tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qq='1029762153@qq.com',open_set='否',qmt_path='D:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55009640',qmt_account_type='STOCK',name='customize_trading_strategies'):
        '''
        问财交易系统
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
    def get_wencai_data(self,text='人气排行'):
        '''
        获取问财数据
        '''
        try:
            df=pywencai.get(query=text,loop=True)
            return df
        except Exception as e:
            print(e)
            print('{}问题数据有问题'.format(text))
            df=pd.DataFrame()
            return df
    def get_buy_data(self):
        '''
        获取买入数据
        '''
        with open(r'{}\问财交易系统.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        is_open=text['是否开启买入条件']
        buy_list=text['买入条件']
        columns=text['买入的证券代码名称']
        if is_open=='是':
            print('开启买入条件************')
            df=self.get_wencai_data(text=buy_list)
            try:
                df['证券代码']=df[columns].apply(lambda x:str(x).split('.')[0])
            except:
                df['证券代码']=df[columns]
            print('买入的问财数据***********')
            print(df)
            df.to_excel(r'{}\买入数据\买入数据.xlsx'.format(self.path))
        else:
            print('不开启问财买入条件**************')
            df=pd.DataFrame()
            df.to_excel(r'{}\买入数据\买入数据.xlsx'.format(self.path))
    def get_sell_data(self):
        '''
        获取卖出数据
        '''
        with open(r'{}\问财交易系统.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        is_open=text['是否开启卖出条件']
        sell_list=text['卖出条件']
        columns=text['卖出的证券代码名称']
        if is_open=='是':
            print('开启卖出条件************')
            df=self.get_wencai_data(text=sell_list)
            try:
                df['证券代码']=df[columns].apply(lambda x:str(x).split('.')[0])
            except:
                df['证券代码']=df[columns]
            print('卖出的问财数据***********')
            print(df)
            df.to_excel(r'{}\卖出数据\卖出数据.xlsx'.format(self.path))
        else:
            print('不开启问财买入条件**************')
            df=pd.DataFrame()
            df.to_excel(r'{}\卖出数据\卖出数据.xlsx'.format(self.path))
    def dea_trader_data(self):
        '''
        处理交易股票池
        '''
        df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        df1=df[df['股票余额']>=10]
        if df1.shape[0]>0:
            df1['证券代码']=df1['证券代码'].apply(lambda x:'0'*(6-len(str(x)))+str(x))
            hold_stock_list=df1['证券代码'].tolist()

        else:
            hold_stock_list=[]
        trader_df=pd.read_excel(r'{}\买入数据\买入数据.xlsx'.format(self.path),dtype='object')
        if trader_df.shape[0]>0:
            trader_df['证券代码']=trader_df['证券代码'].apply(lambda x:'0'*(6-len(str(x)))+str(x))
            def select_data(stock):
                if str(stock) in hold_stock_list:
                    return '持股超过限制'
                else:
                    return '没有持股'
            trader_df['持股检查']=trader_df['证券代码'].apply(select_data)
            trader_df=trader_df[trader_df['持股检查'] !='持股超过限制']
            trader_df.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
        else:
            print('没有交易股票池数据******************')
            trader_df=pd.DataFrame()
            trader_df.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
    def get_time_rotation(self):
        '''
        轮动方式
        '''
        with open(r'{}\问财交易系统.json'.format(self.path),encoding='utf-8') as f:
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
    def get_buy_sell_data(self):
        '''
        获取买卖数据
        '''   
        with open(r'{}\问财交易系统.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)  
        buy_num=text['买入排名前N']
        hold_limit=text['持有限制']
        buy_list=[]
        sell_list=[]
        buy_df=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
        sell_df=pd.read_excel(r'{}\卖出数据\卖出数据.xlsx'.format(self.path))
        hold_stock=pd.read_excel(r'持股数据\持股数据.xlsx'.format(self.path))
        hold_stock=hold_stock[hold_stock['股票余额']>=10]
        if hold_stock.shape[0]>0:
            hold_stock['证券代码']=hold_stock['证券代码'].apply(lambda x:'0'*(6-len(str(x)))+str(x))
            if sell_df.shape[0]>0:
                hold_stock_list=hold_stock['证券代码'].tolist()
                sell_df['证券代码']=sell_df['证券代码'].apply(lambda x:'0'*(6-len(str(x)))+str(x))
                sell_stock_list=sell_df['证券代码'].tolist()
                for stock in hold_stock_list:
                    if stock in sell_stock_list:
                        print('持股{} 在卖出列表'.format(stock))
                        sell_list.append(stock)
                    else:
                        print('持股{} 不在卖出列表继续持有'.format(stock))
            else:
                print('没有卖出的数据*******************')
        else:
            print('没有持股数据***************')
        sell=pd.DataFrame()
        sell['证券代码']=sell_list
        sell['交易状态']='未卖'
        print('卖出股票**************')
        print(sell)
        sell.to_excel(r'卖出股票\卖出股票.xlsx')
        if hold_stock.shape[0]>0:
            hold_num=hold_stock.shape[0]
        else:
            hold_num=0
        if buy_df.shape[0]>0:
            buy_df['证券代码']=buy_df['证券代码'].apply(lambda x:'0'*(6-len(str(x)))+str(x))
            buy_stock_list=buy_df['证券代码'].tolist()
            print(buy_stock_list)
            sell_num=sell.shape[0]
            av_buy=hold_limit-hold_num+sell_num
            print(av_buy,'((((((((((((((((((((((((()))))))))))))))))))))))))')
            if av_buy>=hold_limit:
                av_buy=hold_limit
            else:
                av_buy=av_buy
            buy=pd.DataFrame()
            buy['证券代码']=buy_stock_list[:av_buy]
            buy['交易状态']='未买'
            print('买入股票**********')
            print(buy)
            buy.to_excel(r'买入股票\买入股票.xlsx')
        else:
            print('没有买入的数据*****************')
    def get_del_not_trader_stock(self):
        '''
        剔除黑名单
        '''
        print('剔除黑名单______________*************************_______________________')
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
        def select_del_stock_list(x):
            if str(x)[:6] in del_stock_list:
                return '是'
            else:
                return '否'
        buy_df=pd.read_excel(r'买入股票\买入股票.xlsx',dtype='object')
        if buy_df.shape[0]>0:
            buy_df['证券代码']=buy_df['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
            try:
                del buy_df['Unnamed: 0']
            except:
                pass
            buy_df['黑名单']=buy_df['证券代码'].apply(select_del_stock_list)
            buy_df=buy_df[buy_df['黑名单']=='否']
            #隔离策略
            buy_df['证券代码']=buy_df['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
            buy_df['品种']=buy_df['证券代码'].apply(lambda x: self.trader.select_data_type(x))
            print('买入股票））））））））））））））））））））')
            buy_df.to_excel(r'买入股票\买入股票.xlsx')
            print(buy_df)
        else:
            print("没有买入的股票））））））））））））））")
        #卖出
        sell_df=pd.read_excel(r'卖出股票\卖出股票.xlsx',dtype='object')
        if sell_df.shape[0]>0:
            sell_df['证券代码']=sell_df['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
            try:
                del sell_df['Unnamed: 0']
            except:
                pass
            sell_df['黑名单']=sell_df['证券代码'].apply(select_del_stock_list)
            sell_df=sell_df[sell_df['黑名单']=='否']
            #隔离策略
            sell_df['证券代码']=sell_df['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
            sell_df['品种']=sell_df['证券代码'].apply(lambda x: self.trader.select_data_type(x))
            print('卖出股票））））））））））））））））））））')
            sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
            print(sell_df)
        else:
            print('没有卖出的股票）））））））））））））））））））')
    def updata_all_data(self):
        '''
        更新全部数据
        '''
        if self.get_time_rotation()==True:
            print("今天{} 是轮动时间".format(datetime.now()))
            self.save_position()
            self.save_balance()
            self.get_buy_data()
            self.get_sell_data()
            self.dea_trader_data()
            self.get_buy_sell_data()
            self.get_del_not_trader_stock()
                
        else:
            print("今天{} 不是是轮动时间".format(datetime.now()))

                
                
















    




