import mysql.connector
import os
import csv
import creator as C
import reader as R
import inserter as I

"""
Config
在这里改你自己的设置
本地部署只需要改用户名和密码，改成你设置的
然后改一下数据的路径
"""
HOST = "localhost"
USER = "root"
PASSWORD = "20030709"

Fish_Path = r"C:\Users\31460\Desktop\study_file\软件工程\实验\课设\FishData.csv"
Water_Path = r"C:\Users\31460\Desktop\study_file\软件工程\实验\课设\水质数据\water_quality_by_name"

"""
运行区
"""
if __name__ == '__main__':
    '''
    构建数据库脚本
    '''
    print("正在连接数据库...")
    db = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD
    )
    print("数据库已连接...Host：%(host)s, User：%(user)s" % {"host": HOST, "user": USER})
    cursor = db.cursor()  # 创建数据库操作工具

    print("正在创建数据库...")
    C.createDB(cursor)
    print("正在创建数据库表...")
    C.createTB(cursor)
    print("数据库与数据表构建完成。")

    print("插入鱼类数据")
    datas = R.csvreader(Fish_Path)
    for row in datas[1:]:
        I.insertfishdata(cursor, row)
    db.commit()
    print("插入鱼类数据成功")

    # TODO:实现水质数据导入
    # for root, dirs, files in os.walk(Water_Path):
    #     print(root)
    #     print(dirs)
    #     print(files)

    cursor.close()  # 释放数据库工具
