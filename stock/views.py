import csv
import time
import datetime
from datetime import timedelta
from datetime import datetime as datetime2
from django.shortcuts import render, redirect
import requests
import feedparser
from stock.data.link_creon import LinkCreon
from stock.data.static_app import get_stock_name
import json
from stock.data.networks import network
import numpy as np
import pandas as pd
import random
from pykrx import stock
import time

from django.db.models import Count
from .models import Stock
from users.models import User
from users.models import StockVisitHistory
from django.utils import timezone
import requests
import urllib.request  # 웹에 접근하기 위한 모듈
from bs4 import BeautifulSoup as bs  # 웹 크롤링을 위한 모듈

import sys
import io

COUNT_INFO = 5


def move_board(request):
    return redirect('/board/search?f=g&b=주식')


def index(request):
    contents = {}
    # 맞춤 종목 불러오기
    if request.user.is_authenticated:
        custom_stock = get_custom_analytics_data(request.user)
    else:
        custom_stock = get_cap_100()
        custom_stock = list_shuffle(custom_stock, num=10)
        custom_stock = get_stock_info(custom_stock)


    # 인기 검색어 불러오기
    STOCKLIST_URL = "https://finance.naver.com/sise/lastsearch2.nhn"

    response = urllib.request.urlopen(STOCKLIST_URL)
    STOCKLIST_HTML = response.read()
    soup = bs(STOCKLIST_HTML)

    STOCK_NAME_LIST = []

    for tr in soup.findAll('tr'):
        stockName = tr.findAll('a', attrs={'class', 'tltle'})
        if stockName is None or stockName == []:
            pass
        else:
            STOCK_NAME_LIST.append(stockName[0].contents[-1])

    list1 = []
    codelist = []
    for name in STOCK_NAME_LIST[:20]:
        isok = Stock.objects.filter(stock__exact=name)
        if isok:
            list1.append(name)
            sname = Stock.objects.get(stock=name)
            code = sname.code
            codelist.append(code)

    #주식 검색 페이지 - 마켓 트렌드 불러오기
    market_updown_kospi = get_상위_하위_등락률(market='KOSPI')
    market_updown_kosdaq = get_상위_하위_등락률(market='KOSDAQ')

    market_up_list = pd.concat([market_updown_kospi[0],market_updown_kosdaq[0]], axis=1)
    market_down_list = pd.concat([market_updown_kospi[1], market_updown_kosdaq[1]], axis=1)

    market_net_purchases_f = [get_상위_순매수(market='KOSPI', purchases='외국인')
                              , get_상위_순매수(market='KOSDAQ', purchases='외국인')]
    market_net_purchases_n = [get_상위_순매수(market='KOSPI', purchases='개인')
                              , get_상위_순매수(market='KOSDAQ', purchases='개인')]

    market_net_purchases_f_list = pd.concat(market_net_purchases_f, axis=1)
    market_net_purchases_n_list = pd.concat(market_net_purchases_n, axis=1)

    market_trading_change = [get_거래량(market='KOSPI'), get_거래량(market='KOSDAQ')]
    market_trading_change_list = pd.concat(market_trading_change, axis=1)

    contents['list'] = list1
    contents['codelist'] = codelist
    contents['custom_stock'] = custom_stock
    contents['market_up_list'] = market_up_list.to_dict('records')
    contents['market_down_list'] = market_down_list.to_dict('records')
    contents['market_net_purchases_f_list'] = market_net_purchases_f_list.to_dict('records')
    contents['market_net_purchases_n_list'] = market_net_purchases_n_list.to_dict('records')
    contents['market_trading_change_list'] = market_trading_change_list.to_dict('records')

    network.model.summary()

    return render(request, 'stock/stock_se.html', contents)


def search(request):
    search = request.GET.get('query')
    try:
        sname = Stock.objects.get(stock=search)
        code = sname.code
        return redirect('stock:detail', code)
    except:
        return render(request, 'stock/nodata.html')


# csv db저장
'''
with open('./stock/res/stockitems.csv', mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        Stock(code=row[0][1:], stock=row[1], market=row[2], industry=row[4]).save()'''


# 주식 상세페이지
def detail(request, stock_id):
    try:
        stock = Stock.objects.get(code=stock_id)
    except:
        return render(request, 'stock/nodata.html')
    if request.user.is_authenticated:
        StockVisitHistory(user=request.user, stock_Code=stock, time=timezone.now()).save()
    name = get_stock_name(stock_id)
    news = get_google_news(name)


    creon = LinkCreon('D:/PycharmProjects/Stock_price_analysis_web/venv32/Scripts/python.exe', 'stock/data/creon.py')
    stock = creon.get_stock_data(stock_id)
    stock.reverse()
    stock_json = json.dumps(stock)

    results = creon.execute("creon.get_data_to_prediction('{}', 5)".format(stock_id))

    pred = network.predict(results)
    pred = list(map(lambda x: int(x * 100), pred))

    info = creon.get_stock_info(stock_id)
    info['시가총액'] = get_cap(stock_id) / 100000000

    contents = {'name': name, 'news': news, 'pred': pred, 'stock_json': stock_json, 'info': info}
    #contents = {'name': name, 'news': news}

    return render(request, "stock/detail.html", contents)


