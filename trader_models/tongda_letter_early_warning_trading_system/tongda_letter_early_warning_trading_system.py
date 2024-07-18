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
class tongda_letter_early_warning_trading_system:
    def __init__(self,trader_tool='qmt',exe='C:/同花顺软件/同花顺/xiadan.exe',tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qq='1029762153@qq.com',open_set='否',qmt_path='D:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55009640',qmt_account_type='STOCK',name='customize_trading_strategies'):
        '''
        通达信预警系统
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
    def params_tdx_text(self):
        '''
        分析通达信内容
        '''
        with open(r'{}\通达信预警系统.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        path=text['通达信警告保存路径']
        columns=text['通达信警告列名称']
        try:
            with open(r'{}'.format(path),'r+',encoding='utf-8') as f:
                com=f.readlines()
        except:
            with open(r'{}'.format(path),'r+',encoding='gbk') as f:
                com=f.readlines()
        result_list=[]
        if len(com)<0:
            df=pd.DataFrame()
            df.to_excel(r'{}\原始数据\原始数据.xlsx'.format(self.path))
            print('没有警告内容****')
        else:
            for i in com:
                result_list.append(str(i).strip().split('\t'))
            df=pd.DataFrame(result_list)
            if df.shape[0]>0:
                print('原始的数据*********************')
                print(df)
                df.columns=columns
                print('请仔细核对名称*************************')
                print(df)
                now_date=str(datetime.now())[:10]
                try:
                    df['时间']=df['时间'].apply(lambda x:str(x)[:10])
                    df=df[df['时间']==now_date]
                    df.to_excel(r'{}\原始数据\原始数据.xlsx'.format(self.path))
                except Exception as e:
                    print(e)
                    df.to_excel(r'{}\原始数据\原始数据.xlsx'.format(self.path))
            else:
                df=pd.DataFrame()
                df.to_excel(r'{}\原始数据\原始数据.xlsx'.format(self.path))
    def get_dea_buy_sell_data(self):
        '''
        处理买卖数据
        '''
        with open(r'{}\通达信预警系统.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        maker_list=text['订单唯一的标识行']
        log_df=pd.read_excel(r'{}\下单记录\下单记录.xlsx'.format(self.path))
        try:
            del log_df['Unnamed: 0']
        except:
            pass
        log_columns=log_df.columns.tolist()
        if len(log_columns)>0:
            log_columns=log_columns
        else:
            log_columns=[]
        df=pd.read_excel(r'{}\原始数据\原始数据.xlsx'.format(self.path))
        try:
            del df['Unnamed: 0']
        except:
            pass
        if df.shape[0]>0:
            df1=df
            df_columns=df.columns.tolist()
            alike_list=[]
            for i in maker_list:
                if i in df_columns and len(log_columns)==0:
                    df['{}_选择'.format(i)]='不是'
                    print('表格记录为空**********8')
                elif i in df_columns and i in log_columns:
                    df['{}_选择'.format(i)]=df[i].apply(lambda x: '是' if x in log_df[i].tolist() else '不是')
                    alike_list.append('{}_选择'.format(i))
                else:
                    print('{}标记不在2个表中'.format(i))
            for i in alike_list:
                df=df[df[i]=='不是']
            if df.shape[0]>0:
                print('下单的内容************************8')
                print(df)
                df.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
            else:
                print('没有下单的内容））））））））））））））））））')
                df=pd.DataFrame()
                df.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
        else:
            print('通达信没有预警内容********************')
    def run_user_def_models(self):
        '''
        运行自定义模型
        '''
        with open(r'{}\通达信预警系统.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        is_open=text['是否开启自定义模型']
        user_def_moels_name=list(text['自定义模型'].keys())
        user_func_models=text['自定义模型']
        df=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
        try:
            del df['Unnamed: 0']
        except:
            pass
        log_df=pd.read_excel(r'{}\下单记录\下单记录.xlsx'.format(self.path))
        try:
            del log_df['Unnamed: 0']
        except:
            pass
        if is_open=='是':
            if len(user_def_moels_name)>0:
                if df.shape[0]>0:
                    for name in user_def_moels_name:
                        func=user_func_models[name]
                        select_stock_list=[]
                        for stock in df['证券代码'].tolist():
                            text='self.user_def_moels.{}'.format(func)
                            stats=eval(text)
                            select_stock_list.append(stats)
                        df[name]=select_stock_list
                    for name in user_def_moels_name:
                        df=df[df[name]==True]
                    df.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
                    
                else:
                    print('没有交易数据*************************')
            else:
                print('没有自定义函数****************8')
        else:
            print('不开启自定义函数***********88')
    def analysis_trader_log(self):
        '''
        分析交易记录
        '''
        with open(r'{}\通达信预警系统.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        buy_con=text['买入警告条件']
        sell_con=text['卖出警告条件']
        log_df=pd.read_excel(r'{}\下单记录\下单记录.xlsx'.format(self.path))
        try:
            del log_df['Unnamed: 0']
        except:
            pass
        df=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
        try:
            del df['Unnamed: 0']
        except:
            pass
        if log_df.shape[0]>0:
            log_df['证券代码']=log_df['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
            log_df['时间']=log_df['时间'].apply(lambda x:str(x)[:10])
            log_df=log_df[log_df['时间']==str(datetime.now())[:10]]
            log_stock_list=log_df['证券代码'].tolist()
        else:
            print('没有交易记录')
            log_stock_list=[]
        if df.shape[0]>0:
            if log_df.shape[0]>0:
                df['交易选择']=df['证券代码'].apply(lambda x: '是' if x in log_stock_list else '不是')
                df1=df[df['交易选择']=='不是']
                log_df=pd.concat([log_df,df1],ignore_index=True)
                df1.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
                log_df.to_excel(r'{}\下单记录\下单记录.xlsx'.format(self.path))
            else:
                log_df=pd.concat([log_df,df],ignore_index=True)
                log_df.to_excel(r'{}\下单记录\下单记录.xlsx'.format(self.path))
                print('没有下单记录')
        else:
            print('没有交易股票池')



        
    def get_params_taredr_stock(self):
        '''
        拆分买卖数据
        '''
        with open(r'{}\通达信预警系统.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        df=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
        try:
            df['证券代码']=df['证券代码'].apply(lambda x : '0'*(6-len(str(x)))+str(x))
        except Exception as e:
            print(e)
        try:
            del df['Unnamed: 0']
        except:
            pass
        buy_list=text['买入警告条件']
        sell_list=text['卖出警告条件']
        if df.shape[0]>0:
            df['buy']=df['买卖条件'].apply(lambda x: '是' if x in buy_list else '不是')
            df['sell']=df['买卖条件'].apply(lambda x: '是' if x in sell_list else '不是')
            buy_df=df[df['buy']=='是']
            print('买入股票***************************')
            print(buy_df)
            buy_df.to_excel(r'{}\买入股票\买入股票.xlsx'.format(self.path))
            sell_df=df[df['sell']=='是']
            print('卖出股票*****************')
            print(sell_df)
            sell_df.to_excel(r'{}\卖出股票\卖出股票.xlsx'.format(self.path))
        else:
            print('没有交易数据*****************************')
            buy_df=pd.DataFrame()
            buy_df.to_excel(r'{}\买入股票\买入股票.xlsx'.format(self.path))
            sell_df=pd.DataFrame()
            sell_df.to_excel(r'{}\卖出股票\卖出股票.xlsx'.format(self.path))

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
    def get_deal_hold_stock_limit(self):
        '''
        处理持股限制
        '''
        with open(r'{}\通达信预警系统.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        hold_limt=text['持股限制']
        hold_stock=pd.read_excel(r'持股数据\持股数据.xlsx')
        buy_df=pd.read_excel(r'{}\买入股票\买入股票.xlsx'.format(self.path))
        sell_df=pd.read_excel(r'{}\卖出股票\卖出股票.xlsx'.format(self.path))
        if hold_stock.shape[0]>0:
            hold_stock['证券代码']=hold_stock['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
            hold_amount=hold_stock.shape[0]
            hold_stock_list=hold_stock['证券代码'].tolist()
        else:
            hold_amount=0
            hold_stock_list=[]
        #卖出
        if sell_df.shape[0]>0:
            sell_df['卖出标记']=sell_df['证券代码'].apply(lambda x: '是' if x in hold_stock_list else '不是')
            sell_df=sell_df[sell_df['卖出标记']=='是']
            sell_df.to_excel(r'{}\卖出股票\卖出股票.xlsx'.format(self.path))
            sell_amount=sell_df.shape[0]
        else:
            sell_df=pd.DataFrame()
            sell_df.to_excel(r'{}\卖出股票\卖出股票.xlsx'.format(self.path))
            sell_amount=0
        #买入
        if buy_df.shape[0]>0:
            av_amount=hold_limt+sell_amount-hold_amount
            if av_amount>=hold_limt:
                av_amount=hold_limt
            else:
                if av_amount>0:
                    av_amount=av_amount
                else:
                    av_amount=0
            print('可以买入的数量**************************{}'.format(av_amount))
            buy_df=buy_df[:av_amount]
            buy_df.to_excel(r'{}\买入股票\买入股票.xlsx'.format(self.path))
        else:
            buy_df=pd.DataFrame()
            buy_df.to_excel(r'{}\买入股票\买入股票.xlsx'.format(self.path))
    def trader_data(self):
        '''
        开始下单
        '''
        with open(r'{}\通达信预警系统.json'.format(self.path),encoding='utf-8') as f:
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
            for stock,condi in zip(sell_df['证券代码'].tolist(),sell_df['买卖条件'].tolist()):
                try:
                    price=self.data.get_spot_data(stock=stock)['最新价']
                    if trader_models=='数量':
                        #检查是否可以卖出
                        if self.trader.check_stock_is_av_sell(stock=stock,amount=fix_amount):
                            self.trader.sell(security=stock,price=price,amount=fix_amount)
                            print('交易模式{}卖出条件{} 卖出 股票{} 数量{} 价格{}'.format(trader_models,condi,stock,fix_amount,price))
                        else:
                            print('交易模式{}卖出条件{} {} 不能卖出'.format(trader_models,condi,stock))
                    elif trader_models=='金额':
                        trader_type,amount,price=self.trader.order_value(stock=stock,value=fix_cash,price=price,trader_type='sell')
                        if trader_type=='sell' and amount>=10:
                            self.trader.sell(security=stock,price=price,amount=amount)
                            print('交易模式{}卖出条件{} 卖出 股票{} 数量{} 价格{}'.format(trader_models,condi,stock,amount,price))
                        else:
                            print('交易模式{}卖出条件{} {} 不能卖出'.format(trader_models,condi,stock))
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
            for stock,condi in zip(buy_df['证券代码'].tolist(),buy_df['买卖条件'].tolist()):
                try:
                    price=self.data.get_spot_data(stock=stock)['最新价']
                    if trader_models=='数量':
                        print(fix_amount,'******************')
                        #检查是否可以买入
                        if self.trader.check_stock_is_av_buy(stock=stock,amount=fix_amount,price=price):
                            self.trader.buy(security=stock,price=price,amount=fix_amount)
                            print('交易模式{}买入条件{} 买入 股票{} 数量{} 价格{}'.format(trader_models,condi,stock,fix_amount,price))
                        else:
                            print('交易模式{}买入条件{} {} 不能买入'.format(trader_models,condi,stock))
                    elif trader_models=='金额':
                        trader_type,amount,price=self.trader.order_value(stock=stock,value=fix_cash,price=price,trader_type='buy')
                        if trader_type=='buy' and amount>=10:
                            self.trader.buy(security=stock,price=price,amount=amount)
                            print('交易模式{}买入条件{} 买入 股票{} 数量{} 价格{}'.format(trader_models,condi,stock,amount,price))
                        else:
                            print('交易模式{}买入条件{} {} 不能买入'.format(trader_models,condi,stock))
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
        with open(r'{}\通达信预警系统.json'.format(self.path),encoding='utf-8') as f:
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
        更新策略数据
        '''
        print(self.save_position())
        print(self.save_balance())
        self.params_tdx_text()
        self.get_dea_buy_sell_data()
        self.run_user_def_models()
        self.analysis_trader_log()
        self.get_params_taredr_stock()
        self.get_del_not_trader_stock()
        self.get_deal_hold_stock_limit()
        self.trader_data()
        self.delete_folder_contents()

        