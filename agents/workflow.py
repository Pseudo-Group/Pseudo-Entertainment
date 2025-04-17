from langgraph.graph import StateGraph

from agents.base_workflow import BaseWorkflow
from agents.main_state import MainState


class MainWorkflow(BaseWorkflow):
    """
    메인 Workflow 클래스

    Team Member는 해당 Workflow에서 따로 작업을 진행하지 않으셔도 됩니다.
    이 클래스는 모든 Agentic Workflow를 바탕으로 주요 Workflow를 정의합니다.
    """

    def __init__(self, state):
        """
        Args:
            state (StateGraph): Workflow에서 사용할 상태 클래스
        """
        super().__init__()
        self.state = state

    def build(self):
        """
        Workflow 그래프 구축 메서드

        StateGraph를 사용하여 Workflow 그래프를 구축합니다.
        추후 다양한 노드를 추가하여 최종 Workflow를 구축할 예정입니다.

        Returns:
            CompiledStateGraph: 컴파일된 상태 그래프 객체
        """
        builder = StateGraph(self.state)
        # 노드 추가 예시: builder.add_node("node_name", Node())
        builder.add_edge("__start__", "__end__")  # 시작에서 종료로 바로 연결
        workflow = builder.compile()  # 그래프 컴파일
        workflow.name = self.name  # Workflow 이름 설정
        return workflow


# 다른 Workflow 구현 예시
# class AnotherWorkflow(BaseWorkflow):
#     """
#     다른 Workflow 클래스 예시
#     """
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

# 메인 Workflow 인스턴스 생성
main_workflow = MainWorkflow(MainState)
