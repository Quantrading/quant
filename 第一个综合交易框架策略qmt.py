#导入综合框架
from trader_tool.trader_frame import trader_frame
#统一数据模块
from trader_tool.unification_data import unification_data
from trader_tool.ths_rq import ths_rq
#分析模型
from trader_tool.analysis_models import analysis_models
#形态分析模型
from trader_tool.shape_analysis import shape_analysis
import schedule
from tqdm import tqdm
import time
class trader_strategy:
    def __init__(self,trader_tool='qmt',exe='C:/同花顺软件/同花顺/xiadan.exe',
                tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qmt_path='C:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55003645',qmt_account_type='STOCK',slippage=0.01):
        '''
        交易策略
        买入人气排行前10,脉冲人气排行50,趋势大于50,持有大于25
        '''
        self.exe=exe
        self.tesseract_cmd=tesseract_cmd
        self.trader_tool=trader_tool
        self.qmt_path=qmt_path
        self.qmt_account=qmt_account
        self.qmt_account_type=qmt_account_type
        self.slippage=slippage
        self.trader=trader_frame(trader_tool=self.trader_tool,exe=self.exe,
                tesseract_cmd=self.tesseract_cmd,
                qmt_path=self.qmt_path,
                qmt_account=self.qmt_account,
                qmt_account_type=self.qmt_account_type,
                slippage=self.slippage)
        self.trader=self.trader.get_trader_frame()
        self.data=unification_data(trader_tool=self.trader_tool)
        self.data=self.data.get_unification_data()
        self.ths_rq=ths_rq()
        self.analysis_models=analysis_models()
        self.shape_analysis=shape_analysis
    def connact(self):
        '''
        链接交易系统
        '''
        try:
            self.trader.connect()
            print('{}成功'.format(self.trader_tool))
            return True
        except Exception as e:
            print("运行错误:",e)
            print('{}连接失败'.format(self.trader_tool))
            return False
    def get_buy_sell_data(self):
        '''
        获取同花顺人气排行数据
        '''
        df=self.ths_rq.get_hot_stock_rank()
        print(df)
        df.to_excel(r'数据.xlsx')
        rank_stock_list=df['证券代码'].tolist()
        score_list=[]
        stock_list=df['证券代码'].tolist()
        for i in tqdm(range(len(stock_list))):
            stock=stock_list[i]
            try:
                hist=self.data.get_hist_data_em(stock=stock)
                score=self.analysis_models.mean_line_models(df=hist)
                score_list.append(score)
            except Exception as e:
                print("运行错误:",e)
                score_list.append(None)
        df['score']=score_list
        buy_df=df[df['score']>=50]
        #买入下单
        buy_stock_list=buy_df['证券代码'][:10]
        for stock in buy_stock_list:
            try:
                price=self.data.get_spot_data(stock=stock)['最新价']
                #检查是否可以买入
                if self.trader.check_stock_is_av_buy(stock=stock,price=price,amount=100):
                    self.trader.buy(security=stock,amount=100,price=price)
            except Exception as e:
                print("运行错误:",e)
                print('{}买入有问题'.format(stock))
        #卖出趋势小于25，不在排名前10
        sell_stock_list=[]
        hold_stock=self.trader.position()
        print(hold_stock)
        if hold_stock.shape[0]>0:
            hold_stock_list=hold_stock['证券代码'].tolist()
            for stock in hold_stock_list:
                try:
                    hist=self.data.get_hist_data_em(stock=stock)
                    score=self.analysis_models.mean_line_models(df=hist)
                    if score<=25:
                        sell_stock_list.append(stock)
                except Exception as e:
                    print("运行错误:",e)
                    sell_stock_list.append(None)
        #卖出不在排名前50的
        if hold_stock.shape[0]>0:
            hold_stock_list=hold_stock['证券代码'].tolist()
            for stock in hold_stock_list:
                if stock not in rank_stock_list[:50]:
                    sell_stock_list.append(stock)
        sell_stock_list=list(set(sell_stock_list))
        if len(sell_stock_list):
            for stock in sell_stock_list:
                try:
                    price=self.data.get_spot_data(stock=stock)['最新价']
                    #检查是否可以卖出
                    if self.trader.check_stock_is_av_sell(stock=stock,amount=100):
                        self.trader.sell(security=stock,price=price,amount=100)
                except Exception as e:
                    print("运行错误:",e)
                    print('{}卖出有问题'.format(stock))
if __name__=='__main__':
    trader=trader_strategy(trader_tool='qmt',exe='C:/同花顺软件/同花顺/xiadan.exe',
                tesseract_cmd='C:/Program Files/Tesseract-OCR/tesseract',
                qmt_path='C:/国金QMT交易端模拟/userdata_mini',
                qmt_account='55003682',qmt_account_type='STOCK',slippage=0.01
        )
    trader.connact()
    #测试
    trader.get_buy_sell_data()
    schedule.every().day.at('{}'.format('14:30')).do(trader.get_buy_sell_data)
    while True:
        schedule.run_pending()
        time.sleep(1)
                        



