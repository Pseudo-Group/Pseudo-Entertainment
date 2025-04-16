"""
노드 클래스 모듈

해당 클래스 모듈은 각각 노드 클래스가 BaseNode를 상속받아 노드 클래스를 구현하는 모듈입니다.
"""

from agents.base_node import BaseNode
# from agents.music.modules.chains import set_music_generation_chain

# class MusicGenerationNode(BaseNode):
#     """
#     음악 장르와 분위기에 적합한 음악을 생성하는 노드
#     """

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)  # BaseNode 초기화
#         self.chain = set_music_generation_chain()  # 음악 생성 체인 설정

#     def execute(self, state) -> dict:
#         """
#         주어진 상태(state)에서 music_genre와 music_mood를 추출하여
#         음악 생성 체인에 전달하고, 결과를 응답으로 반환합니다.
        
#         Args:
#             state: 현재 워크플로우 상태
            
#         Returns:
#             dict: 생성된 음악 정보가 포함된 응답
#         """
#         # 음악 생성 체인 실행
#         generated_music = self.chain.invoke(
#             {
#                 "music_genre": state["music_genre"],  # 음악 장르
#                 "music_mood": state["music_mood"],    # 음악 분위기
#             }
#         )

#         # 생성된 음악 정보를 응답으로 반환
#         return {"response": generated_music}
