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
from datetime import datetime
from .user_def_models import user_def_moels
class tdx_plate_trader:
    def __init__(self,trader_tool='qmt',exe='C:/同花顺软件/同花顺/xiadan.exe',tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qq='1029762153@qq.com',open_set='否',qmt_path='D:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55009640',qmt_account_type='STOCK',name='customize_trading_strategies'):
        '''
        通达信板块交易
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
        self.user_def_moels=user_def_moels(trader_tool=self.trader_tool,exe=self.exe,
                                        tesseract_cmd=self.tesseract_cmd,qq=self.qq,
                                        open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                        qmt_account_type=self.qmt_account_type,name=self.name)
        self.user_def_moels=user_def_moels(trader_tool=self.trader_tool,exe=self.exe,
                                        tesseract_cmd=self.tesseract_cmd,qq=self.qq,
                                        open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                        qmt_account_type=self.qmt_account_type,name=self.name)
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
        try:
            df=self.trader.balance()
            df.to_excel(r'账户数据\账户数据.xlsx')
            return df
        except Exception as e:
            print(e)
    def read_tdx_trader_stock(self,path=r'C:\new_tdx\T0002\blocknew\BUY.blk'):
        '''
        读取通达信板块自选股交易
        '''
        try:
            stock_list=[]
            with open(r'{}'.format(path),'r+') as f:
                com=f.readlines()
            for i in com:
                i=i.strip()
                if len(str(i))>0:
                    stock_list.append(i)
            df=pd.DataFrame()
            df['证券代码']=stock_list
            df['证券代码']=df['证券代码'].apply(lambda x:str(x)[-6:])
            return df
        except:
            print('路径有问题{}'.format(path))
            df=pd.DataFrame()
            return df
    def read_tdx_trader_stock_buy(self):
        '''
        处理买入标的
        '''
        with open(r'{}/通达信板块交易.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        buy_path=text['买入板块路径']
        #持股数据
        hold_df=self.trader.position()
        print('持股*****************')
        if hold_df.shape[0]>0:
            hold_df['证券代码']=hold_df['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
            hold_stock_list=hold_df['证券代码'].tolist()
        else :
            hold_stock_list=[]
        #买入记录
        buy_log=pd.read_excel(r'{}\买入记录\买入记录.xlsx'.format(self.path))
        try:
            buy_log_1=buy_log[['证券代码','时间','检查']]
            buy_log_1['证券代码']=buy_log_1['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
            buy_log_1=buy_log_1[buy_log_1['时间']==str(datetime.now())[:10]]
            log_stock_list=buy_log_1['证券代码'].tolist()
        except:
            log_stock_list=[]
        try:
            del buy_log['Unnamed: 0']
        except:
            pass
        df=self.read_tdx_trader_stock(path=buy_path)
        if df.shape[0]>0:
            df['证券代码']=df['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
            df['持股检查']=df['证券代码'].apply(lambda x: '是' if x in hold_stock_list else '不是')
            print('**********************持股检查')
            df=df[df['持股检查']=='不是']
            df['时间']=str(datetime.now())[:10]
            df['检查']=df['证券代码'].apply(lambda x: '是' if x in log_stock_list else '不是')
            df1=df[df['检查']=='不是']
            df2=df1[['证券代码','时间','检查']]
            buy_log=pd.concat([buy_log,df2],ignore_index=True)
            buy_log.to_excel(r'{}\买入记录\买入记录.xlsx'.format(self.path))
            df1.to_excel(r'{}\买入标的\买入标的.xlsx'.format(self.path))
        else:
            df=pd.DataFrame()
            df.to_excel(r'{}\买入标的\买入标的.xlsx'.format(self.path))
    def read_tdx_trader_stock_sell(self):
        '''
        处理卖出标的
        '''
        with open(r'{}/通达信板块交易.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        sell_path=text['卖出板块路径']
        #持股数据
        hold_df=hold_df=self.trader.position()

        if hold_df.shape[0]>0:
            hold_df['证券代码']=hold_df['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
            hold_stock_list=hold_df['证券代码'].tolist()
        else:
            hold_stock_list=[]
        #卖出记录
        sell_log=pd.read_excel(r'{}\卖出记录\卖出记录.xlsx'.format(self.path))
        try:
            sell_log_1=sell_log[['证券代码','时间','检查']]
            sell_log_1['证券代码']=sell_log_1['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
            sell_log_1=sell_log_1[sell_log_1['时间']==str(datetime.now())[:10]]
            log_stock_list=sell_log_1['证券代码'].tolist()
        except:
            log_stock_list=[]
        try:
            del sell_log['Unnamed: 0']
        except:
            pass
        df=self.read_tdx_trader_stock(path=sell_path)
        if df.shape[0]:
            df['证券代码']=df['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
            df['持股检查']=df['证券代码'].apply(lambda x: '是' if x in hold_stock_list else '不是')
            df=df[df['持股检查']=='是']
            df['时间']=str(datetime.now())[:10]
            df['检查']=df['证券代码'].apply(lambda x: '是' if x in log_stock_list else '不是')
            df1=df[df['检查']=='不是']
            df2=df1[['证券代码','时间','检查']]
            sell_log=pd.concat([sell_log,df2],ignore_index=True)
            sell_log.to_excel(r'{}\卖出记录\卖出记录.xlsx'.format(self.path))
            df1.to_excel(r'{}\卖出标的\卖出标的.xlsx'.format(self.path))
        else:
            df=pd.DataFrame()
            df.to_excel(r'{}\卖出标的\卖出标的.xlsx'.format(self.path))
    def run_user_def_select_stock_models(self):
        '''
        运行自定义选股模型
        '''
        print('运行自定义选股模型*************88888888888888888888')
        with open(r'{}/通达信板块交易.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        is_open=text['是否开启选股自定义函数']
        select_models=text['选股自定义模型']
        df=pd.read_excel(r'{}\买入标的\买入标的.xlsx'.format(self.path))
        if df.shape[0]>0:
            df['证券代码']=df['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
        try:
            del df['Unnamed: 0']
        except:
            pass
        if is_open=='是':
            print('开启选股自定义模型')
            if df.shape[0]>0:
                name_list=list(select_models.keys())
                if len(name_list)>0:
                    for name in name_list:
                        func=select_models[name]
                        value_list=[]
                        for stock in df['证券代码'].tolist():
                            try:
                                run_func='self.user_def_moels.{}'.format(func)
                                value=eval(run_func)
                                value_list.append(value)
                            except:
                                value_list.append(False)
                        df[name]=value_list
                    print('**************')
                    print(df)                     
                    for column in name_list:
                        df=df[df[column]==True]
                    df.to_excel(r'{}\自定义选股模型\自定义选股模型.xlsx'.format(self.path))
                else:
                    print('没有自定义选股模型')
                    df.to_excel(r'{}\自定义选股模型\自定义选股模型.xlsx'.format(self.path))
            else:
                print('没有买入的标的')
                df.to_excel(r'{}\自定义选股模型\自定义选股模型.xlsx'.format(self.path))
        else:
            print('不开启自定义选股模型')
            df.to_excel(r'{}\自定义选股模型\自定义选股模型.xlsx'.format(self.path))
    def run_user_def_hold_stock_models(self):
        '''
        运行持股自定义模型
        '''
        print('运行持股自定义模型***************999999999999999999999*')
        with open(r'{}/通达信板块交易.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        is_open=text['是否开启持有自定义函数']
        select_models=text['持股自定义模型']
        df=pd.read_excel(r'{}\卖出标的\卖出标的.xlsx'.format(self.path))
        if df.shape[0]>0:
            df['证券代码']=df['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
        try:
            del df['Unnamed: 0']
        except:
            pass
        if is_open=='是':
            print('开启选股自定义模型')
            if df.shape[0]>0:
                name_list=list(select_models.keys())
                if len(name_list)>0:
                    for name in name_list:
                        func=select_models[name]
                        value_list=[]
                        for stock in df['证券代码'].tolist():
                            try:
                                run_func='self.user_def_moels.{}'.format(func)
                                value=eval(run_func)
                                value_list.append(value)
                            except:
                                value_list.append(False)
                        df[name]=value_list                     
                    for column in name_list:
                        df=df[df[column]==True]
                    df.to_excel(r'{}\自定义持股模型\自定义持股模型.xlsx'.format(self.path))
                else:
                    print('没有自定义选股模型')
                    df.to_excel(r'{}\自定义持股模型\自定义持股模型.xlsx'.format(self.path))
            else:
                print('没有买入的标的')
                df.to_excel(r'{}\自定义持股模型\自定义持股模型.xlsx'.format(self.path))
        else:
            print('不开启自定义选股模型')
            df.to_excel(r'{}\自定义持股模型\自定义持股模型.xlsx'.format(self.path))
    def get_buy_sell_data(self):
        '''
        获取买卖数据
        '''
        with open(r'{}/通达信板块交易.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        hold_limit=text['持股限制']
        hold_stock=pd.read_excel(r'持股数据\持股数据.xlsx')
        try:
            del hold_stock['Unnamed: 0']
        except:
            pass
        if hold_stock.shape[0]>0:
            hold_stock['证券代码']=hold_stock['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
            hold_stock_list=hold_stock['证券代码'].tolist()
            hold_amount=0
        else:
            hold_stock_list=[]
            hold_amount=0
        buy_df=pd.read_excel(r'{}\自定义选股模型\自定义选股模型.xlsx'.format(self.path))
        try:
            del buy_df['Unnamed: 0']
        except:
            pass
        if buy_df.shape[0]>0:
            buy_df['证券代码']=buy_df['证券代码'].apply(lambda x:'0'*(6-len(str(x)))+str(x))
        sell_df=pd.read_excel(r'{}\自定义持股模型\自定义持股模型.xlsx'.format(self.path))
        try:
            del sell_df['Unnamed: 0']
        except:
            pass
        if sell_df.shape[0]>0:
            sell_df['证券代码']=sell_df['证券代码'].apply(lambda x:'0'*(6-len(str(x)))+str(x))
            sell_stock_list=sell_df['证券代码'].tolist()
            sell_amount=len(sell_stock_list)
        else:
            sell_amount=0
        print('卖出股票**********************')
        sell_df.to_excel(r'{}\卖出股票\卖出股票.xlsx'.format(self.path))
        av_buy=(hold_limit-hold_amount)+sell_amount
        if av_buy>=hold_limit:
            av_buy=hold_limit
        else:
            av_buy=av_buy
        buy_df=buy_df[:av_buy]
        print('买入的标的***************************')
        print(buy_df)
        buy_df.to_excel(r'{}\买入股票\买入股票.xlsx'.format(self.path))   
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
        buy_df=pd.read_excel(r'{}\买入股票\买入股票.xlsx'.format(self.path),dtype='object')
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
            buy_df.to_excel(r'{}\买入股票\买入股票.xlsx'.format(self.path))
            print(buy_df)
        else:
            buy_df=pd.DataFrame()
            buy_df.to_excel(r'{}\买入股票\买入股票.xlsx'.format(self.path))
        #卖出
        sell_df=pd.read_excel(r'{}\卖出股票\卖出股票.xlsx'.format(self.path),dtype='object')
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
            sell_df.to_excel(r'{}\卖出股票\卖出股票.xlsx'.format(self.path))
            print(sell_df)
        else:
            sell_df=pd.DataFrame()
            sell_df.to_excel(r'{}\卖出股票\卖出股票.xlsx'.format(self.path))
        return buy_df,sell_df
    def trader_data(self):
        '''
        开始下单
        '''
        with open(r'{}\通达信板块交易.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        trader_models=text['交易模式']
        fix_amount=text['固定交易数量']
        fix_cash=text['固定交易金额']
        #先卖在买入
        sell_df=pd.read_excel(r'{}\卖出股票\卖出股票.xlsx'.format(self.path),dtype='object')
        if sell_df.shape[0]>0:
            sell_df['证券代码']=sell_df['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
            try:
                del sell_df['Unnamed: 0']
            except:
                pass
            for stock in sell_df['证券代码'].tolist():
                try:
                    price=self.data.get_spot_data(stock=stock)['最新价']
                    if trader_models=='数量':
                        #检查是否可以卖出
                        if self.trader.check_stock_is_av_sell(stock=stock,amount=fix_amount):
                            self.trader.sell(security=stock,price=price,amount=fix_amount)
                            print('交易模式{} 卖出 股票{} 数量{} 价格{}'.format(trader_models,stock,fix_amount,price))
                        else:
                            print('交易模式{} {} 不能卖出'.format(trader_models,stock))
                    elif trader_models=='金额':
                        trader_type,amount,price=self.trader.order_value(stock=stock,value=fix_cash,price=price,trader_type='sell')
                        if trader_type=='sell' and amount>=10:
                            self.trader.sell(security=stock,price=price,amount=amount)
                            print('交易模式{} 卖出 股票{} 数量{} 价格{}'.format(trader_models,stock,amount,price))
                        else:
                            print('交易模式{}卖出 {} 不能卖出'.format(trader_models,stock))
                    else:
                        print('{} 未知的交易模式{}'.format(stock,trader_models))
                except Exception as e:
                    print('{}卖出有问题'.format(stock))
                    print(e)
        else:
            print('没有卖出的数据********************')
        #买入
        buy_df=pd.read_excel(r'{}\买入股票\买入股票.xlsx'.format(self.path),dtype='object')
        if buy_df.shape[0]>0:
            buy_df['证券代码']=buy_df['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
            try:
                del buy_df['Unnamed: 0']
            except:
                pass
            for stock in buy_df['证券代码'].tolist():
                try:
                    price=self.data.get_spot_data(stock=stock)['最新价']
                    if trader_models=='数量':
                        print(fix_amount,'******************')
                        #检查是否可以买入
                        if self.trader.check_stock_is_av_buy(stock=stock,amount=fix_amount,price=price):
                            self.trader.buy(security=stock,price=price,amount=fix_amount)
                            print('交易模式{} 买入 股票{} 数量{} 价格{}'.format(trader_models,stock,fix_amount,price))
                        else:
                            print('交易模式{} {} 不能买入'.format(trader_models,stock))
                    elif trader_models=='金额':
                        trader_type,amount,price=self.trader.order_value(stock=stock,value=fix_cash,price=price,trader_type='buy')
                        if trader_type=='buy' and amount>=10:
                            self.trader.buy(security=stock,price=price,amount=amount)
                            print('交易模式{} 买入 股票{} 数量{} 价格{}'.format(trader_models,stock,amount,price))
                        else:
                            print('交易模式{} {} 不能买入'.format(trader_models,stock))
                    else:
                        print('{} 未知的交易模式{}'.format(stock,trader_models))
                
                except Exception as e:
                    print('{}买入有问题'.format(stock))
                    print(e)
    def delete_folder_contents(self):
        '''
        删除缓存内容
        '''
        print('删除缓存内容*********************')
        import shutil
        with open(r'分析配置.json',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        with open(r'{}\通达信板块交易.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text1=json.loads(com)
        qmt_path=text['qmt路径']
        desktop_path=text1['桌面路径']
        try:
            os.makedirs(name=r'{}\del_data'.format(desktop_path))
        except:
            pass
        del_com=r'{}\del_data'.format(desktop_path)
        del_com=del_com.replace('\\',"/")
        all_path=os.listdir(path=qmt_path)
        if len(all_path)>0:
            for path in all_path:
                if path[:5]=='down_':
                    del_path=os.path.join(qmt_path, path)
                    del_path=del_path.replace('\\',"/")
                    try:
                        shutil.move(del_path,del_com)
                    except Exception as e:
                        print(e)
                else:
                    pass
            try:
                shutil.rmtree(r'{}'.format(del_com))
            except:
                pass
        else:
            print('文件夹下面没有文件')           
    def update_all_data(self):
        '''
        更新全部数据
        '''
        print(self.save_position())
        print(self.save_position())
        self.read_tdx_trader_stock_buy()
        self.read_tdx_trader_stock_sell()
        self.run_user_def_select_stock_models()
        self.run_user_def_hold_stock_models()
        self.get_buy_sell_data()
        self.get_del_not_trader_stock()
        self.trader_data()
        self.delete_folder_contents()


            


        
        


        
    