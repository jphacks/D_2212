# -*- coding: utf-8 -*-
from ast import Store
from crypt import methods
from flask import *
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os

# データベースログインの PASS を取得
load_dotenv(override=True)
PASSWORD = os.getenv('DATABASE_PASSWORD')

app = Flask(__name__)

# 日本語を使えるように
app.config['JSON_AS_ASCII'] = False
app.config['MYSQL_USER'] = 'night'
app.config['MYSQL_PASSWORD'] = PASSWORD
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'test'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# ログイン処理
@app.route('/login/',methods=['POST'])
def CONNECT_DB_USER():
    user = request.form["user"]
    # print(user)
    # フロントからデータを受け取って挿入と照合したい
    cs = mysql.connection.cursor()

    cs.execute("SELECT id FROM users where id = '1'")
    data = cs.fetchall()
    if len(data):
        return jsonify(data)
    else:
        return "新規です"

# 店一覧を表示
@app.route('/stores')
def get_stores():
    
    cs = mysql.connection.cursor()
    cs.execute("SELECT * FROM stores")
    data = cs.fetchall()

    return jsonify(data)

# 来店履歴に登録
@app.route('/come_history',methods=["POST"])
def add_come_history():
    try:
        user_id = request.form["user_id"]
        store_id = request.form["store_id"]
    except:
        return 0
        
    cs = mysql.connection.cursor()
    cs.execute("insert into come_history(user_id,store_id) values("+user_id+","+store_id+")")
    mysql.connection.commit()

    return 0


# メニュー一覧を store_id に応じて返す
@app.route('/menues',methods=["GET"])
def menues():
    req = request.args
    store_id = req.get("store_id")

    cs = mysql.connection.cursor()
    cs.execute("SELECT * FROM menues where store_id="+store_id)
    menues = cs.fetchall()
    # print(menues)
    
    cs.execute("SELECT * FROM menues where recommend=true and store_id="+store_id)
    recommend = cs.fetchall()
    # print(recommend)

    # おすすめはメニューとで重複して渡している
    return jsonify(recommend+menues)#,jsonify(recommend)

# 注文履歴に登録
@app.route('/order_history',methods=["POST"])
def add_order_history():
    try:
        user_id = request.form["user_id"]
        menu_id = request.form["menu_id"]
    except:
        return "0"

    cs = mysql.connection.cursor()
    cs.execute("insert into come_history(user_id,store_id) values("+user_id+","+menu_id+")")
    mysql.connection.commit()
    
    # エラーに応じた番号（値）を戻り値にする
    return "0"

# 達成度を表示(コンプリート画面)
@app.route('/check_complete',methods=["POST"])
def check_complete():
    try:
        user_id = request.form["user_id"]
        store_id = request.form["store_id"]
    except:
        return "0"

    cs = mysql.connection.cursor()
    # mysql における差分集合
    # https://qiita.com/Hiraku/items/71873bf31e503eb1b4e1
    cs.execute("select count(id) from (select menues.id from menues where store_id = "+store_id+\
                " and menues.id not in (\
                  select menu_id from order_history where user_id = "+user_id+")) as not_complete")

    # cs.execute("select id from menues where store_id = "+store_id)
    # cs.execute("select menu_id from order_history where user_id = "+user_id)
    check = cs.fetchall()
    return jsonify(check)
    if check:
        # 制覇率を渡す
        return "60%"
    else:
        return "全てのメニューを制覇しました！"
    
    

if __name__ == '__main__':
    app.debug = True
    app.run(port=8080)