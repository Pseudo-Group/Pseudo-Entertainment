from abc import ABC, abstractmethod


class BaseNode(ABC):
    def __init__(self, **kwargs):
        self.name = self.__class__.__name__
        self.verbose = kwargs.get("verbose", False)

    @abstractmethod
    def execute(self, state) -> dict:
        pass

    def logging(self, method_name, **kwargs):
        if self.verbose:
            print(f"[{self.name}] {method_name}")
            for key, value in kwargs.items():
                print(f"{key}: {value}")

    def __call__(self, state):
        return self.execute(state)
