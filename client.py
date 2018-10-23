#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
from concurrent import futures
import json
import math
import socket
import time

import numpy as np


def weighted_quantile(values, quantiles, weights):
    """ Very close to np.percentile, but supports weights.

    :param values: np.array with data
    :param quantiles: array-like with many quantiles needed,
           quantiles should be in [0, 1]!
    :param weights: array-like of the same length as `array`
    :return: np.array with computed quantiles.
    """
    values = np.array(values)
    quantiles = np.array(quantiles)
    weights = np.array(weights)
    assert np.all(quantiles >= 0) and np.all(quantiles <= 1), \
                 'quantiles should be in [0, 1]'

    weighted_quantiles = np.cumsum(weights) - 0.5 * weights
    weighted_quantiles -= weighted_quantiles[0]
    weighted_quantiles /= weighted_quantiles[-1]

    return np.interp(quantiles, weighted_quantiles, values)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--msize', default=1000, type=int,
                        help='message size in bytes')
    parser.add_argument('--mpr', default=1, type=int,
                        help='messages per request')
    parser.add_argument('--duration', '-T', default=30, type=int,
                        help='duration of test in seconds')
    parser.add_argument('--concurrency', default=4, type=int,
                        help='request concurrency')
    parser.add_argument('--timeout', default=2, type=int,
                        help='socket timeout in seconds')
    parser.add_argument('--addr', default='127.0.0.1:3000', type=str,
                        help='server address')
    parser.add_argument('--output-format', default='text', type=str,
                        help='output format', choices=['text', 'json'])
    args = parser.parse_args()

    unix = False
    if args.addr.startswith('file:'):
        unix = True
        addr = args.addr[5:]
    else:
        addr = args.addr.split(':')
        addr[1] = int(addr[1])
        addr = tuple(addr)

    MSGSIZE = args.msize
    msg = (b'x' * (MSGSIZE - 1) + b'\n') * args.mpr

    REQSIZE = MSGSIZE * args.mpr

    timeout = args.timeout * 1000

    def run_test(start, duration):
        if unix:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.settimeout(timeout / 1000)
        sock.connect(addr)

        n = 0
        latency_stats = np.zeros((timeout * 100,))
        min_latency = float('inf')
        max_latency = 0.0

        while time.monotonic() - start < duration:
            req_start = time.monotonic()
            sock.sendall(msg)
            nrecv = 0
            while nrecv < REQSIZE:
                resp = sock.recv(REQSIZE)
                if not resp:
                    raise SystemExit()
                nrecv += len(resp)
            req_time = round((time.monotonic() - req_start) * 100000)
            if req_time > max_latency:
                max_latency = req_time
            if req_time < min_latency:
                min_latency = req_time
            latency_stats[req_time] += 1
            n += 1

        try:
            sock.close()
        except OSError:
            pass

        return n, latency_stats, min_latency, max_latency

    N = args.concurrency
    DURATION = args.duration

    min_latency = float('inf')
    max_latency = 0.0
    messages = 0
    latency_stats = None
    start = time.monotonic()

    with futures.ProcessPoolExecutor(max_workers=N) as e:
        fs = []
        for _ in range(N):
            fs.append(e.submit(run_test, start, DURATION))

        res = futures.wait(fs)
        for fut in res.done:
            t_messages, t_latency_stats, t_min_latency, t_max_latency = \
                fut.result()
            messages += t_messages
            if latency_stats is None:
                latency_stats = t_latency_stats
            else:
                latency_stats = np.add(latency_stats, t_latency_stats)
            if t_max_latency > max_latency:
                max_latency = t_max_latency
            if t_min_latency < min_latency:
                min_latency = t_min_latency

    end = time.monotonic()

    arange = np.arange(len(latency_stats))

    stddev = np.std(arange)

    weighted_latency = np.multiply(latency_stats, arange)

    mean_latency = np.average(arange, weights=latency_stats)
    variance = np.average((arange - mean_latency) ** 2, weights=latency_stats)
    latency_std = math.sqrt(variance)
    latency_cv = latency_std / mean_latency

    percentiles = [25, 50, 75, 90, 99, 99.99]
    percentile_data = []

    quantiles = weighted_quantile(arange, [p / 100 for p in percentiles],
                                  weights=latency_stats)

    for i, percentile in enumerate(percentiles):
        percentile_data.append((percentile, round(quantiles[i] / 100, 3)))

    data = dict(
        messages=messages,
        transfer=round((messages * MSGSIZE / (1024 * 1024)) / DURATION, 2),
        rps=round(messages / DURATION, 2),
        latency_min=round(min_latency / 100, 3),
        latency_mean=round(mean_latency / 100, 3),
        latency_max=round(max_latency / 100, 3),
        latency_std=round(latency_std / 100, 3),
        latency_cv=round(latency_cv * 100, 2),
        latency_percentiles=percentile_data
    )

    if args.output_format == 'json':
        data['latency_percentiles'] = json.dumps(percentile_data)

        output = '''\
{{
    "messages": {messages},
    "transfer": {transfer},
    "rps": {rps},
    "latency_min": {latency_min},
    "latency_mean": {latency_mean},
    "latency_max": {latency_max},
    "latency_std": {latency_std},
    "latency_cv": {latency_cv},
    "latency_percentiles": {latency_percentiles}
}}'''.format(**data)
    else:
        data['latency_percentiles'] = '; '.join(
            '{}% under {}ms'.format(*v) for v in percentile_data)

        output = '''\
{messages} {size}KiB messages in {duration} seconds
Latency: min {latency_min}ms; max {latency_max}ms; mean {latency_mean}ms; \
std: {latency_std}ms ({latency_cv}%)
Latency distribution: {latency_percentiles}
Requests/sec: {rps}
Transfer/sec: {transfer}MiB
'''.format(duration=DURATION, size=round(MSGSIZE / 1024, 2), **data)

    print(output)
