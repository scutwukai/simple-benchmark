#!/usr/bin/env python3


import argparse
import json
import os
import subprocess
import sys
import tempfile


def abort(msg):
    print(msg, file=sys.stdout)
    sys.exit(1)


luascript = '''
function done(summary, latency, requests)
    tpl = [[
{
    "messages": %d,
    "transfer": %.2f,
    "rps": %.2f,
    "latency_min": %.3f,
    "latency_mean": %.3f,
    "latency_max": %.3f,
    "latency_std": %.3f,
    "latency_cv": %.2f,
    "latency_percentiles": [%s]
}]]

    transfer = (summary.bytes / (1024 * 1024)) / (summary.duration / 1000000)
    rps = summary.requests / (summary.duration / 1000000)
    latency_percentiles = {}
    percentiles = {25, 50, 75, 90, 99, 99.99}

    for i, percentile in ipairs(percentiles) do
        table.insert(
            latency_percentiles,
            string.format("[%.2f, %.3f]", percentile,
                          latency:percentile(percentile) / 1000)
        )
    end

    out = string.format(tpl, summary.requests,  transfer, rps,
                        latency.min / 1000, latency.mean / 1000,
                        latency.max / 1000, latency.stdev / 1000,
                        (latency.stdev / latency.mean) * 100,
                        table.concat(latency_percentiles, ','))

    io.stderr:write(out)
end
'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--wrk', default='wrk', type=str,
                        help='wrk location')
    parser.add_argument('--msize', default=1000, type=int,
                        help='message size in bytes')
    parser.add_argument('--duration', '-T', default=30, type=int,
                        help='duration of test in seconds')
    parser.add_argument('--concurrency', default=100, type=int,
                        help='request concurrency')
    parser.add_argument('--addr', default='127.0.0.1:3000', type=str,
                        help='server address')
    parser.add_argument('--output-format', default='text', type=str,
                        help='output format', choices=['text', 'json'])
    args = parser.parse_args()

    unix = False
    if args.addr.startswith('file:'):
        abort('Unix sockets are not supported')

    with tempfile.NamedTemporaryFile(mode='w+t', delete=False) as luaf:
        luaf.write(luascript)
        lua_script_path = luaf.name

    wrk = [args.wrk, '-t4', '--latency',# '--header=Connection: close',
           '--duration={}s'.format(args.duration),
           '--connections={}'.format(args.concurrency),
           '--script={}'.format(lua_script_path),
           'http://{}/{}'.format(args.addr, args.msize)]

    try:
        wrk_run = subprocess.Popen(wrk, universal_newlines=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        out, data_json = wrk_run.communicate()
    finally:
        #print(out)
        os.unlink(lua_script_path)

    if args.output_format == 'json':
        print(data_json)
    else:
        data = json.loads(data_json)

        data['latency_percentiles'] = '\n  '.join(
            '{}%   {}ms'.format(*v) for v in data['latency_percentiles'])

        output = '''\
{messages} {size}KiB messages in {duration} seconds
Latency: min {latency_min}ms; max {latency_max}ms; mean {latency_mean}ms; \
std: {latency_std}ms ({latency_cv}%)
Latency distribution: \n  {latency_percentiles}
Requests/sec: {rps}
Transfer/sec: {transfer}MiB
'''.format(duration=args.duration, size=round(args.msize / 1024, 2), **data)

        print(output)
