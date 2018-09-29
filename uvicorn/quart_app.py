#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import uvicorn
from quart import Quart, make_response

app = Quart(__name__)
app.config.from_mapping({"DEBUG": False, "TESTING": False})

@app.route('/')
async def hello():
    #res = await make_response('<html><h1>rps test</h1></html>')
    #res.headers["Content-Type"] = "text/html; charset=utf-8";
    #return res

    return "<html><h1>rps test</h1></html>", 200, {"Content-Type": "text/html; charset=utf-8"}


if __name__ == '__main__':
    uvicorn.run(app, "127.0.0.1", 3000, log_level="error")
