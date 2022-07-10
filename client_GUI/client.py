# Клиент
# Импорт встроенных библиотек
import pickle
import socket
import threading
import time

# Импорт моих штучек
from constants_client import *
from something import *

# Импорт пользовательских библиотек
from PyQt6.QtWidgets import (  # GUI библиотека
    QLabel,  # И все её приколы
    QLayout,
    QWidget,
    QMainWindow,
    QApplication,
    QPushButton,
    QLineEdit,
    QPlainTextEdit,
    QMessageBox,
    QTabWidget,
    QVBoxLayout,
    QComboBox
)

from PyQt6.QtCore import (
    QSize,
    Qt,
    QThread,
    QObject,
    pyqtSignal
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


# Класс вкладки с игрой
class TTTWindow(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.label = QLabel(self)
        self.label.setText('privet')
        self.label.setGeometry(50, 50, 200, 200)


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
        self.gif = QMovie('Connect_gif3.gif')

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


# Класс вкладки подключенияx
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
        if is_valid_address(address):
            alert = QMessageBox(self)
            alert.setWindowTitle('Request completed!')
            alert.setText('You are the best!\nWait of response request')
            alert.setIcon(QMessageBox.Icon.Information)
            alert.setFixedSize(QSize(200, 200))
            alert.show()
            self.main_window.tab.setCurrentIndex(1)
        else:
            alert = QMessageBox(self)
            alert.setWindowTitle('Error of request!')
            alert.setText('Invalid address!')
            alert.setIcon(QMessageBox.Icon.Critical)
            alert.show()


# Класс интерфейса
class MainWindow(QMainWindow):
    def __init__(self, ip=server_ip, port=server_port):
        super().__init__()

        # Начальная настройка
        self.setWindowTitle('Название съели')
        self.setMinimumSize(QSize(650, 480))
        self.move(475, 200)

        # Создание сокета и подключение к серверу
        self.address = ('127.0.0.1', 9091)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.connect((ip, port))
        threading.Thread(target=self.listen, name='listen', daemon=True).start()
        msg = create_message('set_mode', 'online', 'No address', (ip, port))
        self.client.sendall(pickle.dumps(msg))

        # Меню со вкладками
        self.tab = QTabWidget(self)
        self.tab.addTab(ConnectWindow(self), 'Connect Window')  # Вкладка с подключением
        self.tab.addTab(WaitWindow(), 'Wait Window')  # Вкладка с окном ожидания
        self.tab.addTab(TTTWindow(self), 'TTT Window')  # Вкладка с самой игрой
        self.tab.setCurrentIndex(0)
        self.tab.setTabPosition(QTabWidget.TabPosition.South)

        self.address_line = QLabel(self)
        self.address_line.setText(f'Your address - {self.address[0]}:{self.address[1]}')
        self.address_line.setGeometry(0, 0, 200, 50)

        self.communicate = Communicate()
        self.communicate.update_address.connect(self.update_address)

    def update_address(self):
        self.address_line.setText(f'Your address - {self.address[0]}:{self.address[1]}')

    # Слушаем сервер (НАДО ЗАКОММЕНТИРОВАТЬ, А ТО Я НИЧЕГО НЕ ПОНИМАЮ)
    def listen(self):
        while True:
            data = pickle.loads(self.client.recv(message_size))
            print(data)
            if data['command'] == 'get_address':
                self.address = data['msg']
                self.communicate.update_address.emit()

    # Функция, реагирующая на изменение размера приложения (ивент изменения размеров приложения)
    def resizeEvent(self, event: QResizeEvent):
        self.tab.setGeometry(  # Задаём новые размеры приложению
            0,
            0,
            self.size().width(),
            self.size().height() - 20
        )

        self.address_line.setGeometry(
            self.width() - self.address_line.width() - 10,
            0,
            200,
            50
        )

    # Функция, реагирующая на выключение приложения (ивент закрытия)
    # Уведомляем о закрытии приложения сервер (следовательно, сервер должен изменить статус пользователя на "Offline")
    def closeEvent(self, event):
        print('Close app')
        msg = create_message('set_mode', 'online', 'No address', (server_ip, server_port))
        self.client.sendall(pickle.dumps(msg))


# Создаём приложение и запускаем его
app = QApplication([])
window = MainWindow()
window.show()

app.exec()

# Discord: Jagor#6537
