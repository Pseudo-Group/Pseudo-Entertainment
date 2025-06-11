"""
노드 클래스 모듈

해당 클래스 모듈은 각각 노드 클래스가 BaseNode를 상속받아 노드 클래스를 구현하는 모듈입니다.
"""

from agents.base_node import BaseNode
from agents.music.modules.prompts import get_lyric_template
from agents.music.modules.state import MusicState
from agents.music.modules.models import get_openai_model

class LyricGenerationNode(BaseNode):
    """
    가사 생성 노드
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = get_openai_model()
    
    def execute(self, state: MusicState) -> dict:
        """
        가사 생성 노드 실행
        """
        self.logging("execute", input_state=state)
        prompt = get_lyric_template().format(query=state["query"])
        response = self.model.invoke(prompt)
        return {"response": response, "query": state["query"]}

    def __call__(self, state: MusicState) -> dict:
        """
        노드를 함수처럼 호출 가능하게 만드는 메서드
        """
        return self.execute(state)
    
        


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
