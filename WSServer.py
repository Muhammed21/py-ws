from websocket_server import WebsocketServer
import threading

from Context import Context
from Message import Message, MessageType


class WSServer:
    def __init__(self, ctx):
        self.host = ctx.host
        self.port = ctx.port
        self.server = WebsocketServer(host=self.host, port=self.port, loglevel=1)
        self.server.set_fn_new_client(self.on_new_client)
        self.server.set_fn_client_left(self.on_client_left)
        self.server.set_fn_message_received(self.on_message_received)

        self.clients = {}
        self.running = False

    def on_new_client(self, client, server):
        print(f"\n[+] Client connecté: id={client['id']} addr={client['address']}")
        server.send_message(client, "Bienvenue !")
        print("[SERVER] > ", end="", flush=True)

    def on_client_left(self, client, server):
        print(f"\n[-] Client déconnecté: id={client['id']}")
        for name, c in list(self.clients.items()):
            if c['id'] == client['id']:
                del self.clients[name]
                break
        print("[SERVER] > ", end="", flush=True)

    def on_message_received(self, client, server, message):
        print(f"\n[message reçu] {message}")
        received_msg = Message.from_json(message)
        if received_msg.message_type == MessageType.DECLARATION:
            server.send_message(client, f"Déclaration reçue de {received_msg.emitter}")
            self.clients[received_msg.emitter] = client
            print(f"[info] Client '{received_msg.emitter}' enregistré")
        elif received_msg.message_type == MessageType.ENVOI:
            if received_msg.receiver == "SERVER":
                print(f"[{received_msg.emitter}] {received_msg.content}")
            else:
                receiver_client = self.clients.get(received_msg.receiver, None)
                if receiver_client:
                    server.send_message(receiver_client, f"Message de {received_msg.emitter}: {received_msg.content}")
                else:
                    server.send_message(client, f"Erreur: destinataire {received_msg.receiver} non trouvé.")
        print("[SERVER] > ", end="", flush=True)

    def input_loop(self):
        print("\nChat serveur démarré. Tapez 'dest:message' pour envoyer (ex: Client:bonjour)")
        print("Tapez 'list' pour voir les clients connectés, 'quit' pour quitter.\n")
        while self.running:
            try:
                print("[SERVER] > ", end="", flush=True)
                user_input = input()
                if user_input.lower() == "quit":
                    self.running = False
                    self.server.shutdown_gracefully()
                    break
                elif user_input.lower() == "list":
                    print(f"Clients connectés: {list(self.clients.keys())}")
                elif ":" in user_input:
                    dest, content = user_input.split(":", 1)
                    dest = dest.strip()
                    content = content.strip()
                    if dest.lower() == "all":
                        for name, client in self.clients.items():
                            self.server.send_message(client, f"[SERVER] {content}")
                        print(f"[envoyé à tous] {content}")
                    else:
                        receiver_client = self.clients.get(dest, None)
                        if receiver_client:
                            self.server.send_message(receiver_client, f"[SERVER] {content}")
                            print(f"[envoyé à {dest}] {content}")
                        else:
                            print(f"[erreur] Client '{dest}' non trouvé")
                else:
                    print("Format: 'dest:message' ou 'all:message' pour broadcast")
            except EOFError:
                break

    def start(self):
        print(f"Serveur WS sur ws://{self.host}:{self.port}")
        self.running = True

        input_thread = threading.Thread(target=self.input_loop, daemon=True)
        input_thread.start()

        self.server.run_forever()

    @staticmethod
    def dev():
        return WSServer(Context.dev())

    @staticmethod
    def prod():
        return WSServer(Context.prod())

if __name__ == "__main__":
    ws_server = WSServer.prod()
    ws_server.start()