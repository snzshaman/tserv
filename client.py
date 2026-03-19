"""
Клиент для отправки и получения метрик по простому текстовому протоколу.

Класс Client инкапсулирует TCP‑соединение с сервером метрик и реализует команды
`put` и `get` для записи и чтения данных.
"""
import time
import socket


class Client:
    """
    Клиент для взаимодействия с сервером метрик по TCP.

    Клиент отправляет команды `put` и `get` в текстовом формате
    и обрабатывает ответы сервера.
    """

    def __init__(self, host, port, timeout=None):
        """
        Инициализирует клиент с заданым удресом сервера.

        :param host: адрес сервера метрик (IP или имя хоста)
        :type host: str
        :param port: порт сервера метрик
        :type port: int
        :param timeout: таймаут сокета в секундах, None по умолчанию
        :type timeout: int | None
        """
        self.host = host
        self.port = port
        self.timeout = timeout

    def put(self, metric, value, timestamp=None):
        """
        Отправляет значение метрики на сервер.

        Формирует команду 'put <metric> <value> <timestamp>\\n'
        Если timestamp не передан, использует текущее время в секундах.

        :param metric: имя метрики
        :type metric: str
        :param value: числовое значение метрики
        :type value: int | float
        :param timestamp: текущее время
        :type timestamp: int | None
        :return: ничего не возвращает при успешной отправке
        :rtype: None
        :raises ClientError: Ошибка ответа сервера
        """
        if timestamp is None:
            timestamp = int(time.time())
        data = f"put {metric} {value} {timestamp}\n"

        with socket.create_connection((self.host, self.port), self.timeout) as sock:
            sock.sendall(data.encode("UTF-8"))

            self._read_and_check(sock)


    def _recv_all(self, sock):
        """
        Цикл чтения ответа сервера

        :param sock: открытое TCP-соединение
        :type sock: socket.socket
        :return: полный ответ сервера
        :rtype: str
        """
        data=""
        while "\n\n" not in data:
            line = sock.recv(1024)
            if not line:
                break
            data += line.decode("UTF-8")
        return data

    def _read_and_check(self, sock):
        """
        Читает полный ответ от сервера и проверяет, что первая строка 'ok'
        :param sock: открытое TCP-соединение
        :type sock: socket.socket
        :return: полный ответ сервера
        :rtype: str
        :raises ClientError: Если первая строка != "ok"
        """
        response = self._recv_all(sock)
        lines = response.split("\n")
        if not lines or lines[0] != "ok":
            raise ClientError("Сервер вернул ошибку")
        return response

    def get(self, key):
        ...

class ClientError(Exception):
    pass

