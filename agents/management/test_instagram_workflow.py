"""
인스타그램 API 워크플로우 테스트 스크립트
"""

import os
import sys
import schedule
import time
from dotenv import load_dotenv

load_dotenv(override=True)
# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.management.workflow import management_workflow
from agents.management.modules.state import ManagementState

ACCESS_TOKEN = os.environ.get("INSTAGRAM_API_KEY")
USER_ID = "17841451140542851"

run_count = 0  # 전역 실행 카운터

def test_instagram_workflow():
    global run_count
    run_count += 1
    print(f"\n===== {run_count}번째 실행 =====")
    """
    인스타그램 워크플로우를 테스트합니다.
    """
    # 인스타그램 API 인증 정보 (실제 값으로 교체 필요)
    access_token = ACCESS_TOKEN  # 실제 액세스 토큰으로 교체
    user_id = USER_ID  # 실제 사용자 ID로 교체
    
    # 초기 상태 설정
    initial_state = {
        "access_token": access_token,
        "user_id": user_id,
        "comment_file_path": "instagram_data.json",
        "comment_analysis_file_path": "instagram_data_analysis.json",
        "json_data": None,  # JSON 파일에 저장할 데이터
        "response": []
    }
    
    try:
        # 워크플로우 실행
        print("인스타그램 워크플로우를 시작합니다...")
        
        # 워크플로우 빌드
        workflow = management_workflow.build()
        
        # 워크플로우 실행
        result = workflow.invoke(initial_state)
        
        # 결과 출력
        print("\n=== 워크플로우 실행 결과 ===")
        for message in result.get("response", []):
            if hasattr(message, 'content'):
                print(f"응답: {message.content}")
            else:
                print(f"응답: {message}")
        
        # 상태 정보 출력
        print(f"\n=== 상태 정보 ===")
        print(f"미디어 데이터 개수: {len(result.get('media_data', []))}")
        print(f"첫 번째 미디어 ID: {result.get('first_media_id')}")
        print(f"현재 댓글 수: {result.get('current_comments_count')}")
        print(f"이전 댓글 수: {result.get('previous_comments_count')}")
        print(f"변경 여부: {result.get('has_changes')}")
        
        if result.get('comments_data'):
            print(f"댓글 데이터 개수: {len(result.get('comments_data', []))}")
        
        # API 오류 체크
        response_text = str(result.get("response", []))
        if "API 요청에 실패했습니다" in response_text or "Invalid OAuth access token" in response_text:
            print(f"\n⚠️  API 오류가 발생했습니다. 토큰을 확인해주세요.")
            print(f"   - 토큰이 만료되었을 수 있습니다.")
            print(f"   - 토큰이 올바른지 확인해주세요.")
            print(f"   - 인스타그램 API 권한을 확인해주세요.")
        
    except Exception as e:
        print(f"워크플로우 실행 중 오류 발생: {str(e)}")


# def test_subsequent_runs():
#     """
#     두 번째 실행부터의 워크플로우를 테스트합니다.
#     """
#     # 인스타그램 API 인증 정보 (실제 값으로 교체 필요)
#     access_token = ACCESS_TOKEN  # 실제 액세스 토큰으로 교체
#     user_id = USER_ID  # 실제 사용자 ID로 교체
    
#     # 초기 상태 설정
#     initial_state = {
#         "access_token": access_token,
#         "user_id": user_id,
#         "json_file_path": "instagram_data.json",
#         "json_data": None,  # JSON 파일에 저장할 데이터
#         "response": []
#     }
    
#     try:
#         # 워크플로우 실행
#         print("두 번째 실행: 댓글 수 변경 확인...")
        
#         # 워크플로우 빌드
#         workflow = management_workflow.build()
        
#         # 워크플로우 실행
#         result = workflow.invoke(initial_state)
        
#         # 결과 출력
#         print("\n=== 두 번째 실행 결과 ===")
#         for message in result.get("response", []):
#             if hasattr(message, 'content'):
#                 print(f"응답: {message.content}")
#             else:
#                 print(f"응답: {message}")
        
#         # 상태 정보 출력
#         print(f"\n=== 상태 정보 ===")
#         print(f"현재 댓글 수: {result.get('current_comments_count')}")
#         print(f"이전 댓글 수: {result.get('previous_comments_count')}")
#         print(f"변경 여부: {result.get('has_changes')}")
        
#         if result.get('comments_data'):
#             print(f"댓글 데이터 개수: {len(result.get('comments_data', []))}")
        
#     except Exception as e:
#         print(f"워크플로우 실행 중 오류 발생: {str(e)}")


def run_scheduler():
    # 10분마다 워크플로우 실행
    schedule.every(1).minutes.do(test_instagram_workflow)
    # 또는 매 1시간마다: schedule.every().hour.do(test_instagram_workflow)

    print("스케줄러가 시작되었습니다. (Ctrl+C로 종료)")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # run_scheduler() 
    test_instagram_workflow()