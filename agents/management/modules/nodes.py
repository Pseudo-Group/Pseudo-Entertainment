"""
노드 클래스 모듈

해당 클래스 모듈은 각각 노드 클래스가 BaseNode를 상속받아 노드 클래스를 구현하는 모듈입니다.

아래는 예시입니다.
"""

from agents.base_node import BaseNode
from agents.management.modules.chains import set_resource_planning_chain
from agents.management.modules.state import ManagementState


class ResourceManagementNode(BaseNode):
    """
    프로젝트에 필요한 리소스를 계획하고 관리하는 노드
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # BaseNode 초기화
        self.chain = set_resource_planning_chain()  # 리소스 계획 체인 설정

    def execute(self, state: ManagementState) -> dict:
        """
        주어진 상태(state)에서 project_id, request_type, query 등의 정보를 추출하여
        리소스 계획 체인에 전달하고, 결과를 응답으로 반환합니다.
        """
        # 팀 구성원 기본값 처리
        team_members = state.get("team_members", [])

        # 리소스 계획 체인 실행
        resource_plan = self.chain.invoke(
            {
                "project_id": state["project_id"],  # 프로젝트 ID
                "request_type": state["request_type"],  # 요청 유형
                "query": state["query"],  # 사용자 쿼리
                "team_members": team_members,  # 팀 구성원
                "resources_available": state.get(
                    "resources_available", {}
                ),  # 사용 가능한 리소스
            }
        )

        # 상태 업데이트
        state["resource_plan"] = resource_plan

        # 생성된 리소스 계획을 응답으로 반환
        return {"response": resource_plan}
