# -*- coding: utf-8 -*-

from gevent import monkey;monkey.patch_all()

import configparser
config = configparser.ConfigParser()
config.read('my.cnf')

import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)

import poolmysql, smartpool
setting = {
    'host': config.get('client', 'host'),
    'port': config.get('client', 'port'),
    'db': config.get('client', 'db'),
    'user': config.get('client', 'user'),
    'passwd': config.get('client', 'password'),
    'charset': 'utf8',
}
smartpool.init_pool('mysql', setting, poolmysql.MySQLdbConnection, 100, clean_interval=1000000)
mysql = smartpool.ConnectionProxy('mysql')

from io import BytesIO
from flask import Flask, request



application = Flask(__name__)
responses = dict()

@application.route('/<int:msize>')
def hello(msize):
    if msize not in responses:
        responses[msize] = 'X' * msize

    return responses[msize], 200, {'Content-Type': 'text/plain; charset=utf-8'}

@application.route('/form', methods=['POST'])
def form():
    content = BytesIO()
    _file = request.files['file']
    _file.save(content)

    content.seek(0)
    content = content.read()

    return str(len(content)), 200, {'Content-Type': 'text/plain; charset=utf-8'}

@application.route('/redis', methods=['POST'])
def Redis():
    key = request.values['key']

    r.set(key, 'hello redis')
    word = r.get(key)

    return word, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@application.route('/mysql', methods=['POST'])
def Mysql():
    sql = request.values['sql']

    query = mysql.select(sql)
    value = query[0]

    return str(value[0]), 200, {'Content-Type': 'text/plain; charset=utf-8'}
