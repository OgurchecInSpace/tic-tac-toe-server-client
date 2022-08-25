# Клиент
# Импорт встроенных библиотек
import pickle  # Складывание в байты данных
import socket  # Связь
import threading  # Многопоточность
import random
from tkinter import Tk  # Для работы с буфером обмена

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
# Upd. 28.07.22 Судя по всему, ещё библиотек не будет


# Класс с фоном, от которого наследуются все вкладки игры
class Background1:
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.background = QLabel(self)
        self.background.setPixmap(QPixmap(r'other_files\Фон.png'))
        self.background.setGeometry(0, 0, self.main_window.width(), self.main_window.height())
        self.last_size_background = (self.main_window.width(), self.main_window.height())
        self.background.setScaledContents(True)


# Класс с фоном, от которого наследуются все вкладки игры
class Background:
    def __init__(self):
        super().__init__()
        self.background = QLabel(self)
        self.background.setPixmap(QPixmap(r'other_files\Фон.png'))
        self.background.setGeometry(0, 0, self.width(), self.height())
        self.last_size_background = (self.width(), self.height())
        self.background.setScaledContents(True)


# Класс для коммуникации потока прослушивания сервера и основного потока (графического)
class Communicate(QObject):
    create_game = pyqtSignal()
    update_address = pyqtSignal()
    set_cell = pyqtSignal()


