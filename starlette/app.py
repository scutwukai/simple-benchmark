#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import uvicorn

import configparser
config = configparser.ConfigParser()
config.read('my.cnf')

import aioredis
import aiomysql

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse

app = Starlette(debug=True)
responses = dict()

@app.route('/(?P<msize>\d+)')
async def homepage(request, msize):
    msize = int(msize)

    if msize not in responses:
        responses[msize] = 'X' * msize

    return PlainTextResponse(responses[msize])

@app.route('/form', methods=['POST'])
async def form(request):
    values = await request.form()
    content = await values['file'].read()

    return PlainTextResponse(str(len(content)))

@app.route('/redis', methods=["POST"])
async def redis(request):
    values = await request.form()
    key = values['key']

    await app.redis.set(key, 'hello redis')
    word = await app.redis.get(key)

    return PlainTextResponse(word.decode('utf-8'))

@app.route('/mysql', methods=["POST"])
async def mysql(request):
    values = await request.form()
    sql = values['sql']

    async with app.mysql.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql)
            value = await cur.fetchone()

            return PlainTextResponse(str(value[0]))


@app.on_event('startup')
async def open_database_connection_pool():
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
    uvicorn.run(app, '127.0.0.1', 3000, log_level='error')
