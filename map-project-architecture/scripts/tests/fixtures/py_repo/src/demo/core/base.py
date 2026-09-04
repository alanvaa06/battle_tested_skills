from abc import ABC, abstractmethod


class Repo(ABC):
    @abstractmethod
    def get(self, key: str) -> str: ...
