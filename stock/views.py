from django.shortcuts import render, redirect
import requests
import feedparser
import csv
from bs4 import BeautifulSoup
import urllib.request as req
import sys
import io


def search(request):
    return render(request, 'stock/stock_se.html')


def detail(request, stock_id):
    name = get_name(stock_id)
    news = get_google_news(name)
    contents = {'name': name, 'news': news}

    return render(request, "stock/detail.html", contents)


# 주식 코드의 한글 종목명을 가져옴
def get_name(code):
    with open('./stock/res/stock_names.csv', mode='r') as file:
        reader = csv.reader(file)
        names = {rows[0][1:]: rows[1] for rows in reader}
    return names[code]


# 구글 뉴스 가져오기
def get_google_news(keyword, country='ko'):
    URL = 'https://news.google.com/rss/search?q={}+when:1d'.format(keyword)
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
