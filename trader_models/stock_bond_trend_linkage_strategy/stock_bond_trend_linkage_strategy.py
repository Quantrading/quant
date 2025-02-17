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
import numpy as np
from trader_tool.dfcf_cov_data import dfcf_bond_cov_data
class stock_bond_trend_linkage_strategy:
    def __init__(self,trader_tool='qmt',exe='C:/同花顺软件/同花顺/xiadan.exe',tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qq='1029762153@qq.com',open_set='否',qmt_path='D:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55009640',qmt_account_type='STOCK',name='customize_trading_strategies'):
        '''
        股可转债趋势联动
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
        self.dfcf_bond_cov_data=dfcf_bond_cov_data()
        self.data=self.data.get_unification_data()
        self.now_trader_date=self.stock_data.get_trader_date_list()[-1]
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
    def get_dfcf_bond_data(self):
        '''
        获取东方财富可转债数据
        '''
        df=self.dfcf_bond_cov_data.bond_cov_comparison()
        df.to_excel(r'{}\东方财富可转债数据\东方财富可转债数据.xlsx'.format(self.path))
        return df
    def select_bond_data(self):
        '''
        选择可转债数据
        '''
        with open(r'{}/股债趋势联动设置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        max_zdf=text['实时涨跌幅上限']
        min_zdf=text['实时涨跌幅下限']
        max_price=text['可转债价格上限']
        min_price=text['可转债价格下限']
        max_yjl=text['可转债溢价率上限']
        min_yjl=text['可转债溢价率下限']
        df=pd.read_excel(r'{}\东方财富可转债数据\东方财富可转债数据.xlsx'.format(self.path),dtype='object')
        df['转债涨跌幅']=df['转债涨跌幅'].replace('-',None)
        df['转债涨跌幅']=pd.to_numeric(df['转债涨跌幅'])
        try:
            del df['Unnamed: 0']
        except:
            pass
        df['选择']=df['上市日期'].apply(lambda x:'是' if x=='-' else '不是')
        df=df[df['选择']=='不是']
        df=df[df['转股溢价率']<=max_yjl]
        df=df[df['转股溢价率']>=min_yjl]
        df['转债最新价']=df['转债最新价'].replace('-',0)
        df=df[df['转债最新价']<=max_price]
        df=df[df['转债最新价']>=min_price]
        df=df[df['转债涨跌幅']>=min_zdf]
        df=df[df['转债涨跌幅']<=max_zdf]
        df.to_excel(r'{}\选择可转债\选择可转债.xlsx'.format(self.path))
        return df
    def get_stock_mean_line_analysis(self):
        '''
        正股分析
        均线斜率
        '''
        df=pd.read_excel(r'{}\选择可转债\选择可转债.xlsx'.format(self.path),dtype='object')
        try:
            del df['Unnamed: 0']
        except:
            pass
        with open(r'{}/股债趋势联动设置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        try:
            del df['Unnamed: 0']
        except:
            pass
        min_sroce_list=[]
        min_sroce=text['正股均线最低分数']
        n=text['正股跌破N日均线']
        n_list=[]
        polyfit_list=[]
        stock_list=df['正股代码']
        polyfit_daily=text['斜率天数']
        polyfit_line=text['斜率均线']
        for i in tqdm(range(len(stock_list))):
            try:
                stock=str(stock_list[i])
                stock='0'*(6-len(stock))+stock
                hist=self.data.get_hist_data_em(stock=stock)
                hist['30_mean']=hist['close'].rolling(polyfit_line).mean()
                sroce=self.mean_line_models(df=hist)
                min_sroce_list.append(sroce)
                models=shape_analysis(df=hist)
                down=models.get_down_mean_line_sell(n=n)
                n_list.append(down)
                polyfit=self.cacal_stock_polyfit(x_list=range(1,polyfit_daily+1),y_list=hist['30_mean'][-polyfit_daily:])
                polyfit_list.append(polyfit)
            except:
                print(stock,'正股分析有问题')
                min_sroce_list.append(None)
                n_list.append(None)
                polyfit_list.append(None)
        df['正股分数']=min_sroce_list
        df['正股跌破{}均线'.format(n)]=n_list
        df['股票{}斜率'.format(polyfit_daily)]=polyfit_list
        df=df[df['正股分数']>=min_sroce]
        df=df[df['正股跌破{}均线'.format(n)]=='不是']
        df=df.sort_values(by='正股分数',ascending=False)
        df.to_excel(r'{}\正股分析\正股分析.xlsx'.format(self.path))
        return df
    def cacal_stock_polyfit(self,x_list=[],y_list=[]):
        '''
        计算斜率
        '''
        x = np.array(x_list)
        y = np.array(y_list)
        slope, intercept = np.polyfit(x, y, 1)
        return slope
    def get_bond_cov_mean_line_analysis(self):
        '''
        可转债分析
        均线斜率
        '''
        df=pd.read_excel(r'{}\正股分析\正股分析.xlsx'.format(self.path),dtype='object')
        try:
            del df['Unnamed: 0']
        except:
            pass
        with open(r'{}/股债趋势联动设置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        try:
            del df['Unnamed: 0']
        except:
            pass
        min_sroce_list=[]
        min_sroce=text['可转债均线最低分']
        n=text['跌破N日均线卖出']
        n_list=[]
        polyfit_list=[]
        stock_list=df['转债代码']
        polyfit_daily=text['斜率天数']
        polyfit_line=text['斜率均线']
        for i in tqdm(range(len(stock_list))):
            stock=str(stock_list[i])
            try:
                stock='0'*(6-len(stock))+stock
                hist=self.data.get_hist_data_em(stock=stock)
                hist['30_mean']=hist['close'].rolling(polyfit_line).mean()
                sroce=self.mean_line_models(df=hist)
                models=shape_analysis(df=hist)
                down=models.get_down_mean_line_sell(n=n)
                polyfit=self.cacal_stock_polyfit(x_list=range(1,polyfit_daily+1),y_list=hist['30_mean'][-polyfit_daily:])
                polyfit_list.append(polyfit)
                min_sroce_list.append(sroce)
                n_list.append(down)
            except:
                print(stock,'正股分析有问题')
                min_sroce_list.append(0)
                n_list.append(0)
                polyfit_list.append(0)
        df['可转债分数']=min_sroce_list
        df['可转债跌破{}均线'.format(n)]=n_list
        df['可转债{}斜率'.format(polyfit_daily)]=polyfit_list
        df=df[df['可转债分数']>=min_sroce]
        df=df[df['可转债跌破{}均线'.format(n)]=='不是']
        df=df.sort_values(by=['股票{}斜率'.format(polyfit_daily),'可转债{}斜率'.format(polyfit_daily),'正股分数','可转债分数'],ascending=False)
        df.to_excel(r'{}\可转债分析\可转债分析.xlsx'.format(self.path))
        return df
    def get_del_qzsh_data(self):
        '''
        剔除强制赎回
        '''
        print('剔除强制赎回')
        with open(r'{}/股债趋势联动设置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        del_select=text['是否剔除强制赎回']
        n=text['距离强制赎回天数']
        df=self.bond_cov_data.bank_cov_qz()
        del_list=[]
        for i in range(1,n+1):
            n_text='至少还需{}天'.format(i)
            del_list.append(n_text)
        del_list.append('临近到期')
        del_list.append('已满足强赎条件')
        del_list.append('是否剔除强制赎回')
        text_n=''
        for select_text in del_list:
            text_n+='"{}" in x or '.format(select_text)
        text_n=text_n[:-3]
        if del_select=='是':
            df1=df
            def select_bond_cov(x):
                '''
                选择可转债
                '''
                if eval(text_n):
                    return '是'
                else:
                    return '不是'
            df1['选择']=df1['cell.redeem_count'].apply(select_bond_cov)
            df2=df1[df1['选择']=='是']
            df2.to_excel(r'{}\强制赎回\强制赎回.xlsx'.format(self.path))
            trader_stock=pd.read_excel(r'{}\可转债分析\可转债分析.xlsx'.format(self.path),dtype='object')
            try:
                del trader_stock['Unnamed: 0']
            except:
                pass
            trader_stock['证券代码']=trader_stock['转债代码']
            def select_trader_stock(x):
                '''
                选择交易股票池
                '''
                if x not in df2['cell.bond_id'].tolist():
                    return '不是'
                else:
                    return '是'
            
            trader_stock['强制赎回']=trader_stock['证券代码'].apply(select_trader_stock)
            trader_stock=trader_stock[trader_stock['强制赎回']=='不是']
            trader_stock.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
            return df2,trader_stock
        else:
            df.to_excel(r'{}\非强制赎回\非强制赎回.xlsx'.format(self.path))
            return df
    def get_del_buy_sell_data(self):
        '''
        处理交易股票池买入股票
        '''
        with open(r'{}/股债趋势联动设置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        limit=text['持股限制']
        n=text['跌破N日均线卖出']
        df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        df['证券代码']=df['证券代码'].astype(str)
        df1=df[df['可用余额']>=10]
        hold_stock_list=df1['证券代码'].tolist()
        trader_df=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path),dtype='object')
        trader_df['证券代码']=trader_df['证券代码'].astype(str)
        try:
            del trader_df['Unnamed: 0']
        except:
            pass
        def select_data(stock):
            if stock in hold_stock_list:
                return '持股超过限制'
            else:
                return '没有持股'
        trader_df['持股检查']=trader_df['证券代码'].apply(select_data)
        trader_df=trader_df[trader_df['持股检查'] !='持股超过限制']
        hold_stock_list=trader_df['证券代码'].tolist()
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
    def get_buy_sell_stock(self):
        '''
        获取买卖数据
        '''
        with open(r'{}/股债趋势联动设置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        buy_num=text['买入前N']
        hold_limit=text['持有限制']
        df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        df['证券代码']=df['证券代码'].astype(str)
        hold_min_score=text['持有均线最低分']
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
        trader_df['证券代码']=trader_df['证券代码'].astype(str)
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
                    bond_data=self.bond_cov_data.get_cov_bond_hist_data(stock=stock)
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
                    pass
            #跌破均线分析
            #跌破均线分析
            n=text['跌破N日均线卖出']
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
        更新全部数据
        '''
        self.get_dfcf_bond_data()
        self.select_bond_data()
        self.get_stock_mean_line_analysis()
        self.get_bond_cov_mean_line_analysis()
        self.get_del_qzsh_data()
        self.get_del_buy_sell_data()
        self.get_buy_sell_stock()
        self.get_del_not_trader_stock()
        










        

