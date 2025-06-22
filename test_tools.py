#!/usr/bin/env python3
"""
Tools 테스트 파일
"""

import os
from dotenv import load_dotenv

load_dotenv()


print("TAVILY_API_KEY:", os.getenv("TAVILY_API_KEY"))

try:
    from agents.management.modules.tools import get_tavily_search_tool
    print("✅ tools import 성공")
    
    tool = get_tavily_search_tool()
    print("✅ tool 생성 성공:", type(tool))
    print("Tool name:", tool.name)
    print("Tool description:", tool.description)
    
except Exception as e:
    print("❌ 오류 발생:", str(e))
    import traceback
    traceback.print_exc() 