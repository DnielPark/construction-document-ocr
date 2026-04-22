"""
Claude Vision API 엔진
"""

import anthropic
import base64
import json
from pathlib import Path


class ClaudeEngine:
    """Claude Vision API 클래스"""
    
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
        print("Claude Vision 엔진 초기화 완료!")
        
    def extract_table(self, image_path):
        """이미지에서 표 데이터 추출"""
        # Path 객체를 문자열로 변환
        image_path_str = str(image_path)
        print(f"📊 Claude Vision으로 표 추출 중: {Path(image_path_str).name}")
        
        # 이미지를 base64로 인코딩
        with open(image_path_str, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')
        
        # 이미지 확장자 확인
        ext = image_path_str.lower().split('.')[-1]
        media_type = f"image/{ext}" if ext in ['png', 'jpg', 'jpeg'] else "image/jpeg"
        
        prompt = """첨부된 이미지는 하수관로 공사 수량표입니다.

표 구조는 항상 고정되어 있습니다 (13개 항목):

1. 측점
2. 지반고
3. 관저고 
4. 터파기 육상
5. 터파기 수중
6. 되메우기 관주위
7. 되메우기 관상단
8. 파취 및 복구 ASP
9. 파취 및 복구 Con'c
10. 파취 및 복구 보도블럭
11. 모래부설
12. 보조기층
13. 동상방지층

작업 순서:
1. 측점을 찾으세요: "숫자+숫자.숫자" 형식 (예: 20+0.000)
2. 각 측점 행에서 왼쪽→오른쪽으로 순서대로 숫자를 읽으세요
3. 아래 형식으로 JSON 출력:

[
  {
    "측점": "20+0.000",
    "지반고": "11.40",
    "관저고": "10.31",
    "터파기 육상": "1.25",
    "터파기 수중": "0.00",
    "되메우기 관주위": "0.00",
    "되메우기 관상단": "0.45",
    "파취 및 복구 ASP": "1.72",
    "파취 및 복구 Con'c": "0.00",
    "파취 및 복구 보도블럭": "0.33",
    "모래부설": "0.33",
    "보조기층": "0.47",
    "동상방지층": "0.00"
  }
]

예시 (sample_003.png 참고):
측점 "20+0.000" 행을 왼쪽부터 읽기:
- 측점: 20+0.000
- 지반고: 11.40m
- 관저고: 10.31m
- 터파기 육상: 1.25㎡
- 터파기 수중: 0.00㎡
- 되메우기 관주위: 0.00㎡
- 되메우기 관상단: 0.45㎡
- 파취 및 복구 ASP: 1.72m
- 파취 및 복구 Con'c: 0.00m
- 파취 및 복구 보도블럭: 0.33㎡
- 모래부설: 0.33㎡
- 보조기층: 0.47㎡
- 동상방지층: 0.00㎡

중요 규칙:
1. 단위 제거: m, ㎡, ㎥ 등 모두 제거
2. 소수점 유지: 11.40, 1.25 등
3. OCR 오류 수정: "O" → "0", "l" → "1"
4. 띄어쓰기 무시
5. 빈 셀 = "0" 또는 "0.00"
6. 각 측점마다 정확히 13개 값
7. 헤더 텍스트는 무시하고 위치(순서)만 사용
8. JSON만 출력 (설명 없이)"""
        
        message = self.client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )
        
        content = message.content[0].text
        
        # JSON 파싱
        try:
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