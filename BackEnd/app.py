from flask import Flask, request, jsonify
from Database import Mydb
import json

app = Flask(__name__)

# 假設這是您的數據庫連接信息
host = "127.0.0.1"
db_user = "root2"
db_password = "root"
database = "project"

# 創建 Mydb 的實例
db = Mydb(host, db_user, db_password, database)
from flask import render_template

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/CompanyLoginPage')
def CompanyLoginPage():
    return render_template('CompanyLoginPage.html')
@app.route('/addMess')
def addMessPage():
    return render_template('addMess.html')

@app.route('/login', methods=['POST'])
def login():
    # 從前端接收數據
    data = request.json
    account = data.get('name')
    password = data.get('password')
    
    # 調用 login 方法
    if db.login(account, password):
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Login failed'}), 401




@app.route('/add_message', methods=['POST'])
def add_message():
    data = request.json
    account = data['account']
    barcode = data['barcode']
    db.addMess(account, barcode)
    return jsonify({'success': True}), 200

@app.route('/show_message/<barcode>', methods=['GET'])
def show_message(barcode):
    message = db.showMess(barcode)
    return jsonify({'message': message}), 200
if __name__ == '__main__':
    app.run(debug=True)
