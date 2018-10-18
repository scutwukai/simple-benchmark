# -*- coding: utf-8 -*-

from gevent import monkey;monkey.patch_all()

from io import BytesIO
from flask import Flask, request
application = Flask(__name__)



@application.route("/<int:msize>")
def hello(msize):
    return "X" * msize, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@application.route("/form", methods=["POST"])
def form():
    content = BytesIO()
    _file = request.files["file"]
    _file.save(content)

    content.seek(0)
    content = content.read()

    return str(len(content)), 200, {'Content-Type': 'text/plain; charset=utf-8'}
