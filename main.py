import itertools
import json
import random
import socket
import time
from datetime import datetime
from threading import Thread
from typing import Dict, List

import pytz
import schedule
from quart import Quart, request, make_response

from service import Service, Status
from timer import Timer


app = Quart(__name__)
tz = pytz.timezone('America/Sao_Paulo')
timer = Timer()
services: Dict[str, List[Service]] = {}


@app.before_request
async def before_request():
    timer.start = datetime.now(tz=tz)
    return


@app.after_request
async def after_request(response):
    timer.end = datetime.now(tz=tz)
    total = f'{timer.diff()}s'

    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Request-Duration'] = total
    return response


@app.route('/services', methods=["GET"])
async def find_all():
    items = services.values()
    data = [i for i in list(itertools.chain.from_iterable(items))]
    as_dict = [d.__dict__ for d in data]

    return \
        await make_response(json.dumps(as_dict, default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o))),\
        200


@app.route('/services/<service>/random', methods=["GET"])
async def find_one(service):
    if not service or len(service) == 0:
        return await make_response('service_id must be provided'), 400
    elif service not in services.keys():
        return await make_response(''), 404

    data = list(filter(lambda i: i.status.status == 'running', services[service]))

    size = len(data)
    if size == 0:
        return await make_response(''), 503

    idx = random.randint(0, size - 1)
    return await make_response(data[idx].json()), 200


@app.route('/services', methods=["POST"])
async def register():
    req = await request.json

    name = req.get('name', None)
    service_id = req.get('service_id')
    raw_port = req.get('port')
    host = req.get('host')

    res, code = await validate(service_id, host, raw_port, check_duplicate=False)
    if res:
        return res, code

    port = int(raw_port)
    service = Service(service_id=service_id, name=name, host=host, port=port, status=Status(None),
                      registered_at=datetime.now(tz=tz), last_health_check=None)

    if service_id not in services:
        services[service_id] = list()
    services[service_id].append(service)

    return await make_response(service.json()), 200


async def validate(service, host, port, check_duplicate=True):
    if not str(port).isnumeric():
        return await make_response(f'port must be a number'), 400
    elif not host or len(host) == 0:
        return await make_response('host must be provided'), 400
    elif not service or len(service) == 0:
        return await make_response('service_id must be provided'), 400
    elif check_duplicate and (service not in services.keys()):
        return await make_response(''), 404

    return None, -1


@app.route('/services/<service>/<host>/<port>', methods=["DELETE"])
async def deregister(service, host, port):
    res, code = await validate(service, host, port)
    if res:
        return res, code

    empty_res = await make_response('')
    to_remove = [idx for idx in range(len(services[service])) if services[service][idx].host == host and
                 services[service][idx].port == port]

    if to_remove == 0:
        return empty_res, 404
    elif to_remove != 1:
        print(services)
        print(to_remove)
        return await make_response('more than one peer registered with the same service, host and port'), 409

    idx = to_remove[0]
    del services[service][idx]
    return empty_res, 204


@app.route('/services/flush', methods=["DELETE"])
async def flush():
    services.clear()
    return 204, await make_response('')


def health_check():
    ids = services.values()
    for items in ids:
        for service in items:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)

            if service.status.status == 'disabled':
                continue

            # noinspection PyBroadException
            try:
                s.connect((service.host, service.port))
                service.status = Status('running')
            except Exception as _:
                if service.last_health_check and service.status.status == 'pending':
                    service.status = Status('failing')
                    continue
                elif service.last_health_check and service.status.status == 'failing':
                    service.status = Status('disabled')
                    continue

                service.status = Status('pending')
                print(f'{service.service_id} {service.status.status} health checked')
            finally:
                service.last_health_check = datetime.now(tz=tz)


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


def remove_disabled():
    services2 = services
    for k, v in services2.items():
        for idx, service in enumerate(v):
            if service.status.status == 'disabled':
                del services[k][idx]


schedule.every(30).seconds.do(health_check)
schedule.every(15).minutes.do(remove_disabled)

thread = Thread(target=run_scheduler, args=(), daemon=True)
thread.start()

app.run(host='0.0.0.0', port=10000)
