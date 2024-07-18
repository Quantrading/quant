#自定义模块检验用同花顺数据
from xgtrader.stock_data_ths import stock_data_ths
from xgtrader.bond_cov_data_ths import bond_cov_data_ths
from xgtrader.etf_fund_data_ths import etf_fund_data_ths
from xgtrader.xgtrader import xgtrader
from xgtrader.unification_data_ths import unification_data_ths
from trader_tool.ths_limitup_data import ths_limitup_data
from trader_tool.dfcf_rq import popularity
from trader_tool.ths_rq import ths_rq
from trader_tool import jsl_data
from trader_tool.dfcf_theme import dfcf_theme
from trader_tool.stock_upper_data import stock_upper_data
from trader_tool.analysis_models import analysis_models
from trader_tool.shape_analysis import shape_analysis
from trader_tool.trader_frame import trader_frame
from trader_tool.base_func import base_func
import time
import json
import pywencai
import pandas as pd
from trader_tool.stock_em import stock_em
#可转债趋势策略
from trader_models.bond_cov_rend_strategy.bond_cov_rend_strategy import bond_cov_rend_strategy
#涨停板策略
from trader_models.limit_trading_strategy.limit_trading_strategy import limit_trading_strategy
#etf趋势策略
from trader_models.etf_trend_strategy.etf_trend_strategy import etf_trend_strategy
#可转债人气策略
from trader_models.bond_cov_popularity_strategy.bond_cov_popularity_strategy import bond_cov_popularity_strategy
#股票人气排行策略
from trader_models.stock_sentiment_strategy.stock_sentiment_strategy import stock_sentiment_strategy
#可转债自定义因子轮动策略
from trader_models.bond_cov_custom_factor_rotation.bond_cov_custom_factor_rotation import bond_cov_custom_factor_rotation
#可转债热门概念轮动策略
from trader_models.bond_cov_hot_concept_strategy.bond_cov_hot_concept_strategy import bond_cov_hot_concept_strategy
#微盘股趋势轮动
from trader_models.micro_stock_cap_trend_trading.micro_stock_cap_trend_trading import micro_stock_cap_trend_trading
#聚宽跟单
from trader_models.joinquant_trader_strategy.joinquant_trader_strategy import joinquant_trader_strategy
#自定义交易品种
from trader_models.customize_trading_strategies.customize_trading_strategies import customize_trading_strategies
#股票热门概念
from trader_models.stock_hot_concept_strategy.stock_hot_concept_strategy import stock_hot_concept_strategy
#ETF热门趋势策略
from trader_models.etf_hot_trading_strategies.etf_hot_trading_strategies import etf_hot_trading_strategies
#股可转债联动
from trader_models.stock_bond_trend_linkage_strategy.stock_bond_trend_linkage_strategy import stock_bond_trend_linkage_strategy
#可转债双低轮动策略
from trader_models.convertible_bonds_double_low_strategy.convertible_bonds_double_low_strategy import convertible_bonds_double_low_strategy
#可转债3低
from trader_models.convertible_bonds_three_low_strategy.convertible_bonds_three_low_strategy import convertible_bonds_three_low_strategy
#通达信板块交易
from trader_models.tdx_plate_trader.tdx_plate_trader import tdx_plate_trader
#自定义股票池轮动策略
from trader_models.custom_stock_pool_rotation.custom_stock_pool_rotation import custom_stock_pool_rotation
#自定义红利低波策略
from trader_models.custom_dividend_low_wave_strategy.custom_dividend_low_wave_strategy import custom_dividend_low_wave_strategy
#自定义债券趋势轮动策略
from trader_models.custom_bond_trend_rotation_strategy.custom_bond_trend_rotation_strategy import custom_bond_trend_rotation_strategy
#etf自定义主题轮动
from trader_models.etf_custom_theme_rotation.etf_custom_theme_rotation import etf_custom_theme_rotation
#禄得可转债自定义因子轮动
from trader_models.lude_convertible_bond_custom_factor_rotation.lude_convertible_bond_custom_factor_rotation import lude_convertible_bond_custom_factor_rotation
#雪球跟单
from trader_models.xueqie_trader.xueqie_trader import xueqie_trader
#自定义外盘交易策略
from trader_models.custom_outside_trading_strategy.custom_outside_trading_strategy import custom_outside_trading_strategy
#通达信预警系统交易
from trader_models.tongda_letter_early_warning_trading_system.tongda_letter_early_warning_trading_system import tongda_letter_early_warning_trading_system
#问财交易系统
from trader_models.wencai_trading_system.wencai_trading_system import wencai_trading_system
#自定义资金缓冲区策略.json
from trader_models.customize_the_funds_buffer_policy.customize_the_funds_buffer_policy import customize_the_funds_buffer_policy
class user_def_models:
    def __init__(self,trader_tool='ths',exe='C:/同花顺软件/同花顺/xiadan.exe',tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qq='1029762153@qq.com',open_set='否',qmt_path='D:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55009640',qmt_account_type='STOCK'):
        '''
        自定义模型
        '''
        self.exe=exe
        self.tesseract_cmd=tesseract_cmd
        self.qq=qq
        self.trader_tool=trader_tool
        self.open_set=open_set
        self.qmt_path=qmt_path
        self.qmt_account=qmt_account
        self.qmt_account_type=qmt_account_type
        self.data=unification_data_ths()
        order_frame=trader_frame(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        self.trader=order_frame.get_trader_frame()
        self.stats=0
        self.base_func=base_func()
    def connect(self):
        self.trader.connect()
    def get_wencai_buy_data(self):
        '''
        获取买入数据
        '''
        with open('分析配置.json','r+',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        word=text['问财买入条件']
        df=pywencai.get(loop=True,question=word)
        df.to_excel(r'{}.xlsx'.format(word))
        df['证券代码']=df['code']
        df['交易状态']='未买'
        df.to_excel(r'买入股票\买入股票.xlsx')
        return df
    def get_wencai_sell_data(self):
        '''
        获取问财买入数据
        '''
        with open('分析配置.json','r+',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        word=text['问财卖出条件']
        df=pywencai.get(loop=True,question=word)
        df['证券代码']=df['证券代码'].apply(lambda x:str(x)[:6])
        hold_stock=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        def select_stock(x):
            if x in df['证券代码'].to_list():
                return '是'
            else:
                return '不是'
        if hold_stock.shape[0]>0:
            hold_stock['证券代码']=hold_stock['证券代码'].apply(lambda x:str(x)[:6])
            hold_stock['选择']=hold_stock['证券代码'].apply(select_stock)
            hold_stock=hold_stock[hold_stock['选择']=='是']
            hold_stock['交易状态']='未卖'
            hold_stock.to_excel(r'卖出股票\卖出股票.xlsx')
        else:
            print('没有持股数据')
    def get_dfcf_zh_buy_stock(self):
        '''
        获取东方财富自选股组合买入股票
        '''
        with open('分析配置.json','r+',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        cookie=text['东方财富cookie']
        appkey=text['东方财富appkey']
        name=text['东方财富买入自选股模块名称']
        models=stock_em(Cookie=cookie,appkey=appkey)
        df=models.get_all_zh_code(name=name)
        df['证券代码']=df['security']
        df['交易状态']='未买'
        df.to_excel(r'买入股票\买入股票.xlsx')
    def get_dfcf_zh_sell_stock(self):
        '''
        获取东方财富自选股组合卖出股票
        '''
        with open('分析配置.json','r+',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        cookie=text['东方财富cookie']
        appkey=text['东方财富appkey']
        name=text['东方财富卖出自选股模块名称']
        models=stock_em(Cookie=cookie,appkey=appkey)
        df=models.get_all_zh_code(name=name)
        df['证券代码']=df['security']
        df['交易状态']='未卖'
        df.to_excel(r'卖出股票\卖出股票.xlsx')
    def run_bond_cov_rend_strategy(self):
        '''
        运行可转债趋势轮动策略
        '''
        models=bond_cov_rend_strategy(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.updata_all_data()
    def run_limit_trading_strategy(self):
        '''
        运行涨停板交易策略
        '''
        models=limit_trading_strategy(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.updata_all_data()
    def run_etf_trend_strategy(self):
        '''
        运行etf趋势策略
        '''
        models=etf_trend_strategy(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.updata_all_data()
    def run_bond_cov_popularity_strategy(self):
        '''
        运行可转债人气交易策略
        '''
        models=bond_cov_popularity_strategy(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.updata_all_data()
    def run_stock_sentiment_strategy(self):
        '''
        运行股票人气排行策略
        '''
        models=stock_sentiment_strategy(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.update_all_data()
    def run_bond_cov_custom_factor_rotation(self):
        '''
        可转债自定义因子轮动策略
        '''
        models=bond_cov_custom_factor_rotation(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.updata_all_data()
    def run_bond_cov_hot_concept_strategy(self):
        '''
        运行可转债热门概念策略
        '''
        models=bond_cov_hot_concept_strategy(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.updata_all_data()
    def run_micro_stock_cap_trend_trading(self):
        '''
        微盘股趋势轮动策略
        '''
        models=micro_stock_cap_trend_trading(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                qmt_account_type=self.qmt_account_type)
        models.update_all_data()
    def run_tdx_yj_trader_func(self):
        '''
        运行通达信警告交易函数
        '''
        with open('分析配置.json','r+',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        path=text['通达信警告保存路径']
        columns=text['通达信警告列名称']
        buy_con=text['买入警告条件']
        sell_con=text['卖出警告条件']
        hold_limit=text['持股限制']
        hold_stock=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        try:
            del hold_stock['Unnamed: 0']
        except Exception as e:
            print("运行错误:",e)
        buy_df=pd.read_excel(r'买入股票\买入股票.xlsx',dtype='object')
        if '交易状态' not in buy_df.columns.tolist():
            buy_df['交易状态']=='未买'
        else:
            pass
        buy_df=buy_df[buy_df['交易状态']=='未买']
        try:
            del buy_df['Unnamed: 0']
        except Exception as e:
            print("运行错误:",e)
        sell_df=pd.read_excel(r'卖出股票\卖出股票.xlsx',dtype='object')
        if '交易状态' not in sell_df.columns.tolist():
            sell_df['交易状态']='未卖'
        else:
            pass 
        sell_df=sell_df[sell_df['交易状态']=='未卖']
        try:
            del sell_df['Unnamed: 0']
        except Exception as e:
            print("运行错误:",e)
        with open(r'{}'.format(path),'r+') as f:
            com=f.readlines()
        result_list=[]
        for i in com:
            result_list.append(i.strip().split())
        tdx_df=pd.DataFrame(result_list)
        if tdx_df.shape[0]>0:
            try:
                tdx_df.columns=columns
            except Exception as e:
                print("运行错误:",e)
                re_columns=[]
                for i in range(len(tdx_df.columns.tolist())-2):
                    result_list.append(i)
                re_columns.insert(0,'证券代码')
                re_columns.append('买卖条件')
                tdx_df.columns=columns
            def select_buy_sell(x):
                if x in buy_con or '买' in x:
                    return '未买'
                elif x in sell_con or '卖' in x:
                    return '未卖'
                else:
                    return '未知交易状态'
            tdx_df['交易状态']=tdx_df['买卖条件'].apply(select_buy_sell)
            tdx_df_buy=tdx_df[tdx_df['交易状态']=='未买']
            tdx_df_sell=tdx_df[tdx_df['交易状态']=='未卖']
            def del_hold_stock(x):
                if x in hold_stock['证券代码'].tolist():
                    hold_num=hold_stock[hold_stock['证券代码']==x]['股票余额'].tolist()[-1]
                    if hold_num<=hold_limit:
                        return '持股不足'
                    else:
                        return '超过持股现在'
                else:
                    return '持股不足'
            try:
                if len(buy_df.columns.tolist()) !=len(tdx_df_buy.columns.tolist()):
                    buy_df=pd.DataFrame()
                else:
                    buy_df=buy_df
                buy_df=pd.concat([buy_df,tdx_df_buy],ignore_index=True)
                buy_df=buy_df.drop_duplicates(subset=['证券代码'], keep='last')
                buy_df['持股选择']=buy_df['证券代码'].apply(del_hold_stock)
                buy_df=buy_df[buy_df['持股选择']=='持股不足']
                try:
                    del buy_df['持股选择']
                except Exception as e:
                    print("运行错误:",e)
                buy_df.to_excel(r'买入股票\买入股票.xlsx')
            except Exception as e:
                print("运行错误:",e)
                if len(buy_df.columns.tolist()) !=len(tdx_df_buy.columns.tolist()):
                    buy_df=pd.DataFrame()
                else:
                    buy_df=buy_df
                buy_df=pd.concat([buy_df,tdx_df_buy],ignore_index=True)
                buy_df=buy_df.drop_duplicates(subset=['证券代码'], keep='last')
                buy_df['持股选择']=buy_df['证券代码'].apply(del_hold_stock)
                buy_df=buy_df[buy_df['持股选择']=='持股不足']
                try:
                    del buy_df['持股选择']
                except Exception as e:
                    print("运行错误:",e)
                buy_df.to_excel(r'买入股票\买入股票.xlsx')
            try:
                if len(sell_df.columns.tolist()) !=len(tdx_df_sell.columns.tolist()):
                    sell_df=pd.DataFrame()
                else:
                    sell_df=sell_df
                sell_df=pd.concat([sell_df,tdx_df_sell],ignore_index=True)
                sell_df=sell_df.drop_duplicates(subset=['证券代码'], keep='last')
                sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
            except Exception as e:
                print("运行错误:",e)
                if len(sell_df.columns.tolist()) !=len(tdx_df_sell.columns.tolist()):
                    sell_df=pd.DataFrame()
                else:
                    sell_df=sell_df
                sell_df=pd.concat([sell_df,tdx_df_sell],ignore_index=True)
                sell_df=sell_df.drop_duplicates(subset=['证券代码'], keep='last')
                sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
            print('买入股票**********')
            print(buy_df)
            print('卖出股票*********')
            print(sell_df)
        else:
            print('通达信没有警告数据')
    
    def run_tdx_yj_trader_func_1(self):
        '''
        运行通达信警告交易函数1
        '''
        from datetime import datetime
        now_date=str(datetime.now())[:10]
        with open('分析配置.json','r+',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        path=text['通达信警告保存路径']
        columns=text['通达信警告列名称']
        buy_con=text['买入警告条件']
        sell_con=text['卖出警告条件']
        hold_limit=text['持股限制']
        hold_stock=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        try:
            del hold_stock['Unnamed: 0']
        except Exception as e:
            print("运行错误:",e)
        if self.stats==0:
            buy_df=pd.DataFrame()
            for i in columns:
                buy_df[i]=None
            buy_df.to_excel(r'买入股票\买入股票.xlsx')
            sell_df=pd.DataFrame()
            for i in columns:
                sell_df[i]=None
            sell_df.columns=columns
            sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
        else:
            buy_df=pd.read_excel(r'买入股票\买入股票.xlsx',dtype='object')
            if '交易状态' not in buy_df.columns.tolist():
                buy_df['交易状态']=='未买'
            else:
                pass
            buy_df=buy_df[buy_df['交易状态']=='未买']
            try:
                del buy_df['Unnamed: 0']
            except Exception as e:
                print("运行错误:",e)
            sell_df=pd.read_excel(r'卖出股票\卖出股票.xlsx',dtype='object')
            if '交易状态' not in sell_df.columns.tolist():
                sell_df['交易状态']='未卖'
            else:
                pass 
            sell_df=sell_df[sell_df['交易状态']=='未卖']
            try:
                del sell_df['Unnamed: 0']
            except Exception as e:
                print("运行错误:",e)
        with open(r'{}'.format(path),'r+') as f:
            com=f.readlines()
        result_list=[]
        log_list=[]
        stats=''
        for i in com:
            text=i.strip().split()
            for j in text:
                if len(j)<=1 and len(stats)<3:
                    stats+=j
                elif len(stats)==3:
                    log_list.append(stats)
                    stats=''
                else:
                    log_list.append(j)
            result_list.append(log_list)
            log_list=[]
        tdx_df=pd.DataFrame(result_list)
        tdx_df=tdx_df.dropna(how='any')
        print('通达信警告数据******')
        print(tdx_df)
        if tdx_df.shape[0]>0:
            tdx_df.columns=columns
            def select_buy_sell(x):
                if x in buy_con or '买' in x:
                    return '未买'
                elif x in sell_con or '卖' in x:
                    return '未卖'
                else:
                    return '未知交易状态'
            tdx_df['时间']=pd.to_datetime(tdx_df['时间'])
            tdx_df=tdx_df[tdx_df['时间']>=now_date]
            tdx_df['交易状态']=tdx_df['买卖条件'].apply(select_buy_sell)
            tdx_df_buy=tdx_df[tdx_df['交易状态']=='未买']
            tdx_df_sell=tdx_df[tdx_df['交易状态']=='未卖']
            def del_hold_stock(x):
                if x in hold_stock['证券代码'].tolist():
                    hold_num=hold_stock[hold_stock['证券代码']==x]['股票余额'].tolist()[-1]
                    if hold_num<hold_limit:
                        print("{}持股不足".format(x))
                        return '持股不足'
                    else:
                        print("{}超过持股限制".format(x))
                        return '超过持股限制'
                else:
                    print("{}没有持股".format(x))
                    return '持股不足'
            try:
                if len(buy_df.columns.tolist()) !=len(tdx_df_buy.columns.tolist()):
                    buy_df=pd.DataFrame()
                else:
                    buy_df=buy_df
                buy_df=pd.concat([buy_df,tdx_df_buy],ignore_index=True)
                buy_df=buy_df.drop_duplicates(subset=['证券代码'], keep='last')
                buy_df['持股选择']=buy_df['证券代码'].apply(del_hold_stock)
                buy_df=buy_df[buy_df['持股选择']=='持股不足']
                try:
                    del buy_df['持股选择']
                except Exception as e:
                    print("运行错误:",e)
                buy_df['时间']=pd.DataFrame(buy_df['时间'])
                buy_df[buy_df['时间']>=now_date]
                buy_df['策略名称']='通达信警告交易函数1'
                buy_df.to_excel(r'买入股票\买入股票.xlsx')
            except Exception as e:
                print("运行错误:",e)
                if len(buy_df.columns.tolist()) !=len(tdx_df_buy.columns.tolist()):
                    buy_df=pd.DataFrame()
                else:
                    buy_df=buy_df
                buy_df=pd.concat([buy_df,tdx_df_buy],ignore_index=True)
                buy_df=buy_df.drop_duplicates(subset=['证券代码'], keep='last')
                buy_df['持股选择']=buy_df['证券代码'].apply(del_hold_stock)
                buy_df=buy_df[buy_df['持股选择']=='持股不足']
                try:
                    del buy_df['持股选择']
                except Exception as e:
                    print("运行错误:",e)
                buy_df['时间']=pd.DataFrame(buy_df['时间'])
                buy_df[buy_df['时间']>=now_date]
                buy_df['策略名称']='通达信警告交易函数1'
                buy_df.to_excel(r'买入股票\买入股票.xlsx')
            try:
                if len(sell_df.columns.tolist()) !=len(tdx_df_sell.columns.tolist()):
                    sell_df=pd.DataFrame()
                else:
                    sell_df=sell_df
                sell_df=pd.concat([sell_df,tdx_df_sell],ignore_index=True)
                sell_df=sell_df.drop_duplicates(subset=['证券代码'], keep='last')
                sell_df['时间']=pd.DataFrame(sell_df['时间'])
                sell_df=sell_df[sell_df['时间']>=now_date]
                sell_df['策略名称']='通达信警告交易函数1'
                sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
            except Exception as e:
                print("运行错误:",e)
                if len(sell_df.columns.tolist()) !=len(tdx_df_sell.columns.tolist()):
                    sell_df=pd.DataFrame()
                else:
                    sell_df=sell_df
                sell_df=pd.concat([sell_df,tdx_df_sell],ignore_index=True)
                sell_df=sell_df.drop_duplicates(subset=['证券代码'], keep='last')
                sell_df['时间']=pd.DataFrame(sell_df['时间'])
                sell_df=sell_df[sell_df['时间']>=now_date]
                sell_df['策略名称']='通达信警告交易函数1'
                sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
            print('买入股票**********')
            print(buy_df)
            print('卖出股票*********')
            print(sell_df)
            self.stats+=1
        else:
            print('通达信没有警告数据')
            self.stats+=1
    def run_tdx_trader_stock_buy(self):
        '''
        运行通达信自选股买入模块
        '''
        with open('分析配置.json','r+',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        text=json.loads(com)
        buy_path=text['通达信自选股买入自选股路径']
        df=base_func.read_tdx_trader_stock_buy(path=buy_path)
        df['策略名称']='通达信自选股买入模块'
        df.to_excel(r'买入股票\买入股票.xlsx')
        print('通达信自选股买入********************')
        print(df)
    def run_tdx_trader_stock_sell(self):
        '''
        运行通达信自选股卖出模块
        '''
        with open('分析配置.json','r+',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        text=json.loads(com)
        buy_path=text['通达信自选股卖出自选股路径']
        df=base_func.read_tdx_trader_stock_sell(path=buy_path)
        df['策略名称']='达信自选股卖出模块'
        print('通达信自选股卖出**************')
        df.to_excel(r'卖出股票\卖出股票.xlsx')
        print(df)
    def get_connect_trader_data(self):
        '''
        合并买卖数据
        循环类型直接写入，比如通达信警告
        定时策略合并多个数据，比如模型策略
        '''
        import os
        with open('分析配置.json','r+',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        user_def_func=text['自定义函数']
        user_def_func_name=text['模型策略']
        buy_df=pd.DataFrame()
        sell_df=pd.DataFrame()
        buy_path_list=os.listdir(r'多策略买入股票')
        sell_path_list=os.listdir(r'多策略卖出股票')
        for func in user_def_func:
            name=user_def_func_name[func]
            if func=='run_tdx_yj_trader_func_1':
                print(name,'直接写入买卖数据')
            else:
                #合并买入
                buy_path='{}.xlsx'.format(func)
                if buy_path in buy_path_list:
                    buy=pd.read_excel(r'多策略买入股票\{}'.format(buy_path))
                    if buy.shape[0]>0:
                        print('合并策略{}'.format(name))
                        buy=buy[['证券代码','交易状态','策略名称']]
                        buy_df=pd.concat([buy_df,buy],ignore_index=True)
                    else:
                        print('策略{}没有数据'.format(name))
                #合并卖出
                sell_path='{}.xlsx'.format(func)
                if sell_path in sell_path_list:
                    sell=pd.read_excel(r'多策略卖出股票\{}'.format(sell_path))
                    if sell.shape[0]>0:
                        print('合并策略{}'.format(name))
                        sell=sell[['证券代码','交易状态','策略名称']]
                        sell_df=pd.concat([sell_df,sell],ignore_index=True)
                    else:
                        print('策略{}没有数据'.format(name))
        #多个策略叠加买入一个就可以
        buy_df=buy_df.drop_duplicates(subset=['证券代码'])
        sell_df=sell_df.drop_duplicates(subset=['证券代码'])
        buy_df.to_excel(r'买入股票\买入股票.xlsx')
        print('合并买入股票***********************')
        print(buy_df)
        sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
        print('合并卖出股票***********************')
        print(sell_df)
    def run_joinquant_trader_strategy_get_simultaneous_stock_hold_models(self,n=0):
        '''
        同步持股,交易模式1，对比持股获取买卖数据，会同步聚宽目前的持股
        聚宽跟单持股模式
        n 第几个组合
        '''
        models=joinquant_trader_strategy(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                qmt_account_type=self.qmt_account_type,n=n,name='run_joinquant_trader_strategy_get_simultaneous_stock_hold_models')
        models.get_simultaneous_stock_hold_models()
    def run_joinquant_trader_strategy_get_simultaneous_transaction_models(self,n=0):

        '''
        交易模式2,同步成交，不会同步目前的持股
        聚宽跟单成交模式
        '''
        models=joinquant_trader_strategy(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                qmt_account_type=self.qmt_account_type,n=n,name='run_joinquant_trader_strategy_get_simultaneous_transaction_models')
        models.get_simultaneous_transaction_models()
    def run_customize_trading_strategies(self):
        '''
        自定义交易品种
        '''
        models=customize_trading_strategies(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.update_all_data()
    def run_stock_hot_concept_strategy(self):
        '''
        股票热门概念策略
        '''
        models=stock_hot_concept_strategy(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.get_update_all_data()
    def run_etf_hot_trading_strategies(self):
        '''
        热门ETF趋势策略
        '''
        models=etf_hot_trading_strategies(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.update_all_data()
    def run_stock_bond_trend_linkage_strategy(self):
        '''
        股债联动
        '''
        models=stock_bond_trend_linkage_strategy(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.update_all_data()
    def run_convertible_bonds_double_low_strategy(self):
        '''
        可转债双低轮动策略
        '''
        models=convertible_bonds_double_low_strategy(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.updata_all_data()
    def run_convertible_bonds_three_low_strategy(self):
        '''
        可转债三低轮动策略
        '''
        models=convertible_bonds_three_low_strategy(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.updata_all_data()
    def run_tdx_plate_trader(self):
        '''
        通达信板块交易
        '''
        models=tdx_plate_trader(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.update_all_data()
    def run_custom_stock_pool_rotation(self):
        '''
        自定义股票池轮动策略
        '''
        models=custom_stock_pool_rotation(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.updata_all_data()
    def run_custom_dividend_low_wave_strategy(self):
        '''
        自定义红利低波策略
        '''
        models=custom_dividend_low_wave_strategy(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.update_all_data()
    def run_custom_bond_trend_rotation_strategy(self):
        '''
        自定义债券趋势轮动策略
        '''
        models=custom_bond_trend_rotation_strategy(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.update_all_data()
    def run_etf_custom_theme_rotation(self):
        '''
        etf自定义主题轮动
        '''
        models=etf_custom_theme_rotation(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.update_all_data()
    def run_lude_convertible_bond_custom_factor_rotation(self):
        '''
        禄得可转债自定义因子轮动
        '''
        models=lude_convertible_bond_custom_factor_rotation(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.updata_all_data()
    def run_xueqie_trader(self):
        '''
        雪球跟单
        '''
        models=xueqie_trader(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.update_all_data()
    def run_custom_outside_trading_strategy(self):
        '''
        自定义外盘交易策略
        '''
        models=custom_outside_trading_strategy(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.update_all_data()
    def run_tongda_letter_early_warning_trading_system(self):
        '''
        通达信预警系统交易
        '''
        models=tongda_letter_early_warning_trading_system(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.update_all_data()
    def run_wencai_trading_system(self):
        '''
        问财选股交易系统
        '''
        models=wencai_trading_system(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.updata_all_data()
    def run_release_funds(self):
        '''
        释放国债资金
        '''
        models=customize_the_funds_buffer_policy(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.release_funds()
    def run_buy_bonds_to_deposit_funds(self):
        '''
        购买债券存入资金
        '''
        models=customize_the_funds_buffer_policy(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.buy_bonds_to_deposit_funds()
    def run_reverse_repurchase_of_treasury_bonds_1(self):
        '''
        国债逆回购
        '''
        models=customize_the_funds_buffer_policy(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        models.run_reverse_repurchase_of_treasury_bonds_1()
    
if __name__=='__main__':
    with open('分析配置.json','r+',encoding='utf-8') as f:
        com=f.read()
    text=json.loads(com)
    trader_tool=text['交易系统']
    exe=text['同花顺下单路径']
    tesseract_cmd=text['识别软件安装位置']
    qq=text['发送qq']
    test=text['测试']                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
    open_set=text['是否开启特殊证券公司交易设置']
    qmt_path=text['qmt路径']
    qmt_account=text['qmt账户']
    qmt_account_type=text['qmt账户类型']
    models=user_def_models(trader_tool=trader_tool,exe=exe,tesseract_cmd=tesseract_cmd,qq=qq,
                           open_set=open_set,qmt_path=qmt_path,qmt_account=qmt_account,
                           qmt_account_type=qmt_account_type)
    func_list=text['自定义函数']
    for func in func_list:
        runc_func='models.{}()'.format(func)
        eval(runc_func)
