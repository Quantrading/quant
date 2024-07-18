from  wind_data.WindPy import w
import pandas as pd
from datetime import *
class wind_data:
    def __init__(self):
        w.start()
         # 默认命令超时时间为120秒，如需设置超时时间可以加入waitTime参数，例如waitTime=60,即设置命令超时时间为60秒  
        # 判断WindPy是否已经登录成功
        w.isconnected()
    def get_wsd_hist_data(self,codes='600031.SH',fields=['CLOSE','HIGH','LOW','OPEN','VOLUME'],beginTime='20210101',endTime=None):
        '''
        获取历史数据
        3. 获取日时间序列函数WSD
        w.wsd（codes, fields, beginTime, endTime, options）

        支持股票、债券、基金、期货、指数等多种证券的基本资料、股东信息、市场行情、证券分析、预测评级、财务数据等各种数据。wsd可以支持取 多品种单指标 或者 单品种多指标 的时间序列数据。

        参数说明
        参数	类型	可选	默认值	说明
        codes	str或list	否	无	证券代码，支持获取单品种或多品种，如“600030.SH”或[“600010.SH”,“000001.SZ”]
        fields	str或list	否	无	指标列表,支持获取单指标或多指标，，如“CLOSE,HIGH,LOW,OPEN”
        beginTime	str或datetime	是	endTime	起始日期，为空默认为截止日期，如: "2016-01-01"、“20160101”、“2016/01/01”、"-5D"(当前日期前推5个交易日)、datetime/date类型
        endTime	str或datetime	是	系统当前日期	如: "2016-01-05"、“20160105”、“2016/01/05”、"-2D"(当前日期前推2个交易日) 、datetime/date类型
        options	str	是	“”	options以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用options=""
        集成在options中的参数
        options以字符串的形式集成了多个参数。以下列举了一些常用的参数：

        参数	类型	可选	默认值	说明
        Days	str	是	'Trading'	日期选项，参数值含义如下：
        Weekdays: 工作日，
        Alldays: 日历日，
        Trading: 交易日
        Fill	str	是	'Blank'	空值填充方式。参数值含义如下：
        Previous：沿用前值，
        Blank：返回空值

        如需选择自设数值填充，在options添加“ShowBlank=X", 其中X为自设数。
        Order	str	是	'A'	日期排序，“A”：升序，“D”：降序
        Period	str	是	'D'	取值周期。参数值含义如下：
        D：天，
        W：周，
        M：月，
        Q：季度，
        S：半年，
        Y：年
        TradingCalendar	str	是	'SSE'	交易日对应的交易所。参数值含义如下：
        SSE ：上海证券交易所，
        SZSE：深圳证券交易所，
        CFFE：中金所，
        TWSE：台湾证券交易所，
        DCE：大商所，
        NYSE：纽约证券交易所，
        CZCE：郑商所，
        COMEX：纽约金属交易所，
        SHFE：上期所， 
        NYBOT：纽约期货交易所，
        HKEX：香港交易所，
        CME：芝加哥商业交易所，
        Nasdaq：纳斯达克证券交易所，
        NYMEX：纽约商品交易所，
        CBOT：芝加哥商品交易所，
        LME：伦敦金属交易所，
        IPE：伦敦国际石油交易所
        Currency	str	是	'Original'	输入币种。参数值含义如下：
        Original：“原始货币”，
        HKD：“港币”，
        USD：“美元”，
        CNY：“人民币”
        PriceAdj	str	是	不复权	股票和基金(复权方式)。参数值含义如下：
        F：前复权，
        B：后复权，
        T：定点复权；债券(价格类型)
        CP：净价，
        DP：全价，
        MP：市价，
        YTM：收益率
        注:

        Fields和Parameter也可以传入list，比如可以用[“CLOSE”,“HIGH”,“LOW”,“OPEN”]替代“CLOSE,HIGH,LOW,OPEN”;

        获取多个证券数据时，Fields只能选择一个。

        日期支持相对日期宏表达方式，日期宏具体使用方式参考'日期宏’部分内容

        options为可选参数，可选参数多个，在参数说明详细罗列。

        wsd函数支持输出DataFrame数据格式，需要函数添加参数usedf=True，可以使用usedfdt=True来填充DataFrame输出NaT的日期。

        返回说明
        如果不指定usedf=True，该函数将返回一个WindData对象，包含以下成员：

        返回码	解释	说明
        ErrorCode	错误ID	返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因.
        Data	数据列表	返回函数获取的数据，比如读取000592.SZ的close指标从'2017-05-08'到'2017-05-18'区间的数据，返回值为.Data=[[5.12,5.16,5.02,4.9,4.91,5.13,5.35,5.42,5.32],[5.3,5.12,5.17,4.98,4.94,4.93,5.1,5.4,5.4]]
        Codes	证券代码列表	返回获取数据的证券代码列表.Codes=[000592.SZ]
        Field	指标列表	返回获取数据的指标列表.Fields=[CLOSE]
        Times	时间列表	返回获取数据的日期序列.Times=[20170508,20170509,20170510,20170511,20170512,20170515,20170516, 20170517,20170518]
        示例说明
        # 任取一只国债010107.SH六月份以来的净值历史行情数据
        history_data=w.wsd("010107.SH",
                        "sec_name,ytm_b,volume,duration,convexity,open,high,low,close,vwap", 
                        "2018-06-01", "2018-06-11", "returnType=1;PriceAdj=CP", usedf=True) 
        # returnType表示到期收益率计算方法，PriceAdj表示债券价格类型‘
        history_data[1].head()
        '''
        stats,df=w.wsd(codes=codes,beginTime=beginTime,endTime=endTime,fields=fields,usedf=True)
        if stats==0:
            print('获取成功')
            df['date']=df.index
            df.rename(columns={'CLOSE':"close",'HIGH':'high','LOW':'low','OPEN':'open','VOLUME':'volume'},inplace=True)
            return df
        else:
            df=pd.DataFrame()
            return df
    def get_wsi_mi_data(self,codes='600031.SH',fields=['CLOSE','HIGH','LOW','OPEN','VOLUME'],beginTime='2021-01-01 09:30:00',endTime=None,options=''):
        '''
        获取分钟数据
        w.wsi(codes, fields, beginTime, endTime, options)
        用来获取国内六大交易所（上海交易所、深圳交易所、郑商所、上金所、上期所、大商所）证券品种的分钟线数据，包含基本行情和部分技术指标的分钟数据，分钟周期为1-60min，技术指标参数可以自定义设置。

        参数说明
        参数	类型	可选	默认值	说明
        codes	str或list	否	无	证券代码，支持获取单品种或多品种，如'600030.SH'或['600010.SH','000001.SZ']
        fields	str或list	否	无	指标列表,支持获取单指标或多指标，，如'CLOSE,HIGH,LOW,OPEN'
        beginTime	str或datetime	是	endTime	分钟数据的起始时间，支持字符串、datetime/date如: "2016-01-01 09:00:00"
        endTime	str或datetime	是	当前系统时间	分钟数据的截止时间，支持字符串、datetime/date如: "2016-01-01 15:00:00"，缺省默认当前时间
        options	str	是	""	options以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用options=""
        集成在options中的参数
        options以字符串的形式集成了多个参数。以下列举了一些常用的参数：

        参数	类型	可选	默认值	说明
        BarSize	str	是	“1”	BarSize在1-60间选择输入整数数字，代表分钟数
        Fill	str	是	'Blank'	空值填充方式。参数值含义如下：
        Previous：沿用前值，
        Blank：返回空值

        如需选择自设数值填充，在options添加“ShowBlank=X", 其中X为自设数。
        PriceAdj	str	是	U	股票和基金(复权方式)。参数值含义如下：
        U：不复权,
        F：前复权，
        B：后复权。
        注：

        wsi一次支持提取单品种或多品种，并且品种名带有“.SH”等后缀；

        wsi提取的指标fields和可选参数option可以用list实现；

        wsi支持国内六大交易(上交所、深交所、大商所、中金所、上期所、郑商所)近三年的分钟数据;

        wsi函数支持输出DataFrame数据格式，需要函数添加参数usedf=True，如例2.

        wsi支持多品种多指标,单次提取一个品种支持近三年数据，若单次提多个品种,则品种数*天数≤100。

        返回说明
        如果不指定usedf=True，该函数将返回一个WindData对象，包含以下成员：

        返回码	解释	说明
        ErrorCode	错误ID	返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因.
        Data	数据列表	读取中国平安"601318.SH"的"open,high"指标2017-06-01 09:30:00至2017-06-01 10:01:00的五分钟数据，返回值为.Data=[[45.4,45.15,45.42,45.34,45.47,45.48],[45.63,45.49,45.56,45.52,45.51,45.72]]
        Codes	证券代码列表	返回获取数据的证券代码列表.Codes=[600111.SH,600340.SH,600485.SH]
        Field	指标列表	返回获取数据的指标列表.Fields=[open,high]
        Times	时间列表	返回获取数据的日期序列.Times=[20170601 09:35:00,20170601 09:40:00,20170601 09:45:00,20170601 09:50:00,20170601 09:55:00,20170601 10:00:00]
        示例说明
        # 取IF00.CFE的分钟数据

        from datetime import *
        codes="IF00.CFE";
        fields="open,high,low,close";
        error,data=w.wsi(codes, fields, "2017-06-01 09:30:00", datetime.today(), "",usedf=True)
        #其中，datetime.today()是python内置的日期函数，表示当前时刻。
        '''
        stats,df=w.wsi(codes=codes,beginTime=beginTime,endTime=endTime,
                       fields=fields,
                       options=options,
                       usedf=True)
        if stats==0:
            print('获取成功')
            df['date']=df.index
            df.rename(columns={'CLOSE':"close",'HIGH':'high','LOW':'low','OPEN':'open','VOLUME':'volume'},inplace=True)
            return df
        else:
            df=pd.DataFrame()
            return df
    def get_wst_tick_data(self,codes='600031.SH',fields=['last','bid1','ask1'],beginTime='2024-01-03 09:30:00',endTime=None,options=''):
        '''
        w.wst(codes, fields, beginTime, endTime, options)
        用获取国内六大交易所（上海交易所、深圳交易所、郑商所、上金所、上期所、大商所）证券品种的日内盘口买卖五档快照数据和分时成交数据(tick数据).

        参数说明
        参数	类型	可选	默认值	说明
        codes	str或list	否	无	证券代码，支持获取单品种，如'600030.SH'
        fields	str或list	否	无	指标列表,支持获取单指标或多指标，，如'CLOSE,HIGH,LOW,OPEN'
        beginTime	str或datetime	是	endTime	分钟数据的起始时间，支持字符串、datetime/date如: "2016-01-01 09:00:00"
        endTime	str或datetime	是	当前系统时间	分钟数据的截止时间，支持字符串、datetime/date如: "2016-01-01 15:00:00"，缺省默认当前时间
        options	str	是	""	options以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用options=""
        注：

        wst只支持提取单品种，并且品种名带有“.SH”等后缀；

        wst提取的指标fields可以用list实现；

        wst支持国内六大交易(上交所、深交所、大商所、中金所、上期所、郑商所)近七个交易日的tick数据;

        wst函数支持输出DataFrame数据格式，需要函数添加参数usedf=True。

        返回说明
        如果不指定usedf=True，该函数将返回一个WindData对象，包含以下成员：

        返回码	解释	说明
        ErrorCode	错误ID	返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因.
        Data	数据列表	返回函数获取的tick数据，读取中国平安"601318.SH"的"last,bid1"指标2017-06-13 09:30:00至2017-06-13 9:31:00的tick数据，返回值为.Data=[[9.11,9.11,9.11,9.11,9.11,9.11,9.11,9.11,9.11,9.11,...],[9.11,9.11,9.12,9.11,9.11,9.11,9.11,9.11,9.11,9.12,...]]
        Codes	证券代码列表	返回获取数据的证券代码列表.Codes=[601318.SH]
        Field	指标列表	返回获取数据的指标列表.Fields=[open,high]
        Times	时间列表	返回获取数据的日期序列.Times=[20170601 09:35:00,20170601 09:40:00,20170601 09:45:00,20170601 09:50:00,20170601 09:55:00,20170601 10:00:00]
        示例说明
        # 提取平安银行（000001.SZ）当天的买卖盘数据。
        from datetime import *

        # 设置起始时间和截止时间，通过wst接口提取序列数据
        begintime=datetime.strftime(datetime.now(),'%Y-%m-%d 09:30:00')
        endtime=datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
        # last最新价，amt成交额，volume成交量
        # bid1 买1价，bsize1 买1量
        # ask1 卖1价, asize1 卖1量
        codes="000001.SZ"
        fields="last,bid1,ask1" 
        w.wst(codes,fields,begintime,endtime)
        '''
        stats,df=w.wst(codes=codes,beginTime=beginTime,endTime=endTime,
                       fields=fields,
                       options=options,
                       usedf=True)
        if stats==0:
            print('获取成功')
            df['date']=df.index
            df.rename(columns={'CLOSE':"close",'HIGH':'high','LOW':'low','OPEN':'open','VOLUME':'volume'})
            return df
        else:
            df=pd.DataFrame()
            return df
    def get_wsq_spot_data(self,codes='600031.SH',fields=['rt_low,rt_last_vol'],func=None,options=''):
        '''
        实时数据
        w.wsq（codes, fields, options, func)
        用来获取股票、债券、基金、期货、指数等选定证券品种的当天指标实时数据，可以一次性请求实时快照数据，也可以通过订阅的方式获取实时数据。
        参数说明
        参数	类型	可选	默认值	说明
        codes	str或list	否	无	证券代码，支持获取单品种或多品种，如："600030.SH,000001.SZ "、["600030.SH","000001.SZ"]'
        fields	str或list	否	无	指标列表,支持获取多指标，，如'CLOSE,HIGH,LOW,OPEN'
        options	str	是	”“	options以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用options=""
        func	str	是	None	func默认为None, 此时以一次性快照方式获取数据，func=DemoWSQCallback时, 以订阅的方式实时返回行情数据, DemoWSQCallback的函数定义可参考API帮助中心的案例
        注：
        wsq函数的参数中品种代码、指标和可选参数也可以用list实现；用户可以一次提取或者订阅多个品种数据多个指标；

        wsq函数订阅模式下只返回订阅品种行情有变化的订阅指标, 对没有变化的订阅指标不重复返回实时行情数据；

        wsq订阅时，API发现用户订阅内容发生变化则调用回调函数，并且只把变动的内容传递给回调函数。

        用户自己定义的回调函数格式请参考API帮助中心的案例，回调函数中不应处理复杂的操作；

        wsq函数快照模式支持输出DataFrame数据格式，需要函数添加参数usedf=True，可以使用usedfdt=True来填充DataFrame输出NaT的日期。

        返回说明

        快照模式下函数输出字段解释如下：

        返回码	解释	说明
        ErrorCode	错误ID	返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因.
        Data	数据列表	返回函数获取的快照数据，读取中国平安"601318.SH "的"rt_last,rt_open"指标快照数据.Data=[[54.16],[53.72]]
        Codes	证券代码列表	返回获取数据的证券代码列表.Codes=[601318.SH]
        Field	指标列表	返回获取数据的指标列表.Fields=[open,high]
        Times	时间列表	返回获取数据的日期序列.Times=[20170626 17:50:53]
        ​ 订阅模式下函数输出字段解释如下：

        w.wsq运行后，会将行情传入回调函数DemoWSQCallback, 传入数据为WindData类型，具体数据字段信息如下:

        返回码	解释	说明
        ErrorCode	错误ID	返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因.
        StateCode	状态ID	返回订阅时的字段，无实质意义..StateCode=1
        RequestID	请求ID	返回订阅的请求ID.RequestID=4
        Code	证券代码列表	返回获取实时数据的品种列表, 只返回行情变动指标对应的品种..Code=[601318.SZ]
        Fileds	字段列表	返回获取的实时数据的指标列表, 只返回行情变动的指标列表.Fields=[RT_OPEN,RT_LAST]
        Times	时间列表	返回获取数据的本地时间戳.Times=[20170626 17:50:53]
        Data	数据列表	返回函数获取的实时行情数据，获取中国平安"601318.SH" 的"rt_last,rt_open"指标订阅数据.Data=[[54.16],[53.72]]
        取消实时行情订阅函数CancelRequest
        w.cancelRequest(RequestID)

        用来根据w.wsq的订阅请求ID来取消订阅

        参数说明
        参数	类型	可选	默认值	说明
        RequestID	int	否	无	输入取消订阅的订阅ID, 支持取消单次订阅和全部订阅.支持格式: 1或0
        注：

        可以像w.cancelRequest(3)一样，输入一个id的数字，而取消某订阅；

        请求ID为0代表取消全部订阅，即输入w.cancelRequest(0)。

        示例说明
        data=w.wsq("600000.SH","rt_low,rt_last_vol",func=DemoWSQCallback);
        #订阅
        #等待回调，用户可以根据实际情况写回调函数
        #....
        #根据刚才wsq返回的请求ID，取消订阅
        w.cancelRequest(data.RequestID)
        '''
        stats,df=w.wsq(codes=codes,
                       fields=fields,
                       func=func,
                       options=options,
                       usedf=True)
        if stats==0:
            print('获取成功')
            df['date']=df.index
            df.rename(columns={'CLOSE':"close",'HIGH':'high','LOW':'low','OPEN':'open','volume':'volume'},inplace=True)
            return df
        else:
            df=pd.DataFrame()
            return df
    def get_wss_data(self,codes='600031.SH',fields=['CLOSE','HIGH','LOW','OPEN','VOLUME'],options=''):
        '''
        w.wss（codes, fields, option）
        同样支持股票、债券、基金、期货、指数等多种证券的基本资料、股东信息、市场行情、证券分析、预测评级、财务数据等各种数据。但是WSS支持取多品种多指标某个时间点的截面数据。

        参数说明
        参数	类型	可选	默认值	说明
        windCodes	str或list	否	无	证券代码，支持获取单品种或多品种如'600030.SH'或['600010.SH','000001.SZ']
        Fields	str或list	否	无	指标列表，支持获取多指标如'CLOSE,HIGH,LOW,OPEN'
        options	str	是	""	options以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用options=""
        注:

        wss函数一次只能提取一个交易日或报告期数据，但可以提取多个品种和多个指标；

        wss函数可选参数有很多，rptDate，currencyType，rptType等可借助代码生成器获取；

        wss函数支持输出DataFrame数据格式，需要函数添加参数usedf=True，可以使用usedfdt=True来填充DataFrame输出NaT的日期。

        返回说明
        如果不指定usedf=True，该函数将返回一个WindData对象，包含以下成员：

        返回码	解释	说明
        ErrorCode	错误ID	返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因.
        Data	数据列表	返回函数获取的数据，比如读取"600111.SH,600340.SH,600485.SH" 的"eps_basic,profittogr"指标20161231（即2016年的年报）的数据，返回值为.Data=[[0.025,2.22,0.52],[1.5701,11.4605,51.8106]]
        Codes	证券代码列表	返回获取数据的证券代码列表.Codes=[600111.SH,600340.SH,600485.SH]
        Field	指标列表	返回获取数据的指标列表.Fields=[EPS_BASIC,PROFITTOGR]
        Times	时间列表	返回获取数据的日期序列.Times=[20180824]
        示例说明
        # 取被动指数型基金最新业绩排名
        fund=w.wset("sectorconstituent","date=2018-06-11;sectorid=2001010102000000").Data[1]
        error_code,returns=w.wss(fund, 
                                "sec_name,return_1w,return_1m,return_3m,return_6m,return_1y,return_ytd,fund_fundmanager",
                                "annualized=0;tradeDate=20180611",usedf=True)
        returns.head(10)
        '''
        stats,df=w.wsq(codes=codes,
                       fields=fields,
                       options=options,
                       usedf=True)
        if stats==0:
            print('获取成功')
            df['date']=df.index
            df.rename(columns={'CLOSE':"close",'HIGH':'high','LOW':'low','OPEN':'open','VOLUME':'volume'},inplace=True)
            return df
        else:
            df=pd.DataFrame()
            return df
if __name__=="__main__":
    models=wind_data()
    df=models.get_wsq_spot_data()
    print(df)
