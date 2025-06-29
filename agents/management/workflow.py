from langgraph.graph import StateGraph

from agents.base_workflow import BaseWorkflow
from agents.management.modules.conditions import route_request
from agents.management.modules.nodes import (
    ContentRisksAnalysisNode,
    InstagramContentVerificationNode,
    InstagramPoliciesSearchNode,
    ResourceManagementNode,
)
from agents.management.modules.state import ManagementState


class ManagementWorkflow(BaseWorkflow):
    """
    콘텐츠 관리를 위한 Workflow 클래스

    이 클래스는 프로젝트, 팀, 리소스의 관리와 크리에이터 직업 성장을 위한 Workflow를 정의합니다.
    BaseWorkflow를 상속받아 기본 구조를 구현하고, ManagementState를 사용하여 상태를 관리합니다.
    MCP 서버를 통한 인스타그램 컨텐츠 검증, 정책 검색, 위험 요소 분석 기능을 포함합니다.
    """

    def __init__(self, state):
        super().__init__()
        self.state = state

    def build(self):
        """
        관리 Workflow 그래프 구축 메서드

        StateGraph를 사용하여 콘텐츠 관리를 위한 Workflow 그래프를 구축합니다.
        리소스 관리, 인스타그램 컨텐츠 검증, 정책 검색, 위험 요소 분석 노드를 포함하며,
        조건부 라우팅을 통해 요청 유형에 따라 적절한 노드로 분기합니다.

        Returns:
            CompiledStateGraph: 컴파일된 상태 그래프 객체
        """
        builder = StateGraph(self.state)

        # 노드들 추가
        builder.add_node("resource_management", ResourceManagementNode())
        builder.add_node(
            "instagram_content_verification", InstagramContentVerificationNode()
        )
        builder.add_node("instagram_policies_search", InstagramPoliciesSearchNode())
        builder.add_node("content_risks_analysis", ContentRisksAnalysisNode())

        # 시작 노드에서 라우터로 연결
        builder.add_edge("__start__", "router")

        # 조건부 에지를 통한 라우팅
        builder.add_conditional_edges(
            "router",
            route_request,
            {
                "resource_management": "resource_management",
                "instagram_content_verification": "instagram_content_verification",
                "instagram_policies_search": "instagram_policies_search",
                "content_risks_analysis": "content_risks_analysis",
            },
        )

        # 각 노드에서 종료 노드로 연결
        builder.add_edge("resource_management", "__end__")
        builder.add_edge("instagram_content_verification", "__end__")
        builder.add_edge("instagram_policies_search", "__end__")
        builder.add_edge("content_risks_analysis", "__end__")

        workflow = builder.compile()  # 그래프 컴파일
        workflow.name = self.name  # Workflow 이름 설정

        return workflow


# 관리 Workflow 인스턴스 생성
management_workflow = ManagementWorkflow(ManagementState)
