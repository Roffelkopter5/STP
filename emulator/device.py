from __future__ import annotations
from queue import Queue, Empty
import time
from typing import NamedTuple
from enum import Enum, auto


class RequestMethod(Enum):
    WRITE = auto()
    READ = auto()


class Request(NamedTuple):
    method: RequestMethod
    port: int
    data: int

    @classmethod
    def read(cls, port: int, data: int = 0):
        return cls(RequestMethod.READ, port, data)

    @classmethod
    def write(cls, port: int, data: int = 0):
        return cls(RequestMethod.WRITE, port, data)


class ResponseCode(Enum):
    FAIL = auto()
    SUCCESS = auto()


class Response(NamedTuple):
    code: ResponseCode
    data: int

    @classmethod
    def fail(cls, data: int = 0):
        return cls(ResponseCode.FAIL, data)

    @classmethod
    def success(cls, data: int = 0):
        return cls(ResponseCode.SUCCESS, data)


class Device:
    def startup(self, port: int):
        self._port = port
    
    def shutdown(self):
        self._port = -1

    def send(self, data: int):
        self._controller.interrupt(Request.write(self._port, data))

    def receive(self):
        self._controller.interrupt(Request.read(self._port))

    def on_write(self, data: int):
        pass

    def on_read(self):
        return 0

    def update(self, dt: float):
        pass


class DeviceController:
    def __init__(self, max_ports: int, in_queue: Queue = None, out_queue: Queue = None):
        self.status_reg = 0
        self.max_devices = max_ports
        self.devices: list[Device] = [None for _ in range(max_ports)]
        self.in_queue = in_queue
        self.out_queue = out_queue

    def allow_int(self, port: int):
        return bool(2**port & self.status_reg)

    def interrupt(self, req: Request):
        if self.allow_int(req.port):
            # TODO send interrupt to cpu
            return Response.success()
        else:
            if self.allow_int(0):
                # TODO send missed interrupt to cpu
                pass
            return Response.fail()

    def register_device(self, device: Device, port: int) -> bool:
        if self.devices[port]:
            return False
        self.devices[port] = device
        return True

    def remove_device(self, device_or_port: Device | int) -> bool:
        if isinstance(device_or_port, Device):
            try:
                port = self.devices.index(device_or_port)
            except ValueError:
                return False
        else:
            port = device_or_port
        self.devices.pop(port).shutdown()
        return True

    def get_delta(self, last):
        current = time.monotonic()
        delta = current - last
        return delta, current

    def internal_request(self, req: Request):
        if req.method == RequestMethod.READ:
            return Response.success(self.status_reg)
        elif req.method == RequestMethod.WRITE:
            self.status_reg = req.data
            return Response.success()

    def handle_request(self, req: Request):
        if req.port == 0:
            return self.internal_request(req)
        if dev := self.devices[req.port]:
            if req.method == RequestMethod.READ:
                return dev.on_read()
            elif req.method == RequestMethod.WRITE:
                return dev.on_write(req.data)
        else:
            return Response(ResponseCode.FAIL, 0)

    def run(self):
        last_time = time.monotonic()
        for port, dev in enumerate(self.devices):
            if dev:
                dev.startup(port)
        while True:
            try:
                request = self.in_queue.get_nowait()
                response = self.handle_request(request)
                self.out_queue.put(response)
            except Empty:
                pass
            delta, last_time = self.get_delta(last_time)
            for dev in self.devices:
                if dev:
                    dev.update(delta)
        for port, dev in enumerate(self.devices):
            if dev:
                dev.shutdown()