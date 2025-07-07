import os

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from agents.text.modules.models import get_openai_model


async def scrape_news(scraping_query: str) -> str:
    """
    비동기적으로 뉴스 스크래핑 MCP 서버에 요청을 보내고, 응답을 반환합니다.
    """

    server_params = StdioServerParameters(
        command="uv",
        args=["--directory", "agents/text/mcp/", "run", "mcp_news_server.py"],
        env=os.environ,
    )

    async with stdio_client(server=server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)
            print("사용 가능한 도구:", tools)

            graph = create_react_agent(model=get_openai_model(), tools=tools)

            response = await graph.ainvoke({"messages": scraping_query})

            if "messages" in response:
                messages = response["messages"]
                for message in messages:
                    if hasattr(message, "content") and message.content:
                        last_content = message.content
                        break

            return last_content
