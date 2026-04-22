"""
DeepSeek Vision API 엔진
"""

import requests
import base64
from pathlib import Path
import json


class DeepSeekEngine:
    """DeepSeek Vision API 클래스"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        print("DeepSeek Vision 엔진 초기화 완료!")
        
    def extract_table(self, image_path):
        """이미지에서 표 데이터 추출"""
        print(f"📊 DeepSeek Vision으로 표 추출 중: {Path(image_path).name}")
        
        # 이미지를 base64로 인코딩
        with open(image_path, 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # API 요청
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        prompt = """
첨부된 이미지는 하수관로 공사 수량표입니다.
측점별 데이터를 다음 JSON 형식으로 추출해주세요:

[
  {
    "측점": "22+12.200",
    "누가거리": "100",
    "구간거리": "20",
    "터파기_A(㎡)": "4.51",
    "터파기_V(㎥)": "45.1",
    "되메우기_A(㎡)": "2.84",
    "되메우기_V(㎥)": "28.4",
    "모래부설_A(㎡)": "0.35",
    "모래부설_V(㎥)": "3.5",
    "ASP파취복구_L(m)": "2.51",
    "ASP파취복구_A(㎡)": "25.1",
    "Conc파취복구_L(m)": "0",
    "Conc파취복구_A(㎡)": "0",
    "ASC파취복구_L(m)": "0",
    "ASC파취복구_A(㎡)": "0",
    "ASP포장절단_L(m)": "0",
    "ASP포장절단_A(㎡)": "0",
    "Conc포장절단_L(m)": "0",
    "Conc포장절단_A(㎡)": "0",
    "노면파쇄_L(m)": "0",
    "노면파쇄_A(㎡)": "0"
  }
]

규칙:
1. 측점은 "숫자+숫자.숫자" 형식 (예: 22+12.200)
2. 띄어쓰기 무시하고 병합 (예: "지 반 고" → "지반고")
3. 단위 기호 제거 (예: "11.64m" → "11.64")
4. 빈 값은 "0"
5. JSON만 반환 (설명 없이)
6. 모든 측점을 배열에 포함
"""
        
        data = {
            'model': 'deepseek-chat',
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': prompt},
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': f'data:image/jpeg;base64,{image_base64}'
                            }
                        }
                    ]
                }
            ],
            'temperature': 0.1,  # 정확도 우선
            'max_tokens': 2000
        }
        
        response = requests.post(self.api_url, headers=headers, json=data)
        
        if response.status_code != 200:
            raise Exception(f"DeepSeek API 오류: {response.text}")
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # JSON 파싱
        try:
            # ```json ... ``` 제거
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]
            
            table_data = json.loads(content.strip())
            print(f"✅ {len(table_data)}개 측점 추출 완료")
            return table_data
        except json.JSONDecodeError as e:
            raise Exception(f"JSON 파싱 오류: {e}\n응답: {content}")
            
    def extract_table_from_array(self, image_array):
        """OpenCV 배열에서 표 데이터 추출"""
        import cv2
        import tempfile
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            cv2.imwrite(tmp.name, image_array)
            tmp_path = tmp.name
        
        try:
            result = self.extract_table(tmp_path)
            return result
        finally:
            # 임시 파일 삭제
            import os
            os.unlink(tmp_path)