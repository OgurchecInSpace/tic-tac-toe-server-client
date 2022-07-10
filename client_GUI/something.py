# Файл с вспомогательными функциями
from constants_client import *


def get_ip():  # Получение своего внешнего IP адреса
    import http.client
    conn = http.client.HTTPConnection("ifconfig.me")
    conn.request("GET", "/ip")
    return conn.getresponse().read().decode()


def is_valid_address(address):  # Функция проверки, что IP адекватный
    try:
        ip = address.split(':')[0]
        port = address.split(':')[1]
        valid_ip = False
        ip = ip.split('.')
        for value in ip:
            if 0 <= int(value) < 256:
                valid_ip = True
            else:
                valid_ip = False
                break
        return valid_ip and len(ip) == 4 and port.isdigit() and 0 < int(port) < 65536
    except:
        return False


# Функция, собирающая сообщение (укорачивает процесс)
def create_message(command, msg, sender, receiver):
    message = message_pattern.copy()
    message['command'] = command
    message['msg'] = msg
    message['sender'] = sender
    message['receiver'] = receiver

    return message
