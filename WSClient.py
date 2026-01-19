import websocket
import threading

from Context import Context
from Message import Message, MessageType


class WSClient:
    def __init__(self, ctx, username="Client"):
        self.username = username
        self.connected = False
        self.ws = websocket.WebSocketApp(
            ctx.url(),
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

    def on_message(self, ws, message):
        received_msg = Message.from_json(message)
        print(f"\n[{received_msg.emitter}] {received_msg.value}")
        print(f"[{self.username}] > ", end="", flush=True)

    def on_error(self, ws, error):
        print(f"\n[error] {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print(f"\n[close] code={close_status_code} msg={close_msg}")
        self.connected = False

    def on_open(self, ws):
        print("[open] connecté")
        self.connected = True
        message = Message(MessageType.DECLARATION, emitter=self.username, receiver="", value="")
        ws.send(message.to_json())

        input_thread = threading.Thread(target=self.input_loop, daemon=True)
        input_thread.start()

    def input_loop(self):
        print(f"Chat démarré. Tapez 'dest:message' pour envoyer (ex: SERVER:bonjour)")
        print(f"Tapez 'quit' pour quitter.\n")
        while self.connected:
            try:
                print(f"[{self.username}] > ", end="", flush=True)
                user_input = input()
                if user_input.lower() == "quit":
                    self.ws.close()
                    break
                if ":" in user_input:
                    dest, content = user_input.split(":", 1)
                    self.send(content.strip(), dest.strip())
                else:
                    self.send(user_input, "SERVER")
            except EOFError:
                break

    def connect(self):
        self.ws.run_forever()

    def send(self, value, dest):
        message = Message(MessageType.ENVOI, emitter=self.username, receiver=dest, value=value)
        self.ws.send(message.to_json())

    @staticmethod
    def dev(username="Client"):
        return WSClient(Context.dev(), username)

    @staticmethod
    def prod(username="Client"):
        return WSClient(Context.prod(), username)

if __name__ == "__main__":
    import sys
    username = sys.argv[1] if len(sys.argv) > 1 else "Client"
    client = WSClient.dev(username)
    client.connect()