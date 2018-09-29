#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uvicorn


class App():
    def __init__(self, scope):
        self.scope = scope

    async def __call__(self, receive, send):
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                [b'Content-Type', b'text/html; charset=utf-8'],
            ]
        })
        await send({
            'type': 'http.response.body',
            'body': b'<html><h1>rps test</h1></html>',
        })


if __name__ == "__main__":
    uvicorn.run(App, "127.0.0.1", 3000, log_level="error")
