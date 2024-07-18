import datetime
import time
import pandas as pd
import execjs
import os
import json
import requests
from bs4 import BeautifulSoup
from lxml import etree
import os
class jsl_data_xg:
    '''
    获取集思录数据
    '''
    def __init__(self,user, password):
        filename = 'encode_jsl.txt'
        self.user=user
        self.password=password
        self.path=os.path.dirname(os.path.abspath(__file__))
        path = os.path.dirname(os.path.abspath(__file__))
        self.full_path = os.path.join(path, filename)
        self.headers = {
            'Host': 'www.jisilu.cn', 'Connection': 'keep-alive', 'Pragma': 'no-cache',
            'Cache-Control': 'no-cache', 'Accept': 'application/json,text/javascript,*/*;q=0.01',
            'Origin': 'https://www.jisilu.cn', 'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0(WindowsNT6.1;WOW64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/67.0.3396.99Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Referer': 'https://www.jisilu.cn/login/',
            'Accept-Encoding': 'gzip,deflate,br',
            'Accept-Language': 'zh,en;q=0.9,en-US;q=0.8'
        }
        self.session=''
    def decoder(self,text): # 加密用户名和密码
        with open(self.full_path, 'r', encoding='utf8') as f:
            source = f.read()

        ctx = execjs.compile(source)
        key = '397151C04723421F'
        return ctx.call('jslencode', text, key)
    def login(self,): # 登录
        session = requests.Session()
        url = 'https://www.jisilu.cn/account/ajax/login_process/'
        username = self.decoder(self.user)
        jsl_password = self.decoder(self.password)
        data = {
                'return_url': 'https://www.jisilu.cn/',
                'user_name': username,
                'password': jsl_password,
                'net_auto_login': '1',
                '_post_type': 'ajax',
        }

        js = session.post(
            url=url,
            headers=self.headers,
            data=data,
            )
        ret = js.json()
        if ret.get('errno') == 1:
            print('集思录登录成功 账户 {}'.format(self.user))
            self.session=session
            return session
        else:
            print('集思录登录失败 账户 {}'.format(self.user))
            return ''   
    def get_bond_info(self): # 获取行情数据
        ts = int(time.time() * 1000)
        url = 'https://www.jisilu.cn/data/cbnew/cb_list_new/?___jsl=LST___t={}'.format(ts)
        data={
            'fprice':'' ,
            'tprice':'' ,
            'curr_iss_amt':'' ,
            'volume': '',
            'svolume':'' ,
            'premium_rt': '',
            'ytm_rt':'', 
            'rating_cd':'' ,
            'is_search': 'N',
            'market_cd[]': 'shmb',
            'market_cd[]': 'shkc',
            'market_cd[]': 'szmb',
            'market_cd[]': 'szcy',
            'btype':'' ,
            'listed': 'Y',
            'qflag': 'N',
            'sw_cd': '',
            'bond_ids':'' ,
            'rp': '50',
            'page': '0'
        }
        
        r = self.session.post(
            url=url,
            headers=self.headers,
            data=json.dumps(data)
        )
        ret = r.json()
        result = []
        for item in ret['rows']:
            result.append(item['cell'])
        return result
    def get_convert_bond_detail(self,stock='128123'):
        '''
        获取仔细数据
        '''
        '''
        url='https://www.jisilu.cn/data/convert_bond_detail/{}'.format(stock)
        r = self.session.get(
            url=url,
            headers=self.headers,
        )
        ret = r.text
        with open(r'{}\text.html'.format(self.path),'w+',encoding='utf-8') as f:
            f.write(ret)
        '''
        data=pd.DataFrame()
        df=pd.read_html(r'{}\text.html'.format(self.path))
        df1=df[2]
        values_0_0=df1.iloc[0,0].split(' ')
        #可转债代码,行，列
        data['转债名称']=[values_0_0[0]]
        data['转债代码']=[values_0_0[1]]
        data['正股名称']=[values_0_0[6][2:]]
        data['正股代码']=[values_0_0[7]]
        data['行业']=[values_0_0[11]]
        values_1_0=df1.iloc[1,0]
        data['价格']=[values_1_0.split(' ')[-1]]
        values_1_2=df1.iloc[1,2]
        data['转股价值']=[values_1_2.split(' ')[-1]]
        values_1_4=df1.iloc[1,4]
        data['到期税前收益%']=[values_1_4.split(' ')[-1].split('%')[0]]
        values_1_6=df1.iloc[1,6]
        data['成交(万)']=[values_1_6.split(' ')[-1]]
        values_2_0=df1.iloc[2,0]
        data['涨幅%']=[values_2_0.split(' ')[-1].split('%')[0]]
        values_2_2=df1.iloc[2,2]
        data['溢价率%']=[values_2_2.split(' ')[-1].split('%')[0]]
        values_2_4=df1.iloc[2,4]
        data['到期税后收益%']=[values_2_4.split(' ')[-1].split('%')[0]]
        values_2_6=df1.iloc[2,6]
        data['换手率%']=[values_2_6.split(' ')[-1].split('%')[0]]
        values_3_1=df1.iloc[3,1]
        data['起息日']=[values_3_1.split(' ')[-1]]
        print(data)
        

       

       

        



    def adjust_data(x):
        x=str(x)
        if '%' in x:
            return x.replace('%','')
        else:
            return x
    def get_jsl_data(self):
        '''
        获取集思录数据
        '''
        if True:
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            ret = self.get_bond_info()
            df = pd.DataFrame(ret)
            df = df.reset_index()
            '''
            df.rename(
                columns={
                    'index': 'index',
                    'bond_id': '证券代码', 
                    'bond_nm': '可转债名称', 
                    'bond_py': 'bond_py', 
                    'price': '价格', 
                    'increase_rt': '涨跌幅', 
                    'stock_id': '正股代码', 
                    'stock_nm': '正股名称', 
                    'stock_py': 'stock_py', 
                    'sprice': '正股价', 
                    'sincrease_rt': '正股涨跌', 
                    'pb': '正股PB', 
                    'convert_price': '转股价', 
                    'convert_value': '转股价值', 
                    'convert_dt': '转股开始日', 
                    'premium_rt': '转股溢价率', 
                    'bond_premium_rt': '债底溢价率', 
                    'dblow': '双低', 
                    'adjust_condition': '下修状态', 
                    'sw_cd': '申万', 
                    'market_cd': '市场', 
                    'btype': 'btype', 
                    'list_dt': '上市时间', 
                    'owned': 'owned', 
                    'hold': 'hold', 
                    'bond_value': '纯债价值', 
                    'rating_cd': '评级', 
                    'option_value': '期权价值', 
                    'volatility_rate': '正股年化波动率', 
                    'put_convert_price': '回售触发价', 
                    'force_redeem_price': '强赎触发价', 
                    'convert_amt_ratio': '转债占比', 
                    'fund_rt': '机构持仓', 
                    'maturity_dt': '到期时间', 
                    'year_left': '剩余年限', 
                    'curr_iss_amt': '剩余规模', 
                    'volume': '成交额', 
                    'svolume': '正股成交额',
                    'turnover_rt': '换手率', 
                    'ytm_rt': '到期税前收益', 
                    'put_ytm_rt': 'put_ytm_rt', 
                    'notes': 'notes', 
                    'noted':'noted', 
                    'last_time': 'last_time', 
                    'qstatus': 'qstatus', 
                    'sqflag': 'sqflag', 
                    'pb_flag': 'pb_flag', 
                    'adj_cnt': 'adj_cnt', 
                    'adj_scnt': 'adj_scnt', 
                    'convert_price_valid': 'convert_price_valid', 
                    'convert_price_tips': 'convert_price_tips', 
                    'convert_cd_tip': 'convert_cd_tip', 
                    'ref_yield_info': 'ref_yield_info', 
                    'adjusted': 'adjusted', 
                    'orig_iss_amt': '发行规模', 
                    'price_tips': 'price_tips', 
                    'redeem_dt': 'redeem_dt', 
                    'real_force_redeem_price': 'real_force_redeem_price', 
                    'option_tip': 'option_tip', 
                    'adjust_status': 'adjust_status', 
                    'unadj_cnt': 'unadj_cnt', 
                    'after_next_put_dt': 'after_next_put_dt', 
                    'adjust_remain_days': 'adjust_remain_days', 
                    'adjust_orders': 'adjust_orders', 
                    'icons': 'icons'
                    },inplace=True)
            '''
            df.rename(
                columns={
                    "bond_id":"代码",
                    "bond_nm":"转债名称",
                    "price":"现价",
                    "increase_rt":"涨跌幅",
                    "stock_id":"正股代码",
                    "stock_nm":"正股名称",
                    "sprice":"正股价",
                    "sincrease_rt":"正股涨跌",
                    "pb":"正股PB",
                    "convert_price":"转股价",
                    "convert_value":"转股价值",
                    "premium_rt":"转股溢价率",
                    "bond_premium_rt":"债低溢价率",
                    "dblow":"双低",
                    "list_dt":"上市时间",
                    "bond_value":"纯债价值",
                    "rating_cd":"债券评级",
                    "volatility_rate":"正股波动率",
                    "put_convert_price":"回售触发价",
                    "force_redeem_price":"强赎触发价",
                    "convert_amt_ratio":"可转债占比",
                    "fund_rt":"基金持仓",
                    "maturity_dt":"到期时间",
                    "year_left":"剩余年限",
                    "curr_iss_amt":"剩余规模(亿元)",
                    "volume":"成交额(万元)",
                    "turnover_rt":"换手率",
                    "ytm_rt":"到期税前收益",
                    "last_time":"更新时间",
                    'svolume': '正股成交额',
                    'option_value': '期权价值',

                },inplace=True
            )
            return df           
if __name__=='__main__':
    models=jsl_data_xg('','')
    models.login()
    print('))))))))))))))))))')
    print(models.get_convert_bond_detail(()))