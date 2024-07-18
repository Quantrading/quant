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
import numpy as np
import os
from datetime import datetime
import time
class convertible_bonds_three_low_strategy:
    def __init__(self,trader_tool='ths',exe='C:/同花顺软件/同花顺/xiadan.exe',tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qq='1029762153@qq.com',open_set='否',qmt_path='D:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55009640',qmt_account_type='STOCK',name='run_bond_cov_rend_strategy'):
        '''
        可转债三低策略
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
        with open(r'{}/可转债三低策略设置.json'.format(self.path),encoding='utf-8') as f:
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
        with open(r'{}/可转债三低策略设置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        user=text['集思录账户']
        password=text['集思录密码']
        df=jsl_data.get_all_cov_bond_data(jsl_user=user,jsl_password=password)
        print(df)
        df.to_excel(r'{}\全部数据\全部数据.xlsx'.format(self.path))
        return df
    def calculated_double_low(self):
        '''
        计算三低
        三低=价格+100*转股溢价率+转债余额
        '''
        with open(r'{}/可转债三低策略设置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        max_yjl=text['可转债溢价率上限']
        min_yjl=text['可转债溢价率下限']
        max_gm=text['转债余额上限']
        min_gm=text['转债余额下限']
        min_value=text['三低最小值']
        max_value=text['三低最大值']
        max_price=text['价格上限']
        min_price=text['价格下限']
        yjl_weight=text['可转债溢价率权重']
        gm_weight=text['转债余额权重']
        price_weight=text['价格权重']
        max_time=text['剩余年限上限']
        min_time=text['剩余年限下限']
        trader_models=text['实盘交易模式']
        df=pd.read_excel(r'{}\全部数据\全部数据.xlsx'.format(self.path),dtype='object')
        try:
            df['转股溢价率']=df['转股溢价率_x']
        except:
            pass
        try:
            del df['Unnamed: 0']
        except:
            pass
        try:
            df['三低']=df['价格']*price_weight+df['转股溢价率']*yjl_weight+df['转债 余额']*gm_weight
        except:
            df['三低']=df['价格']*price_weight+df['转股溢价率']*yjl_weight+df['转债余额']*gm_weight
        if trader_models=='默认':
            df.to_excel(r'{}\原始三低\原始三低.xlsx'.format(self.path ))
            #排序
            df=df.sort_values(by='三低',ascending=True)
            df['三低']=pd.to_numeric(df['三低'])
            df1=df[df['三低']>=min_value]
            df2=df1[df1['三低']<=max_value]
            df3=df2[df2['价格']<=max_price]
            df4=df3[df3['价格']>=min_price]
            df5=df4[df4['转股溢价率']<=max_yjl]
            df6=df5[df5['转股溢价率']>=min_yjl]
            df7=df6[df6['剩余年限']<=max_time]
            df8=df7[df7['剩余年限']>=min_time]
            df8.to_excel(r'{}\三低\三低.xlsx'.format(self.path))
        else:
            #禄得老师的计算方式单因子排序加起来
            df['债溢价得分']=df['转股溢价率'].rank(ascending=False)*yjl_weight
            df['价格得分']=df['价格'].rank(ascending=False)*price_weight
            try:
                df['转债余额得分']=df['转债 余额'].rank(ascending=False)*gm_weight
            except:
                df['转债余额得分']=df['转债余额'].rank(ascending=False)*gm_weight
            df['总分']=df['债溢价得分']+df['价格得分']+df['转债余额得分']
            #从高到低排序，权重带了相关性
            df=df.sort_values(by='总分',ascending=False)
            df.to_excel(r'{}\全部打分\全部打分.xlsx'.format(self.path))
            df['代码']=df['证券代码'].tolist()
            df1=df[df['转股溢价率']<=max_yjl]
            df2=df1[df1['转股溢价率']>=min_yjl]
            try:
                df3=df2[df2['转债 余额']>=min_gm]
            except:
                df3=df2[df2['转债余额']>=min_gm]
            try:
                df3=df2[df2['转债 余额']<=max_gm]
            except:
                df3=df2[df2['转债余额']<=max_gm]
            df4=df3[df3['价格']<=max_price]
            df5=df4[df4['价格']>=min_price]
            df6=df5[df5['剩余年限']<=max_time]
            df7=df6[df6['剩余年限']>=min_time]
            df5.to_excel(r'{}\三低\三低.xlsx'.format(self.path))

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
        df=pd.read_excel(r'{}\三低\三低.xlsx'.format(self.path),dtype='object')
        with open(r'{}/可转债三低策略设置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        n=text['跌破N日均线卖出']
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
                line=models.get_down_mean_line_sell(n=n)
                mean_line.append(line)
            except:
                over_lining.append(None)
                mean_line.append(None)
        df['上影线']=over_lining
        df['跌破均线']=mean_line
        df1=df[df['跌破均线']=='不是']
        df1.to_excel(r'{}\选择可转债\选择可转债.xlsx'.format(self.path))
        return df1
    def get_stock_mean_line_retuen_analysis(self):
        '''
        可转债均线收益分析
        '''
        print('可转债均线收益分析')
        with open(r'{}/可转债三低策略设置.json'.format(self.path),encoding='utf-8') as f:
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
    def get_select_trader_type(self):
        '''
        选择交易方式
        '''
        with open(r'{}/可转债三低策略设置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        rend=text['是否开启趋势轮动']
        if rend=='是':
            self.get_cov_bond_shape_analysis()
            self.get_stock_mean_line_retuen_analysis()
        else:
            df=pd.read_excel(r'{}\三低\三低.xlsx'.format(self.path),dtype='object')
            try:
                df['Unnamed: 0']
            except:
                pass
            df.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
    def get_del_qzsh_data(self):
        '''
        剔除强制赎回
        '''
        print('剔除强制赎回')
        with open('{}/可转债三低策略设置.json'.format(self.path),encoding='utf-8') as f:
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
            try:
                trader_stock['Unnamed: 0']
            except:
                pass
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
            trader_stock['证券代码']=trader_stock['证券代码'].astype(str)
            df2['cell.bond_id']=df2['cell.bond_id'].astype(str)
            qssl_stock=df2['cell.bond_id'].tolist()
            trader_stock['强制赎回']=trader_stock['证券代码'].apply(lambda x: '是' if x in qssl_stock else '不是')
            trader_stock=trader_stock[trader_stock['强制赎回']=='不是']
            trader_stock.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
            return trader_stock
        else:
            trader_stock=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path),dtype='object')
            return trader_stock
    def get_del_buy_sell_data(self):
        '''
        处理交易股票池买入股票
        '''
        with open(r'{}/可转债三低策略设置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        limit=text['持股限制']
        df=self.save_position()
        df['证券代码']=df['证券代码'].astype(str)
        df1=df[df['可用余额']>=10]
        hold_stock_list=df1['证券代码'].tolist()
        n=text['跌破N日均线卖出']
        trader_df=self.get_del_qzsh_data()
        trader_df['证券代码']=trader_df['证券代码'].astype(str)
        def select_data(stock):
            if stock in hold_stock_list:
                return '持股超过限制'
            else:
                return '没有持股'
        trader_df['持股检查']=trader_df['证券代码'].apply(select_data)
        trader_df=trader_df[trader_df['持股检查'] !='持股超过限制']
        hold_stock_list=trader_df['证券代码'].tolist()
        trend=text['是否开启趋势轮动']
        if trend=='是':
            sell_list=[]
            for i in tqdm(range(len(hold_stock_list))):
                stock=hold_stock_list[i]
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
        else:
            trader_df=trader_df
        for i in range(0,10):
            try:
                trader_df['Unnamed: {}'.format(i/10)]
            except:
                pass
        trader_df.to_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path))
        return trader_df
    def get_time_rotation(self):
        '''
        轮动方式
        '''
        with open('{}/可转债三低策略设置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        now_date=''.join(str(datetime.now())[:10].split('-'))
        now_time=time.localtime()                               
        trader_type=text['轮动方式']                               
        trader_wday=text['每周轮动时间']                               
        moth_trader_time=text['每月轮动时间']
        specific_time=text['特定时间']
        year=now_time.tm_year
        moth=now_time.tm_mon
        wday=now_time.tm_wday
        daily=now_time.tm_mday
        if trader_type=='每天':
            print('轮动方式每天')
            return True
        elif trader_type=='每周':
            if trader_wday==wday:
                return True
            elif trader_wday<wday:
                print('安周轮动 目前星期{} 轮动时间星期{} 目前时间大于轮动时间不轮动'.format(wday+1,trader_wday+1))
                return False
            else:
                print('安周轮动 目前星期{} 轮动时间星期{} 目前时间小于轮动时间不轮动'.format(wday+1,trader_wday+1))
                return False
        elif trader_type=='每月轮动时间':
            stats=''
            for date in moth_trader_time:
                data=''.join(data.split('-'))
                if int(moth_trader_time)==int(date):
                    print('安月轮动 目前{} 轮动时间{} 目前时间等于轮动时间轮动'.format(now_date,date))
                    stats=True
                    break
                elif int(moth_trader_time)<int(date):
                    print('安月轮动 目前{} 轮动时间{} 目前时间小于轮动时间轮动'.format(now_date,date))
                    stats=False
                else:
                    print('安月轮动 目前{} 轮动时间{} 目前时间大于轮动时间轮动'.format(now_date,date))
                    stats=False
            return stats
        else:
            #特别时间
            stats=''
            for date in specific_time:
                data=''.join(data.split('-'))
                if int(specific_time)==int(date):
                    print('安月轮动 目前{} 轮动时间{} 目前时间等于轮动时间轮动'.format(now_date,date))
                    stats=True
                    break
                elif int(specific_time)<int(date):
                    print('安月轮动 目前{} 轮动时间{} 目前时间小于轮动时间轮动'.format(now_date,date))
                    stats=False
                else:
                    print('安月轮动 目前{} 轮动时间{} 目前时间大于轮动时间轮动'.format(now_date,date))
                    stats=False
            return stats                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
    def get_buy_sell_stock(self):
        '''
        获取买卖数据
        '''
        with open('{}/可转债三低策略设置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        buy_num=text['买入排名前N']
        hold_rank_num=text['持有排名前N']
        sell_rank_num=text['跌出排名卖出N']
        sell_value=text['三低平仓']
        hold_limit=text['持有限制']
        trader_models=text['实盘交易模式']
        df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        df['证券代码']=df['证券代码'].astype(str)
        df_yjl=pd.read_excel(r'{}\原始三低\原始三低.xlsx'.format(self.path))
        sd_dict=dict(zip(df_yjl['证券代码'],df_yjl['三低']))
        trend=text['是否开启趋势轮动']
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
                    print('目前持股 {} 没有大于{}'.format(hold_daily,hold_daily_limit))
            else:
                print('不启动持股限制')
            #跌破均线分析
            n=text['跌破N日均线卖出'] 
            if trend=='是':
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
            else:
                print('**************************88不开启持股趋势分析')
            #三低平仓
            if trader_models=='默认':
                for stock in hold_stock_list:
                    value=sd_dict.get(stock,0)
                    if value>=sell_value:
                        print('三低平仓 {} 三低{} 大于 平仓值{}'.format(stock,value,sell_value))   
                        sell_list.append(stock)
                    else:
                        print('三低平仓 {} 三低{} 小于 平仓值{}'.format(stock,value,sell_value))   
                #跌出排名卖出N
            rank_df=pd.read_excel(r'{}\三低\三低.xlsx'.format(self.path),dtype='object') 
            sell_rank_stock=rank_df['证券代码'].tolist()[:sell_rank_num]   
            if len(sell_rank_stock)>0:
                for stock in hold_stock_list:
                    if stock in sell_rank_stock:
                        print('{} 在持有排名里面'.format(stock))
                    else:
                        print('{} 不在持有排名里面'.format(stock))
                        sell_list.append(stock)
            sell_list=list(set(sell_list))
            sell_df=pd.DataFrame()
            sell_df['证券代码']=sell_list
            sell_df['交易状态']='未卖'
            if sell_df.shape[0]>0:
                print('卖出etf*****************')
                print(sell_df)
                sell_df['策略名称']=self.name
                sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
            else:
                print('没有卖出etf')
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
            df['证券代码']=df['证券代码']
            print(buy_df)
            buy_df['策略名称']=self.name
            buy_df.to_excel(r'买入股票\买入股票.xlsx')
            return buy_df
        else:
            buy_df=trader_df[:buy_num]
            print(trader_df)
            buy_df['证券代码']=buy_df['证券代码']
            buy_df['交易状态']='未买'
            print('买入etf*****************')
            print(buy_df)
            buy_df['策略名称']=self.name
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
    def updata_all_data(self):
        '''
        更新全部数据
        '''
        with open(r'{}/可转债三低策略设置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        select=text['是否测试']
        if select=='是':
            self.save_position()
            self.save_balance()
            self.get_all_jsl_data()
            self.calculated_double_low()
            self.get_select_trader_type()
            self.get_del_qzsh_data()
            self.get_del_buy_sell_data()
            self.get_buy_sell_stock()
            self.get_del_not_trader_stock()
        else:
            if self.get_time_rotation()==True:
                self.save_position()
                self.save_balance()
                self.get_all_jsl_data()
                print("今天{} 是轮动时间".format(datetime.now()))
                self.calculated_double_low()
                self.get_select_trader_type()
                self.get_del_qzsh_data()
                self.get_del_buy_sell_data()
                self.get_buy_sell_stock()
                self.get_del_not_trader_stock()
            else:
                print("今天{} 不是是轮动时间".format(datetime.now()))