import csv
import json
'''
从csv读取并插入数据
'''
def csvreader(Path):
    datas = []
    with open(Path) as f:
        csv_reader = csv.reader(f, delimiter=",")
        for row in csv_reader:
            datas.append(row)

    return datas

