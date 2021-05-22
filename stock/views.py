from django.shortcuts import render
import requests
import feedparser
from stock import static_app


# 주식 상세페이지
def detail(request, stock_id):
    name = get_stock_name(stock_id)
    news = get_google_news(name)
    contents = {'name': name, 'news': news}

    return render(request, "stock/detail.html", contents)


# 주식 코드의 한글 종목명을 가져옴
def get_stock_name(code):
    return static_app.stock_names[code]

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
