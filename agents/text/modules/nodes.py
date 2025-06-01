"""
노드 클래스 모듈

해당 클래스 모듈은 각각 노드 클래스가 BaseNode를 상속받아 노드 클래스를 구현하는 모듈입니다.
"""

import os

import requests

from agents.base_node import BaseNode
from agents.text.modules.chains import set_extraction_chain
from agents.text.modules.models import get_openai_model
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

        state["persona_extracted"] = extracted_persona

        # 추출된 페르소나를 응답으로 반환
        return {"response": extracted_persona}


class ContentSafetyCheckNode(BaseNode):
    """
    Content Safety and Format Check Node using llama-guard-3-8b (via Groq API)
    """

    def check_text_instagram_format(self, text: str) -> bool:
        """Checks whether the text meets Instagram format constraints (max 2200 characters)"""
        return len(text) <= 2200

    def check_sensitive_text(self, text: str) -> bool:
        """Checks whether the given text is safe using the llama-guard model"""
        api_url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "llama-guard-3-8b",
            "messages": [{"role": "user", "content": text}],
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                message = (
                    result.get("choices", [{}])[0].get("message", {}).get("content", "")
                )
                return "safe" in message.lower()
        except Exception as e:
            print(f"[ERROR] llama-guard request failed: {e}")
        return False

    def check_persona_match(self, text: str, persona: dict) -> bool:
        """
        Checks whether the given text matches the extracted persona using OpenAI GPT model
        """
        model = get_openai_model(temperature=0.0)

        # Format the persona into a readable description
        persona_description = "\n".join([f"{k}: {v}" for k, v in persona.items()])
        prompt = (
            "The following is an Instagram text content. Please determine whether it aligns with the provided persona. "
            "Reply only with 'YES' if it matches well, or 'NO' if it doesn't.\n\n"
            f"[Persona]\n{persona_description}\n\n"
            f"[Text]\n{text}"
        )

        try:
            response = model.invoke(prompt).content.strip().upper()
            return "YES" in response
        except Exception as e:
            print(f"[ERROR] Persona check failed: {e}")
            return False  # Fail open if API call fails

    def execute(self, state: TextState) -> dict:
        """
        Runs safety, format, and persona alignment checks on the generated text.
        Updates state with the results of each check.
        """

        text = state.get("response", [""])[-1]
        if not text:
            return {
                "success": False,
                "reason": "EMPTY_TEXT",
                "response": "No text found to check.",
            }

        reasons = []

        # Check content safety
        is_safe = self.check_sensitive_text(text)
        if not is_safe:
            reasons.append("INAPPROPRIATE_TOPIC")

        # Check Instagram format compliance
        is_valid_format = self.check_text_instagram_format(text)
        if not is_valid_format:
            reasons.append("INVALID_INSTAGRAM_FORMAT")

        # Check persona alignment
        persona = state.get("persona_extracted", {})
        is_persona_matched = self.check_persona_match(text, persona)
        if not is_persona_matched:
            reasons.append("MISMATCHED_PERSONA")

        # Determine overall success
        success = len(reasons) == 0

        # Update state with check results
        state["safety_check_passed"] = is_safe
        state["format_check_passed"] = is_valid_format
        state["persona_check_passed"] = is_persona_matched
        state["content_check_passed"] = success

        return {
            "success": success,
            "reason": None if success else reasons,
            "response": "Text content is valid."
            if success
            else "Text content failed validation checks.",
        }
