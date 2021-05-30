import time
import win32com.client
import pandas as pd
import sys
import time
import csv


class Creon:
    def __init__(self):
        self.obj_CpCodeMgr = win32com.client.Dispatch('CpUtil.CpCodeMgr')
        self.obj_CpCybos = win32com.client.Dispatch('CpUtil.CpCybos')
        self.obj_StockChart = win32com.client.Dispatch('CpSysDib.StockChart')

    def creon_7400_주식차트조회(self, code):
        b_connected = self.obj_CpCybos.IsConnect
        if b_connected == 0:
            print("연결 실패")
            return None

        list_field_key = [0, 1, 2, 3, 4, 5, 8]
        list_field_name = ['date', 'time', 'open', 'high', 'low', 'close', 'volume']
        dict_chart = {name: [] for name in list_field_name}

        self.obj_StockChart.SetInputValue(0, 'A'+code)
        self.obj_StockChart.SetInputValue(1, ord('2'))  # 0: 개수, 1: 기간
        self.obj_StockChart.SetInputValue(4, 10000) # 갯수
        self.obj_StockChart.SetInputValue(5, list_field_key)  # 필드
        self.obj_StockChart.SetInputValue(6, ord('m'))  # 'D', 'W', 'M', 'm', 'T'
        self.obj_StockChart.SetInputValue(7, 5)
        self.obj_StockChart.BlockRequest()

        status = self.obj_StockChart.GetDibStatus()
        msg = self.obj_StockChart.GetDibMsg1()
        #print("통신상태: {} {}".format(status, msg))

        if status != 0:
            return None

        cnt = self.obj_StockChart.GetHeaderValue(3)  # 수신개수

        stock_list = []

        for i in range(cnt):
            dict_item = {}

            str_time = str(self.obj_StockChart.GetDataValue(0, i)) + str(self.obj_StockChart.GetDataValue(1, i))
            t = time.strptime(str_time, '%Y%m%d%H%M')

            dict_item['date'] = int(time.mktime(t))
            dict_item['open'] = self.obj_StockChart.GetDataValue(2, i)
            dict_item['high'] = self.obj_StockChart.GetDataValue(3, i)
            dict_item['low'] = self.obj_StockChart.GetDataValue(4, i)
            dict_item['close'] = self.obj_StockChart.GetDataValue(5, i)
            dict_item['volume'] = self.obj_StockChart.GetDataValue(6, i)

            stock_list.append(dict_item)

        return stock_list


    def get_all_stock_data(self):
        with open('./stockitems.csv', mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            code_list = [code[0][1:] for code in list(reader)[1:]]

        all_stock_dict = {}

        for code in code_list:
            time.sleep(0.25)
            stock = self.creon_7400_주식차트조회(code)
            all_stock_dict[code] = stock
            # print(code)

        return all_stock_dict

if __name__ == '__main__':
    creon = Creon()
    print(eval(sys.argv[1]))