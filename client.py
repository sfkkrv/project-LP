import sys
import requests
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal, QThread

SERVER_URL = "http://25.69.126.6:5000"

class ClientApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Клиент проверки утечек")
        self.setGeometry(100, 100, 400, 400)

        self.label = QLabel("Введите Email / Логин / Пароль:", self)
        self.input_field = QLineEdit(self)

        self.check_button = QPushButton("Проверить утечку", self)
        self.check_button.clicked.connect(self.start_check_leak)

        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Email (необязательно)")

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Логин (необязательно)")

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Пароль (необязательно)")

        self.data_input = QLineEdit(self)
        self.data_input.setPlaceholderText("Описание утечки")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.check_button)
        layout.addWidget(self.result_text)
        layout.addWidget(self.email_input)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.data_input)
        self.setLayout(layout)

    # Проверка утечки в отдельном потоке
    def start_check_leak(self):
        email = self.email_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not (email or username or password):
            self.result_text.setText("Введите хотя бы одно поле: Email, логин или пароль!")
            return

        payload = {
            "email": email if email else None,
            "username": username if username else None,
            "password": password if password else None
        }

        self.thread = QThread()
        self.worker = LeakChecker(payload)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_check_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_check_finished(self, result):
        self.result_text.setText(result)

    def check_leak(self):
        email = self.email_input.text()
        username = self.username_input.text()
        password = self.password_input.text()

        data = {"email": email, "username": username, "password": password}
        response = requests.post("http://25.69.126.6:5000/check", json=data)

        if response.status_code == 200:
            result = response.json()
            if result["status"] == "leaked":
                QMessageBox.warning(self, "Результат", "Данные утекли! " + result["details"])
            else:
                QMessageBox.information(self, "Результат", "Данные в безопасности")
        else:
            QMessageBox.critical(self, "Ошибка", "Ошибка соединения с сервером")


    # Добавление утечки в отдельном потоке
    def start_add_leak(self):
        threading.Thread(target=self.add_leak, daemon=True).start()


class LeakChecker(QObject):
    finished = pyqtSignal(str)

    def __init__(self, payload):
        super().__init__()
        self.payload = payload

    def run(self):
        try:
            response = requests.post(f"{SERVER_URL}/check", json=self.payload)
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "leaked":
                    result = f"Обнаружена утечка:\n{data['details']}"
                else:
                    result = "Утечек не найдено."
            else:
                result = "Ошибка при запросе к серверу"
        except requests.exceptions.ConnectionError:
            result = "Ошибка: сервер недоступен"

        self.finished.emit(result)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = ClientApp()
    client.show()
    sys.exit(app.exec())



