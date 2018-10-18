#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import uvloop
from io import BytesIO
from logging import getLogger
from quart import Quart, request



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


if __name__ == '__main__':
    logger = getLogger('quart.serving')
    logger.setLevel("ERROR")
    app.run('127.0.0.1', 3000, loop=uvloop.new_event_loop())
