import enum


class MsgType(enum.Enum):
    TELL = 1
    ASK = 2
    RPC = 3
    ERROR = 4
    INTERNAL = 5
    INTERNAL_ERROR = 6
    TERMINAL = 7


class Envelope(object):
    __slots__ = ['msg', 'type', 'sender']

    def __init__(self, msg, *, type, sender):
        self.msg = msg
        self.type = type
        self.sender = sender

    @classmethod
    def for_tell(cls, msg, *, sender):
        return Envelope(msg, type=MsgType.TELL, sender=sender)

    @classmethod
    def for_ask(cls, msg, *, sender):
        return Envelope(msg, type=MsgType.ASK, sender=sender)

    @classmethod
    def for_rpc(cls, msg, *, sender):
        return Envelope(msg, type=MsgType.RPC, sender=sender)

    @classmethod
    def for_error(cls, err):
        return Envelope(err, type=MsgType.ERROR, sender=None)

    @classmethod
    def for_internal(cls, msg, *, sender):
        return Envelope(msg, type=MsgType.INTERNAL, sender=sender)

    @classmethod
    def for_internal_error(cls, err):
        return Envelope(err, type=MsgType.INTERNAL_ERROR, sender=None)

    @classmethod
    def for_terminal(cls, msg, *, sender):
        return Envelope(msg, type=MsgType.TERMINAL, sender=sender)

    @property
    def need_reply(self):
        return self.type == MsgType.ASK

    @property
    def is_error(self):
        return self.type == MsgType.ERROR or self.type == MsgType.INTERNAL_ERROR
