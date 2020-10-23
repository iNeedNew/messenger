import json
import socket
import sys
import threading


name = input('Your name: ')


def prepare_message_for_sending(message, remove_connect=False):
    """Подготовить сообщение к отправке"""
    return json.dumps({"name": name, "message": message, "remove_connect": remove_connect}).encode('utf-8')


def message_validation(message):
    """Сделать валидным сообщение"""
    for symbol in ['\n', '\t', ' ']:
        message = message.strip(symbol)

    return message


def write_new_message_and_send(client_socket):
    """Написать новое сообщение сообщение и отправить"""
    while True:
        message = input()

        if message_validation(message):
            request = prepare_message_for_sending(message)
            client_socket.send(request)


def read_response(response: bytes):
    """Прочитать ответ. Декодировать и загрузить данные из json"""
    return json.loads(response.decode())


def show_message_that_came(response):
    """Показать пришедшее сообщение"""
    data = read_response(response)
    return f'[{data["name"]}]> {data["message"]}'


def run_client(client_socket):
    """Запустить клиент"""
    while True:
        response = client_socket.recv(1024)
        print(show_message_that_came(response))


def main():
    host = 'localhost'
    port = 5050

    client_socket = socket.create_connection((host, port))
    # Поток, для ввода сообщения
    thread = threading.Thread(target=write_new_message_and_send, daemon=True, args=(client_socket,))
    thread.start()
    try:
        run_client(client_socket)
    except (KeyboardInterrupt, SystemExit):
        client_socket.send(prepare_message_for_sending(message='', remove_connect=True))
        sys.exit()


if __name__ == '__main__':
    main()
