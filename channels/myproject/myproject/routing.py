# -*- coding: utf-8 -*-

import configparser
config = configparser.ConfigParser()
config.read('my.cnf')

import aioredis
import aiomysql

from django.conf.urls import url

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.generic.http import AsyncHttpConsumer

from io import BytesIO
from urllib.parse import parse_qs
from multipart import parse_options_header, MultipartParser


responses = dict()
class BasicHttpConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        msize = int(self.scope['url_route']['kwargs']['msize'])

        if msize not in responses:
            responses[msize] = b'X' * msize

        await self.send_response(200, responses[msize], headers=[
            ('Content-Type', 'text/plain; charset=utf-8'),
        ])

class FormHttpConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        ctype = dict(self.scope['headers'])[b'content-type']
        _, options = parse_options_header(ctype.decode())

        mp = MultipartParser(BytesIO(body), options['boundary'])

        content = '';
        for part in mp.parts():
            if part.filename:
                content = part.value

        await self.send_response(200, b'%d' % len(content), headers=[
            ('Content-Type', 'text/plain; charset=utf-8'),
        ])

redis = None
class RedisHttpConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        global redis
        if redis is None:
            redis = await aioredis.create_redis('redis://localhost')

        key = parse_qs(body.decode('utf-8'))['key'][0]
        await redis.set(key, "hello redis")
        word = await redis.get(key)

        await self.send_response(200, word, headers=[
            ('Content-Type', 'text/plain; charset=utf-8'),
        ])

mysql = None
class MysqlHttpConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        global mysql
        if mysql is None:
            mysql = await aiomysql.create_pool(
                maxsize=100,
                host=config.get('client', 'host'),
                port=config.getint('client', 'port'),
                user=config.get('client', 'user'),
                password=config.get('client', 'password'),
                db=config.get('client', 'db')
            )

        sql = parse_qs(body.decode('utf-8'))['sql'][0]
        async with mysql.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql)
                value = await cur.fetchone()

                await self.send_response(200, bytes(str(value[0]), "utf-8"), headers=[
                    ('Content-Type', 'text/plain; charset=utf-8'),
                ])


application = ProtocolTypeRouter({
    'http': URLRouter([
        url(r'^(?P<msize>\d+)$', BasicHttpConsumer),
        url(r'^form$', FormHttpConsumer),
        url(r'^redis$', RedisHttpConsumer),
        url(r'^mysql$', MysqlHttpConsumer),
    ]),
})
