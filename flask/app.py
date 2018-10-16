# -*- coding: utf-8 -*-

from gevent import monkey;monkey.patch_all()

from flask import Flask
application = Flask(__name__)

@application.route("/<int:msize>")
def hello(msize):
    return "X" * msize
