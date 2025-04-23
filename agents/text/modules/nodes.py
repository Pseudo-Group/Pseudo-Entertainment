"""
노드 클래스 모듈

해당 클래스 모듈은 각각 노드 클래스가 BaseNode를 상속받아 노드 클래스를 구현하는 모듈입니다.
"""

from agents.base_node import BaseNode
from agents.text.modules.chains import set_extraction_chain
from agents.text.modules.persona import PERSONA
from agents.text.modules.state import TextState

import requests
from datetime import datetime
import xmltodict
import os 
from dotenv import load_dotenv

class PersonaExtractionNode(BaseNode):
    """
    콘텐츠 종류에 적합한 페르소나를 추출하는 노드
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # BaseNode 초기화
        self.chain = set_extraction_chain()  # 페르소나 추출 체인 설정

    def execute(self, state: TextState) -> dict:
        """
        주어진 상태(state)에서 content_topic과 content_type을 추출하여
        페르소나 추출 체인에 전달하고, 결과를 응답으로 반환합니다.
        """
        # 페르소나 추출 체인 실행
        extracted_persona = self.chain.invoke(
            {
                "content_topic": state["content_topic"],  # 콘텐츠 주제
                "content_type": state["content_type"],  # 콘텐츠 유형
                "persona_details": PERSONA,  # 페르소나 세부 정보
            }
        )

        # 추출된 페르소나를 응답으로 반환
        return {"response": extracted_persona}

class WeatherAPINode(BaseNode) :
    """
    공공데이터 API로부터 Weather에 대한 정보를 받아오는 Node
    
    출력 샘플 : "현재 강남의 날씨는 맑음이며 온도는 22.3도, 습도는 40% 입니다."
    env 파일에 공공데이터 API를 받아와서 저장 필요
    https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15084084
    DECODING 부분의 값을 .env WEATHER_API_KEY에 입력
    """
    ### https://velog.io/@acdongpgm/Python-%EB%82%A0%EC%94%A8-API-%EC%82%AC%EC%9A%A9%ED%95%98%EA%B8%B0-%EB%AC%B4%EB%A3%8CFree

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # BaseNode 초기화
        load_dotenv()


    def execute(self, state: TextState) -> dict:
        """
        주어진 상태(state)에서 content_topic과 content_type을 추출하여
        페르소나 추출 체인에 전달하고, 결과를 응답으로 반환합니다.
        """
        #   # 강수형태: 없음(0), 비(1), 비/눈(2), 눈(3), 빗방울(5), 빗방울눈날림(6), 눈날림(7)

        keys = os.getenv("WEATHER_API_KEY")

        params ={'serviceKey' : keys, 
                'pageNo' : '1', 
                'numOfRows' : '10', 
                'dataType' : 'XML', 
                'base_date' : get_current_date(), 
                'base_time' : get_current_hour(), 
                # 강남 신사동동 61, 126
                'nx' : '61', 
                'ny' : '126' }

        temperature, weather, humidity = forecast(params)

        weather_sentence = f"현재 강남의 날씨는 {weather}이며 온도는 {temperature}도, 습도는 {humidity}% 입니다."

        return {"weather": weather_sentence}

    @staticmethod
    def get_current_date():
        current_date = datetime.now().date()
        return current_date.strftime("%Y%m%d")
    @staticmethod
    def get_current_hour():
        now = datetime.now()
        return datetime.now().strftime("%H%M")

    @staticmethod
    def forecast(params):

        int_to_weather = {
            "0": "맑음",
            "1": "비",
            "2": "비/눈",
            "3": "눈",
            "5": "빗방울",
            "6": "빗방울눈날림",
            "7": "눈날림"
        }

        url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst' # 초단기예보
        # 값 요청 (웹 브라우저 서버에서 요청 - url주소와 파라미터)
        res = requests.get(url, params)

        #XML -> 딕셔너리
        xml_data = res.text
        dict_data = xmltodict.parse(xml_data)

        for item in dict_data['response']['body']['items']['item']:
            if item['category'] == 'T1H':
                temp = item['obsrValue']

            # 강수형태: 없음(0), 비(1), 비/눈(2), 눈(3), 빗방울(5), 빗방울눈날림(6), 눈날림(7)
            if item['category'] == 'PTY':
                sky = item['obsrValue']

            if item['category'] == 'REH':
                humidity = item['obsrValue']

            ### SKY 는 있는데 왜 추출이 안되는지 잘 모르겠음.
            # # 하늘상태: 맑음(1) 구름많은(3) 흐림(4)
            # if item['category'] == 'SKY':
            #     cloudy = item['obsrValue']

        sky = int_to_weather[sky]
        
        return temp, sky, humidity

