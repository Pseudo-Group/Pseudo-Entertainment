import os

from dotenv import load_dotenv
from instagrapi import Client


class InstagramUploader:
    def __init__(self, username=None, password=None):
        """Instagram 클라이언트 초기화 및 로그인"""
        self.username = username
        self.password = password

        self.client = Client()
        self.client.delay_range = [1, 2]  # 요청 간 딜레이 조절
        self.login()

    def login(self):
        """Instagram 로그인"""
        try:
            self.client.login(self.username, self.password, relogin=True)
            print("✅ Instagram 로그인 성공!")
        except Exception as e:
            print("❌ 로그인 실패:", e)

    def upload_photo(self, image_path: str, caption: str):
        """사진 업로드"""
        try:
            media = self.client.photo_upload(image_path, caption)
            print("✅ 업로드 완료! Post ID:", media.model_dump()["id"])
            return media
        except Exception as e:
            print("❌ 업로드 실패:", e)
            return None
