from trader_tool.unification_data import unification_data
from trader_tool.trader_frame import trader_frame
from trader_tool.analysis_models import analysis_models
from trader_tool.shape_analysis import shape_analysis
from user_def_models import user_def_models
import pandas as pd
from tqdm import tqdm
import numpy as np
import time
import json
from datetime import datetime
import schedule
import yagmail
from trader_tool.base_func import base_func
from trader_tool.decode_trader_password import decode_trader_password
class trader_strategy:
    def __init__(self,trader_tool='ths',exe='C:/同花顺软件/同花顺/xiadan.exe',tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qq='1029762153@qq.com',open_set='否',qmt_path='D:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55009640',qmt_account_type='STOCK',slippage=0.01):
        '''
        参数配置
        '''
        self.exe=exe
        self.tesseract_cmd=tesseract_cmd
        self.qq=qq
        self.trader_tool=trader_tool
        self.open_set=open_set
        self.qmt_path=qmt_path
        self.qmt_account=qmt_account
        self.qmt_account_type=qmt_account_type
        self.slippage=slippage
        self.user_def_models=user_def_models(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type)
        order_frame=trader_frame(trader_tool=self.trader_tool,exe=self.exe,tesseract_cmd=self.tesseract_cmd,
                                 open_set=self.open_set,qmt_path=self.qmt_path,qmt_account=self.qmt_account,
                                 qmt_account_type=self.qmt_account_type,slippage=self.slippage)
        self.trader=order_frame.get_trader_frame()
        data=unification_data(trader_tool=self.trader_tool)
        self.data=data.get_unification_data()
        self.analysis_models=analysis_models()
        self.shape_analysis=shape_analysis()
        self.base_func=base_func()
        self.password=decode_trader_password()
    def connact(self):
        '''
        链接同花顺
        '''
        try:
            self.trader.connect()
            return True
        except Exception as e:
            print("运行错误:",e)
            print('{}连接失败'.format(self.trader_tool))
            return False
    def adjust_hold_data(self,stock='603918',trader_type='sell',price=12,amount=100):
        '''
        模拟持股数据
        '''
        price=float(price)
        amount=float(amount)
        df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        del df['Unnamed: 0']
        df.index=df['证券代码']
        df1=df[df['证券代码']==stock]
        if df1.shape[0]>0:
            #可用余额
            available_balance=df1['可用余额'].tolist()[-1]
            #股票余额
            stock_balance=df1['股票余额'].tolist()[-1]
            if trader_type=='buy':
                stock_balance+=float(amount)
                available_balance+=float(amount)
            elif trader_type=='sell':
                available_balance-=float(amount)
                stock_balance-=float(amount)
                if available_balance<=0:
                    available_balance=0
                if stock_balance<=0:
                    stock_balance=0
            else:
                pass
            df1['可用余额']=[available_balance]
            df1['股票余额']=[stock_balance]
            data=df.drop(stock,axis=0)
            data=pd.concat([data,df1],ignore_index=True)
            data.to_excel(r'持股数据\持股数据.xlsx')
            print('持股数据调整成功')
        else:
            df2=pd.DataFrame()
            df2['明细']=['0']
            df2['证券代码']=[stock]
            df2['证券名称']=['0']
            df2['股票余额']=[amount]
            df2['可用余额']=[amount]
            df2['冻结数量']=[0]
            df2['成本价']=[price]
            df2['市价']=[price]
            df2['盈亏']=[0]
            df2['盈亏比(%)']=[0]
            df2['市值']=[amount*price]
            df2['当日买入']=[0]
            df2['当日卖出']=[0]
            df2['交易市场']=[0]
            df2['持股天数']=[0]
            data=pd.concat([df,df2],ignore_index=True)
            data.to_excel(r'持股数据\持股数据.xlsx')
            print('持股数据调整成功')													
            print('{}没有持股'.format(stock))
    def adjust_account_cash(self,stock='128036',trader_type='buy',price=123,amount=10):
        '''
        调整账户资金
        '''
        price=float(price)
        amount=float(amount)
        df=pd.read_excel(r'账户数据\账户数据.xlsx',dtype='object')
        try:
            del df['Unnamed: 0']
        except Exception as e:
            print("运行错误:",e)
        value=price*amount
        #可用余额
        av_user_cash=float(df['可用金额'].tolist()[-1])
        if trader_type=='buy':
            av_user_cash-=value
        elif trader_type=='sell':
            av_user_cash+=value
        else:
            av_user_cash=av_user_cash
        df['可用金额']=[av_user_cash]
        df.to_excel(r'账户数据\账户数据.xlsx')
        print('账户资金调整完成')
        return df
    def check_cov_bond_av_trader(self,stock='128106'):
        '''
        检查可转债是否可以交易
        '''
        with open(r'分析配置.json',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        del_stock=text['黑名单']
        if stock in del_stock:
            print('{}黑名单'.format(stock))
            return False
        else:
            return True
    def check_stock_is_av_buy(self,stock='128036',price='156.700',amount=10):
        '''
        检查是否可以买入
        '''
        price=float(price)
        amount=float(amount)
        with open(r'分析配置.json',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        hold_limit=text['持股限制']
        stats=self.trader.check_stock_is_av_buy(stock=stock,price=price,amount=amount,hold_limit=hold_limit)
        return stats
    def check_stock_is_av_sell(self,stock='128036',amount=10):
        '''
        检查是否可以卖出
        '''
        stats=self.trader.check_stock_is_av_sell(stock=stock,amount=amount)
        return stats
    def check_av_target_tarder(self,stock='600031',price=2.475,trader_type='buy'):
        '''
        检查目标交易
        '''
        with open('分析配置.json','r+',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        data_type=text['交易模式']
        value=text['固定交易资金']
        limit_value=text['持有金额限制']
        amount1=text['固定交易数量']
        limit_amount=text['持股限制']
        special_stock=text['特殊标的']
        special_value=text['特殊固定交易资金']
        special_limit_value=text['特殊持有金额限制']
        trader_stock=self.trader.select_data_type(stock)
        if trader_stock=='stock':
            amount1=amount1*10
            limit_amount=limit_amount*10
        elif trader_stock=='fund':
            amount1=amount1*100
            limit_amount=limit_amount*100
        else:
            amount1=amount1
            limit_amount=limit_amount
        if str(stock)[:6] in special_stock:
            value=special_value
            limit_value=special_limit_value
        else:
            value=value
            limit_value=limit_value
        trader_type_1,buy_sell_amount,price=self.trader.check_av_target_trader(data_type=data_type,trader_type=trader_type,
                                           amount=amount1,limit_volume=limit_amount,
                value=value,limit_value=limit_value,stock=stock,price=price)
        return trader_type_1,buy_sell_amount,price
    def seed_dingding(self,msg='买卖交易成功,',access_token_list=['ab5d0a609429a786b9a849cefd5db60c0ef2f17f2ec877a60bea5f8480d86b1b']):
        import requests
        import json
        import random
        access_token=random.choice(access_token_list)
        url='https://oapi.dingtalk.com/robot/send?access_token={}'.format(access_token)
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        data = {
            "msgtype": "text",  # 发送消息类型为文本
            "at": {
                #"atMobiles": reminders,
                "isAtAll": False,  # 不@所有人
            },
            "text": {
                "content": msg,  # 消息正文
            }
        }
        r = requests.post(url, data=json.dumps(data), headers=headers)
        text=r.json()
        errmsg=text['errmsg']
        if errmsg=='ok':
                print('钉钉发生成功')
                return text
        else:
            print(text)
            return text
    '''
    def seed_emial_qq(self,text='交易完成'):

        with open('分析配置.json','r+',encoding='utf-8') as f:
            com=f.read()
        text1=json.loads(com)
        try:
            password=text1['qq掩码']
            seed_qq=text1['发送qq']
            yag = yagmail.SMTP(user='{}'.format(seed_qq), password=password, host='smtp.qq.com')
            m = text1['接收qq']
            text = text
            yag.send(to=m, contents=text, subject='邮件')
            print('邮箱发生成功')
        except Exception as e:
            print("运行错误:",e)
            print('qq发送失败可能用的人多')
    '''
    def check_is_trader_date(self):
        '''
        检测是不是交易时间
        '''
        loc=time.localtime()
        tm_hour=loc.tm_hour
        tm_min=loc.tm_min
        #利用通用时间，不考虑中午不交易
        is_trader=''
        wo=loc.tm_wday
        with open('分析配置.json','r+',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        trader_time=text['交易时间段']
        start_date=text['交易开始时间']
        end_date=text['交易结束时间']
        if wo<=trader_time:
            if (tm_hour>=start_date) and (tm_hour<=end_date):
                is_trader=True
                return True
            else:
                is_trader=False
                return False
        else:
            print('周末')
            return False
    def check_is_trader_date_1(self):
        '''
        检测是不是交易时间
        '''
        with open('分析配置.json','r+',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        password=text['软件授权码']
        trader_time=text['交易时间段']
        start_date=text['交易开始时间']
        end_date=text['交易结束时间']
        start_mi=text['开始交易分钟']
        jhjj=text['是否参加集合竞价']
        stats=self.password.decode_trader_password()
        if stats==True:
            if jhjj=='是':
                jhjj_time=15
            else:
                jhjj_time=30
            loc=time.localtime()
            tm_hour=loc.tm_hour
            tm_min=loc.tm_min
            wo=loc.tm_wday
            if wo<=trader_time:
                if tm_hour>=start_date and tm_hour<=end_date:
                    if tm_hour==9 and tm_min<jhjj_time:
                        return False
                    elif tm_min>=start_mi:
                        return True
                    else:
                        return False
                else:
                    return False    
            else:
                print('周末')
                return False
        else:
            print('**************软件授权码不正确联系作者微信15117320079**************')
            return False
    def run_stock_trader_buy(self):
        '''
        运行交易策略 可转债,买入
        '''
        if self.check_is_trader_date_1()==True:
        #if True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            seed=text['发送通知']
            stop=text['停止程序']
            max_zdf=text['买入时间的涨跌幅上限']
            min_zdf=text['买入时间的涨跌幅下限']
            data_source=text['买卖数据源']
            name=text['策略名称']
            trader_stats=[]
            if stop=='真':
                print('程序停止')
            else:
                if data_source=='默认':
                    df=pd.read_excel(r'买入股票\买入股票.xlsx',dtype='object')
                    try:
                        del df['Unnamed: 0']
                    except Exception as e:
                        print("运行错误:",e)
                else:
                    df=pd.read_excel(r'自定义买入\自定义买入.xlsx',dtype='object')
                    try:
                        del df['Unnamed: 0']
                    except Exception as e:
                        print("运行错误:",e)
                if df.shape[0]>0:
                    for stock,stats in zip(df['证券代码'].tolist(),df['交易状态'].tolist()):
                        stock=str(stock)
                        if stats=='未买':
                            amount=text['固定交易数量']
                            #检查是不是强制赎回
                            try:

                                if self.check_cov_bond_av_trader(stock=stock):
                                    spot_data=self.data.get_spot_data(stock=stock) 
                                    #价格
                                    price=spot_data['最新价']
                                    lof_list=text['lof基金列表']
                                    stock=str(stock)
                                    if stock[:6] in lof_list:
                                        price=price/10
                                    else:
                                        price=price
                                    #实时涨跌幅
                                    zdf=spot_data['涨跌幅']
                                    #检查是不是可以买入
                                    if self.check_stock_is_av_buy(stock=stock,price=price,amount=amount):
                                        if zdf<=max_zdf and zdf>=min_zdf:
                                            trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='buy')
                                            if trader_type=='buy':
                                                self.trader.buy(security=stock,price=price,amount=amount)
                                                text1='买入 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                                text1='可转债,买入'+name+text1
                                                if seed=='真':
                                                    self.seed_emial_qq(text=text1)
                                                else:
                                                    pass
                                                #标记状态
                                                trader_stats.append('已买')
                                                #调整持股
                                                self.adjust_hold_data(stock=stock,trader_type='buy',price=price,amount=amount)
                                                #调整账户资金
                                                self.adjust_account_cash(stock=stock,trader_type='buy',price=price,amount=amount)
                                            else:
                                                trader_stats.append('未买')
                                        else:
                                            print('时间{} 代码{} 涨跌幅{}不在涨跌幅范围'.format(datetime.now(),stock,zdf))
                                            trader_stats.append('未买')
                                    else:
                                        trader_stats.append('未买')
                            
                            except Exception as e:
                                print("运行错误:",e)
                                print('循环买入{}有问题'.format(stock))
                                trader_stats.append('未买')
                            
                        else:
                            print('{}循环买入{}已经买入'.format(datetime.now(),stock))
                            trader_stats.append(stats)
                    df['交易状态']=trader_stats
                    if data_source=='默认':
                        df.to_excel(r'买入股票\买入股票.xlsx')
                    else:
                        df.to_excel(r'自定义买入\自定义买入.xlsx')  
                else:
                    print('买入可转债为空')

        else:
            print('{}目前不是交易时间'.format(datetime.now()))
    def run_user_def_stock_trader_buy(self):
        '''
        运行自定义买入
        '''
        if self.check_is_trader_date_1()==True:
        #if True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            seed=text['发送通知']
            stop=text['停止程序']
            max_zdf=text['自定义买入时间的涨跌幅上限']
            min_zdf=text['自定义买入时间的涨跌幅下限']
            data_source=text['买卖数据源']
            name=text['策略名称']
            trader_stats=[]
            if stop=='真':
                print('程序停止')
            else:
                df=pd.read_excel(r'自定义买入股票\自定义买入股票.xlsx',dtype='object')
                try:
                    del df['Unnamed: 0']
                except Exception as e:
                    print("运行错误:",e)
                if df.shape[0]>0:
                    for stock,name,auto_price,price,trader_type,amount,stats in zip(df['证券代码'],df['证券名称'],
                            df['自动价格'],df['价格'],df['交易类型'],df['数量'],df['交易状态']):
                        stock=str(stock)
                        if stats=='未买':
                            #检查是不是强制赎回
                            try:
                                if self.check_cov_bond_av_trader(stock=stock):
                                    if auto_price=='是':
                                        price=price
                                    else:
                                        spot_data=self.data.get_spot_data(stock=stock) 
                                        #价格
                                        price=spot_data['最新价']
                                    lof_list=text['lof基金列表']
                                    stock=str(stock)
                                    if stock[:6] in lof_list:
                                        price=price/10
                                    else:
                                        price=price
                                    #实时涨跌幅
                                    zdf=spot_data['涨跌幅']
                                    #检查是不是可以买入
                                    if self.check_stock_is_av_buy(stock=stock,price=price,amount=amount):
                                        if zdf<=max_zdf and zdf>=min_zdf:
                                            if trader_type=='数量':
                                                self.trader.buy(security=stock,price=price,amount=amount)
                                                text1='买入 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                                text1='可转债,买入'+name+text1
                                                if seed=='真':
                                                    self.seed_emial_qq(text=text1)
                                                else:
                                                    pass
                                                #标记状态
                                                trader_stats.append('已买')
                                                #调整持股
                                                self.adjust_hold_data(stock=stock,trader_type='buy',price=price,amount=amount)
                                                #调整账户资金
                                                self.adjust_account_cash(stock=stock,trader_type='buy',price=price,amount=amount)
                                            elif trader_type=='价值':
                                                trader,amount,price=self.trader.order_value(stock=stock,price=price,value=amount,trader_type='buy')
                                                if trader=='buy' and amount>0:
                                                    self.trader.buy(security=stock,price=price,amount=amount)
                                                    text1='买入 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                                    text1='可转债,买入'+name+text1
                                                    if seed=='真':
                                                        self.seed_emial_qq(text=text1)
                                                    else:
                                                        pass
                                                    #标记状态
                                                    trader_stats.append('已买')
                                                    #调整持股
                                                    self.adjust_hold_data(stock=stock,trader_type='buy',price=price,amount=amount)
                                                    #调整账户资金
                                                    self.adjust_account_cash(stock=stock,trader_type='buy',price=price,amount=amount)
                                                else:
                                                    trader_stats.append('已买')
                                            elif trader_type=='百分比':
                                                trader,amount,price=self.trader.order_percent(stock=stock,price=price,percent=amount,trader_type='buy')
                                                if trader=='buy' and amount>0:
                                                    self.trader.buy(security=stock,price=price,amount=amount)
                                                    text1='买入 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                                    text1='可转债,买入'+name+text1
                                                    if seed=='真':
                                                        self.seed_emial_qq(text=text1)
                                                    else:
                                                        pass
                                                    #标记状态
                                                    trader_stats.append('已买')
                                                    #调整持股
                                                    self.adjust_hold_data(stock=stock,trader_type='buy',price=price,amount=amount)
                                                    #调整账户资金
                                                    self.adjust_account_cash(stock=stock,trader_type='buy',price=price,amount=amount)
                                                else:
                                                    trader_stats.append('已买')
                                            else:
                                                trader_stats.append('未买')
                                        else:
                                            print('时间{} 代码{} 涨跌幅{}不在涨跌幅范围'.format(datetime.now(),stock,zdf))
                                            trader_stats.append('未买')
                                    else:
                                        trader_stats.append('未买')
                            except Exception as e:
                                print("运行错误:",e)
                                print('循环买入{}有问题'.format(stock))
                                trader_stats.append('未买')
                        else:
                            print('{}循环买入{}已经买入'.format(datetime.now(),stock))
                            trader_stats.append(stats)
                    df['交易状态']=trader_stats
                    if data_source=='默认':
                        df.to_excel(r'自定义买入股票\自定义买入股票.xlsx')
                    else:
                        df.to_excel(r'自定义买入股票\自定义买入股票.xlsx')  
                else:
                    print('买入可转债为空')
        else:
            print('{}目前不是交易时间'.format(datetime.now()))
    def run_stock_tail_platetrader_buy(self):
        '''
        运行交易策略 可转债,尾盘买入
        '''
        if self.check_is_trader_date_1()==True:
        #if True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            seed=text['发送通知']
            stop=text['停止程序']
            max_zdf=text['尾盘建仓涨跌幅上限']
            min_zdf=text['尾盘建仓涨跌幅下限']
            data_source=text['买卖数据源']
            hold_limit=text['持股限制']
            name=text['策略名称']
            trader_stats=[]
            if stop=='真':
                print('程序停止')
            else:
                if data_source=='默认':
                    df=pd.read_excel(r'买入股票\买入股票.xlsx',dtype='object')
                    try:
                        del df['Unnamed: 0']
                    except Exception as e:
                        print("运行错误:",e)
                else:
                    df=pd.read_excel(r'自定义买入\自定义买入.xlsx',dtype='object')
                    try:
                        del df['Unnamed: 0']
                    except Exception as e:
                        print("运行错误:",e)
                if df.shape[0]>0:
                    for stock,stats in zip(df['证券代码'].tolist(),df['交易状态'].tolist()):
                        stock=str(stock)
                        if stats=='未买':
                            amount=text['固定交易数量']
                            #检查是不是强制赎回
                            try:
                                if self.check_cov_bond_av_trader(stock=stock):
                                    spot_data=self.data.get_spot_data(stock=stock)
                                    #价格
                                    price=spot_data['最新价']
                                    lof_list=text['lof基金列表']
                                    stock=str(stock)
                                    if stock[:6] in lof_list:
                                        price=price/10
                                    else:
                                        price=price
                                    #实时涨跌幅
                                    zdf=spot_data['涨跌幅']
                                    #检查是不是可以买入
                                    if self.check_stock_is_av_buy(stock=stock,price=price,amount=amount):
                                        if zdf<=max_zdf and zdf>=min_zdf:
                                            trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price)
                                            if trader_type=='buy':
                                                self.trader.buy(security=stock,price=price,amount=amount)
                                                text1='买入 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                                text1='可转债,买入'+name+text1
                                                print(text1)
                                                if seed=='真':
                                                    self.seed_emial_qq(text=text1)
                                                else:
                                                    pass
                                                #标记状态
                                                hold_num=df[df['证券代码']==stock]
                                                if hold_num.shape[0]>0:
                                                    hold_num=hold_num['可用余额'].tolist()[-1]
                                                    if hold_num<hold_limit:
                                                        trader_stats.append('已买')
                                                    else:
                                                        trader_stats.append('到达持股限制')
                                                    #调整持股
                                                    self.adjust_hold_data(stock=stock,trader_type='buy',price=price,amount=amount)
                                                    #调整账户资金
                                                    self.adjust_account_cash(stock=stock,trader_type='buy',price=price,amount=amount)
                                            else:
                                                trader_stats.append('已买')
                                        else:
                                            print('时间{} 代码{} 涨跌幅{}不在涨跌幅范围'.format(datetime.now(),stock,zdf))
                                            trader_stats.append('未买')
                                    else:
                                        trader_stats.append('未买')
                            except Exception as e:
                                print("运行错误:",e)
                                print('可转债,尾盘买入{}有问题'.format(stock))
                                trader_stats.append('未买')
                        else:
                            print('{}循环卖出{}已经卖出'.format(datetime.now(),stock))
                            trader_stats.append(stats)
                    df['交易状态']=trader_stats
                    if data_source=='默认':
                        df.to_excel(r'买入股票\买入股票.xlsx')
                    else:
                        df.to_excel(r'自定义买入\自定义买入.xlsx')  
                else:
                    print('买入可转债为空')
        else:
            print('{}目前不是交易时间'.format(datetime.now()))
    def run_stock_trader_sell(self):
        '''
        运行交易策略 股票,策略卖出
        '''
        if self.check_is_trader_date_1()==True:
        #if True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            seed=text['发送通知']
            stop=text['停止程序']
            data_source=text['买卖数据源']
            name=text['策略名称']
            stats_list=[]
            if stop=='真':
                print('程序停止')
            else:
                if data_source=='默认':
                    df=pd.read_excel(r'卖出股票\卖出股票.xlsx',dtype='object')
                else:
                    df=pd.read_excel(r'自定义卖出\自定义卖出.xlsx',dtype='object')
                try:
                    del df['Unnamed: 0']
                except Exception as e:
                    print("运行错误:",e)
                if df.shape[0]>0:
                    for stock,stats in zip(df['证券代码'].tolist(),df['交易状态'].tolist()):
                        stock=str(stock)
                        if stats=='未卖':
                            amount=text['固定交易数量']
                            #检查是否可以卖出
                            try:
                                if self.check_stock_is_av_sell(stock=stock,amount=amount):
                                    #获取实时数据
                                    spot_data=self.data.get_spot_data(stock=stock)
                                    #价格
                                    price=spot_data['最新价']
                                    lof_list=text['lof基金列表']
                                    stock=str(stock)
                                    if stock[:6] in lof_list:
                                        price=price/10
                                    else:
                                        price=price
                                    stock=str(stock)
                                    trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='sell')
                                    if trader_type=='sell':
                                        self.trader.sell(security=stock,price=price,amount=amount)
                                        text1='策略卖出 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                        text1=name+text1
                                        print(text1)
                                        if seed=='真':
                                            self.seed_emial_qq(text=text1)
                                        else:
                                            pass
                                        #标记状态
                                        hold_data=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
                                        hold_data['证券代码']=hold_data['证券代码'].astype(str)
                                        stock=str(stock)
                                        try:
                                            del hold_data['Unnamed: 0']
                                        except Exception as e:
                                            print("运行错误:",e)
                                        hold_num=hold_data[hold_data['证券代码']==stock]
                                        if hold_num.shape[0]>0:
                                            hold_num=hold_num['可用余额'].tolist()[-1]
                                            if hold_num>=10:
                                                stats_list.append('未卖')
                                            else:
                                                stats_list.append('已卖')
                                            #调整持股
                                            self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                            #调整账户资金
                                            self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                                    else:
                                        stats_list.append('未卖')
                                else:
                                    stats_list.append('未卖')
                        
                            except Exception as e:
                                print("运行错误:",e)
                                print('循环卖出{}有问题'.format(stock))
                                stats_list.append('未卖')
                        else:
                            print("不是卖出状态")
                            stats_list.append(stats)
                    df['交易状态']=stats_list
                    if data_source=='默认':
                        df.to_excel(r'卖出股票\卖出股票.xlsx')
                    else:
                        df.to_excel(r'自定义卖出\自定义卖出.xlsx')  
                else:
                    print('没有卖出的可转债')
        else:
            print('{}目前不是交易时间'.format(datetime.now()))
    def run_user_def_stock_trader_sell(self):
        '''
        运行交易策略 自定义策略卖出
        '''
        if self.check_is_trader_date_1()==True:
        #if True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            seed=text['发送通知']
            stop=text['停止程序']
            data_source=text['买卖数据源']
            name=text['策略名称']
            stats_list=[]
            if stop=='真':
                print('程序停止')
            else:
                df=pd.read_excel(r'自定义卖出股票\自定义卖出股票.xlsx',dtype='object')
                try:
                    del df['Unnamed: 0']
                except Exception as e:
                    print("运行错误:",e)
                if df.shape[0]>0:
                    for stock,name,auto_price,price,trader_type,amount,stats in zip(df['证券代码'],df['证券名称'],
                            df['自动价格'],df['价格'],df['交易类型'],df['数量'],df['交易状态']):
                        if stats=='未卖':
                            #检查是否可以卖出
                            try:
                                if self.check_stock_is_av_sell(stock=stock,amount=amount):
                                    #获取实时数据
                                    if auto_price=='是':
                                        spot_data=self.data.get_spot_data(stock=stock)
                                        #价格
                                        price=spot_data['最新价']
                                    else:
                                        price=price
                                    lof_list=text['lof基金列表']
                                    stock=str(stock)
                                    if stock[:6] in lof_list:
                                        price=price/10
                                    else:
                                        price=price
                                    stock=str(stock)
                                    if trader_type=='数量':
                                        self.trader.sell(security=stock,price=price,amount=amount)
                                        text1='卖出 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                        text1='可转债,卖出'+name+text1
                                        if seed=='真':
                                            self.seed_emial_qq(text=text1)
                                        else:
                                            pass
                                        #标记状态
                                        stats_list.append('已卖')
                                        #调整持股
                                        self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                        #调整账户资金
                                        self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                                    elif trader_type=='价值':
                                        trader,amount,price=self.trader.order_value(stock=stock,price=price,value=amount,trader_type='sell')
                                        if trader=='sell' and amount>0:
                                            self.trader.sell(security=stock,price=price,amount=amount)
                                            text1='卖出 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                            text1='可转债,卖出'+name+text1
                                            if seed=='真':
                                                self.seed_emial_qq(text=text1)
                                            else:
                                                pass
                                                #标记状态
                                            stats_list.append('已卖')
                                            #调整持股
                                            self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                            #调整账户资金
                                            self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                                    elif trader_type=='百分比':
                                        trader,amount,price=self.trader.order_percent(stock=stock,price=price,percent=amount,trader_type='sell')
                                        if trader=='sell' and amount>0:
                                            self.trader.sell(security=stock,price=price,amount=amount)
                                            text1='卖出 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                            text1='可转债,卖出'+name+text1
                                            if seed=='真':
                                                self.seed_emial_qq(text=text1)
                                            else:
                                                pass
                                            #标记状态
                                            stats_list.append('已卖')
                                            #调整持股
                                            self.adjust_hold_data(stock=stock,trader_type='buy',price=price,amount=amount)
                                            #调整账户资金
                                            self.adjust_account_cash(stock=stock,trader_type='buy',price=price,amount=amount)
                                    else:
                                        stats_list.append('已买')
                                else:
                                    stats_list.append('未卖')
                        
                            except Exception as e:
                                print("运行错误:",e)
                                print('循环卖出{}有问题'.format(stock))
                                stats_list.append('未卖')
                        else:
                            print("不是卖出状态")
                            stats_list.append(stats)
                    df['交易状态']=stats_list
                    df.to_excel(r'自定义卖出股票\自定义卖出股票.xlsx')
                else:
                    print('没有卖出的可转债')
        else:
            print('{}目前不是交易时间'.format(datetime.now()))
    def run_sell_below_the_moving_average_in_real_time(self):
        '''
        跌破均线实时卖出
        '''
        if self.check_is_trader_date_1()==True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            seed=text['发送通知']
            stop=text['停止程序']
            name=text['策略名称']
            mean_line=text['跌破均线']
            is_sell_all=text['跌破均线是否一次性卖出']
            fix_amount=text['跌破均线固定交易数量']
            if stop=='真':
                print('程序停止')
            else:
                df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
                try:
                    del df['Unnamed: 0']
                except Exception as e:
                    print("运行错误:",e)
                if df.shape[0]>0:
                    df['证券代码']=df['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
                    stock_list=df['证券代码'].tolist()
                    for stock in stock_list:
                        try:
                            hist=self.data.get_hist_data_em(stock=stock)
                            down_mean=self.analysis_models.sell_below_the_moving_average_in_real_time(df=hist,mean_line=mean_line)
                            if down_mean==True:
                                if is_sell_all=='是':
                                    hold_num=df[df['证券代码']==stock]
                                    amount=hold_num['可用余额'].tolist()[-1]
                                else:
                                    amount=fix_amount
                                if self.check_stock_is_av_sell(stock=stock,amount=amount):
                                    #获取实时数据
                                    spot_data=self.data.get_spot_data(stock=stock)
                                    #价格
                                    price=spot_data['最新价']
                                    lof_list=text['lof基金列表']
                                    stock=str(stock)
                                    if stock[:6] in lof_list:
                                        price=price/10
                                    else:
                                        price=price
                                    stock=str(stock)
                                    self.trader.sell(security=stock,price=price,amount=amount)
                                    text1='跌破均线实时卖出 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                    text1=name+text1
                                    print(text1)
                                    if seed=='真':
                                        self.seed_emial_qq(text=text1)
                                    else:
                                        pass
                                    #调整持股
                                    self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                    #调整账户资金
                                    self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                                else:
                                    text1='跌破均线实时卖出 不可以卖出 时间{} 代码 '.format(datetime.now(),stock)
                                    print(text1)
                            else:
                                text1='跌破均线实时卖出 不可以卖出没有跌破均线 时间{} 代码 '.format(datetime.now(),stock)
                                print(text1)
                        except Exception as e:
                            print("运行错误:",e)
                            text1='跌破均线实时卖出 不可以卖出有问题 时间{} 代码 '.format(datetime.now(),stock)
                            print(text1)
                else:
                    text1='跌破均线实时卖出 不可以卖出没有持股 时间{}'.format(datetime.now())
                    print(text1)
        else:
            text1='跌破均线实时卖出 不是交易时间 时间{}'.format(datetime.now())
            print(text1)

    def run_stock_trader_sell_1(self):
        '''
        运行交易策略 股票,策略卖出,尾盘清仓
        '''
        if self.check_is_trader_date_1()==True:
        #if True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            seed=text['发送通知']
            stop=text['停止程序']
            data_source=text['买卖数据源']
            name=text['策略名称']
            if stop=='真':
                print('程序停止')
            else:
                if data_source=='默认':
                    df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
                else:
                    df=pd.read_excel(r'自定义卖出\自定义卖出.xlsx',dtype='object')
                try:
                    del df['Unnamed: 0']
                except Exception as e:
                    print("运行错误:",e)
                if df.shape[0]>0:
                    for stock in df['证券代码'].tolist():
                        if True:
                            df=df[df['证券代码']==stock]
                            try:
                                if df.shape[0].shape>0:
                                    amount=df['可用余额'].tolist()[-1]
                                    #检查是否可以卖出
                                    if self.check_stock_is_av_sell(stock=stock,amount=amount):
                                        #获取实时数据
                                        spot_data=self.data.get_spot_data(stock=stock)
                                        #价格
                                        price=spot_data['最新价']
                                        lof_list=text['lof基金列表']
                                        stock=str(stock)
                                        if stock[:6] in lof_list:
                                            price=price
                                        else:
                                            price=price
                                        stock=str(stock)
                                        self.trader.sell(security=stock,price=price,amount=amount)
                                        text1='策略卖出 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                        text1=name+text1
                                        print(text1)
                                        if seed=='真':
                                            self.seed_emial_qq(text=text1)
                                        else:
                                            pass
                                        #调整持股
                                        self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                        #调整账户资金
                                        self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                            except Exception as e:
                                print("运行错误:",e)
                                print('策略卖出,尾盘清仓{}有问题'.format(stock))
                        else:
                            print("不是卖出状态")
                else:
                    print('没有卖出的可转债')
        else:
            print('{}目前不是交易时间'.format(datetime.now()))
    def get_sell_not_in_analaysis_models_in_close(self):
        '''
        卖出不在分析模型的可转债
        '''
        if self.check_is_trader_date_1()==True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            #amount=text['固定交易数量']
            seed=text['发送通知']
            stop=text['停止程序']
            stop_profit=text['当日止盈']
            stop_loss=text['当日止损']
            sell_all=text['一次性卖出']
            name=text['策略名称']
            df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
            try:
                del df['Unnamed: 0']
            except Exception as e:
                print("运行错误:",e)
            if df.shape[0]>0:
                stock_list=df['证券代码'].tolist()
                for stock in stock_list:
                    try:
                        hold_num=df[df['证券代码']==stock]['可用余额'].tolist()[-1]
                        if sell_all=='是':
                            amount=hold_num
                        else:
                            amount=text['固定交易数量']
                        if self.trader_tool=='ths':
                            hist_df=self.data.get_hist_data_em(stock=stock)
                            shape=shape_analysis(df=hist_df)
                        else:
                            hist_df=self.data.get_hist_data_em(stock=stock)
                            shape=shape_analysis(df=hist_df)
                        if shape.get_down_mean_line_sell()=='是' or shape.get_over_lining_sell()=='是' or shape.get_del_qzsh_cov_bond()=='是':
                            #获取实时数据
                            spot_data=self.data.get_spot_data(stock=stock)
                            #价格
                            price=spot_data['最新价']
                            lof_list=text['lof基金列表']
                            stock=str(stock)
                            if stock[:6] in lof_list:
                                price=price
                            else:
                                price=price
                            stock=str(stock)
                            self.trader.sell(security=stock,price=price,amount=amount)
                            text1='尾盘卖出不符合 策略卖出 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                            text1=name+text1
                            print(text1)
                            if seed=='真':
                                self.seed_emial_qq(text=text1)
                            else:
                                pass
                            #调整持股
                            self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                            #调整账户资金
                            self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                    except Exception as e:
                        print("运行错误:",e)
                        print('形态卖出有问题{}'.format(stock))
            else:
                print('没有持股')
        else:
            print('尾盘卖出不符合',datetime.now(),'不是交易时间')
    def daily_dynamic_stop_profit_stop_loss(self):
        '''
        当日止盈止损
        '''
        if self.check_is_trader_date_1()==True:
        #if True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            #amount=text['固定交易数量']
            seed=text['发送通知']
            stop=text['停止程序']
            stop_profit=text['当日止盈']
            stop_loss=text['当日止损']
            sell_all=text['一次性卖出']
            name=text['策略名称']
            if stop=='真':
                print('程序停止')
            else:
                df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
                try:
                    del df['Unnamed: 0']
                except Exception as e:
                    print("运行错误:",e)
                if df.shape[0]>0:
                    stock_list=df['证券代码'].tolist()
                    for stock in stock_list:
                        #检查是否可以交易
                        try:
                            if self.check_cov_bond_av_trader(stock=stock):
                                #持有数量
                                hold_num=df[df['证券代码']==stock]['可用余额'].tolist()[-1]
                                if sell_all=='是':
                                    amount=hold_num
                                else:
                                    amount=text['固定交易数量']
                                #检查是否可以卖出
                                if self.check_stock_is_av_sell(stock=stock,amount=amount):
                                    spot_data=self.data.get_spot_data(stock=stock)
                                    cost_price=df[df['证券代码']==stock]['成本价'].tolist()[-1]
                                    #价格
                                    price=spot_data['最新价']
                                    lof_list=text['lof基金列表']
                                    stock=str(stock)
                                    if stock[:6] in lof_list:
                                        price=price/10
                                    else:
                                        price=price
                                    #实时涨跌幅
                                    zdf=((price-cost_price)/cost_price)*100
                                    if zdf>=stop_profit:
                                        stock=str(stock)
                                        trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='sell')
                                        if trader_type=='sell':
                                            self.trader.sell(security=stock,price=price,amount=amount)
                                            text1='当日止盈卖出 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                            text1=name+text1
                                            print(text1)
                                            if seed=='真':
                                                self.seed_emial_qq(text=text1)
                                            else:
                                                pass
                                            #调整持股
                                            self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                            #调整账户资金
                                            self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                                    elif zdf<=stop_loss:
                                        stock=str(stock)
                                        trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='sell')
                                        if trader_type=='sell':
                                            self.trader.sell(security=stock,price=price,amount=amount)
                                            text1='当日止损卖出 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                            text1=name+text1
                                            print(text1)
                                            if seed=='真':
                                                self.seed_emial_qq(text=text1)
                                            else:
                                                pass
                                            #调整持股
                                            self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                            #调整账户资金
                                            self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                                    else:
                                        print('{} {}不符合当日止盈止损条件'.format(stock,datetime.now()))
                                else:
                                    print('{} {}当日止盈不可以卖出'.format(stock,datetime.now()))
                            else:
                                print('{}当日止盈不可以交易'.format(datetime.now()))
                        except Exception as e:
                            print("运行错误:",e)
                            print('{}当日止盈有问题'.format(stock))
                else:
                    print('{}当日止盈没有持股'.format(datetime.now()))
        else:
            print('{}当日止盈不是交易时间'.format(datetime.now()))
    def dynamic_stop_profit_stop_loss(self):
        '''
        动态/账户止盈止损
        '''
        if self.check_is_trader_date_1()==True:
        #if True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            #amount=text['固定交易数量']
            seed=text['发送通知']
            stop=text['停止程序']
            stop_profit=text['账户止盈']
            stop_loss=text['账户止损']
            sell_all=text['一次性卖出']
            name=text['策略名称']
            if stop=='真':
                print('程序停止')
            else:
                df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
                try:
                    del df['Unnamed: 0']
                except Exception as e:
                    print("运行错误:",e)
                if df.shape[0]>0:
                    stock_list=df['证券代码'].tolist()
                    for stock in stock_list:
                        #检查是否可以交易
                        try:
                            if self.check_cov_bond_av_trader(stock=stock):
                                #持有数量
                                hold_num=df[df['证券代码']==stock]['可用余额'].tolist()[-1]
                                cost_price=df[df['证券代码']==stock]['成本价'].tolist()[-1]
                                if sell_all=='是':
                                    amount=hold_num
                                else:
                                    amount=text['固定交易数量']
                                #检查是否可以卖出
                                if self.check_stock_is_av_sell(stock=stock,amount=amount):
                                    spot_data=self.data.get_spot_data(stock=stock)
                                    #价格
                                    price=spot_data['最新价']
                                    lof_list=text['lof基金列表']
                                    stock=str(stock)
                                    if stock[:6] in lof_list:
                                        price=price/10
                                    else:
                                        price=price
                                    #实时涨跌幅
                                    zdf=((price-cost_price)/cost_price)*100
                                    if zdf>=stop_profit:
                                        stock=str(stock)
                                        trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='sell')
                                        if trader_type=='sell':
                                            self.trader.sell(security=stock,price=price,amount=amount)
                                            text1='账户止盈卖出 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                            text1=name+text1
                                            print(text1)
                                            if seed=='真':
                                                self.seed_emial_qq(text=text1)
                                            else:
                                                pass
                                            #调整持股
                                            self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                            #调整账户资金
                                            self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                                    elif zdf<=stop_loss:
                                        stock=str(stock)
                                        trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='sell')
                                        if trader_type=='sell':
                                            self.trader.sell(security=stock,price=price,amount=amount)
                                            text1='账户止损卖出 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                            text1=name+text1
                                            print(text1)
                                            if seed=='真':
                                                self.seed_emial_qq(text=text1)
                                            else:
                                                pass
                                            #调整持股
                                            self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                            #调整账户资金
                                            self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                                    else:
                                        print('{} {}不符合账户止盈止损条件'.format(stock,datetime.now()))
                                else:
                                    print('{} {}账户止盈不可以卖出'.format(stock,datetime.now()))
                            else:
                                print('{}账户止盈不可以交易'.format(datetime.now()))
                        except Exception as e:
                            print("运行错误:",e)
                            print('{}账户止盈有问题'.format(stock))
                else:
                    print('{}账户止盈没有持股'.format(datetime.now()))
        else:
            print('{}账户止盈止损不是交易时间'.format(datetime.now()))
    def save_gains_and_stop_losses(self):
        '''
        保存收益止盈止损
        '''
        if self.check_is_trader_date_1()==True:
        #if True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            #amount=text['固定交易数量']
            seed=text['发送通知']
            stop=text['停止程序']
            stop_profit=text['保存的最低收益']
            sell_all=text['一次性卖出']
            name=text['策略名称']
            if stop=='真':
                print('程序停止')
            else:
                df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
                try:
                    del df['Unnamed: 0']
                except Exception as e:
                    print("运行错误:",e)
                if df.shape[0]>0:
                    stock_list=df['证券代码'].tolist()
                    for stock in stock_list:
                        #检查是否可以交易
                        try:
                            if self.check_cov_bond_av_trader(stock=stock):
                                #持有数量
                                hold_num=df[df['证券代码']==stock]['可用余额'].tolist()[-1]
                                cost_price=df[df['证券代码']==stock]['成本价'].tolist()[-1]
                                if sell_all=='是':
                                    amount=hold_num
                                else:
                                    amount=text['固定交易数量']
                                #检查是否可以卖出
                                if self.check_stock_is_av_sell(stock=stock,amount=amount):
                                    spot_data=self.data.get_spot_data(stock=stock)
                                    #价格
                                    price=spot_data['最新价']
                                    lof_list=text['lof基金列表']
                                    stock=str(stock)
                                    if stock[:6] in lof_list:
                                        price=price/10
                                    else:
                                        price=price
                                    #实时涨跌幅
                                    zdf=((price-cost_price)/cost_price)*100
                                    if zdf<=stop_profit and zdf>=0.8:
                                        stock=str(stock)
                                        trader_type='sell'
                                        if trader_type=='sell':
                                            self.trader.sell(security=stock,price=price,amount=amount)
                                            text1='保存收益止盈止损 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                            text1=name+text1
                                            print(text1)
                                            if seed=='真':
                                                self.seed_emial_qq(text=text1)
                                            else:
                                                pass
                                            #调整持股
                                            self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                            #调整账户资金
                                            self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                                    else:
                                        print('{} {}不符合保存收益止盈止损'.format(stock,datetime.now()))
                                else:
                                    print('{} {}账户止盈保存收益止盈止损'.format(stock,datetime.now()))
                            else:
                                print('{}账户止盈不可以交易'.format(datetime.now()))
                        except Exception as e:
                            print("运行错误:",e)
                            print('{}保存收益止盈止损有问题'.format(stock))
                else:
                    print('{}保存收益止盈止损没有持股'.format(datetime.now()))
        else:
            print('{}保存收益止盈止损不是交易时间'.format(datetime.now()))
    def surge_and_fall_overfall_rebound_func(self):
        '''
        冲高回落---超跌反弹
        '''
        if self.check_is_trader_date_1()==True:
        #if True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            #amount=text['固定交易数量']
            seed=text['发送通知']
            min_return=text['冲高最低收益']
            max_down=text['从高回落幅度']
            max_df=text['超跌幅度']
            ft_return=text['超跌反弹收益']
            sell_all=text['一次性卖出']
            name=text['策略名称']
            df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
            try:
                del df['Unnamed: 0']
            except Exception as e:
                print("运行错误:",e)
            df['可用余额']=df['可用余额'].astype(float)
            #股票不能T0
            #df1=df[df['可用余额']>=10]
            df1=df
            if df1.shape[0]>0:
                stock_list=df1['证券代码'].tolist()
                for stock in stock_list:
                    #持有数量
                    try:
                        hold_num=df[df['证券代码']==stock]['可用余额'].tolist()[-1]
                        if sell_all=='是':
                            amount=hold_num
                        else:
                            amount=text['固定交易数量']
                        trader_type,select,text1=self.analysis_models.surge_and_fall_overfall_rebound(stock=stock,
                            min_return=min_return,max_down=max_down,max_df=max_df,ft_return=ft_return
                        )
                        #冲高回落卖出
                        if trader_type=='冲高回落' and select==True:
                            #检查是否可以卖出
                            if self.check_stock_is_av_sell(stock=stock,amount=amount):
                                #获取实时数据
                                spot_data=self.data.get_spot_data(stock=stock)
                                #价格
                                price=spot_data['最新价']
                                lof_list=text['lof基金列表']
                                stock=str(stock)
                                if stock[:6] in lof_list:
                                    price=price
                                else:
                                    price=price
                                stock=str(stock)
                                trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='sell')
                                if trader_type=='sell':
                                    self.trader.sell(security=stock,price=price,amount=amount)
                                    #text1='卖出 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                    text1=name+text1
                                    print(text1)
                                    if seed=='真':
                                        self.seed_emial_qq(text=text1)
                                    else:
                                        pass
                                    #调整持股
                                    self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                    #调整账户资金
                                    self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                            else:
                                print('{}  {} 冲高回落 不可以卖出'.format(stock,datetime.now()))
                        #超跌反弹买入
                        elif trader_type=='超跌反弹' and select==True:
                            #检查是不是强制赎回
                            if self.check_cov_bond_av_trader(stock=stock):
                                spot_data=self.data.get_spot_data(stock=stock)
                                #价格
                                price=spot_data['最新价']
                                lof_list=text['lof基金列表']
                                stock=str(stock)
                                if stock[:6] in lof_list:
                                    price=price
                                else:
                                    price=price
                                #实时涨跌幅
                                zdf=spot_data['涨跌幅']
                                #检查是不是可以买入
                                if self.check_stock_is_av_buy(stock=stock,price=price,amount=amount):
                                    trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='sell')
                                    if trader_type=='buy':
                                        self.trader.buy(security=stock,price=price,amount=amount)
                                        #text1='买入 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                        text1=name+text1
                                        print(text1)
                                        if seed=='真':
                                            self.seed_emial_qq(text=text1)
                                        else:
                                            pass
                                        #调整持股                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                        self.adjust_hold_data(stock=stock,trader_type='buy',price=price,amount=amount)
                                        #调整账户资金
                                        self.adjust_account_cash(stock=stock,trader_type='buy',price=price,amount=amount)
                                else:
                                    print('{} {}冲高回落超跌反弹不可以买入'.format(stock,datetime.now()))
                            else:
                                print('{} {}冲高回落超跌反弹不交易'.format(stock,datetime.now()))
                        else:
                            print('{} {}不符合冲高回落超跌反弹'.format(stock,datetime.now()))
                    except Exception as e:
                        print("运行错误:",e)
                        print('{}冲高回落超跌反弹有问题'.format(stock))
            else:
                print('{}冲高回落超跌反弹没有持股'.format(datetime.now()))
        else:
            print('{}冲高回落超跌反弹不是交易时间'.format(datetime.now()))
    def get_mi_pulse_trader(self):
        '''
        分钟脉冲分析
        '''
        if self.check_is_trader_date_1()==True:
        #if True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            seed=text['发送通知']
            pulse_time=text['分钟脉冲时间']
            max_pulse=text['分钟脉冲上涨']
            min_pulse=text['分钟脉冲下跌']
            sell_all=text['一次性卖出']
            name=text['策略名称']
            select=text['分钟脉冲是否时间增强']
            h=text['分钟脉冲增强小时']
            mi=text['分钟脉冲增强分钟']
            num=text['分钟脉冲增强倍数']
            df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
            try:
                del df['Unnamed: 0']
            except Exception as e:
                print("运行错误:",e)
            df['可用余额']=df['可用余额'].astype(float)
            #股票不能T0
            #df1=df[df['可用余额']>=10]
            df1=df
            if df1.shape[0]>0:
                stock_list=df1['证券代码'].tolist()
                for stock in stock_list:
                    try:
                        hold_num=df[df['证券代码']==stock]['可用余额'].tolist()[-1]
                        if sell_all=='是':
                            amount=hold_num
                        else:
                            amount=text['固定交易数量']
                        #脉冲
                        try:
                            pulse=self.analysis_models.get_mi_pulse_trader_analysis(n=pulse_time,x1=max_pulse,
                            x2=min_pulse,stock=stock,select=select,h=h,mi=mi,num=num)
                        except Exception as e:
                            print("运行错误:",e)
                            print('分钟脉冲分析{}有问题'.format(stock))
                            pulse=False
                        #脉冲卖出
                        if pulse=='sell':
                            #检查是否可以卖出
                            if self.check_stock_is_av_sell(stock=stock,amount=amount):
                                #获取实时数据
                                spot_data=self.data.get_spot_data(stock=stock)
                                #价格
                                price=spot_data['最新价']
                                lof_list=text['lof基金列表']
                                stock=str(stock)
                                if stock[:6] in lof_list:
                                    price=price
                                else:
                                    price=price
                                stock=str(stock)
                                trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='sell')
                                if trader_type=='sell':
                                    self.trader.sell(security=stock,price=price,amount=amount)
                                    text1='分钟向上脉冲卖出 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                    text1=name+text1
                                    print(text1)
                                    if seed=='真':
                                        self.seed_emial_qq(text=text1)
                                    else:
                                        pass
                                    #调整持股
                                    self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                    #调整账户资金
                                    self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                            else:
                                print('分钟脉冲{} {} 不可以卖出'.format(stock,datetime.now()))
                        elif pulse=='buy':
                            #检查是不是强制赎回
                            if self.check_cov_bond_av_trader(stock=stock):
                                spot_data=self.data.get_spot_data(stock=stock)
                                #价格
                                price=spot_data['最新价']
                                lof_list=text['lof基金列表']
                                stock=str(stock)
                                if stock[:6] in lof_list:
                                    price=price
                                else:
                                    price=price
                                #实时涨跌幅
                                #检查是不是可以买入
                                if self.check_stock_is_av_buy(stock=stock,price=price,amount=amount):
                                    trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='buy')
                                    if trader_type=='buy':
                                        self.trader.buy(security=stock,price=price,amount=amount)
                                        text1='分钟向下脉冲买入 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                        text1=name+text1
                                        print(text1)
                                        if seed=='真':
                                            self.seed_emial_qq(text=text1)
                                        else:
                                            pass
                                        #调整持股
                                        self.adjust_hold_data(stock=stock,trader_type='buy',price=price,amount=amount)
                                        #调整账户资金
                                        self.adjust_account_cash(stock=stock,trader_type='buy',price=price,amount=amount)
                                else:
                                    print('分钟脉冲{} {} 不可以买入'.format(stock,datetime.now()))
                            else:
                                print('分钟脉冲{} {} 强制赎回不可以交易'.format(stock,datetime.now()))
                        else:
                            print('分钟脉冲{} {} 不符合买入要求'.format(stock,datetime.now()))
                    except Exception as e:
                        print("运行错误:",e)
                        print('{}分钟脉冲反弹有问题'.format(stock))
            else:
                print('分钟脉冲{} 没有持股'.format(datetime.now()))
        else:
            print('分钟脉冲{} 不是交易时间'.format(datetime.now()))
    def get_dynamicmi_pulse_trader(self):
        '''
        动态脉冲分钟交易
        '''
        if self.check_is_trader_date_1()==True:
        #if True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            seed=text['发送通知']
            daily=text['动态脉冲天数']
            mi=text['动态脉冲时间']
            up_ratio=text['动态脉冲上涨比例']
            down_ratio=text['动态脉冲下跌比例']
            sell_all=text['一次性卖出']
            name=text['策略名称']
            df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
            try:
                del df['Unnamed: 0']
            except Exception as e:
                print("运行错误:",e)
            df['可用余额']=df['可用余额'].astype(float)
            #股票不能T0
            #df1=df[df['可用余额']>=10]
            df1=df
            if df1.shape[0]>0:
                stock_list=df1['证券代码'].tolist()
                for stock in stock_list:
                    try:
                        hold_num=df[df['证券代码']==stock]['可用余额'].tolist()[-1]
                        if sell_all=='是':
                            amount=hold_num
                        else:
                            amount=text['固定交易数量']
                        #脉冲
                        try:
                            pulse=self.analysis_models.get_dynamic_trader_analysis(daily=daily,mi=mi,x=up_ratio,x1=down_ratio)
                        except Exception as e:
                            print("运行错误:",e)
                            print('动态脉冲分钟交易{}有问题'.format(stock))
                            pulse=False
                        #脉冲卖出
                        if pulse=='sell':
                            #检查是否可以卖出
                            if self.check_stock_is_av_sell(stock=stock,amount=amount):
                                #获取实时数据
                                spot_data=self.data.get_spot_data(stock=stock)
                                #价格
                                price=spot_data['最新价']
                                lof_list=text['lof基金列表']
                                stock=str(stock)
                                if stock[:6] in lof_list:
                                    price=price
                                else:
                                    price=price
                                stock=str(stock)
                                trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='sell')
                                if trader_type=='sell':
                                    self.trader.sell(security=stock,price=price,amount=amount)
                                    text1='动态脉冲分钟交易卖出 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                    text1=name+text1
                                    print(text1)
                                    if seed=='真':
                                        self.seed_emial_qq(text=text1)
                                    else:
                                        pass
                                    #调整持股
                                    self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                    #调整账户资金
                                    self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                            else:
                                print('动态脉冲分钟交易{} {} 不可以卖出'.format(stock,datetime.now()))
                        elif pulse=='buy':
                            #检查是不是强制赎回
                            if self.check_cov_bond_av_trader(stock=stock):
                                spot_data=self.data.get_spot_data(stock=stock)
                                #价格
                                price=spot_data['最新价']
                                lof_list=text['lof基金列表']
                                stock=str(stock)
                                if stock[:6] in lof_list:
                                    price=price
                                else:
                                    price=price
                                #实时涨跌幅
                                zdf=spot_data['涨跌幅']
                                #检查是不是可以买入
                                if self.check_stock_is_av_buy(stock=stock,price=price,amount=amount):
                                    trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='sell')
                                    if trader_type=='sell':
                                        self.trader.buy(security=stock,price=price,amount=amount)
                                        text1='动态脉冲买入 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                        text1=name+text1
                                        print(text1)
                                        if seed=='真':
                                            self.seed_emial_qq(text=text1)
                                        else:
                                            pass
                                        #调整持股
                                        self.adjust_hold_data(stock=stock,trader_type='buy',price=price,amount=amount)
                                        #调整账户资金
                                        self.adjust_account_cash(stock=stock,trader_type='buy',price=price,amount=amount)
                                else:
                                    print('动态脉冲分钟交易{} {} 不可以买入'.format(stock,datetime.now()))
                            else:
                                print('动态脉冲分钟交易{} {} 强制赎回不可以交易'.format(stock,datetime.now()))
                        else:
                            print('动态脉冲分钟交易{} {} 不符合买入要求'.format(stock,datetime.now()))
                    except Exception as e:
                        print("运行错误:",e)
                        print('动态脉冲分钟{}有问题'.format(stock))
            else:
                print('动态脉冲分钟交易{} 没有持股'.format(datetime.now()))
        else:
            print('动态脉冲分钟交易{} 不是交易时间'.format(datetime.now()))
    def get_hour_pulse_trader(self):
        '''
        小时趋势
        '''
        if self.check_is_trader_date_1()==True:
        #if True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            seed=text['发送通知']
            pulse_time=text['小时趋势时间']
            max_pulse=text['小时趋势上涨']
            min_pulse=text['小时趋势下跌']
            sell_all=text['一次性卖出']
            name=text['策略名称']
            df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
            try:
                del df['Unnamed: 0']
            except Exception as e:
                print("运行错误:",e)
            df['可用余额']=df['可用余额'].astype(float)
            #股票不能T0
            #df1=df[df['可用余额']>=10]
            df1=df
            if df1.shape[0]>0:
                stock_list=df1['证券代码'].tolist()
                for stock in stock_list:
                    try:
                        hold_num=df[df['证券代码']==stock]['可用余额'].tolist()[-1]
                        if sell_all=='是':
                            amount=hold_num
                        else:
                            amount=text['固定交易数量']
                        #脉冲
                        pulse=self.analysis_models.get_hour_pulse_trader_analysis(hour=pulse_time*60,x1=max_pulse,x2=min_pulse,stock=stock)
                        #脉冲卖出
                        if pulse=='sell':
                            #检查是否可以卖出
                            if self.check_stock_is_av_sell(stock=stock,amount=amount):
                                #获取实时数据
                                spot_data=self.data.get_spot_data(stock=stock)
                                #价格
                                price=spot_data['最新价']
                                lof_list=text['lof基金列表']
                                stock=str(stock)
                                if stock[:6] in lof_list:
                                    price=price
                                else:
                                    price=price
                                stock=str(stock)
                                trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='sell')
                                if trader_type=='sell':
                                    self.trader.sell(security=stock,price=price,amount=amount)
                                    text1='小时趋势卖出 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                    text1=name+text1
                                    print(text1)
                                    if seed=='真':
                                        self.seed_emial_qq(text=text1)
                                    else:
                                        pass
                                    #调整持股
                                    self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                    #调整账户资金
                                    self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                            else:
                                print('小时趋势{} {} 不可以卖出'.format(stock,datetime.now()))
                        elif pulse=='buy':
                            #检查是不是强制赎回
                            if self.check_cov_bond_av_trader(stock=stock):
                                spot_data=self.data.get_spot_data(stock=stock)
                                #价格
                                price=spot_data['最新价']
                                lof_list=text['lof基金列表']
                                stock=str(stock)
                                if stock[:6] in lof_list:
                                    price=price
                                else:
                                    price=price
                                #实时涨跌幅
                                zdf=spot_data['涨跌幅']
                                #检查是不是可以买入
                                if self.check_stock_is_av_buy(stock=stock,price=price,amount=amount):
                                    trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='sell')
                                    if trader_type=='buy':
                                        self.trader.buy(security=stock,price=price,amount=amount)
                                        text1='小时趋势买入 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                        text1=name+text1
                                        print(text1)
                                        if seed=='真':
                                            self.seed_emial_qq(text=text1)
                                        else:
                                            pass
                                        #调整持股
                                        self.adjust_hold_data(stock=stock,trader_type='buy',price=price,amount=amount)
                                        #调整账户资金
                                        self.adjust_account_cash(stock=stock,trader_type='buy',price=price,amount=amount)
                                else:
                                    print('小时趋势{} {} 不可以买入'.format(stock,datetime.now()))
                            else:
                                print('小时趋势{} {} 强制赎回不可以交易'.format(stock,datetime.now()))
                        else:
                            print('小时趋势{} {} 不符合买入要求'.format(stock,datetime.now()))
                    except Exception as e:
                        print("运行错误:",e)
                        print('小时趋势{}有问题'.format(stock))
            else:
                print('小时趋势{} 没有持股'.format(datetime.now()))
        else:
            print('小时趋势{} 不是交易时间'.format(datetime.now()))
    def get_mean_line_trade(self):
        '''
        参考均线交易
        '''
        if self.check_is_trader_date_1()==True:
        #if True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            seed=text['发送通知']
            update_time=text['盘中均线刷新时间']
            data_type=text['盘中参考数据周期']
            n=text['盘中窗口']
            sell_all=text['一次性卖出']
            name=text['策略名称']
            df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
            try:
                del df['Unnamed: 0']
            except Exception as e:
                print("运行错误:",e)
            df['可用余额']=df['可用余额'].astype(float)
            #股票不能T0
            #df1=df[df['可用余额']>=10]
            df1=df
            if df1.shape[0]>0:
                stock_list=df1['证券代码'].tolist()
                for stock in stock_list:
                    try:
                        hold_num=df[df['证券代码']==stock]['可用余额'].tolist()[-1]
                        if sell_all=='是':
                            amount=hold_num
                        else:
                            amount=text['固定交易数量']
                        #参考均线交易
                        try:
                            pulse=self.analysis_models.get_trader_mean_line_analysis(stock=stock,n=data_type,mean_line=n)
                        except Exception as e:
                            print("运行错误:",e)
                            print('参考均线{}有问题'.format(stock))
                            pulse=False
                        #参考均线交易卖出
                        if pulse=='sell':
                            #检查是否可以卖出
                            if self.check_stock_is_av_sell(stock=stock,amount=amount):
                                #获取实时数据
                                spot_data=self.data.get_spot_data(stock=stock)
                                #价格
                                price=spot_data['最新价']
                                lof_list=text['lof基金列表']
                                stock=str(stock)
                                if stock[:6] in lof_list:
                                    price=price
                                else:
                                    price=price
                                stock=str(stock)
                                trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='sell')
                                if trader_type=='sell':
                                    self.trader.sell(security=stock,price=price,amount=amount)
                                    text1='参考均线交易卖出 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                    text1=name+text1
                                    print(text1)
                                    if seed=='真':
                                        self.seed_emial_qq(text=text1)
                                    else:
                                        pass
                                    #调整持股
                                    self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                    #调整账户资金
                                    self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                            else:
                                print('参考均线交易趋势{} {} 不可以卖出'.format(stock,datetime.now()))
                        elif pulse=='buy':
                            #检查是不是强制赎回
                            if self.check_cov_bond_av_trader(stock=stock):
                                spot_data=self.data.get_spot_data(stock=stock)
                                #价格
                                price=spot_data['最新价']
                                lof_list=text['lof基金列表']
                                stock=str(stock)
                                if stock[:6] in lof_list:
                                    price=price
                                else:
                                    price=price
                                #实时涨跌幅
                                zdf=spot_data['涨跌幅']
                                #检查是不是可以买入
                                if self.check_stock_is_av_buy(stock=stock,price=price,amount=amount):
                                    trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='sell')
                                    if trader_type=='buy':
                                        self.trader.buy(security=stock,price=price,amount=amount)
                                        text1='参考均线交易买入 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                        text1=name+text1
                                        print(text1)
                                        if seed=='真':
                                            self.seed_emial_qq(text=text1)
                                        else:
                                            pass
                                        #调整持股
                                        self.adjust_hold_data(stock=stock,trader_type='buy',price=price,amount=amount)
                                        #调整账户资金
                                        self.adjust_account_cash(stock=stock,trader_type='buy',price=price,amount=amount)
                                else:
                                    print('参考均线交易{} {} 不可以买入'.format(stock,datetime.now()))
                            else:
                                print('参考均线交易{} {} 强制赎回不可以交易'.format(stock,datetime.now()))
                        else:
                            print('参考均线交易{} {} 不符合买入要求'.format(stock,datetime.now()))
                    except Exception as e:
                        print("运行错误:",e)
                        print('参考均线{}有问题'.format(stock))
            else:
                print('参考均线交易{} 没有持股'.format(datetime.now()))
        else:
            print('参考均线交易{} 不是交易时间'.format(datetime.now()))

    def get_zig_trader(self):
        '''
        之子转向
        '''
        if self.check_is_trader_date_1()==True:
        #if True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            seed=text['发送通知']
            x=text['zig转向点']
            sell_all=text['一次性卖出']
            name=text['策略名称']
            df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
            try:
                del df['Unnamed: 0']
            except Exception as e:
                print("运行错误:",e)
            df['可用余额']=df['可用余额'].astype(float)
            #股票不能T0
            #df1=df[df['可用余额']>=10]
            df1=df
            if df1.shape[0]>0:
                stock_list=df1['证券代码'].tolist()
                for stock in stock_list:
                    try:
                        hold_num=df[df['证券代码']==stock]['可用余额'].tolist()[-1]
                        if sell_all=='是':
                            amount=hold_num
                        else:
                            amount=text['固定交易数量']
                        try:
                            zig=self.analysis_models.cacal_zig_data(stock=stock,x=x)
                            stats=zig['买卖点'].tolist()[-1]
                        except Exception as e:
                            print("运行错误:",e)
                            print('zig{}有问题'.format(stock))
                            stats=False
                        if stats=='sell':
                            #检查是否可以卖出
                            if self.check_stock_is_av_sell(stock=stock,amount=amount):
                                #获取实时数据
                                spot_data=self.data.get_spot_data(stock=stock)
                                #价格
                                price=spot_data['最新价']
                                lof_list=text['lof基金列表']
                                stock=str(stock)
                                if stock[:6] in lof_list:
                                    price=price
                                else:
                                    price=price
                                stock=str(stock)
                                trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='sell')
                                if trader_type=='sell':
                                    self.trader.sell(security=stock,price=price,amount=amount)
                                    text1='之子转向卖出 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                    text1=name+text1
                                    print(text1)
                                    if seed=='真':
                                        self.seed_emial_qq(text=text1)
                                    else:
                                        pass
                                    #调整持股
                                    self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                    #调整账户资金
                                    self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                            else:
                                print('之子转向{} {} 不可以卖出'.format(stock,datetime.now()))
                        elif stats=='buy':
                            #检查是不是强制赎回
                            if self.check_cov_bond_av_trader(stock=stock):
                                spot_data=self.data.get_spot_data(stock=stock)
                                #价格
                                price=spot_data['最新价']
                                lof_list=text['lof基金列表']
                                stock=str(stock)
                                if stock[:6] in lof_list:
                                    price=price
                                else:
                                    price=price
                                #实时涨跌幅
                                zdf=spot_data['涨跌幅']
                                #检查是不是可以买入
                                if self.check_stock_is_av_buy(stock=stock,price=price,amount=amount):
                                    trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='sell')
                                    if trader_type=='sell':
                                        self.trader.buy(security=stock,price=price,amount=amount)
                                        text1='之子转向买入 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                        text1=name+text1
                                        print(text1)
                                        if seed=='真':
                                            self.seed_emial_qq(text=text1)
                                        else:
                                            pass
                                        #调整持股
                                        self.adjust_hold_data(stock=stock,trader_type='buy',price=price,amount=amount)
                                        #调整账户资金
                                        self.adjust_account_cash(stock=stock,trader_type='buy',price=price,amount=amount)
                                else:
                                    print('之子转向{} {} 不可以买入'.format(stock,datetime.now()))
                            else:
                                print('之子转向{} {} 强制赎回不可以交易'.format(stock,datetime.now()))
                        else:
                            print('之子转向{} {} 不符合买入要求'.format(stock,datetime.now()))
                    except Exception as e:
                        print("运行错误:",e)
                        print('之子转向{}有问题'.format(stock))
                    
            else:
                print('之子转向{} 没有持股'.format(datetime.now()))
        else:
            print('之子转向{} 不是交易时间'.format(datetime.now()))
    def save_data_before_disk(self):
        '''
        盘前保存数据
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
        print('黑名单*********')
        print(del_stock_list)
        def select_del_stock_list(x):
            if str(x)[:6] in del_stock_list:
                return '是'
            else:
                return '否'
        #持股
        try:
            position=self.trader.position()
            position['黑名单']=position['证券代码'].apply(select_del_stock_list)
            position=position[position['黑名单']=='否']
            print('剔除黑名单**********')
            position['标的类型']=position['证券代码'].apply(self.base_func.select_data_type)
            trader_type=text['交易品种']
            if trader_type=='全部':
                position=position[position['股票余额']>=10]
                position.to_excel(r'盘前持股\盘前持股.xlsx')
            else:
                position=position[position['股票余额']>=10]
                position=position[position['标的类型']==trader_type]
            print('盘前保存数据获取成功')
            position.to_excel(r'盘前持股\盘前持股.xlsx')
            print(position)
        except Exception as e:
            print("运行错误:",e)
            print('获取持股失败')
    def save_account_data(self):
        '''
        保持账户数据
        '''
        #if self.check_is_trader_date_1()==True:
        with open(r'分析配置.json',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        del_stock_list=text['黑名单']
        print(del_stock_list)
        def select_del_stock_list(x):
            if str(x)[:6] in del_stock_list:
                return '是'
            else:
                return '否'
        if True:
            #持股
            try:
                position=self.trader.position()
                position['黑名单']=position['证券代码'].apply(select_del_stock_list)
                position=position[position['黑名单']=='否']
                print('剔除黑名单**********')
                position['标的类型']=position['证券代码'].apply(self.base_func.select_data_type)
                trader_type=text['交易品种']
                if trader_type=='全部':
                    position=position[position['股票余额']>=10]
                    position.to_excel(r'持股数据\持股数据.xlsx')
                else:
                    position=position[position['股票余额']>=10]
                    position=position[position['标的类型']==trader_type]
                print('账户数据获取成功')
                position.to_excel(r'持股数据\持股数据.xlsx')
                print(position)
            except Exception as e:
                print("运行错误:",e)
                print('获取持股失败')
            #账户
            try:
                account=self.trader.balance()
                account.to_excel(r'账户数据\账户数据.xlsx')
                print('获取账户成功')
                print(account)
            except Exception as e:
                print("运行错误:",e)
                print('获取账户失败')
            try:
                today_trades=self.trader.today_trades()
                today_trades.to_excel(r'当日成交\当日成交.xlsx')
                print('当日成交**********')
                print(today_trades)
            except Exception as e:
                print("运行错误:",e)
                today_trades=pd.DataFrame()
                today_trades.to_excel(r'当日成交\当日成交.xlsx')
                print('当日成交失败**********')
            try:
                today_entrusts=self.trader.today_entrusts()
                today_entrusts.to_excel(r'当日委托\当日委托.xlsx')
            except Exception as e:
                print("运行错误:",e)
                today_entrusts=pd.DataFrame()
                today_entrusts.to_excel(r'当日委托\当日委托.xlsx')
                print('当日委托失败**********')
                
        else:
            self.connact()
            print('{} 目前不是交易时间'.format(datetime.now()))
    def save_account_data_1(self):
        '''
        保持账户数据
        '''
        #if self.check_is_trader_date_1()==True:
        #持股
        if True:
            try:
                position=self.trader.position()
                position.to_excel(r'持股数据\持股数据.xlsx')
                print('账户数据获取成功')
            except Exception as e:
                print("运行错误:",e)
                #账户
                try:
                    account=self.trader.balance()
                    account.to_excel(r'账户数据\账户数据.xlsx')
                    print('获取账户成功')
                except Exception as e:
                    print("运行错误:",e)
                    print('获取账户失败')
        else:
            self.connact()
            print('{} 目前不是交易时间'.format(datetime.now()))
    def seed_qq_email_info(self):
        #self.connact()
        #self.trader.refresh()
        if self.check_is_trader_date()==True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            name=text['策略名称']
        #if True:
            if self.connact()==True:
                now=str(datetime.now())
                text1=name+now+'程序连接正常'
                print(text1)
                with open('分析配置.json','r+',encoding='utf-8') as f:
                    com=f.read()
                text=json.loads(com)
                seed=text['发送通知']
                seed_type=text['发送方式']
                token_list=text['钉钉账户token']
                if seed=='真':
                    if seed_type=='钉钉':
                        try:
                            self.seed_dingding(msg=text1,access_token_list=token_list)
                        except Exception as e:
                            print("运行错误:",e)
                            print('钉钉发送失败')
                    else:
                        try: 
                            self.seed_emial_qq(text=text1)
                        except Exception as e:
                            print("运行错误:",e)
                            print('qq发送失败')
                else:
                    pass
            else:
                self.connact()
        else:
            self.connact()
            print('{} 目前不是交易时间'.format(datetime.now()))
    def get_dt_grid_trade(self):
        '''
        动态网格交易
        '''
        if self.check_is_trader_date_1()==True:
        #if True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            seed=text['发送通知']
            daily=text['网格最近N天']
            n=text['网格数量']
            tiem_size=text['网格时间大小']
            q=text['买卖分位数']
            entiy_select=text['网格单元格小于']
            bs=text['增强倍数']
            stop=text['跌破最后一个网格是否全部卖出']
            auto_adjust=text['动态网格自动调整']
            if auto_adjust=='是':
                auto_adjust=True
            else:
                auto_adjust=False
            if stop=='True':
                stop=True
            else:
                stop=False
            stop_line=text['网格止损线']
            sell_all=text['一次性卖出']
            name=text['策略名称']
            df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
            try:
                del df['Unnamed: 0']
            except Exception as e:
                print("运行错误:",e)
            df['可用余额']=df['可用余额'].astype(float)
            #股票不能T0
            #df1=df[df['可用余额']>=10]
            df1=df
            if df1.shape[0]>0:
                stock_list=df1['证券代码'].tolist()
                for stock in stock_list:
                    try:
                        hold_num=df[df['证券代码']==stock]['可用余额'].tolist()[-1]
                        if sell_all=='是':
                            amount=hold_num
                        else:
                            amount=text['固定交易数量']
                        # 动态网格交易
                        try:
                            pulse,text1=self.analysis_models.get_grid_analysis(stock=stock,daily=daily,n=n,time_size=tiem_size,
                            buy_sell_dot=q,stop=stop,stop_line=stop_line,entiy_select=entiy_select,bs=bs,auto_adjust=auto_adjust)
                        except Exception as e:
                            print("运行错误:",e)
                            print('动态网格交易{}有问题'.format(stock))
                            pulse=False
                        # 动态网格交易
                        if pulse=='sell':
                            #检查是否可以卖出
                            if self.check_stock_is_av_sell(stock=stock,amount=amount):
                                #获取实时数据
                                spot_data=self.data.get_spot_data(stock=stock)
                                #价格
                                price=spot_data['最新价']
                                lof_list=text['lof基金列表']
                                stock=str(stock)
                                if stock[:6] in lof_list:
                                    price=price
                                else:
                                    price=price
                                stock=str(stock)
                                trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='sell')
                                if trader_type=='sell':
                                    self.trader.sell(security=stock,price=price,amount=amount)
                                    text1=text1
                                    text1=name+text1
                                    print(text1)
                                    if seed=='真':
                                        self.seed_emial_qq(text=text1)
                                    else:
                                        pass
                                    #调整持股
                                    self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                    #调整账户资金
                                    self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                            else:
                                print('动态网格{} {} 不可以卖出'.format(stock,datetime.now()))
                        elif pulse=='buy':
                            #检查是不是强制赎回
                            if self.check_cov_bond_av_trader(stock=stock):
                                spot_data=self.data.get_spot_data(stock=stock)
                                #价格
                                price=spot_data['最新价']
                                lof_list=text['lof基金列表']
                                stock=str(stock)
                                if stock[:6] in lof_list:
                                    price=price
                                else:
                                    price=price
                                #实时涨跌幅
                                zdf=spot_data['涨跌幅']
                                #检查是不是可以买入
                                if self.check_stock_is_av_buy(stock=stock,price=price,amount=amount):
                                    trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='buy')
                                    if trader_type=='buy':
                                        self.trader.buy(security=stock,price=price,amount=amount)
                                        text1=text1
                                        text1=name+text1
                                        print(text1)
                                        if seed=='真':
                                            self.seed_emial_qq(text=text1)
                                        else:
                                            pass
                                        #调整持股
                                        self.adjust_hold_data(stock=stock,trader_type='buy',price=price,amount=amount)
                                        #调整账户资金
                                        self.adjust_account_cash(stock=stock,trader_type='buy',price=price,amount=amount)
                                else:
                                    print('动态网格{} {} 不可以买入'.format(stock,datetime.now()))
                            else:
                                print('动态网格{} {} 强制赎回不可以交易'.format(stock,datetime.now()))
                        else:
                            print('动态网格{} {} 不符合买入要求'.format(stock,datetime.now()))
                    except Exception as e:
                        print("运行错误:",e)
                        print('动态网格{}有问题'.format(stock))
            else:
                print('动态网格{} 没有持股'.format(datetime.now()))
        else:
            print('动态网格{} 不是交易时间'.format(datetime.now()))   
    def get_fix_grid_trade(self):
        '''
        固定网格
        '''
        if self.check_is_trader_date_1()==True:
        #if True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            seed=text['发送通知']
            n=text['固定网格数量']
            entiy=text['固定单元格大小']
            time_size=text['固定网格时间大小']
            buy_sell_dot=text['固定网格买卖分位数']
            stop=text['固定网格止损']
            stop_line=text['固定网格止损线']
            auto_adjust=text['固定网格自动调整']
            name=text['策略名称']
            if stop=='是':
                stop=True
            else:
                stop=False
            if auto_adjust=='是':
                auto_adjust=True
            else:
                auto_adjust=False
            df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
            try:
                del df['Unnamed: 0']
            except Exception as e:
                print("运行错误:",e)
            df['可用余额']=df['可用余额'].astype(float)
            #股票不能T0
            #df1=df[df['可用余额']>=10]
            df1=df
            if df1.shape[0]>0:
                stock_list=df1['证券代码'].tolist()
                for stock in stock_list:
                        try:
                            pulse,trader_text=self.analysis_models.get_fix_grid_analysis(stock=stock,n=n,entiy=entiy,time_size=time_size,
                                        buy_sell_dot=buy_sell_dot,stop=stop,stop_line=stop_line,auto_adjust=auto_adjust)
                        except Exception as e:
                            print("运行错误:",e)
                            print('固定网格分析{}有问题'.format(stock))
                            pulse=False
                            trader_text=''
                        #固定网格
                        if pulse=='sell':
                            #检查是否可以卖出
                            spot_data=self.data.get_spot_data(stock=stock)
                            #价格
                            price=spot_data['最新价']
                            lof_list=text['lof基金列表']
                            stock=str(stock)
                            if stock[:6] in lof_list:
                                price=price
                            else:
                                price=price
                            trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='sell')
                            if self.check_stock_is_av_sell(stock=stock,amount=amount):
                                #获取实时数据
                                spot_data=self.data.get_spot_data(stock=stock)
                                #价格
                                stock=str(stock)
                                if trader_type=='sell':
                                    self.trader.sell(security=stock,price=price,amount=amount)
                                    text1=trader_text
                                    text1=name+text1
                                    print(text1)
                                    if seed=='真':
                                        self.seed_emial_qq(text=text1)
                                    else:
                                        pass
                                    #调整持股
                                    self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                    #调整账户资金
                                    self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                            else:
                                print('固定网格{} {} 不可以卖出'.format(stock,datetime.now()))
                        elif pulse=='buy':
                            #检查是不是强制赎回
                            if self.check_cov_bond_av_trader(stock=stock):
                                spot_data=self.data.get_spot_data(stock=stock)
                                #价格
                                price=spot_data['最新价']
                                lof_list=text['lof基金列表']
                                stock=str(stock)
                                if stock[:6] in lof_list:
                                    price=price
                                else:
                                    price=price
                                #实时涨跌幅
                                zdf=spot_data['涨跌幅']
                                #检查是不是可以买入
                                if True:
                                    trader_type,amount,price=self.check_av_target_tarder(stock=stock,price=price,trader_type='buy')
                                    if trader_type=='buy':
                                        self.trader.buy(security=stock,price=price,amount=amount)
                                        text1=trader_text
                                        text1=name+text1
                                        print(text1)
                                        if seed=='真':
                                            self.seed_emial_qq(text=text1)
                                        else:
                                            pass
                                        #调整持股
                                        self.adjust_hold_data(stock=stock,trader_type='buy',price=price,amount=amount)
                                        #调整账户资金
                                        self.adjust_account_cash(stock=stock,trader_type='buy',price=price,amount=amount)
                                else:
                                    print('固定网格{} {} 不可以买入'.format(stock,datetime.now()))
                            else:
                                print('固定网格{} {} 强制赎回不可以交易'.format(stock,datetime.now()))
                        else:
                            print('固定网格{} {} 不符合买入要求'.format(stock,datetime.now()))
            else:
                print('固定网格{} 没有持股'.format(datetime.now()))
        else:
            print('固定网格{} 不是交易时间'.format(datetime.now()))             
    def run_user_def_trader_models(self):
        '''
        运行自定义交易模型
        '''
        with open('分析配置.json','r+',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        if True:
            user_def_type=text['自定义函数运行类型']
            user_def_time=text['自定义函数模块运行时间']
            user_def_func=text['自定义函数']

            for def_type,def_time,def_func in zip(user_def_type,user_def_time,user_def_func):
                func='self.user_def_models.{}'.format(def_func)
                if def_type=='定时':
                    schedule.every().day.at('{}'.format(def_time)).do(eval(func))
                    print('{}运行自定义分析模型{}函数在{}'.format(def_type,def_func,def_time))
                else:
                    schedule.every(def_time).minutes.do(eval(func))
                    print('{}运行自定义分析模型{}函数每{}分钟'.format(def_type,def_func,def_time))
    def get_reverse_repurchase_of_treasury_bonds(self):
        '''
        国债回购
        '''
        with open('分析配置.json','r+',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        if self.check_is_trader_date_1()==True:
            security=text['国债代码'],
            buy_ratio=text['国债购买比率']
            if self.trader_tool=='qmt':
                try:
                    stats,text1=self.trader.reverse_repurchase_of_treasury_bonds(security=security,buy_ratio=buy_ratio)
                except Exception as e:
                    print("运行错误:",e)
                    stats,text1=self.trader.reverse_repurchase_of_treasury_bonds_1(buy_ratio=buy_ratio)
            else:
                stats,text1=self.trader.reverse_repurchase_of_treasury_bonds(buy_ratio=buy_ratio)
                print('同花顺目前没有支持国债回购')
            if stats=='交易成功':
                self.seed_emial_qq(text=text1)
            else:
                text1='国债回购失败'
                self.seed_emial_qq(text=text1)
        else:
            print('目前不是交易时间',datetime.now())
    def get_ipo_trader(self):
        '''
        新股可转债申购
        '''
        with open('分析配置.json','r+',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        if self.check_is_trader_date_1()==True:
            if self.trader_tool=='qmt':
                self.trader.get_buy_stock_ipo()
                self.seed_emial_qq(text='新股可转债申购完成')
            else:
                print('同花顺目前没有支持新股可转债申购')
        else:
            print('目前不是交易时间',datetime.now())
    def run_day_trading_stop_profit_and_loss(self):
        '''
        当日交易止盈止损，按最后一笔买入价格，进行止盈止损
        stock股票代码
        spot_price实时价格
        up上涨幅度
        down下单幅度
        '''
        if self.check_is_trader_date_1()==True:
        #if True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            #amount=text['固定交易数量']
            seed=text['发送通知']
            stop=text['停止程序']
            stop_profit=text['当日交易止盈比例']
            stop_loss=text['当日交易止损比例']
            sell_all='是'
            name=text['策略名称']
            if stop=='真':
                print('程序停止')
            else:
                df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
                try:
                    del df['Unnamed: 0']
                except Exception as e:
                    print("运行错误:",e)
                if df.shape[0]>0:
                    stock_list=df['证券代码'].tolist()
                    for stock in stock_list:
                        #检查是否可以交易
                        try:
                            if self.check_cov_bond_av_trader(stock=stock):
                                #持有数量
                                hold_num=df[df['证券代码']==stock]['可用余额'].tolist()[-1]
                                if sell_all=='是':
                                    amount=hold_num
                                else:
                                    amount=text['固定交易数量']
                                #检查是否可以卖出
                                if self.check_stock_is_av_sell(stock=stock,amount=amount):
                                    spot_data=self.data.get_spot_data(stock=stock)
                                    #价格
                                    price=spot_data['最新价']
                                    lof_list=text['lof基金列表']
                                    stock=str(stock)
                                    if stock[:6] in lof_list:
                                        price=price/10
                                    else:
                                        price=price
                                    stock=str(stock)
                                    push=self.analysis_models.day_trading_stop_profit_and_loss(stock=stock,spot_price=price,up=stop_profit,down=stop_loss)
                                    if push=='sell' and amount>0:
                                        self.trader.sell(security=stock,price=price,amount=amount)
                                        text1='当日交易止盈止损， 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                        text1=name+text1
                                        print(text1)
                                        if seed=='真':
                                            self.seed_emial_qq(text=text1)
                                        else:
                                            pass
                                        #调整持股
                                        self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                        #调整账户资金
                                        self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                                    else:
                                        print('{} {}当日交易止盈止损,不符合要求1'.format(stock,datetime.now()))
                                else:
                                    print('{} {}当日交易止盈止损，不符合要求2'.format(stock,datetime.now()))
                            else:
                                print('{}当日交易止盈止损，不符合要求3'.format(datetime.now()))
                        except Exception as e:
                            print("运行错误:",e)
                            print('{}当日交易止盈止损，有问题不符合要求4'.format(stock))
                else:
                    print('{}当日交易止盈止损，没有持股'.format(datetime.now()))
        else:
            print('{}当日交易止盈止损，不是交易时间'.format(datetime.now()))
    def seed_emial_qq_1(self,text='交易完成'):
        with open('分析配置.json','r+',encoding='utf-8') as f:
            com=f.read()
        text1=json.loads(com)
        try:
            password=text1['qq掩码']
            seed_qq=text1['发送qq']
            yag = yagmail.SMTP(user='{}'.format(seed_qq), password=password, host='smtp.qq.com')
            m = text1['接收qq']
            text = text
            yag.send(to=m, contents=text, subject='邮件')
            print('邮箱发生成功')
        except Exception as e:
            print("运行错误:",e)
            print('qq发送失败可能用的人多')
    def seed_emial_qq(self,text='交易完成,'):
        '''
        发生交易通知
        '''
        msg=text
        msg+=','
        with open('分析配置.json','r+',encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        access_token_list=text['钉钉账户token']
        seed_type=text['发送方式']
        if seed_type=='qq':
            self.seed_emial_qq_1(text=msg)
        else:
            self.seed_dingding(msg=msg,access_token_list=access_token_list)
    def run_the_order_is_being_withdrawn(self):
        '''
        撤单了在下单qmt
        '''
        if self.check_is_trader_date_1()==True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            df=self.trader.today_entrusts()
            if df.shape[0]>0:
                df=df[df['委托状态']>=48]
                df=df[df['委托状态']<=53]
                if df.shape[0]>0:
                    for stock,amount,order_id,data_type,in zip(df['证券代码'],df['未成交数量'],df['订单编号'],df['委托类型']):
                        #撤单
                        price=self.data.get_spot_data(stock=stock)['最新价']
                        if data_type==23 or data_type=='买入':
                            cancel_order_result=self.trader.cancel_order_stock_async(order_id=int(order_id))
                            if cancel_order_result>=0:
                                mag='时间{} 股票买入撤单{} 数量{}'.format(datetime.now(),stock,amount)
                                print(mag)
                                #下单
                                self.trader.buy(security=stock,price=price,amount=amount)
                                msg=mag='时间{} 股票买入撤单在买入{} 数量{} 价格{}'.format(datetime.now(),stock,amount,price)
                            else:
                                print(cancel_order_result)
                        elif data_type==24 or data_type=='卖出':
                            cancel_order_result=self.trader.cancel_order_stock_async(order_id=order_id)
                            if cancel_order_result>=0:
                                mag='时间{} 股票卖出撤单{} 数量{}'.format(datetime.now(),stock,amount)
                                print(mag)
                                #下单
                                self.trader.sell(security=stock,price=price,amount=amount)
                                msg=mag='时间{} 股票卖出撤单在卖出{} 数量{} 价格{}'.format(datetime.now(),stock,amount,price)
                                print(msg)
                            else:
                                print(cancel_order_result)
                        else:
                            print('{}未知的交易类型'.format(stock))
                else:
                    print('{} 没有委托可用撤单'.format(datetime.now()))
            else:
                print('{} 没有委托'.format(datetime.now()))
    def run_intra_day_stop_loss(self):
        '''
        运行盘中日线止损
        '''
        if self.check_is_trader_date_1()==True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
    def run_custom_profit_stop_loss(self):
        '''
        自定义止盈止损
        '''
        if self.check_is_trader_date_1()==True:
            with open('分析配置.json','r+',encoding='utf-8') as f:
                com=f.read()
            text=json.loads(com)
            df=pd.read_excel(r'自定义止盈止损\自定义止盈止损.xlsx',dtype='object')
            #print(df)
            try:
                del df['Unnamed: 0']
            except Exception as e:
                print("运行错误:",e)
            now_date=''.join(str(datetime.now())[:10].split('-'))
            stats_list=[]
            if df.shape[0]>0:
                df['证券代码']=df['证券代码'].apply(lambda x:'0'*(6-len(str(x)))+str(x))
                df['截止日期']=pd.to_datetime(df['截止日期'])
                for stock,name,trader_type,fix_price,amount,fix_date,stats in  zip(df['证券代码'],df['证券名称'],df['操作'],df['价格'],df['数量'],df['截止日期'],df['交易状态']):
                    if stats[:4]=='等待交易':
                        fix_date=''.join(str(fix_date)[:10].split('-'))
                        if fix_date>=now_date:
                            price=self.data.get_spot_data(stock=stock)['最新价']
                            print('{} 最新价 {} 止盈止损价格{}'.format(stock,price,fix_price))
                            if trader_type=='止盈':
                                #现在的价格大于固定的价格
                                if float(price)>=float(fix_price):
                                    #检查是否可以卖出
                                    if self.trader.check_stock_is_av_sell(stock=stock,amount=amount):
                                        self.trader.sell(security=stock,price=price,amount=amount)
                                        text1='自定义止盈， 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                        text1=name+text1
                                        print(text1)
                                        self.seed_emial_qq(text=text1)
                                        self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                        #调整账户资金
                                        self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                                        stats_list.append('已经止盈')
                                    else:
                                        stats_list.append('等待交易--止盈不能卖出')
                                else:
                                    print('{} {} {} 等待交易'.format(trader_type,datetime.now(),stock))
                                    stats_list.append('等待交易')
                            elif trader_type=='止损':
                                #限制的价格低于固定价格
                                if float(price)<float(fix_price):
                                    #检查是否可以卖出
                                    if self.trader.check_stock_is_av_sell(stock=stock,amount=amount):
                                        self.trader.sell(security=stock,price=price,amount=amount)
                                        text1='自定义止损， 时间{} 代码{} 价格{} 数量{}'.format(datetime.now(),stock,price,amount)
                                        text1=name+text1
                                        print(text1)
                                        self.seed_emial_qq(text=text1)
                                        self.adjust_hold_data(stock=stock,trader_type='sell',price=price,amount=amount)
                                        #调整账户资金
                                        self.adjust_account_cash(stock=stock,trader_type='sell',price=price,amount=amount)
                                        stats_list.append('已经止损')
                                    else:
                                        stats_list.append('等待交易--止盈不能止损')
                                else:
                                    print('{} {} {} 等待交易'.format(trader_type,datetime.now(),stock))
                                    stats_list.append('等待交易')
                            else:
                                stats_list.append('等待交易--未知操作')
                        else:
                            stats_list.append('已经到期')
                    else:
                        print('{} {} {}'.format(datetime.now(),stock,stats))
                        stats_list.append(stats)
                df['交易状态']=stats_list
                df.to_excel(r'自定义止盈止损\自定义止盈止损.xlsx')
            else:
                print('{} 自定义止盈止损没有数据'.format(datetime.now()))
        else:
            print('自定义止盈止损 {} 不是交易时间'.format(datetime.now()))    

if __name__=='__main__':
    '''
    交易策略
    '''
    with open('分析配置.json','r+',encoding='utf-8') as f:
        com=f.read()
    text=json.loads(com)
    trader_tool=text['交易系统']
    exe=text['同花顺下单路径']
    tesseract_cmd=text['识别软件安装位置']
    print(tesseract_cmd)
    qq=text['发送qq']
    test=text['测试']
    open_set=text['是否开启特殊证券公司交易设置']
    qmt_path=text['qmt路径']
    qmt_account=text['qmt账户']
    qmt_account_type=text['qmt账户类型']
    slippage=text['滑点']
    trader=trader_strategy(trader_tool=trader_tool
    ,exe=exe,tesseract_cmd=tesseract_cmd,qq=qq,
                           open_set=open_set,qmt_path=qmt_path,qmt_account=qmt_account,
                           qmt_account_type=qmt_account_type,slippage=slippage)
    trader.connact()
    #运行就更新账户数据
    
    trader.save_account_data()
    if test=='真':
        trader.run_sell_below_the_moving_average_in_real_time()
        '''
        trader.save_account_data()
        trader.run_stock_trader_buy()
        trader.run_stock_trader_sell()
        trader.daily_dynamic_stop_profit_stop_loss()
        trader.dynamic_stop_profit_stop_loss()
        trader.surge_and_fall_overfall_rebound_func()
        trader.get_mi_pulse_trader()
        trader.get_dynamicmi_pulse_trader
        trader.get_hour_pulse_trader()
        trader.get_zig_trader()
        trader.get_mean_line_trade()
        trader.get_dynamicmi_pulse_trader()
        trader.get_dt_grid_trade()
        trader.get_sell_not_in_analaysis_models_in_close()
        trader.get_fix_grid_trade()
        trader.get_ipo_trader()
        trader.get_reverse_repurchase_of_treasury_bonds()
        '''
    else:
        #交易前先保存数据
        user_def_select=text['是否开启自定义函数模块']
        user_def_type=text['自定义函数运行类型']
        user_def_time=text['自定义函数模块运行时间']
        user_def_func=text['自定义函数']
        if user_def_select=='是':
            print('开启自定义函数模块')
            trader.run_user_def_trader_models()
        else:
            print('不开启自定义函数模块')
        #是否自动申购新股可转债
        auto_stock_trader=text['是否自动申购新股可转债']
        auto_stock_trader_time=text['自动申购新股可转债时间']
        if auto_stock_trader=='是':
            print('开启自动申购新股可转债')
            schedule.every().day.at('{}'.format(auto_stock_trader_time)).do(trader.get_ipo_trader)
        else:
            print('不开启自动申购新股可转债')
        #国债回购
        select_bond_trader=text['是否自动回购国债']
        bond_trader_time=text['国债购买时间']
        if select_bond_trader=='是':
            print('开启国债购买')
            schedule.every().day.at('{}'.format(bond_trader_time)).do(trader.get_reverse_repurchase_of_treasury_bonds)
        else:
            print('不开启国债购买')
        #建仓
        buy_time=text['买入时间']
        schedule.every().day.at('{}'.format(buy_time)).do(trader.run_stock_trader_buy)
        #卖出
        sell_time=text['卖出时间']
        schedule.every().day.at('{}'.format(sell_time)).do(trader.run_stock_trader_sell)
        #循环买入
        cycle_buy_select=text['是否循环买入设置']
        if cycle_buy_select=='是':
            print('循环买入启动')
            cycle_buy_time=text['循环买入刷新时间']
            schedule.every(cycle_buy_time).minutes.do(trader.run_stock_trader_buy)
        else:
            print('不启动循环买入程序')
        #循环卖出
        cycle_sell_select=text['是否循环卖出']
        if cycle_sell_select=='是':
            print('循环卖出启动')
            cycle_sell_time=text['循环卖出刷新时间']
            schedule.every(cycle_sell_time).minutes.do(trader.run_stock_trader_sell)
        else:
            print('不启动循环卖出程序')
        #当日止盈止损
        daily_zyzs_select=text['是否当日止盈止损']
        if daily_zyzs_select=='是':
            print('当日止盈止损启动')
            daily_zyzs_time=text['当日止盈止损刷新时间']
            schedule.every(daily_zyzs_time).minutes.do(trader.daily_dynamic_stop_profit_stop_loss)
        else:
            print('不启动止盈止损')
        #账户止盈止损
        account_zyzs_select=text['是否账户止盈止损']
        if account_zyzs_select=='是':
            print('启动账户止盈止损')
            account_zyzs_time=text['账户止盈止损刷新时间']
            schedule.every(account_zyzs_time).minutes.do(trader.dynamic_stop_profit_stop_loss)
        else:
            print('不启动账户止盈止损')
        #冲高回落模块--超跌反弹
        cghl_zdft_select=text['是否冲高回落模块--超跌反弹']
        if cghl_zdft_select=='是':
            print('启动冲高回落模块--超跌反弹')
            cghl_zdft_time=text['冲高回落模块--超跌反弹刷新时间']
            schedule.every(cghl_zdft_time).minutes.do(trader.surge_and_fall_overfall_rebound_func)
        else:
            print('不启动启动冲高回落模块--超跌反弹')
        #分钟脉冲设置
        fzmc_select=text['是否分钟脉冲']
        if fzmc_select=='是':
            print('启动分钟脉冲')
            fzmc_time=text['分钟脉冲刷新时间']
            schedule.every(fzmc_time).minutes.do(trader.get_mi_pulse_trader)
        else:
            print('不启动分钟脉冲')
        #小时趋势
        xsqs_select=text['是否小时趋势']
        if xsqs_select=='是':
            print('启动小时趋势')
            xsqs_time=text['小时趋势刷新时间']
            xsqs_time=xsqs_time
            schedule.every(xsqs_time).minutes.do(trader.get_hour_pulse_trader)
        else:
            print('不启动小时趋势')
        #动态分钟脉冲
        dt_mi_select=text['是否动态脉冲']
        if dt_mi_select=='是':
            print('启动动态脉冲')
            dt_mi_time=text['动态脉冲刷新时间']
            schedule.every(dt_mi_time).minutes.do(trader.get_dynamicmi_pulse_trader)
        else:
            print('不启动动态脉冲')
        #之子转向
        zig_select=text['是否zig']
        if zig_select=='是':
            print('启动zig')
            zig_time=text['zig刷新时间']
            schedule.every(zig_time).minutes.do(trader.get_zig_trader)
        else:
            print('不启动zig')
        #盘中均线刷新时间
        mean_select=text['是否盘中参考均线']
        if mean_select=='是':
            print("启动盘中参考均线")
            trader_mean_line_update_time=text['盘中均线刷新时间']
            schedule.every(trader_mean_line_update_time).minutes.do(trader.get_mean_line_trade)
        else:
            print("不启动盘中参考均线")
        #发qq
        schedule.every(10).minutes.do(trader.seed_emial_qq)
        #盘中换股
        #同步手动下单数据
        tb_select=text['是否同步数据']
        tb_time=text['同步周期']
        if tb_select=='是':
            print('启动同步数据')
            schedule.every(tb_time).minutes.do(trader.save_account_data)
        else:
            print('不启动同步数据')
        #是否开启动态网格
        dt_grid_select=text['是否开启动态网格']
        dt_grid_time=text['自定义网格刷新时间']
        if dt_grid_select=='是':
            print('开启动态网格')
            schedule.every(dt_grid_time).minutes.do(trader.get_dt_grid_trade)
        else:
            print('不开启动态网格')
        fix_grid_select=text['是否开启固定网格']
        fix_grid_time=text['固定网格刷新时间']
        if fix_grid_select=='是':
            print('开启固定网格')
            schedule.every(fix_grid_time).minutes.do(trader.get_fix_grid_trade)
        else:
            print('不开启固定网格')
        trading_stop_profit=text['是否当日交易止盈止损']
        trading_stop_profit_time=text['当日交易止盈止损刷新时间']
        if trading_stop_profit=='是':
            print('开启当日交易止盈止损')
            schedule.every(trading_stop_profit_time).minutes.do(trader.run_day_trading_stop_profit_and_loss)
        else:
            print('不开启当日交易止盈止损')
        cacal=text['是否开启撤单了下单设置']
        cacal_time=text['撤单下单时间']
        if cacal=='是':
            print('开启撤单了下单设置')
            schedule.every(cacal_time).minutes.do(trader.run_the_order_is_being_withdrawn)
        else:
            print('不开启撤单了下单设置')
        spot_sell_down_mean_line=text['是否开启实时跌破均线卖出']
        spot_sell_down_mean_line_time=text['实时跌破均线卖出刷新时间']
        if spot_sell_down_mean_line=='是':
            print('开启实时跌破均线卖出')
            schedule.every(spot_sell_down_mean_line_time).minutes.do(trader.run_sell_below_the_moving_average_in_real_time)
        else:
            print('不开启实时跌破均线卖出')
        #自定义止盈止损
        user_spot_loss_select=text['是否开启自定义止盈止损']
        user_spot_loss_time=text['自定义止盈止损刷新时间']
        if user_spot_loss_select=='是':
            print('开启自定义止盈止损**************')
            schedule.every(user_spot_loss_time).minutes.do(trader.run_custom_profit_stop_loss)
        else:
            print('不开启自定义止盈止损')
    while True:
        schedule.run_pending()
        time.sleep(1)
        

