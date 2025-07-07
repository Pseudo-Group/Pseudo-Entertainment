"""LangChain 체인를 설정하는 함수 모듈

LCEL(LangChain Expression Language)을 사용하여 체인을 구성합니다.
기본적으로 modules.prompt 템플릿과 modules.models 모듈을 사용하여 LangChain 체인를 생성합니다.

"""

from langchain.schema.runnable import (
    RunnableLambda,
    RunnableMap,
    RunnablePassthrough,
    RunnableSerializable,
)
from langchain_core.output_parsers import StrOutputParser

from agents.text.modules.models import get_groq_model, get_openai_model
from agents.text.modules.persona import PERSONA
from agents.text.modules.prompts import (
    get_extraction_prompt,
    get_instagram_text_prompt,
    get_persona_match_prompt,
)


def set_extraction_chain() -> RunnableSerializable:
    """
    페르소나 추출에 사용할 LangChain 체인을 생성합니다.

    이 함수는 LCEL(LangChain Expression Language)을 사용하여 체인을 구성합니다.
    체인은 다음 단계로 구성됩니다:
    1. 입력에서 content_topic과 content_type을 추출하여 프롬프트에 전달
    2. 프롬프트 템플릿에 값을 삽입하여 최종 프롬프트 생성
    3. LLM을 호출하여 페르소나 추출 수행
    4. 결과를 문자열로 변환

    이 함수는 페르소나 추출 노드에서 사용됩니다.
    ```

    Returns:
        RunnableSerializable: 실행 가능한 체인 객체
    """
    # 페르소나 추출을 위한 프롬프트 가져오기
    prompt = get_extraction_prompt()
    # OpenAI 모델 가져오기
    model = get_openai_model()

    # LCEL을 사용하여 체인 구성
    return (
        # 입력에서 필요한 필드 추출 및 프롬프트에 전달
        RunnablePassthrough.assign(
            content_topic=lambda x: x["content_topic"],  # 콘텐츠 주제 추출
            content_type=lambda x: x["content_type"],  # 콘텐츠 유형 추출
            persona_details=lambda x: PERSONA,
        )
        | prompt  # 프롬프트 적용
        | model  # LLM 모델 호출
        | StrOutputParser()  # 결과를 문자열로 변환
    )


def set_instagram_text_chain() -> RunnableSerializable:
    """
    인스타그램 텍스트 생성에 사용할 LangChain 체인을 생성합니다.

    이 함수는 LCEL(LangChain Expression Language)을 사용하여 체인을 구성합니다.
    체인은 다음 단계로 구성됩니다:
    1. 입력에서 persona_extracted를 추출하여 프롬프트에 전달
    2. 프롬프트 템플릿에 값을 삽입하여 최종 프롬프트 생성
    3. LLM을 호출하여 인스타그램 텍스트 생성 수행
    4. 결과를 문자열로 변환

    이 함수는 GenTextNode에서 사용됩니다.

    Returns:
        RunnableSerializable: 실행 가능한 체인 객체
    """
    # 인스타그램 텍스트 생성을 위한 프롬프트 가져오기
    prompt = get_instagram_text_prompt()
    # OpenAI 모델 가져오기
    model = get_openai_model()

    # LCEL을 사용하여 체인 구성
    return (
        # 입력에서 필요한 필드 추출 및 프롬프트에 전달
        RunnablePassthrough.assign(
            persona_extracted=lambda x: x["persona_extracted"],  # 추출된 페르소나
        )
        | prompt  # 프롬프트 적용
        | model  # LLM 모델 호출
        | StrOutputParser()  # 결과를 문자열로 변환
    )


def set_instagram_text_format_check_chain() -> RunnableLambda:
    """
    인스타그램 포맷(2200자 이하) 검사를 위한 체인을 반환합니다.

    Returns:
        RunnableLambda: 텍스트 길이를 검사하는 실행 체인
    """
    return RunnableLambda(lambda x: len(x["text"]) <= 2200)


def set_sensitive_text_check_chain() -> RunnableLambda:
    def is_text_safe(x):
        model = get_groq_model("meta-llama/llama-guard-4-12b")
        try:
            response = model.invoke(x["text"])
            return "safe" in response.content.lower()
        except Exception as e:
            print(f"[ERROR] llama-guard request failed: {e}")
        return False

    return RunnableLambda(is_text_safe)


def set_text_persona_match_check_chain() -> RunnableLambda:
    def check_persona_match(x):
        model = get_openai_model()

        text = x["text"]
        persona = x.get("persona", {})

        # 다양한 타입의 persona_description 처리: dict, str, list
        if isinstance(persona, dict):
            persona_description = "\n".join([f"{k}: {v}" for k, v in persona.items()])
        elif isinstance(persona, list):
            persona_description = "\n".join([str(p) for p in persona])
        else:
            persona_description = str(persona)

        prompt_template = get_persona_match_prompt()
        prompt = prompt_template.format(
            persona_description=persona_description, text=text
        )

        try:
            response = model.invoke(prompt).content.strip().upper()
            return "YES" in response
        except Exception as e:
            print(f"[ERROR] Persona check failed: {e}")
            return False

    return RunnableLambda(check_persona_match)


def set_text_content_check_chain() -> RunnableSerializable:
    return (
        RunnablePassthrough.assign(
            text=lambda x: x if isinstance(x, str) else x.get("instagram_text", ""),
            persona=lambda x: (
                x.get("persona_extracted", {}) if isinstance(x, dict) else {}
            ),
        )
        | RunnableMap(
            {
                "format_check_passed": set_instagram_text_format_check_chain(),
                "safety_check_passed": set_sensitive_text_check_chain(),
                "persona_check_passed": set_text_persona_match_check_chain(),
            }
        )
        | RunnableLambda(
            lambda results: {
                "text_content_checker_result": {
                    "success": all(results.values()),
                    "reason": [k for k, v in results.items() if not v],
                    "content_check_passed": all(results.values()),
                    **results,
                    "message": (
                        "Text content is valid."
                        if all(results.values())
                        else "Text content failed validation checks."
                    ),
                }
            }
        )
    )
