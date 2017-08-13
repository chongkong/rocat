import enum


class MsgType(enum.Enum):
    NORMAL = 1
    TERMINAL = 2


class Envelope(object):
    __slots__ = ['msg', 'type', 'sender']

    def __init__(self, msg, *, type=MsgType.NORMAL, sender):
        self.msg = msg
        self.type = type
        self.sender = sender
