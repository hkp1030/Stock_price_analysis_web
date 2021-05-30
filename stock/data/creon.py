import time
import win32com.client
import pandas as pd
import sys
import time
import csv
import data_manager


class Creon:
    def __init__(self):
        #creon_7400_주식차트조회
        self.obj_CpCodeMgr = win32com.client.Dispatch('CpUtil.CpCodeMgr')
        self.obj_CpCybos = win32com.client.Dispatch('CpUtil.CpCybos')
        self.obj_StockChart = win32com.client.Dispatch('CpSysDib.StockChart')

        # creon_7818_금리지표
        self.obj_gook = win32com.client.Dispatch('Dscbo1.CpSvr7818C')

        # creon_7059_주식지수
        self.obj_MarketEye = win32com.client.Dispatch('CpSysDib.MarketEye')

    # 한국 국채 3년
    def creon_7818_국채(self):
        self.obj_gook.SetInputValue(0, '09')
        self.obj_gook.SetInputValue(1, '2')

        self.obj_gook.BlockRequest()


        status = self.obj_gook.GetDibStatus()
        msg = self.obj_gook.GetDibMsg1()
        # print("통신상태: {} {}".format(status, msg))

        if status != 0:
            return None

        cnt = self.obj_gook.GetHeaderValue(0)  # 수신개수

        stock_list = []

        for i in range(cnt):
            dict_item = {}

            dict_item['date'] = self.obj_gook.GetDataValue(0, i)
            dict_item['close'] = self.obj_gook.GetDataValue(1, i) * 0.1

            stock_list.append(dict_item)

        return stock_list

    # 0=종목코드, 4=현재가, 67=PER, 77=ROE, BPS=89, PBR = 현재가 / BPS
    def creon_7059_주식지수(self, code):

        self.obj_MarketEye.SetInputValue(0, [0, 4, 67, 77, 89])
        self.obj_MarketEye.SetInputValue(1, 'A'+code)
        self.obj_MarketEye.SetInputValue(2, '1')

        self.obj_MarketEye.BlockRequest()

        status = self.obj_MarketEye.GetDibStatus()
        msg = self.obj_MarketEye.GetDibMsg1()
        # print("통신상태: {} {}".format(status, msg))

        if status != 0:
            return None

        stock_dict = {}

        stock_dict['per'] = self.obj_MarketEye.GetDataValue(2, 0)
        stock_dict['pbr'] = self.obj_MarketEye.GetDataValue(1, 0) / self.obj_MarketEye.GetDataValue(4, 0)
        stock_dict['roe'] = self.obj_MarketEye.GetDataValue(3, 0)

        return stock_dict

    # 코스피 - U001
    def creon_7400_코스피(self):
        b_connected = self.obj_CpCybos.IsConnect
        if b_connected == 0:
            #print("연결 실패")
            return None

        list_field_key = [0, 5]
        list_field_name = ['date', 'close']
        dict_chart = {name: [] for name in list_field_name}

        self.obj_StockChart.SetInputValue(0, 'U001')
        self.obj_StockChart.SetInputValue(1, ord('2'))  # 0: 개수, 1: 기간
        self.obj_StockChart.SetInputValue(4, 180) # 갯수
        self.obj_StockChart.SetInputValue(5, list_field_key)  # 필드
        self.obj_StockChart.SetInputValue(6, ord('D'))  # 'D', 'W', 'M', 'm', 'T'
        self.obj_StockChart.SetInputValue(7, 1)
        self.obj_StockChart.BlockRequest()

        status = self.obj_StockChart.GetDibStatus()

        if status != 0:
            return None

        cnt = self.obj_StockChart.GetHeaderValue(3)  # 수신개수

        stock_list = []

        for i in range(cnt):
            dict_item = {}


            dict_item['date'] = self.obj_StockChart.GetDataValue(0, i)
            dict_item['close'] = self.obj_StockChart.GetDataValue(1, i)

            stock_list.append(dict_item)

        return stock_list

    def creon_7400_주식차트조회(self, code, salary='m', scale=5):
        b_connected = self.obj_CpCybos.IsConnect
        if b_connected == 0:
            #print("연결 실패")
            return None

        list_field_key = [0, 1, 2, 3, 4, 5, 8]
        list_field_name = ['date', 'time', 'open', 'high', 'low', 'close', 'volume']
        dict_chart = {name: [] for name in list_field_name}

        salary = ord(salary)

        self.obj_StockChart.SetInputValue(0, 'A'+code)
        self.obj_StockChart.SetInputValue(1, ord('2'))  # 2: 개수, 1: 기간
        self.obj_StockChart.SetInputValue(4, 10000) # 갯수
        self.obj_StockChart.SetInputValue(5, list_field_key)  # 필드
        self.obj_StockChart.SetInputValue(6, salary)  # 'D', 'W', 'M', 'm', 'T'
        self.obj_StockChart.SetInputValue(7, scale)

        self.obj_StockChart.BlockRequest()

        status = self.obj_StockChart.GetDibStatus()

        if status != 0:
            return None

        cnt = self.obj_StockChart.GetHeaderValue(3)  # 수신개수

        stock_list = []

        for i in range(cnt):
            dict_item = {}

            date = self.obj_StockChart.GetDataValue(0, i)
            date_time = self.obj_StockChart.GetDataValue(1, i)

            str_time = str(date) + str(date_time).zfill(4)
            t = time.strptime(str_time, '%Y%m%d%H%M')

            dict_item['date'] = date
            dict_item['time'] = date_time
            dict_item['date_sec'] = int(time.mktime(t))
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

    def get_data_to_prediction(self, code, num_step):
        dict_data_kospi = self.creon_7400_코스피()
        df_kospi = pd.DataFrame(dict_data_kospi)
        df_kospi = df_kospi.rename(columns={'close': 'close_kospi'})

        dict_data_stock = self.creon_7400_주식차트조회(code, 'D', 1)
        df_stock = pd.DataFrame(dict_data_stock)

        dict_data_bond = self.creon_7818_국채()
        df_bond = pd.DataFrame(dict_data_bond)
        df_bond = df_bond.rename(columns={'close': 'close_bond'})

        dict_data_7059 = self.creon_7059_주식지수(code)

        data = pd.merge(df_bond, df_kospi, "left", "date")
        data = pd.merge(data, df_stock, "left", "date")

        data['per'] = dict_data_7059['per']
        data['pbr'] = dict_data_7059['pbr']
        data['roe'] = dict_data_7059['roe']

        data = data.sort_values(by='date', ascending=True).reset_index()

        windows = [5, 20, 60, 120]
        for window in windows:
            data['market_kospi_ma{}'.format(window)] = data['close_kospi'].rolling(window).mean()
            data['market_kospi_ma{}_ratio'.format(window)] = (data['close_kospi'] - data[
                'market_kospi_ma{}'.format(window)]) / \
                                                             data['market_kospi_ma{}'.format(window)]

            data['bond_k3y_ma{}'.format(window)] = data['close_bond'].rolling(window).mean()
            data['bond_k3y_ma{}_ratio'.format(window)] = (data['close_bond'] - data['bond_k3y_ma{}'.format(window)]) / \
                                                         data['bond_k3y_ma{}'.format(window)]

        data = data[['date', 'open', 'high', 'low', 'close', 'volume', 'per', 'pbr', 'roe', 'market_kospi_ma5_ratio',
                     'market_kospi_ma20_ratio', 'market_kospi_ma60_ratio', 'market_kospi_ma120_ratio',
                     'bond_k3y_ma5_ratio', 'bond_k3y_ma20_ratio', 'bond_k3y_ma60_ratio', 'bond_k3y_ma120_ratio']]

        date_start = str(data['date'].iloc[-num_step])
        date_end = str(data['date'].iloc[-1])

        data = data_manager.load_data(data, date_start, date_end, 'v2',  False)[1]
        data = data.values.tolist()

        return [d + [0.5, 0.5] for d in data]


if __name__ == '__main__':
    creon = Creon()
    print(eval(sys.argv[1]))