from abc import ABC, abstractmethod

from langgraph.graph import StateGraph


class BaseWorkflow(ABC):
    def __init__(self):
        self.name = self.__class__.__name__

    @abstractmethod
    def build_workflow(self) -> dict:
        pass

    def __call__(self):
        return self.build_workflow()
