#!/usr/bin/env python3
"""
Import 테스트 파일
"""

try:
    # 메인 workflow 테스트
    from agents.workflow import main_workflow
    print("✅ main_workflow import 성공")
except Exception as e:
    print(f"❌ main_workflow import 실패: {e}")

try:
    # management workflow 테스트
    from agents.management.workflow import management_workflow
    print("✅ management_workflow import 성공")
except Exception as e:
    print(f"❌ management_workflow import 실패: {e}")

try:
    # management 모듈 전체 테스트
    from agents.management import management_workflow
    print("✅ management 모듈에서 management_workflow import 성공")
except Exception as e:
    print(f"❌ management 모듈에서 import 실패: {e}")

print("🎉 모든 테스트 완료!") 