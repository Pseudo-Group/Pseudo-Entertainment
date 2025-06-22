"""
Management Workflow 테스트 스크립트

이 스크립트는 management 워크플로우를 직접 실행하여 테스트합니다.
웹 UI 없이 로컬에서 직접 실행할 수 있습니다.
"""

import os
import sys
from dotenv import load_dotenv

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.abspath('.')
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# .env 파일 로드
load_dotenv()

# 환경 변수 확인
print("=== 환경 변수 확인 ===")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')[:20]}...")
print(f"TAVILY_API_KEY: {os.getenv('TAVILY_API_KEY')[:20] if os.getenv('TAVILY_API_KEY') else 'Not set'}")

from agents.management.modules.state import ManagementState
from agents.management.modules.nodes import WebSearchNode, ResourceManagementNode
from agents.management.workflow import ManagementWorkflow


def test_individual_nodes():
    """개별 노드 테스트"""
    print("\n=== 개별 노드 테스트 ===")
    
    # 웹 검색 노드 테스트
    web_search_node = WebSearchNode()
    
    # 초기 상태 생성
    test_state = {
        "project_id": "PRJ-2024-001",
        "request_type": "resource_allocation",
        "query": "아이유 콘서트 기획",
        "response": [],
        "team_members": ["기획팀", "마케팅팀", "기술팀"],
        "resources_available": {"budget": "5억원", "venue": "올림픽공원"}
    }
    
    print("\n1. 웹 검색 노드 실행")
    search_result = web_search_node.execute(test_state)
    print(f"검색 결과: {search_result}")
    
    # 검색 결과를 상태에 추가
    test_state["search_results"] = search_result.get("search_results", "검색 결과 없음")
    
    # 리소스 관리 노드 테스트
    resource_node = ResourceManagementNode()
    
    print("\n2. 리소스 관리 노드 실행")
    resource_result = resource_node.execute(test_state)
    print(f"\n리소스 계획:\n{resource_result['response'][:500]}...")


def test_full_workflow():
    """전체 워크플로우 테스트"""
    print("\n\n=== 전체 워크플로우 테스트 ===")
    
    # ManagementWorkflow 인스턴스 생성
    workflow = ManagementWorkflow()
    
    # 워크플로우 컴파일
    compiled_workflow = workflow.build()
    
    # 워크플로우 실행을 위한 입력 데이터
    workflow_input = {
        "project_id": "PRJ-2024-002",
        "request_type": "team_management",
        "query": "신규 드라마 제작팀 구성",
        "response": [],
        "team_members": ["PD", "작가", "촬영감독"],
        "resources_available": {
            "budget": "100억원",
            "duration": "6개월",
            "location": "서울 및 부산"
        }
    }
    
    print(f"\n입력 데이터:")
    print(f"- 프로젝트 ID: {workflow_input['project_id']}")
    print(f"- 요청 유형: {workflow_input['request_type']}")
    print(f"- 쿼리: {workflow_input['query']}")
    
    # 워크플로우 실행
    result = compiled_workflow.invoke(workflow_input)
    
    print("\n=== 최종 결과 ===")
    print(f"프로젝트 ID: {result['project_id']}")
    print(f"요청 유형: {result['request_type']}")
    print(f"\n리소스 계획:\n{result.get('response', '응답 없음')}")


def test_streaming_mode():
    """스트리밍 모드 테스트"""
    print("\n\n=== 스트리밍 모드 테스트 ===")
    
    workflow = ManagementWorkflow()
    compiled_workflow = workflow.build()
    
    streaming_input = {
        "project_id": "STREAM-2024-001",
        "request_type": "resource_allocation",
        "query": "넷플릭스 시리즈 제작",
        "response": [],
        "team_members": ["총괄 PD", "각본가", "캐스팅 디렉터"],
        "resources_available": {
            "budget": "200억원",
            "episodes": "8부작",
            "platform": "Netflix"
        }
    }
    
    print("워크플로우 실행 중...")
    for event in compiled_workflow.stream(streaming_input):
        for node_name, node_output in event.items():
            print(f"\n[{node_name}] 실행 중...")
            if isinstance(node_output, dict):
                for key, value in node_output.items():
                    if key == "response" and value:
                        print(f"응답 생성 중: {value[:200]}...")
                    elif key == "search_results":
                        print(f"검색 완료: {value[:100]}...")


def test_various_scenarios():
    """다양한 시나리오 테스트"""
    print("\n\n=== 다양한 시나리오 테스트 ===")
    
    workflow = ManagementWorkflow()
    compiled_workflow = workflow.build()
    
    scenarios = [
        {
            "name": "음악 앨범 제작",
            "input": {
                "project_id": "MUSIC-2024-IU",
                "request_type": "resource_allocation",
                "query": "아이유 새 앨범 제작을 위한 리소스 계획",
                "response": [],
                "team_members": ["프로듀서", "작곡가", "편곡자", "엔지니어"],
                "resources_available": {
                    "budget": "20억원",
                    "studio": "서울 스튜디오 A, B",
                    "timeline": "3개월"
                }
            }
        },
        {
            "name": "팬미팅 이벤트",
            "input": {
                "project_id": "EVENT-2024-FM",
                "request_type": "creator_development",
                "query": "아이유 글로벌 팬미팅 투어 계획",
                "response": [],
                "team_members": ["이벤트 기획팀", "보안팀", "통역팀"],
                "resources_available": {
                    "budget": "30억원",
                    "cities": "서울, 도쿄, 방콕, 홍콩",
                    "duration": "2주"
                }
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        result = compiled_workflow.invoke(scenario['input'])
        print(f"결과: {result.get('response', '응답 없음')[:500]}...")


if __name__ == "__main__":
    print("Management Workflow 테스트 시작\n")
    
    # 개별 노드 테스트
    test_individual_nodes()
    
    # 전체 워크플로우 테스트
    test_full_workflow()
    
    # 스트리밍 모드 테스트
    test_streaming_mode()
    
    # 다양한 시나리오 테스트
    test_various_scenarios()
    
    print("\n\n테스트 완료!")
