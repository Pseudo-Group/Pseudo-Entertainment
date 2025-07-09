"""
노드 클래스 모듈

해당 클래스 모듈은 각각 노드 클래스가 BaseNode를 상속받아 노드 클래스를 구현하는 모듈입니다.
"""

from agents.base_node import BaseNode
from agents.music.modules.prompts import get_lyric_template, get_diary_template, get_query_extraction_template, get_youtube_query_template, get_youtube_analysis_template
from agents.music.modules.state import MusicState
from agents.music.modules.models import get_openai_model, get_gemini_client, get_youtube_client
from agents.music.modules.tools.weather import WeatherService
from googleapiclient.discovery import build
from google import genai


class DiaryGenerationNode(BaseNode):
    """
    일기 생성 노드
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = get_openai_model()

    def execute(self, state) -> dict:
        """
        일기 생성 노드 실행
        """
        self.logging("execute", input_state=state)
        first_prompt = get_diary_template().format(query=state["diary_query"])
        diary_topic_response = self.model.invoke(first_prompt)
        diary_topic_response = diary_topic_response.text()
        
        second_prompt = get_query_extraction_template().format(query=state["diary_query"])
        messages = [
            {
                "role" : "user",
                "content" : first_prompt,
            },
            {
                "role" : "assistant",
                "content" : diary_topic_response,
            },
            {
                "role" : "user",
                "content" : second_prompt,
            }
        ]
        query_response = self.model.invoke(messages)
        query_response = query_response.text()
        
        return {"youtube_query" : query_response}

    def __call__(self, state):
        """
        노드를 함수처럼 호출 가능하게 만드는 메서드
        """
        return self.execute(state)


class YoutubeSearchNode(BaseNode):
    """
    유튜브 영상을 찾는 노드
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = get_youtube_client()

    def execute(self, state : MusicState) -> dict:
        """
        유튜브 영상 검색 노드 실행
        """
        self.logging("execute", input_state = state)
        prompt = state["youtube_query"]
        max_results = 1

        search_response = self.model.search().list(
            q = prompt,
            part = "id", #영상 식별만 하면 돼서 id로 검색
            type = "video", # 영상만 검색
            order = "relevance", # 관련성 기준으로 정렬
            maxResults = max_results
        ).execute()

        videos = []
        # 검색 결과 파싱
        for item in search_response.get('items', []):
            video_id = str(item['id']['videoId'])
            videos.append("https://www.youtube.com/watch?v=" + video_id)
        
        return {"video_url" : videos[0]}

    def __call__(self, state):
        """
        노드를 함수처럼 호출 가능하게 만드는 메서드
        """
        return self.execute(state)


class YoutubeAnalysisNode(BaseNode):
    """
    유튜브 영상을 분석하는 노드
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = get_gemini_client()

    def execute(self, state : MusicState) -> dict:
        """
        유튜브 영상 분석 노드 실행
        """
        self.logging("execute", input_state = state)
        prompt = get_youtube_analysis_template().format(query=state["diary_query"])
        video_link = state["video_url"]
        response = self.model.models.generate_content(
            model='models/gemini-2.0-flash',
            contents = genai.types.Content(
            parts = [
                genai.types.Part(
                    file_data = genai.types.FileData(file_uri = video_link)
                    ),
                    genai.types.Part(text = prompt)
                ]
            )
        )

        return {"video_analysis" : response.text}

    def __call__(self, state):
        """
        노드를 함수처럼 호출 가능하게 만드는 메서드
        """
        return self.execute(state)
    

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
        prompt = get_lyric_template().format(
            query=state["lyric_query"], 
            weather_info=state["weather_info"], 
            video_analysis=state["video_analysis"]
        )
        response = self.model.invoke(prompt)
        return {"response": response, "query": state["lyric_query"]}

    def __call__(self, state: MusicState) -> dict:
        """
        노드를 함수처럼 호출 가능하게 만드는 메서드
        """
        return self.execute(state)
    

class WeatherGenerationNode(BaseNode):
    """
    날씨 정보 생성 노드
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.weather_service = WeatherService()

    def execute(self, state: MusicState) -> dict:
        """
        날씨 정보 생성 노드 실행
        """
        self.logging("execute", input_state=state)
        
        # 날씨 정보 가져오기
        weather_info = self.weather_service.get_current_weather() 
        return {"weather_info": weather_info}

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
