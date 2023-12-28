from flask import Flask, request, jsonify
from Database import Mydb
import json
from flask import Flask, request, abort
from flask_restful import Resource
import json
import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

# 假設這是您的數據庫連接信息
host = "127.0.0.1"
db_user = "root"
db_password = "root"
database = "project"
port = "3306"

LINE_CHANNEL_TOKEN="LDnZcg+WaxrmiK76VelELkJzWcJEpFyNMNCPeyeJwEyerSMXNTjb+7aXixz3yOz4qI1WMJShZQ4N77hp2rjmyVJrmL2ZaJlc3aNM8gfrBDypk2/DGuhgN/J1CmfGwzooKGYZdB8s0jjXmH3c+HK6ZwdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET_KEY="274cdcb7c8527e33bcfb500bdb319777"
line_bot_api = LineBotApi(LINE_CHANNEL_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET_KEY)

# 創建 Mydb 的實例
db = Mydb(host, port ,db_user, db_password, database)

from flask import render_template

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/CompanyLoginPage')
def CompanyLoginPage():
    return render_template('CompanyLoginPage.html')
@app.route('/CustomerLoginPage')
def CustomerLoginPage():
    return render_template('CustomerLoginPage.html')
@app.route('/addMess')
def addMessPage():
    return render_template('addMess.html')
@app.route('/showMess')
def showMessPage():
    return render_template('showMess.html')

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

@app.route('/loginCustomer', methods=['POST'])
def loginCustomer():
    # 從前端接收數據
    data = request.json
    account = data.get('name')
    password = data.get('password')
    
    # 調用 login 方法
    if db.loginCustomer(account, password):
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
    if message:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'message': 'No details found for this barcode.'}), 404
    

@app.route('/save_order', methods=['POST'])
def save_order():
    data = request.json
    account = data.get('account')
    barcode = data.get('barcode')
    
    result = db.save_order(account, barcode)
    
    return jsonify(result)

@app.route('/get_orders', methods=['POST'])
def get_orders():
    data = request.json
    account = data.get('account')
    orders = db.get_orders(account)
    return jsonify(orders)

@app.route("/webhook", methods=['POST'])
def webhook():
    # 從請求中獲取 X-Line-Signature 頭
    signature = request.headers['X-Line-Signature']

    # 獲取請求體作為文本
    body = request.get_data(as_text=True)

    # 處理 webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 當收到文字訊息時回應同樣的文字
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )

if __name__ == '__main__':
    
    app.run(debug=True, port=8000)
    

