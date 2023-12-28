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
host = "0.tcp.jp.ngrok.io"
db_user = "root"
db_password = "root"
database = "project"
port = 18787

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
    
    user_ids = db.get_user_ids_by_barcode(barcode)
    result = db.showMess(barcode)
    # 生成包含所有
    count = 0
    all_details_message = 'All updates:\n\n'
    
    for item in result['results']:
        all_details_message += f"No.{count+1}\n"
        all_details_message += f"Company Name: {item['company_name']}\nLocation: {item['company_location']}\nArrive Time: {item['arrive_time']}\n\n"
        count += 1
    print(all_details_message)
    
    if result['results']:
        latest_update = result['results'][-1]
        latest_update_message = (f"Latest Update:\nCompany Name: {latest_update['company_name']}, "
                                 f"Location: {latest_update['company_location']}, "
                                 f"Arrive Time: {latest_update['arrive_time']}\n\n")
    else:
        latest_update_message = "No latest update details available.\n\n"
    

    for user_id in user_ids:
        message = latest_update_message + all_details_message
        #line_bot_api.push_message(user_id, TextSendMessage(text=message))
        line_bot_api.push_message(user_id, TextSendMessage(text=message))
    
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
    user_message = event.message.text
    user_id = event.source.user_id
    if user_message.startswith('barcode:'):
        barcode = user_message.split(':', 1)[1]
        result = db.showMess(barcode)
        count=0
        reply_message = 'Result is:\n\n'
        for item in result['results']:
            reply_message += f"No.{count+1}\n"
            reply_message += f"Company Name: {item['company_name']}\n Location: {item['company_location']}\n Arrive Time: {item['arrive_time']}\n\n"
            count+=1
        if count==0: reply_message = "No result QQ"

    elif user_message.startswith("Register:"):
        barcode = user_message.split(":", 1)[1]
        db.save_user_barcode(user_id, barcode)
        reply_text = f"Barcode registered: {barcode}"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        #line_bot_api.push_message(user_id, TextSendMessage(text='Hello World!!!'))

    else:
        reply_message = "I don't understand"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )

if __name__ == '__main__':
    
    app.run(debug=True, port=8000)
    

