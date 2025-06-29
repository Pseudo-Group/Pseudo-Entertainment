import os

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from agents.management.modules.models import get_openai_model


async def verify_instagram_content(
    content_text: str, content_type: str = "text"
) -> str:
    """
    비동기적으로 인스타그램 컨텐츠 검증 MCP 서버에 요청을 보내고, 응답을 반환합니다.
    """

    server_params = StdioServerParameters(
        command="uv",
        args=[
            "--directory",
            "agents/management/mcp/",
            "run",
            "mcp_contents_verify_server.py",
        ],
        env=os.environ,
    )

    async with stdio_client(server=server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)
            print("사용 가능한 도구:", tools)

            graph = create_react_agent(model=get_openai_model(), tools=tools)

            query = f"다음 인스타그램 컨텐츠를 검증해주세요: {content_text} (유형: {content_type})"
            response = await graph.ainvoke({"messages": query})

            if "messages" in response:
                messages = response["messages"]
                for message in messages:
                    if hasattr(message, "content") and message.content:
                        last_content = message.content
                        break

            return last_content


async def search_instagram_policies(keywords: str) -> str:
    """
    비동기적으로 인스타그램 정책 검색 MCP 서버에 요청을 보내고, 응답을 반환합니다.
    """

    server_params = StdioServerParameters(
        command="uv",
        args=[
            "--directory",
            "agents/management/mcp/",
            "run",
            "mcp_contents_verify_server.py",
        ],
        env=os.environ,
    )

    async with stdio_client(server=server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)
            print("사용 가능한 도구:", tools)

            graph = create_react_agent(model=get_openai_model(), tools=tools)

            query = f"다음 키워드로 인스타그램 정책을 검색해주세요: {keywords}"
            response = await graph.ainvoke({"messages": query})

            if "messages" in response:
                messages = response["messages"]
                for message in messages:
                    if hasattr(message, "content") and message.content:
                        last_content = message.content
                        break

            return last_content


async def analyze_content_risks(content_text: str) -> str:
    """
    비동기적으로 컨텐츠 위험 분석 MCP 서버에 요청을 보내고, 응답을 반환합니다.
    """

    server_params = StdioServerParameters(
        command="uv",
        args=[
            "--directory",
            "agents/management/mcp/",
            "run",
            "mcp_contents_verify_server.py",
        ],
        env=os.environ,
    )

    async with stdio_client(server=server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)
            print("사용 가능한 도구:", tools)

            graph = create_react_agent(model=get_openai_model(), tools=tools)

            query = f"다음 컨텐츠의 위험 요소를 분석해주세요: {content_text}"
            response = await graph.ainvoke({"messages": query})

            if "messages" in response:
                messages = response["messages"]
                for message in messages:
                    if hasattr(message, "content") and message.content:
                        last_content = message.content
                        break

            return last_content
