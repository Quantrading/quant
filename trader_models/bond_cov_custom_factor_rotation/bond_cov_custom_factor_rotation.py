from .user_def_factor_data import user_def_factor_data
from  trader_tool.stock_data import stock_data
from trader_tool.bond_cov_data import bond_cov_data
from trader_tool.etf_fund_data import etf_fund_data
from trader_tool.trader_frame import trader_frame
from trader_tool.shape_analysis import shape_analysis
from trader_tool.ths_rq import ths_rq
import pandas as pd
from tqdm import tqdm
import numpy as np
import json
from trader_tool import jsl_data
import os
from datetime import datetime
import time
class bond_cov_custom_factor_rotation:
    def __init__(self,trader_tool='ths',exe='C:/同花顺软件/同花顺/xiadan.exe',tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qq='1029762153@qq.com',open_set='否',qmt_path='D:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55009640',qmt_account_type='STOCK',name='run_bond_cov_custom_factor_rotation'):
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
        self.ths_rq=ths_rq()
        self.bond_cov_data=bond_cov_data()
        self.stock_data=stock_data()
        self.etf_fund_data=etf_fund_data()
        self.user_factor=user_def_factor_data()
        self.name=name
    def save_position(self):
        '''
        保存持股数据
        '''
        with open(r'{}/可转债自定义因子轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        df=self.trader.position()
        def select_bond_cov(x):
            '''
            选择可转债
            '''
            if x[:3] in ['110','113','123','127','128','111','118']:
                return '是'
            else:
                return '不是'
        try:
            if df==False:
                print('获取持股失败')
        except Exception as e:
            print("运行错误:",e)
            if df.shape[0]>0:
                df['选择']=df['证券代码'].apply(select_bond_cov)
                try:
                    df['持股天数']=df['持股天数'].replace('--',1)
                except Exception as e:
                    print("运行错误:",e)
                    df['持股天数']=1
                df1=df[df['选择']=='是']
                df1['交易状态']='未卖'
                df1=df1[df1['可用余额']>=10]
                df1.to_excel(r'持股数据\持股数据.xlsx')
                return df1
            else:
                print('没有持股')
    def save_position_1(self):
        '''
        保存持股数据
        '''
        with open(r'{}/可转债自定义因子轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        df=self.trader.position()
        print(df)
        def select_bond_cov(x):
            '''
            选择可转债
            '''
            if x[:3] in ['110','113','123','127','128','111'] or x[:2] in ['11','12']:
                return '是'
            else:
                return '不是'
        try:
            if df==False:
                print('获取持股失败')
        except Exception as e:
            print("运行错误:",e)
            if df.shape[0]>0:
                df['选择']=df['证券代码'].apply(select_bond_cov)
                try:
                    df['持股天数']=df['持股天数'].replace('--',1)
                except Exception as e:
                    print("运行错误:",e)
                    df['持股天数']=1
                df1=df[df['选择']=='是']
                df1=df1[df1['可用余额']>=10]
                df1['交易状态']='未卖'
                #df1.to_excel(r'持有可转债\持有可转债.xlsx')
                df1.to_excel(r'持股数据\持股数据.xlsx')
                return df1
            else:
                print('没有持股')
    def select_bond_cov(self,x):
        '''
        选择证券代码
        '''
        if x[:3] in ['110','113','123','127','128','111']:
            return '是'
        else:
            return '不是'
    def save_balance(self):
        '''
        保持账户数据
        '''
        with open(r'{}/可转债自定义因子轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        df=self.trader.balance()
        df.to_excel(r'账户数据\账户数据.xlsx')
        return df
    def get_ths_rq_data(self):
        '''
        获取同花顺人气数据
        '''
        df=self.ths_rq.get_cov_bond_rot_rank()
        df.to_excel(r'{}\同花顺人气原始数据\同花顺人气原始数据.xlsx'.format(self.path))
        print(df)
    def get_all_jsl_data(self):
        '''
        获取可转债全部数据
        '''
        with open('{}/可转债自定义因子轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        user=text['集思录账户']
        password=text['集思录密码']
        df=jsl_data.get_all_cov_bond_data(jsl_user=user,jsl_password=password)
        df.to_excel(r'{}\默认因子数据\默认因子数据.xlsx'.format(self.path))
        return df
    def get_concact_data(self):
        '''
        获取合并数据,默认因子合并
        把股票默认因子
        '''
        df=pd.read_excel(r'{}\默认因子数据\默认因子数据.xlsx'.format(self.path),dtype='object')
        try:
            del df['Unnamed: 0']
        except Exception as e:
            print("运行错误:",e)
        df['正股代码']=df['正股代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
        stock_list=df['正股代码'].tolist()
        all_df=pd.DataFrame()
        for i in tqdm(range(len(stock_list))):
            stock=stock_list[i]
            try:
                df1=self.stock_data.get_stock_spot_data_1(stock=stock)
                all_df=pd.concat([all_df,df1])
            except Exception as e:
                print("运行错误:",e)
                print('{}数据有问题'.format(stock))
                df1=pd.DataFrame()
                all_df=pd.concat([all_df,df1])
        
        all_df.to_excel(r'{}\股票默认因子\股票默认因子.xlsx'.format(self.path))
        df.reset_index(inplace=True)
        all_df.reset_index(inplace=True)
        df=pd.concat([df,all_df],axis=1)
        df.to_excel(r'{}\默认因子数据\默认因子数据.xlsx'.format(self.path))
        return df
    def get_concact_user_factor_data(self):
        '''
        合并自定义因子数据
        '''
        with open('{}/可转债自定义因子轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        text1=text['自定义因子函数']
        #自定义因子名称
        user_factor_name=list(text1.keys())
        if len(user_factor_name)<1:
            print('没有自定义因子')
            df=pd.DataFrame()
            df.to_excel(r'{}\自定义因子数据\自定义因子数据.xlsx'.format(self.path))
        else:
            #自定义因子函数
            user_factor_func=list(text1.values())
            user_factor_func_list=[]
            for func in user_factor_func:
                user_factor_func_list.append(func[0])
            df=pd.read_excel(r'{}\默认因子数据\默认因子数据.xlsx'.format(self.path),dtype='object')
            try:
                del df['Unnamed: 0']
            except Exception as e:
                print("运行错误:",e)
            stock_list=df['正股代码'].tolist()
            bond_list=df['证券代码'].tolist()
            all_df=pd.DataFrame()
            for j in tqdm(range(len(stock_list))):
                factor_df=pd.DataFrame()
                stock_1,stock_2=stock_list[j],bond_list[j]
                for i in range(len(user_factor_name)):
                    name=user_factor_name[i]
                    func=user_factor_func_list[i]
                    if name[:2]=='股票':
                        stock=stock_1
                        factor_type,factor_value=eval('self.user_factor.'+func)
                        factor_df['因子代码']=[stock]
                        factor_df[name]=[factor_value]
                    else:
                        stock=stock_2
                        factor_type,factor_value=eval('self.user_factor.'+func)
                        factor_df['因子代码']=[stock]
                        factor_df[name]=[factor_value]
                all_df=pd.concat([all_df,factor_df],ignore_index=True)
            all_df.to_excel(r'{}\自定义因子数据\自定义因子数据.xlsx'.format(self.path))
            return all_df
    def get_concat_all_factor_data(self):
        '''
        连接全部因子数据
        '''
        #默认因子
        df1=pd.read_excel(r'{}\默认因子数据\默认因子数据.xlsx'.format(self.path),dtype='object')
        try:
            del df1['Unnamed: 0']
            del df1['level_0']
        except:
            pass
        #自定义因子
        df2=pd.read_excel(r'{}\自定义因子数据\自定义因子数据.xlsx'.format(self.path),dtype='object')
        try:
            del df2['Unnamed: 0']
        except:
            pass
        df1.reset_index(inplace=True)
        df2.reset_index(inplace=True)
        df=pd.concat([df1,df2],axis=1)
        df.to_excel(r'{}\全部因子数据\全部因子数据.xlsx'.format(self.path))
        return df
    def cacal_ys_user_factor_data(self):
        '''
        衍生因子计算
        '''
        with open('{}/可转债自定义因子轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        is_ys=text['是否开启衍生因子']
        if is_ys=='是':
            print('开启衍生因子计算')
            ys_factor_dict=text['自定义衍生因子函数']
            if len(ys_factor_dict)>0:
                name_list=list(ys_factor_dict.keys())
                func_list=list(ys_factor_dict.values())
                for name,func in zip(name_list,func_list):
                    print('自定义衍生因子{}'.format(name))
                    text='self.user_factor.{}'.format(func)
                    eval(text)
            else:
                print('没有自定义衍生因子')
        else:
            print('不开启衍生因子计算')
    def get_select_trader_bond_cov_data(self):
        '''
        选择交易的可转债数据
        '''
        with open('{}/可转债自定义因子轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        weight_dict=text['打分因子']
        df=pd.read_excel(r'{}\全部因子数据\全部因子数据.xlsx'.format(self.path),dtype='object')
        for i in df.columns.tolist():
            try:
                df[i]=pd.to_numeric(df[i])
            except:
                pass
        #选择默认因子
        try:
            del df['Unnamed: 0']
        except:
            pass
        mr_factor=text['排除因子']
        text1=text['自定义因子函数']
        mr_factor_keys=list(mr_factor.keys())
        if len(mr_factor_keys)<0:
            print('没有默认因子______________排除')
        else:
            for keys in mr_factor_keys:
                try:
                    min_value=mr_factor[keys][0]
                    max_value=mr_factor[keys][1]
                    df[keys]=df[keys].astype(float)
                    df=df[df[keys]>=min_value]
                    df=df[df[keys]<=max_value]
                except Exception as e:
                    print("运行错误:",e)
                    print('非数字选择****************************************')
                    select_list=mr_factor[keys]
                    print(select_list)
                    df['非数字选择']=df[keys].apply(lambda x:'是' if x in select_list else '不是')
                    df=df[df['非数字选择']=='不是']
        print(df)
        #选择自定义因子
        #自定义因子名称
        user_factor_name=list(text1.keys())
        if len(user_factor_name)<1:
            print('没有自定义因子————————————排除')
        else:
            #自定义因子函数
            for name in user_factor_name:
                try:
                    min_value=text1[name][1][0]
                    max_value=text1[name][1][1]
                    df=df[df[name]>=min_value]
                    df=df[df[name]<=max_value]
                except:
                    select_list=text1[name]
                    df['非数字选择']=df[name].apply(lambda x:'是' if str(x) in select_list else '不是')
                    df=df[df['非数字选择']=='不是']
        df.to_excel(r'{}\排除因子\排除因子.xlsx'.format(self.path))
        return df
    def get_score_factor_data(self):
        '''
        获取交易模式
        '''
        with open('{}/可转债自定义因子轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        df=pd.read_excel(r'{}\排除因子\排除因子.xlsx'.format(self.path),dtype='object')
        text=json.loads(com)
        trader_models=text['交易模式']
        score_dict=text['打分因子']
        select_columns=list(score_dict.keys())
        if trader_models=='默认':
            score_name=[]
            for i in select_columns:
                weight=score_dict[i]
                df[i]=df[i].astype(float)
                df['{}得分'.format(i)]=df[i]*weight
                score_name.append('{}得分'.format(i))
            df['得分']=df[score_name].sum(axis=1).tolist()
            df=df.sort_values(by='得分',ascending=True)
            df.to_excel(r'{}\默认打分因子\默认打分因子.xlsx'.format(self.path))
            df.to_excel(r'{}\打分因子\打分因子.xlsx'.format(self.path))
        else:
            #禄得老师的计算方式单因子排序加起来
            score_name=[]
            for i in select_columns:
                weight=score_dict[i]
                df[i]=df[i].astype(float)
                df['{}得分'.format(i)]=df[i].rank(ascending=False)*weight
                score_name.append('{}得分'.format(i))
            df['得分']=df[score_name].sum(axis=1).tolist()
            df=df.sort_values(by='得分',ascending=False)
            df.to_excel(r'{}\禄得打分因子\禄得打分因子.xlsx'.format(self.path))   
            df.to_excel(r'{}\打分因子\打分因子.xlsx'.format(self.path))
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
        df=pd.read_excel(r'{}\打分因子\打分因子.xlsx'.format(self.path),dtype='object')
        with open(r'{}/可转债自定义因子轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
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
            except Exception as e:
                print("运行错误:",e)
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
        with open(r'{}/可转债自定义因子轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
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
        with open(r'{}\可转债自定义因子轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        rend=text['是否开启趋势轮动']
        if rend=='是':
            self.get_cov_bond_shape_analysis()
            self.get_stock_mean_line_retuen_analysis()
        else:
            df=pd.read_excel(r'{}\打分因子\打分因子.xlsx'.format(self.path),dtype='object')
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
        with open('{}/可转债自定义因子轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
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
        with open(r'{}/可转债自定义因子轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
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
            for stock in hold_stock_list:
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
        with open('{}/可转债自定义因子轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
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
        with open('{}/可转债自定义因子轮动交易配置.json'.format(self.path),encoding='utf-8') as f:
            com=f.read()
        text=json.loads(com)
        buy_num=text['买入排名前N']
        hold_rank_num=text['持有排名前N']
        sell_rank_num=text['跌出排名卖出N']
        hold_limit=text['持有限制']
        df=pd.read_excel(r'持股数据\持股数据.xlsx',dtype='object')
        df['证券代码']=df['证券代码'].astype(str)
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
            #跌出排名卖出N
            rank_df=pd.read_excel(r'{}\交易股票池\交易股票池.xlsx'.format(self.path),dtype='object') 
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
                print('卖出可转债*****************')
                print(sell_df)
                sell_df['策略名称']=self.name
                sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
            else:
                print('没有卖出的可转债')
                sell_df=pd.DataFrame()
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
            buy_df['证券代码']=buy_df['证券代码']
            buy_df['交易状态']='未买'
            print('买入可转债*****************')
            print(buy_df)
            buy_df['策略名称']=self.name
            buy_df.to_excel(r'买入股票\买入股票.xlsx')
            print('没有卖出的可转债')
            sell_df=pd.DataFrame()
            sell_df['证券代码']=None
            sell_df['交易状态']=None
            sell_df['策略名称']=self.name
            sell_df.to_excel(r'卖出股票\卖出股票.xlsx')
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
            if del_df.shape[0]>0:
                del_df['证券代码']=del_df['证券代码'].apply(lambda x : str(x).split('.')[0])
                del_df['证券代码']=del_df['证券代码'].apply(lambda x: '0'*(6-len(str(x)))+str(x))
                del_stock_list=del_df['证券代码'].tolist()
            else:
                del_stock_list=[]
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
        if self.get_time_rotation()==True:
            print("今天{} 是轮动时间".format(datetime.now()))
            self.save_position()
            self.save_balance()
            self.get_all_jsl_data()
            self.get_ths_rq_data()
            self.get_concact_data()
            self.get_concact_user_factor_data()
            self.get_concat_all_factor_data()
            self.cacal_ys_user_factor_data()
            self.get_select_trader_bond_cov_data()
            self.get_score_factor_data()
            self.get_select_trader_type()
            self.get_del_qzsh_data()
            self.get_buy_sell_stock()
            self.get_del_not_trader_stock()

        else:
            print("今天{} 不是是轮动时间".format(datetime.now()))

