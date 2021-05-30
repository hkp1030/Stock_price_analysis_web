import csv

with open('./stock/res/stock_names.csv', mode='r') as file:
    reader = csv.reader(file)
    stock_names = {rows[0][1:]: rows[1] for rows in reader}


# 주식 코드의 한글 종목명을 가져옴
def get_stock_name(code):
    return stock_names[code]