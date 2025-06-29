"""프롬프트 템플릿을 생성하는 함수 모듈

프롬프트 템플릿을 생성하는 함수 모듈을 구성합니다.
기본적으로 PromptTemplate을 사용하여 프롬프트 템플릿을 생성하고 반환합니다.
"""

from langchain_core.prompts import PromptTemplate

def get_image_generation_prompt():
    """
    자연스럽고 선명한 정면 얼굴 이미지 생성 프롬프트.

    - persona 변수는 전달받되 프롬프트 안에 직접 언급하지 않음
    - 색상과 질감은 선명하고 깨끗하게 출력되도록 유도
    - 전체 얼굴(머리 꼭대기부터 턱 끝까지)과 자연스러운 머리카락 윤곽이 잘 보이게
    """
    image_generation_template = """Create a hyper-realistic head-and-shoulders portrait of a young female singer-songwriter based on the following persona:

{persona}

You must strictly generate only a portrait of the subject, focusing only on the face and shoulders. 
No full-body shots, no landscapes, no objects, no backgrounds, no decorations, no frames, and absolutely no text, letters, symbols, numbers, watermarks, or signatures are allowed in the image. 
The background must be simple and neutral or blurred to avoid any distractions. 
The final output must be a clean portrait focusing entirely on the subject without any additional elements.
"""

    return PromptTemplate(
        template=image_generation_template,
        input_variables=["persona"],
    )

def get_comfyui_generation_prompt():
    """
    ComfyUI에 요청하는 Payload를 생성하기 위한 프롬프트
    """
    comfyui_generation_template = """
너는 이미지 생성 프롬프트를 만드는 전문가야.

다음은 인물의 페르소나 정보야:
--------------------
{persona}
--------------------

위 페르소나를 바탕으로, 그 인물과 어울리는 **이미지 생성용 prompt**와 **negative_prompt**를 각각 작성해줘.

형식은 아래와 같아:

```json
{{
  "prompt": "<페르소나와 어울리는 감성, 스타일, 배경 등을 담은 photorealistic 이미지 생성 프롬프트>",
  "negative_prompt": "<이 인물이 싫어할 요소나 방해가 될 요소를 배제하기 위한 프롬프트 (예: nsfw, lowres 등)>"
}}
```
"""
    return PromptTemplate(
        template=comfyui_generation_template,
        input_variables=["persona"],
    )