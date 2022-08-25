# Сервер
# Импорт
import socket
import datetime
import pickle
from constants_server import *
from server_something import *


def get_now_time():  # Получение времени на данный момент в читаемом формате
    now = datetime.datetime.now()
    return f'[{now.date()} {now.hour}:{now.minute}:{now.second}]'


def main():  # Главная функция
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((socket.gethostbyname_ex(socket.gethostname())[-1][0], server_port))
    print((socket.gethostbyname_ex(socket.gethostname()), server_port))

    members = dict()  # Словарь всех участников с их статусом
    requests = dict()  # Словарь запросов на подключение
    bunches = dict()  # Словарь всех подключений

    while True:
        msg, addr = server.recvfrom(message_size)  # Получение сообщения от отправителя и его адрес
        msg = pickle.loads(msg)
        print(f'{msg} from {addr}')

        if msg['command'] == 'set_mode':
            if msg['msg'] == 'online':
                server.sendto(pickle.dumps(create_message('get_address', addr,
                                                          ('Server IP', 'server port'), addr)), addr)
            elif msg['msg'] == 'offline' and addr in requests.keys():
                del requests[addr]

            members[addr] = msg['msg']

        elif msg['command'] == 'connect_to':
            if msg['msg'] in members.keys() and members[msg['msg']] == 'online':
                requests[addr] = msg['msg']
            else:
                server.sendto(
                    pickle.dumps(create_message('alert', 'Interlocutor is offline', (server_ip, server_port), addr)),
                    addr
                )

        # Если сообщение - сообщение о ходе, то просто переадресуем его тому, кто указан как получатель
        elif msg['command'] == 'msg_to':
            server.sendto(pickle.dumps(msg), msg['receiver'])

        # Проходимся по всем запросам
        for member in requests.keys():
            # Если запрашиваемый пользователь запрашивал кого-то
            # И если запрашиваемый запрашиваемым - изначально запросивший,
            # То соединяем их
            if requests[member] in requests.keys() and \
                    requests[requests[member]] == member:
                bunches[member] = requests[member]  # Связываем
                bunches[requests[member]] = member
                buffer_address = requests[member]
                del requests[member]  # Удаляем их из запросов
                del requests[buffer_address]

                # Уведомляем оба клиента о подключении
                server.sendto(pickle.dumps(
                    create_message('connecting', (buffer_address, 'crosses'), (server_ip, server_port), member)),
                    member
                )
                server.sendto(pickle.dumps(
                    create_message('connecting', (member, 'zeros'), (server_ip, server_port), buffer_address)),
                    buffer_address
                )

                break


if __name__ == '__main__':
    main()
