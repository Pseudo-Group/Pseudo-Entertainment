from agents.base_node import BaseNode
from agents.collect_comments.modules.state import CollectCommentsState
from langsmith import traceable
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
import re
import csv




class InitDriverNode(BaseNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @traceable
    def execute(self, state: CollectCommentsState) -> dict:
        # 크롬 드라이버 옵션 설정 및 초기화
        options = Options()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        state.driver = driver  # 상태에 드라이버 저장
        return {"driver": driver}


class CollectPostLinksNode(BaseNode):
    @traceable
    def execute(self, state: CollectCommentsState) -> dict:
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
        MAX_LINKS = 8 # 수집할 최대 게시물 링크 수 (여기 숫자만 바꾸면 됨)
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
    def execute(self, state: CollectCommentsState) -> dict:
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
    def execute(self, state: CollectCommentsState) -> dict:
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
    def execute(self, state: CollectCommentsState) -> dict:
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
    def execute(self, state: CollectCommentsState) -> dict:
        # 댓글을 CSV 파일에 저장
        with open(state.csv_filename, mode='a', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            for comment in state.comments:
                writer.writerow([state.current_post_url, comment])
        return {"current_post_url": state.current_post_url}