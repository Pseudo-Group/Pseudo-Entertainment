"""LangChain 체인을 설정하는 함수 모듈

LCEL(LangChain Expression Language)을 사용하여 체인을 구성합니다.
기본적으로 modules.prompt 템플릿과 modules.models 모듈을 사용하여 LangChain 체인을 생성합니다.
"""

from langchain.schema.runnable import RunnableLambda
from langchain_core.messages import HumanMessage

from agents.image.modules.models import get_gemini_model
from agents.image.modules.prompts import get_image_generation_prompt

def set_image_generation_chain() -> RunnableLambda:
    """
    이미지 생성에 사용할 LangChain 체인을 생성합니다.

    체인은 다음 단계로 구성됩니다:
    1. 입력에서 query를 추출하여 프롬프트에 전달
    2. 프롬프트 템플릿에 값을 삽입하여 최종 프롬프트 생성
    3. LLM을 호출하여 이미지 생성 수행
    4. 결과를 문자열로 변환

    이 함수는 이미지 생성 노드에서 사용됩니다.

    Returns:
        RunnableLambda: 실행 가능한 체인 객체
    """
    # 이미지 생성을 위한 프롬프트 가져오기
    prompt = get_image_generation_prompt()
    # OpenAI 모델 가져오기
    model = get_gemini_model()

    def get_chain(input: dict):
        chian_prompt = prompt.invoke(
            {
                'persona' : input['persona']
            }
        )
        response = model.invoke(
            chian_prompt,
            generation_config = dict(response_modalities=["TEXT", "IMAGE"])
        )
        return response
    return RunnableLambda(get_chain)

def set_image_to_image_generation_chain() -> RunnableLambda:
    """
    이미지를 포함하여 페르소나를 생성합니다.\
    """

    model = get_gemini_model()


    def get_chain(input: dict):

        message = HumanMessage(
            content=[
                {
    "type": "text",
    "text": (
        "You are provided with a reference image and a persona description.\n\n"
        "Your task is to create a hyper-realistic, head-and-shoulders portrait of the **same individual depicted in the reference image**.\n\n"
        "Instructions:\n"
        "- **Identity Preservation is Critical**: The generated portrait must accurately preserve the facial identity, features, and overall appearance of the individual in the reference image.\n"
        "- Only adjust minor details to harmonize with the provided persona description, such as hairstyle, clothing style, or facial expression, without changing the core facial structure.\n"
        "- Do not create a new or different person.\n"
        "- Do not alter essential traits like eye shape, nose, lips, face shape, or skin tone.\n"
        "- Focus strictly on the subject's face and shoulders.\n"
        "- Absolutely avoid generating full-body images, backgrounds with objects, text, frames, numbers, or watermarks.\n"
        "- The background should be simple, neutral, softly blurred, and non-distracting.\n\n"
        "Persona Description:\n"
        f"{input['persona']}\n\n"
        "Again, **the generated portrait must be clearly recognizable as the same person in the reference image**."
    )
},
{
    "type": "image_url",
    "image_url": {"url": f"data:image/jpeg;base64,{input['image_data']}"}
}
            ]
        )

        response = model.invoke(
            [message],
            generation_config=dict(response_modalities=["TEXT","IMAGE"])
        )

        return response
    return RunnableLambda(get_chain)


