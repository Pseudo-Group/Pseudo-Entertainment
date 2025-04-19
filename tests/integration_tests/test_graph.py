"""
통합 테스트 모듈 - 그래프 테스트

이 모듈은 LangGraph Workflow의 통합 테스트를 수행합니다.
전체 그래프가 예상대로 작동하는지 확인하기 위한 테스트 케이스를 포함합니다.

통합 테스트는 여러 컴포넌트가 함께 작동하는 방식을 검증하며,
실제 사용 사례와 유사한 시나리오에서 시스템을 테스트합니다.

이 테스트는 LangSmith의 unit 데코레이터를 사용하여 테스트 실행을 추적하고 기록합니다.
"""

import pytest
from langsmith import unit

from agents import main_workflow


@pytest.mark.asyncio
@unit
async def test_agent_simple_passthrough() -> None:
    """
    에이전트 그래프의 기본 패스스루 기능을 테스트합니다.

    이 테스트는 그래프가 입력 값을 올바르게 처리하고 결과를 반환하는지 확인합니다.
    간단한 입력 딕셔너리를 그래프에 전달하고 결과가 None이 아닌지 검증합니다.

    테스트 단계:
    1. 그래프에 간단한 입력 값 전달
    2. 결과가 None이 아닌지 확인

    Returns:
        None
    """
    # 그래프에 간단한 입력 값 전달
    res = await main_workflow().ainvoke({"response": "some_val"})
    # 결과가 None이 아닌지 확인
    assert res is not None
