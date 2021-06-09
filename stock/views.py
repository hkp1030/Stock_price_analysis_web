import csv
import time
import datetime
from datetime import timedelta
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

TEMP_DATE = '20210609'


def move_board(request):
    return redirect('/board/search?f=g&b=주식')


def index(request):
    contents = {}

    # 맞춤 종목 불러오기
    by_age, by_gender = get_custom_analytics_data(request.user)
    custom_stock = list_shuffle(by_age, by_gender)
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

    market_updown_kospi = get_상위_하위_등락률(market='KOSPI')
    market_updown_kosdaq = get_상위_하위_등락률(market='KOSDAQ')

    market_updown_kospi_list = {
        '상위' : {
            '종목명' : list(market_updown_kospi[0]['종목명']),
            '종가' : list(market_updown_kospi[0]['종가']),
            '변동폭' : list(market_updown_kospi[0]['변동폭']),
            '등락률' : list(market_updown_kospi[0]['등락률']),
            '거래량' : list(market_updown_kospi[0]['거래량'])
        },
        '하위': {
            '종목명': list(market_updown_kospi[1]['종목명']),
            '종가': list(market_updown_kospi[1]['종가']),
            '변동폭': list(market_updown_kospi[1]['변동폭']),
            '등락률': list(market_updown_kospi[1]['등락률']),
            '거래량': list(market_updown_kospi[1]['거래량'])
        }
    }

    market_updown_kosdaq_list = {
        '상위' : {
            '종목명' : list(market_updown_kosdaq[0]['종목명']),
            '종가' : list(market_updown_kosdaq[0]['종가']),
            '변동폭' : list(market_updown_kosdaq[0]['변동폭']),
            '등락률' : list(market_updown_kosdaq[0]['등락률']),
            '거래량' : list(market_updown_kosdaq[0]['거래량'])
        },
        '하위': {
            '종목명': list(market_updown_kosdaq[1]['종목명']),
            '종가': list(market_updown_kosdaq[1]['종가']),
            '변동폭': list(market_updown_kosdaq[1]['변동폭']),
            '등락률': list(market_updown_kosdaq[1]['등락률']),
            '거래량': list(market_updown_kosdaq[1]['거래량'])
        }
    }

    contents['list'] = list1
    contents['codelist'] = codelist
    contents['custom_stock'] = custom_stock
    contents['market_updown_kospi_list'] = market_updown_kospi_list
    contents['market_updown_kosdaq_list'] = market_updown_kosdaq_list

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
with open('./stock/res/stockitems.csv', mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        Stock(code=row[0][1:], stock=row[1], market=row[2], industry=row[4]).save()
'''

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


    contents = {'name': name, 'news': news, 'pred': pred, 'stock_json': stock_json}
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


# 유저의 나이, 성별을 이용한 맞춤 종목을 분석
def get_custom_analytics_data(user):
    birth = user.birth
    start_date = datetime.date(birth.year-5, 1, 1)
    end_date = datetime.date(birth.year+5, 1, 1)
    gender = user.sex

    by_age = StockVisitHistory.objects.filter(user__birth__range=[start_date, end_date])\
        .values('stock_Code').annotate(Count('stock_Code')).order_by('-stock_Code__count')[:30]
    by_age = [Stock.objects.get(id=stock['stock_Code']).code for stock in by_age]

    by_gender = StockVisitHistory.objects.filter(user__sex=gender)\
        .values('stock_Code').annotate(Count('stock_Code')).order_by('-stock_Code__count')[:30]
    by_gender = [Stock.objects.get(id=stock['stock_Code']).code for stock in by_gender]

    return by_age, by_gender


# 리스트를 합친 후, 섞어서 중복제거하여 num 크기의 리스트 반환
def list_shuffle(*args, num=10):
    total = []
    for l in args:
        total.extend(l)
    random.shuffle(total)
    total = list(set(total))

    return total[:num]

# 유저의 나이, 성별을 이용한 맞춤 종목을 분석
def get_custom_analytics_data(user):
    birth = user.birth
    start_date = datetime.date(birth.year-5, 1, 1)
    end_date = datetime.date(birth.year+5, 1, 1)
    gender = user.sex

    by_age = StockVisitHistory.objects.filter(user__birth__range=[start_date, end_date])\
        .values('stock_Code').annotate(Count('stock_Code')).order_by('-stock_Code__count')[:30]
    by_age = [Stock.objects.get(id=stock['stock_Code']).code for stock in by_age]

    by_gender = StockVisitHistory.objects.filter(user__sex=gender)\
        .values('stock_Code').annotate(Count('stock_Code')).order_by('-stock_Code__count')[:30]
    by_gender = [Stock.objects.get(id=stock['stock_Code']).code for stock in by_gender]

    return by_age, by_gender


# 리스트를 합친 후, 섞어서 중복제거하여 num 크기의 리스트 반환
def list_shuffle(*args, num=10):
    total = []
    for l in args:
        total.extend(l)
    random.shuffle(total)
    total = list(set(total))

    return total[:num]


# 주식 코드가 담긴 리스트를 받아서 각 종목의 이름, 주가, 등락률을 반환
def get_stock_info(stocks):
    #date = time.strftime('%Y%m%d', time.localtime(time.time()))
    date = TEMP_DATE
    print(date)
    stock_info = stock.get_market_ohlcv_by_ticker(date)

    result = [{'code' : code,
               'name' : Stock.objects.get(code=code).stock,
               'close' : stock_info.loc[code]['종가'],
               'rate' : stock_info.loc[code]['등락률']}
              for code in stocks]
    return result

COUNT_INFO = 5
# 개인 / 외국인 / 기관
def get_상위_순매수(market='KOSPI', purchases='개인'):
    #date = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")

    date = TEMP_DATE

    market_net_purchases = \
        stock.get_market_net_purchases_of_equities_by_ticker(date, date, market, purchases)

    market_net_purchases = market_net_purchases.drop(['매도거래량'], axis='columns')
    market_net_purchases = market_net_purchases.drop(['매수거래량'], axis='columns')
    market_net_purchases = market_net_purchases.drop(['매도거래대금'], axis='columns')
    market_net_purchases = market_net_purchases.drop(['매수거래대금'], axis='columns')

    data_s = market_net_purchases.sort_values(by=["순매수거래대금"], ascending=[False])
    data_up = data_s.head(COUNT_INFO)

    return data_up


def get_상위_하위_등락률(market='KOSPI'):
    #date = datetime.today().strftime("%Y%m%d")
    date = TEMP_DATE
    market_price_change = stock.get_market_price_change_by_ticker(date, date)
    market_price_change['등락률'] = [value / 100 for value in market_price_change['등락률'].values]
    market_price_change = market_price_change.drop(['거래대금'], axis='columns')
    market_price_change = market_price_change.drop(['시가'], axis='columns')
    market_price_change_s = market_price_change.sort_values(by=["등락률"], ascending=[False])

    market_price_change_up = market_price_change_s.head(COUNT_INFO)
    market_price_change_down = market_price_change_s.tail(COUNT_INFO).sort_values(by=["등락률"], ascending=[True])

    return market_price_change_up, market_price_change_down
