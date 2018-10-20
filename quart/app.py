#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import uvloop
from io import BytesIO
from logging import getLogger

import configparser
config = configparser.ConfigParser()
config.read('my.cnf')

import aioredis
import aiomysql

from quart import current_app, Quart, request



app = Quart(__name__)
app.config.from_mapping({'DEBUG': False, 'TESTING': False})

responses = dict()
@app.route('/<int:msize>')
async def hello(msize):
    if msize not in responses:
        responses[msize] = 'X' * msize

    return responses[msize], 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/form', methods=["POST"])
async def form():
    content = BytesIO()
    _file = await request.files
    _file["file"].save(content)

    content.seek(0)
    content = content.read()

    return str(len(content)), 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/redis', methods=["POST"])
async def redis():
    key = (await request.values)['key']

    await current_app.redis.set(key, 'hello redis')
    word = await current_app.redis.get(key)

    return word, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/mysql', methods=["POST"])
async def mysql():
    sql = (await request.values)['sql']

    async with current_app.mysql.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql)
            value = await cur.fetchone()

            return str(value[0]), 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.before_serving
async def create_db_pool():
    current_app.redis = await aioredis.create_redis('redis://localhost')
    current_app.mysql = await aiomysql.create_pool(
        maxsize=100,
        host=config.get('client', 'host'),
        port=config.getint('client', 'port'),
        user=config.get('client', 'user'),
        password=config.get('client', 'password'),
        db=config.get('client', 'db')
    )

if __name__ == '__main__':
    logger = getLogger('quart.serving')
    logger.setLevel("ERROR")
    app.run('127.0.0.1', 3000, loop=uvloop.new_event_loop())
