"""
노드 클래스 모듈

해당 클래스 모듈은 각각 노드 클래스가 BaseNode를 상속받아 노드 클래스를 구현하는 모듈입니다.
"""

from agents.base_node import BaseNode
from agents.text.modules.chains import (
    set_extraction_chain,
    set_instagram_text_chain,
    set_text_content_check_chain,
)
from agents.text.modules.persona import PERSONA
from agents.text.modules.state import TextState


class PersonaExtractionNode(BaseNode):
    """
    콘텐츠 종류에 적합한 페르소나를 추출하는 노드
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # BaseNode 초기화
        self.chain = set_extraction_chain()  # 페르소나 추출 체인 설정

    def execute(self, state: TextState) -> dict:
        """
        주어진 상태(state)에서 content_topic과 content_type을 추출하여
        페르소나 추출 체인에 전달하고, 결과를 응답으로 반환합니다.
        """
        # 페르소나 추출 체인 실행
        extracted_persona = self.chain.invoke(
            {
                "content_topic": state["content_topic"],  # 콘텐츠 주제
                "content_type": state["content_type"],  # 콘텐츠 유형
                "persona_details": PERSONA,  # 페르소나 세부 정보
            }
        )

        # LangGraph에서 state 업데이트는 반환값으로 처리
        return {
            "persona_extracted": extracted_persona,
        }


class GenTextNode(BaseNode):
    """
    추출된 페르소나를 바탕으로 인스타그램 포스트에 적합한 텍스트를 생성합니다.
    트윗과 같은 간결하고 매력적인 형태로 니제(NEEDZE)의 감성을 담은 텍스트를 생성합니다.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # BaseNode 초기화
        self.chain = set_instagram_text_chain()  # 인스타그램 텍스트 생성 체인 설정

    def execute(self, state: TextState) -> dict:
        """
        추출된 페르소나(persona_extracted)를 받아서 인스타그램에 적합한 텍스트를 생성하여 응답으로 반환합니다.
        """
        # 인스타그램 텍스트 생성 체인 실행
        instagram_text = self.chain.invoke(
            {"persona_extracted": state["persona_extracted"]}  # 추출된 페르소나
        )

        # LangGraph에서 state 업데이트는 반환값으로 처리
        return {
            "instagram_text": instagram_text,
        }


class TextContentCheckNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chain = set_text_content_check_chain()

    def execute(self, state: TextState) -> dict:
        instagram_text = state.get("instagram_text", "")

        # instagram_text가 빈 칸(또는 공백)일 때는 모든 체크를 스킵하고 성공 결과 리턴
        if not instagram_text or not instagram_text.strip():
            result = {
                "text_content_checker_result": {
                    "success": True,
                    "reason": [],
                    "content_check_passed": True,
                    "format_check_passed": True,
                    "safety_check_passed": True,
                    "persona_check_passed": True,
                    "message": "Skipped checks because text_content is empty.",
                }
            }
            state.update(result)
            return result

        input_data = {
            "response": state.get("response", [""]),
            "persona_extracted": state.get("persona_extracted", {}),
        }
        result = self.chain.invoke(input_data)
        state.update(result)
        return result
