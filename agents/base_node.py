from abc import ABC, abstractmethod


class BaseNode(ABC):
    """
    모든 노드의 기본 클래스입니다. LangGraph Workflow에서 사용되는 노드의 기본 구조를 정의합니다.

    이 추상 클래스는 모든 노드가 구현해야 하는 기본 메서드와 속성을 정의합니다.
    노드는 LangGraph의 상태 그래프에서 작업을 수행하는 개별 단위입니다.

    예시:
    ```python
    class MyCustomNode(BaseNode):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            # 추가 초기화 코드

        def execute(self, state) -> dict:
            # 상태를 처리하는 로직
            result = process_state(state)
            return {"output_key": result}
    ```
    """

    def __init__(self, **kwargs):
        """
        노드 초기화 메서드

        Args:
            **kwargs: 키워드 인자
                - verbose (bool): 로깅 활성화 여부 (기본값: False)
        """
        self.name = self.__class__.__name__  # 노드 이름은 클래스 이름으로 자동 설정
        self.verbose = kwargs.get("verbose", False)  # 상세 로깅 활성화 여부

    @abstractmethod
    def execute(self, state) -> dict:
        """
        노드의 주요 실행 로직을 구현하는 추상 메서드

        모든 하위 클래스는 이 메서드를 반드시 구현해야 합니다.

        Args:
            state: 현재 그래프 상태 객체

        Returns:
            dict: 업데이트된 상태 값을 포함하는 딕셔너리
        """
        pass

    def logging(self, method_name, **kwargs):
        """
        노드 실행 과정의 로깅을 처리하는 메서드 (로깅이 필요할 때만 사용하시면 됩니다.)
        보통은 LangSmith에서 추적 확인 가능합니다.

        Args:
            method_name (str): 로깅할 메서드 이름
            **kwargs: 로깅할 추가 정보
        """
        if self.verbose:
            print(f"[{self.name}] {method_name}")  # 노드 이름과 메서드 이름 출력
            for key, value in kwargs.items():
                print(f"{key}: {value}")  # 추가 정보 출력

    def __call__(self, state):
        """
        노드를 함수처럼 호출 가능하게 만드는 메서드

        LangGraph에서 노드를 직접 호출할 때 사용됩니다.

        Args:
            state: 현재 그래프 상태 객체

        Returns:
            dict: execute 메서드의 결과
        """
        return self.execute(state)
