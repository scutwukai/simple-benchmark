#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import uvicorn
from quart import Quart, make_response

app = Quart(__name__)
app.config.from_mapping({'DEBUG': False, 'TESTING': False})

responses = dict()

@app.route('/<int:msize>')
async def hello(msize):
    if msize not in responses:
        responses[msize] = 'X' * msize

    return responses[msize], 200, {'Content-Type': 'text/plain; charset=utf-8'}


if __name__ == '__main__':
    uvicorn.run(app, '127.0.0.1', 3000, log_level='error')
