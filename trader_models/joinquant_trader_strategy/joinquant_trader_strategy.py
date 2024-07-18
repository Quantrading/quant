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
import os
import pandas as pd
from trader_models.joinquant_trader_strategy.joinquant_data import joinquant_data
from trader_tool.base_func import base_func
from trader_tool.unification_data import unification_data
from trader_tool.tdx_data import tdx_data
class joinquant_trader_strategy:
    def __init__(self,trader_tool='ths',exe='C:/同花顺软件/同花顺/xiadan.exe',tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qq='1029762153@qq.com',open_set='否',qmt_path='D:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55009640',qmt_account_type='STOCK',name='run_joinquant_trader_strategy',n=0):
        '''
        分析模型
        n第几个组合
        0第一个组合
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
        self.n=n
        self.name=name
        with open(r'{}/聚宽跟单设置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        self.account=text['聚宽账户']
        self.password=text['聚宽密码']
        self.ratio=text['跟单比例']
        self.joinquant_data=joinquant_data(account=self.account,password=self.password,n=self.n)
        #交易时间
        self.trader_time_list=self.stock_data.get_trader_date_list()
        self.now_date=self.trader_time_list[-1]
        self.base_func=base_func()
        self.data=unification_data(trader_tool=self.trader_tool)
        self.data=self.data.get_unification_data()
        self.trader.connect()
        self.tdx_data=tdx_data()
        self.tdx_data.connect()
        self.save_position()
        self.save_balance()
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
           return '是'
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
            return '是'
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
        return '是'
    def save_balance(self):
        '''
        保持账户数据
        '''
        with open(r'{}/聚宽跟单设置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        self.trader.connect()
        df=self.trader.balance()
        df.to_excel(r'账户数据\账户数据.xlsx')
        return df
    def get_simultaneous_stock_hold_models(self):
        '''
        同步持股,交易模式1，对比持股获取买卖数据，会同步聚宽目前的持股
        '''
        trader_time_list=self.stock_data.get_trader_date_list()
        now_date=trader_time_list[-1]
        with open(r'{}/聚宽跟单设置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        simultaneous=text['是否需要同步持股']
        if simultaneous=='是':
            hold_stock=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
            if hold_stock.shape[0]>0:
                stock_list=hold_stock['证券代码'].tolist()
            #账户没有持股
            else:
                stock_list=[]
            account=pd.read_excel(r'账户数据\账户数据.xlsx')
            joinquant_hold=self.joinquant_data.get_position(date=now_date)
            if joinquant_hold.shape[0]>0:
                for stock,amount in zip(joinquant_hold['证券代码'].tolist(),joinquant_hold['amount'].tolist()):
                    try:
                        if stock in stock_list:
                            #账户持股数量
                            hold_amount=hold_stock[hold_stock['证券代码']==stock]['股票余额'].tolist()[-1]
                        else:
                            #账户没有持股直接安比例买入
                            hold_amount=0
                        #账户可用数量
                        hold=hold_stock[hold_stock['证券代码']==stock]
                        if hold.shape[0]>0:
                            av_amount=hold['可用余额'].tolist()[-1]
                        else:
                            av_amount=0
                        #可用金额
                        av_money=account['可用金额'].tolist()[-1]
                        #差的数据量账户-聚宽
                        #差的数据大于0账户多了卖出
                        #差的数据小于0账户少了买入
                        poor_amount=hold_amount-amount*self.ratio
                        poor_amount=self.trader.adjust_amount(stock=stock,amount=poor_amount)
                        data_type=self.trader.select_data_type(stock=stock)
                        if data_type in ['stock','fund'] and poor_amount>0 and poor_amount<100:
                            poor_amount=100
                        if data_type in ['stock','fund'] and poor_amount<=0 and poor_amount>-100:
                            poor_amount=-100
                        elif data_type=='bond' and poor_amount>0 and poor_amount<10:
                            poor_amount=10
                        elif data_type=='bond' and poor_amount<=0 and poor_amount>-10:
                            poor_amount=-10
                        else:
                            poor_amount=poor_amount
                        try:
                            price=self.data.get_spot_data(stock=stock)['最新价']
                        except:
                            try:
                                price=self.tdx_data.get_security_quotes_none(stock=stock)['price'].tolist()[-1]
                            except:
                                try:
                                    price=self.data.get_spot_trader_data(stock=stock)['价格'].tolist()[-1]
                                except:
                                    price=self.data.get_hist_data_em(stock=stock)['close'].tolist()[-1]
                        
                        #买入的价值
                        value=poor_amount*price
                        #买入差额
                        if poor_amount<=0:
                            if av_money>value:
                                amount=abs(poor_amount)
                                if amount !=0:
                                    self.trader.buy(security=stock,amount=amount,price=price)
                                    text1='聚宽跟单买入代码{} 价格{} 数量{}'.format(stock,price,amount)
                                    print(text1)
                                    self.base_func.adjust_hold_data(stock=stock,trader_type='buy',price=price,amount=amount)
                                    self.base_func.adjust_account_cash(stock=stock,trader_type='buy',price=price,amount=amount)
                                    self.base_func.seed_trader_info(text=text1)
                                else:
                                    text1='聚宽跟单{}已经买入'.format(stock)
                                    print(text1)
                            else:
                                text1='聚宽跟单买入失败代码,可用金额不足{} 买入价值{} {} 价格{} 数量{}'.format(av_amount,value,stock,price,amount)
                        #账户有多余的股票，卖出
                        else:
                            amount=abs(poor_amount)
                            if amount !=0:
                                self.trader.sell(security=stock,amount=amount,price=price)
                                text1='聚宽跟单卖出代码{} 价格{} 数量{}'.format(stock,price,amount)
                                self.base_func.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                self.base_func.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                                self.base_func.seed_trader_info(text=text1)
                            else:
                                text1='聚宽跟单{}已经卖出'.format(stock)
                                print(text1)
                    except Exception as e:
                        print('错误',e)
    def get_simultaneous_transaction_models(self):
        '''
        交易模式2,同步成交，不会同步目前的持股
        '''
        trader_time_list=self.stock_data.get_trader_date_list()
        now_date=trader_time_list[-1]
        #now_date='2023-11-02'
        hold_stock=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        account=pd.read_excel(r'账户数据\账户数据.xlsx')
        joinquant_trader=self.joinquant_data.get_backtrader_trader_log(date=now_date)
        joinquant_hold=self.joinquant_data.get_position(date=now_date)
        #账户可用数量
        if joinquant_trader.shape[0]>0:
            for stock,amount,transaction in zip(joinquant_trader['证券代码'],joinquant_trader['amount'],joinquant_trader['transaction']):
                try:
                    hold=hold_stock[hold_stock['证券代码']==stock]
                    if hold.shape[0]>0:
                        av_amount=hold['可用余额'].tolist()[-1]
                    else:
                        av_amount=0
                    #可用金额
                    av_money=account['可用金额'].tolist()[-1]
                    amount=amount*self.ratio
                    
                    data_type=self.trader.select_data_type(stock=stock)
                    amount=self.trader.adjust_amount(stock=stock,amount=amount)
                    if data_type in ['stock','fund'] and amount<100:
                        amount=100
                    elif data_type=='bond' and amount<10:
                        amount=10
                    else:
                        amount=amount
                    try:
                        price=self.data.get_spot_data(stock=stock)['最新价']
                    except:
                        try:
                            price=self.tdx_data.get_security_quotes_none(stock=stock)['price'].tolist()[-1]
                        except:
                            try:
                                price=self.data.get_spot_trader_data(stock=stock)['价格'].tolist()[-1]
                            except:
                                price=self.data.get_hist_data_em(stock=stock)['close'].tolist()[-1]
                    #买入的价值
                    value=amount*price
                    joinquant_hold_amount=joinquant_hold[joinquant_hold['证券代码']==stock]
                    if joinquant_hold_amount.shape[0]>0:
                        joinquant_amount=joinquant_hold_amount['amount'].tolist()[-1]
                    else:
                        joinquant_amount=0
                    #账户持股数量
                    hold=hold_stock[hold_stock['证券代码']==stock]
                    if hold.shape[0]>0:
                        hold_amount=hold['股票余额'].tolist()[-1]
                    else:
                        hold_amount=0
                    if transaction=='卖':
                        #如果账户可用持股大于聚宽下单,直接卖
                        if joinquant_amount==hold_amount:
                            print('聚宽跟单{}已经卖出'.format(stock))
                        else:
                            if av_amount>0:
                                if av_amount>=amount:
                                    self.trader.sell(security=stock,amount=amount,price=price)
                                    text1='聚宽跟单卖出代码{} 价格{} 数量{}'.format(stock,price,amount)
                                    self.base_func.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                    self.base_func.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                                    self.base_func.seed_trader_info(text=text1)
                                #持股数量小于下单数据直接卖出全部可用卖出的
                                else:
                                    amount=av_amount
                                    self.trader.sell(security=stock,amount=amount,price=price)
                                    text1='聚宽跟单卖出代码{} 价格{} 数量{}'.format(stock,price,amount)
                                    self.base_func.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                    self.base_func.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                                    self.base_func.seed_trader_info(text=text1)
                            else:
                                print('聚宽跟单{}已经卖出'.format(stock))
                    #买入的情况
                    else:
                        #
                        if joinquant_amount==hold_amount:
                            print('聚宽跟单{}已经买入'.format(stock))
                        else:
                            #可用资金大于下单价值
                            if av_money>value:
                                self.trader.buy(security=stock,amount=amount,price=price)
                                text1='聚宽跟单买入代码{} 价格{} 数量{}'.format(stock,price,amount)
                                print(text1)
                                self.base_func.adjust_hold_data(stock=stock,trader_type='buy',price=price,amount=amount)
                                self.base_func.adjust_account_cash(stock=stock,trader_type='buy',price=price,amount=amount)
                                self.base_func.seed_trader_info(text=text1)
                            else:
                                text1='聚宽跟单买入代码失败可用资金{}不足'.format(av_money)
                except Exception as e:
                        print('错误',e)
        else:
            print('{}没有成交'.format(now_date))
                        











                


            








                        
                    

