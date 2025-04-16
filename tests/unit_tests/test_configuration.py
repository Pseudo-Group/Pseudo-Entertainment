"""
단위 테스트 모듈 - 구성 테스트

이 모듈은 에이전트 구성 클래스의 단위 테스트를 수행합니다.
개별 컴포넌트의 기능이 예상대로 작동하는지 확인하기 위한 테스트 케이스를 포함합니다.

단위 테스트는 코드의 가장 작은 단위(함수, 클래스, 메서드 등)가 올바르게 작동하는지 검증합니다.
단위 테스트는 외부 의존성을 최소화하고 테스트 실행 속도를 최대화하도록 설계됩니다.
"""

from agent.configuration import Configuration


def test_configuration_empty() -> None:
    """
    빈 구성으로 Configuration 객체를 생성하는 테스트

    이 테스트는 Configuration 클래스가 빈 구성 데이터로도 올바르게 초기화되는지 확인합니다.
    빈 딕셔너리를 전달하여 from_runnable_config 메서드가 예외를 발생시키지 않고
    기본값으로 올바르게 초기화되는지 테스트합니다.

    테스트 단계:
    1. 빈 딕셔너리를 사용하여 Configuration 객체 생성
    2. 예외가 발생하지 않으면 테스트 통과

    Returns:
        None
    """
    # 빈 딕셔너리로 Configuration 객체 생성
    # 예외가 발생하지 않으면 테스트 통과
    Configuration.from_runnable_config({})
