"""
유틸리티 및 보조 함수 모듈

이 모듈은 텍스트 처리 Workflow에서 사용할 수 있는 다양한 유틸리티 함수를 제공합니다.
현재는 주석 처리된 예시 코드만 포함되어 있으며, 필요에 따라 실제 구현을 추가할 수 있습니다.

아래 예시 코드는 ReAct Agent 패턴에서 사용될 수 있는 유틸리티 함수들입니다.
이 함수들은 메시지 처리 및 모델 로딩과 관련된 기능을 제공합니다.

추후 개발 시 필요한 유틸리티 함수를 이 모듈에 추가하여 코드 재사용성을 높일 수 있습니다.
예를 들어, 텍스트 전처리, 포맷팅, 데이터 변환 등의 기능을 구현할 수 있습니다.
"""

# from langchain.chat_models import init_chat_model
# from langchain_core.language_models import BaseChatModel
# from langchain_core.messages import BaseMessage


# def get_message_text(msg: BaseMessage) -> str:
#     """메시지의 텍스트 내용을 가져옵니다."""
#     content = msg.content
#     if isinstance(content, str):
#         return content
#     elif isinstance(content, dict):
#         return content.get("text", "")
#     else:
#         txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
#         return "".join(txts).strip()


# def load_chat_model(fully_specified_name: str) -> BaseChatModel:
#     """완전히 지정된 이름에서 채팅 모델을 로드합니다.

#     매개변수:
#         fully_specified_name (str): 'provider/model' 형식의 문자열.
#     """
#     provider, model = fully_specified_name.split("/", maxsplit=1)
#     return init_chat_model(model, model_provider=provider)
