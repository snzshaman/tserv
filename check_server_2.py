"""
Вспомогательный скрипт для тестирования сервера из задания 6 блока.

Для запуска:
1. Рядом должен лежать файл client.py с реализацией клиента из 5 блока.
2. Сначала запустите ваш сервер на 127.0.0.1:8888.
3. Затем запустите этот скрипт.
"""

import sys
from client import Client, ClientError  # под твой код


def run(host, port):
    client1 = Client(host, port, timeout=5)
    client2 = Client(host, port, timeout=5)

    # 1. Проверяем реакцию сервера на некорректную команду
    try:
        client1.put("malformed command test", 0)  # у тебя, возможно, нет метода send
        client2.put("malformed command test", 0)
    except ClientError:
        # ожидаем, что клиент увидит ошибку протокола от сервера
        pass
    except Exception as err:
        print(f"Ошибка общения с сервером: {err.__class__}: {err}")
        sys.exit(1)
    else:
        print(
            "Неверная команда, отправленная серверу, должна возвращать ошибку протокола"
        )
        sys.exit(1)

    # 2. Отправляем серию put
    try:
        client1.put("k1", 0.25, timestamp=1)
        client2.put("k1", 2.156, timestamp=2)
        client1.put("k1", 0.35, timestamp=3)
        client2.put("k2", 30, timestamp=4)
        client1.put("k2", 40, timestamp=5)
        client1.put("k2", 40, timestamp=5)
    except Exception as err:
        print(f"Ошибка вызова client.put(...): {err.__class__}: {err}")
        sys.exit(1)

    expected_metrics = {
        "k1": [(1, 0.25), (2, 2.156), (3, 0.35)],
        "k2": [(4, 30.0), (5, 40.0)],
    }

    # 3. Проверяем get("*")
    try:
        metrics = client1.get("*")
        if metrics != expected_metrics:
            print(
                f"client.get('*') вернул неверный результат. "
                f"Ожидается: {expected_metrics}. Получено: {metrics}"
            )
            sys.exit(1)
    except Exception as err:
        print(f"Ошибка вызова client.get('*'): {err.__class__}: {err}")
        sys.exit(1)

    # 4. Проверяем get('k2')
    expected_metrics = {"k2": [(4, 30.0), (5, 40.0)]}
    try:
        metrics = client2.get("k2")
        if metrics != expected_metrics:
            print(
                f"client.get('k2') вернул неверный результат. "
                f"Ожидается: {expected_metrics}. Получено: {metrics}"
            )
            sys.exit(1)
    except Exception as err:
        print(f"Ошибка вызова client.get('k2'): {err.__class__}: {err}")
        sys.exit(1)

    # 5. Проверяем get('k3') для ещё не существующего ключа
    try:
        result = client1.get("k3")
        if result != {}:
            print(
                "Ошибка вызова метода get с ключом, который еще не был добавлен. "
                f"Ожидается: пустой словарь. Получено: {result}"
            )
            sys.exit(1)
    except Exception as err:
        print(
            "Ошибка вызова метода get с ключом, который еще не был добавлен: "
            f"{err.__class__} {err}"
        )
        sys.exit(1)

    print("Похоже, что все верно!")


if __name__ == "__main__":
    run("127.0.0.1", 8888)