"""
collect_comments 패키지 초기화 모듈

이 모듈은 collect_comments Workflow를 외부에 노출시키는 역할을 합니다.
"""

from agents.collect_comments.workflow import collect_comments_workflow

__all__ = ["collect_comments_workflow"]


"""
comments_workflow를 실행할 때, 기본적으로 게시물이 6개 이하라면 정상적으로 반복 실행되며 종료됩니다.
하지만 게시물 수가 6개를 초과할 경우, workflow는 최대 6번까지만 실행되고 중단됩니다.

이 문제를 해결하려면 invoke 메서드를 사용하고,
config 옵션으로 recursion_limit 값을 충분히 크게 설정하면
게시물 끝까지 모든 반복을 실행할 수 있습니다.

예시:
from .modules.state import CollectCommentsState
compiled = collect_comments_workflow()
result = compiled.invoke(
    CollectCommentsState(profile_url="https://instagram.com/rozy.gram/"),
    config={"recursion_limit": 50}
)

다만, invoke()를 사용하면 끝까지 실행되지만 LangSmith 대시보드에서 워크플로우의 실행 과정을 실시간으로 모니터링할 수 없습니다.
"""
