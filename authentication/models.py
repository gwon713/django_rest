from enum import Enum


class NoValue(Enum):
    def __repr__(self):
        return "<%s.%s>" % (self.__class__.__name__, self.name)


class VerificationType(NoValue):
    SIGN_UP = "sign_up"
    RESET_PASSWORD = "reset_password"
