from __future__ import annotations

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages

from dataclasses import dataclass

@dataclass
class TextState(TypedDict):
    """
    텍스트 Workflow의 상태를 정의하는 TypedDict 클래스
    
    텍스트 기반 콘텐츠 생성을 위한 Workflow에서 사용되는 상태 정보를 정의합니다.
    LangGraph의 상태 관리를 위한 클래스로, Workflow 내에서 처리되는 데이터의 형태와 구조를 지정합니다.
    """
    
    content_topic: str  # 콘텐츠의 주제 (예: "여름 휴가", "음식 리뷰")
    content_type: str   # 콘텐츠의 유형 (예: "블로그 글", "소셜 미디어 포스트")
    query: str          # 사용자 쿼리 또는 요청사항
    response: Annotated[list, add_messages]  # 응답 메시지 목록 (add_messages로 주석되어 메시지 추가 기능 제공)
