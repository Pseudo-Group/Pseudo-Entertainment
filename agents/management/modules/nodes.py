"""
노드 클래스 모듈

해당 클래스 모듈은 각각 노드 클래스가 BaseNode를 상속받아 노드 클래스를 구현하는 모듈입니다.
"""

from agents.base_node import BaseNode
from agents.management.modules.chains import (
    set_resource_planning_chain,
    set_search_planning_chain,
    set_summary_chain
)
from agents.management.modules.state import ManagementState
from agents.management.modules.tools import tavily_tool


class ResourceManagementNode(BaseNode):
    """
    프로젝트에 필요한 리소스를 계획하고 관리하는 노드
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chain = set_resource_planning_chain()

    def execute(self, state: ManagementState) -> dict:
        """
        주어진 상태(state)에서 project_id, request_type, query 등의 정보를 추출하여
        리소스 계획 체인에 전달하고, 결과를 응답으로 반환합니다.
        """
        team_members = state.get("team_members", [])

        resource_plan = self.chain.invoke(
            {
                "project_id": state["project_id"],
                "request_type": state["request_type"],
                "query": state["query"],
                "team_members": team_members,
                "resources_available": state.get("resources_available", {}),
            }
        )

        state["resource_plan"] = resource_plan
        return {"response": resource_plan}


class IUResearchPlanNode(BaseNode):
    """
    IU 관련 조사 주제를 바탕으로 구체적인 웹 검색 계획을 수립하는 노드
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chain = set_search_planning_chain()

    def execute(self, state: ManagementState) -> dict:
        """
        조사 주제를 바탕으로 구체적인 웹 검색 계획을 수립합니다.
        """
        if self.verbose:
            self.logging("execute", message="검색 계획 수립 시작")

        print("--- 1. 검색 계획 수립 중.. ---")
        
        # topic이 없으면 query에서 추출
        topic = state.get("topic") or state["query"]
        
        search_queries_text = self.chain.invoke({"topic": topic})
        search_queries = search_queries_text.split("\n")

        # 빈 줄 제거
        search_queries = [q.strip() for q in search_queries if q.strip()]

        print(f"생성된 쿼리: {search_queries}")
        
        return {
            "topic": topic,
            "search_queries": search_queries,
            "response": f"검색 계획이 수립되었습니다. 총 {len(search_queries)}개의 검색어가 생성되었습니다."
        }


class IUResearchSearchNode(BaseNode):
    """
    생성된 쿼리들을 바탕으로 웹 검색을 수행하고 결과를 취합하는 노드
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute(self, state: ManagementState) -> dict:
        """
        생성된 쿼리들을 바탕으로 웹 검색을 수행하고 결과를 취합합니다.
        """
        if self.verbose:
            self.logging("execute", message="웹 검색 수행 시작")

        print("--- 2. 웹 검색 수행 중.. ---")
        
        search_queries = state["search_queries"]
        all_results = []

        for query in search_queries:
            print(f"검색어 '{query}' 검색 중..")
            try:
                results = tavily_tool.invoke({"query": query})
                all_results.append(f"'{query}' 검색 결과: \n{results}\n\n")
            except Exception as e:
                print(f"검색 오류: {e}")
                all_results.append(f"'{query}' 검색 실패: {str(e)}\n\n")

        search_results = "\n".join(all_results)
        
        return {
            "search_results": search_results,
            "response": f"웹 검색이 완료되었습니다. {len(search_queries)}개의 검색어로 조사를 수행했습니다."
        }


class IUResearchSummaryNode(BaseNode):
    """
    수집된 모든 검색 결과를 바탕으로 최종 보고서를 요약/생성하는 노드
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chain = set_summary_chain()

    def execute(self, state: ManagementState) -> dict:
        """
        수집된 모든 검색 결과를 바탕으로 최종 보고서를 요약/생성합니다.
        """
        if self.verbose:
            self.logging("execute", message="검색 결과 요약 시작")

        print("--- 3. 검색 결과 요약 및 보고서 생성 중.. ---")
        
        summary = self.chain.invoke({
            "topic": state["topic"],
            "search_results": state["search_results"]
        })
        
        return {
            "summary": summary,
            "response": summary
        }