# Клиент
# Импорт встроенных библиотек
import pickle  # Складывание в байты данных
import socket  # Связь
import threading  # Многопоточность
from tkinter import Tk  # Для работы с буфером обмена
import time

# Импорт моих штучек
from constants_client import *
from client_something import *

# Импорт сторонних библиотек
from PyQt6.QtWidgets import (  # GUI библиотека
    QLabel,  # И все её приколы
    QWidget,
    QMainWindow,
    QApplication,
    QPushButton,
    QLineEdit,
    QMessageBox,
    QTabWidget,
    QGridLayout
)

from PyQt6.QtCore import (
    QSize,
    Qt,
    QThread,
    QObject,
    pyqtSignal,
)

from PyQt6.QtGui import (
    QPalette,
    QColor,
    QResizeEvent,
    QIcon,
    QPixmap,
    QMovie
)


# Тут наверняка будут ещё библиотеки, надо только подождать


# Класс для коммуникации потока прослушивания сервера и основного потока (графического)
class Communicate(QObject):
    create_game = pyqtSignal()
    update_address = pyqtSignal()
    set_cell = pyqtSignal()


# Класс вкладки с игрой
class TTTWindow(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Создаём кнопки и потом
        # проходимся по всем кнопкам игры и подключаем нажатие на них к функции,
        # которая возвращает отработавшую функцию нажатия

        self.game_buttons = [QPushButton(self) for _ in range(9)]
        list(map(lambda ttt_button: ttt_button.setFixedSize(100, 100), self.game_buttons))
        self.layout = QGridLayout(self)
        list(map(
            lambda ttt_button:
            ttt_button.clicked.connect(lambda checked, button=ttt_button: self.clicked_button(button)),
            self.game_buttons))
        self.game_buttons = dict(enumerate(self.game_buttons, start=1))
        for index, btn in self.game_buttons.items():
            self.layout.addWidget(btn, (index - 1) // 3 + 1, (index - 1) % 3 + 1)
        self.my_buttons = {}
        self.opponent_buttons = {}

        # Расставляем кнопки
        self.button_x = 100
        self.button_y = 100
        # Расстановка кнопок в окне
        self.buttons_widget = QWidget(self)
        self.buttons_widget.setLayout(self.layout)
        self.buttons_widget.setGeometry(10, 10, 900, 900)
        # for index, button in list(self.game_buttons.items())[:3]:
        #     button.setGeometry(self.button_x * index + index * 10, self.button_y, 100, 100)
        # for index, button in list(self.game_buttons.items())[3:6]:
        #     button.setGeometry(self.button_x * (index - 3) + (index - 3) * 10, self.button_y + 110, 100, 100)
        # for index, button in list(self.game_buttons.items())[6:]:
        #     button.setGeometry(self.button_x * (index - 6) + (index - 6) * 10, self.button_y + 220, 100, 100)

        # Картинка и текст команды игрока
        self.team_text = QLabel(self)
        self.team_text.setText('You')
        self.team_text.setGeometry(self.width() // 2, int(self.height() // 1.1), 50, 30)

        self.team_image = QLabel(self)
        self.images = {'crosses': r'other_files\Крестик.png',
                       'zeros': r'other_files\Нолик.png'}

        # self.team_image.setPixmap(QPixmap(r'other_files\Крестик.png'))
        self.team_image.setPixmap(QPixmap(self.images.get(self.main_window.team, '')))
        self.team_image.setGeometry(self.width() // 2, int(self.height() // 1.1) + 50, 100, 100)
        self.team_image.setScaledContents(True)

    def clicked_button(self, button):
        inverted_game_buttons = {btn: index for index, btn in self.game_buttons.copy().items()}
        team = ''
        if self.main_window.team == 'crosses':
            button.setIcon(QIcon(r'other_files\Крестик.png'))
            button.setIconSize(QSize(100, 100))
            team = 'crosses'

        elif self.main_window.team == 'zeros':
            button.setIcon(QIcon(r'other_files\Нолик.png'))
            button.setIconSize(QSize(100, 100))
            team = 'zeros'

        # Отправляем уведомление оппоненту о том, что сходили
        self.main_window.client.sendall(pickle.dumps(
            create_message('msg_to', (team, inverted_game_buttons[button]),
                           self.main_window.address, self.main_window.opponent)
        ))

        for index, btn in self.game_buttons.copy().items():
            self.game_buttons[index].setDisabled(True)
            if self.game_buttons[index] == button:
                self.my_buttons[index] = button
                del self.game_buttons[index]

        # Проверяем, не закончилась ли игра чье-либо победой
        if self.main_window.is_win(self.my_buttons, self.opponent_buttons) is not None:
            if self.main_window.is_win(self.my_buttons, self.opponent_buttons) == True:
                alert = QMessageBox(self)
                alert.setWindowTitle('You won!')
                alert.setText('You are the best!\n')
                alert.setIcon(QMessageBox.Icon.Information)
                alert.setFixedSize(QSize(200, 200))
                alert.show()
            elif self.main_window.is_win(self.my_buttons, self.opponent_buttons) == False:
                alert = QMessageBox(self)
                alert.setWindowTitle('You are defeated!')
                alert.setText('You are the best!\n')
                alert.setIcon(QMessageBox.Icon.Information)
                alert.setFixedSize(QSize(200, 200))
                alert.show()
            self.main_window.tab.removeTab(2)
            self.main_window.tab.addTab(TTTWindow(self), 'TTT Window')
            self.main_window.tab.setCurrentIndex(0)


# Класс вкладки ожидания
class WaitWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Виджет с гифкой ожидания подключения
        self.wait_gif = QLabel(self)
        self.wait_gif.setFixedSize(QSize(1920 // 5, 1080 // 5))
        self.wait_gif.setScaledContents(True)
        # 1567x1561 - размеры гифки №2 (надо брать размеры делённые на 8)
        # 1920x1080 - размеры гифки №3 (надо брать размеры делённые на 5)
        self.gif = QMovie(r'other_files\Connect_gif3.gif')

        self.wait_gif.setMovie(self.gif)
        self.gif.start()

        # >>> Текст, подсказывающий, что происходит
        self.alert_label = QLabel(self)
        self.alert_label.setFixedSize(169, 200)
        self.alert_label.setText('Request to connect completed. Please, wait of response request')
        self.alert_label.setWordWrap(True)

    # # # Функция, реагирующая на изменение окна
    def resizeEvent(self, event: QResizeEvent):
        self.wait_gif.setGeometry(
            (self.width() // 2) - (self.wait_gif.width() // 2),
            self.height() // 3,
            self.wait_gif.width(),
            self.wait_gif.height()
        )
        self.alert_label.setGeometry(
            (self.width() // 2) - (self.alert_label.width() // 2),
            self.wait_gif.y() + 120,  # На 120 пикселей вниз спускаемся для гифки №2 (для гифки №3 тоже так можно)
            self.alert_label.width(),
            self.alert_label.height()
        )


# Класс вкладки подключения
class ConnectWindow(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Кнопка для подключения
        self.button_connect = QPushButton(self)
        self.button_connect.setText('Connect!')
        self.button_connect.setGeometry(
            100,
            340,
            120,
            50
        )
        self.button_connect.clicked.connect(self.connect)

        # Поле ввода адреса
        self.address_line = QLineEdit(self)
        self.address_line.setFixedSize(QSize(220, 50))
        self.address_line.move(250, 340)
        # >>> Текст с информацией о том, что надо вводить в поле для ввода адреса
        self.caption_address_line = QLabel('Requesting address in format "IP:Port"', self)
        self.caption_address_line.setFixedSize(QSize(200, 30))
        self.caption_address_line.move(250, 300)

    def connect(self):
        address = self.address_line.text()
        # Если адрес корректный
        # И он не соответствует нашему адресу
        if is_valid_address(address) and \
                (address.split(':')[0], int(address.split(':')[1])) != self.main_window.address:
            # То отправляем запрос на подключение
            address = address.split(':')
            alert = QMessageBox(self)
            alert.setWindowTitle('Request completed!')
            alert.setText('You are the best!\nWait of response request')
            alert.setIcon(QMessageBox.Icon.Information)
            alert.setFixedSize(QSize(200, 200))
            alert.show()
            self.main_window.tab.setCurrentIndex(1)
            address = (address[0], int(address[1]))
            self.main_window.client.sendall(pickle.dumps(create_message('connect_to',
                                                                        address, self.main_window.address, address)))
        else:
            alert = QMessageBox(self)
            alert.setWindowTitle('Error of request!')
            alert.setText('Invalid address or entered address is your address!')
            alert.setIcon(QMessageBox.Icon.Critical)
            alert.show()


# Класс интерфейса
class MainWindow(QMainWindow):
    def __init__(self, ip=server_ip, port=server_port):
        super().__init__()

        print('Start app')

        # Начальная настройка
        self.setWindowTitle('Название съели')
        self.setMinimumSize(QSize(650, 480))
        self.move(500, 220)

        # Объект для коммуникации основного потока (графического) с потоком прослушивания сервера
        self.communicate = Communicate()
        self.communicate.update_address.connect(self.update_address)
        self.communicate.create_game.connect(self.create_game)
        self.communicate.set_cell.connect(self.set_cell)

        # Создание сокета, подключение к серверу и прочие штучки для игры по сети
        self.address = ('127.0.0.1', 9091)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.connect((ip, port))
        threading.Thread(target=self.listen, name='listen', daemon=True).start()
        msg = create_message('set_mode', 'online', 'No address', (ip, port))
        self.client.sendall(pickle.dumps(msg))
        self.opponent = ()  # Оппонент в игре
        self.team = ''  # Команда (?), за которую играет игрок (крестики/нолики)
        self.last_message = {}

        # Для работы с буфером обмена
        self.clipboard = Tk()

        # Меню со вкладками
        self.tab = QTabWidget(self)
        self.tab.addTab(ConnectWindow(self), 'Connect Window')  # Вкладка с подключением
        self.tab.addTab(WaitWindow(), 'Wait Window')  # Вкладка с окном ожидания
        self.tab.addTab(TTTWindow(self), 'TTT Window')  # Вкладка с самой игрой
        self.tab.setCurrentIndex(0)
        self.tab.setTabPosition(QTabWidget.TabPosition.South)

        # Строчка вашего адреса
        self.address_line = QLabel(self)
        self.address_line.setText(f'Your address - {self.address[0]}:{self.address[1]}')
        self.address_line.setGeometry(0, 0, 200, 30)

        # Кнопка для копирования это вашего адреса
        self.address_copy_button = QPushButton(self)
        self.address_copy_button.setText('Copy')
        self.address_copy_button.setGeometry(590, 0, 40, 30)
        self.address_copy_button.clicked.connect(self.copy_to_clipboard)

    # Функция заноса в буфер обмена адреса
    def copy_to_clipboard(self):
        self.clipboard.clipboard_clear()
        self.clipboard.clipboard_append(f'{self.address[0]}:{self.address[1]}')

    # Функции сигналов для реакции на входящие сообщения сервера.
    # >>> Функция обновления адреса.
    def update_address(self):
        self.address_line.setText(f'Your address - {self.address[0]}:{self.address[1]}')

    # >>> Функция перехода на страничку игры, если подключились.
    def create_game(self):
        self.tab.removeTab(2)
        self.tab.addTab(TTTWindow(self), 'TTT Window')
        self.tab.setCurrentIndex(2)
        if self.team == 'crosses':
            pass
        else:
            for button in self.tab.currentWidget().game_buttons.values():
                button.setDisabled(True)

    # >>> Функция задавания клетке игры в крестики-нолики определённого значения (крестик/нолик)
    def set_cell(self):
        game = self.tab.currentWidget()
        button = game.game_buttons[self.last_message['msg'][1]]
        if self.last_message['msg'][0] == 'crosses':
            button.setIcon(QIcon(r'other_files\Крестик.png'))
            button.setIconSize(QSize(100, 100))
        elif self.last_message['msg'][0] == 'zeros':
            button.setIcon(QIcon(r'other_files\Нолик.png'))
            button.setIconSize(QSize(100, 100))

        for index, btn in game.game_buttons.copy().items():
            game.game_buttons[index].setDisabled(False)
            if game.game_buttons[index] == button:
                game.game_buttons[index].setDisabled(True)
                game.opponent_buttons[index] = button
                del game.game_buttons[index]

        # Проверяем, не закончилась ли игра чье-либо победой
        if self.is_win(game.my_buttons, game.opponent_buttons) is not None:
            if self.is_win(game.my_buttons, game.opponent_buttons) == True:
                alert = QMessageBox(self)
                alert.setWindowTitle('You won!')
                alert.setText('You are the best!\n')
                alert.setIcon(QMessageBox.Icon.Information)
                alert.setFixedSize(QSize(200, 200))
                alert.show()
            elif self.is_win(game.my_buttons, game.opponent_buttons) == False:
                alert = QMessageBox(self)
                alert.setWindowTitle('You are defeated!')
                alert.setText('You are the best!\n')
                alert.setIcon(QMessageBox.Icon.Information)
                alert.setFixedSize(QSize(200, 200))
                alert.show()
            self.tab.removeTab(2)
            self.tab.addTab(TTTWindow(self), 'TTT Window')
            self.tab.setCurrentIndex(0)



    # Слушаем сервер
    def listen(self):
        while True:
            msg = pickle.loads(self.client.recv(message_size))
            print(msg)
            if msg['command'] == 'get_address':
                self.address = msg['msg']
                self.communicate.update_address.emit()
            elif msg['command'] == 'connecting':
                self.opponent = msg['msg'][0]
                self.team = msg['msg'][1]
                self.communicate.create_game.emit()
            elif msg['command'] == 'msg_to':
                pass
                self.communicate.set_cell.emit()
                self.last_message = msg

    def is_win(self, my_buttons, opponent_buttons):
        my_buttons = set(my_buttons.keys())
        winning_buttons = [{1, 4, 7}, {1, 2, 3}, {3, 6, 9}, {7, 8, 9}, {1, 5, 9}, {3, 5, 7}, {2, 5, 8}, {4, 5, 6}]
        for buttons in winning_buttons:
            if all(map(lambda num_button: num_button in my_buttons, buttons)):
                return True
            elif all(map(lambda num_button: num_button in opponent_buttons, buttons)):
                return False
        return None

    # Функция, реагирующая на изменение размера приложения (ивент изменения размеров приложения)
    def resizeEvent(self, event: QResizeEvent):
        self.tab.setGeometry(
            0,
            0,
            self.size().width(),
            self.size().height() - 20
        )

        # Изменение положения строки адреса и кнопки копирования
        self.address_line.setGeometry(
            self.width() - self.address_line.width() - self.address_copy_button.width() - 10,
            0,
            200,
            30
        )

        self.address_copy_button.setGeometry(
            self.width() - self.address_copy_button.width() - 10,
            0,
            40,
            30
        )

    # Функция, реагирующая на выключение приложения (ивент закрытия)
    # Уведомляем о закрытии приложения сервер (следовательно, сервер должен изменить статус пользователя на "Offline")
    def closeEvent(self, event):
        print('Close app')
        msg = create_message('set_mode', 'offline', self.address, (server_ip, server_port))
        self.client.sendall(pickle.dumps(msg))


# Создаём приложение и запускаем его
app = QApplication([])
window = MainWindow()
window.show()

app.exec()

# Discord: Jagor#6537
