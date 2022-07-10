class Session:  # Сессия отправки и получения сообщений
    def __init__(self):
        self.connection = False  # Флажки подключения и одобрения запроса
        self.request_done = False

    # Метод получения сообщений, работающая в другом "потоке"
    def listen(self, client):
        while True:
            msg = client.recv(message_size).decode('utf-8')
            # Обработка системных сообщений
            if msg.startswith('%your address '):
                print(msg[1:])
            elif msg.startswith('%connection to '):
                self.connection = True
                self.request_done = False
            elif msg.startswith('%request to connection to '):
                print('Request completed, wait of connection...')
                self.request_done = True
            # И если всё-таки сообщение не является системным, то печатаем его для пользователя
            else:
                print('\r\r' + msg + '\n' + 'You>>> ', end='')

    # Метод, который отвечает за отправку сообщений
    def send(self, ip=server_ip, port=server_port):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.connect((ip, port))

        # Вынос в другой "поток" метода listen
        threading.Thread(target=self.listen, name='listen', args=[client], daemon=True).start()

        client.send('%connection'.encode('utf-8'))
        timer = 0
        while True:  # Получение запроса на подключение
            time.sleep(0.3)  # Небольшая задержка для нормального вывода
            if self.connection:
                print('Connection!')
                break
            elif self.request_done:
                seconds = datetime.datetime.now().second
                if timer + 2 <= seconds:
                    print('Waiting of connection...')
                    timer = seconds
            else:  # Запрашиваем адрес и проверяем, корректный ли он
                request_address = input('''Requesting address in format "IP:port" (DON'T REQUEST SELF!!!)>>> ''')
                if is_valid_address(request_address):
                    request_address = '%request ' + request_address  # Если да, то отправляем серверу запрос
                    client.send(request_address.encode('utf-8'))  # на подключение к нему
                else:
                    print('Invalid IP')
                timer = datetime.datetime.now().second

        while True:  # Отправка сообщений
            msg = input('You>>> ')
            msg = '%msg_to ' + msg
            client.send(msg.encode('utf-8'))