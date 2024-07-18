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
import os
class bond_cov_rend_strategy:
    def __init__(self,trader_tool='ths',exe='C:/同花顺软件/同花顺/xiadan.exe',tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qq='1029762153@qq.com',open_set='否',qmt_path='D:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55009640',qmt_account_type='STOCK',name='run_bond_cov_rend_strategy'):
        '''
        分析模型可转债趋势策略
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
        self.name=name
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
        def select_del_stock_list(x):
            if str(x)[:6] in del_stock_list:
                return '是'
            else:
                return '否'
        self.trader.connect()
        df=self.trader.position()
        def select_bond_cov(x):
            '''
            选择可转债
            '''
            if x[:3] in ['110','113','123','127','128','111','118'] or x[:2] in ['11','12']:
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
                df1=df1[df1['可用余额']>=10]
                df1['黑名单']=df1['证券代码'].apply(select_del_stock_list)
                df1=df1[df1['黑名单']=='否']
                print('剔除黑名单**********')
                df1.to_excel(r'持股数据\持股数据.xlsx')
                return df1
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
        def select_del_stock_list(x):
            if str(x)[:6] in del_stock_list:
                return '是'
            else:
                return '否'
        self.trader.connect()
        df=self.trader.position()
        def select_bond_cov(x):
            '''
            选择可转债
            '''
            if x[:3] in ['110','113','123','127','128','111','118'] or x[:2] in ['11','12']:
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
                df1=df1[df1['可用余额']>=10]
                df1['黑名单']=df1['证券代码'].apply(select_del_stock_list)
                df1=df1[df1['黑名单']=='否']
                print('剔除黑名单**********')
                df1.to_excel(r'持股数据\持股数据.xlsx')
                return df1
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
        with open(r'{}/可转债趋势策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        self.trader.connect()
        df=self.trader.balance()
        df.to_excel(r'账户数据\账户数据.xlsx')
        return df
    def get_all_jsl_data(self):
        '''
        获取可转债全部数据
        '''
        print('获取可转债全部数据')
        with open(r'{}/可转债趋势策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        max_yjl=text['可转债溢价率上限']
        min_yjl=text['可转债溢价率下限']
        user=text['集思录账户']
        password=text['集思录密码']
        df=jsl_data.get_all_cov_bond_data(jsl_user=user,jsl_password=password)
        df['代码']=df['证券代码'].tolist()
        df1=df[df['转股溢价率']<=max_yjl]
        df2=df1[df1['转股溢价率']>=min_yjl]
        df2.to_excel(r'{}\目前溢价率可转债\目前溢价率可转债.xlsx'.format(self.path))
        return df2
    def select_cov_bond_data(self):
        '''
        选择股票
        '''
        print('选择可转债')
        with open(r'{}/可转债趋势策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        max_price=text['价格上限']
        min_price=text['价格下限']
        max_spot_zdf=text['实时涨跌幅上限']
        min_spot_zdf=text['实时涨跌幅下限']
        max_yjl=text['可转债溢价率上限']
        min_yjl=text['可转债溢价率下限']
        df=pd.read_excel(r'{}\目前溢价率可转债\目前溢价率可转债.xlsx'.format(self.path),dtype='object')
        try:
            del df['Unnamed: 0']
        except:
            pass
        df1=df[df['价格']<=max_price]
        df2=df1[df1['价格']>=min_price]
        df3=df2[df2['涨跌幅']<=max_spot_zdf]
        df4=df3[df3['涨跌幅']>=min_spot_zdf]
        df5=df4[df4['转股溢价率']<=max_yjl]
        df6=df5[df5['转股溢价率']>=min_yjl]
        df6.to_excel(r'{}\选择可转债\选择可转债.xlsx'.format(self.path))
        return df6
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
    def get_cov_bond_shape_analysis(self):
        '''
        可转债形态分析
        '''
        print('可转债形态分析')
        df=pd.read_excel(r'{}\选择可转债\选择可转债.xlsx'.format(self.path),dtype='object')
        try:
            del df['Unnamed: 0']
        except:
            pass
        stock_list=df['证券代码'].tolist()
        over_lining=[]
        mean_line=[]
        for i in tqdm(range(len(stock_list))):
            stock=stock_list[i]
            try:
                hist_df=self.bond_cov_data.get_cov_bond_hist_data(stock=stock)
                models=shape_analysis(df=hist_df)
                over=models.get_over_lining_sell()
                over_lining.append(over)
                #均线分析
                line=models.get_down_mean_line_sell()
                mean_line.append(line)
            except:
                over_lining.append(None)
                mean_line.append(None)
        df['上影线']=over_lining
        df['跌破均线']=mean_line
        df1=df[df['上影线']=='不是']
        df1=df1[df1['跌破均线']=='不是']
        df1.to_excel(r'{}\选择可转债\选择可转债.xlsx'.format(self.path))
        return df1
    def get_stock_mean_line_retuen_analysis(self):
        '''
        可转债均线收益分析
        '''
        print('可转债均线收益分析')
        with open(r'{}/可转债趋势策略交易配置.json'.format(self.path),encoding='utf-8') as f:
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
        stock_list=df['证券代码'].tolist()
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
        print('正股今天收益率分析')
        with open(r'{}/可转债趋势策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        max_zdf=text['正股涨跌幅上限']
        min_zdf=text['正股涨跌幅下限']
        df=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path),dtype='object')
        try:
            del df['Unnamed: 0']
        except:
            pass
        stock_list=df['证券代码'].tolist()
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
        df2.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
        return df2
    def get_del_qzsh_data(self):
        '''
        剔除强制赎回
        '''
        print('剔除强制赎回')
        with open('{}/可转债趋势策略交易配置.json'.format(self.path),encoding='utf-8') as f:
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
            trader_stock=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path),dtype='object')
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
        with open(r'{}/可转债趋势策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        limit=text['持股限制']
        df=self.save_position()
        df['证券代码']=df['证券代码'].astype(str)
        df1=df[df['可用余额']>=10]
        hold_stock_list=df['证券代码'].tolist()
        n=text['跌破N日均线卖出']
        stats,trader_df=self.get_del_qzsh_data()
        trader_df['证券代码']=trader_df['证券代码'].astype(str)
        def select_data(stock):
            if stock in hold_stock_list:
                return '持股超过限制'
            else:
                return '没有持股'
        trader_df['持股检查']=trader_df['证券代码'].apply(select_data)
        trader_df=trader_df[trader_df['持股检查'] !='持股超过限制']
        trader_df=trader_df.sort_values(by='均线得分',ascending=False)
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
        with open('{}/可转债趋势策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        buy_num=text['买入前N']
        hold_limit=text['持有限制']
        df=self.save_position()
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
    def updata_all_data(self):
        '''
        更新全部数据
        '''
        with open(r'{}/可转债趋势策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        self.save_position()
        self.save_balance()
        self.get_all_jsl_data()
        self.select_cov_bond_data()
        self.get_cov_bond_shape_analysis()
        self.get_stock_mean_line_retuen_analysis()
        self.get_stock_daily_return_analysis()
        self.get_del_qzsh_data()
        self.get_del_buy_sell_data()
        self.get_buy_sell_stock()
        self.get_del_not_trader_stock()
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