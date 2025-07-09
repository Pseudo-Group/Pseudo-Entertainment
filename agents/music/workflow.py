"""
음악 관련 콘텐츠 생성을 위한 Workflow 모듈

이 모듈은 음악 기반 콘텐츠 생성을 위한 Workflow를 정의합니다.
StateGraph를 사용하여 음악 처리를 위한 워크플로우를 구축합니다.
"""

from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from agents.base_workflow import BaseWorkflow
from agents.music.modules.state import MusicState
from agents.music.modules.nodes import LyricGenerationNode, DiaryGenerationNode, YoutubeSearchNode, YoutubeAnalysisNode, WeatherGenerationNode

class MusicWorkflow(BaseWorkflow):
    """
    음악 관련 콘텐츠 생성을 위한 Workflow 클래스

    이 클래스는 음악 기반 콘텐츠 생성을 위한 Workflow를 정의합니다.
    BaseWorkflow를 상속받아 기본 구조를 구현하고, MusicState를 사용하여 상태를 관리합니다.
    """

    def __init__(self, state):
        super().__init__()
        self.state = state

    def build(self) -> CompiledStateGraph:
        """
        음악 Workflow 그래프 구축 메서드

        StateGraph를 사용하여 음악 처리를 위한 Workflow 그래프를 구축합니다.
        현재는 음악 생성 노드를 포함하고 있으며, 추후 조건부 에지를 추가하여
        다양한 경로를 가진 Workflow를 구축할 수 있습니다.

        Returns:
            CompiledStateGraph: 컴파일된 상태 그래프 객체
        """
        builder = StateGraph(self.state)
        

        # 노드 생성 및 연결결
        builder.add_node("diary_generation", DiaryGenerationNode())
        builder.add_node("weather_generation", WeatherGenerationNode())
        builder.add_edge("__start__", "diary_generation")
        builder.add_edge("__start__", "weather_generation")

        builder.add_node("youtube_search", YoutubeSearchNode())
        builder.add_node("youtube_analysis", YoutubeAnalysisNode())
        builder.add_edge("diary_generation", "youtube_search")
        builder.add_edge("youtube_search", "youtube_analysis")

        builder.add_node("lyric_generation", LyricGenerationNode())
        builder.add_edge(["youtube_analysis", "weather_generation"], "lyric_generation")
        builder.add_edge("lyric_generation", "__end__")

        workflow = builder.compile()  # 그래프 컴파일
        workflow.name = self.name  # Workflow 이름 설정

        return workflow


if __name__ == "__main__":
    diary_query = input("일기 생성용 입력: ")
    lyric_query = input("가사 생성용 입력: ")

    music_workflow = MusicWorkflow(MusicState)
    graph = music_workflow.build()

    graph.invoke({
        "diary_query": diary_query,
        "lyric_query": lyric_query
    })
    
