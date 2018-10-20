#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import uvloop;asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

import configparser
config = configparser.ConfigParser()
config.read('my.cnf')

import aioredis
import aiomysql

from aiohttp import web



app = web.Application()
responses = dict()

async def index(request):
    msize = int(request.match_info['msize'])
    if msize not in responses:
        responses[msize] = 'X' * msize

    return web.Response(body=responses[msize], content_type='text/plain', charset='utf-8');

async def form(request):
    reader = await request.multipart()

    content = ''
    while True:
        part = await reader.next()
        if part is None:
            break

        if part.name == 'file':
            content = await part.read(decode=False)
            break

    return web.Response(body=b'%d' % len(content), content_type='text/plain', charset='utf-8');

async def redis(request):
    form = await request.post()
    key = form['key']

    await app['redis'].set(key, 'hello redis')
    word = await app['redis'].get(key)

    return web.Response(body=word, content_type='text/plain', charset='utf-8');

async def mysql(request):
    form = await request.post()
    sql = form['sql']

    async with app['mysql'].acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql)
            value = await cur.fetchone()

            return web.Response(body=bytes(str(value[0]), 'utf-8'), content_type='text/plain', charset='utf-8');


app.router.add_get('/{msize:\d+}', index)
app.router.add_post('/form', form)
app.router.add_post('/redis', redis)
app.router.add_post('/mysql', mysql)


async def create_conn(current_app):
    current_app['redis'] = await aioredis.create_redis('redis://localhost')
    current_app['mysql'] = await aiomysql.create_pool(
        maxsize=100,
        host=config.get('client', 'host'),
        port=config.getint('client', 'port'),
        user=config.get('client', 'user'),
        password=config.get('client', 'password'),
        db=config.get('client', 'db')
    )

app.on_startup.append(create_conn)


if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=3000)
