import json
import socket
import sys
import threading
import time


clients = []


def send_message_to_all_clients(message: bytes, client_socket):
    """Отправить сообщения всем клиентам"""
    for client in clients:
        if client == client_socket:
            continue
        client.send(message)


def read_request(request: bytes):
    """Декодировать и загрузить данные запроса из json"""
    return json.loads(request.decode())


def delete_connect(client_socket):
    """Удалить и закрыть клиента"""
    clients.remove(client_socket)
    client_socket.close()


def prepare_message_for_sending(name, message):
    """Подготовить сообщение к отправке"""
    return json.dumps({"name": name, "message": message}).encode()


def accepting_request_from_client(client_socket, ip, port):
    """Работа с запросами клиента"""
    while True:
        request = client_socket.recv(1024)
        data = read_request(request)

        if data['remove_connect']:
            response = prepare_message_for_sending(name='system', message=f'[client exit {data["name"]}]')
            delete_connect(client_socket)
            print(display_remove_connect(ip, port))
        else:
            response = prepare_message_for_sending(name=data['name'], message=data['message'])

        send_message_to_all_clients(response, client_socket)

        if data['remove_connect']:
            sys.exit()


def run_server(server_socket):
    """Запустить сервер"""
    count_connection = 1
    while True:
        client_socket, (ip, port) = server_socket.accept()
        clients.append(client_socket)
        print(display_new_connect(ip, port))
        thread = threading.Thread(target=accepting_request_from_client,
                                  name=f'THREAD №{count_connection} [{ip}:{port}]',
                                  args=(client_socket, ip, port),
                                  daemon=True)
        thread.start()
        count_connection += 1


def display_new_connect(ip, port):
    """Отобразить новое подключение"""
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return f'[+] NEW CONNECT [{ip}:{port}]-[{current_time}]'


def display_remove_connect(ip, port):
    """Отобразить удаление подключения"""
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return f'[-] REMOVE CONNECT [{ip}:{port}]-[{current_time}]'


def green_text(item):
    return f'\033[32m{str(item)}\033[0m'


def red_text(item):
    return f'\033[31m{str(item)}\033[0m'


def main():
    host = 'localhost'
    port = 5050

    # print('Установка протоколов: ', end='')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # print('✔')

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # print('Свьязывание сокета с локальным адресом протокола:', end='')
    server_socket.bind((host, port))
    # print('✔')

    server_socket.listen()
    # print('Прослушивание: ')

    try:
        print(green_text(f'[SERVER-IS-RUNNING] [{host}:{port}]'))
        run_server(server_socket)
    except (KeyboardInterrupt, SystemExit):
        server_socket.close()
        print(red_text(f'[SERVER-IS-DOWN] [{host}:{port}]'))


if __name__ == '__main__':
    main()
