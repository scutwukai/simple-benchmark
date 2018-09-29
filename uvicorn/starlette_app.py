#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from starlette.applications import Starlette
from starlette.responses import HTMLResponse
import uvicorn

app = Starlette(debug=False)

@app.route('/')
def homepage(request):
    return HTMLResponse("<html><h1>rps test</h1></html>")

if __name__ == '__main__':
    uvicorn.run(app, "127.0.0.1", 3000, log_level="error")
