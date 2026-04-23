"""
Сервер по приёму метрик.

...
"""
storage = {}

def process_request(request, storage):
    """
    request: строка типа "put key 10.0 123\n" или "get key\n"
    storage: словарь с метриками, который мы будем обновлять/читать
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
            # values — это список [(timestamp, value), ...]
            # пока без сортировки
            for timestamp, value in values:
                lines.append(f"{metric} {value} {timestamp}")

        # собираем ответ
        return "\n".join(lines) + "\n\n"
    else:
        # неизвестная команда
        return "error\nwrong command\n\n"

if __name__ == '__main__':
    # print(process_request("put test_key 10.0 1503319740\n", storage))
    # print(storage)
    print(process_request("put k1 10.0 1\n", storage))
    print(process_request("put k1 20.0 2\n", storage))
    print(process_request("get k1\n", storage))
    print(process_request("get *\n", storage))
    print(process_request("get k2\n", storage))