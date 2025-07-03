from langgraph.graph import StateGraph, END

from agents.base_workflow import BaseWorkflow
from agents.management.modules import nodes
from agents.management.modules.state import ManagementState
from agents.management.modules.state import CommentWorkflowState


class ManagementWorkflow(BaseWorkflow):
    """
    콘텐츠 관리를 위한 Workflow 클래스

    이 클래스는 프로젝트, 팀, 리소스의 관리와 크리에이터 직업 성장을 위한 Workflow를 정의합니다.
    BaseWorkflow를 상속받아 기본 구조를 구현하고, ManagementState를 사용하여 상태를 관리합니다.
    """

    def __init__(self, state):
        super().__init__()
        self.state = state
         

    def build(self):
        """
        관리 Workflow 그래프 구축 메서드

        StateGraph를 사용하여 콘텐츠 관리를 위한 Workflow 그래프를 구축합니다.
        현재는 리소스 관리 노드를 포함하고 있으며, 추후 조건부 에지를 추가하여
        다양한 경로를 가진 Workflow를 구축할 수 있습니다.

        Returns:
            CompiledStateGraph: 컴파일된 상태 그래프 객체
        """
        builder = StateGraph(self.state)
        # 리소스 관리 노드 추가
        builder.add_node("resource_management", nodes.ResourceManagementNode())
        # 시작 노드에서 리소스 관리 노드로 연결
        builder.add_edge("__start__", "resource_management")
        # 리소스 관리 노드에서 종료 노드로 연결
        builder.add_edge("resource_management", "__end__")

        # 조건부 에지 추가 예시
        # builder.add_conditional_edges(
        #     "resource_planning",
        #     # resource_planning 실행이 완료된 후, 다음 노드(들)는
        #     # router의 출력을 기반으로 예약됩니다
        #     router,
        # )

        workflow = builder.compile()  # 그래프 컴파일
        workflow.name = self.name  # Workflow 이름 설정

        return workflow


# 관리 Workflow 인스턴스 생성
management_workflow = ManagementWorkflow(ManagementState)



class CommentsWorkflow(BaseWorkflow):
    """
    인스타그램 댓글 수집을 위한 Workflow 클래스
    """

    def __init__(self, state):
        super().__init__()
        self.state = state
        

    def build(self):
        workflow = StateGraph(self.state)

        # 노드 등록
        workflow.add_node("init_driver", nodes.InitDriverNode())
        workflow.add_node("collect_post_links", nodes.CollectPostLinksNode())
        workflow.add_node("set_current_post_url", nodes.SetCurrentPostUrlNode())
        workflow.add_node("load_comments", nodes.LoadCommentsNode())
        workflow.add_node("extract_comments", nodes.ExtractCommentsNode())
        workflow.add_node("save_comments", nodes.SaveCommentsNode())

        # 엣지 설정
        workflow.set_entry_point("init_driver")
        workflow.add_edge("init_driver", "collect_post_links")
        workflow.add_edge("collect_post_links", "set_current_post_url")
        workflow.add_edge("save_comments", "set_current_post_url")
        workflow.add_edge("load_comments", "extract_comments")
        workflow.add_edge("extract_comments", "save_comments")

        # 조건부 엣지
        def has_more_posts(state: CommentWorkflowState) -> str:
            return "load_comments" if state.current_post_url else END

        workflow.add_conditional_edges("set_current_post_url", has_more_posts, {
            "load_comments": "load_comments",
            END: END
        })

        workflow.set_finish_point("set_current_post_url")

        compiled = workflow.compile()
        compiled.name = self.name  
        return compiled


# Workflow 인스턴스 생성

comments_workflow = CommentsWorkflow(CommentWorkflowState)


