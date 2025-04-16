"""
이미지 관련 콘텐츠 생성을 위한 Workflow 모듈

이 모듈은 이미지 기반 콘텐츠 생성을 위한 Workflow를 정의합니다.
StateGraph를 사용하여 이미지 처리를 위한 워크플로우를 구축합니다.
"""

from langgraph.graph import StateGraph

from agents.base_workflow import BaseWorkflow
from agents.image.modules.state import ImageState


class ImageWorkflow(BaseWorkflow):
    """
    이미지 관련 콘텐츠 생성을 위한 Workflow 클래스
    
    이 클래스는 이미지 기반 콘텐츠 생성을 위한 Workflow를 정의합니다.
    BaseWorkflow를 상속받아 기본 구조를 구현하고, ImageState를 사용하여 상태를 관리합니다.
    """
    def __init__(self, state: StateGraph):
        super().__init__()
        self.state = state

    def build(self):
        """
        이미지 Workflow 그래프 구축 메서드
        
        StateGraph를 사용하여 이미지 처리를 위한 Workflow 그래프를 구축합니다.
        현재는 간단한 구조로 시작 노드에서 종료 노드로 직접 연결되어 있으며,
        추후 이미지 생성 노드 등을 추가하여 확장할 수 있습니다.
        
        Returns:
            CompiledStateGraph: 컴파일된 상태 그래프 객체
        """
        builder = StateGraph(self.state)
        
        # 기본 구조: 시작 노드에서 종료 노드로 직접 연결
        builder.add_edge("__start__", "__end__")
        
        # 향후 이미지 생성 노드 추가 예시
        # builder.add_node("image_generation", ImageGenerationNode())
        # builder.add_edge("__start__", "image_generation")
        # builder.add_edge("image_generation", "__end__")
        
        workflow = builder.compile()  # 그래프 컴파일
        workflow.name = self.name  # Workflow 이름 설정

        return workflow


# 이미지 Workflow 인스턴스 생성
image_workflow = ImageWorkflow(ImageState)
