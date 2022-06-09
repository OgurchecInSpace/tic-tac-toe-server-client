# Код сервера
import socket  # Импорт
# from tkinter import *
import asyncio
from something import get_ip

print(get_ip())
print(socket.gethostbyname_ex(socket.gethostname()))
ip = socket.gethostbyname_ex(socket.gethostname())[-1][-1]
port = 9091

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((ip, 9091))
server.listen(1)
conn, addr = server.accept()
print(f'Connected: {addr}')
print(f'Server has started on {ip}:{port}')
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
