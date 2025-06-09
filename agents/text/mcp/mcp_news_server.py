import os
from datetime import date, timedelta

from mcp.server.fastmcp import FastMCP
from newsapi import NewsApiClient

from agents.text.mcp.mcp_config_loader import mcp_config

news_mcp = FastMCP(
    name="news",
    instructions=(
        "Act as a news-scraping assistant that, given today's date, finds today's news for Instagram text content."
    ),
    host=mcp_config.news_host,
    port=mcp_config.news_port,
)

news_api = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))


@news_mcp.tool()
async def find_news(keywords: str) -> list[dict]:
    """
    키워드를 기반으로 뉴스 기사를 찾습니다.

    Args:
        keywords (str): 검색할 뉴스 기사 키워드

    Returns:
        list[dict]: 뉴스 기사 목록 (최대 5개)
    """
    from_date = (date.today() - timedelta(days=7)).isoformat()  # 7일 전까지만 기사 검색

    news: list[dict] = news_api.get_everything(
        q=keywords,
        from_param=from_date,
        sort_by="popularity",  # 인기도 순으로 정렬
    )["articles"]

    return news[:5]  # 상위 5개 기사만 반환


if __name__ == "__main__":
    print(
        f"news MCP server is running on {mcp_config.news_host}:{mcp_config.news_port}"
    )

    news_mcp.run(transport=mcp_config.news_transport)
