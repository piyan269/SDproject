import mysql.connector
import time

import mysql.connector
import time

class Mydb:

    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
    
    # 檢查登入的帳密是否存在且正確的方法
    def login(self, account, password):
        conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        cursor = conn.cursor()
        cursor.execute("SELECT `password` FROM `admin` WHERE `account` = %s", (account,))

        for (db_password,) in cursor:
            if db_password == password:
                return True
            else:
                print("Password error.")
                return False

        print("Account not found.")
        return False

    # 商家用來新增物流資訊，將信息加進資料庫
    def addMess(self, account, barcode):
        conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        cursor = conn.cursor()

        cursor.execute("SELECT `company_location`, `company_name` FROM `admin` WHERE account = %s", (account,))
        company_location, company_name = None, None
        for (loc, name) in cursor:
            company_location, company_name = loc, name

        localtime = time.localtime()
        arrive_time = time.strftime("%Y-%m-%d %H:%M:%S", localtime)

        cursor.execute("INSERT INTO `goods` (barcode, company_name, company_location, arrive_time) VALUES (%s, %s, %s, %s);", (barcode, company_name, company_location, arrive_time))
        conn.commit()

    #用來向消費者展示，將信息從資料庫讀出
    def showMess(self, barcode):
        conn = mysql.connector.connect(
            host = self.host,
            user = self.user,
            password = self.password,
            database = self.database
        )
        cursor = conn.cursor()
        cursor.execute("SELECT `company_name`, `company_location`, `arrive_time` FROM `goods` where barcode = '{}'".format(
            barcode))
        
        output = "商品編號: " + barcode + "\n" + "經過:\n"
        for (company_name, company_location, arrive_time) in cursor:
            # 將 arrive_time 轉換為字符串
            arrive_time_str = arrive_time.strftime("%Y-%m-%d %H:%M:%S") if arrive_time else "N/A"
            output += company_name + " " + company_location + " " + arrive_time_str + "\n"

        print(output)

    