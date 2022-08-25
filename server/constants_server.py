server_ip = 'localhost'  # Тут IP хоста
server_port = 9091  # Тут порт хоста
message_size = 4096

message_pattern = {
    'command': '',
    'msg': '',
    'sender': ('ip', 'port'),
    'receiver': ('ip', 'port')
}

# Описания паттерна сообщения:
# 'command' - это команда, которая подсказывает, что нужно делать.
# 'msg' - это либо аргумент команды, либо само сообщение, которое передаётся.
# 'from' - это кортеж из IP и порта отправителя (нужно для передачи самих сообщений между клиентами через сервер).
# 'to' - это кортеж из IP и порта, но уже того, кому отправляется. Нужно для обмена сообщениями (как 'from')
#
# Команды:
# 'alert' - команда от сервера, уведомляющая о чём-либо
# 'get_address' - команда от сервера, которая отправляет адрес
# 'set_mode' - установка режима. Аргументы (то, что пишется в 'msg') - 'online'/'offline'
# 'connect_to' - запрос на подключение к кому-либо. В 'from' адрес отправителя, в 'to' адрес получателя
# 'connecting' - уведомление о подключении одного клиента к другому
# 'msg_to' - сообщение кому-либо. В 'from' адрес отправителя, в 'to' адрес получателя
# Пока всё
