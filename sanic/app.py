#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sanic import Sanic, response

app = Sanic()

@app.route('/')
async def test(request):
    return response.text(
        "<html><h1>rps test</h1></html>",
        headers={"Content-Type": "text/html; charset=utf-8"},
        status=200
    )

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000, access_log=False)
