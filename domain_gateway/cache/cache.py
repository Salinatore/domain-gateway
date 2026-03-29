from abc import ABC


class IngressMessageCache(ABC):
    def __init__(self):
        pass

    def latest_value(self, key: str) -> str | None:
        raise NotImplementedError

    def set(self, key: str, value: str) -> None:
        raise NotImplementedError
