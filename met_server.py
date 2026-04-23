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
        # тут будет get
        ...
    else:
        # неизвестная команда
        return "error\nwrong command\n\n"

if __name__ == '__main__':
    print(process_request("put test_key 10.0 1503319740\n", storage))
    print(storage)