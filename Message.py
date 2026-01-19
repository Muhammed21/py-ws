import json


class MessageType:
    DECLARATION = "declaration"
    ENVOI = "envoi"
    RECEPTION = "reception"

class Message:
    def __init__(self, message_type: MessageType, value, emitter, receiver=None):
        self.message_type = message_type
        self.value = value
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
        value = data['data']['value']
        return Message(message_type, value, emitter, receiver)

    def to_json(self):
        data = {
            'message_type': self.message_type,
            'data': {
                'emitter': self.emitter,
                'receiver': self.receiver,
                'value': self.value
            }
        }
        return json.dumps(data)

message = Message(MessageType.DECLARATION, emitter="System", receiver="All", value="This is a test message")
messageRebuild = Message.from_json(message.to_json())