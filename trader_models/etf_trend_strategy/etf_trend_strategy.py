from trader_tool.stock_data import stock_data
from trader_tool.bond_cov_data import bond_cov_data
from trader_tool.shape_analysis import shape_analysis
from trader_tool.etf_fund_data import etf_fund_data
from trader_tool.stock_upper_data import stock_upper_data
from trader_tool.ths_limitup_data import ths_limitup_data
from trader_tool.trader_frame import trader_frame
from trader_tool.unification_data import unification_data
import pandas as pd
from trader_tool.ths_rq import ths_rq
from tqdm import tqdm
import numpy as np
import json
from  trader_tool import jsl_data
from trader_tool.dfcf_etf_data import dfcf_etf_data
import os
class etf_trend_strategy:
    def __init__(self,trader_tool='ths',exe='C:/同花顺软件/同花顺/xiadan.exe',tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qq='1029762153@qq.com',open_set='否',qmt_path='D:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55009640',qmt_account_type='STOCK',name='run_etf_trend_strategy'):
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
        order_frame=trader_frame(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        self.trader=order_frame.get_trader_frame()
        self.trader.connect()
        self.etf_fund_data=etf_fund_data()
        self.path=os.path.dirname(os.path.abspath(__file__))
        self.name=name
        self.dfcf_etf_data=dfcf_etf_data()
        self.data=unification_data(trader_tool=self.trader_tool)
        self.data=self.data.get_unification_data()
    def save_position(self):
        '''
        保存持股数据
        '''
        df=self.trader.position()
        def select_bond_cov(x):
            '''
            选择ETF基金
            '''
            if x[:3] in ['510','511','512','513','514','515','516','517','518','588','159','501']:
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
            选择etf
            '''
            if x[:3] in ['510','511','512','513','514','515','516','517','518','588','159','501']:
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
                #df1=df1[df1['可用余额']>=10]
                df1['交易状态']='未卖'
                df1.to_excel(r'持股数据\持股数据.xlsx')
                return df1
            else:
                print('没有持股')
    def select_etf_fund(self,x):
        '''
        选择etf
        '''
        if x[:3] in ['510','511','512','513','514','515','516','517','518','588','159','501']:
            return '是'
        else:
            return '不是'
    def save_balance(self):
        '''
        保持账户数据
        '''
        df=self.trader.balance()
        df.to_excel(r'账户数据\账户数据.xlsx')
        return df
    def get_all_etf_fund_data(self):
        '''
        获取etf基金数据
        '''
        not_del=self.dfcf_etf_data.get_all_etf_data_1()
        not_del.to_excel(r'{}\不剔除ETF\不剔除ETF.xlsx'.format(self.path))
        data=pd.DataFrame()
        df=self.dfcf_etf_data.get_all_etf_data()
        df['证券代码']=df['基金代码']
        df['类型']='全部'
        data=pd.concat([data,df],ignore_index=True)
        df.to_excel(r'{}\全部ETF\全部ETF.xlsx'.format(self.path))
        df=self.dfcf_etf_data.get_sz_sh_etf()
        df['证券代码']=df['基金代码']
        df['类型']='A股'
        data=pd.concat([data,df],ignore_index=True)
        df.to_excel(r'{}\沪深ETF\沪深ETF.xlsx'.format(self.path))
        df=self.dfcf_etf_data.get_wp_etf_data()
        df['证券代码']=df['基金代码']
        df['类型']='外盘'
        data=pd.concat([data,df],ignore_index=True)
        df.to_excel(r'{}\外盘ETF\外盘ETF.xlsx'.format(self.path))
        df=self.dfcf_etf_data.get_bond_etf_data()
        df['证券代码']=df['基金代码']
        df['类型']='债券'
        data=pd.concat([data,df],ignore_index=True)
        df.to_excel(r'{}\债券ETF\债券ETF.xlsx'.format(self.path))
        df=self.dfcf_etf_data.get_sp_etf_data()
        df['证券代码']=df['基金代码']
        df['类型']='商品'
        data=pd.concat([data,df],ignore_index=True)
        df.to_excel(r'{}\商品ETF\商品ETF.xlsx'.format(self.path))
        data.to_excel(r'{}\综合ETF\综合ETF.xlsx'.format(self.path))
        
    def select_etf_fund_data(self):
        '''
        选择ETF
        '''
        print('选择ETF')
        with open(r'{}/etf趋势轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        select_list=text['默认市场']
        select_type=text['选择类型']
        user_def_stock=text['自定义股票池']
        user_def_indictor=text['分析指标']
        user_def_str_is=text['是否开启自定义字符串']
        user_def_str=text['自定义字符串内容']
        if select_type=='默认':
            df=pd.read_excel(r'{}\综合ETF\综合ETF.xlsx'.format(self.path),dtype='object')
            try:
                del df['Unnamed: 0']
            except:
                pass
            def select_data(x):
                if x in select_list:
                    return '是'
                else:
                    return '不是'
            if user_def_str_is=='是':
                data=pd.DataFrame()
                str_list=user_def_str.split(',')
                for i in str_list:
                    df['匹配']=df['基金名称'].apply(lambda x: '是' if i in str(x) else '不是')
                    df1=df[df['匹配']=='是']
                    data=pd.concat([data,df1],ignore_index=True)
                    data=data.drop_duplicates()
                df=data
            else:
                df=df
            df['选择']=df['类型'].apply(select_data)
            df=df[df['选择']=='是']
            indictor_list=list(user_def_indictor.keys())
            for indicator in indictor_list:
                if len(indictor_list)>0:
                    try:
                        min_value=user_def_indictor[indicator][0]
                        max_value=user_def_indictor[indicator][-1]
                        df=df[df[indicator]>=min_value]
                        df=df[df[indicator]<=max_value]
                    except:
                        pass
                else:
                    print('没有分析指标')
        else:
            df=pd.DataFrame()
            df['证券代码']=user_def_stock
            df['基金代码']=user_def_stock
            df['基金名称']=user_def_stock
        df.to_excel(r'{}\选择etf\选择etf.xlsx'.format(self.path))
    def mean_line_models(self,df=''):
        '''
        均线模型
        趋势模型
        5，10，20，30，60
        '''
        #df=self.etf_fund_data.get_ETF_fund_hist_data(stock='1598')
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
        etf均线收益分析
        '''
        print('etf均线收益分析')
        with open(r'{}/etf趋势轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
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
        df=pd.read_excel(r'{}\选择etf\选择etf.xlsx'.format(self.path),dtype='object')
        try:
            df['Unnamed: 0']
        except:
            pass
        stock_list=df['基金代码'].tolist()
        for i in tqdm(range(len(stock_list))):
            stock=stock_list[i]
            try:
                df1=self.etf_fund_data.get_ETF_fund_hist_data(stock=stock)
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
        df4=df3[df3['最近天{}最大回撤'.format(n)]<=max_down]
        df4.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
        return df4
    def get_etf_fund_shape_analysis(self):
        '''
        etf分析
        '''
        print('etf分析形态分析')
        with open(r'{}/etf趋势轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        df=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path),dtype='object')
        try:
            del df['Unnamed: 0']
        except:
            pass
        stock_list=df['基金代码'].tolist()
        n=text['跌破N日均线卖出']
        over_lining=[]
        mean_line=[]
        for i in tqdm(range(len(stock_list))):
            stock=stock_list[i]
            hist=self.etf_fund_data.get_ETF_fund_hist_data(stock=stock)
            models=shape_analysis(df=hist)
            try:
                over=models.get_over_lining_sell(n=n)
                over_lining.append(over)
                #均线分析
                line=models.get_down_mean_line_sell(n=n)
                mean_line.append(line)
            except:
                over_lining.append(None)
                mean_line.append(None)
        df['上影线']=over_lining
        df['跌破均线']=mean_line
        df1=df[df['上影线']=='不是']
        df1=df1[df1['跌破均线']=='不是']
        df1.to_excel(r'{}\选择etf\选择etf.xlsx'.format(self.path))
    def get_del_buy_sell_data(self):
        '''
        处理交易etf
        '''
        with open(r'{}/etf趋势轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        limit=text['持股限制']
        data_type=text['交易模式']
        value=text['固定交易资金']
        limit_value=text['持有金额限制']
        amount=text['固定交易数量']
        limit_amount=text['持股限制']
        df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        df['证券代码']=df['证券代码'].astype(str)
        df1=df[df['可用余额']>=10]
        hold_stock_list=df['证券代码'].tolist()
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
        trader_df['持股检查']=trader_df['基金代码'].apply(select_data)
        trader_df=trader_df[trader_df['持股检查'] !='持股超过限制']
        trader_df.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
        trader_df=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path),dtype='object')
        try:
            del trader_df['Unnamed: 0']
        except:
            pass
        hold_stock_list=trader_df['基金代码'].tolist()
        #跌破均线分析
        mean_analysis=[]
        n=text['跌破N日均线卖出']
        for i in tqdm(range(len(hold_stock_list))):
            stock=hold_stock_list[i]
            try:
                hist_df=self.etf_fund_data.get_ETF_fund_hist_data(stock=stock)
                models=shape_analysis(df=hist_df)
                mean_line=models.get_down_mean_line_sell(n=n)
                if mean_line=='是':
                    mean_analysis.append('是')
                else:
                    mean_analysis.append('不是')
            except:
                    print(stock,'错误')
                    mean_analysis.append(None)
        trader_df['跌破均线分析']=mean_analysis
        trader_df=trader_df[trader_df['跌破均线分析']=='不是']
        trader_df.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
        return trader_df
    def get_buy_sell_stock(self):
        '''
        获取买卖数据
        '''
        with open('{}/etf趋势轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
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
            选择etf
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
        try:
            del trader_df['Unnamed: 0']
        except:
            pass
        print('交易股票池*******************')
        print(trader_df)
        trader_df['选择']=trader_df['基金代码'].apply(select_stock)
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
            #跌破均线分析
            
            '''
            for stock in hold_stock_list:
                    try:
                        hist_df=self.etf_fund_data.get_ETF_fund_hist_data(stock=stock)
                        models=shape_analysis(df=hist_df)
                        mean_line=models.get_down_mean_line_sell(n=n)
                        if mean_line=='是':
                            sell_list.append(stock)
                            print('{}跌破均线'.format(stock))
                        else:
                            pass
                    except:
                        pass
            '''
            is_buffer=text['是否开启策略缓冲区']
            deviation_mean=text['偏离均线']
            deviation_up_spot=text['向上偏离N点卖出']
            deviation_down_spot=text['跌破偏离线下穿N点卖出']
            minimum_guarantee=text['偏离保底均线N卖出']
            n=text['跌破N日均线卖出']
            if is_buffer=='是':
                print("开启策略缓冲区**************")
                for stock in hold_stock_list:
                    try:
                        #偏离
                        hist=self.data.get_hist_data_em(stock=stock)
                        price=hist['close'].tolist()[-1]
                        hist['mean_line']=hist['close'].rolling(window=deviation_mean).mean()
                        line=hist['mean_line'].tolist()[-1]
                        deviation=((price-line)/line)*100
                        print('{} {}价格 {}日均线{} 偏离度{}'.format(stock,price,deviation_mean,line,deviation))
                        models=shape_analysis(df=hist)
                        mean_line=models.get_down_mean_line_sell(n=n)
                        minimum=models.get_down_mean_line_sell(n=minimum_guarantee)
                        if minimum=='是':
                            print('{} 跌破保底均线{} 卖出'.format(stock,minimum_guarantee))
                            sell_list.append(stock)
                        elif deviation>0 and deviation>=deviation_up_spot:
                            print('{} 偏离{}均线并且 偏离{} 偏离向上缓冲区{}'.format(stock,n,deviation,deviation_up_spot))
                            sell_list.append(stock)
                        elif mean_line=='是':
                            print('{} 跌破均线{} 进入缓冲区分析'.format(n,stock))
                            if deviation<=0 and abs(deviation)>=deviation_down_spot:
                                print('{} 跌破{}均线并且 下穿{} 跌破向下缓冲区{}'.format(stock,n,deviation,deviation_down_spot))
                                sell_list.append(stock)
                            else:
                                print('{} 正常{}均线并且 偏离{} 偏离在正常的缓冲区{}'.format(stock,n,deviation,deviation_down_spot))
                        else:
                            print('{} 符合缓冲区要求'.format(stock))
                    except:
                        print('{} 缓冲区处理有问题'.format(stock))
                    
                else:
                    print('不开启策略缓冲区**********************')
                #溢价率自动平仓
                fund=self.dfcf_etf_data.get_all_etf_data_1()
                yjl_dict=dict(zip(fund['基金代码'].tolist(),fund['溢价率'].tolist()))
                is_yjl=text['是否开启溢价率平仓']
                max_yjl=text['平仓溢价率']
                if is_yjl=='是':
                    print('********************溢价率自动平仓')
                    for stock in hold_stock_list:
                        try:
                            yjl=yjl_dict.get(stock,0)
                            if yjl>=max_yjl:
                                print('{} 溢价率{} 符合最大溢价率{} 自动平仓'.format(stock,yjl,max_yjl))
                                sell_list.append(stock)
                            else:
                                print('{} 溢价率{} 不符合最大溢价率{} 不自动平仓'.format(stock,yjl,max_yjl))
                        except:
                            print('{} 溢价率平仓有问题'.format(stock))
                #是否开启大涨卖出
                is_max_up=text['是否开启大涨卖出']
                max_up=text['大涨']
                if is_max_up=='是':
                    print('开启大涨卖出')
                    for stock in hold_stock_list:
                        try:
                            hist=self.data.get_hist_data_em(stock=stock)
                            zdf=hist['涨跌幅'].tolist()[-1]
                            if zdf>=max_up:
                                print('{} 今日涨跌幅{} 大于最大涨跌幅{} 卖出'.format(stock,zdf,max_up))
                                sell_list.append(stock)
                            else:
                                print('{} 今日涨跌幅{} 小于最大涨跌幅{} 不操作'.format(stock,zdf,max_up))
                        except:
                            print('{} 开启大涨卖出有问题'.format(stock))
            sell_df=pd.DataFrame()
            sell_df['证券代码']=sell_list
            sell_df['交易状态']='未卖'
            #剔除新股申购
            sell_df['选择']=sell_df['证券代码'].apply(self.select_etf_fund)
            sell_df=sell_df[sell_df['选择']=='是']
            if sell_df.shape[0]>0:
                print('卖出etf*****************')
                print(sell_df)
                sell_df['策略名称']=self.name
                sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
            else:
                print('没有卖出etf')
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
            df['证券代码']=df['证券代码']
            print(buy_df)
            buy_df['策略名称']=self.name
            buy_df['剔除']=buy_df['基金名称'].apply(lambda x:str(x)[:2])
            buy_df=buy_df.drop_duplicates(subset='剔除',ignore_index=True)
            if buy_df.shape[0]>=hold_limit:
                buy_df=buy_df[:hold_limit]
            else:
                buy_df=buy_df
            buy_df.to_excel(r'买入股票\买入股票.xlsx')
            return buy_df
        else:
            buy_df=trader_df[:buy_num]
            print(trader_df)
            buy_df['证券代码']=buy_df['基金代码']
            buy_df['交易状态']='未买'
            print('买入etf*****************')
            print(buy_df)
            buy_df['策略名称']=self.name
            buy_df['剔除']=buy_df['基金名称'].apply(lambda x:str(x)[:2])
            buy_df=buy_df.drop_duplicates(subset='剔除',ignore_index=True)
            if buy_df.shape[0]>=hold_limit:
                buy_df=buy_df[:hold_limit]
            else:
                buy_df=buy_df
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
            
            buy_df=buy_df[buy_df['品种']=='fund']
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
            sell_df=sell_df[sell_df['品种']=='fund']
            sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
            print(sell_df)
        else:
            pass
    def updata_all_data(self):
        '''
        更新全部数据
        '''
        with open(r'{}/etf趋势轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        self.save_position()
        self.save_balance()
        self.get_all_etf_fund_data()
        self.select_etf_fund_data()
        self.get_stock_mean_line_retuen_analysis()
        self.get_del_buy_sell_data()
        self.get_buy_sell_stock()
        self.get_del_not_trader_stock()