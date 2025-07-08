"""
인스타그램 API 워크플로우를 위한 상태 정의
"""

from __future__ import annotations

from typing import Annotated, TypedDict, List, Dict, Optional, Any

from langgraph.graph.message import add_messages


class ManagementState(TypedDict):
    """
    인스타그램 API 워크플로우의 상태를 정의하는 TypedDict 클래스

    인스타그램 포스트 정보와 댓글 모니터링을 위한 Workflow에서 사용되는 상태 정보를 정의합니다.
    LangGraph의 상태 관리를 위한 클래스로, Workflow 내에서 처리되는 데이터의 형태와 구조를 지정합니다.
    """

    access_token: str  # 인스타그램 액세스 토큰
    user_id: str  # 인스타그램 사용자 ID
    comment_file_path: str  # JSON 파일 경로
    comment_analysis_file_path:str
    media_data: Optional[List[Dict[str, Any]]]  # 미디어 데이터 목록
    first_media_id: Optional[str]  # 첫 번째 미디어 ID
    current_comments_count: Optional[int]  # 현재 댓글 수
    previous_comments_count: Optional[int]  # 이전 댓글 수
    comments_data: Optional[List[Dict[str, Any]]]  # 댓글 데이터
    has_changes: Optional[bool]  # 댓글 수 변경 여부
    json_data: Optional[Dict[str, Any]]  # JSON 파일에 저장할 데이터
    response: Annotated[
        List[Any], add_messages
    ]  # 응답 메시지 목록 (add_messages로 주석되어 메시지 추가 기능 제공)
    comment_analysis_result: Optional[Any]  # 댓글 분석 결과
