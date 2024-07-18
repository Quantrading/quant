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
class custom_dividend_low_wave_strategy:
    def __init__(self,trader_tool='ths',exe='C:/同花顺软件/同花顺/xiadan.exe',tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qq='1029762153@qq.com',open_set='否',qmt_path='D:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55009640',qmt_account_type='STOCK',name='customize_trading_strategies'):
        '''
        红利低波策略
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
        with open(r'{}\自定义红利低波交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        limit=text['持股限制']
        n=text['自定义交易品种跌破N日均线卖出']
        max_yjl=text['ETF溢价率上限']
        min_yjl=text['ETF溢价率下限']
        buy_min_srore=text['买入最低分']
        df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        df1=df[df['股票余额']>=10]
        df1['证券代码']=df1['证券代码'].astype(str)
        hold_stock_list=df1['证券代码'].tolist()
        trader_df=pd.read_excel(r'{}\自定义交易股票池\自定义交易股票池.xlsx'.format(self.path),dtype='object')
        trader_df['证券代码']=trader_df['证券代码'].astype(str)
        print(hold_stock_list)
        def select_data(stock):
            if str(stock) in hold_stock_list:
                return '持股超过限制'
            else:
                return '没有持股'
        trader_df['持股检查']=trader_df['证券代码'].apply(select_data)
        trader_df=trader_df[trader_df['持股检查'] !='持股超过限制']
        print('原始自定义交易股票池****************')
        print(trader_df)
        #再次处理
        is_buffer=text['是否开启策略缓冲区']
        deviation_mean=text['偏离均线']
        deviation_up_spot=text['买入时候的偏离度']
        deviation_down_spot=text['跌破偏离线下穿N点卖出']
        minimum_guarantee=text['买入保底均线']
        n=text['自定义交易品种跌破N日均线卖出']
        max_zdf=text['最大涨跌幅']
        min_zdf=text['最小涨跌幅']
        trader_list=trader_df['证券代码'].tolist()
        zdf_list=[]
        sell_list=[]
        if is_buffer=='是':
            print("开启策略缓冲区**************")
            for stock in trader_list:
                try:
                    #偏离
                    hist=self.data.get_hist_data_em(stock=stock)
                    zdf=hist['涨跌幅'].tolist()[-1]
                    zdf_list.append(zdf)
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
                    zdf_list.append(None)
            trader_df['涨跌幅']=zdf_list
            trader_df=trader_df[trader_df['涨跌幅']>=min_zdf]
            trader_df=trader_df[trader_df['涨跌幅']<=max_zdf]
            trader_df['缓冲区']=trader_df['证券代码'].apply(lambda x: '是' if x in sell_list else '不是')
            trader_df=trader_df[trader_df['缓冲区']=='不是']
            print('处理的交易股票池********************')
            print(trader_df)
            trader_list=trader_df['证券代码'].tolist()
            sell_list=[]
            mean_score_list=[]
            for stock in trader_list:
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
                except:
                    print('{}有问题--处理交易股票池买入股票'.format(stock))
                    mean_score_list.append(None)
                    sell_list.append('是')
            trader_df['均线得分']=mean_score_list 
            trader_df=trader_df[trader_df['均线得分']>=buy_min_srore]
            fund=self.dfcf_etf_data.get_all_etf_data_1()
            yjl_dict=dict(zip(fund['基金代码'].tolist(),fund['溢价率'].tolist()))
            trader_df['溢价率']=trader_df['证券代码'].apply(lambda x :yjl_dict.get(str(x),0))
            print('00000000000000000000000000000000000000')
            trader_df=trader_df[trader_df['溢价率']<=max_yjl]
            trader_df=trader_df[trader_df['溢价率']>=min_yjl]
            trader_df.to_excel(r'买入股票\买入股票.xlsx')
        else:
            zdf_list=[]
            print('不开启策略缓冲区**********************')
            trader_df=pd.read_excel(r'{}\自定义交易股票池\自定义交易股票池.xlsx'.format(self.path),dtype='object')
            trader_df['证券代码']=trader_df['证券代码'].astype(str)
            df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
            df1=df[df['股票余额']>=10]
            df1['证券代码']=df1['证券代码'].astype(str)
            hold_stock_list=df1['证券代码'].tolist()
            def select_data(stock):
                if stock in hold_stock_list:
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
                    zdf=hist_df['涨跌幅'].tolist()[-1]
                    zdf_list.append(zdf)
                    score=self.mean_line_models(df=hist_df)
                    mean_score_list.append(score)
                    models=shape_analysis(df=hist_df)
                    mean_line=models.get_down_mean_line_sell(n=n)
                    if mean_line=='是':
                        sell_list.append('是')
                    else:
                        sell_list.append('不是')
                except:
                    print('{}有问题--处理交易股票池买入股票'.format(stock))
                    mean_score_list.append(None)
                    sell_list.append('是')
                    zdf_list.append(None)
            trader_df['涨跌幅']=zdf_list
            trader_df['跌破均线']=sell_list
            trader_df['均线得分']=mean_score_list
            trader_df=trader_df[trader_df['涨跌幅']>=min_zdf]
            trader_df=trader_df[trader_df['涨跌幅']<=max_zdf]
            trader_df=trader_df[trader_df['跌破均线']=='不是']  
            trader_df=trader_df[trader_df['均线得分']>=buy_min_srore]
            fund=self.dfcf_etf_data.get_all_etf_data_1()
            yjl_dict=dict(zip(fund['基金代码'].tolist(),fund['溢价率'].tolist()))
            trader_df['溢价率']=trader_df['证券代码'].apply(lambda x :yjl_dict.get(str(x),0))
            print('00000000000000000000000000000000000000')
            trader_df=trader_df[trader_df['溢价率']<=max_yjl]
            trader_df=trader_df[trader_df['溢价率']>=min_yjl]
            print(trader_df)
            is_buy=text['是否开启当日卖出买回']
            if is_buy=='是':
                trader_df.to_excel(r'买入股票\买入股票.xlsx')
            else:
                today_trades=self.trader.today_trades()
                if today_trades.shape[0]>0:
                    trader_list=today_trades['证券代码'].tolist()
                    trader_df['今日成交']=trader_df['证券代码'].apply(lambda x: '是' if x in trader_list else '不是')
                    trader_df=trader_df[trader_df['今日成交']=='不是']
                    trader_df.to_excel(r'买入股票\买入股票.xlsx')
                else:
                    print('当日没有委托）））））））））））））））））））')
            return trader_df
    def get_buy_sell_stock(self):
        '''
        获取买卖数据
        '''
        with open(r'{}\自定义红利低波交易配置.json'.format(self.path),encoding='utf-8') as f:
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
                return '持股超过限制'
            else:
                return "持股不足"
        try:
            del df['Unnamed: 0']
        except:
            pass
        trader_df=pd.read_excel(r'买入股票\买入股票.xlsx',dtype='object')
        try:
            del trader_df['Unnamed: 0']
        except:
            pass
        sell_df=pd.read_excel(r'卖出股票\卖出股票.xlsx')
        sell_list=[]
        trader_df['选择']=trader_df['证券代码'].apply(select_stock)
        trader_df=trader_df[trader_df['选择']!='持股超过限制']
        if True:
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
                            print('{}符合最低分{}'.format(stock,hold_min_score))
                    except:
                        print('{}卖出数据有问题'.format(stock))
                #跌破均线分析
                '''
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
                '''
                #再次处理
                is_buffer=text['是否开启策略缓冲区']
                deviation_mean=text['偏离均线']
                deviation_up_spot=text['向上偏离N点卖出']
                deviation_down_spot=text['跌破偏离线下穿N点卖出']
                minimum_guarantee=text['偏离保底均线N卖出']
                n=text['自定义交易品种跌破N日均线卖出']
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
                            print('不开启策略缓冲区{}有问题'.format(stock))
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
                else:
                    print('不开启大涨卖出')
                sell_df=pd.DataFrame()
                sell_list=list(set(sell_list))
                print('************************')
                print(sell_list)
                is_sell=text['是否开启大跌不卖']
                sell_spot=text['大跌']
                if is_sell=='是':
                    print("开启大跌不卖****************")
                    for stock in sell_list:
                        try:
                            hist=self.data.get_hist_data_em(stock=stock)
                            zdf=hist['涨跌幅'].tolist()[-1]
                            if zdf>=sell_spot:
                                print('大跌不卖{} 今日涨跌幅{} 大于大跌涨跌幅{} 符合模型'.format(stock,zdf,sell_spot))
                            else:
                                print('大跌不卖{} 今日涨跌幅{} 小于大跌涨跌幅{} 不卖出'.format(stock,zdf,sell_spot))
                                sell_list.remove(stock)
                        except:
                            print('大跌不卖{} 开启大写不卖出有问题'.format(stock))
                else:
                    print('不开启大跌不卖00000000000000000000000000000000000000000')
                sell_df['证券代码']=sell_list
                sell_df['交易状态']='未卖'
                if sell_df.shape[0]>0:
                    print('卖出*****************')
                    print(sell_df)
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
                    if av_buy_num>=hold_limit:
                        av_buy_num=hold_limit
                    else:
                        av_buy_num=av_buy_num
                    buy_df=trader_df[:av_buy_num]
                    if buy_df.shape[0]>0:
                        pass
                    else:
                        buy_df=pd.DataFrame()
                        buy_df['证券代码']=[None]
                        buy_df['交易状态']=[None]
                else:
                    buy_df=trader_df[:buy_num]
                    if buy_df.shape[0]>0:
                        pass
                    else:
                        buy_df=pd.DataFrame()
                        buy_df['证券代码']=[None]
                        buy_df['交易状态']=[None]
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
            sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
            print(sell_df)
        else:
            pass
    def update_all_data(self):
        '''
        更新策略数据
        '''
        print(self.save_position())
        print(self.save_balance())
        self.get_del_buy_sell_data()
        self.get_buy_sell_stock()
        self.get_del_not_trader_stock()
        