from langgraph.graph import StateGraph

from agents.main_state import GraphState


class MuseChatGraph:
    def __init__(self):
        self.main_graph = self.build_main_graph()
        self.rewrite_graph = self.build_rewrite_graph()

    def build_main_graph(self) -> StateGraph:
        """
        LangGraph를 사용하여 노드들을 연결
        """

        main_graph = StateGraph(GraphState)
        # main_graph.add_node("single2hyde", Single2HyDENode())
        # main_graph.add_node("multi2hyde", Multi2HyDENode())
        # main_graph.add_node("manager_sub_graph", ManangerSubGraph())
        # main_graph.add_node("judge", JudgeNode())
        # main_graph.add_node("supervisor", SupervisorNode())

        # main_graph.add_edge(START, "judge")
        # main_graph.add_conditional_edges(
        #     "judge",
        #     CheckAnswer(),
        #     {
        #         "yes": END,
        #         "no": "supervisor",
        #     },
        # )
        # main_graph.add_conditional_edges(
        #     "supervisor",
        #     Supervisor(),
        #     {
        #         "single_modal_input": "single2hyde",
        #         "multi_modal_input": "multi2hyde",
        #     },
        # )
        # main_graph.add_edge("single2hyde", "sub_graph")
        # main_graph.add_edge("multi2hyde", "sub_graph")
        # main_graph.add_edge("sub_graph", END)

        # 그래프 컴파일
        return main_graph.compile()

    def build_rewrite_graph(self) -> StateGraph:
        rewrite_graph = StateGraph(GraphState)
        # rewrite_graph.add_node("re_writer", ReWriterNode())
        # rewrite_graph.add_node("sub_graph", self.sub_graph)

        # rewrite_graph.add_edge(START, "re_writer")
        # rewrite_graph.add_edge("re_writer", "sub_graph")
        # rewrite_graph.add_edge("sub_graph", END)
        return rewrite_graph.compile()


def process_query(
    graph: StateGraph,
    query: str,
    image: str = None,
    chat_history: list = None,
    last_documents: list = None,
    hypothetical_doc: str = None,
):
    initial_state = {
        "query": query,
        "image": image or "",
        "chat_history": chat_history or [],
        "documents": last_documents or [],
        "hypothetical_doc": hypothetical_doc or "",
    }

    # LangGraph의 메시지 스트리밍 모드 사용
    for namespace, chunk in graph.stream(
        initial_state, stream_mode="updates", subgraphs=True
    ):
        for node, value in chunk.items():
            # aggregation 노드의 결과 캡처
            if node == "aggregation":
                if isinstance(value, dict) and "aggregated_documents" in value:
                    yield {"aggregated_documents": value["aggregated_documents"]}
                continue

            # judge 노드의 응답 스트리밍
            if node == "judge" and value["judge_answer"] != "No":
                yield value["judge_answer"]
                continue

            # single2hyde 또는 multi2hyde 노드의 결과 캡처
            if node in ["single2hyde", "multi2hyde"]:
                if isinstance(value, dict) and "hypothetical_doc" in value:
                    yield {"hypothetical_doc": value["hypothetical_doc"]}
                continue

            # generator 노드의 응답 스트리밍
            if node in ["high_similarity_generator", "low_similarity_generator"]:
                yield value["response"]
