"""
인스타그램 API 워크플로우를 위한 노드 클래스 모듈

해당 클래스 모듈은 각각 노드 클래스가 BaseNode를 상속받아 노드 클래스를 구현하는 모듈입니다.
"""

import json
import os
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from datetime import datetime

from agents.base_node import BaseNode
from agents.management.modules.state import ManagementState
from agents.management.modules.prompts import get_instagram_comment_analysis_prompt

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv(override=True)

class InstagramMediaFetchNode(BaseNode):
    """
    인스타그램 미디어 정보를 가져오는 노드
    """

    def execute(self, state: ManagementState) -> Dict[str, Any]:
        """
        인스타그램 API를 통해 미디어 정보를 가져오거나 JSON 파일에서 읽어옵니다.
        댓글 수 변경을 감지하고 상태를 업데이트합니다.
        """
        print(f"🔍 [InstagramMediaFetchNode] 실행 중...")
        
        json_file_path = state["comment_file_path"]
        access_token = state["access_token"]
        user_id = state["user_id"]
        
        # JSON 파일에서 이전 데이터 읽기
        previous_data = None
        if os.path.exists(json_file_path):
            try:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    previous_data = json.load(f)
                print(f"📁 [InstagramMediaFetchNode] JSON 파일에서 이전 데이터를 읽어왔습니다.")
                # print(f"first_media_id: {previous_data['first_media_id']} / previous_comments_count: {previous_data['previous_comments_count']}")
            except Exception as e:
                print(f"JSON 파일 읽기 오류: {str(e)}")
        
        # Instagram API에서 최신 미디어 데이터 가져오기
        print(f"📡 [InstagramMediaFetchNode] Instagram API에서 미디어 데이터를 가져오는 중...")
        
        # 요청할 필드 지정
        fields = 'id,caption,media_type,timestamp,username,like_count,comments_count'
        
        url = f'https://graph.instagram.com/v23.0/{user_id}/media?access_token={access_token}'
        params = {
            'fields': fields,
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                media_data = data.get('data', [])
                
                if not media_data:
                    return {
                        "response": "미디어 데이터가 없습니다."
                    }
                
                # 첫 번째 미디어 정보
                first_media = media_data[0]
                first_media_id = first_media['id']
                current_comments_count = first_media['comments_count']
                
                print(f"📊 [InstagramMediaFetchNode] 첫 번째 미디어 {first_media_id}의 댓글 수: {current_comments_count}")
                
                # 이전 데이터와 비교
                has_changes = False
                previous_comments_count = 0
                
                if previous_data:
                    previous_comments_count = previous_data.get('previous_comments_count', 0)
                    has_changes = current_comments_count != previous_comments_count
                    print(f"📊 [InstagramMediaFetchNode] 이전 댓글 수: {previous_comments_count}, 현재: {current_comments_count}, 변경: {has_changes}")
                
                # 댓글 수 변경이 있을 때는 JSON 파일을 나중에 업데이트하도록 임시 데이터만 준비
                json_data = {
                    'media_data': media_data,
                    'first_media_id': first_media_id,
                    'previous_comments_count': current_comments_count
                }
                
                # 최초 실행, 댓글 수 변경이 있을 때만 JSON 파일 업데이트
                if not os.path.exists(json_file_path):
                    with open(json_file_path, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, ensure_ascii=False, indent=2)
                    print(f"💾 [InstagramMediaFetchNode] 최초 실행: 미디어 데이터를 JSON 파일에 저장했습니다.")
                else:
                    if has_changes:
                        print(f"📝 [InstagramMediaFetchNode] 댓글 수 변경 감지. JSON 파일은 댓글 수집 후 업데이트됩니다.")
                    else:
                        print(f"📝 [InstagramMediaFetchNode] 기존 JSON 파일이 존재하여 저장하지 않습니다.")
            
                
                return {
                    "media_data": media_data,
                    "first_media_id": first_media_id,
                    "current_comments_count": current_comments_count,
                    "previous_comments_count": previous_comments_count,
                    "has_changes": has_changes,
                    "json_data": json_data,  # 댓글 수집 후 저장할 데이터
                    "response": f"미디어 데이터를 성공적으로 가져왔습니다. 총 {len(media_data)}개의 포스트가 있습니다. 댓글 수 변경: {has_changes}"
                }
            else:
                return {
                    "response": f"API 요청 실패: {response.status_code} - {response.text}"
                }
        except Exception as e:
            return {
                "response": f"미디어 데이터 가져오기 중 오류 발생: {str(e)}"
            }


class InstagramCommentsFetchNode(BaseNode):
    """
    댓글 데이터를 가져오는 노드
    """

    def execute(self, state: ManagementState) -> Dict[str, Any]:
        """
        첫 번째 미디어의 댓글 데이터를 가져옵니다.
        """
        print(f"🔍 [InstagramCommentsFetchNode] 실행 중...")
        
        access_token = state["access_token"]
        first_media_id = state["first_media_id"]
        json_file_path = state["comment_file_path"]
        json_data = state.get("json_data")
        
        if not first_media_id:
            return {
                "response": "미디어 ID가 없습니다."
            }
        
        try:
            # 댓글 데이터 가져오기
            comments_data = self._get_comments_data(access_token, first_media_id)
            
            # 댓글 리스트 출력
            print(f"\n📝 [InstagramCommentsFetchNode] 댓글 리스트:")
            for i, comment in enumerate(comments_data, 1):
                print(f"  {i}. {comment.get('text', 'N/A')} (by {comment.get('username', 'Unknown')})")
            print()
            
            # 댓글 수집 후 JSON 파일 저장
            if json_data:
                # media_data의 첫 번째 항목의 comments_count 업데이트
                if json_data.get('media_data') and len(json_data['media_data']) > 0:
                    json_data['media_data'][0]['comments_count'] = state.get('current_comments_count', 0)
                
                # previous_comments_count 업데이트
                json_data['previous_comments_count'] = state.get('current_comments_count', 0)
                
                with open(json_file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                print(f"💾 [InstagramCommentsFetchNode] 댓글 수집 완료 후 JSON 파일을 업데이트했습니다.")
            
            return {
                "comments_data": comments_data,
                "response": f"댓글 데이터를 성공적으로 가져왔습니다. 총 {len(comments_data)}개의 댓글이 있습니다."
            }
        except Exception as e:
            return {
                "response": f"댓글 데이터 가져오기 중 오류 발생: {str(e)}"
            }
    
    def _get_comments_data(self, access_token: str, media_id: str) -> List[Dict[str, Any]]:
        """
        Get comments API를 통해 특정 미디어의 댓글 데이터를 가져옵니다.
        """
        url = f'https://graph.instagram.com/v23.0/{media_id}/comments?access_token={access_token}'
        params = {
            'fields': 'id,text,timestamp,username'
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                comments = data.get('data', [])
                print(f"📝 [InstagramCommentsFetchNode] 미디어 {media_id}에서 {len(comments)}개의 댓글을 가져왔습니다.")
                return comments
            else:
                print(f"댓글 가져오기 API 오류: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"댓글 가져오기 네트워크 오류: {str(e)}")
            return []


class InstagramCommentsAnalysisNode(BaseNode):
    """
    인스타그램 댓글을 LLM(Gemini)으로 분석하는 노드 (langchain 기반)
    """
    def execute(self, state: ManagementState) -> Dict[str, Any]:
        print(f"🔍 [InstagramCommentsAnalysisNode] 실행 중...")
        comments_data = state.get("comments_data", [])
        if not comments_data:
            return {"response": "분석할 댓글 데이터가 없습니다."}

        # 댓글 텍스트만 추출
        comments_texts = [c.get("text", "") for c in comments_data if c.get("text")]
        comments_str = "\n".join(comments_texts)

        # 프롬프트 생성
        prompt_template = get_instagram_comment_analysis_prompt()
        prompt = prompt_template.format(comments=comments_str)

        # LangChain 기반 Gemini LLM 호출
        try:
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                return {"response": "GOOGLE_API_KEY 환경변수가 설정되어 있지 않습니다.", "comment_analysis_result": None}
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)
            response = llm.invoke([HumanMessage(content=prompt)])
            result_text = response.content if hasattr(response, "content") else str(response)
            print(f"[InstagramCommentsAnalysisNode] 분석 결과:\n{result_text}")
            state["comment_analysis_result"] = result_text
            
            # 분석 결과를 별도 json 파일로 저장

            now_str = datetime.now().isoformat()
            analysis_file_path = state.get("comment_analysis_file_path")
            # 파일이 존재하면 기존 데이터에 추가, 없으면 새로 생성
            if os.path.exists(analysis_file_path):
                try:
                    with open(analysis_file_path, 'r', encoding='utf-8') as f:
                        analysis_data = json.load(f)
                except Exception:
                    analysis_data = {}
                analysis_data[now_str] = result_text
            else:
                analysis_data = {now_str: result_text}
            with open(analysis_file_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            print(f"[InstagramCommentsAnalysisNode] 분석 결과를 {analysis_file_path}에 저장했습니다.")
            return {"comment_analysis_result": result_text, "response": "댓글 분석이 완료되었습니다."}
        except Exception as e:
            print(f"[InstagramCommentsAnalysisNode] Gemini 호출 오류: {str(e)}")
            return {"response": f"Gemini 호출 오류: {str(e)}", "comment_analysis_result": None}


class NoChangeNode(BaseNode):
    """
    댓글 수 변경이 없을 때 실행되는 노드
    """

    def execute(self, state: ManagementState) -> Dict[str, Any]:
        """
        댓글 수 변경이 없을 때의 처리를 수행합니다.
        """
        print(f"🔍 [NoChangeNode] 실행 중...")
        
        return {
            "response": "댓글 수에 변경이 없습니다. 모니터링을 계속합니다."
        }
