from langgraph.graph import StateGraph
from agents.base_workflow import BaseWorkflow
from agents.collect_comments.modules import nodes
from agents.collect_comments.modules.state import CollectCommentsState

class CollectCommentsWorkflow(BaseWorkflow):
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
        def has_more_posts(state: CollectCommentsState) -> str:
            return "load_comments" if state.current_post_url else "__end__"

        workflow.add_conditional_edges("set_current_post_url", has_more_posts, {
            "load_comments": "load_comments",
            "__end__": "__end__"
        })

        workflow.set_finish_point("set_current_post_url")

        compiled = workflow.compile()
        compiled.name = self.name  
        return compiled


# Workflow 인스턴스 생성

collect_comments_workflow = CollectCommentsWorkflow(CollectCommentsState)


