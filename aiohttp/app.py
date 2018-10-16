#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import uvloop;asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from aiohttp import web

app = web.Application()
responses = dict()

async def index(request):
    msize = int(request.match_info["msize"])
    if msize not in responses:
        responses[msize] = 'X' * msize

    return web.Response(body=responses[msize], content_type="text/plain", charset="utf-8");

app.router.add_get("/{msize:\d+}", index)

if __name__ == "__main__":
    web.run_app(app, host="127.0.0.1", port=3000)
