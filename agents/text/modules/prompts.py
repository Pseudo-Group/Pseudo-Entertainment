"""프롬프트 템플릿를 생성하는 함수 모듈

프롬프트 템플릿를 생성하는 함수 모듈을 구성합니다.
기본적으로 PromptTemplate를 사용하여 프롬프트 템플릿를 생성하고 반환시킵니다.
"""

from langchain_core.prompts import PromptTemplate


def get_extraction_prompt():
    """
    페르소나 추출을 위한 프롬프트 템플릿을 생성합니다.

    1. 기본 페르소나 정보: 니제(NEEDZE)의 상세 프로필
    2. 콘텐츠 유형: 생성할 콘텐츠의 형태 (예: 블로그 글, 소셜 미디어 포스트 등)
    3. 콘텐츠 주제: 생성할 콘텐츠의 주제 (예: 여름 휴가, 음식 리뷰 등)

    프롬프트는 LLM에게 주어진 콘텐츠 유형과 주제에 맞게 페르소나의 가장 연관성 높은
    측면을 추출하고 요약하도록 지시합니다. 추출된 페르소나는 한국어로 반환됩니다.

    Returns:
        PromptTemplate: 페르소나 추출을 위한 프롬프트 템플릿 객체
    """
    # 페르소나 추출을 위한 프롬프트 템플릿 정의
    extraction_template = """You are a creative assistant tasked with extracting and summarizing a detailed persona
for targeted creative output. You are provided with the following inputs:

1. Persona Details: {persona_details}

2. Content Type: {content_type}

3. Content Topic: {content_topic}

Your Task:
Using the above inputs, extract and summarize the most relevant aspects of NEEDZE’s persona tailored to the specified
content type and content topic. In your summary, ensure you:

Highlight key personal details and characteristics that align with the content type.

Emphasize the elements of her artistic style that resonate with the content topic (e.g., visual aesthetics for images,
lyrical and tone details for text, or vocal and musical nuances for music/voice).

Maintain a tone that reflects NEEDZE’s authentic, introspective, and creative identity.

Your output should be a concise, focused summary of the persona that serves as a clear reference for creating content
in the specified format.

All responses must be in Korean.

Extracted Persona:"""

    # PromptTemplate 객체 생성 및 반환
    return PromptTemplate(
        template=extraction_template,  # 정의된 프롬프트 템플릿
        input_variables=[
            "content_type",
            "content_topic",
            "persona_details",
        ],  # 프롬프트에 삽입될 변수들
    )


def get_instagram_text_prompt():
    """
    추출된 페르소나를 바탕으로 인스타그램 텍스트를 생성하기 위한 프롬프트 템플릿을 생성합니다.

    이 함수는 이미 추출된 페르소나 정보를 받아서 인스타그램에 적합한
    짧고 매력적인 텍스트를 생성하도록 LLM에게 지시합니다.

    Returns:
        PromptTemplate: 인스타그램 텍스트 생성을 위한 프롬프트 템플릿 객체
    """
    # 인스타그램 텍스트 생성을 위한 프롬프트 템플릿 정의
    instagram_template = """당신은 니제(NEEDZE)의 인스타그램 계정을 운영하는 크리에이티브 어시스턴트입니다.

다음은 특정 주제와 콘텐츠 유형에 맞게 추출된 니제의 페르소나입니다:

{persona_extracted}

위의 추출된 페르소나를 바탕으로, 니제의 목소리와 스타일을 반영한 인스타그램 포스트 텍스트를 작성해주세요.

작성 가이드라인:
1. 트윗과 비슷한 길이로 간결하고 임팩트 있게 작성 (1-3문장)
2. 니제의 진솔하고 내성적인 성격을 반영
3. 감각적이고 시적인 표현 사용
4. 일상 속 미묘한 감정을 포착
5. 시각적 색감과 촉각적 표현을 조화롭게 활용
6. 니제의 음악적 감성과 예술적 스타일이 드러나도록 작성
7. 자연스럽고 친근한 어조 사용
8. 해시태그는 포함하지 말고 순수 텍스트만 작성

인스타그램 포스트:"""

    # PromptTemplate 객체 생성 및 반환
    return PromptTemplate(
        template=instagram_template,  # 정의된 프롬프트 템플릿
        input_variables=[
            "persona_extracted",
        ],
    )


def get_persona_match_prompt() -> PromptTemplate:
    """
    Returns a prompt template to evaluate if a given text aligns with a provided persona.

    The model must respond only with "YES" or "NO".
    """
    template = (
        "The following is an Instagram text content. Please determine whether it aligns with the provided persona. "
        "Reply only with 'YES' if it matches well, or 'NO' if it doesn't.\n\n"
        "[Persona]\n{persona_description}\n\n"
        "[Text]\n{text}"
    )

    return PromptTemplate(
        template=template, input_variables=["persona_description", "text"]
    )
