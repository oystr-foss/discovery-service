import json
from typing import Optional
from datetime import datetime


class Status(object):
    STATES = [
        "running",
        "stopped",
        "unknown",
        "pending",
        "disabled",
        "failing"
    ]

    def __init__(self, status):
        self.status = self.__to_status(status)

    def __to_status(self, status):
        return status if str(status).lower() in self.STATES else 'unknown'

    def __str__(self):
        return self.status


class Service(object):
    def __init__(self, service_id: str, name: Optional[str], host: str, port: int, status: Status,
                 registered_at: datetime, last_health_check: Optional[datetime] = None):
        self.service_id = service_id
        self.name = name
        self.host = host
        self.port = port
        self.status = status
        self.registered_at = registered_at
        self.last_health_check = last_health_check

    def __str__(self):
        return self.__dict__

    def json(self):
        return json.dumps(self.__str__(), default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o))
