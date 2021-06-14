import csv
import datetime
from django.shortcuts import render, redirect
import requests
import feedparser
from stock.data.link_creon import LinkCreon
from stock.data.static_app import get_stock_name
import json
#from stock.data.networks import network
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


def move_board(request):
    return redirect('/board/search?f=g&b=주식')


def index(request):
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

    list = []
    codelist = []
    for name in STOCK_NAME_LIST[:20]:
        isok = Stock.objects.filter(stock__exact=name)
        if isok:
            list.append(name)
            sname = Stock.objects.get(stock=name)
            code = sname.code
            codelist.append(code)

    return render(request, 'stock/stock_se.html', {'list': list, 'codelist': codelist, 'custom_stock' : custom_stock})


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

    '''
    creon = LinkCreon('D:/PycharmProjects/Stock_price_analysis_web/venv32/Scripts/python.exe', 'stock/data/creon.py')
    stock = creon.get_stock_data(stock_id)
    stock.reverse()
    stock_json = json.dumps(stock)

    results = creon.execute("creon.get_data_to_prediction('{}', 5)".format(stock_id))

    pred = network.predict(results)
    pred = list(map(lambda x: int(x * 100), pred))
    '''

    #contents = {'name': name, 'news': news, 'pred': pred, 'stock_json': stock_json}
    contents = {'name': name, 'news': news}

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


# 주식 코드가 담긴 리스트를 받아서 각 종목의 이름, 주가, 등락률을 반환
def get_stock_info(stocks):
    date = time.strftime('%Y%m%d', time.localtime(time.time()))
    stock_info = stock.get_market_ohlcv_by_ticker(date)

    result = [{'code' : code,
               'name' : Stock.objects.get(code=code).stock,
               'close' : stock_info.loc[code]['종가'],
               'rate' : stock_info.loc[code]['등락률']}
              for code in stocks]
    return result