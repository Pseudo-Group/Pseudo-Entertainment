from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from agents.base_workflow import BaseWorkflow
from agents.management.modules.nodes import (
    InstagramMediaFetchNode,
    InstagramCommentsFetchNode,
    NoChangeNode,
    InstagramCommentsAnalysisNode
)
from agents.management.modules.state import ManagementState


class ManagementWorkflow(BaseWorkflow):
    """
    인스타그램 API 모니터링을 위한 Workflow 클래스

    이 클래스는 인스타그램 포스트의 댓글 수 변화를 모니터링하는 Workflow를 정의합니다.
    BaseWorkflow를 상속받아 기본 구조를 구현하고, ManagementState를 사용하여 상태를 관리합니다.
    """

    def __init__(self, state):
        super().__init__()
        self.state = state

    def build(self):
        """
        인스타그램 모니터링 Workflow 그래프 구축 메서드

        StateGraph를 사용하여 인스타그램 API 모니터링을 위한 Workflow 그래프를 구축합니다.
        조건부 에지를 사용하여 댓글 수 변경 여부에 따라 다른 경로를 실행합니다.

        Returns:
            CompiledStateGraph: 컴파일된 상태 그래프 객체
        """
        builder = StateGraph(self.state)
        
        # 노드 추가
        builder.add_node("media_fetch", InstagramMediaFetchNode())
        builder.add_node("comments_fetch", InstagramCommentsFetchNode())
        builder.add_node("analysis", InstagramCommentsAnalysisNode())
        builder.add_node("no_change", NoChangeNode())
        
        # 시작 노드에서 미디어 가져오기 노드로 연결
        builder.add_edge("__start__", "media_fetch")
        
        # 조건부 에지: 댓글 수 변경 여부에 따라 분기
        builder.add_conditional_edges(
            "media_fetch",
            self._should_fetch_comments,
            {
                "fetch_comments": "comments_fetch",
                "no_change": "no_change",
                "api_error": "__end__"  # API 오류 시 종료
            }
        )
        
        # 댓글 가져오기 노드에서 분석 노드로, 분석 노드에서 종료
        builder.add_edge("comments_fetch", "analysis")
        builder.add_edge("analysis", "__end__")

        workflow = builder.compile()  # 그래프 컴파일
        workflow.name = self.name  # Workflow 이름 설정

        return workflow
    
    def _should_fetch_comments(self, state: ManagementState) -> str:
        """
        댓글을 가져올지 결정하는 라우터 함수
        
        Args:
            state: 현재 상태
            
        Returns:
            str: 다음 노드 이름 ("fetch_comments", "no_change", 또는 "api_error")
        """
        print(f"🔄 [Router] 다음 노드 결정 중...")
        
        # API 오류 체크
        if "API 요청에 실패했습니다" in str(state.get("response", [])):
            print(f"🔄 [Router] API 오류 감지 → api_error 경로 선택")
            return "api_error"
        
        has_changes = state.get("has_changes", False)
        
        if has_changes:
            print(f"🔄 [Router] 댓글 수 변경 감지 → fetch_comments 경로 선택")
            return "fetch_comments"
        else:
            print(f"🔄 [Router] 댓글 수 변경 없음 → no_change 경로 선택")
            return "no_change"


# 관리 Workflow 인스턴스 생성
management_workflow = ManagementWorkflow(ManagementState)
