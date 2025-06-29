"""
이미지 관련 콘텐츠 생성을 위한 Workflow 모듈

이 모듈은 이미지 기반 콘텐츠 생성을 위한 Workflow를 정의합니다.
StateGraph를 사용하여 이미지 처리를 위한 워크플로우를 구축합니다.
"""

from langgraph.graph import StateGraph, START, END

from agents.base_workflow import BaseWorkflow
from agents.image.modules.state import ImageState
from agents.image.modules.nodes import NewFaceGenerationNode, FixedFaceGenerationNode

class ImageWorkflow(BaseWorkflow):
    def __init__(self, state):
        super().__init__()
        self.state = state

    def build(self):
        builder = StateGraph(self.state)

        # 비동기 노드는 async wrapper로 감싸기
        async def fixed_face_generation(state: dict) -> dict:
            node = FixedFaceGenerationNode()
            return await node.execute(state)

        # 동기 노드는 그냥 호출해서 넘기면 됨
        node_new_face = NewFaceGenerationNode()
        def new_face_generation(state: dict) -> dict:
            return node_new_face.execute(state)

        # 노드 등록
        builder.add_node("fixed_face_generation", fixed_face_generation)
        builder.add_node("new_face_generation", new_face_generation)

        # 분기 조건 등록
        builder.add_conditional_edges(
            START,
            self.check_fixed,
            {
                "fixed_face_generation": "fixed_face_generation",
                "new_face_generation": "new_face_generation"
            },
            then=END,
        )

        workflow = builder.compile()
        workflow.name = self.name
        return workflow

    def check_fixed(self, state):
        return "fixed_face_generation" if state.get('fixed', False) else "new_face_generation"


# 이미지 Workflow 인스턴스 생성
image_workflow = ImageWorkflow(ImageState)
