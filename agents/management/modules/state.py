"""
아래는 예시입니다.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, TypedDict, List, Dict, Optional

from langgraph.graph.message import add_messages


@dataclass
class ManagementState(TypedDict):
    """
    관리(Management) Workflow의 상태를 정의하는 TypedDict 클래스

    프로젝트, 팀, 리소스의 관리와 크리에이터 직업 성장을 위한 Workflow에서 사용되는 상태 정보를 정의합니다.
    LangGraph의 상태 관리를 위한 클래스로, Workflow 내에서 처리되는 데이터의 형태와 구조를 지정합니다.
    """

    project_id: str  # 프로젝트 ID (예: "PRJ-2023-001", "EP-MARVEL-S01")
    request_type: str  # 요청 유형 (예: "resource_allocation", "team_management", "creator_development")
    query: str  # 사용자 쿼리 또는 요청사항
    response: Annotated[
        list, add_messages
    ]
    team_members: Optional[List[str]] = None  # 팀 구성원 목록
    resources_available: Optional[Dict[str, any]] = None  # 사용 가능한 리소스 정보
    resource_plan: Optional[str] = None  # 리소스 계획 콘텐츠
      # 응답 메시지 목록 (add_messages로 주석되어 메시지 추가 기능 제공)