# Класс вкладки с игрой по сети
class TTTWindow(QMainWindow, Background):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Создаём кнопки
        self.game_buttons = [QPushButton(self) for _ in range(9)]
        # И словари для нажатых нами кнопок и кнопок, нажатых оппонентом
        self.my_buttons = {}
        self.opponent_buttons = {}
        # Задаём кнопкам размер
        list(map(lambda ttt_button: ttt_button.setFixedSize(100, 100), self.game_buttons))
        # проходимся по всем кнопкам игры и подключаем нажатие на них к функции,
        # которая возвращает отработавшую функцию нажатия
        list(map(
            lambda ttt_button:
            ttt_button.clicked.connect(lambda checked, button=ttt_button: self.clicked_button(button)),
            self.game_buttons))
        # Превращаем список с кнопками в словарь, номер кнопки: кнопка
        self.game_buttons = dict(enumerate(self.game_buttons, start=1))
        # Сетка для удобного размещения кнопок и виджет, который её отображает
        self.buttons_widget = QWidget(self)
        self.layout = QGridLayout(self.buttons_widget)
        self.layout.setSpacing(0)
        for index, btn in self.game_buttons.items():
            self.layout.addWidget(btn, (index - 1) // 3 + 1, (index - 1) % 3 + 1)
        self.buttons_widget.setLayout(self.layout)
        self.buttons_widget.setGeometry(int(self.width() // 5.5), int(self.height() // 7), 400, 400)

        # Картинка и текст команды игрока
        self.team_text = QLabel(self)
        self.team_text.setText('You')
        self.team_text.setGeometry(self.width() // 2, int(self.height() // 1.1), 20, 10)

        self.team_image = QLabel(self)
        self.images = {'crosses': r'other_files\Крестик.png',
                       'zeros': r'other_files\Нолик.png'}

        self.team_image.setPixmap(QPixmap(self.images.get(self.main_window.team, '')))
        self.team_image.setGeometry(self.width() // 2, int(self.height() // 1.1) + 50, 50, 50)
        self.team_image.setScaledContents(True)

    # Функция нажатия на кнопку игры
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
            if self.main_window.is_win(self.my_buttons, self.opponent_buttons):
                # Отображаем победу
                self.preparation_end_game('win_image')

            elif not self.main_window.is_win(self.my_buttons, self.opponent_buttons):
                # Отображаем поражение
                self.preparation_end_game('defeat_image')
        # Если не кончилась победой, то проверяем на ничью
        else:
            if len(self.game_buttons.keys()) == 0:
                self.preparation_end_game('tie_image')

    # Функция окончания игры
    def preparation_end_game(self, image):
        # Картинка окончания игры
        self.image_end_game = QLabel(self)
        self.image_end_game.setPixmap(QPixmap(fr'other_files\{image}.png'))
        self.image_end_game.setGeometry(self.width() // 2 - 250, self.height() // 2 - 250, 500, 500)
        self.image_end_game.show()

        # Кнопка окончания игры
        self.button_end = QPushButton(self)
        self.button_end.setText('End game')
        self.button_end.setGeometry(0, 0, 80, 40)
        self.button_end.show()
        self.button_end.clicked.connect(self.end_game)

    # Функция переноса пользователя в главное меню и пересозданием меню игры
    def end_game(self):
        self.main_window.tab.removeTab(self.main_window.tab.indexOf(self.main_window.ttt_window))
        self.main_window.ttt_window = TTTWindow(self.main_window)
        self.main_window.tab.addTab(self.main_window.ttt_window, 'TTT Window')
        self.main_window.tab.setCurrentWidget(self.main_window.connect_window)

    def resizeEvent(self, event: QResizeEvent):
        self.background.setGeometry(
            -10, -10,
            self.width() + 10, self.height() + 10
        )

        # Кнопки
        self.buttons_widget.setGeometry(
            self.width() // 2 - self.buttons_widget.width() // 2,
            self.height() // 2 - self.buttons_widget.height() // 2,
            400,
            400)
        # Подпись к картинке команды
        self.team_text.setGeometry(
            self.width() // 2 - self.team_text.width() // 2,
            self.buttons_widget.y() + self.buttons_widget.height() - 30,
            20,
            30
        )
        # Картинка команды
        self.team_image.setGeometry(
            self.width() // 2 - self.team_image.width() // 2,
            self.buttons_widget.y() + self.buttons_widget.height() + self.team_text.height() - 40,
            50,
            50
        )

        try:
            self.image_end_game.setGeometry(int(self.width() // 2) - 250, self.height() // 2 - 250, 500, 500)
        except:
            pass


# Класс вкладки для игры с ботом (который жутко тупой)
class TTTWindowOffline(QMainWindow, Background):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Создаём кнопки
        self.game_buttons = [QPushButton(self) for _ in range(9)]
        # И словари для нажатых нами кнопок и кнопок, нажатых оппонентом
        self.crosses_buttons = {}
        self.zeros_buttons = {}
        # Задаём кнопкам размер
        list(map(lambda ttt_button: ttt_button.setFixedSize(100, 100), self.game_buttons))
        # проходимся по всем кнопкам игры и подключаем нажатие на них к функции,
        # которая возвращает отработавшую функцию нажатия
        list(map(
            lambda ttt_button:
            ttt_button.clicked.connect(lambda checked, button=ttt_button: self.clicked_button(button)),
            self.game_buttons))
        # Превращаем список с кнопками в словарь, номер кнопки: кнопка
        self.game_buttons = dict(enumerate(self.game_buttons, start=1))
        # Сетка для удобного размещения кнопок и виджет, который её отображает
        self.buttons_widget = QWidget(self)
        self.layout = QGridLayout(self.buttons_widget)
        self.layout.setSpacing(0)
        for index, btn in self.game_buttons.items():
            self.layout.addWidget(btn, (index - 1) // 3 + 1, (index - 1) % 3 + 1)
        self.buttons_widget.setLayout(self.layout)
        self.buttons_widget.setGeometry(int(self.width() // 5.5), int(self.height() // 7), 400, 400)

        # Команда игрока
        self.team = 'crosses'

        # Картинка и текст команды игрока
        self.team_text = QLabel(self)
        self.team_text.setText('You')
        self.team_text.setGeometry(self.width() // 2, int(self.height() // 1.1), 25, 10)

        self.team_image = QLabel(self)
        self.images = {'crosses': r'other_files\Крестик.png',
                       'zeros': r'other_files\Нолик.png'}

        self.team_image.setPixmap(QPixmap(self.images[self.team]))
        self.team_image.setGeometry(self.width() // 2, int(self.height() // 1.1) + 50, 50, 50)
        self.team_image.setScaledContents(True)

    # Функция, которая реагирует на нажатие пользователем на кнопку (отображает картинку на ней, "нажимает" сама
    # на случайную кнопку и т.д.)
    def clicked_button(self, button):
        inverted_game_buttons = {btn: index for index, btn in self.game_buttons.copy().items()}
        button.setIcon(QIcon(self.images[self.team]))
        button.setIconSize(QSize(100, 100))
        self.crosses_buttons[inverted_game_buttons[button]] = button
        button.setDisabled(True)
        del self.game_buttons[inverted_game_buttons[button]]
        if len(self.game_buttons.values()) > 0:
            random_button = random.choice(list(self.game_buttons.values()))
            random_button.setIcon(QIcon(self.images['zeros']))
            self.zeros_buttons[inverted_game_buttons[random_button]] = random_button
            random_button.setIconSize(QSize(100, 100))
            random_button.setDisabled(True)
            del self.game_buttons[inverted_game_buttons[random_button]]

        # Проверяем, не закончилась ли игра чье-либо победой
        if self.main_window.is_win(self.crosses_buttons, self.zeros_buttons) is not None:
            if self.main_window.is_win(self.crosses_buttons, self.zeros_buttons):
                # Отображаем победу
                self.preparation_end_game('win_crosses_image')
                # Костыль (или нет?)
                try:
                    random_button.setIcon(QIcon(''))
                    random_button.setEnabled(True)
                except:
                    pass
            elif not self.main_window.is_win(self.crosses_buttons, self.zeros_buttons):
                # Отображаем поражение
                self.preparation_end_game('win_zeros_image')
        # Если не кончилась победой, то проверяем на ничью
        else:
            if len(self.game_buttons.keys()) == 0:
                self.preparation_end_game('tie_image')

    # Функция окончания игры
    def preparation_end_game(self, image):
        # Картинка окончания игры
        self.image_end_game = QLabel(self)
        self.image_end_game.setPixmap(QPixmap(fr'other_files\{image}.png'))
        self.image_end_game.setGeometry(self.width() // 2 - 250, self.height() // 2 - 250, 500, 500)
        self.image_end_game.show()

        # Кнопка окончания игры
        self.button_end = QPushButton(self)
        self.button_end.setText('End game')
        self.button_end.setGeometry(0, 0, 80, 40)
        self.button_end.show()
        self.button_end.clicked.connect(self.end_game)

    # Функция переноса пользователя в главное меню и пересозданием меню игры
    def end_game(self):
        self.main_window.tab.removeTab(self.main_window.tab.indexOf(self.main_window.ttt_window_offline))
        self.main_window.ttt_window_offline = TTTWindowOffline(self.main_window)
        self.main_window.tab.addTab(self.main_window.ttt_window_offline, 'TTT Window Offline')
        self.main_window.tab.setCurrentWidget(self.main_window.connect_window)

    def resizeEvent(self, event: QResizeEvent):
        self.background.setGeometry(
            -10, -10,
            self.width() + 10, self.height() + 10
        )

        # Кнопки
        self.buttons_widget.setGeometry(
            self.width() // 2 - self.buttons_widget.width() // 2,
            self.height() // 2 - self.buttons_widget.height() // 2,
            400,
            400)
        # Подпись к картинке команды
        self.team_text.setGeometry(
            self.width() // 2 - self.team_text.width() // 2,
            self.buttons_widget.y() + self.buttons_widget.height() - 30,
            25,
            30
        )
        # Картинка команды
        self.team_image.setGeometry(
            self.width() // 2 - self.team_image.width() // 2,
            self.buttons_widget.y() + self.buttons_widget.height() + self.team_text.height() - 40,
            50,
            50
        )

        try:
            self.image_end_game.setGeometry(int(self.width() // 2) - 250, self.height() // 2 - 250, 500, 500)
        except:
            pass


# Класс вкладки ожидания подключения
class WaitWindow(QMainWindow, Background):
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
        self.background.setGeometry(
            -10, -10,
            self.width() + 10, self.height() + 10
        )

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


# Класс вкладки для выбора игры
class ConnectWindow(QMainWindow, Background):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Кнопка для подключения для игры с настоящим игроком
        self.button_connect = QPushButton(self)
        self.button_connect.setText('Connect!')
        self.button_connect.setGeometry(
            self.width() // 2 - 120 // 2, self.height() // 2, 220, 50
        )
        self.button_connect.clicked.connect(self.connect)

        # Кнопка для игры в одиночку (с другом)
        self.button_offline_game = QPushButton(self)
        self.button_offline_game.setText('Play offline')
        self.button_offline_game.setGeometry(
            self.width() // 2 - 120 // 2 - self.button_connect.y(),
            self.height() // 2, 220, 50
        )
        self.button_offline_game.clicked.connect(self.create_offline_game)

        # Текст с информацией о том, что надо вводить в поле для ввода адреса
        self.caption_address_line = QLabel('Requesting address in format "IP:Port"', self)
        self.caption_address_line.setGeometry(
            self.width() // 2, self.height() // 2 + self.button_connect.height(), 200, 30
        )

        # Поле ввода адреса
        self.address_line = QLineEdit(self)
        self.address_line.setGeometry(
            self.width() // 2 - 220 // 2,
            self.height() // 2 + self.button_connect.height() + self.caption_address_line.height(), 220, 50
        )

    # Функция для подключения к оппоненту по игре
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

    # Функция для игры оффлайн (с другим человеком за одним ПК)
    def create_offline_game(self):
        self.main_window.tab.removeTab(self.main_window.tab.indexOf(self.main_window.ttt_window_offline))
        self.main_window.ttt_window_offline = TTTWindowOffline(self.main_window)
        self.main_window.tab.addTab(self.main_window.ttt_window_offline, 'TTT Window Offline')
        self.main_window.tab.setCurrentWidget(self.main_window.ttt_window_offline)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.background.setGeometry(
            -10, -10,
            self.width() + 10, self.height() + 10
        )

        # Изменяем положение текста
        self.caption_address_line.setGeometry(
            self.width() // 2 - self.caption_address_line.width() // 2,
            self.height() // 2,
            200,
            30
        )

        # поля ввода адреса
        self.address_line.setGeometry(
            self.width() // 2 - self.address_line.width() // 2,
            self.height() // 2 + self.caption_address_line.height(),
            220,
            50
        )

        # И кнопки
        self.button_connect.setGeometry(
            self.width() // 2 - self.button_connect.width() // 2,
            self.height() // 2 + self.caption_address_line.height() + self.address_line.height() + 5,
            220,
            50
        )

        self.button_offline_game.setGeometry(
            self.width() // 2 - self.button_offline_game.width() // 2,
            self.height() // 2 + self.caption_address_line.height() + self.address_line.height() + 10 +
            self.button_connect.height(),
            220,
            50
        )


# Класс интерфейса
class MainWindow(QMainWindow):
    def __init__(self, ip=server_ip, port=server_port):
        super().__init__()

        print('Start app')

        # Начальная настройка

        self.setWindowTitle('Tic-Tac-Toe Online')
        self.setMinimumSize(QSize(650, 540))
        self.move(500, 220)

        # Объект для коммуникации основного потока (графического) с потоком прослушивания сервера
        self.communicate = Communicate()
        self.communicate.update_address.connect(self.update_address)
        self.communicate.create_game.connect(self.create_game)
        self.communicate.set_cell.connect(self.set_cell)

        # Создание сокета, подключение к серверу и прочие штучки для игры по сети
        self.address = ('127.0.0.1', 9091)
        self.online = False
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
        self.connect_window = ConnectWindow(self)
        self.wait_window = WaitWindow()
        self.ttt_window = TTTWindow(self)
        self.ttt_window_offline = TTTWindowOffline(self)
        self.tab.addTab(self.connect_window, 'Connect Window')  # Вкладка с подключением
        self.tab.addTab(self.wait_window, 'Wait Window')  # Вкладка с окном ожидания
        self.tab.addTab(self.ttt_window, 'TTT Window')  # Вкладка с самой игрой
        self.tab.addTab(self.ttt_window_offline, 'TTT Window Offline')  # Вкладка для игры оффлайн
        self.tab.setCurrentWidget(self.connect_window)
        self.tab.setTabPosition(QTabWidget.TabPosition.South)

        # Строчка вашего адреса
        self.address_line = QLabel(self)
        self.address_line.setText(f'You are offline!')
        self.address_line.setGeometry(0, 0, 200, 30)

        # Кнопка для копирования адреса
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
        self.tab.removeTab(self.tab.indexOf(self.ttt_window))
        self.ttt_window = TTTWindow(self)
        self.tab.addTab(self.ttt_window, 'TTT Window')
        self.tab.setCurrentWidget(self.ttt_window)
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
        game = self.tab.currentWidget()
        if self.is_win(game.my_buttons, game.opponent_buttons) is not None:
            if self.is_win(game.my_buttons, game.opponent_buttons) == True:
                game.preparation_end_game('win_image')

            elif self.is_win(game.my_buttons, game.opponent_buttons) == False:
                game.preparation_end_game('defeat_image')
        else:
            if len(game.game_buttons.keys()) == 0:
                game.preparation_end_game('tie_image')

    # Слушаем сервер
    def listen(self):
        while True:
            msg = pickle.loads(self.client.recv(message_size))
            print(msg)
            if msg['command'] == 'get_address':
                self.address = msg['msg']
                self.communicate.update_address.emit()
                self.online = True
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
            self.size().height() + 50
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
