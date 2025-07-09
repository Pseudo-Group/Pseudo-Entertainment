"""
날씨 정보를 가져오는 모듈

기상청 API를 사용하여 현재 날씨 정보를 가져오고, 
음악 생성에 활용할 수 있는 형태로 변환합니다.
"""

from datetime import datetime, timedelta
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import os 

load_dotenv()


class WeatherService:
    """
    기상청 API를 사용하여 날씨 정보를 가져오는 서비스 클래스
    """
    
    def __init__(self):
        self.service_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
        self.numOfRows = '1000'
        self.pageNO = '1'
        self.dataType = 'JSON'

        # 방위 코드 정의
        self.deg_code = {
            0: 'N', 360: 'N', 180: 'S', 270: 'W', 90: 'E', 22.5: 'NNE',
            45: 'NE', 67.5: 'ENE', 112.5: 'ESE', 135: 'SE', 157.5: 'SSE',
            202.5: 'SSW', 225: 'SW', 247.5: 'WSW', 292.5: 'WNW', 315: 'NW',
            337.5: 'NNW'
        }
        
        # 날씨 코드 정의
        self.pty_code = {
            0: '강수 없음', 1: '비', 2: '비/눈', 3: '눈', 
            5: '빗방울눈날림', 6: '진눈깨비', 7: '눈날림'
        }
        self.sky_code = {1: '맑음', 3: '구름많음', 4: '흐림'}
    
    def deg_to_dir(self, deg: float) -> str:
        """
        각도를 방위로 변환
        
        Args:
            deg: 각도 (0-360)
            
        Returns:
            방위 문자열 (N, S, E, W, NE, SE, SW, NW 등)
        """
        close_dir = ''
        min_abs = 360
        if deg not in self.deg_code.keys():
            for key in self.deg_code.keys():
                if abs(key - deg) < min_abs:
                    min_abs = abs(key - deg)
                    close_dir = self.deg_code[key]
        else:
            close_dir = self.deg_code[deg]
        return close_dir
    
    def get_weather_data(self, nx: str = '60', ny: str = '126') -> Dict[str, Any]:
        """
        기상청 API에서 날씨 데이터를 가져옵니다.
        
        Args:
            nx: X 좌표 (기본값: 서울 용산구)
            ny: Y 좌표 (기본값: 서울 용산구)
            
        Returns:
            날씨 데이터 딕셔너리
        """
        # 현재 날짜와 시간 사용
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)

        base_date = now.strftime('%Y%m%d')
        base_time = one_hour_ago.strftime('%H%M')
        
        # URL 생성
        url = f"{self.base_url}?serviceKey={self.service_key}&numOfRows={self.numOfRows}&pageNo={self.pageNO}&dataType={self.dataType}&base_date={base_date}&base_time={base_time}&nx={nx}&ny={ny}"

        try:
            response = requests.get(url)
            return json.loads(response.text)
        except requests.RequestException as e:
            print(f"날씨 API 요청 실패: {e}")
            return {}
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 실패: {e}")
            return {}
    
    def parse_weather_data(self, weather_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        날씨 데이터를 시간대별로 파싱합니다.
        
        Args:
            weather_data: API 응답 데이터
            
        Returns:
            시간대별 날씨 정보 딕셔너리
        """
        informations = {}
        
        if 'response' not in weather_data or 'body' not in weather_data['response']:
            return informations
            
        items = weather_data['response']['body']['items']['item']
        
        for item in items:
            cate = item['category']
            fcst_time = item['fcstTime']
            fcst_value = item['fcstValue']
            
            if fcst_time not in informations:
                informations[fcst_time] = {}
            
            informations[fcst_time][cate] = fcst_value
        
        return informations
    
    def format_weather_info(self, weather_info: Dict[str, Any], base_date: str, 
                          fcst_time: str, nx: str, ny: str) -> str:
        """
        날씨 정보를 읽기 쉬운 형태로 포맷팅합니다.
        
        Args:
            weather_info: 특정 시간의 날씨 정보
            base_date: 기준 날짜
            fcst_time: 예보 시간
            nx: X 좌표
            ny: Y 좌표
            
        Returns:
            포맷팅된 날씨 정보 문자열
        """
        template = f"{base_date[:4]}년 {base_date[4:6]}월 {base_date[-2:]}일 {fcst_time[:2]}시 {fcst_time[2:]}분 ({int(nx)}, {int(ny)}) 지역의 날씨는 "
        
        # 하늘 상태
        if 'SKY' in weather_info:
            sky_temp = self.sky_code[int(weather_info['SKY'])]
            template += sky_temp + " | "
        
        # 강수 형태
        if 'PTY' in weather_info:
            pty_temp = self.pty_code[int(weather_info['PTY'])]
            template += pty_temp + " | "
        
        # 1시간 강수량
        if 'RN1' in weather_info:
            rn1_temp = weather_info['RN1']
            template += f"시간당 {rn1_temp} | "
        
        # 기온
        if 'T1H' in weather_info:
            t1h_temp = float(weather_info['T1H'])
            template += f"기온 {t1h_temp}°C | "
        
        # 습도
        if 'REH' in weather_info:
            reh_temp = float(weather_info['REH'])
            template += f"습도 {reh_temp}% | "
        
        # 동서 바람 성분
        if 'UUU' in weather_info:
            uuu_temp = float(weather_info['UUU'])
            template += f"동서 바람 성분 {uuu_temp}m/s | "
        
        # 남북 바람 성분
        if 'VVV' in weather_info:
            vvv_temp = float(weather_info['VVV'])
            template += f"남북 바람 성분 {vvv_temp}m/s | "
        
        # 풍향
        if 'VEC' in weather_info:
            vec_temp = self.deg_to_dir(float(weather_info['VEC']))
            template += f"풍향 {vec_temp} | "
        
        # 풍속
        if 'WSD' in weather_info:
            wsd_temp = weather_info['WSD']
            template += f"풍속 {wsd_temp}m/s | "
        
        # 낙뢰
        if 'LGT' in weather_info:
            lgt_temp = weather_info['LGT']
            template += f"낙뢰 {lgt_temp}kA"
        
        return template
    
    def get_current_weather(self, nx: str = '60', ny: str = '126') -> Dict[str, Any]:
        """
        현재 시간과 가장 가까운 날씨 정보를 가져옵니다.
        
        Args:
            nx: X 좌표
            ny: Y 좌표
            
        Returns:
            현재 날씨 정보 딕셔너리
        """
        # 날씨 데이터 가져오기
        weather_data = self.get_weather_data(nx, ny)
        if not weather_data:
            return {}
        
        # 시간대별로 파싱
        informations = self.parse_weather_data(weather_data)
        if not informations:
            return {}
        
        # 현재 시간과 가장 가까운 예보 시간 찾기
        now = datetime.now()
        current_time = now.strftime('%H%M')
        base_date = now.strftime('%Y%m%d')
        
        closest_time = min(informations.keys(), 
                          key=lambda x: abs(int(x) - int(current_time)))
        
        # 해당 시간의 날씨 정보
        current_weather = informations[closest_time]
        
        # 포맷팅된 문자열 생성
        formatted_weather = self.format_weather_info(
            current_weather, base_date, closest_time, nx, ny
        )
        
        return {
            'raw_data': current_weather,
            'formatted_text': formatted_weather,
            'temperature': float(current_weather.get('T1H', 0)),
            'humidity': float(current_weather.get('REH', 0)),
            'sky_condition': self.sky_code.get(int(current_weather.get('SKY', 1)), '맑음'),
            'precipitation': self.pty_code.get(int(current_weather.get('PTY', 0)), '강수 없음'),
            'wind_speed': current_weather.get('WSD', '0'),
            'wind_direction': self.deg_to_dir(float(current_weather.get('VEC', 0))),
            'location': f"({nx}, {ny})"
        }