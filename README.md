# ods (Oystr - Discovery Service)

[![badge](https://img.shields.io/badge/license-MIT-blue)](https://github.com/oystr-foss/discovery-service/blob/main/LICENSE)

Ods is a discovery/registry service that allows us to keep track of dynamic services added to our infrastructure and their status through regular health checks. e.g.: dynamic proxy servers.

### Requirements

* Python3.7+
* PIP3

### Installation

To install, we basically run pip along with requirements.txt:

```bash
$ pip install -r requirements.txt
```

### Running

In order to run the service, just type:

```bash
$ python3 main.py
```

### Default behaviour/configuration

By default, we run a health check task every 30 seconds and update the service status accordingly.

A newly registered service starts as `unknown`. After the first successful health check, it's then updated to `running`, otherwise it's updated to `pending`. After 2 failures, the status is updated to `failing` and after the third failure, the status is updated to `disabled`.

Every 15 minutes we run a cleanup tasks that removes all services marked as disabled.

### Routes

```bash
GET    /services                             Get a list of all services with meta information (last_health_check, status, registered_at...).
POST   /services                             Add a new service. e.g.: {"service_id": "<ID>", "host": "<IP_ADDRESS>", "port": 8888}
DELETE /services/<service_id>/<host>/<port>  Delete a service.
```

### TODO

* Document routes;
* Avoid duplicated services + hosts + ports;
* Dockerize;
* Use GUnicorn;
* Create a discovery.conf file;
* Log to /var/log/ods.log.
