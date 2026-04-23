import socket

def send_cmd(cmd: str) -> str:
    # подключаемся к серверу
    with socket.create_connection(("127.0.0.1", 8888), timeout=5) as sock:
        # отправляем команду как байты
        sock.sendall(cmd.encode("utf-8"))
        # читаем ответ (до 4 КБ для простоты)
        data = sock.recv(4096)
    return data.decode("utf-8")

if __name__ == "__main__":
    # несколько пробных запросов
    print("PUT 1:")
    print(repr(send_cmd("put k1 10.0 1\n")))

    print("PUT 2:")
    print(repr(send_cmd("put k1 20.0 2\n")))

    print("GET k1:")
    print(repr(send_cmd("get k1\n")))

    print("GET *:")
    print(repr(send_cmd("get *\n")))

    print("GET k2 (нет такой):")
    print(repr(send_cmd("get k2\n")))