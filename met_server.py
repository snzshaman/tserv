"""
Сервер по приёму метрик.

Модуль реализует:
- функцию :func:`process_request`, которая обрабатывает команды ``put`` и ``get`` над
  внутренним хранилищем метрик;
- класс :class:`ClientServerProtocol` на базе :mod:`asyncio`, который принимает
  запросы от клиентов по TCP и передаёт их в :func:`process_request`;
- функцию :func:`run_server`, запускающую асинхронный TCP‑сервер на указанном
  хосте и порту.
"""
import asyncio
storage = {}

def process_request(request, storage):
    """
    Обрабатывает одну текстовую команду протокола метрик.

    Поддерживаются команды::

        put <key> <value> <timestamp>\\n
        get <key>\\n

    В случае команды ``put`` значение метрики добавляется во внутреннее
    хранилище. В случае ``get`` формируется текстовый ответ со всеми
    подходящими метриками или пустой ответ, если данных нет.

    :param request: строка запроса, например ``"put test 10.0 1\\n"`` или ``"get *\\n"``
    :type request: str
    :param storage: словарь с метриками, изменяемое хранилище вида
                    ``{metric_name: [(timestamp, value), ...], ...}``
    :type storage: dict[str, list[tuple[int, float]]]
    :return: строка ответа сервера в формате протокола
    :rtype: str
    """

    # убираем лишние пробелы и \n
    request = request.strip()

    # разбиваем по пробелам
    parts = request.split()

    if not parts:
        # пустая строка — ошибка протокола
        return "error\nwrong command\n\n"

    command = parts[0]

    if command == "put":
        if len(parts) != 4:
            return "error\nwrong command\n\n"

        _, key, value_str, ts_str = parts

        try:
            value = float(value_str)
            timestamp = int(ts_str)
        except ValueError:
            return "error\nwrong command\n\n"

        # добавляем в storage
        storage.setdefault(key, [])
        storage[key].append((timestamp, value))

        return "ok\n\n"
    elif command == "get":
        if len(parts) != 2:
            return "error\nwrong command\n\n"

        _, key = parts

        lines = ["ok"]

        # выбираем, какие ключи смотреть
        if key == "*":
            items = storage.items()
        else:
            # если ключа нет — просто ok\n\n
            if key not in storage:
                return "ok\n\n"
            items = [(key, storage[key])]

        # проходим по выбранным метрикам
        for metric, values in items:
            # гарантируем порядок по timestamp
            values_sorted = sorted(values, key=lambda item: item[0])
            for timestamp, value in values_sorted:
                lines.append(f"{metric} {value} {timestamp}")

        # собираем ответ
        return "\n".join(lines) + "\n\n"
    else:
        # неизвестная команда
        return "error\nwrong command\n\n"


class ClientServerProtocol(asyncio.Protocol):
    """
    Реализация протокола asyncio для сервера метрик.

    Экземпляр этого класса создаётся для каждого клиентского TCP‑соединения.
    Полученные от клиента данные передаются в :func:`process_request`, а
    сформированный ответ отправляется обратно по тому же соединению.
    """
    def connection_made(self, transport):
        """
        Вызывается при установлении нового соединения с клиентом.

        :param transport: транспорт asyncio для записи в TCP‑соединение
        :type transport: asyncio.transports.Transport
        """
        self.transport = transport

    def data_received(self, data):
        """
        Вызывается при получении данных от клиента.

        Декодирует байты в строку, передаёт запрос в :func:`process_request`,
        кодирует строку-ответ и отправляет её обратно клиенту.

        :param data: данные, полученные от клиента
        :type data: bytes
        """
        request = data.decode()
        response = process_request(request, storage)
        self.transport.write(response.encode())


async def _run_async_server(host, port):
    """
    Запускает асинхронный TCP‑сервер метрик.

    Создаёт сервер, который принимает входящие соединения и обрабатывает
    запросы с помощью :class:`ClientServerProtocol`.

    :param host: адрес, на котором нужно слушать соединения
    :type host: str
    :param port: номер порта сервера
    :type port: int
    """
    loop = asyncio.get_running_loop()
    server = await loop.create_server(ClientServerProtocol, host, port)

    try:
        await server.serve_forever()
    finally:
        server.close()
        await server.wait_closed()


def run_server(host, port):
    """
    Запускает сервер метрик в текущем процессе.

    Обёртка над :func:`_run_async_server`, которая создаёт и управляет
    циклом событий :mod:`asyncio` с помощью :func:`asyncio.run`.

    :param host: адрес, на котором нужно слушать соединения
    :type host: str
    :param port: номер порта сервера
    :type port: int
    """
    asyncio.run(_run_async_server(host, port))


if __name__ == "__main__":
    run_server("127.0.0.1", 8888)

# if __name__ == '__main__':
#     # print(process_request("put test_key 10.0 1503319740\n", storage))
#     # print(storage)
#     print(process_request("put k2 10.0 2\n", storage))
#     print(process_request("put k1 20.0 1\n", storage))
#     print(process_request("put k1 10.0 2\n", storage))
#     print(process_request("put k2 20.0 1\n", storage))
#     print(process_request("get k1\n", storage))
#     print(process_request("get *\n", storage))
#     print(process_request("get k2\n", storage))