# 구글 뉴스 가져오기
def get_google_news(keyword, country='ko'):
    URL = 'https://news.google.com/rss/search?q={}+when:7d'.format(keyword)
    if country == 'en':
        URL += '&hl=en-NG&gl=NG&ceid=NG:en'
    elif country == 'ko':
        URL += '&hl=ko&gl=KR&ceid=KR:ko'

    try:
        res = requests.get(URL)
        if res.status_code == 200:
            datas = feedparser.parse(res.text).entries
            for data in datas:
                data['source'] = data.source.title
        else:
            print('Google 검색 에러')
            return None
    except requests.exceptions.RequestException as err:
        print('Error Requests: {}'.format(err))
        return None
    return datas[:5]


# 유저의 나이, 성별, 관심 업종을 분석하여 맞춤 종목을 분석
def get_custom_analytics_data(user):
    birth = user.birth
    start_date = datetime.date(birth.year-5, 1, 1)
    end_date = datetime.date(birth.year+5, 1, 1)
    gender = user.sex

    # 성별 분석
    by_age = StockVisitHistory.objects.filter(user__birth__range=[start_date, end_date])\
        .values('stock_Code').annotate(Count('stock_Code')).order_by('-stock_Code__count')[:30]
    by_age = [Stock.objects.get(id=stock['stock_Code']).code for stock in by_age]

    # 나이 분석
    by_gender = StockVisitHistory.objects.filter(user__sex=gender)\
        .values('stock_Code').annotate(Count('stock_Code')).order_by('-stock_Code__count')[:30]
    by_gender = [Stock.objects.get(id=stock['stock_Code']).code for stock in by_gender]

    # 관심 업종 분석
    by_cat = list(
        StockVisitHistory.objects.filter(user=user)
            .values('stock_Code__industry')
            .annotate(Count('stock_Code__industry'))
            .order_by('-stock_Code__industry__count')[:3]
    )
    by_cat_sum = sum([data['stock_Code__industry__count'] for data in by_cat])
    by_cat = {data['stock_Code__industry']: data['stock_Code__industry__count'] / by_cat_sum for data in by_cat}
    by_cat_stock = {}
    for cat, value in by_cat.items():
        stock_list = list(Stock.objects.filter(industry=cat))
        by_cat_stock[cat] = list_shuffle(stock_list, num=30)
    by_cat_final = []
    for cat, value in by_cat_stock.items():
        by_cat_final.extend(value[:int(30*by_cat[cat])])
    by_cat_final = [stock.code for stock in by_cat_final]

    # 합치기
    result = list_shuffle(by_age, by_gender, by_cat_final, num=10)
    result = get_stock_info(result)

    return result


# 리스트를 합친 후, 섞어서 중복제거하여 num 크기의 리스트 반환
def list_shuffle(*args, num=10):
    total = []
    for l in args:
        total.extend(l)
    random.shuffle(total)
    result = []
    for data in total:
        if data not in result:
            result.append(data)

    return result[:num]


# 주식 코드가 담긴 리스트를 받아서 각 종목의 이름, 주가, 등락률을 반환
def get_stock_info(stocks):
    date = get_date()
    stock_info = stock.get_market_ohlcv_by_ticker(date, market="ALL")

    result = [{'code' : code,
               'name' : Stock.objects.get(code=code).stock,
               'close' : stock_info.loc[code]['종가'],
               'rate' : stock_info.loc[code]['등락률']}
              for code in stocks]
    return result



def get_거래량(market='KOSPI'):
    date = get_date()

    market_price_change_a = stock.get_market_ohlcv_by_ticker(date, market=market)

    market_price_change_a['변동폭'] = [int(close - (close / (1+(ratio/100)))) for close, ratio in
                                    zip(market_price_change_a['종가'].values, market_price_change_a['등락률'].values)]



    market_price_change_a = market_price_change_a.drop(['시가'], axis='columns')
    market_price_change_a = market_price_change_a.drop(['고가'], axis='columns')
    market_price_change_a = market_price_change_a.drop(['저가'], axis='columns')
    market_price_change_a = market_price_change_a.drop(['거래대금'], axis='columns')

    market_price_change_a_s = market_price_change_a.sort_values(by=["거래량"], ascending=[False])

    market_price_change_a_up = market_price_change_a_s.head(COUNT_INFO)
    market_price_change_a_up["종목명"] = [stock.get_market_ticker_name(value) for value in
                                       market_price_change_a_up.index.values]

    market_price_change_a_up = market_price_change_a_up.reset_index(drop=False)
    market_price_change_a_up = market_price_change_a_up.rename(columns={'티커': market + '티커'})
    market_price_change_a_up = market_price_change_a_up.rename(columns={'종가': market + '종가'})
    market_price_change_a_up = market_price_change_a_up.rename(columns={'거래량': market + '거래량'})
    market_price_change_a_up = market_price_change_a_up.rename(columns={'등락률': market + '등락률'})
    market_price_change_a_up = market_price_change_a_up.rename(columns={'변동폭': market + '변동폭'})
    market_price_change_a_up = market_price_change_a_up.rename(columns={'종목명': market + '종목명'})

    return market_price_change_a_up

