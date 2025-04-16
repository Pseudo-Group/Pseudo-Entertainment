from abc import ABC, abstractmethod

from langgraph.graph.state import CompiledStateGraph


class BaseWorkflow(ABC):
    """
    모든 Workflow의 기본 클래스입니다. LangGraph Workflow의 기본 구조를 정의합니다.

    이 추상 클래스는 모든 Workflow가 구현해야 하는 기본 메서드와 속성을 정의합니다.
    Workflow는 여러 노드를 연결하여 작업을 수행하는 전체 그래프를 관리합니다.

    예시:
    ```python
    # 이 클래스를 상속받은 클래스로 인스턴스 생성하는 방법
    name_workflow = NameWorkflow(StateName)
    ```
    """

    def __init__(self):
        """
        Workflow 초기화 메서드

        Workflow 이름을 클래스 이름으로 자동 설정합니다.
        """
        self.name = self.__class__.__name__  # Workflow 이름은 클래스 이름으로 자동 설정

    @abstractmethod
    def build(self) -> CompiledStateGraph:
        """
        Workflow 그래프를 구축하는 추상 메서드

        모든 하위 클래스는 이 메서드를 반드시 구현해야 합니다.
        이 메서드에서는 노드를 추가하고, 에지를 연결하여 Workflow 그래프를 구축합니다.

        Returns:
            CompiledStateGraph: 컴파일된 상태 그래프 객체
        """
        pass

    def __call__(self):
        """
        Workflow를 함수처럼 호출 가능하게 만드는 메서드

        Workflow 객체를 직접 호출할 때 사용됩니다.

        Returns:
            CompiledStateGraph: build 메서드의 결과
        """
        return self.build()
