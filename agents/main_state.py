from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


@dataclass
class MainState(TypedDict):
    """
    메인 Workflow의 상태를 정의하는 TypedDict 클래스

    Team Member는 해당 State에서 따로 작업을 진행하지 않으셔도 됩니다.

    예시:
    ```python
    # 상태 초기화
    initial_state = {
        "content_topic": "여름 휴가",
        "content_type": "블로그 글",
        "query": "여름 휴가 계획",
        "image": "",
        "response": [],
    }
    ```
    """

    query: str
    response: Annotated[list, add_messages]
