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
class limit_trading_strategy:
    def __init__(self,trader_tool='ths',exe='C:/同花顺软件/同花顺/xiadan.exe',tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qq='1029762153@qq.com',open_set='否',qmt_path='D:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55009640',qmt_account_type='STOCK',name='run_limit_trading_strategy'):
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
        self.path=os.path.dirname(os.path.abspath(__file__))
        self.trader.connect()
        self.name=name
    def save_position(self):
        '''
        保存持股数据
        '''
        with open(r'{}/涨停板交易策略交易配置.json'.format(self.path),encoding='utf-8') as f:
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
                df1=df1[df1['可用余额']>=100]
                df1.to_excel(r'持股数据\持股数据.xlsx')
                return df1
            else:
                print('没有持股')
    def save_position_1(self):
        '''
        保存持股数据
        '''
        with open(r'{}/涨停板交易策略交易配置.json'.format(self.path),encoding='utf-8') as f:
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
                df1=df1[df1['可用余额']>=10]
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
        with open(r'{}/涨停板交易策略交易配置.json'.format(self.path),encoding='utf-8') as f:
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
    def get_ths_upper_limit_data(self):
        '''
        获取同花顺涨停数据
        '''
        new_date=''.join(str(self.get_new_trader_list()[-1]).split('-'))
        func="self.get_limit_up_pool(date='{}')".format(new_date)
        df=self.ths_limitup_data.read_func_data(func=func)
        df.to_excel(r'{}\同花顺涨停数据\同花顺涨停数据.xlsx'.format(self.path))
    def get_ths_limit_up_data(self):
        '''
        获取同花顺冲刺涨停数据
        '''
        new_date=''.join(str(self.get_new_trader_list()[-1]).split('-'))
        func="self.get_limit_up(date='{}')".format(new_date)
        df=self.ths_limitup_data.read_func_data(func=func)
        df=df.fillna(0)
        df.to_excel(r'同花顺冲刺涨停数据\同花顺冲刺涨停数据.xlsx')
    def select_limit_stock_data(self):
        '''
        选择涨停板数据
        '''
        with open(r'{}/涨停板交易策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        trader_type=text['交易类型']
        del_cyb=text['是否剔除创业板']
        n_daily=text['几天']
        n_num=text['几板']
        price=text['最新价']
        def select_stock(x):
            if x[:3] in ['300','688']:
                return '是'
            else:
                return '不是'
        def select_tarder_type(x):
            '''
            选择交易类型
            '''
            if x in trader_type:
                return '是'
            else:
                return '不是'
        df=pd.read_excel(r'{}\同花顺涨停数据\同花顺涨停数据.xlsx'.format(self.path),dtype='object')
        df['选择交易类型']=df['涨停形态'].apply(select_tarder_type)
        df=df[df['选择交易类型']=='是']
        try:
            del df['Unnamed: 0']
        except:
            pass
        df['创业板']=df['证券代码'].apply(select_stock)
        if del_cyb=='是':
            df=df[df['创业板']=='不是']
        else:
            df=df
        
        min_daily=n_daily[0]
        max_daily=n_daily[-1]
        min_num=n_num[0]
        max_num=n_num[-1]
        min_price=price[0]
        max_price=price[-1]
        df['最新价']=df['最新价'].apply(lambda x: float(x))
        df=df[df['几天']>=min_daily]
        df=df[df['几天']<=max_daily]
        df=df[df['几板']>=min_num]
        df=df[df['几板']<=max_num]
        df=df[df['最新价']>=min_price]
        df=df[df['最新价']<=max_price]
        df['封单额']=df['封单额'].apply(lambda x: float(x))
        limit_money=text['封单额']
        min_money=limit_money[0]
        max_money=limit_money[-1]
        df=df[df['封单额']>=min_money]
        df=df[df['封单额']<=max_money]
        df['流通市值']=df['流通市值'].apply(lambda x: float(x))
        flow_value_list=text['流通市值']
        min_value=flow_value_list[0]
        max_value=flow_value_list[-1]
        df=df[df['流通市值']>=min_value]
        df=df[df['流通市值']<=max_value]
        df['开板次数']=df['开板次数'].apply(lambda x: float(x))
        open_limit_list=text['开板次数']
        min_open_num=open_limit_list[0]
        max_open_num=open_limit_list[-1]
        df=df[df['开板次数']>=min_open_num]
        df=df[df['开板次数']<=max_open_num]
        zdf_list=[]
        if df.shape[0]>0:
            for stock in df['证券代码'].tolist():
                try:
                    hist=self.stock_data.get_stock_hist_data_em(stock=str(stock)[:6])
                    zf=hist['振幅'].tolist()[-1]
                    zdf_list.append(zf)
                except:
                    zdf_list.append(None)
        else:
            zdf_list=0
        df['当日振幅']=zdf_list
        zf_list=text['当日振幅']
        min_zf=zf_list[0]
        max_zf=zf_list[-1]
        df=df[df['当日振幅']>=min_zf]
        df=df[df['当日振幅']<=max_zf]
        df=df.sort_values(by='封单额比流通市值',ascending=False)
        df.to_excel(r'{}\选择涨停板股票\选择涨停板股票.xlsx'.format(self.path))
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
    def get_stock_line_analysis(self):
        '''
        对股票继续均线分析
        '''
        with open(r'{}/涨停板交易策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        mean_score=text['均线得分']
        df=pd.read_excel(r'{}\选择涨停板股票\选择涨停板股票.xlsx'.format(self.path),dtype='object')
        sroce_list=[]
        stock_list=df['证券代码'].tolist()
        for stock in stock_list:
            try:
                df1=self.stock_data.get_stock_hist_data_em(stock=stock,end_date='20500101')
                score=self.mean_line_models(df=df1)
                sroce_list.append(score)
            except:
                sroce_list.append(None)
        df['均线得分']=sroce_list
        df=df[df['均线得分']>=mean_score]
        df['交易状态']='未买'
        df.to_excel(r'{}\选择涨停板股票\选择涨停板股票.xlsx'.format(self.path))
        df.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
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
        收益分析
        '''
        with open(r'{}/涨停板交易策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        n=text['最近N天']
        max_retuen=text['最近N天最大收益率']
        min_return=text['最近N天最小收益率']
        max_down=text['最近N天最大回撤']
        zdf_list=[]
        max_down_list=[]
        df=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path),dtype='object')
        try:
            df['Unnamed: 0']
        except:
            pass
        stock_list=df['证券代码'].tolist()
        for i in tqdm(range(len(stock_list))):
            stock=stock_list[i][:6]
            try:
                df1=self.stock_data.get_stock_hist_data_em(stock=stock,end_date='20500101')
                zdf,down=self.get_return_ananlysis(df=df1,n=n)
                zdf_list.append(zdf)
                max_down_list.append(down)
            except:
                zdf_list.append(None)
                max_down_list.append(None)
        df['最近{}天收益'.format(n)]=zdf_list
        df['最近天{}最大回撤'.format(n)]=max_down_list
        df1=df
        df2=df1[df1['最近{}天收益'.format(n)]>=min_return]
        df3=df2[df2['最近{}天收益'.format(n)]<=max_retuen]
        df4=df3[df3['最近天{}最大回撤'.format(n)]>=max_down]
        df4.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
        return df4
    
    def get_del_buy_sell_data(self):
        '''
        处理交易股票池买入股票
        '''
        with open(r'{}/涨停板交易策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        limit=text['持股限制']
        df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        #df1=df[df['可用余额']>=100]
        df1=df
        hold_stock_list=df['证券代码'].tolist()
        trader_df=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path),dtype='object')
        def select_data(stock):
            if stock in hold_stock_list:
                num=df1[df1['证券代码']==stock]['可用余额'].tolist()[-1]
                if float(num)>=float(limit):
                    return '持股超过限制'
                else:
                    return '持股不足'
            else:
                return '没有持股'
        trader_df['持股检查']=trader_df['证券代码'].apply(select_data)
        trader_df=trader_df[trader_df['持股检查'] !='持股超过限制']
        trader_df.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
        return trader_df
    def get_buy_sell_stock(self):
        '''
        获取买卖数据
        '''
        with open('{}/涨停板交易策略交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        buy_num=text['买入前N']
        hold_limit=text['持有限制']
        df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        trader_df=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path),dtype='object')
        print('交易股票池*******************')
        print(trader_df)
        hold_num=df.shape[0]
        #卖出股票池
        sell_list=[]
        n=text['跌破N日均线卖出']
        if hold_num>0:
            stock_list=df['证券代码'].tolist()
            for stock in stock_list:
                hist=self.stock_data.get_stock_hist_data_em(stock=stock)
                shape=shape_analysis(df=hist)
                if shape.get_down_mean_line_sell(n=n):
                    sell_list.append(stock)
                if shape.get_over_lining_sell():
                    sell_list.append(stock)
            sell_df=pd.DataFrame()
            sell_list=list(set(sell_list))
            len_sell=len(sell_list)
            if len_sell>0:
                sell_df['证券代码']=sell_list
                sell_df['交易状态']='未卖'
                sell_df['策略名称']=self.name
                sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
                print('***********卖出股票')
                print(sell_df)
            else:
                print('**************没有卖出股票')
                sell_df['策略名称']=self.name
                sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
            av_buy_num=(hold_limit-hold_num)+len_sell
            buy_df=trader_df[:av_buy_num]
            buy_df['交易状态']='未买'
            buy_df['证券代码']=buy_df['证券代码']
            buy_df.to_excel(r'买入股票\买入股票.xlsx')  
            print('买入股票*************')
            print(buy_df)
        else:
            buy_df=trader_df[:buy_num]
            buy_df['交易状态']='未买'
            buy_df['证券代码']=buy_df['证券代码']
            buy_df['策略名称']=self.name
            buy_df.to_excel(r'买入股票\买入股票.xlsx')
            print('买入股票*************')
            print(buy_df)
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
        self.get_ths_upper_limit_data()
        self.select_limit_stock_data()
        self.get_stock_line_analysis()
        self.get_stock_mean_line_retuen_analysis()
        self.get_del_buy_sell_data()
        self.get_buy_sell_stock()
        self.get_del_not_trader_stock()
    def cacal_zig_data(self,stock='123018',x=0.005):
        '''
        计算之字转向
        x=5%之子转向
        :return:
        '''
        ZIG_STATE_START = 0
        ZIG_STATE_RISE = 1
        ZIG_STATE_FALL = 2
        df=self.bond_cov_data.get_cov_bond_spot_trader_data(stock=stock)
        df['价格']=df['价格'].astype(float)
        # print(list(df["close"]))
        df = df[::-1]
        df = df.reset_index(drop=True)
        # df = df.iloc[-100:]
        x = x
        k = df["价格"]
        d = df["时间"]
        peer_i = 0
        candidate_i = None
        scan_i = 0
        peers = [0]
        z = np.zeros(len(k))
        state = ZIG_STATE_START
        while True:
            scan_i += 1
            if scan_i == len(k) - 1:
                # 扫描到尾部
                if candidate_i is None:
                    peer_i = scan_i
                    peers.append(peer_i)
                else:
                    if state == ZIG_STATE_RISE:
                        if k[scan_i] >= k[candidate_i]:
                            peer_i = scan_i
                            peers.append(peer_i)
                        else:
                            peer_i = candidate_i
                            peers.append(peer_i)
                            peer_i = scan_i
                            peers.append(peer_i)
                    elif state == ZIG_STATE_FALL:
                        if k[scan_i] <= k[candidate_i]:
                            peer_i = scan_i
                            peers.append(peer_i)
                        else:
                            peer_i = candidate_i
                            peers.append(peer_i)
                            peer_i = scan_i
                            peers.append(peer_i)
                break
            if state == ZIG_STATE_START:
                if k[scan_i] >= k[peer_i] * (1 + x):
                    candidate_i = scan_i
                    state = ZIG_STATE_RISE
                elif k[scan_i] <= k[peer_i] * (1 - x):
                    candidate_i = scan_i
                    state = ZIG_STATE_FALL
            elif state == ZIG_STATE_RISE:
                if k[scan_i] >= k[candidate_i]:
                    candidate_i = scan_i
                elif k[scan_i] <= k[candidate_i] * (1 - x):
                    peer_i = candidate_i
                    peers.append(peer_i)
                    state = ZIG_STATE_FALL
                    candidate_i = scan_i
            elif state == ZIG_STATE_FALL:
                if k[scan_i] <= k[candidate_i]:
                    candidate_i = scan_i
                elif k[scan_i] >= k[candidate_i] * (1 + x):
                    peer_i = candidate_i
                    peers.append(peer_i)
                    state = ZIG_STATE_RISE
                    candidate_i = scan_i
        for i in range(len(peers) - 1):
            peer_start_i = peers[i]
            peer_end_i = peers[i + 1]
            start_value = k[peer_start_i]
            end_value = k[peer_end_i]
            a = (end_value - start_value) / (peer_end_i - peer_start_i)  # 斜率
            for j in range(peer_end_i - peer_start_i + 1):
                z[j + peer_start_i] = start_value + a * j
        df['结果']=z
        #前天
        line_1=df['结果'].shift(2)
        #昨天
        line_2=df['结果'].shift(1)
        #今天
        line_3=df['结果'].shift(0)
        result=[]
        for x,y,z in zip(line_1,line_2,line_3):
            if x<y and y>z:
                result.append('sell')
            elif x>y and y<z:
                result.append('buy')
            else:
                result.append(None)
        df['买卖点']=result
        df1=df.sort_index(ascending=False,ignore_index=True)
        return df1
    def get_mean_line_trader_analysis(self,stock='128036',window=30):
        '''
        均线交易分析模型，
        数据为3秒一次
        60 3分钟
        '''
        import numpy as np
        df=self.bond_cov_data.get_cov_bond_hist_data(stock=stock,data_type='1')
        df['close']=df['close'].astype(float)
        df['mean_5']=df['close'].rolling(5).mean()
        x1=df['mean_1'].shift(2)
        x2=df['mean_1'].shift(1)
        x3=df['mean_1'].shift(0)
        df['买点']=np.logical_and(x1<x2,x3>x2)
        df['卖点']=np.logical_and(x1>x2,x3<x2)
        print(df[df['买点']==True])
        buy_spot=df['买点'].tolist()[-1]
        sell_spot=df['卖点'].tolist()[-1]
        if buy_spot==True:
            return 'buy'
        else:
            return False
        if sell_spot==True:
            return 'sell'
        else:
            return False
    def get_macd_trader_analysis(self,stock='111007'):
        '''
        macd
        '''
        pass
    def get_mi_pulse_trader_analysis(self,n=10,x1=1,x2=-2,stock='111007',select='是',h='9',mi='3300',num=1.5):
        '''
        分钟脉冲分析     
        '''
        df=self.bond_cov_data.get_cov_bond_spot_trader_data(stock=stock)
        date=df['时间'].tolist()[-1]
        if select=='是':
            now_date=float(h+mi)
            if float(date)<=now_date:
                x1=x1*num
            else:
                x1=x1
        else:
            x1=x1
        n=20*n
        zdf_list=df['涨跌幅'].tolist()[-n:]
        zdf=zdf_list[-1]-zdf_list[0]
        if zdf>=x1:
            return 'sell'
        elif zdf<=x2:
            return 'buy'
        else:
            return False
    def get_dynamic_trader_analysis(self,daily=5,mi=10,x=0.3,x1=-0.3,stock='128041'):
        '''
        动态分钟脉冲
        '''
        df=self.bond_cov_data.get_cov_bond_hist_data(stock=stock)
        df['平均振幅']=df['振幅'].rolling(daily).mean()
        zdf=df['平均振幅'].tolist()[-1]
        zdf=abs(zdf)
        #实时交易数据
        df1=self.bond_cov_data.get_cov_bond_spot_trader_data(stock=stock)
        n=20*mi
        zdf_list=df1['涨跌幅'].tolist()[-n:]
        spot_zdf=zdf_list[-1]-zdf_list[0]
        if spot_zdf>=0:
            sell_zdf=zdf*x
            if spot_zdf>sell_zdf:
                return 'sell'
            else:
                return False
        elif spot_zdf<0:
            buy_zdf=zdf*x1
            if spot_zdf<=buy_zdf:
                return 'buy'
            else:
                return False
        else:
            return False
    def get_hour_pulse_trader_analysis(self,hour=1,x1=5,x2=-3,stock=''):
        '''
        小时趋势
        '''
        df=self.bond_cov_data.get_cov_bond_hist_data(stock=stock,data_type='1')
        df['累计涨跌幅']=df['涨跌幅'].cumsum()
        zdf_list=df['累计涨跌幅'].tolist()[-hour:]
        zdf=zdf_list[-1]-zdf_list[0]
        if zdf>=x1:
            return 'sell'
        elif zdf<=x2:
            return 'buy'
        else:
            return False
    def surge_and_fall_overfall_rebound(self,stock='123018',min_return=7,max_down=-1,max_df=-5,ft_return=3):
        '''
        冲高回落--超跌反弹
        min_return冲高的涨跌幅
        max_down最大的回撤
        #超跌反弹
        max_df最大跌幅
        ft_return反弹收益
        '''
        df=self.bond_cov_data.get_cov_bond_spot_trader_data(stock=stock)
        #最大涨跌幅
        max_return_ratio=max(df['涨跌幅'].tolist())
        #现在的涨跌幅
        now_return_ratio=df['涨跌幅'].tolist()[-1]
        #目前的收益回撤
        max_down_ratio=now_return_ratio-max_return_ratio
        if max_return_ratio>min_return and max_down_ratio<=max_down:
            text='冲高回落，股票{} 最大涨跌幅{} 现在的涨跌幅{} 收益回撤{}'.format(stock,max_return_ratio,now_return_ratio,max_down_ratio)
            return '冲高回落',True,text
        else:
            text='不符合冲高回落，股票{} 最大涨跌幅{} 现在的涨跌幅{} 收益回撤{}'.format(stock,max_return_ratio,now_return_ratio,max_down_ratio)
            return '冲高回落',False,text
        #最小涨跌幅
        min_return_ratio=min(df['涨跌幅'].tolist())
        #反弹收益
        ft_return_ratio=now_return_ratio-min_return_ratio
        if min_return_ratio<max_df and ft_return_ratio >ft_return:
            text='超跌反弹，股票{} 最大跌幅{} 现在的涨跌幅{} 收益反弹{}'.format(stock, min_return_ratio,now_return_ratio,ft_return_ratio)
            return '超跌反弹',True,text
        else:
            text='不符合超跌反弹，股票{} 最大跌幅{} 现在的涨跌幅{} 收益反弹{}'.format(stock, min_return_ratio,now_return_ratio,ft_return_ratio)
            return "超跌反弹",False,text
    def get_trader_mean_line_analysis(self,stock='128041',n=5,mean_line=20):
        '''
        盘中参考均线分析
        '''
        df=self.bond_cov_data.get_cov_bond_hist_data(stock=stock,data_type='5',limit=100000000)
        df['mean_line']=df['close'].rolling(mean_line).mean()
        open_price=df['open'].tolist()[-1]
        close_price=df['close'].tolist()[-1]
        mean_price=df['mean_line'].tolist()[-1]
        if open_price <mean_price and close_price>mean_price:
            return 'buy'
        elif open_price>mean_price and close_price<mean_price:
            return 'sell'
        else:
            return False
    def get_rising_speed_analysis(self,n=5,stock='110070'):
        '''
        涨速分析
        '''
        import matplotlib.pyplot as plt
        df=self.bond_cov_data.get_cov_bond_spot_trader_data(stock=stock)
        df['实时涨跌幅'][-200:].plot()
        plt.show()
    def get_creat_cov_bond_grid(self,daily=5,n=6,df='',entiy_select='0.5',bs=2,spot_zdf=2):
        '''
        生成网格交易 从上到下一次为1，2，3，4，5网格
        '''
        #df=self.bond_cov_data.get_cov_bond_hist_data(stock=stock)
        df=df
        #因为数据是实时数据，题材今天的数据
        df1=df[-daily+1:-1]
        mean_zf=df1['振幅'].mean()
        #单元格
        entiy=mean_zf/n
        if float(entiy)<=float(entiy_select):
            entiy=entiy*bs
        else:
            entiy=entiy
        data_dict={}
        for i in range(1,int(n/2)+1):
            data_dict['{}'.format(i)]=entiy*(abs((i-1)-int(n/2)))
        for i in range(int(n/2)+1,n+1):
            data_dict['{}'.format(i)]=entiy*(int(n/2)-i)
        for j in range(1,n):
            if spot_zdf>data_dict['1']:
                index='up'
            elif spot_zdf<data_dict[str(n)]:
                index='down'
            elif spot_zdf<=data_dict[str(j)] and spot_zdf>=data_dict[str(j+1)]:
                index=j
        #print(data_dict)
        return data_dict,entiy,index
    def get_grid_analysis(self,stock='110074',daily=5,n=6,time_size=600,buy_sell_dot=0.75,
    stop=True,stop_line=-3,entiy_select='0.5',bs=2):
        '''
        网格分析数据3秒一次数据
        daily最近N天，振幅为平均值为上下网格
        n网格线多少
        time_size时间窗口 20是一分钟
        buy_sell_dot 到到目标网格的分位数
        stop开启网格止损
        stop_line=-3止损线
        '''
        from datetime import datetime
        now_time=datetime.now()
        hist_df=self.bond_cov_data.get_cov_bond_hist_data(stock=stock)
        df=self.bond_cov_data.get_cov_bond_spot_trader_data(stock=stock)
        #print(df)
        zdf_list=df['涨跌幅'].tolist()[-time_size:]
        #前N分钟的涨跌幅
        pre_zdf=zdf_list[0]
        #现在的涨跌幅
        now_zdf=zdf_list[-1]
        if now_zdf<=stop_line and stop==True:
            text='{} {} 现在的涨跌幅 {}达到止损线全部卖出'.format(now_time,stock,now_zdf)
            return 'all_sell',text
        else:
            #前面涨跌幅在的格子
            pre_dict,entiy,pre_index=self.get_creat_cov_bond_grid(daily=daily,n=n,df=hist_df,spot_zdf=pre_zdf,entiy_select=entiy_select,bs=bs)
            #现在涨跌幅在的格子
            now_dict,entiy,now_index=self.get_creat_cov_bond_grid(daily=daily,n=n,df=hist_df,spot_zdf=now_zdf,entiy_select=entiy_select,bs=bs)
            #现在的可转债涨跌幅大于上边线自动添加一个卖出网格
            if now_index in ['up'] and now_zdf>=pre_dict[str(1)]+(entiy*buy_sell_dot):
                text='卖出 时间{} 可转债{} 突破上边线而且达到{}分位数'.format(now_time,stock,buy_sell_dot)
                return 'sell_up',text
            elif now_index=='down' or pre_index=='down':
                text='卖出 时间{} 控制住{}跌破下边线'.format(now_time,stock)
                return 'sell_down',text
            elif now_index in ['up'] or pre_index=='up':
                text='卖出 时间{} 可转债{}突破上边线'.format(now_time,stock)
                return 'sell',text
            #向上多单元格跳动，比如从3单元格直接跳动到1 单元格
            elif (pre_index-now_index)>=2:
                text='卖出 向上多单元格跳动 {} {} 从{}单元格跳到{}单元格'.format(now_time,stock,pre_index,now_index)
                return 'sell',text
            #向下多单元格跳动，比如从1单元格直接跳动到3 单元格
            elif (pre_index-now_index)<=-2:
                text='买入 向下多单元格跳动 {} {} 从{}单元格跳到{}单元格'.format(now_time,stock,pre_index,now_index)
                return 'buy',text
            #一个一个单元格跳动
            #在同一个单元格不操作
            elif now_index==pre_index:
                text='{} 可转债{} 现在的涨跌幅{} 在同一个网格布交易 目前的网格{}'.format(now_time,stock,now_zdf,now_index)
                return False,text
            else:
                #买入的操作
                #可转债从上一个格子进入下一个格子同时现在的涨跌幅在新格子的1-buy_sell_dot的分位数位置
                if pre_index <now_index:
                    if now_zdf<=pre_dict[str(now_index)]-(entiy*buy_sell_dot):
                        text='买入 {} {} 从{}单元格跌到{}单元格 达到{}单元格的{}位置'.format(now_time,
                        stock,pre_index,now_index,now_index,buy_sell_dot)
                        return 'buy',text
                    else:
                        text='{} {} 从{}单元格跌到{}单元格目前没有达到{}买入点'.format(now_time,
                        stock,pre_index,now_index,buy_sell_dot)
                        return False,text
                #卖出操作
                elif pre_index >now_index:
                    if now_zdf>=pre_dict[str(pre_index)]+(entiy*buy_sell_dot):
                        text='卖出 {} {} 从{}单元格上涨{}单元格 达到{}单元格 的{}位置'.format(now_time,
                        stock,pre_index,now_index,now_index,buy_sell_dot)
                        return 'sell',text
                    else:
                        text='{} {} 从{}单元格上涨{}单元格目前没有达到{}卖出点'.format(now_time,
                        stock,pre_index,now_index,buy_sell_dot)
                        return False,text 
                else:
                    return False,0   
    def hold_bond_cov_exchange(self,stock='127080',trader_type='sell'):
        '''
        可转债上影线
        '''      
        df=pd.read_excel(r'持股数据\持股数据.xlsx')
        try:
            del df['Unnamed: 0']
        except:
            pass
        stock_list=df['代码'].tolist()
        for i in tqdm(range(len(stock_list))):
            stock=stock_list[i]
            models=shape_analysis(stock=stock)
            print(models.get_over_lining_sell())
if __name__=='__main__':
    with open('{}/涨停板交易策略交易配置.json'.format(self.path),'r+',encoding='utf-8') as f:
        com=f.read()
    text=json.loads(com)
    path=text['qmt路径']
    account=text['qmt账户']
    account_type=text['qmt账户类型']
    models=analysis_models(path=path,account=account,account_type=account_type)
    models.updata_all_data()