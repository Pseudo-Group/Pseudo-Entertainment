"""
노드 클래스 모듈

해당 클래스 모듈은 각각 노드 클래스가 BaseNode를 상속받아 노드 클래스를 구현하는 모듈입니다.

아래는 예시입니다.
"""

from agents.base_node import BaseNode
from agents.management.modules.chains import set_resource_planning_chain
from agents.management.modules.state import ManagementState
from agents.management.modules.state import CommentWorkflowState
from langsmith import traceable

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
import re
import csv


class ResourceManagementNode(BaseNode):
    """
    프로젝트에 필요한 리소스를 계획하고 관리하는 노드
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # BaseNode 초기화
        self.chain = set_resource_planning_chain()  # 리소스 계획 체인 설정

    def execute(self, state: ManagementState) -> dict:
        """
        주어진 상태(state)에서 project_id, request_type, query 등의 정보를 추출하여
        리소스 계획 체인에 전달하고, 결과를 응답으로 반환합니다.
        """
        # 팀 구성원 기본값 처리
        team_members = state.get("team_members", [])

        # 리소스 계획 체인 실행
        resource_plan = self.chain.invoke(
            {
                "project_id": state["project_id"],  # 프로젝트 ID
                "request_type": state["request_type"],  # 요청 유형
                "query": state["query"],  # 사용자 쿼리
                "team_members": team_members,  # 팀 구성원
                "resources_available": state.get(
                    "resources_available", {}
                ),  # 사용 가능한 리소스
            }
        )

        # 상태 업데이트
        state["resource_plan"] = resource_plan

        # 생성된 리소스 계획을 응답으로 반환
        return {"response": resource_plan}


class InitDriverNode(BaseNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @traceable
    def execute(self, state: CommentWorkflowState) -> dict:
        # 크롬 드라이버 옵션 설정 및 초기화
        options = Options()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        state.driver = driver  # 상태에 드라이버 저장
        return {"driver": driver}


class CollectPostLinksNode(BaseNode):
    @traceable
    def execute(self, state: CommentWorkflowState) -> dict:
        driver = state.driver
        if not driver:
            raise ValueError("WebDriver 인스턴스가 상태에 없습니다.")
        if not state.profile_url:
            raise ValueError("프로필 URL이 상태에 없습니다.")

        driver.get(state.profile_url)
        time.sleep(5)  # 페이지 로딩 대기

        soup = bs(driver.page_source, 'html.parser')
        links = []

        # 게시물 링크 수집
        MAX_LINKS = 3 # 수집할 최대 게시물 링크 수 (여기 숫자만 바꾸면 됨)
        for a in soup.find_all('a', href=True):
            href = a['href']
            if "/p/" in href and href not in links:
                links.append("https://www.instagram.com" + href)
            if len(links) >= MAX_LINKS:
                break

        state.post_links = links  # 상태에 수집한 링크 저장
        return {"post_links": links}

class SetCurrentPostUrlNode(BaseNode):
    @traceable
    def execute(self, state: CommentWorkflowState) -> dict:
        # 처리할 게시물이 없으면 current_post_url을 None으로 설정
        if not state.post_links:
            print("DEBUG: 처리할 게시물이 더 이상 없습니다.")
            state.current_post_url = None
            return {"current_post_url": None}

        # 다음 게시물 링크 꺼내서 current_post_url에 저장
        state.current_post_url = state.post_links.pop(0)
        print(f"DEBUG: 현재 게시물 URL 설정 -> {state.current_post_url}")
        return {
            "current_post_url": state.current_post_url,
            "post_links": state.post_links
            }


class LoadCommentsNode(BaseNode):
    @traceable
    def execute(self, state: CommentWorkflowState) -> dict:
        driver = state.driver
        post_address = state.current_post_url

        if not driver:
            raise ValueError("WebDriver 인스턴스가 상태에 없습니다.")

        if not isinstance(post_address, str) or not post_address.strip():
            raise ValueError(f"잘못된 게시물 URL입니다: {post_address}")

        print(f"DEBUG: 게시물 페이지 로딩 -> {post_address}")
        driver.get(post_address)
        time.sleep(5)

        # '댓글 더보기' 버튼 클릭 반복
        while True:
            try:
                buttons = driver.find_elements(By.XPATH, '//span[@aria-label="Load more comments"]')
                if buttons:
                    buttons[0].click()
                    time.sleep(2)
                else:
                    break
            except Exception:
                break

        state.page_source = driver.page_source  # 페이지 소스 상태에 저장
        return {"page_source": state.page_source}
    
class ExtractCommentsNode(BaseNode):
    @traceable
    def execute(self, state: CommentWorkflowState) -> dict:
        # 페이지 소스에서 댓글 텍스트 추출
        soup = bs(state.page_source, 'html.parser')
        comments = []

        # 제외할 불필요한 텍스트 목록
        junk_texts = [
            "Reply", "Like", "Log in to like or comment.", "See more posts", "Meta",
            "About", "Blog", "Jobs", "Help", "API", "Privacy", "Terms", "Locations",
            "Instagram Lite", "Threads", "Contact uploading and non-users", "Meta Verified",
            "English (UK)", "© 2025 Instagram from Meta",
            "By continuing, you agree to Instagram's Terms of Use and Privacy Policy.",
            "See more from", "See photos, videos and more from"
        ]

        for span in soup.find_all("span", {"dir": "auto"}):
            txt = span.get_text().strip()
            if not txt:
                continue
            if txt in junk_texts:
                continue
            if any(junk in txt for junk in junk_texts):
                continue
            if re.fullmatch(r"\d+\s?[wdhmy]", txt.lower()):
                continue
            if re.fullmatch(r"[\d,]+\s+likes?", txt.lower()):
                continue
            if re.fullmatch(r"\d{1,2}\s+\w+\s+\d{4}", txt):
                continue
            if re.fullmatch(r"[A-Za-z0-9._]{3,30}", txt):
                continue
            if len(txt) < 3:
                continue

            comments.append(txt)

        state.comments = comments
        return {"comments":state.comments}


class SaveCommentsNode(BaseNode):
    @traceable
    def execute(self, state: CommentWorkflowState) -> dict:
        # 댓글을 CSV 파일에 저장
        with open(state.csv_filename, mode='a', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            for comment in state.comments:
                writer.writerow([state.current_post_url, comment])
        return {"current_post_url": state.current_post_url}