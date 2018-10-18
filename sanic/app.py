#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sanic import Sanic, response

app = Sanic()
responses = dict()

@app.route('/<msize:int>')
async def test(request, msize):
    if msize not in responses:
        responses[msize] = 'X' * msize

    return response.text(
        responses[msize],
        headers={"Content-Type": "text/html; charset=utf-8"},
        status=200
    )

@app.route('/form', methods=['POST'])
async def form(request):
    content = b''
    for v in request.files.values():
        content = v[0].body
        break

    return response.text(
        '%d' % len(content),
        headers={"Content-Type": "text/html; charset=utf-8"},
        status=200
    )


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000, access_log=False)
