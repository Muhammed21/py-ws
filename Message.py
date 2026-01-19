import json


class MessageType:
    DECLARATION = "declaration"
    ENVOI = "envoi"
    RECEPTION = "reception"

class Message:
    def __init__(self, message_type: MessageType, content, emitter, receiver=None):
        self.message_type = message_type
        self.content = content
        self.emitter = emitter
        self.receiver = receiver

    @staticmethod
    def default_message():
        return Message(MessageType.DECLARATION, "System", "This is a default message", "All")

    @staticmethod
    def from_json(json_data):
        data = json.loads(json_data)
        message_type = data['message_type']
        emitter = data['data']['emitter']
        receiver = data['data'].get('receiver', None)
        content = data['data']['content']
        return Message(message_type, content, emitter, receiver)

    def to_json(self):
        data = {
            'message_type': self.message_type,
            'data': {
                'emitter': self.emitter,
                'receiver': self.receiver,
                'content': self.content
            }
        }
        return json.dumps(data)

message = Message(MessageType.DECLARATION, emitter="System", receiver="All", content="This is a test message")
messageRebuild = Message.from_json(message.to_json())