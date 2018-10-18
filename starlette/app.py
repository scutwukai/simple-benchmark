#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uvicorn
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


if __name__ == '__main__':
    uvicorn.run(app, '127.0.0.1', 3000, log_level='error')
