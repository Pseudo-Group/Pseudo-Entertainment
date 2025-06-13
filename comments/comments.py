from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import time
import re
import csv

def get_post_links(driver, profile_url, limit=25):
    # limit: 프로필에서 가져올 게시물 링크 개수
    driver.get(profile_url)
    time.sleep(5)
    soup = bs(driver.page_source, 'html.parser')
    links = []

    for a in soup.find_all('a', href=True):
        href = a['href']
        if "/p/" in href and href not in links:
            links.append("https://www.instagram.com" + href)
        if len(links) >= limit:
            break # 설정한 limit 개수만큼 링크를 수집한 경우 반복 종료

    print(f"Found {len(links)} post links.")
    return links

def click_more_comments(driver, post_address):
    print(f"\nOpening post: {post_address}")
    driver.get(post_address)
    time.sleep(5) # 페이지가 완전히 로드될 때까지 대기

    while True:
        try:
            buttons = driver.find_elements(By.XPATH, '//span[@aria-label="Load more comments"]')
            if buttons:
                buttons[0].click() # '댓글 더 보기' 버튼 클릭
                time.sleep(2)
            else:
                break
        except:
            break

    return driver.page_source

def extract_comments(page_source):
    soup = bs(page_source, 'html.parser')
    comments = []

    junk_texts = [
        # 불필요한 고정 문구 및 UI 텍스트를 제거하기 위한 리스트
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
            continue # 빈 문자열 건너뛰기
        if txt in junk_texts:
            continue
        if any(junk in txt for junk in junk_texts):
            continue
        if re.fullmatch(r"\d+\s?[wdhmy]", txt.lower()):
            continue # '1w', '5d' 형식의 시간 표시 건너뛰기
        if re.fullmatch(r"[\d,]+\s+likes?", txt.lower()):
            continue # '1,234 likes' 형식 건너뛰기
        if re.fullmatch(r"\d{1,2}\s+\w+\s+\d{4}", txt):
            continue # 날짜 형식 (예: '10 April 2023') 건너뛰기
        if re.fullmatch(r"[A-Za-z0-9._]{3,30}", txt):
            continue # 인스타그램 아이디 형식 (영문/숫자/._ 조합) 필터링
        if len(txt) < 3:
            continue # 너무 짧은 댓글 필터링

        comments.append(txt)

    return comments

def scrape_comments_from_profile(profile_url, limit=25, csv_filename="instagram_comments.csv"):
    options = Options()
    options.add_argument("--start-maximized") # 크롬 브라우저 최대화 실행
    driver = webdriver.Chrome(options=options)

    try:
        post_links = get_post_links(driver, profile_url, limit=limit)

        with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(["Post URL", "Comment"]) # CSV 파일 헤더 작성

            for post_url in post_links:
                page_source = click_more_comments(driver, post_url)
                comments = extract_comments(page_source)

                print(f"\nComments from {post_url}:")
                for comment in comments:
                    print(f"- {comment}")
                    writer.writerow([post_url, comment]) # CSV 파일에 데이터 저장

    finally:
        driver.quit()
        print(f"\n✅ Comments saved to {csv_filename}")

# usage:
profile_url = "https://www.instagram.com/rozy.gram/"
scrape_comments_from_profile(profile_url, limit=25)
