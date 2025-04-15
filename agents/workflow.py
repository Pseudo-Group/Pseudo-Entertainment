from langgraph.graph import StateGraph

from agents.base_workflow import BaseWorkflow
from agents.main_state import MainState


class MainWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()

    def build_workflow(self):
        builder = StateGraph(MainState)
        # builder.add_node("node_name", Node())
        builder.add_edge("__start__", "__end__")
        workflow = builder.compile()
        workflow.name = self.name
        return workflow


main_workflow = MainWorkflow()
