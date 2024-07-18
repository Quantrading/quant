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
import os
class bond_cov_popularity_strategy:
    def __init__(self,trader_tool='ths',exe='C:/同花顺软件/同花顺/xiadan.exe',tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qq='1029762153@qq.com',open_set='否',qmt_path='D:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55009640',qmt_account_type='STOCK',name='run_bond_cov_popularity_strategy'):
        '''
        分析模型可转债热门模型
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
        self.path=os.path.dirname(os.path.abspath(__file__))
        self.trader.connect()
        self.name=name
    def save_position(self):
        '''
        保存持股数据
        '''
        df=self.trader.position()
        def select_bond_cov(x):
            '''
            选择可转债
            '''
            if x[:3] in ['110','113','123','127','128','111'] or x[:2] in ['11','12']:
                return '是'
            else:
                return '不是'
        try:
            if df==False:
                print('获取持股失败')
        except:
            if df.shape[0]>0:
                df['选择']=df['证券代码'].apply(select_bond_cov)
                df1=df[df['选择']=='是']
                df1=df1[df1['可用余额']>=10]
                df1.to_excel(r'持股数据\持股数据.xlsx')
                return df1
            else:
                print('没有持股')
    def save_position_1(self):
        '''
        保存持股数据
        '''
        df=self.trader.position()
        def select_bond_cov(x):
            '''
            选择可转债
            '''
            if x[:3] in ['110','113','123','127','128','111'] or x[:2] in ['11','12']:
                return '是'
            else:
                return '不是'
        try:
            if df==False:
                print('获取持股失败')
        except:
            if df.shape[0]>0:
                df['选择']=df['证券代码'].apply(select_bond_cov)
                df1=df[df['选择']=='是']
                #df1=df1[df1['可用余额']>=10]
                df1.to_excel(r'持股数据\持股数据.xlsx')
                return df1
            else:
                print('没有持股')
   
    def select_bond_cov(self,x):
        '''
        选择证券代码
        '''
        if x[:3] in ['110','113','123','127','128','111'] or x[:2] in ['11','12']:
            return '是'
        else:
            return '不是'
    def save_balance(self):
        '''
        保持账户数据
        '''
        with open(r'{}/可转债人气模型交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        df=self.trader.balance()
        df.to_excel(r'账户数据\账户数据.xlsx')
        return df
    def get_ths_rq_data(self):
        '''
        获取同花顺人气数据
        '''
        df=self.ths_rq.get_cov_bond_rot_rank()
        df.to_excel(r'{}\同花顺人气原始数据\同花顺人气原始数据.xlsx'.format(self.path))
        return df
    def get_concact_data(self):
        '''
        获取合并数据
        '''
        df=pd.read_excel(r'{}\同花顺人气原始数据\同花顺人气原始数据.xlsx'.format(self.path),dtype='object')
        try:
            del df['Unnamed: 0']
        except:
            pass
        stock_list=df['代码'].tolist()
        price_list=[]
        for i in tqdm(range(len(stock_list))):
            stock=stock_list[i]
            try:
                df1=self.bond_cov_data.get_cov_bond_spot(stock=stock)
                price=df1['最新价']
                price_list.append(price)
            except:
                price_list.append(None)
        df['最新价']=price_list
        df.to_excel(r'{}\合并数据\合并数据.xlsx'.format(self.path))
        return df
    def select_cov_bond_data(self):
        '''
        选择股票
        '''
        with open(r'{}/可转债人气模型交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        max_price=text['价格上限']
        min_price=text['价格下限']
        max_spot_zdf=text['实时涨跌幅上限']
        min_spot_zdf=text['实时涨跌幅下限']
        df=pd.read_excel(r'{}\合并数据\合并数据.xlsx'.format(self.path),dtype='object')
        try:
            del df['Unnamed: 0']
        except:
            pass
        df1=df[df['最新价']<=max_price]
        df2=df1[df1['最新价']>=min_price]
        df3=df2[df2['涨跌幅']<=max_spot_zdf]
        df4=df3[df3['涨跌幅']>=min_spot_zdf]
        df4.to_excel(r'{}\选择可转债\选择可转债.xlsx'.format(self.path))
        return df4
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
    def get_return_ananlysis(self,df='',n=5):
        '''
        收益率分析
        '''
        #涨跌幅
        df1=df
        prices=df1[-n:]['close']
        zdf= ((prices.iloc[-1] / prices.iloc[0]) - 1)*100
        #最大回撤
        max_down_result=((prices / prices.expanding(min_periods=1).max()).min() - 1)*100
        #累计收益】
        return zdf,max_down_result
    def get_stock_mean_line_retuen_analysis(self):
        '''
        可转债均线收益分析
        '''
        with open(r'{}/可转债人气模型交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        n=text['最近N天']
        max_retuen=text['最近N天最大收益率']
        min_return=text['最近N天最小收益率']
        max_down=text['最近N天最大回撤']
        min_secore=text['均线最低分数']
        mean_sorce_list=[]
        zdf_list=[]
        max_down_list=[]
        df=pd.read_excel(r'{}\选择可转债\选择可转债.xlsx'.format(self.path),dtype='object')
        try:
            df['Unnamed: 0']
        except:
            pass
        stock_list=df['代码'].tolist()
        for i in tqdm(range(len(stock_list))):
            stock=stock_list[i]
            try:
                df1=self.bond_cov_data.get_cov_bond_hist_data(stock=stock,start='19990101',end='20500101',limit=10000000)
                sorce=self.mean_line_models(df=df1)
                zdf,down=self.get_return_ananlysis(df=df1,n=n)
                mean_sorce_list.append(sorce)
                zdf_list.append(zdf)
                max_down_list.append(down)
            except:
                mean_sorce_list.append(None)
                zdf_list.append(None)
                max_down_list.append(None)
        df['均线得分']=mean_sorce_list
        df['最近{}天收益'.format(n)]=zdf_list
        df['最近天{}最大回撤'.format(n)]=max_down_list
        df.to_excel(r'{}\分析原始数据\分析原始数据.xlsx'.format(self.path))
        df1=df[df['均线得分']>=min_secore]
        df2=df1[df1['最近{}天收益'.format(n)]>=min_return]
        df3=df2[df2['最近{}天收益'.format(n)]<=max_retuen]
        df4=df3[df3['最近天{}最大回撤'.format(n)]>=max_down]
        df4.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
        return df4
    def get_stock_daily_return_analysis(self):
        '''
        正股今天收益率分析
        '''
        with open(r'{}/可转债人气模型交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        max_zdf=text['正股涨跌幅上限']
        min_zdf=text['正股涨跌幅下限']
        n=text['跌破N日均线卖出']
        df=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path),dtype='object')
        try:
            del df['Unnamed: 0']
        except:
            pass
        stock_list=df['代码'].tolist()
        zdf_list=[]
        stock_code_list=[]
        for i in tqdm(range(len(stock_list))):
            stock=stock_list[i]
            try:
                stock=self.bond_cov_data.get_cov_bond_spot(stock=stock)['证券代码']
                stock_spot=self.stock_data.get_stock_spot_data(stock=stock)['涨跌幅']
                zdf_list.append(stock_spot)
                stock_code_list.append(stock)
            except:
                zdf_list.append(None)
                stock_code_list.append(None)
        df['正股代码']=stock_code_list
        df['正股涨跌幅']=zdf_list
        df1=df[df['正股涨跌幅']<=max_zdf]
        df2=df1[df1['正股涨跌幅']>=min_zdf]
        trader_df=df2
        hold_stock_list=trader_df['代码'].tolist()
        sell_list=[]
        for stock in hold_stock_list:
            try:
                hist_df=self.bond_cov_data.get_cov_bond_hist_data(stock=stock)
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
    def get_del_qzsh_data(self):
        '''
        剔除强制赎回
        '''
        with open('{}/可转债人气模型交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        del_select=text['是否剔除强制赎回']
        n=text['距离强制赎回天数']
        df=self.bond_cov_data.bank_cov_qz()
        df.to_excel(r'{}\强制赎回\强制赎回.xlsx'.format(self.path))
        if del_select=='是':
            df1=df[df['cell.redeem_real_days']<=n]
            def select_bond_cov(x):
                '''
                选择可转债
                '''
                if '临近到期' in x or '已满足强赎条件' in x:
                    return '是'
                else:
                    return '不是'
            df1['选择']=df1['cell.redeem_count'].apply(select_bond_cov)
            df.to_excel(r'{}\非强制赎回\非强制赎回.xlsx'.format(self.path))
            return df
        else:
            df.to_excel(r'{}\非强制赎回\非强制赎回.xlsx'.format(self.path))
            return df
    def get_buy_sell_stock(self):
        '''
        获取买卖数据
        '''
        with open('{}/可转债人气模型交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        buy_num=text['买入前N']
        hold_limit=text['持有限制']
        hold_rank=text['持有人气排行前N']
        n=text['跌破N日均线卖出']
        df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        df1=df[df['可用余额']>=10]
        hold_stock_list=df['证券代码'].tolist()
        def select_stock(x):
            '''
            选择股票
            '''
            if x in hold_stock_list:
                return '持股'
            else:
                return "持股不足"
        try:
            del df['Unnamed: 0']
        except:
            pass
        trader_df=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path),dtype='object')
        print('交易股票池*********************************')
        print(trader_df)
        trader_df['选择']=trader_df['代码'].apply(select_stock)
        trader_df=trader_df[trader_df['选择']=='持股不足']
        try:
            del trader_df['Unnamed: 0']
        except:
            pass
        rank_data=pd.read_excel(r'{}\同花顺人气原始数据\同花顺人气原始数据.xlsx'.format(self.path),dtype='object')
        try:
            del rank_data['Unnamed: 0']
        except:
            pass
        if df1.shape[0]>0:
            hold_rank_data=rank_data[:hold_rank]
            #卖出列表
            sell_list=[]
            #持股列表
            hold_stock_list=df['证券代码'].tolist()
            #排名列表
            rank_stock_list=hold_rank_data['代码'].tolist()
            for stock in hold_stock_list:
                if stock in rank_stock_list:
                    pass
                else:
                    #sell_list.append(stock)
                    pass
            n=text['跌破N日均线卖出']
            hold_stock_list=df1['证券代码'].tolist()
            for stock in hold_stock_list:
                    try:
                        hist_df=self.bond_cov_data.get_cov_bond_hist_data(stock=stock)
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
                sell_df['证券代码']=None
                sell_df['交易状态']=None
                sell_df['策略名称']=self.name
                sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
            hold_num=df1.shape[0]
            if hold_num>0:
                av_buy_num=hold_limit-hold_num
                av_buy_num+sell_df.shape[0]
                buy_df=trader_df[:av_buy_num]
            else:
                buy_df=trader_df[:buy_num]
            buy_df['证券代码']=buy_df['代码']
            buy_df['交易状态']='未买'
            print('买入可转债*************')
            print(buy_df)
            buy_df['策略名称']=self.name
            buy_df.to_excel(r'买入股票\买入股票.xlsx')
            return buy_df
        else:
            buy_df=trader_df[:buy_num]
            buy_df['证券代码']=buy_df['代码']
            buy_df['交易状态']='未买'
            print('买入可转债*************')
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
            
            buy_df=buy_df[buy_df['品种']=='bond']
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
            sell_df=sell_df[sell_df['品种']=='bond']
            sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
            print(sell_df)
        else:
            pass
    def updata_all_data(self):
        '''
        更新全部数据
        '''
        self.save_position()
        self.save_balance()
        self.get_ths_rq_data()
        self.get_concact_data()
        self.select_cov_bond_data()
        self.get_stock_mean_line_retuen_analysis()
        self.get_stock_daily_return_analysis()
        self.get_del_qzsh_data()
        self.get_buy_sell_stock()
        self.get_del_not_trader_stock()
    