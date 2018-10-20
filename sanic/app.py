#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
config = configparser.ConfigParser()
config.read('my.cnf')

import aioredis
import aiomysql

from sanic import Sanic, response



app = Sanic()
responses = dict()

@app.route('/<msize:int>')
async def test(request, msize):
    if msize not in responses:
        responses[msize] = 'X' * msize

    return response.text(
        responses[msize],
        headers={'Content-Type': 'text/html; charset=utf-8'},
        status=200
    )

@app.route('/form', methods=['POST'])
async def form(request):
    content = b''
    for v in request.files.values():
        content = v[0].body
        break

    return response.text(
        '%d' % len(content),
        headers={'Content-Type': 'text/html; charset=utf-8'},
        status=200
    )

@app.route('/redis', methods=['POST'])
async def redis(request):
    key = request.form.get('key')

    await app.redis.set(key, 'hello redis')
    word = await app.redis.get(key)

    return response.text(
        word.decode('utf-8'),
        headers={'Content-Type': 'text/html; charset=utf-8'},
        status=200
    )

@app.route('/mysql', methods=['POST'])
async def mysql(request):
    sql = request.form.get('sql')

    async with app.mysql.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql)
            value = await cur.fetchone()

            return response.text(
                str(value[0]),
                headers={'Content-Type': 'text/html; charset=utf-8'},
                status=200
            )


@app.listener('before_server_start')
async def notify_server_started(app, loop):
    app.redis = await aioredis.create_redis('redis://localhost')
    app.mysql = await aiomysql.create_pool(
        maxsize=100,
        host=config.get('client', 'host'),
        port=config.getint('client', 'port'),
        user=config.get('client', 'user'),
        password=config.get('client', 'password'),
        db=config.get('client', 'db'),
        loop=loop
    )

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000, access_log=False)
