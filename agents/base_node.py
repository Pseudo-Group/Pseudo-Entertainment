from abc import ABC, abstractmethod

from agents.main_state import GraphState


class BaseNode(ABC):
    """
    모든 RAG 파이프라인 기본 클래스
    """

    def __init__(self, verbose: bool = False, **kwargs):
        self.name = self.__class__.__name__
        self.verbose = verbose

    @abstractmethod
    def process(self, state: GraphState) -> GraphState:
        pass

    def log(self, message: str, **kwargs):
        if self.verbose:
            print(f"{type}: {self.name}: {message}")
            for key, value in kwargs.items():
                print(f"{key}: {value}")

    def __call__(self, state: GraphState) -> GraphState:
        print(f"Calling {self.name}")
        result = self.process(state)
        if self.verbose:
            print(f"state after {self.name}: {state}")
        return result
