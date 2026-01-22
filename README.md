# Guide de Lancement

Ce guide explique comment lancer les différents composants de l'application WebSocket.

## Prérequis

### Dépendances Python

```bash
# Installation des dépendances pour le serveur et client
pip install websocket-server websocket-client PyQt5

# Installation des dépendances pour le dashboard admin
pip install flask
```

---

## 1. Lancer le Serveur WebSocket

Le serveur gère les connexions et le routage des messages entre clients.

```bash
cd ws
python WSServer.py
```

**Configuration :**
- Mode dev : `127.0.0.1:9000`
- Mode prod : `192.168.4.230:9000`

Par défaut, le serveur se lance en mode **dev**.

**Commandes disponibles dans le terminal serveur :**
- `dest:message` - Envoyer un message à un client (ex: `Client:bonjour`)
- `ALL:message` - Broadcast à tous les clients
- `img:dest:chemin` - Envoyer une image
- `audio:dest:chemin` - Envoyer un audio
- `video:dest:chemin` - Envoyer une vidéo
- `list` - Afficher les clients connectés
- `disconnect` - Arrêter le serveur

---

## 2. Lancer le Client (Interface PyQt5)

L'interface graphique permet de se connecter au serveur et d'échanger des messages.

```bash
cd ws
python ui/UiContext.py
```

**Utilisation :**
1. Renseignez un **nom** (par défaut : "Client")
2. Choisissez l'environnement (**dev** ou **prod**)
   - Ou spécifiez manuellement **Host** et **Port**
3. Cliquez sur **Connect**

---

## 3. Lancer le Dashboard Admin

Le dashboard web permet de monitorer les clients connectés et les messages routés en temps réel.

```bash
cd ws/web
pip install -r requirements.txt
python app.py
```

**Accès :** http://127.0.0.1:5001

**Fonctionnalités :**
- Liste des clients connectés en temps réel
- Logs de routage des messages
- Notifications de connexion/déconnexion
---

## Ordre de Lancement Recommandé

1. **Serveur** (`python WSServer.py`)
2. **Dashboard Admin** (`python web/app.py`) - optionnel
3. **Client(s)** (`python ui/UiContext.py`)

---

## Structure des Fichiers

```
ws/
├── WSServer.py          # Serveur WebSocket
├── WSClient.py          # Client WebSocket
├── Context.py           # Configuration (host/port)
├── Message.py           # Types de messages
├── ui/
│   ├── UiContext.py     # Interface de connexion (PyQt5)
│   ├── UiHome.py        # Interface de chat
│   └── MacOs.qss        # Styles Qt
└── web/
    ├── app.py           # Dashboard Admin (Flask)
    ├── requirements.txt # Dépendances Flask
    └── templates/       # Templates HTML
```
