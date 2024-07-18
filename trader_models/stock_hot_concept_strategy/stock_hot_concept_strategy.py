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
class stock_hot_concept_strategy:
    def __init__(self,trader_tool='qmt',exe='C:/同花顺软件/同花顺/xiadan.exe',tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qq='1029762153@qq.com',open_set='否',qmt_path='D:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55009640',qmt_account_type='STOCK',name='customize_trading_strategies'):
        '''
        股票热门概念
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
    def get_ths_stock_rq_data(self):
        '''
        获取同花顺人气
        '''
        df=self.ths_rq.get_hot_stock_rank()
        df.to_excel(r'{}\同花顺人气\同花顺人气.xlsx'.format(self.path))
        return df
    def get_all_ths_hot_concept(self):
        '''
        获取同花顺全部题材
        '''
        with open(r'{}\股票热门概念策略.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        n=text['分析题材前N']
        print('获取同花顺全部题材')
        ths_concept=self.ths_rq.get_stock_concept_rot_rank()[:n]
        ths_concept.to_excel(r'{}\同花顺热门概念\同花顺热门概念.xlsx'.format(self.path))
        all_concept_stock=pd.DataFrame()
        for stock,name in zip(ths_concept['概念代码'],ths_concept['概念名称']):
            try:
                df=self.ths_board_concept_data.stock_board_cons_ths(symbol=stock)
                df['概念名称']=name
                all_concept_stock=pd.concat([all_concept_stock,df],ignore_index=True)
                print('{}获取完成'.format(name))
            except:
                print('{}概念有问题'.format(name))
        all_concept_stock=all_concept_stock.drop_duplicates(subset=['代码'], keep='first')
        all_concept_stock['排序']=range(0,all_concept_stock.shape[0])
        all_concept_stock.to_excel(r'{}\同花顺概念热门成分股\同花顺概念热门成分股.xlsx'.format(self.path))
        return all_concept_stock
    def select_stock_data(self):
        '''
        选择股票
        '''
        with open(r'{}\股票热门概念策略.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        del_list=text['剔除代码开头']
        price_list=text['价格区间']
        min_price=price_list[0]
        max_price=price_list[-1]
        zdf_list=text['实时涨跌幅区间']
        min_zdf=zdf_list[0]
        max_zdf=zdf_list[-1]
        df=pd.read_excel(r'{}\同花顺概念热门成分股\同花顺概念热门成分股.xlsx'.format(self.path),dtype='object')
        try:
            del df['Unnamed: 0']
        except:
            pass
        def del_stock(x):
            if str(x)[:2] in del_list:
                return '是'
            else:
                return '不是'
        df['剔除']=df['代码'].apply(del_stock)
        df['现价']=df['现价'].replace('--',0)
        df['涨跌幅']=df['涨跌幅'].replace('--',0)
        df['现价']=pd.to_numeric(df['现价'])
        df['涨跌幅']=pd.to_numeric(df['涨跌幅'])
        df=df[df['剔除']=='不是']
        df=df[df['现价']>=min_price]
        df=df[df['现价']<=max_price]
        df=df[df['涨跌幅']>=min_zdf]
        df=df[df['涨跌幅']<=max_zdf]
        df.to_excel(r'{}\选择股票\选择股票.xlsx'.format(self.path))
        return df
    def get_stock_shape_analysis(self):
        '''
        股票形态分析
        '''
        print('股票形态分析')
        df=pd.read_excel(r'{}\选择股票\选择股票.xlsx'.format(self.path),dtype='object')
        try:
            del df['Unnamed: 0']
        except:
            pass
        stock_list=df['代码'].tolist()
        over_lining=[]
        mean_line=[]
        with open(r'{}\股票热门概念策略.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        n=text['跌破N日均线卖出']
        for i in tqdm(range(len(stock_list))):
            stock=stock_list[i]
            try:
                hist_df=self.data.get_hist_data_em(stock=stock)
                models=shape_analysis(df=hist_df)
            
                over=models.get_over_lining_sell()
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
        df1.to_excel(r'{}\形态选择\形态选择.xlsx'.format(self.path))
        return df1
    def get_stock_mean_line_retuen_analysis(self):
        '''
        股票均线收益分析
        '''
        print('股票均线收益分析')
        with open(r'{}/股票热门概念策略.json'.format(self.path),encoding='utf-8') as f:
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
        df=pd.read_excel(r'{}\形态选择\形态选择.xlsx'.format(self.path),dtype='object')
        try:
            df['Unnamed: 0']
        except:
            pass
        stock_list=df['代码'].tolist()
        for i in tqdm(range(len(stock_list))):
            stock=stock_list[i]
            try:
                df1=self.data.get_hist_data_em(stock=stock)
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
        #df.to_excel(r'分析原始数据\分析原始数据.xlsx')
        df1=df[df['均线得分']>=min_secore]
        df2=df1[df1['最近{}天收益'.format(n)]>=min_return]
        df3=df2[df2['最近{}天收益'.format(n)]<=max_retuen]
        df4=df3[df3['最近天{}最大回撤'.format(n)]>=max_down]
        df4.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
        return df4
    def get_del_buy_sell_data(self):
        '''
        处理交易股票池买入股票
        '''
        with open(r'{}/股票热门概念策略.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        limit=text['持股限制']
        n=text['跌破N日均线卖出']
        df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        df1=df[df['可用余额']>=10]
        hold_stock_list=df['证券代码'].tolist()
        trader_df=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path),dtype='object')
        try:
            df['Unnamed: 0']
        except:
            pass
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
        trader_df['持股检查']=trader_df['代码'].apply(select_data)
        trader_df=trader_df[trader_df['持股检查'] !='持股超过限制']
        trader_df=trader_df.sort_values(by='均线得分',ascending=False)
        trader_df.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
        return trader_df
    def get_select_trader_stock_data(self):
        '''
        选择交易股票池
        '''
        ths_df=pd.read_excel(r'{}\同花顺热门概念\同花顺热门概念.xlsx'.format(self.path),dtype='object')
        try:
            ths_df['Unnamed: 0']
        except:
            pass
        trader_df=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
        try:
            trader_df['Unnamed: 0']
        except:
            pass
        with open(r'{}/股票热门概念策略.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        rank_name=text['热门题材交易前N']
        buy_n=text['每个题材买N']
        name_list=ths_df['概念名称'].tolist()[:rank_name][:rank_name]
        data=pd.DataFrame()
        for name in name_list:
            df1=trader_df[trader_df['概念名称']==name][:buy_n]
            data=pd.concat([data,df1],ignore_index=True)
        data.to_excel(r'{}\最后交易股票池\最后交易股票池.xlsx'.format(self.path))
        return data
    def get_buy_sell_stock(self):
        '''
        获取买卖数据
        '''
        with open('{}/股票热门概念策略.json'.format(self.path),encoding='utf-8') as f:
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
                return '超过持股限制'
            else:
                return "持股不足"
        try:
            del df['Unnamed: 0']
        except:
            pass
        trader_df=pd.read_excel(r'{}\最后交易股票池\最后交易股票池.xlsx'.format(self.path),dtype='object')
        trader_df['证券代码']=trader_df['代码']
        trader_df['证券代码']=trader_df['证券代码'].astype(str)
        for i in range(0,10):
            try:
                del trader_df['Unnamed: 0.{}'.format(i)]
            except:
                pass
        print('交易股票池*******************')
        print(trader_df)
        trader_df['选择']=trader_df['代码'].apply(select_stock)
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
                    bond_data=self.data.get_hist_data_em(stock=stock)
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
            sell_df=pd.DataFrame()
            sell_df['证券代码']=sell_list
            sell_df['交易状态']='未卖'
            #剔除新股申购
            if sell_df.shape[0]>0:
                print('卖出可转债*****************')
                print(sell_df)
                sell_df['策略名称']=self.name
                sell_df['证券代码']=sell_df['证券代码'].apply(lambda x:'0'*(6-len(str(x)))+str(x))
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
            buy_df['证券代码']=buy_df['证券代码'].apply(lambda x:'0'*(6-len(str(x)))+str(x))
            buy_df.to_excel(r'买入股票\买入股票.xlsx')
            return buy_df
        else:
            buy_df=trader_df[:hold_limit]
            buy_df['交易状态']='未买'
            print('买入可转债*****************')
            print(buy_df)
            buy_df['策略名称']=self.name
            buy_df['证券代码']=buy_df['证券代码'].apply(lambda x:'0'*(6-len(str(x)))+str(x))
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
            buy_df.to_excel(r'买入股票\买入股票.xlsx')
            print('买入的股票））））））））））））））））））））））））））')
            print(buy_df)
        else:
            print('买入的股票为空************')
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
            print('卖出股票））））））））））））））））））））')
            print(sell_df)
        else:
            print('卖出的股票为空************')
    def get_update_all_data(self):
        '''
        更新全部数据
        '''
        self.save_position()
        self.save_balance()
        self.get_all_ths_hot_concept()
        self.select_stock_data()
        self.get_stock_shape_analysis()
        self.get_stock_mean_line_retuen_analysis()
        self.get_del_buy_sell_data()
        self.get_select_trader_stock_data()
        self.get_buy_sell_stock()
        self.get_del_not_trader_stock()
    