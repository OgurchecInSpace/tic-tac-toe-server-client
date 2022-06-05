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
    conn.send(data.decode("utf-8").upper().encode("utf-8"))

conn.close()
server.close()
print('Server has finished')
