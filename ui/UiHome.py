import sys
import base64
import tempfile
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QComboBox, QPushButton, QTextEdit, QFileDialog, QScrollArea)
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

sys.path.append('..')
from Message import MessageType


def load_stylesheet():
    """Charge le fichier QSS MacOs.qss"""
    qss_path = os.path.join(os.path.dirname(__file__), 'MacOs.qss')
    with open(qss_path, 'r') as f:
        return f.read()


class SignalEmitter(QObject):
    message_received = pyqtSignal(object)
    users_list_received = pyqtSignal(list)


class UiHome(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.signal_emitter = SignalEmitter()
        self.signal_emitter.message_received.connect(self.on_message_received)
        self.signal_emitter.users_list_received.connect(self.on_users_list_received)

        # Audio player
        self.media_player = QMediaPlayer()
        self.audio_data = None
        self.temp_audio_file = None

        # Video player
        self.video_player = QMediaPlayer()
        self.video_data = None
        self.temp_video_file = None

        # Connecter les callbacks du client
        if self.client:
            self.client.on_message_callback = self.emit_message_signal
            self.client.on_users_list_callback = self.emit_users_list_signal

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Home")
        self.setGeometry(150, 150, 900, 650)

        # Layout principal horizontal
        main_layout = QHBoxLayout()

        # Partie gauche (messages et contrôles)
        left_layout = QVBoxLayout()

        # Label de connexion
        left_layout.addWidget(QLabel(f"Connecté en tant que: {self.client.username}"))

        # Zone de messages reçus
        self.messages_area = QTextEdit()
        self.messages_area.setReadOnly(True)
        left_layout.addWidget(QLabel("Messages:"))
        left_layout.addWidget(self.messages_area)

        # Partie droite (image reçue)
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Image reçue:"))

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(250, 250)
        self.image_label.setStyleSheet("border: 1px solid gray;")

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        right_layout.addWidget(scroll_area)

        # Section audio
        right_layout.addWidget(QLabel("Audio reçu:"))
        self.audio_label = QLabel("Aucun audio")
        self.audio_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.audio_label)

        self.play_btn = QPushButton("Play Audio")
        self.play_btn.clicked.connect(self.play_audio)
        self.play_btn.setEnabled(False)
        right_layout.addWidget(self.play_btn)

        # Section vidéo
        right_layout.addWidget(QLabel("Vidéo reçue:"))
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(250, 150)
        self.video_player.setVideoOutput(self.video_widget)
        right_layout.addWidget(self.video_widget)

        self.video_label = QLabel("Aucune vidéo")
        self.video_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.video_label)

        self.play_video_btn = QPushButton("Play Vidéo")
        self.play_video_btn.clicked.connect(self.play_video)
        self.play_video_btn.setEnabled(False)
        right_layout.addWidget(self.play_video_btn)

        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)

        # Layout pour les contrôles (sous le layout principal)
        layout = QVBoxLayout()
        layout.addLayout(main_layout)

        # Sélection du destinataire
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(QLabel("Destinataire:"))
        self.dest_combo = QComboBox()
        self.dest_combo.addItems(['SERVER'])
        dest_layout.addWidget(self.dest_combo)
        layout.addLayout(dest_layout)

        # Champ de message et bouton envoyer
        msg_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Tapez votre message...")
        self.message_input.returnPressed.connect(self.send_message)
        msg_layout.addWidget(self.message_input)

        send_btn = QPushButton("Envoyer")
        send_btn.clicked.connect(self.send_message)
        msg_layout.addWidget(send_btn)
        layout.addLayout(msg_layout)

        # Boutons pour envoyer image et audio
        media_layout = QHBoxLayout()

        img_btn = QPushButton("Envoyer Image")
        img_btn.clicked.connect(self.send_image)
        media_layout.addWidget(img_btn)

        audio_btn = QPushButton("Envoyer Audio")
        audio_btn.clicked.connect(self.send_audio)
        media_layout.addWidget(audio_btn)

        video_btn = QPushButton("Envoyer Vidéo")
        video_btn.clicked.connect(self.send_video)
        media_layout.addWidget(video_btn)

        layout.addLayout(media_layout)

        self.setLayout(layout)

    def send_message(self):
        message = self.message_input.text().strip()
        dest = self.dest_combo.currentText().strip()

        if message and dest:
            self.client.send(message, dest)
            self.messages_area.append(f"[Moi -> {dest}] {message}")
            self.message_input.clear()

    def emit_message_signal(self, message):
        self.signal_emitter.message_received.emit(message)

    def emit_users_list_signal(self, users_list):
        self.signal_emitter.users_list_received.emit(users_list)

    def on_users_list_received(self, users_list):
        # Sauvegarder la sélection actuelle
        current_selection = self.dest_combo.currentText()

        # Vider et reconstruire la liste
        self.dest_combo.clear()
        self.dest_combo.addItem("SERVER")
        self.dest_combo.addItem("ALL")

        for user in users_list:
            if user != self.client.username:  # Ne pas s'ajouter soi-même
                self.dest_combo.addItem(user)

        # Restaurer la sélection si elle existe encore
        index = self.dest_combo.findText(current_selection)
        if index >= 0:
            self.dest_combo.setCurrentIndex(index)

    def on_message_received(self, message):
        # Vérifier si c'est une image
        if message.message_type == MessageType.RECEPTION.IMAGE:
            self.messages_area.append(f"[{message.emitter}] [IMAGE reçue]")
            self.display_image(message.value)
        # Vérifier si c'est un audio
        elif message.message_type == MessageType.RECEPTION.AUDIO:
            self.messages_area.append(f"[{message.emitter}] [AUDIO reçu]")
            self.store_audio(message.value, message.emitter)
        # Vérifier si c'est une vidéo
        elif message.message_type == MessageType.RECEPTION.VIDEO:
            self.messages_area.append(f"[{message.emitter}] [VIDEO reçue]")
            self.store_video(message.value, message.emitter)
        else:
            # Afficher le message dans la zone de texte
            self.messages_area.append(f"[{message.emitter}] {message.value}")

        # Ajouter l'émetteur à la ComboBox s'il n'y est pas
        if message.emitter and message.emitter != "SERVER":
            if self.dest_combo.findText(message.emitter) == -1:
                self.dest_combo.addItem(message.emitter)

    def display_image(self, value):
        # Extraire le base64 de la valeur (format: IMG:base64data)
        if value.startswith("IMG:"):
            img_base64 = value[4:]
        else:
            img_base64 = value

        # Décoder et afficher l'image
        img_data = base64.b64decode(img_base64)
        pixmap = QPixmap()
        pixmap.loadFromData(img_data)

        # Redimensionner si nécessaire
        scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)

    def store_audio(self, value, emitter):
        # Extraire le base64 de la valeur (format: AUDIO:base64data)
        if value.startswith("AUDIO:"):
            audio_base64 = value[6:]
        else:
            audio_base64 = value

        # Décoder l'audio
        self.audio_data = base64.b64decode(audio_base64)
        self.audio_label.setText(f"Audio de {emitter}")
        self.play_btn.setEnabled(True)

    def play_audio(self):
        if not self.audio_data:
            return

        # Créer un fichier temporaire pour l'audio
        if self.temp_audio_file:
            try:
                os.remove(self.temp_audio_file)
            except:
                pass

        # Sauvegarder dans un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            f.write(self.audio_data)
            self.temp_audio_file = f.name

        # Jouer l'audio
        url = QUrl.fromLocalFile(self.temp_audio_file)
        self.media_player.setMedia(QMediaContent(url))
        self.media_player.play()

    def store_video(self, value, emitter):
        # Extraire le base64 de la valeur (format: VIDEO:base64data)
        if value.startswith("VIDEO:"):
            video_base64 = value[6:]
        else:
            video_base64 = value

        # Décoder la vidéo
        self.video_data = base64.b64decode(video_base64)
        self.video_label.setText(f"Vidéo de {emitter}")
        self.play_video_btn.setEnabled(True)

    def play_video(self):
        if not self.video_data:
            return

        # Créer un fichier temporaire pour la vidéo
        if self.temp_video_file:
            try:
                os.remove(self.temp_video_file)
            except:
                pass

        # Sauvegarder dans un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            f.write(self.video_data)
            self.temp_video_file = f.name

        # Jouer la vidéo
        url = QUrl.fromLocalFile(self.temp_video_file)
        self.video_player.setMedia(QMediaContent(url))
        self.video_player.play()

    def send_video(self):
        dest = self.dest_combo.currentText().strip()
        if not dest:
            return

        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une vidéo",
            "",
            "Vidéos (*.mp4 *.avi *.mkv *.mov *.wmv)"
        )

        if filepath:
            self.client.send_video(filepath, dest)
            self.messages_area.append(f"[Moi -> {dest}] [VIDEO envoyée: {filepath}]")

    def add_user(self):
        user = self.user_input.text().strip()
        if user and self.dest_combo.findText(user) == -1:
            self.dest_combo.addItem(user)
            self.user_input.clear()

    def send_image(self):
        dest = self.dest_combo.currentText().strip()
        if not dest:
            return

        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp)"
        )

        if filepath:
            self.client.send_image(filepath, dest)
            self.messages_area.append(f"[Moi -> {dest}] [IMAGE envoyée: {filepath}]")

    def send_audio(self):
        dest = self.dest_combo.currentText().strip()
        if not dest:
            return

        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un audio",
            "",
            "Audio (*.mp3 *.wav *.ogg *.m4a *.flac)"
        )

        if filepath:
            self.client.send_audio(filepath, dest)
            self.messages_area.append(f"[Moi -> {dest}] [AUDIO envoyé: {filepath}]")


if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet(load_stylesheet())
    home = UiHome(None)
    home.show()
    sys.exit(app.exec_())
