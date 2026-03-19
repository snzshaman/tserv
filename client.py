import time
from socket import create_connection


class Client:
    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout

    def put(self, metric, value, timestamp=None):
        if timestamp is None:
            timestamp = int(time.time())
        data = f"put {metric} {value} {timestamp}\n"

        with create_connection((self.host, self.port), self.timeout) as sock:
            sock.sendall(data.encode("UTF-8"))

            response = self._recv_all(sock)
            lines = response.split("\n")
            if not lines or lines[0] != "ok":
                raise ClientError("Ошибка ответа сервера")


    def _recv_all(self, sock):
        data=""
        while "\n\n" not in data:
            line = sock.recv(1024)
            if not line:
                break
            data += line.decode("UTF-8")
        return data



    def get(self, key):
        ...

class ClientError(Exception):
    pass