# 개인 / 외국인 / 기관
def get_상위_순매수(market='KOSPI', purchases='외국인'):
    date = get_date()

    market_net_purchases = \
        stock.get_market_net_purchases_of_equities_by_ticker(date, date, market, purchases)

    market_net_purchases = market_net_purchases.drop(['매도거래량'], axis='columns')
    market_net_purchases = market_net_purchases.drop(['매수거래량'], axis='columns')
    market_net_purchases = market_net_purchases.drop(['매도거래대금'], axis='columns')
    market_net_purchases = market_net_purchases.drop(['매수거래대금'], axis='columns')

    data_s = market_net_purchases.sort_values(by=["순매수거래대금"], ascending=[False])

    data_up = data_s.head(COUNT_INFO)

    data_up = data_up.reset_index(drop=False)
    data_up = data_up.rename(columns={'티커': market + '티커'})
    data_up = data_up.rename(columns={'종목명': market + '종목명'})
    data_up = data_up.rename(columns={'순매수거래량': market + '순매수거래량'})
    data_up = data_up.rename(columns={'순매수거래대금': market + '순매수거래대금'})

    return data_up


def get_상위_하위_등락률(market='KOSPI'):
    date = get_date()

    market_price_change_a = stock.get_market_ohlcv_by_ticker(date, market=market)

    market_price_change_a['변동폭'] = [int(close - (close / (1 + (ratio / 100)))) for close, ratio in
                                    zip(market_price_change_a['종가'].values, market_price_change_a['등락률'].values)]

    market_price_change_a = market_price_change_a.drop(['시가'], axis='columns')
    market_price_change_a = market_price_change_a.drop(['고가'], axis='columns')
    market_price_change_a = market_price_change_a.drop(['저가'], axis='columns')
    # market_price_change_a = market_price_change_a.drop(['종가'], axis='columns')
    # market_price_change_a = market_price_change_a.drop(['거래량'], axis='columns')
    market_price_change_a = market_price_change_a.drop(['거래대금'], axis='columns')

    market_price_change_a_s = market_price_change_a.sort_values(by=["등락률"], ascending=[False])

    market_price_change_a_s = market_price_change_a_s.rename(columns={'티커': market + '티커'})
    market_price_change_a_s = market_price_change_a_s.rename(columns={'종가': market + '종가'})
    market_price_change_a_s = market_price_change_a_s.rename(columns={'거래량': market + '거래량'})
    market_price_change_a_s = market_price_change_a_s.rename(columns={'등락률': market + '등락률'})
    market_price_change_a_s = market_price_change_a_s.rename(columns={'변동폭': market + '변동폭'})
    market_price_change_a_s = market_price_change_a_s.rename(columns={'종목명': market + '종목명'})

    market_price_change_a_up = market_price_change_a_s.head(COUNT_INFO)
    market_price_change_a_up[market + "종목명"] = [stock.get_market_ticker_name(value) for value in
                                       market_price_change_a_up.index.values]
    market_price_change_a_up = market_price_change_a_up.reset_index(drop=False)

    market_price_change_a_down = market_price_change_a_s.tail(COUNT_INFO).sort_values(by=[market + "등락률"], ascending=[True])
    market_price_change_a_down[market + "종목명"] = [stock.get_market_ticker_name(value) for value in
                                         market_price_change_a_down.index.values]
    market_price_change_a_down = market_price_change_a_down.reset_index(drop=False)

    return market_price_change_a_up, market_price_change_a_down

def get_cap(code):
    date = get_date()
    df = stock.get_market_cap_by_date(date, date, code)
    return df.head()['시가총액'].values[0]

def get_cap_100():
    date = get_date()
    df = stock.get_market_cap_by_ticker(date)
    df = df.sort_values(by=["시가총액"], ascending=[False])
    df = df.index.values

    return df[:100]


def get_date():
    date = datetime2.today().strftime("%Y%m%d")
    df = stock.get_market_ohlcv_by_date('20210610', date, "005930")

    ts = pd.to_datetime(str(df.tail(1).index.values[0]))
    return ts.strftime("%Y%m%d")