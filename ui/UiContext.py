import sys
import os
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QFormLayout, QLabel, QLineEdit, QComboBox, QPushButton
from PyQt5.QtCore import pyqtSignal, QObject

from WSClient import WSClient
from Context import Context
from .UiHome import UiHome


def load_stylesheet():
    """Charge le fichier QSS MacOs.qss"""
    qss_path = os.path.join(os.path.dirname(__file__), 'MacOs.qss')
    with open(qss_path, 'r') as f:
        return f.read()


class SignalEmitter(QObject):
    connected = pyqtSignal()


class UiContext(QWidget):
    def __init__(self):
        super().__init__()
        self.client = None
        self.signal_emitter = SignalEmitter()
        self.signal_emitter.connected.connect(self.on_connection_success)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Connexion WebSocket")
        self.setGeometry(150, 150, 350, 150)

        layout = QFormLayout()

        # NAME
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Client")
        layout.addRow(QLabel("Name:"))
        layout.addRow(self.name_input)

        # HOST
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("127.0.0.1")
        layout.addRow(QLabel("Host:"))
        layout.addRow(self.host_input)

        # PORT
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("9000")
        layout.addRow(QLabel("Port:"))
        layout.addRow(self.port_input)

        # ENV
        self.env_combo = QComboBox()
        self.env_combo.addItems(['dev', 'prod'])
        layout.addRow(QLabel("Env:"))
        layout.addRow(self.env_combo)

        connect_btn = QPushButton('Connect')
        connect_btn.clicked.connect(self.on_connect)
        layout.addWidget(connect_btn)

        self.setLayout(layout)

    def on_connect(self):
        host = self.host_input.text().strip()
        port = self.port_input.text().strip()
        name = self.name_input.text().strip() or "Client"

        if not host or not port:
            env = self.env_combo.currentText()
            if env == 'dev':
                ctx = Context.dev()
            else:
                ctx = Context.prod()
        else:
            ctx = Context(host, int(port))

        self.client = WSClient(ctx, username=name, on_connect_callback=self.emit_connected_signal)

        connect_thread = threading.Thread(target=self.client.connect, daemon=True)
        connect_thread.start()

    def emit_connected_signal(self):
        self.signal_emitter.connected.emit()

    def on_connection_success(self):
        self.home = UiHome(self.client)
        self.home.show()
        self.close()


if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet(load_stylesheet())
    ui_context = UiContext()
    ui_context.show()
    sys.exit(app.exec_())
