# Код сервера
import socket  # Импорт
from something import get_ip
# from tkinter import *
import asyncio

get_ip()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', 5000))
server.listen(1)
conn, addr = server.accept()
print(f'Connected: {addr}')
print('Server has started')
running = True

while running:
    # Блок принятия данных
    data = conn.recv(1024)
    if data.decode("utf-8") == 'stop' or not data:
        running = False
    print(f"Message from client {':'.join(map(str, addr))}: {data.decode('utf-8')}")

    # Блок отправки данных
    message = input("Message to client>>> ")
    if message == 'stop' or not message:
        conn.send('stop'.encode('utf-8'))
        running = False
    conn.send(f'{message}'.encode('utf-8'))

conn.close()
server.close()
print('Server has finished')
