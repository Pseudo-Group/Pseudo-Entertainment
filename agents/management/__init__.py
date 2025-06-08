"""
Management 패키지 초기화 모듈

이 모듈은 Management Workflow를 외부에 노출시키는 역할을 합니다.
"""

from agents.management.workflow import management_workflow

__all__ = ["management_workflow"]
