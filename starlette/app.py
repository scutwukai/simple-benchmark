#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
import uvicorn

app = Starlette(debug=False)
responses = dict()

@app.route('/(?P<msize>\d+)')
def homepage(request, msize):
    msize = int(msize)

    if msize not in responses:
        responses[msize] = 'X' * msize

    return PlainTextResponse(responses[msize])

if __name__ == '__main__':
    uvicorn.run(app, "127.0.0.1", 3000, log_level="error")
