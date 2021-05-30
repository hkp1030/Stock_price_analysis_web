import subprocess

class LinkCreon:
    def __init__(self, python_path, py_path):
        self.python_path = python_path
        self.py_path = py_path

    def execute(self, command):
        result = subprocess.check_output(args=[self.python_path, self.py_path, command], encoding='utf-8')
        return eval(result)

    def get_stock_data(self, code):
        results = self.execute("creon.creon_7400_주식차트조회('" + code + "')")
        return results
