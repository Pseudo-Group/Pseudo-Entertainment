import os
from pathlib import Path
from typing import List
from datetime import datetime
import requests
import xmltodict
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(
    name="Weather",
    version="0.0.1",
    description="Agent for weather information"
)

def get_current_date():
    current_date = datetime.now().date()
    return current_date.strftime("%Y%m%d")

def get_current_hour():
    now = datetime.now()
    return datetime.now().strftime("%H%M")

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

    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'
    res = requests.get(url, params)

    xml_data = res.text
    dict_data = xmltodict.parse(xml_data)

    for item in dict_data['response']['body']['items']['item']:
        if item['category'] == 'T1H':
            temp = item['obsrValue']
        if item['category'] == 'PTY':
            sky = item['obsrValue']
        if item['category'] == 'REH':
            humidity = item['obsrValue']

    sky = int_to_weather[sky]
    
    return temp, sky, humidity

@mcp.tool()
async def weather_information() -> str:
    """
    Using OpenWeather API, get information about the weather in gangnam-gu, seoul.  
    
    Parameters:
    There's no need to specify the parameters.

    출력 샘플 : "현재 강남의 날씨는 맑음이며 온도는 22.3도, 습도는 40% 입니다."
    *env 파일에 공공데이터 API를 받아와서 저장 필요
    https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15084084

    """

    try:
        keys = os.getenv("WEATHER_API_KEY")
        
        params = {
            'serviceKey': keys,
            'pageNo': '1',
            'numOfRows': '10',
            'dataType': 'XML',
            'base_date': get_current_date(),
            'base_time': get_current_hour(),
            'nx': '61',  # 강남 신사동
            'ny': '126'
        }

        temperature, weather, humidity = forecast(params)
        weather_information = f"현재 강남의 날씨는 {weather}이며 온도는 {temperature}도, 습도는 {humidity}% 입니다."
        return weather_information
    
    except Exception as e:
        return f"An error occurred during weather information retrieval: {str(e)}"


if __name__ == "__main__":
    mcp.run()