"""
노드 클래스 모듈

해당 클래스 모듈은 각각 노드 클래스가 BaseNode를 상속받아 노드 클래스를 구현하는 모듈입니다.
"""

from agents.base_node import BaseNode

from agents.image.modules.graphs import set_image_generation_graph


class ImageGenerationNode(BaseNode):
     """
     이미지 생성을 위한 노드

     이 노드는 사용자의 요청에 따라 이미지를 생성하는 기능을 담당합니다.
     """

     def __init__(self, **kwargs):
         super().__init__(**kwargs)  # BaseNode 초기화
         self.graph = set_image_generation_graph()  # 이미지 생성 체인 설정

     def execute(self, state) -> dict:
        """
         주어진 상태(state)에서 query를 추출하여
         이미지 생성 체인에 전달하고, 결과를 응답으로 반환합니다.

         Args:
             state: 현재 워크플로우 상태

         Returns:
             dict: 생성된 이미지 정보가 포함된 응답
         """
         # 실제 구현은 추후 개발 시 추가
        generated_image = self.graph.invoke(
              {
                   "purpose": "앨범 제작",
                    "text": "마침 주말 해가 밝아와 부를 사람 하나 없지만 꺼놓은 radio 를 틀고 이 작은 city (CD) 안에 꼬인 테이프 내 맘을 달래주는 노래네 시계 소리마저 멜로딘걸 oh"
             }
         )

#         # 더미 응답 생성
#         dummy_response = "이미지 생성 기능은 아직 구현되지 않았습니다."

#         # 응답 반환
#         return {"response": dummy_response}
