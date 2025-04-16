from langgraph.graph import StateGraph

from agents.base_workflow import BaseWorkflow
from agents.main_state import MainState


class MainWorkflow(BaseWorkflow):
    def __init__(self, state: StateGraph):
        super().__init__()
        self.state = state

    def build(self):
        builder = StateGraph(self.state)
        # builder.add_node("node_name", Node())
        builder.add_edge("__start__", "__end__")
        workflow = builder.compile()
        workflow.name = self.name
        return workflow

# class AnotherWorkflow(BaseWorkflow):
#     def __init__(self):
#         super().__init__()

#     def build(self, state: StateGraph):
#         builder = StateGraph(state)
#         # builder.add_node("node_name", Node())
#         builder.add_edge("__start__", "__end__")
#         workflow = builder.compile()
#         workflow.name = self.name
#         return workflow

# another_workflow = AnotherWorkflow(AnotherState)

main_workflow = MainWorkflow(MainState)
