import pandas as pd 
import numpy as np
import warnings
import empyrical
import matplotlib.pyplot as plt
# 支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
from trader_tool.index_data import index_data
print('导入包完成!')
### 因子分析工具
class factor_analysis_frame(object):
    def __init__(self, params, factor_data,factor_return):

        # params: 字典格式。 形如 params = {'group_num':5, 'factor_field':'hf_fz_ykws', 'instruments':'全市场', 'factor_direction':1} 
        # group_num:分组数量
        # factor_field:因子在表中所对应的字段名称
        # instruments:标的池
        # factor_direction：因子方向，字符串格式，取值为1、-1。1表示因子方向为正，因子值越大越好，-1表示因子值为负，因子值越小越好。

        # factor_data:pandas.DataFrame格式,形如
        #   instrument	date	    hf_fz_ykws
        # 0	000001.SZ	2017-01-03	1.564644
        # 1	000001.SZ	2017-01-04	1.521567
        # 2	000001.SZ	2017-01-05	1.519973
        # 3	000001.SZ	2017-01-06	1.553225
        # 4	000001.SZ	2017-01-09	1.367971
        # 其中, instrument:str ,以股票代码+.sh（沪市） +.SZ（深市）
        #     date:datetime64 
        #     hf_fz_ykws:float64
        self.data=index_data()
        self.params = params
        self.top_n_ins = 5 # 默认5只
        self.factor_data = factor_data.rename(columns={self.params['factor_field']:'factor'}) 
        #print(self.factor_data)
        self.factor_data['factor'] *= self.params['factor_direction']

        # 检查因子数据格式
        '''
        try:
            self.check_data_format(self.factor_data)
            print("数据格式检查通过")
        except ValueError as e:
            print("数据格式检查失败：" + str(e))
        '''

        self.start_date = self.factor_data.date.min().strftime('%Y-%m-%d')
        self.end_date =  self.factor_data.date.max().strftime('%Y-%m-%d')

        #self.price_data =  self.get_daily_ret(self.start_date, self.end_date) # 日收益率数据
        self.price_data=factor_return
        print('个股日收益率计算完成')
        self.merge_data = pd.merge(self.factor_data.sort_values(['date', 'instrument']), \
                                   self.price_data.sort_values(['date', 'instrument']), on=['date','instrument'], how='left')
        self.group_data = self.get_group_data()  # 分组数据
        print('因子分组完成')
        self.bm_ret = self.get_bm_ret(self.params['benchmark'])
        print('基准日收益率计算完成')
        self.group_cumret = self.get_group_cumret()  # 分组累积收益率
        print('分组收益率计算完成')
        self.whole_perf = self.get_whole_perf()   # 整体绩效指标 
        print('整体绩效计算完成')
        self.yearly_perf =  self.get_yearly_perf() # 按年度绩效指标
        print('年度绩效计算完成')
        self.ic = self.get_IC_data('all')  # ic指标
        print('IC计算完成')

    def check_data_format(self, df):
        # 检查date列是否是日期型类型
        if df['date'].dtype != 'datetime64[ns]':
            raise ValueError("date列的数据格式应为datetime格式")
        # 检查instrument列是否是以SZ\SH结尾
        if not all(df['instrument'].str.endswith('.SH') | df['instrument'].str.endswith('.SZ') | df['instrument'].str.endswith('.BJ')):
            raise ValueError("instrument列的数据格式应为以.SH或.SZ或.BJ结尾的字符串")
        # 检查factor列是否是浮点型数值
        if df['factor'].dtype != 'float64':
            raise ValueError("factor列的数据格式应为浮点型")

    def get_daily_ret(self, start_date, end_date):
        """计算收益率. T0的因子对应的收益率是T+1日开盘买入,T+2开盘卖出"""
        sql = f"SELECT instrument,date, (m_lead(open, 2)/ m_lead(open, 1) - 1) AS daily_ret from cn_stock_bar1d ORDER BY date, instrument;"
        
        from datetime import datetime, timedelta
        ten_days_ago_start_date = pd.Timestamp(self.start_date) - timedelta(days=10) # 往前多取10天数据
        ten_days_ago_start_date = ten_days_ago_start_date.strftime('%Y-%m-%d')

        price_data = dai.query(sql, filters={"date": [ten_days_ago_start_date, self.end_date]}).df()
        return price_data

    def get_group_data(self):
        """因子分组，因子值越大，组数越大，默认的多头组合是因子数值最大的组合"""
        def cut(df, group_num=10):
            """分组"""
            df['group'] = pd.qcut(df['factor'], q=group_num, labels=False, duplicates='drop')
            df = df.dropna(subset=['group'], how='any')
            df['group'] =  df['group'].apply(int).apply(str)
            return df

        group_data = self.merge_data.groupby('date', group_keys=False).apply(cut, group_num=self.params['group_num'])
        return group_data

    def get_bm_ret(self, benchmark='000852.SHI'):
        # 获取基准日收益率数据
        bm_ret=self.data.get_index_hist_data(stock=self.params['benchmark'],start_date='18000101',end_date='20500101')
        bm_ret=bm_ret[-self.price_data.shape[0]:]
        bm_ret['benchmark_ret']=bm_ret['close'].pct_change()
        return bm_ret

    def get_group_cumret(self):
        # 分组收益率
        groupret_data = self.group_data[['date','group','daily_ret']].groupby(['date','group'], group_keys=False).apply(lambda x:np.nanmean(x)).reset_index()
        groupret_data.rename(columns={0:'g_ret'}, inplace=True)

        groupret_pivotdata = groupret_data.pivot(index='date', values='g_ret', columns='group')
        groupret_pivotdata['ls'] = groupret_pivotdata['{0}'.format(self.params['group_num']-1)] - groupret_pivotdata['0']  # 日收益率

        bm_ret = self.bm_ret.set_index('date') # 基准收益率
        groupret_pivotdata['bm'] = bm_ret['benchmark_ret'] 
        groupret_pivotdata = groupret_pivotdata.shift(1) # 首日为nan，最后一日有值
        self.groupret_pivotdata = groupret_pivotdata
        
        groupcumret_pivotdata = groupret_pivotdata.cumsum() # 单利下的累积收益率
        return groupcumret_pivotdata.round(4) # 数值型数据都是保留到小数点后四位 

    def get_Performance(self, data_type):
        def get_stats(series, bm_series):
            """
            series是日收益率数据, pandas.series 
            data_type是组合类型, 'long'、'short'、'long_short'
            """
            return_ratio =  series.sum() # 总收益
            annual_return_ratio = series.sum() * 242 / len(series)  #  年度收益

            ex_return_ratio =  (series-bm_series).sum() # 超额总收益
            ex_annual_return_ratio =  (series-bm_series).sum() * 242 / len( (series-bm_series))  #  超额年度收益
            
            sharp_ratio = empyrical.sharpe_ratio(series, 0.035/242)
            return_volatility = empyrical.annual_volatility(series)
            max_drawdown  = empyrical.max_drawdown(series)
            information_ratio=series.mean()/series.std()
            win_percent = len(series[series>0]) / len(series)
            trading_days = len(series)

            series = series.fillna(0)
            ret_3 = series.rolling(3).sum().iloc[-1]
            ret_10 = series.rolling(10).sum().iloc[-1]
            ret_21 = series.rolling(21).sum().iloc[-1]
            ret_63 = series.rolling(63).sum().iloc[-1]
            ret_126 = series.rolling(126).sum().iloc[-1]
            ret_252 = series.rolling(252).sum().iloc[-1]

            return {
                    'return_ratio': return_ratio,
                    'annual_return_ratio': annual_return_ratio,
                    'ex_return_ratio': ex_return_ratio,
                    'ex_annual_return_ratio': ex_annual_return_ratio,
                    'sharp_ratio': sharp_ratio,
                    'return_volatility': return_volatility,
                    'information_ratio':information_ratio,
                    'max_drawdown': max_drawdown,
                    'win_percent':win_percent,
                    'trading_days':trading_days,
                    'ret_3':ret_3,
                    'ret_10':ret_10,
                    'ret_21':ret_21,
                    'ret_63':ret_63,
                    'ret_126':ret_126,
                    'ret_252':ret_252
                    }

        if data_type == 'long':
            perf = get_stats(self.groupret_pivotdata['{0}'.format(self.params['group_num']-1)], self.groupret_pivotdata['bm'])
        elif data_type =='short':
            perf = get_stats(self.groupret_pivotdata['0'], self.groupret_pivotdata['bm'])
        elif data_type =='long_short':
            perf = get_stats(self.groupret_pivotdata['ls'], self.groupret_pivotdata['bm'])
        return perf

    def get_IC_data(self, data_type):
            # IC
            def cal_ic(df):
                return df['daily_ret'].corr(df['factor'], method='spearman')

            if data_type == 'all':
                groupIC_data = self.group_data[['date','daily_ret','factor']].groupby('date', group_keys=False).apply(lambda x:cal_ic(x)).reset_index()
                groupIC_data.rename(columns={0:'g_ic'}, inplace=True)
                groupIC_data = groupIC_data.shift(1) # 首日为nan，最后一日有值
                groupIC_data['ic_cumsum'] = groupIC_data['g_ic'].cumsum()
                groupIC_data['ic_roll_ma'] = groupIC_data['g_ic'].rolling(22).mean()
                return groupIC_data.round(4).dropna() 

            elif data_type == 'long':
                data = self.group_data[self.group_data['group'] == str(self.params['group_num']-1)][['date','daily_ret','factor']]  
                groupIC_data = data.groupby('date', group_keys=False).apply(lambda x:cal_ic(x)).reset_index()
            elif data_type == 'short':
                data = self.group_data[self.group_data['group'] == '0'][['date','daily_ret','factor']]  
                groupIC_data = data.groupby('date', group_keys=False).apply(lambda x:cal_ic(x)).reset_index()
            elif data_type == 'long_short':
                data = self.group_data[self.group_data['group'].isin(['0',str(self.params['group_num']-1)])][['date','daily_ret','factor']]  
                groupIC_data = data.groupby('date', group_keys=False).apply(lambda x:cal_ic(x)).reset_index()
        
            IC_data = groupIC_data.rename(columns={0:'g_ic'}).dropna()
            
            ic_mean = np.nanmean(IC_data['g_ic'])
            ir = np.nanmean(IC_data['g_ic']) / np.nanstd(IC_data['g_ic'])
            ic_3 = IC_data['g_ic'].tail(3).mean()
            ic_10 = IC_data['g_ic'].tail(10).mean()
            ic_21 = IC_data['g_ic'].tail(21).mean()
            ic_63 = IC_data['g_ic'].tail(63).mean()
            ic_126 = IC_data['g_ic'].tail(126).mean()
            ic_252 = IC_data['g_ic'].tail(252).mean()

            return {
                    'ic':ic_mean,
                    'ir':ir,
                    'ic_3':ic_3,
                    'ic_10':ic_10,
                    'ic_21':ic_21,
                    'ic_63':ic_63,
                    'ic_126':ic_126,
                    'ic_252':ic_252
                    }

    def get_Turnover_data(self, data_type):

        def cal_turnover(df):
            # 求每天instrument和上一日的重复元素数量
            def count_repeat(s):
                if s.name > 0:
                    return len(set(s['instrument']).intersection(set(df.loc[s.name - 1, 'instrument'])))
                else:
                    return 0

            s = df.groupby('date').apply(lambda x:x.instrument.tolist())
            df = pd.DataFrame(s, columns = ['instrument']).reset_index()
            # 求每天instrument有多少元素
            df['instrument_count'] = df['instrument'].apply(len)

            df['repeat_count'] = df.apply(count_repeat, axis=1)
            df['turnover'] = 1 - df['repeat_count'] / df['instrument_count']
            return np.nanmean(df['turnover'])

        if data_type == 'long':
            df = self.group_data[self.group_data['group'] == str(self.params['group_num']-1)]
            return {'turnover':cal_turnover(df)}
        elif data_type == 'short':
            df = self.group_data[self.group_data['group'] == '0']
            return {'turnover':cal_turnover(df)}
        elif data_type == 'long_short':
            long_df = self.group_data[self.group_data['group'] == str(self.params['group_num']-1)]
            short_df = self.group_data[self.group_data['group'] == '0']
            return {'turnover':cal_turnover(long_df) + cal_turnover(short_df)}

    ## 总体绩效计算
    def get_whole_perf(self):
        summary_df = pd.DataFrame() 
        for _type in ['long', 'short', 'long_short']:   
            dict_merged = {} 
            dict1 = self.get_IC_data(_type)
            dict2 = self.get_Performance(_type)
            dict3 = self.get_Turnover_data(_type)

            dict_merged.update(dict1)
            dict_merged.update(dict2)
            dict_merged.update(dict3)
            df = pd.DataFrame.from_dict(dict_merged, orient='index', columns=['value']).T
            df['portfolio'] = _type 
            summary_df = summary_df.append(df)
        
        summary_df.index = range(len(summary_df))
        return summary_df.round(4)

    # 按年绩效计算
    def get_yearly_perf(self):
        # 计算年度绩效指标
        year_df = self.groupret_pivotdata.reset_index('date')
        year_df['year'] = year_df['date'].apply(lambda x:x.year)
        
        def cal_Performance(data):
            series = data['{0}'.format(self.params['group_num']-1)] # 只看多头组合
            bm_series = data['bm']

            return_ratio =  series.sum() # 总收益
            annual_return_ratio = series.sum() * 242 / len(series)  #  年度收益
            ex_return_ratio =  (series-bm_series).sum() # 总收益
            ex_annual_return_ratio = (series-bm_series).sum() * 242 / len(series-bm_series)  #  年度收益

            sharp_ratio = empyrical.sharpe_ratio(series,0.035/242)
            return_volatility = empyrical.annual_volatility(series)
            max_drawdown  = empyrical.max_drawdown(series)
            information_ratio=series.mean()/series.std()
            win_percent = len(series[series>0]) / len(series)
            trading_days = len(series)
            perf =  pd.DataFrame({
                    'return_ratio': [return_ratio],
                    'annual_return_ratio': [annual_return_ratio],
                    'ex_return_ratio': [ex_return_ratio],
                    'ex_annual_return_ratio': [ex_annual_return_ratio],
                    'sharp_ratio': [sharp_ratio],
                    'return_volatility': [return_volatility],
                    'max_drawdown': [max_drawdown],
                    'win_percent':[win_percent],
                    'trading_days':[int(trading_days)],
                    })
            return perf
        yearly_perf = year_df.groupby(['year'], group_keys=True).apply(cal_Performance) 
        yearly_perf = yearly_perf.droplevel(1).round(4)   # 去掉一个level

        # 计算年度IC
        data = self.group_data[self.group_data['group'] == str(self.params['group_num']-1)][['date','daily_ret','factor']] # 只看多头组合
        def cal_ic(df):
            return df['daily_ret'].corr(df['factor'])
        groupIC_data = data.groupby('date', group_keys=False).apply(lambda x:cal_ic(x)).reset_index()       
        IC_data = groupIC_data.rename(columns={0:'g_ic'}).dropna()
        IC_data['year'] = IC_data['date'].apply(lambda x:x.year)
        yearly_IC = IC_data.groupby('year').apply(lambda x:np.nanmean(x['g_ic']))

        yearly_perf['ic'] = yearly_IC.round(4)
        yearly_perf = yearly_perf.reset_index()
        yearly_perf['year'] = yearly_perf['year'].apply(str) 
        return yearly_perf

    def render(self):
        """图表展示因子分析结果"""
        print('*****************整体绩效指标*********************')
        fields = ['portfolio','ic', 'ir', 'return_ratio', 'annual_return_ratio','ex_return_ratio', 'ex_annual_return_ratio', 'sharp_ratio', 'return_volatility', 'information_ratio', 'max_drawdown', 'turnover', 'win_percent', 'ic_252', 'ret_252']
        whole_perf = self.whole_perf[fields] 
        print(whole_perf)
        print('**************年度绩效指标*********')
        fields = ['year','ic', 'return_ratio', 'annual_return_ratio', 'ex_return_ratio', 'ex_annual_return_ratio', 'sharp_ratio', 'return_volatility',
        'max_drawdown', 'win_percent', 'trading_days']
        yearly_perf = self.yearly_perf[fields]
        print(yearly_perf)
        # 绘制累积收益图
        self.group_cumret.plot(figsize=(18,8),title='累计分组收益')
        plt.show()
        plt.close()
        _IC = np.nanmean(self.ic['g_ic'])
        _IR = np.nanmean(self.ic['g_ic']) / np.nanstd(self.ic['g_ic'])
        abs_IC = self.ic['g_ic'].abs()
        significant_ic_ratio = abs_IC[abs_IC>=0.02].shape[0] / abs_IC.shape[0]
        ic_table=pd.DataFrame()
        ic_table['_IC']=[_IC]
        ic_table['_IR']=[_IR]
        ic_table['abs_IC']=[abs_IC]
        ic_table['significant_ic_ratio']=[significant_ic_ratio]
        print('*********************ic分析*****************')
        print(ic_table)
        # 绘制每期IC时序图
        # 绘制IC累计曲线图 
        ic=self.ic
        fig=plt.figure(figsize=(18,10))
        plt.subplot(2,1,1)
        plt.title('ic时间序列图')
        plt.plot(ic['date'],ic[['g_ic','ic_roll_ma']])
        plt.subplot(2,1,2)
        plt.plot(ic['date'],ic['ic_cumsum'])
        plt.show()
        plt.close()
        top_factor_df = self.factor_data[self.factor_data['date'] == self.end_date].round(4) # 最后一天因子数据
        top_factor_df['date'] = top_factor_df['date'].apply(lambda x:x.strftime('%Y-%m-%d'))
        # 按照 factor 列升序排序，获取最小的10行数据
        df_sorted_min = top_factor_df.sort_values('factor').head(self.top_n_ins)
        # 按照 factor 列降序排序，获取最大的10行数据
        df_sorted_max = top_factor_df.sort_values('factor', ascending=False).head(self.top_n_ins)
        print('***********因子值最大的标的**************')
        print(df_sorted_max)
        print('***********因子值最小的标的**************')
        print(df_sorted_min)
        return df_sorted_max,df_sorted_min