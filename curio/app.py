#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Taken from curio: https://github.com/dabeaz/curio
# A simple echo server

from curio import run, tcp_server
from socket import *


async def echo_handler(client, addr):
    print('Connection from', addr)
    try:
        client.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
    except (OSError, NameError):
        pass

    while True:
        data = await client.recv(102400)
        if not data:
            break
        await client.sendall(data)
    print('Connection closed')

if __name__ == '__main__':
    run(tcp_server('', 3000, echo_handler))
