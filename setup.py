from flask import Flask, render_template
from flask import jsonify
from flask import request

app = Flask(__name__)

"""
服务日志
"""


@app.route('/')
def index():
    dict1 = {"index": "hahaha"}
    print(request)
    return jsonify(dict1)


@app.route('/shops/<shop_name>')
def shops(shop_name):
    return shop_name


@app.route('/students', methods=['post'])
def students():
    for key in request.form:
        print('key', key)
    return request


@app.route('/persons', methods=['post'])
def persons():
    return jsonify(
        {
            "username": request.args.get('username'),
            "password": request.args.get('password'),
        }
    )
