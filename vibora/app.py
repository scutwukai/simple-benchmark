#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.parse import parse_qs

import configparser
config = configparser.ConfigParser()
config.read('my.cnf')

import aioredis
import aiomysql

from vibora import Vibora, Request
from vibora.hooks import Events
from vibora.responses import Response



app = Vibora()
responses = dict()

@app.route('/<msize>', cache=False)
async def home(req: Request, msize: int):
    if msize not in responses:
        responses[msize] = b'X' * msize

    return Response(responses[msize], headers={'Content-Type': 'text/plain; charset=utf-8'})

@app.route('/form', methods=['POST'], cache=False)
async def form(req: Request):
    files = await req.files()
    content = await files[0].read()

    return Response(bytes(str(len(content)), 'utf-8'), headers={'Content-Type': 'text/plain; charset=utf-8'})

@app.route('/redis', methods=['POST'], cache=False)
async def redis(req: Request):
    values = parse_qs((await req.stream.read()).decode('utf-8'))
    key = values['key'][0]

    await app.redis.set(key, 'hello redis')
    word = await app.redis.get(key)

    return Response(word, headers={'Content-Type': 'text/plain; charset=utf-8'})

@app.route('/mysql', methods=['POST'], cache=False)
async def mysql(req: Request):
    values = parse_qs((await req.stream.read()).decode('utf-8'))
    sql = values['sql'][0]

    async with app.mysql.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql)
            value = await cur.fetchone()

            return Response(bytes(str(value[0]), 'utf-8'), headers={'Content-Type': 'text/plain; charset=utf-8'})


@app.handle(Events.BEFORE_SERVER_START)
async def before_server_start():
    app.redis = await aioredis.create_redis('redis://localhost')
    app.mysql = await aiomysql.create_pool(
        maxsize=100,
        host=config.get('client', 'host'),
        port=config.getint('client', 'port'),
        user=config.get('client', 'user'),
        password=config.get('client', 'password'),
        db=config.get('client', 'db')
    )

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=3000, workers=1)
