#!/usr/bin/env python3
"""
환경변수 및 tools 테스트
"""

import os

# .env 파일 로드 테스트
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ dotenv 로드 성공")
except ImportError:
    print("❌ python-dotenv 없음")

print(f"TAVILY_API_KEY: '{os.getenv('TAVILY_API_KEY')}'")
print(f"LANGSMITH_API_KEY: '{os.getenv('LANGSMITH_API_KEY')}'")

# tools 함수 테스트
try:
    from agents.management.modules.tools import get_tavily_search_tool
    tool = get_tavily_search_tool()
    print(f"✅ Tool 생성 성공: {tool.name}")
    
    # 테스트 검색
    result = tool.invoke("테스트 검색")
    print(f"✅ 검색 테스트 결과: {result}")
    
except Exception as e:
    print(f"❌ 오류: {e}")
    import traceback
    traceback.print_exc() 