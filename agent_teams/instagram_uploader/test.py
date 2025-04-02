import os

from core import InstagramUploader
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()

    uploader = InstagramUploader(
        username=os.getenv("ACCOUNT_USERNAME"), password=os.getenv("ACCOUNT_PASSWORD")
    )

    test_content = {
        "image": "test.jpeg",
        "text": "이것은 인스타그램 포스트에 올릴 테스트 문장입니다.",
    }

    uploader.upload_photo(test_content["image"], test_content["text"])
