"""
조건부 라우팅 함수 모듈

이 모듈은 LangGraph Workflow에서 조건부 라우팅을 처리하는 함수들을 제공합니다.
조건부 라우팅은 Workflow의 다음 단계를 동적으로 결정하는 데 사용됩니다.

현재는 주석 처리된 예시 코드만 포함되어 있으며, 필요에 따라 실제 구현을 추가할 수 있습니다.
이 예시 코드는 ReAct 패턴에서 LLM의 출력에 따라 다음 노드를 결정하는 라우터 함수를 보여줍니다.

Workflow가 확장됨에 따라 다양한 조건부 라우팅 함수를 이 모듈에 추가할 수 있습니다.
예를 들어, 콘텐츠 유형에 따른 라우팅, 사용자 요청 유형에 따른 라우팅 등을 구현할 수 있습니다.
"""

from typing import Literal


def route_request(
    state,
) -> Literal[
    "resource_management",
    "instagram_content_verification",
    "instagram_policies_search",
    "content_risks_analysis",
]:
    """
    요청 유형에 따라 적절한 노드로 라우팅하는 함수

    이 함수는 상태의 request_type을 기반으로 다음에 실행할 노드를 결정합니다.

    Args:
        state: 현재 Workflow 상태 객체

    Returns:
        str: 다음에 실행할 노드의 이름
    """
    request_type = state.get("request_type", "").lower()

    # 요청 유형에 따른 라우팅
    if "content" in request_type or "verify" in request_type or "검증" in request_type:
        return "instagram_content_verification"
    elif (
        "policy" in request_type
        or "정책" in request_type
        or "guideline" in request_type
    ):
        return "instagram_policies_search"
    elif "risk" in request_type or "위험" in request_type or "분석" in request_type:
        return "content_risks_analysis"
    else:
        # 기본적으로 리소스 관리로 라우팅
        return "resource_management"


# from typing import Literal


# def router(state) -> Literal["__end__", "tools"]:
#     """
#     모델의 출력을 기반으로 다음 노드를 결정하는 라우터 함수
#
#     이 함수는 LLM의 마지막 메시지를 검사하여 도구 호출이 포함되어 있는지 확인하고,
#     그 결과에 따라 Workflow의 다음 단계를 결정합니다.
#
#     도구 호출이 있으면 "tools" 노드로 라우팅하고, 그렇지 않으면 Workflow를 종료합니다.
#     이는 ReAct 패턴의 일반적인 구현 방식으로, LLM이 도구를 사용해야 할지 또는
#     최종 응답을 생성해야 할지를 결정하게 합니다.
#
#     Args:
#         state (State): 현재 Workflow 상태 객체 (메시지 기록 포함)
#
#     Returns:
#         str: 다음에 실행할 노드의 이름 ("__end__" 또는 "tools")
#
#     Raises:
#         ValueError: 마지막 메시지가 AIMessage 타입이 아닌 경우
#
#     예시:
#     ```python
#     # Workflow에 조건부 에지 추가
#     builder.add_conditional_edges(
#         "call_model",  # 소스 노드
#         router,       # 라우터 함수
#         {
#             "__end__": "__end__",  # 종료 조건
#             "tools": "execute_tools"  # 도구 실행 조건
#         }
#     )
#     ```
#     """
#     # 상태에서 마지막 메시지 가져오기
#     last_message = state.messages[-1]
#
#     # 메시지 타입 검증
#     if not isinstance(last_message, AIMessage):
#         raise ValueError(
#             f"Expected AIMessage in output edges, but got {type(last_message).__name__}"
#         )
#
#     # 도구 호출 여부에 따른 라우팅 결정
#     if not last_message.tool_calls:
#         return "__end__"  # 도구 호출이 없으면 Workflow 종료
#
#     # 도구 호출이 있으면 도구 실행 노드로 라우팅
#     return "tools"
