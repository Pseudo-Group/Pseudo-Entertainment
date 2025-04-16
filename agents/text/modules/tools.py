"""
도구(Tools) 모듈

이 모듈은 LangGraph Workflow에서 사용할 수 있는 다양한 도구를 정의합니다.
도구는 LLM이 외부 시스템과 상호작용하거나 특정 작업을 수행할 수 있도록 해주는 함수들입니다.

현재는 주석 처리된 예시 코드만 포함되어 있으며, 필요에 따라 실제 구현을 추가할 수 있습니다.
아래 예시 코드는 Tavily API를 사용하여 웹 검색을 수행하는 도구를 보여줍니다.

추후 개발 시 다음과 같은 다양한 도구를 구현하여 추가할 수 있습니다:
- 웹 스크래핑 도구: 웹사이트에서 정보 추출
- 데이터베이스 조회 도구: 데이터베이스에서 정보 검색 및 조회
- API 호출 도구: 외부 API와 통합
- 파일 조작 도구: 파일 읽기, 쓰기, 생성 등
- 이미지 처리 도구: 이미지 분석 및 생성
"""

# from typing import Any, Callable, List, Optional, cast

# from langchain_community.tools.tavily_search import TavilySearchResults
# from langchain_core.runnables import RunnableConfig
# from langchain_core.tools import InjectedToolArg
# from typing_extensions import Annotated

# from react_agent.configuration import Configuration


# async def search(
#     query: str, *, config: Annotated[RunnableConfig, InjectedToolArg]
# ) -> Optional[list[dict[str, Any]]]:
#     """
#     일반 웹 결과를 검색합니다.

#     이 함수는 Tavily 검색 엔진을 사용하여 검색을 수행합니다. 이 엔진은 포괄적이고 정확하며 신뢰할 수 있는 결과를 제공하도록 설계되었습니다. 특히 현재 이벤트에 대한 질문에 대답하는 데 유용합니다.
#     """
#     configuration = Configuration.from_runnable_config(config)
#     wrapped = TavilySearchResults(max_results=configuration.max_search_results)
#     result = await wrapped.ainvoke({"query": query})
#     return cast(list[dict[str, Any]], result)


# TOOLS: List[Callable[..., Any]] = [search]
