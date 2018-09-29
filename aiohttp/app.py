#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from aiohttp import web

app = web.Application()

async def index(request):
    return web.Response(body="<html><h1>rps test</h1></html>", content_type="text/html");

app.router.add_get("/", index)

if __name__ == '__main__':
    web.run_app(app, port=3000)
