from abc import ABC, abstractmethod

from langgraph.graph.state import CompiledStateGraph


class BaseWorkflow(ABC):
    def __init__(self):
        self.name = self.__class__.__name__

    @abstractmethod
    def build(self) -> CompiledStateGraph:
        pass

    def __call__(self):
        return self.build()
