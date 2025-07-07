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
