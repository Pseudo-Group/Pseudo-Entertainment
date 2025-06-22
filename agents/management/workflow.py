from langgraph.graph import StateGraph

from agents.base_workflow import BaseWorkflow
from agents.management.modules.nodes import (
    ResourceManagementNode,
    IUResearchPlanNode,
    IUResearchSearchNode,
    IUResearchSummaryNode
)
from agents.management.modules.state import ManagementState


def route_request_type(state: ManagementState):
    """
    요청 유형에 따라 다음 노드를 결정하는 라우터 함수
    
    Args:
        state: 현재 상태
        
    Returns:
        str: 다음에 실행할 노드의 이름
    """
    request_type = state.get("request_type", "")
    
    if request_type == "iu_research":
        return "iu_research_plan"
    else:
        return "resource_management"


class ManagementWorkflow(BaseWorkflow):
    """
    콘텐츠 관리를 위한 Workflow 클래스

    이 클래스는 프로젝트, 팀, 리소스의 관리와 크리에이터 직업 성장, 
    그리고 IU 리서치를 위한 Workflow를 정의합니다.
    BaseWorkflow를 상속받아 기본 구조를 구현하고, ManagementState를 사용하여 상태를 관리합니다.
    """

    def __init__(self, state):
        super().__init__()
        self.state = state

    def build(self):
        """
        관리 Workflow 그래프 구축 메서드

        StateGraph를 사용하여 콘텐츠 관리를 위한 Workflow 그래프를 구축합니다.
        요청 유형에 따라 다른 경로로 분기됩니다:
        - resource_allocation, team_management 등: 기존 리소스 관리
        - iu_research: IU 관련 조사 워크플로우

        Returns:
            CompiledStateGraph: 컴파일된 상태 그래프 객체
        """
        builder = StateGraph(self.state)
        
        # 노드 추가
        builder.add_node("resource_management", ResourceManagementNode())
        builder.add_node("iu_research_plan", IUResearchPlanNode())
        builder.add_node("iu_research_search", IUResearchSearchNode())
        builder.add_node("iu_research_summary", IUResearchSummaryNode())
        
        # 조건부 에지 추가: 시작점에서 요청 유형에 따라 분기
        builder.add_conditional_edges(
            "__start__",
            route_request_type,
            {
                "resource_management": "resource_management",
                "iu_research_plan": "iu_research_plan"
            }
        )
        
        # 기존 리소스 관리 경로
        builder.add_edge("resource_management", "__end__")
        
        # IU 리서치 경로
        builder.add_edge("iu_research_plan", "iu_research_search")
        builder.add_edge("iu_research_search", "iu_research_summary")
        builder.add_edge("iu_research_summary", "__end__")

        workflow = builder.compile()
        workflow.name = self.name

        return workflow


# 관리 Workflow 인스턴스 생성
management_workflow = ManagementWorkflow(ManagementState)