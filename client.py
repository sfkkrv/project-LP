import sys
import requests
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QMessageBox


SERVER_URL = "localhost"

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

        self.add_button = QPushButton("Добавить в базу", self)
        self.add_button.clicked.connect(self.start_add_leak)

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
        layout.addWidget(self.add_button)
        self.setLayout(layout)

    # Проверка утечки в отдельном потоке
    def start_check_leak(self):
        threading.Thread(target=self.check_leak, daemon=True).start()

    def check_leak(self):
        email = self.input_email.text()
        username = self.input_username.text()
        password = self.input_password.text()

        data = {"email": email, "username": username, "password": password}
        response = requests.post("25.69.126.6", json=data)

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

    def add_leak(self):
        email = self.email_input.text() or None
        username = self.username_input.text() or None
        password = self.password_input.text() or None
        leaked_data = self.data_input.text()

        if not leaked_data:
            self.result_text.setText("Введите описание утечки!")
            return

        payload = {
            "email": email,
            "username": username,
            "password": password,
            "leaked_data": leaked_data
        }
        try:
            response = requests.post(f"{SERVER_URL}/add_leak", json=payload)
            if response.status_code == 200:
                self.result_text.setText("Данные успешно добавлены")
            else:
                self.result_text.setText("Ошибка при добавлении данных")
        except requests.exceptions.ConnectionError:
            self.result_text.setText("Ошибка: сервер недоступен")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = ClientApp()
    client.show()
    sys.exit(app.exec())
