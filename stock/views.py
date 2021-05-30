from django.shortcuts import render, redirect
import requests
import feedparser
from stock.data.link_creon import LinkCreon
from stock.data.static_app import get_stock_name
import json
from stock.data.networks import network
import numpy as np

from .models import Stock
from bs4 import BeautifulSoup
import urllib.request as req
import sys
import io


def index(request):
    return render(request, 'stock/stock_se.html')


def search(request):
    search = request.GET.get('query')
    sname = Stock.objects.get(stock=search)
    code = sname.code

    return redirect('stock:detail', code)


'''
# csv db저장
with open('./stock/res/stock_names.csv', mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        Stock(stock=row[1], code=row[0][1:]).save()
'''


# 주식 상세페이지
def detail(request, stock_id):
    name = get_stock_name(stock_id)
    news = get_google_news(name)

    creon = LinkCreon('D:/PycharmProjects/Stock_price_analysis_web/venv32/Scripts/python.exe', 'stock/data/creon.py')
    stock = creon.get_stock_data(stock_id)
    stock.reverse()
    stock_json = json.dumps(stock)
    #contents = {'name': name, 'news': news, 'stock_json':stock_json}

    results = creon.execute("creon.get_data_to_prediction('{}', 5)".format(stock_id))

    pred = network.predict(results)
    pred = list(map(lambda x: int(x*100), pred))

    contents = {'name': name, 'news': news, 'pred': pred, 'stock_json':stock_json}

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
