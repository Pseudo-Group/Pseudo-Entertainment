"""
Management 패키지 초기화 모듈

이 모듈은 Management Workflow를 외부에 노출시키는 역할을 합니다.
"""

# .env 파일 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv가 없어도 계속 진행

from .workflow import management_workflow

__all__ = ["management_workflow"]
