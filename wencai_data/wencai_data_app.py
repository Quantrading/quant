import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory  as fg
import akshare as ak
from dash import html
from dash import dcc
from dash import Input#输入
from dash import Output#输出
import time
from dash import dash_table
import dash
import pandas as pd
import requests
import json
from datetime import datetime
import os
import pywencai
def get_word_result(word='股票'):
    try:
        df=pywencai.get(question=word,loop=True)
        return True,df
    except:
        text='获取失败可能 {}有问题'.format(word)
        return False,text
now_date=str(datetime.now())[:10]
app=dash.Dash(__name__)
app.layout=html.Div([
    html.H1('财经数据智能问答，数据来自网站，单纯的分享,数据获取比较慢耐心等待'),
    html.H3('输入你问题，多个问题逗号分开'),
    dcc.Textarea(value='股票包含可转债',id='wencai_text'),
    html.H5('运行程序'),
    dcc.Dropdown(options=['运行','不运行'],id='wencai_run',value='运行'),
    dcc.RadioItems(options={'下载数据':"下载数据","不下载数据":"不下载数据"},id='wencai_down_data',value='不下载数据'),
    dash_table.DataTable(
        id='wencai_data_table',
        page_size=30,
        style_table={'font-size': 15},
        sort_action='native'),
    dcc.Download(id='wencai_data_table_down') 
])
#回调表
@app.callback(
    Output(component_id='wencai_data_table',component_property='data'),
    Input(component_id='wencai_text',component_property='value'),
    Input(component_id='wencai_run',component_property='value'),
    Input(component_id='wencai_down_data',component_property='value')
)
def show_wencai_data_table(text,run,down_data):
    if run=='运行':
        stats,df=get_word_result(word=text)
        if stats==True:
            return df.to_dict('records')
        else:
            pass
    else:
        pass
#回调下载
@app.callback(
    Output(component_id='wencai_data_table_down',component_property='data'),
    Input(component_id='wencai_text',component_property='value'),
    Input(component_id='wencai_run',component_property='value'),
    Input(component_id='wencai_down_data',component_property='value')
)
def show_wencai_data_table_down(text,run,down_data):
    if down_data=='下载数据':
        stats,df=get_word_result(word=text)
        if stats==True:
            return dcc.send_data_frame(df.to_excel, filename='{}.xlsx'.format(text))
        else:
            pass
    else:
        pass
if __name__=='__main__':
    app.run_server(debug=True)
    #host='0.0.0.0',
    #port=8023 )
