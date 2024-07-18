import pandas as pd
import requests
import json
import random
from trader_tool.stock_data import stock_data
from trader_tool.bond_cov_data import bond_cov_data
from trader_tool.shape_analysis import shape_analysis
from trader_tool.etf_fund_data import etf_fund_data
from trader_tool.stock_upper_data import stock_upper_data
from trader_tool.ths_limitup_data import ths_limitup_data
from trader_tool.trader_frame import trader_frame
import pandas as pd
from trader_tool.ths_rq import ths_rq
from tqdm import tqdm
import numpy as np
import json
from  trader_tool import jsl_data
from trader_tool.analysis_models import analysis_models
import os
class micro_stock_cap_trend_trading:
    def __init__(self,trader_tool='qmt',exe='C:/同花顺软件/同花顺/xiadan.exe',tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qq='1029762153@qq.com',open_set='否',qmt_path='D:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55009640',qmt_account_type='STOCK',name='run_micro_stock_cap_trend_trading'):
        '''
        分析模型
        涨停板交易
        '''
        self.exe=exe
        self.tesseract_cmd=tesseract_cmd
        self.qq=qq
        self.trader_tool=trader_tool
        self.open_set=open_set
        self.qmt_path=qmt_path
        self.qmt_account=qmt_account
        self.qmt_account_type=qmt_account_type
        order_frame=trader_frame(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        self.trader=order_frame.get_trader_frame()
        self.stock_data=stock_data()
        self.bond_cov_data=bond_cov_data()
        self.etf_fund_data=etf_fund_data()
        self.ths_rq=ths_rq()
        self.shape_analysis=shape_analysis()
        self.stock_upper_data=stock_upper_data()
        self.ths_limitup_data=ths_limitup_data()
        self.analysis_models=analysis_models()
        self.path=os.path.dirname(os.path.abspath(__file__))
        self.trader.connect()
        self.name=name
    def save_position(self):
        '''
        保存持股数据
        '''
        with open(r'{}/股票微盘股趋势策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        df=self.trader.position()
        def select_bond_cov(x):
            '''
            选择股票
            '''
            if x[:3] in ['000','0001','002','003','300','600','601','603']:
                return '是'
            else:
                return '不是'
        try:
            if df==False:
                print('获取持股失败')
        except:
            if df.shape[0]>0:
                df['选择']=df['证券代码'].apply(select_bond_cov)
                try:
                    df['持股天数']=df['持股天数'].replace('--',1)
                except:
                    df['持股天数']=1
                df1=df[df['选择']=='是']
                df1['交易状态']='未卖'
                df1=df1[df1['股票余额']>=100]
                df1.to_excel(r'持股数据\持股数据.xlsx')
                return df1
            else:
                print('没有持股')
    def save_position_1(self):
        '''
        保存持股数据
        '''
        with open(r'{}/股票微盘股趋势策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        df=self.trader.position()
        print(df)
        def select_bond_cov(x):
            '''
            选择股票
            '''
            if x[:3] in ['000','0001','002','003','300','600','601','603']:
                return '是'
            else:
                return '不是'
        try:
            if df==False:
                print('获取持股失败')
        except:
            if df.shape[0]>0:
                df['选择']=df['证券代码'].apply(select_bond_cov)
                try:
                    df['持股天数']=df['持股天数'].replace('--',1)
                except:
                    df['持股天数']=1
                df1=df[df['选择']=='是']
                df1=df1[df1['股票余额']>=10]
                df1['交易状态']='未卖'
                df1.to_excel(r'持股数据\持股数据.xlsx')
                return df1
            else:
                print('没有持股')
    def select_bond_cov(self,x):
        '''
        选择股票
        '''
        if x[:3] in ['000','0001','002','003','300','600','601','603']:
            return '是'
        else:
            return '不是'
    def save_balance(self):
        '''
        保持账户数据
        '''
        with open(r'{}/股票微盘股趋势策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        df=self.trader.balance()
        df.to_excel(r'账户数据\账户数据.xlsx')
        return df
    def get_new_trader_list(self):
        '''
        获取交易时间
        '''
        date_list=self.stock_data.get_trader_date_list()
        return date_list
    def get_mirco_stock_index_data(self):
        '''
        获取微盘股指数数据
        '''
        if True:
            headers={
                'Referer':'https://m.10jqka.com.cn/',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76'
            }
            n=''
            for i in range(6):
                n+=str(random.randint(1,9))
            url='https://d.10jqka.com.cn/v2/blockrank/883418/199112/d200.js'
            res=requests.get(url=url,headers=headers)
            text=res.text
            stats_index=text.index('(')
            end_index=text.index('})')
            text=text[stats_index+1:end_index+1]
            text=json.loads(text)
            df=pd.DataFrame(text['items'])
            stats= res.status_code
            if str(stats)=='200' and df.shape[0]>0:
                df=df
            else:
                df=pd.DataFrame()
                return '403',df
            return res.status_code,df
    def read_ths_func_data(self,func='get_mirco_stock_index_data()'):
        '''
        读取函数数据
        '''
        func='self.'+func
        while True:
            stats,df=eval(func)
            if df.shape[0]>0:
                df=df
                print('数据获取成功')
                break
            else:
                print('数据获取失败')
        df.to_excel(r'{}\微盘股全部股票\微盘股全部股票.xlsx'.format(self.path))
        return df
    def select_del_st_stock(self):
        '''
        删除st
        '''
        with open(r'{}/股票微盘股趋势策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        def select_st(x):
            if '*ST' in x or 'ST' in x:
                return '是'
            else:
                return '不是'
        df=pd.read_excel(r'{}\微盘股全部股票\微盘股全部股票.xlsx'.format(self.path),dtype='object')
        try:
            del df['Unnamed: 0 ']
        except:
            pass
        df['ST选择']=df['55'].apply(select_st)
        df=df[df['ST选择']=='不是']
        df.rename(columns={'5':"证券代码"},inplace=True)
        df.to_excel(r'{}\剔除ST全部股票\剔除ST全部股票.xlsx'.format(self.path))
        del_select=text['是否开启剔除模块']
        del_list=text['需要剔除的标的前2位']
        def select_func(x):
            if str(x)[:2] in del_list:
                return '剔除'
            else:
                return '不剔除'
        if del_select=='是':
            df['剔除']=df['证券代码'].apply(select_func)
            df=df[df['剔除']=='不剔除']
            df.to_excel(r'{}\选择股票\选择股票.xlsx'.format(self.path))
        else:
            df.to_excel(r'{}\选择股票\选择股票.xlsx'.format(self.path))
        return df
    def get_mean_line_analysis_models(self):
        '''
        均线分析
        '''
        with open(r'{}/股票微盘股趋势策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        df=pd.read_excel(r'{}\选择股票\选择股票.xlsx'.format(self.path),dtype='object')
        try:
            del df['Unnamed: 0 ']
        except:
            pass
        min_score=text['均线最低分数']
        stock_list=df['证券代码']
        score_list=[]
        for i in tqdm(range(len(stock_list))):
            stock=stock_list[i]
            try:
                hist=self.stock_data.get_stock_hist_data_em(stock)
                score=self.analysis_models.mean_line_models(df=hist)
                score_list.append(score)
            except:
                score_list.append(None)
        df['均线得分']=score_list
        df=df[df['均线得分']>=min_score]
        df.to_excel(r'{}\选择股票\选择股票.xlsx'.format(self.path))
        return df
    def get_stock_shape_analysis(self):
        '''
        形态分析
        '''
        df=pd.read_excel(r'{}\选择股票\选择股票.xlsx'.format(self.path),dtype='object')
        try:
            del df['Unnamed: 0 ']
        except:
            pass
        df1=self.analysis_models.get_shape_analysis(df=df)
        df1.to_excel(r'{}\选择股票\选择股票.xlsx'.format(self.path))
    def get_stock_return_analysis(self):
        '''
        收益分析
        '''
        with open(r'{}/股票微盘股趋势策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        n=text['最近N天']
        max_retuen=text['最近N天最大收益率']
        min_return=text['最近N天最小收益率']
        max_down=text['最近N天最大回撤']
        min_secore=text['均线最低分数']
        df=pd.read_excel(r'{}\选择股票\选择股票.xlsx'.format(self.path),dtype='object')
        try:
            del df['Unnamed: 0 ']
        except:
            pass
        df1=self.analysis_models.get_stock_mean_line_retuen_analysis(df=df,n=n,max_retuen=max_retuen,
                    min_return=min_return,max_down=max_down)
        df1.to_excel(r'{}/交易股票池/交易股票池.xlsx'.format(self.path))
    def get_del_buy_sell_data(self):
        '''
        处理交易股票池买入股票
        '''
        print('处理交易股票池买入股票')
        with open(r'{}/股票微盘股趋势策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        limit=text['持股限制']
        df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        df1=df[df['可用余额']>=10]
        hold_stock_list=df['证券代码'].tolist()
        trader_df=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path),dtype='object')
        def select_data(stock):
            if stock in hold_stock_list:
                try:
                    num=df1[df1['证券代码']==stock]['可用余额'].tolist()[-1]
                    if float(num)>=float(limit):
                        return '持股超过限制'
                    else:
                        return '持股不足'
                except:
                    return '持股超过限制'
            else:
                return '没有持股'
        trader_df['持股检查']=trader_df['证券代码'].apply(select_data)
        trader_df=trader_df[trader_df['持股检查'] !='持股超过限制']
        trader_df=trader_df.sort_values(by='均线得分',ascending=False)
        sell_list=[]
        n=text['跌破N日均线卖出']
        for stock in trader_df['证券代码'].tolist():
            try:
                hist_df=self.stock_data.get_stock_hist_data_em(stock=stock)
                models=shape_analysis(df=hist_df)
                mean_line=models.get_down_mean_line_sell(n=n)
                if mean_line=='是':
                    sell_list.append('是')
                else:
                    sell_list.append('不是')
            except:
                print('{}有问题'.format(stock))
                sell_list.append('是')
        
        trader_df['跌破均线']=sell_list
        trader_df=trader_df[trader_df['跌破均线']=='不是']  
        trader_df.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
        return trader_df
    def get_buy_sell_stock(self):
        '''
        获取买卖数据
        '''
        print('获取买卖数据')
        with open('{}/股票微盘股趋势策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        buy_num=text['买入前N']
        hold_limit=text['持有限制']
        df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        hold_min_score=text['持有均线最低分']
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
        except:
            pass
        trader_df=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path),dtype='object')
        print('交易股票池*******************')
        print(trader_df)
        trader_df['选择']=trader_df['证券代码'].apply(select_stock)
        trader_df=trader_df[trader_df['选择']=='持股不足']
        select=text['是否开启持股周期']
        hold_daily_limit=text['持股持股周期天数']
        try:
            del trader_df['Unnamed: 0']
        except:
            pass
        if df1.shape[0]>0:
            #卖出列表
            sell_list=[]
            #持股列表
            hold_stock_list=df['证券代码'].tolist()
            #排名列表
            if select=='是':
                for stock in hold_stock_list:
                    hold_daily=df[df['证券代码']==stock]['持股天数'].tolist()[-1]
                    if hold_daily>=hold_daily_limit:
                        sell_list.append(stock)
                    else:
                        print('人气排行目前持股 {} 没有大于{}'.format(hold_daily,hold_daily_limit))
            else:
                print('不启动持股限制')
            #对持有的可转债做均线分析
            for stock in hold_stock_list:
                try:
                    bond_data=self.stock_data.get_stock_hist_data_em(stock=stock)
                    socre=self.mean_line_models(df=bond_data)
                    if socre<hold_min_score:
                        if select=='是':
                            hold_daily=df[df['证券代码']==stock]['持股天数'].tolist()[-1]
                            if hold_daily>=hold_daily_limit:
                                sell_list.append(stock)
                            else:
                                print('持有的可转债做均线分析目前持股 {} 没有大于{}'.format(hold_daily,hold_daily_limit))
                        else:
                            sell_list.append(stock)
                            print('{} 目前{}分数 不符合最低分数{}'.format(stock,socre,hold_min_score))
                except:
                    print('均线分析有问题{}'.format(stock))
            #跌破均线分析
            n=text['跌破N日均线卖出']
            for stock in hold_stock_list:
                    try:
                        hist_df=self.stock_data.get_stock_hist_data_em(stock=stock)
                        models=shape_analysis(df=hist_df)
                        mean_line=models.get_down_mean_line_sell(n=n)
                        if mean_line=='是':
                            sell_list.append(stock)
                            print('{}跌破均线'.format(stock))
                        else:
                            pass
                    except:
                        pass
            sell_df=pd.DataFrame()
            print('************************')
            print(sell_list)
            sell_df['证券代码']=sell_list
            sell_df['交易状态']='未卖'
            #剔除新股申购
            sell_df['选择']=sell_df['证券代码'].apply(self.select_bond_cov)
            sell_df=sell_df[sell_df['选择']=='是']
            if sell_df.shape[0]>0:
                print('卖出可转债*****************')
                print(sell_df)
                sell_df['策略名称']=self.name
                sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
            else:
                print('没有卖出的可转债')
                sell_df['证券代码']=[None]
                sell_df['交易状态']=[None]
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
            print('买入可转债*****************')
            print(buy_df)
            buy_df['策略名称']=self.name
            buy_df.to_excel(r'买入股票\买入股票.xlsx')
            return buy_df
        else:
            buy_df=trader_df[:hold_limit]
            buy_df['交易状态']='未买'
            print('买入可转债*****************')
            print(buy_df)
            buy_df['策略名称']=self.name
            buy_df.to_excel(r'买入股票\买入股票.xlsx')
            return buy_df
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
            
            buy_df=buy_df[buy_df['品种']=='stock']
            buy_df.to_excel(r'买入股票\买入股票.xlsx')
            print(buy_df)
        else:
            pass
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
            sell_df=sell_df[sell_df['品种']=='stock']
            sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
            print(sell_df)
        else:
            pass
    def update_all_data(self):
        '''
        更新数据
        '''
        self.save_position()
        self.save_balance()
        self.read_ths_func_data()
        self.select_del_st_stock()
        self.get_mean_line_analysis_models()
        self.get_stock_shape_analysis()
        self.get_stock_return_analysis()
        self.get_del_buy_sell_data()
        self.get_buy_sell_stock()
        self.get_del_not_trader_stock()

        
