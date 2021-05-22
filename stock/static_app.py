import csv

with open('./stock/res/stock_names.csv', mode='r') as file:
    reader = csv.reader(file)
    stock_names = {rows[0][1:]: rows[1] for rows in reader}


