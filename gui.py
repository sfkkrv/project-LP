import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout

class ServerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.server_process = None  # Процесс сервера

    def initUI(self):
        self.setWindowTitle("Управление сервером")
        self.setGeometry(100, 100, 300, 200)

        self.status_label = QLabel("Сервер: Остановлен", self)

        self.start_button = QPushButton("Запустить сервер", self)
        self.start_button.clicked.connect(self.start_server)

        self.stop_button = QPushButton("Остановить сервер", self)
        self.stop_button.clicked.connect(self.stop_server)
        self.stop_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        self.setLayout(layout)

    def start_server(self):
        if not self.server_process:
            self.server_process = subprocess.Popen(["python", "server.py"])
            self.status_label.setText("Сервер: Запущен")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

    def stop_server(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None
            self.status_label.setText("Сервер: Остановлен")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

if name == '__main__':
    app = QApplication(sys.argv)
    gui = ServerGUI()
    gui.show()
    sys.exit(app.exec())
