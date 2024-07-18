import requests
import time
import pandas as pd
import numpy as np
import json
import yagmail
from datetime import datetime
import warnings
#通达信指标
warnings.filterwarnings(action='ignore')
import requests
from finta import TA
from tqdm import tqdm
from qmt_trader.tdx_data import tdx_data
from qmt_trader.qmt_data import qmt_data
#股票核心数据
class stock_data_qmt:
    def __init__(self,qq='1029762153@qq.com'):
        self.qq=qq
        self.tdx_data=tdx_data()
        self.tdx_data.connect()
        self.qmt_data=qmt_data()
        #self.qmt_all_data=self.qmt_data.get_all_data()
    def rename_stock_type_1(self,stock='600031'):
        '''
        将股票类型格式化
        stock证券代码
        1上海
        0深圳
        '''
        if stock[:3] in ['600','601','603','688','510','511',
                            '512','513','515','113','110','118','501'] or stock[:2] in ['11']:
            marker=1
        else:
            marker=0
        return marker,stock
    def get_stock_hist_data_em(self,stock='600031',start_date='20210101',end_date='20500101',data_type='D',count=8000):
        '''
        获取股票数据
        start_date=''默认上市时间
        - ``1`` : 分钟
            - ``5`` : 5 分钟
            - ``15`` : 15 分钟
            - ``30`` : 30 分钟
            - ``60`` : 60 分钟
            - ``101`` : 日
            - ``102`` : 周
            - ``103`` : 月
        fq=0股票除权
        fq=1前复权
        fq=2后复权
        '''
        try:
            stock=str(stock)[:6]
            data_dict = {'1': '1', '5': '5', '15': '15', '30': '30', '60': '60', 'D': '101', 'W': '102', 'M': '103'}
            klt=data_dict[data_type]
            klt=data_dict[data_type]
            secid='{}.{}'.format(0,stock)
            url = 'http://push2his.eastmoney.com/api/qt/stock/kline/get?'
            params = {
                'fields1': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'beg': start_date,
                'end': end_date,
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                'rtntype':end_date,
                'secid': secid,
                'klt':klt,
                'fqt': '1',
                'cb': 'jsonp1668432946680'
            }
            res = requests.get(url=url, params=params)
            text = res.text[19:len(res.text) - 2]
            json_text = json.loads(text)
            df = pd.DataFrame(json_text['data']['klines'])
            df.columns = ['数据']
            data_list = []
            for i in df['数据']:
                data_list.append(i.split(','))
            data = pd.DataFrame(data_list)
            columns = ['date', 'open', 'close', 'high', 'low', 'volume', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
            data.columns = columns
            for m in columns[1:]:
                data[m] = pd.to_numeric(data[m])
            data.sort_index(ascending=True,ignore_index=True,inplace=True)
            return data
        except:
            try:
                stock=str(stock)[:6]
                data_dict = {'1': '1', '5': '5', '15': '15', '30': '30', '60': '60', 'D': '101', 'W': '102', 'M': '103'}
                klt=data_dict[data_type]
                klt=data_dict[data_type]
                secid='{}.{}'.format(1,stock)
                url = 'http://push2his.eastmoney.com/api/qt/stock/kline/get?'
                params = {
                    'fields1': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13',
                    'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                    'beg': start_date,
                    'end': end_date,
                    'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                    'rtntype':end_date,
                    'secid': secid,
                    'klt':klt,
                    'fqt': '1',
                    'cb': 'jsonp1668432946680'
                }
                res = requests.get(url=url, params=params)
                text = res.text[19:len(res.text) - 2]
                json_text = json.loads(text)
                df = pd.DataFrame(json_text['data']['klines'])
                df.columns = ['数据']
                data_list = []
                for i in df['数据']:
                    data_list.append(i.split(','))
                data = pd.DataFrame(data_list)
                columns = ['date', 'open', 'close', 'high', 'low', 'volume', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
                data.columns = columns
                for m in columns[1:]:
                    data[m] = pd.to_numeric(data[m])
                data.sort_index(ascending=True,ignore_index=True,inplace=True)
                return data
            except Exception as e:
                print("运行错误:",e)
                stock=self.qmt_data.adjust_stock(stock)
                data1=self.qmt_all_data.get_market_data_ex(stock_list=[stock])
                data1=data1[stock]
                if data1.shape[0]>0:
                    return data1
                else:
                    '''
                    0 5分钟K线
                    1 15分钟K线 
                    2 30分钟K线 
                    3 1小时K线 
                    4 日K线
                    7 1分钟
                    8 1分钟K线
                    '''
                    data_dict = {'1': '8', '5': '0', '15': '1', '30': '2', '60': '3', 'D': '4', '7': '7',}
                    n=data_dict[data_type]
                    data=self.tdx_data.get_security_minute_data(stock=stock,n=n,count=count)
                    data['date']=data['datetime'].apply(lambda x:str(x)[:10])
                    data['volume']=data['vol']
                    data['涨跌幅']=data['close'].pct_change()*100
                    data['涨跌额']=data['close']-data['open']
                    data['振幅']=(data['high']-data['low'])/data['low']*100
                    return data
    def get_stock_all_trader_data(self,stock='600031'):
        '''
        获取股票全部分时交易数据
        备用
        :param stock:
        :return:
        '''
        try:
            url='http://push2ex.eastmoney.com/getStockFenShi?'
            params = {
                'pagesize': '10000',#144
                'ut': '7eea3edcaed734bea9cbfc24409ed989',
                'dpt': 'wzfscj',
                'cb': 'jQuery1124032472207483171633_1633697823102',
                'pageindex': '0',
                'id': '{}'.format(stock,0),
                'sort': '1',
                'ft': '1',
                'code': '{}'.format(stock),
                'market': '{}'.format(0),
                '_': '1633697823103'
            }
            res=requests.get(url=url,params=params)
            text=res.text[43:len(res.text)-2]
            json_text=json.loads(text)
            df=pd.DataFrame(json_text['data']['data'])
            columns=['date','价格','成交量','性质']
            df.columns=columns
            df['价格']=df['价格']/1000
            df['close']=df['价格']
            df['实时涨跌幅']=df['价格'].pct_change()
            spot_data=self.get_stock_spot_data(stock=stock)['昨收']
            df['涨跌幅']=((df['价格']-spot_data)/spot_data)*100
            def select_stock(x):
                    if x==2:
                        return '买盘'
                    elif x==1:
                        return '卖盘'
                    else:
                        return x
            df['性质']=df['性质'].apply(select_stock)
            return df
        except:
            try:
                url='http://push2ex.eastmoney.com/getStockFenShi?'
                params = {
                    'pagesize': '10000',#144
                    'ut': '7eea3edcaed734bea9cbfc24409ed989',
                    'dpt': 'wzfscj',
                    'cb': 'jQuery1124032472207483171633_1633697823102',
                    'pageindex': '0',
                    'id': '{}'.format(stock,1),
                    'sort': '1',
                    'ft': '1',
                    'code': '{}'.format(stock),
                    'market': '{}'.format(1),
                    '_': '1633697823103'
                }
                res=requests.get(url=url,params=params)
                text=res.text[43:len(res.text)-2]
                json_text=json.loads(text)
                df=pd.DataFrame(json_text['data']['data'])
                columns=['date','价格','成交量','性质']
                df.columns=columns
                df['价格']=df['价格']/1000
                df['close']=df['价格']
                df['实时涨跌幅']=df['价格'].pct_change()
                spot_data=self.get_stock_spot_data(stock=stock)['昨收']
                df['涨跌幅']=((df['价格']-spot_data)/spot_data)*100
                def select_stock(x):
                        if x==2:
                            return '买盘'
                        elif x==1:
                            return '卖盘'
                        else:
                            return x
                df['性质']=df['性质'].apply(select_stock)
                return df
            except Exception as e:
                print("运行错误:",e)
                data=self.tdx_data.get_trader_data(stock=stock,start=0,count=9000)
                data['价格']=data['price']/10
                data['涨跌幅']=(data['价格'].pct_change()*100).cumsum()
                data['实时涨跌幅']=data['涨跌幅']-data['涨跌幅'].shift(1)
                return data
    def seed_emial_qq(self,text='交易完成'):
        with open('分析配置.json','r+',encoding='utf-8') as f:
            com=f.read()
        text1=json.loads(com)
        try:
            password=text1['qq掩码']
            seed_qq=text1['发送qq']
            yag = yagmail.SMTP(user='{}'.format(seed_qq), password=password, host='smtp.qq.com')
            m = self.qq
            text = text
            yag.send(to=m, contents=text, subject='邮件')
            print('邮箱发生成功')
        except Exception as e:
            print("运行错误:",e)
            print('qq发送失败可能用的人多')
    def get_trader_date_list(self):
        '''
        获取交易日历
        :return:
        '''
        df=self.get_stock_hist_data_em()
        date_list=df['date'].tolist()
        return date_list
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
        trader_time=text['交易时间段']
        start_date=text['交易开始时间']
        end_date=text['交易结束时间']
        start_mi=text['开始交易分钟']
        jhjj=text['是否参加集合竞价']
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
    def get_stock_spot_data(self,stock='002858'):
        '''
        获取股票实时数据
        '''
        try:
            stock=str(stock)[:6]
            secid='{}.{}'.format(0,stock)
            params={
                'invt':'2',
                'fltt':'1',
                'cb':'jQuery3510180390237681324_1685191053405',
                'fields':'f58,f107,f57,f43,f59,f169,f170,f152,f46,f60,f44,f45,f47,f48,f161,f49,f171,f50,f86,f177,f111,f51,f52,f168,f116,f117,f167,f162,f262',
                'secid': secid,
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                'wbp2u': '1452376043169950|0|1|0|web',
                '_': '1685191053406',
            }
            url='http://push2.eastmoney.com/api/qt/stock/get?'
            res=requests.get(url=url,params=params)
            text=res.text
            text=text[40:len(text)-2]
            json_text=json.loads(text)
            data=json_text['data']
            result={}
            result['最新价']=data['f43']/100
            result['最高价']=data['f44']/100
            result['最低价']=data['f45']/100
            result['今开']=data['f46']/100
            result['成交量']=data['f47']
            result['成交额']=data['f48']
            result['量比']=data['f50']/100
            result['涨停']=data['f51']/100
            result['跌停']=data['f52']/100
            result['证券代码']=data['f57']
            result['股票名称'] = data['f58']
            result['昨收']=data['f60']/100
            result['总市值']=data['f116']
            result['流通市值']=data['f117']
            result['换手率']=data['f168']/100
            result['涨跌幅']=data['f170']/100
            return result
        except:
            try:
                stock=str(stock)[:6]
                secid='{}.{}'.format(1,stock)
                params={
                    'invt':'2',
                    'fltt':'1',
                    'cb':'jQuery3510180390237681324_1685191053405',
                    'fields':'f58,f107,f57,f43,f59,f169,f170,f152,f46,f60,f44,f45,f47,f48,f161,f49,f171,f50,f86,f177,f111,f51,f52,f168,f116,f117,f167,f162,f262',
                    'secid': secid,
                    'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                    'wbp2u': '1452376043169950|0|1|0|web',
                    '_': '1685191053406',
                }
                url='http://push2.eastmoney.com/api/qt/stock/get?'
                res=requests.get(url=url,params=params)
                text=res.text
                text=text[40:len(text)-2]
                json_text=json.loads(text)
                data=json_text['data']
                result={}
                result['最新价']=data['f43']/100
                result['最高价']=data['f44']/100
                result['最低价']=data['f45']/100
                result['今开']=data['f46']/100
                result['成交量']=data['f47']
                result['成交额']=data['f48']
                result['量比']=data['f50']/100
                result['涨停']=data['f51']/100
                result['跌停']=data['f52']/100
                result['证券代码']=data['f57']
                result['股票名称'] = data['f58']
                result['昨收']=data['f60']/100
                result['总市值']=data['f116']
                result['流通市值']=data['f117']
                result['换手率']=data['f168']/100
                result['涨跌幅']=data['f170']/100
                return result
            except Exception as e:
                try:
                    print("运行错误:",e)
                    json_text=self.tdx_data.get_security_quotes_none(stock=stock)
                    data_dict={}
                    data_dict['最新价']=json_text['price'].tolist()[-1]
                    data_dict['最高价']=json_text['high'].tolist()[-1]
                    data_dict['最低价']=json_text['low'].tolist()[-1]
                    data_dict['今开']=json_text['open'].tolist()[-1]
                    data_dict['涨跌幅']=((data_dict['最新价']-data_dict['今开'])/data_dict['今开'])*100
                    return data_dict
                except Exception as e:
                    result={}
                    stock_1=stock
                    stock_1=str(stock)+'.SH'
                    text=self.qmt_data.get_full_tick(code_list=[stock_1])
                    text=text[stock_1]
                    if len(text)>0:
                        result['最新价']=text['lastPrice']
                        result['最高价']=text['high']
                        result['最低价']=text['low']
                        result['开盘价']=text['open']
                        result['金额']=text['amount']
                        result['涨跌幅']=((text['lastPrice']-text['open'])/text['open'])*100
                        return result
                    else:
                        stock=str(stock)[:6]+'.SZ'

                        text=self.qmt_data.get_full_tick(code_list=[stock_1])
                        text=text[stock_1]
                        result['最新价']=text['lastPrice']
                        result['最高价']=text['high']
                        result['最低价']=text['low']
                        result['开盘价']=text['open']
                        result['金额']=text['amount']
                        result['涨跌幅']=((text['lastPrice']-text['open'])/text['open'])*100
                        return result
                
if __name__=='__main__':
    a=stock_data_qmt()
    a.check_is_trader_date_1()








