"""
이미지 Workflow의 상태를 정의하는 모듈

이 모듈은 이미지 기반 콘텐츠 생성을 위한 Workflow에서 사용되는 상태 정보를 정의합니다.
LangGraph의 상태 관리를 위한 클래스를 포함합니다.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage

@dataclass
class ImageState(TypedDict):
    """
    이미지 Workflow의 상태를 정의하는 TypedDict 클래스

    이미지 기반 콘텐츠 생성을 위한 Workflow에서 사용되는 상태 정보를 정의합니다.
    LangGraph의 상태 관리를 위한 클래스로, Workflow 내에서 처리되는 데이터의 형태와 구조를 지정합니다.
    """

    persona: Annotated[str, "Text Team 에서 추출된 persona"]
    fixed: Annotated[bool, "고정된 이미지 생성 여부"]
    fixed_image: Annotated[str, "고정된 이미지 URL"]
    fixed_image_path: Annotated[str, "고정된 이미지 경로"]

    gen_image: Annotated[str, "생성된 이미지 URL"]  
    gen_image_path: Annotated[str, "생성된 이미지 경로"]

    response: Annotated[
        list, add_messages
    ]  # 응답 메시지 목록 (add_messages로 주석되어 메시지 추가 기능 제공)
    generation_image: AIMessage
