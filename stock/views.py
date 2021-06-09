import csv

from django.shortcuts import render, redirect
import requests
import feedparser
from stock.data.link_creon import LinkCreon
from stock.data.static_app import get_stock_name
import json

from .models import Stock
import requests
import urllib.request  # 웹에 접근하기 위한 모듈
from bs4 import BeautifulSoup as bs  # 웹 크롤링을 위한 모듈

import sys
import io

def move_board(request):
    return redirect('/board/search?f=g&b=주식')

def move_board(request):
    return redirect('/board/search?f=g&b=주식')


def index(request):

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

        search = request.GET.get('query')

    list = []
    codelist = []
    for name in STOCK_NAME_LIST[:20]:
        isok = Stock.objects.filter(stock__exact=name)
        if isok:
            list.append(name)
            sname = Stock.objects.get(stock=name)
            code = sname.code
            codelist.append(code)

    return render(request, 'stock/stock_se.html', {'list': list, 'codelist': codelist})


def search(request):
    search = request.GET.get('query')
    if Stock.stock == search:
        sname = Stock.objects.get(stock=search)
        code = sname.code
        return redirect('stock:detail', code)
    else:
        return render(request, 'stock/nodata.html')


'''
csv db저장
with open('./stock/res/stock_names.csv', mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        Stock(stock=row[1], code=row[0][1:]).save()
'''


# 주식 상세페이지
def detail(request, stock_id):
    return render(request, "stock/detail.html")


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
