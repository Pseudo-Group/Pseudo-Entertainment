"""
음악 Workflow의 상태를 정의하는 모듈

이 모듈은 음악 기반 콘텐츠 생성을 위한 Workflow에서 사용되는 상태 정보를 정의합니다.
LangGraph의 상태 관리를 위한 클래스를 포함합니다.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, TypedDict, Dict

from langgraph.graph.message import add_messages


@dataclass
class MusicState(TypedDict):
    """
    음악 Workflow의 상태를 정의하는 TypedDict 클래스

    음악 기반 콘텐츠 생성을 위한 Workflow에서 사용되는 상태 정보를 정의합니다.
    LangGraph의 상태 관리를 위한 클래스로, Workflow 내에서 처리되는 데이터의 형태와 구조를 지정합니다.
    """

    query: str  # 사용자 쿼리 또는 요청사항
    response: Annotated[
        list, add_messages
    ]  # 응답 메시지 목록 (add_messages로 주석되어 메시지 추가 기능 제공)
    youtube_query: str
    video_url: str
    video_analysis: str
