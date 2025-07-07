"""
노드 클래스 모듈

해당 클래스 모듈은 각각 노드 클래스가 BaseNode를 상속받아 노드 클래스를 구현하는 모듈입니다.
"""

import re

from agents.image.modules.chains import get_outfit_prompt_chain


def generate_outfit_prompt_node(state):
    user_request = state["query"]
    chain = get_outfit_prompt_chain()
    result = chain.run(user_request)
    return {**state, "outfit_prompt": result}


def refine_outfit_prompt_node(state):
    prompt = state["outfit_prompt"]

    # "Image Generation Prompt:" 이후 한 문장 추출
    match = re.search(
        r"Image Generation Prompt:\s*(.+)", prompt, re.DOTALL | re.IGNORECASE
    )
    if match:
        image_prompt = match.group(1).strip()
    else:
        # fallback: 첫 문단만 사용
        image_prompt = prompt.strip().split("\n\n")[0]

    image_prompt = re.sub(r"\*\*.*?\*\*", "", image_prompt)  # bold 제거
    image_prompt = re.sub(r"[^\x00-\x7F]+", "", image_prompt)  # 이모지 제거
    image_prompt = image_prompt.strip()[:800]

    return {**state, "refined_outfit_prompt": image_prompt}


def refine_outfit_prompt_with_llm_node(state):
    """
    LLM을 활용하여 생성된 의상 프롬프트를 이미지 생성에 적합한 한 문단으로 정제하는 노드

    이 노드는 outfit_prompt 필드에 저장된 스타일링 설명을 받아,
    이미지 생성 모델이 이해하기 좋은 영어 묘사로 재구성합니다.
    """

    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate

    from agents.image.modules.chains import get_llm

    prompt_template = PromptTemplate.from_template(
        "다음은 의상 스타일링 결과입니다.\n\n{raw_prompt}\n\n"
        "위 결과에서 '**Image Generation Prompt:**' 문단만 참고하여 아래 요구를 따르세요:\n"
        "- 하나의 문장만 생성하세요.\n"
        "- 문장 외의 설명, 인삿말, 주석은 절대 포함하지 마세요.\n"
        "- 인물과 의상을 구체적으로 묘사하세요.\n"
        "- 영어로 작성하세요.\n"
        "단 하나의 문장만 출력하세요."
    )

    chain = LLMChain(llm=get_llm(), prompt=prompt_template)
    raw_prompt = state["outfit_prompt"]
    refined_prompt = chain.run({"raw_prompt": raw_prompt})

    return {**state, "refined_outfit_prompt": refined_prompt.strip()}


# from agents.base_node import BaseNode

# from agents.image.modules.chains import set_image_generation_chain


# class ImageGenerationNode(BaseNode):
#     """
#     이미지 생성을 위한 노드

#     이 노드는 사용자의 요청에 따라 이미지를 생성하는 기능을 담당합니다.
#     """

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)  # BaseNode 초기화
#         # self.chain = set_image_generation_chain()  # 이미지 생성 체인 설정

#     def execute(self, state) -> dict:
#         """
#         주어진 상태(state)에서 query를 추출하여
#         이미지 생성 체인에 전달하고, 결과를 응답으로 반환합니다.

#         Args:
#             state: 현재 워크플로우 상태

#         Returns:
#             dict: 생성된 이미지 정보가 포함된 응답
#         """
#         # 실제 구현은 추후 개발 시 추가
#         # generated_image = self.chain.invoke(
#         #     {
#         #         "query": state["query"],  # 사용자 쿼리
#         #     }
#         # )

#         # 더미 응답 생성
#         dummy_response = "이미지 생성 기능은 아직 구현되지 않았습니다."

#         # 응답 반환
#         return {"response": dummy_response}
