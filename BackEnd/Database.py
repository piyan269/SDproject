import mysql.connector
import time

class Mydb:

    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.conn = mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def _get_cursor(self):
        try:
            return self.conn.cursor()
        except mysql.connector.errors.OperationalError:
            self.conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return self.conn.cursor()

    
    def close(self):
        self.conn.close()

    
    # 檢查登入的帳密是否存在且正確的方法
    def login(self, account, password):
        cursor = self._get_cursor()
        cursor.execute("SELECT `password` FROM `admin` WHERE `account` = %s", (account,))

        for (db_password,) in cursor:
            if db_password == password:
                return True
            else:
                print("Password error.")
                return False

        print("Account not found.")
        return False
    def loginCustomer(self, account, password):
        cursor = self._get_cursor()
        cursor.execute("SELECT `password` FROM `customer` WHERE `account` = %s", (account,))

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
        cursor = self._get_cursor()

        cursor.execute("SELECT `company_location`, `company_name` FROM `admin` WHERE account = %s", (account,))
        company_location, company_name = None, None
        #print("OK")
        for (loc, name) in cursor:
            company_location, company_name = loc, name

        localtime = time.localtime()
        arrive_time = time.strftime("%Y-%m-%d %H:%M:%S", localtime)

        cursor.execute("INSERT INTO `goods` (barcode, company_name, company_location, arrive_time) VALUES (%s, %s, %s, %s);", (barcode, company_name, company_location, arrive_time))
        self.conn.commit()

    #用來向消費者展示，將信息從資料庫讀出
    def showMess(self, barcode):
        cursor = self._get_cursor()
        cursor.execute("SELECT `company_name`, `company_location`, `arrive_time` FROM `goods` WHERE `barcode` = %s", (barcode,))

        # 初始化一個列表來存儲所有的信息
        results = []
        for (company_name, company_location, arrive_time) in cursor:
            # 將每條記錄轉換為字典
            results.append({
                'company_name': company_name,
                'company_location': company_location,
                'arrive_time': arrive_time.strftime("%Y-%m-%d %H:%M:%S") if arrive_time else "N/A"
            })
        #print(results)
        # 確保關閉數據庫連接
        cursor.close()
        self.conn.close()

        # 返回JSON格式的數據
        return {'barcode': barcode, 'results': results}


    def save_order(self, account, barcode):
        cursor = self._get_cursor()
        try:
            cursor.execute("INSERT INTO `order` (account, barcode) VALUES (%s, %s)", (account, barcode))
            self.conn.commit()
            return {'success': True, 'message': 'Order saved successfully'}
        except mysql.connector.Error as err:
            self.conn.rollback()
            print(f"Error: {err}")
            return {'success': False, 'message': 'Failed to save order'}
        finally:
            cursor.close()
            self.conn.close()

    def get_orders(self, account):
        cursor = self._get_cursor()
        try:
            cursor.execute("SELECT DISTINCT barcode FROM `Order` WHERE account = %s", (account,))
            orders = cursor.fetchall() 
            order_details = []

            for order in orders:
                barcode = order[0]
                cursor.execute("SELECT `company_name`, `company_location`, `arrive_time` FROM `goods` WHERE `barcode` = %s", (barcode,))
                details = cursor.fetchall()
                details_list = [{'company_name': detail[0], 'company_location': detail[1], 'arrive_time': detail[2].strftime("%Y-%m-%d %H:%M:%S") if detail[2] else "N/A"} for detail in details]
                order_details.append({'barcode': barcode, 'details': details_list})

            return order_details
        except mysql.self.connector.Error as err:
            print(f"Error: {err}")
            return []
        finally:
            cursor.close()
            self.conn.close()

    def save_user_barcode(self, user_id, barcode):
        cursor = self._get_cursor()
        query = "INSERT INTO user_barcode (user_id, barcode) VALUES (%s, %s)"
        cursor.execute(query, (user_id, barcode))
        self.conn.commit()
        cursor.close()

    def get_user_ids_by_barcode(self, barcode):
        cursor = self._get_cursor()
        query = "SELECT user_id FROM user_barcode WHERE barcode = %s"
        cursor.execute(query, (barcode,))
        user_ids = [row[0] for row in cursor]
        cursor.close()
        return user_ids