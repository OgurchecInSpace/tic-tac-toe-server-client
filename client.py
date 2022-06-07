# Код клиента
import socket  # Импорт
import asyncio

server_ip = '192.168.0.28'

print('Client has started')
client = socket.socket()
client.connect((server_ip, 9091))
client.send('Connection!'.encode('utf-8'))
running = True


while running:
    # Блок принятия данных
    data = client.recv(1024)
    if data == 'stop':
        running = False
    print(f'Message from server>>> {data.decode("utf-8")}')

    # Блок отправки данных
    message = input('Message to server>>> ')
    if message == 'stop' or not message:
        client.send('stop'.encode('utf-8'))
        running = False
    client.send(message.encode('utf-8'))

client.close()
print('Client has finished')
