# Сервер
# Импорт
import socket
import datetime
import pickle
from constants_server import *
from something import *


def get_now_time():  # Получение времени на данный момент в читаемом формате
    now = datetime.datetime.now()
    return f'[{now.date()} {now.hour}:{now.minute}:{now.second}]'


def main():  # Главная функция
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((socket.gethostbyname_ex(socket.gethostname())[-1][-1], server_port))
    print((socket.gethostbyname_ex(socket.gethostname()), server_port))
    print('====check server IP and server port on host site====')

    members = dict()  # Список всех участников

    while True:
        msg, addr = server.recvfrom(message_size)  # Получение сообщения от отправителя и его адрес
        msg = pickle.loads(msg)
        print(f'{msg} from {addr}')

        if msg['command'] == 'set_mode':
            if msg['msg'] == 'online':
                msg_to_user = message_pattern.copy()
                msg_to_user['command'] = 'get_address'
                msg_to_user['msg'] = addr
                server.sendto(pickle.dumps(msg_to_user), addr)
            members[addr] = msg['msg']
        elif msg['command'] == 'msg_to':         # Если команда - сообщение к кому-либо, то
            if members[msg['to']] == 'online':   # Отправляем, если собеседник онлайн
                server.sendto(pickle.dumps(msg), msg['to'])
            else:                                # Если же нет, уведомляем об этом изначальный компьютер
                msg = message_pattern.copy()
                msg['command'] = 'alert'
                msg['msg'] = 'Sorry, your companion is offline'
                msg = pickle.dumps(msg)
                server.sendto(msg, addr)
        elif msg['command'] == 'connect_to':    # Если команда - подключение к кому-либо, то
            if members[msg['to']] == 'online':  # Подключаем, если собеседник онлайн
                server.sendto(pickle.dumps(msg), msg['to'])
            else:                               # Если же нет, уведомляем об этом изначальный компьютер
                msg = message_pattern.copy()
                msg['command'] = 'alert'
                msg['msg'] = 'Sorry, your companion is offline'
                msg = pickle.dumps(msg)
                server.sendto(msg, addr)
        else:                                   # Если команда не найдена, уведомляем об этом изначальный компьютер
            msg = message_pattern.copy()
            msg['command'] = 'alert'
            msg['msg'] = 'Not found command'
            msg = pickle.dumps(msg)
            server.sendto(msg, addr)


if __name__ == '__main__':
    main()
