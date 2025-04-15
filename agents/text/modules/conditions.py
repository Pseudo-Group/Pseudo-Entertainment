# from typing import Literal


# def router(state) -> Literal["__end__", "tools"]:
#     """모델의 출력을 기반으로 다음 노드를 결정합니다.

#         이 함수는 모델의 마지막 메시지가 도구 호출을 포함하는지 확인합니다.

#         매개변수:
#                 state (State): 대화의 현재 상태.

#             반환:
#                 str: 호출할 **다음 노드의 이름** (이 예제에선 "__end__" 노드 또는 "tools" 노드).
#     """
#     last_message = state.messages[-1]
#     if not isinstance(last_message, AIMessage):
#         raise ValueError(
#             f"Expected AIMessage in output edges, but got {type(last_message).__name__}"
#         )
#     # 도구 호출이 없으면 완료합니다
#     if not last_message.tool_calls:
#         return "__end__"
#     # 그렇지 않으면 요청된 작업을 실행합니다
#     return "tools"
