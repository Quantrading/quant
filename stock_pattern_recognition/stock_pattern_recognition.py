from trader_tool.stock_data import stock_data
from trader_tool.etf_fund_data import etf_fund_data
from trader_tool.bond_cov_data import bond_cov_data
from trader_tool.unification_data import unification_data
import json
import pandas as pd
import matplotlib.pyplot as plt
import requests
import numpy as np
from finta import TA
import mplfinance as mpf
import numpy as np
# 支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
class stock_pattern_recognition:
    def __init__(self,df='',show=True):
        '''
        股票/可转债/ETF形态识别
        df股票历史数据
        '''
        self.df=df
        self.show=show
    def plot_kline_figure(self,title='stock_w_bottom',df='',name_list=['12'],data_type=['线','点'],data_list=[[12]]):
        '''
        绘制标有买卖点的K线图
        name_list名称列表
        data_type绘制的数据类型线/点
        data_list数据列表，数据类型列表
        :return:
        '''
        df1=df
        #拆分买卖点
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        for name,data in zip(name_list,data_list):
            df1[name]=data
        macd = TA.MACD(df1)
        rsi = TA.RSI(df1)
        df1.rename(columns={'date': 'Date', 'open': 'Open', 'close': 'Close', 'high': 'High', 'low': 'Low',
                            'volume': 'Volume'}, inplace=True)
        # 时间格式转换
        plt.rcParams['font.family'] = 'SimHei'
        plt.rcParams['axes.unicode_minus'] = False
        df1['Date'] = pd.to_datetime(df1['Date'])
        # 出现设置索引
        df1.set_index(['Date'], inplace=True)
        # 设置股票颜
        mc = mpf.make_marketcolors(up='r', down='g', edge='i',volume='i')
        # 设置系统
        s = mpf.make_mpf_style(marketcolors=mc)
        add_plot = [mpf.make_addplot(macd['MACD'], panel=1, color='r'),
                    mpf.make_addplot(macd['SIGNAL'], panel=1, color='y'),
                    mpf.make_addplot(rsi, panel=2, title='RSI'),
                    mpf.make_addplot(df1['Close'], panel=0)]
        for name,plot_type in zip(name_list,data_type):
            if plot_type=='线':
                add_plot.append(mpf.make_addplot(df1[name], panel=0,color='r',title=title))
            else:
                add_plot.append(mpf.make_addplot(df1[name]-1,panel=0,color='r',type='scatter',marker='^',markersize=80))
                
        # 绘制股票图，5，10，20日均线
        mpf.plot(df1, type='candle', style=s,addplot=add_plot,volume=True)#mav=(5, 10, 20),
        plt.show()
    def get_stock_w_bottom(self,n=60):
        '''
        W底 n整数
        # 1. 找区间1的极小值，为左底
        # 2. 找区间2的极小值，为右底
        # 3. 找左底与右底之间区域的极大值
        # 4. 比较左底与右底的涨幅，是否相差<3%
        # 5. 比较左底与右底的macd值，是否形成底背离
        # 6. 终点日期收盘价，是否突破颈线位
        # 以下条件可选
        # 7. 比较左底与右底的成交额，是否左底成交额>右底成交额
        # 8. 比较左底与极大值之间涨跌幅，是否>N%(判断颈线位幅度)
        # 9. 比较左底与右底之间，是否出现过涨停(判断股性活跃程度)
        # 10. 其他
        算法自定义词汇说明：
        1. 以实际交易日期为X横坐标，某只股票的价格为Y纵坐标；
        2. 一个交易日，就会出现一条K线。以当前需要回测的日期为终点，往历史时间选择一个大区间N天；
        3. 将大区间一分为二，简化处理，两个小区间完全相等，分别包含N/2条K线。命名为：可变化区间1，可变化区间2，简称区间1，区间2.
        ————————————————
        '''
        #一半的数据
        n_2=int(n/2)
        #最近N天
        df=self.df[-n:]
        #价格列表
        close_list=df['close'].tolist()
        #开始的价格
        open_price=close_list[0]
        #现在的价格
        last_price=close_list[-1]
        #左边的数据
        left_df=df[-n:-n_2]
        #右边的数据
        right_df=df[-n_2:]
        # 1. 找区间1的极小值，为左底
        #左边的最小值
        left_min_value=min(left_df['close'].tolist())
        #最小值的位置
        left_min_value_index=close_list.index(left_min_value)
        # 2. 找区间2的极小值，为右底
        #右边的最小值
        right_min_value=min(right_df['close'].tolist())
        #右边最小值的位置
        right_min_value_index=close_list.index(right_min_value)
        # 3. 找左底与右底之间区域的极大值
        #中间最大的价格,是否突破颈线位
        middle_max_value=max(df[left_min_value_index:right_min_value_index]['close'].tolist())
        # 4. 比较左底与右底的涨幅，是否相差<3%,不同周期不一样
        up_and_down=((right_min_value-left_min_value)/left_min_value)*100
        # 5. 比较左底与右底的macd值，是否形成底背离
        # 6. 终点日期收盘价，是否突破颈线位
        break_through=''
        if last_price>=middle_max_value:
            break_through=True
        else:
            break_through=False
        # 以下条件可选
        # 7. 比较左底与右底的成交额，是否左底成交额>右底成交额
        left_volume=left_df['volume'].sum()
        right_volume=right_df['volume'].sum()
        trading_volume=''
        if left_volume>=right_volume:
            trading_volume=True
        else:
            trading_volume=False
        # 8. 比较左底与极大值之间涨跌幅，是否>N%(判断颈线位幅度)
        # 9. 比较左底与右底之间，是否出现过涨停(判断股性活跃程度)
        df['涨停']=df['涨跌幅'].apply(lambda x: '涨停' if round(x)==10 else '不涨停')
        limt_stats=''
        if df[df['涨停']=='涨停'].shape[0]>0:
            limt_stats=True
        else:
            limt_stats=False
        #目前颈线位核限制价格的涨跌幅
        mid_return=((last_price-middle_max_value)/middle_max_value)*100
        #通用我w底，其他的条件可以自己价
        #绘制突破
        if self.show==True:
            w_list=[]
            for i in close_list:
                if i in [open_price,last_price,left_min_value,right_min_value,middle_max_value]:
                    w_list.append(i)
                else:
                    w_list.append(None)
            self.plot_kline_figure(df=df,name_list=['底','线'],data_type=['点','线'],data_list=[w_list,middle_max_value,df['close'].tolist()])
        else:
            pass
        if left_min_value<=right_min_value and mid_return>=3:
            return "是"
        else:
            return "不是"
    def get_break_through_box(self,n=60,forward_n=20,up_and_down=40,right_return=3):
        '''
        突破箱体
        n取60
        forward_选择后面10天的数据继续对比
        up_and_down区间的涨跌幅
        right_return右边的收益
        '''
        if n<=forward_n:
            forward_n=1
        else:
            forward_n=forward_n
        #最近N天
        df=self.df[-n:]
        #价格列表
        close_list=df['close'].tolist()
        #开始的价格
        open_price=close_list[0]
        #现在的价格
        last_price=close_list[-1]
        #向前取的
        forward_close_list=close_list[:n-forward_n]
        #最大值
        max_value=max(forward_close_list)
        #最小值
        min_value=min(forward_close_list)
        #区间收益
        range_return=((max_value -min_value)/min_value)*100
        #对比区间的收益
        return_contrast=((last_price-max_value)/max_value)*100
        box_list=[]
        if self.show==True:
            for i in close_list:
                if i in [open_price,last_price,max_value,min_value]:
                    box_list.append(i)
                else:
                    box_list.append(None)
            self.plot_kline_figure(df=df,title='break_through_box',name_list=['最大值','最小值','关键点'],data_type=['线','线','点'],data_list=[max_value,min_value,box_list])
        if range_return<=up_and_down and return_contrast>=right_return:
            return "是"
        else:
            return "不是"
    def get_stock_m_top(self,all_n=120,select_n=100,up_and_down=3,quant=75):
        '''
        识别股票m顶
        all_全部的数据
        select_n最近N天
        up_and_down 2个顶的涨跌幅价格差
        quant价格分位数
        M顶，也被称为“双重顶”或“双顶”，是K线图中一种常见的反转形态。它由两个相对接近的高点组成，形状类似于英文字母“M”。这种形态通常出现在股票价格的上升趋势中，预示着股价可能会发生反转，由涨转跌。
        M顶的技术特征包括：
        1. 出现在上涨趋势中。
        2. 两个高点处在同一价格水平或右边高点略低。只有极少数的双顶右边高点高于左边高点。
        3. 大多数双顶右边高点的成交量小于左边。
        4. 双顶的颈线一般是过第一次回落低点的水平线。
        在通达信软件中，M顶的公式主要涉及到一些技术指标和条件。首先，M顶通常出现在连续上升的过程中，当市场价格上涨至某一价格水平，成交量显著放大，然后价格开始掉头回落；当价格下跌至某一位置时，价格再度反弹上行，但成交量较第一高峰时略有收缩，反弹至前高附近之后再第二次下跌，并跌破第一次回落的低点。
        具体到计算或检测M顶的公式，可能需要利用到如均线、高低点比较等技术指标。例如，可以用MA (CLOSE,13)来计算13日的收盘价的移动平均值。此外，还需要设定一些阈值来判断是否形成了M顶，比如两个头部大致处在同一水平线，两顶高度落差不超过3%，以及两顶间隔需要保持一定距离等。
        '''
        #最近N天
        try:
            df=self.df[-all_n:]
            #价格列表
            all_close_list=df['close'].tolist()
            #开始的价格
            open_price=all_close_list[0]
            #现在的价格
            last_price=all_close_list[-1]
            close_list=all_close_list[-select_n:]
            #选择数据的最低点
            rank_close_list=sorted(close_list)
            #二分发
            mid_value=rank_close_list[int(len(rank_close_list)/2)]
            mid_value_index=close_list.index(mid_value)
            #左边最大值
            left_max_value=max(close_list[:mid_value_index])
            left_max_value_index=close_list.index(left_max_value)
            #右边最大值
            right_max_value=max(close_list[-mid_value_index:])
            right_max_value_index=close_list.index(right_max_value)
            #最大最小涨跌幅
            max_min_up_down=abs(((right_max_value-left_max_value)/left_max_value)*100)
            #颈线
            try:
                line=min(close_list[left_max_value_index:right_max_value_index])
            except Exception as e:
                print("运行错误:",e)
                line=mid_value
            #最高价的位位数
            max_quant=np.percentile(all_close_list,quant)
            m_list=[]
            if self.show==True:
                for i in all_close_list:
                    if i in [open_price,last_price,line,right_max_value,left_max_value,mid_value]:
                        m_list.append(i)
                    else:
                        m_list.append(None)
                self.plot_kline_figure(df=df,title='stock_m_top',name_list=['线','点'],data_type=['线','点'],data_list=[line,m_list])

            if left_max_value>=right_max_value and max_min_up_down<=up_and_down and left_max_value>max_quant and last_price<=line:
                return "是"
            else:
                return "不是"
        except Exception as e:
            print("运行错误:",e)
            return "不是"
    def get_stock_bottom_of_circular_arc(self,all_n=90,select_n=80,up_and_down=30,new_zdf=5):
        '''
        "圆弧底"是一种常出现于交易清淡的个股中的K线形态，
        具体表现为K线在一段时间内的连续走势中，连线呈圆弧形，主要耗时几个月甚至更久，
        因此具有相当大的能量。这种形状往往类似于一个碟子或碗，所以它也被称为碟形或碗形。此外，
        它主要出现在价格底部区域，是极弱势行情的典型特征。其具体的形态特征包括：
        1. 出现在下跌行情中，形态形成过程中股价和成交量均显现圆弧状；
        2. 圆弧底形成的时间越长，向上突破后力度越强，涨幅越大
        ；3.有时，在圆弧底形态形成后，股价并不会立刻上涨，而会先形成一个低位横盘的阶段。
        这些特点使投资者能通过观察圆弧底形态来预测股票的未来走势。
        '''
        #最近N天
        df=self.df[-all_n:]
        #价格列表
        all_close_list=df['close'].tolist()
        #开始的价格
        open_price=all_close_list[0]
        #现在的价格
        last_price=all_close_list[-1]
        close_list=all_close_list[:select_n]
        left_max_value=close_list[0]
        left_max_value_index=close_list.index(left_max_value)
        #右边最大值
        right_max_value=close_list[-1]
        right_max_value_index=close_list.index(right_max_value)
        min_value=min(close_list)
        #最小值核最大值的涨跌幅
        min_max_value_up_down=((left_max_value-min_value)/min_value)*100
        #中间的线
        line=min_value+((left_max_value-min_value)/3)*2
        #中间的线核最新价的涨跌幅
        line_last_price_up_down=((last_price-line)/line)*100
        m_list=[]
        if self.show==True:
            for i in all_close_list:
                if i in [open_price,last_price,line,right_max_value,left_max_value,min_value]:
                    m_list.append(i)
                else:
                    m_list.append(None)
            self.plot_kline_figure(df=df,title='stock_bottom_of_circular_arc',name_list=['线','点'],data_type=['线','点'],data_list=[line,m_list])
        if left_max_value>min_value and last_price>=right_max_value and min_max_value_up_down>=up_and_down and line_last_price_up_down>=new_zdf:
           return "是"
        else:
            return "不是"
    def get_water_hibiscus_shape(self,all_n=60,select_n=30,down_n=10,up_n=10,max_zdf=-15,min_zdf=-8,right_zdf=3,disk_n=10):
        '''
        形态分析
        前面有一个相对高位箱体，向下跌破箱体，下跌-8%-15%，下跌
        反弹周期10天上涨8-15
        10天的整理，放量3倍突破
        '''
       
        #最近N天
        df=self.df[-all_n:]
        df['5日成交量']=df['volume'].rolling(5).mean()
        #价格列表
        all_close_list=df['close'].tolist()
        #开始的价格
        open_price=all_close_list[0]
        #现在的价格
        last_price=all_close_list[-1]
        close_list=all_close_list[:select_n]
        #位置75的位置
        price_75=np.percentile(all_close_list,75)
        #左边箱体的最新价
        #左边箱体的最高价
        left_max_value=max(close_list)
        left_max_value_index=close_list.index(left_max_value)
        #左边箱体的最低价
        left_min_value=min(close_list)
        left_min_value_index=close_list.index(left_max_value)
        #箱体中线
        center_line=(left_max_value+left_min_value)/2
        down_close=all_close_list[select_n:select_n+down_n]
        #下跌的幅度
        down=((down_close[-1]-down_close[0])/down_close[0])*100
        #上涨的幅度
        up_close=all_close_list[select_n+down_n:select_n+down_n+up_n]
        up=((up_close[-1]-up_close[0]/up_close[0]))*100
        #上涨的最新加
        up_last_price=up_close[-1]
        #突破前面的箱体
        if up_last_price>=center_line:
            is_break=True
        else:
            is_break=False
        #右边的数据
        right_close=all_close_list[-(all_n-select_n-up_n-down_n):]
        #右边箱体的最高加
        right_max_price=max(right_close)
        #右边的涨跌幅
        right=((right_close[-1]-right_close[0])/right_close[0])*100
        #放量突破前一个平台的中线
        last_volume=df['volume'].tolist()[-1]
        volume_5=df['5日成交量'].tolist()[-1]
        m_list=[]
        if self.show==True:
            for i in all_close_list:
                if i in [open_price,last_price,center_line,right_max_price,left_max_value,left_min_value,left_max_value,]:
                    m_list.append(i)
                else:
                    m_list.append(None)
            self.plot_kline_figure(df=df,title='stock_water_hibiscus',name_list=['线1','线2','点'],data_type=['线','线','点'],data_list=[center_line,left_max_value,m_list])
        if is_break and down<=min_zdf and down>=max_zdf and last_price>=center_line and last_volume>=2*volume_5 and center_line>=price_75:
            return '是'
        else:
            return '不是'
        






        





        





        













        


        

        
        

        


        


        





        
        






        


        
        

    
    

