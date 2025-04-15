"""
유틸리티 및 보조 함수.
아래는 실제 ReAct Agent에서 사용되는 예시입니다.
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
