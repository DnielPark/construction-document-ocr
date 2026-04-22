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

다음 2단계로 작업하세요:

═══════════════════════════════════════════════════════════
1단계: 표의 Grid 구조 파악
═══════════════════════════════════════════════════════════

표의 가로선/세로선을 인식하여 셀(칸)을 구분하세요.

각 측점 행의 구조:
[측점][지반고][관저고][터파기육상][터파기수중][되메우기관주위][되메우기관상단][ASP][Con'c][보도블럭][모래부설][보조기층][동상방지층]

예시:
행1: [20+0.000][11.40m][10.31m][1.25㎡][0.00㎡][0.00㎡][0.45㎡][1.72m][0m][빈칸][0.33㎡][0.47㎡][0.00㎡]
 ↑ 여기 빈칸 확인!

═══════════════════════════════════════════════════════════
2단계: 13개 항목 값 추출 및 검증
═══════════════════════════════════════════════════════════

각 측점 행에서 왼쪽부터 순서대로 셀을 읽으면서:

【1. 측점】
- 첫 번째 셀
- "숫자+숫자.숫자" 형식 (예: 20+0.000)

【2. 지반고】
- 두 번째 셀
- 단위 "m" 제거
- 예: "11.40m" → "11.40"

【3. 관저고】
- 세 번째 셀
- 단위 "m" 제거
- 예: "10.31m" → "10.31"

【4. 터파기 육상】
- 네 번째 셀
- 단위 "㎡" 제거
- 예: "1.25㎡" → "1.25"

【5. 터파기 수중】
- 다섯 번째 셀
- 단위 "㎡" 제거
- 예: "0.00㎡" → "0.00"

【6. 되메우기 관주위】
- 여섯 번째 셀
- 단위 "㎡" 제거
- 예: "0.00㎡" → "0.00"

【7. 되메우기 관상단】
- 일곱 번째 셀
- 단위 "㎡" 제거
- 예: "0.45㎡" → "0.45"

【8. 파취 및 복구 ASP】
- 여덟 번째 셀
- 단위 "m" 제거
- 예: "1.72m" → "1.72"

【9. 파취 및 복구 Con'c】
- 아홉 번째 셀
- 단위 "m" 제거
- 셀이 비어있으면 "0"
- 예: "0m" → "0" 또는 빈칸 → "0"

【10. 파취 및 복구 보도블럭】
- 열 번째 셀
- 단위 "m" 제거
- ⚠️ **셀이 비어있는지 정확히 확인!**
- 셀이 비어있으면 "0"
- 예: "0.33m" → "0.33" 또는 빈칸 → "0"

【11. 모래부설】
- 열한 번째 셀
- 단위 "㎡" 제거
- 예: "0.33㎡" → "0.33"

【12. 보조기층】
- 열두 번째 셀
- 단위 "㎡" 제거
- 예: "0.47㎡" → "0.47"

【13. 동상방지층】
- 열세 번째 셀
- 단위 "㎡" 제거
- 예: "0.00㎡" → "0.00"

═══════════════════════════════════════════════════════════
검증 규칙 (매우 중요!):
═══════════════════════════════════════════════════════════

1. **셀 경계를 정확히 인식**하세요
 - 가로선과 세로선으로 구분된 각 칸이 하나의 셀

2. **빈 셀 확인**:
 - 셀에 아무 텍스트도 없으면 → "0"
 - 셀에 "0" 또는 "0.00"이 있으면 → "0"
 - 셀에 값이 있으면 → 그 값

3. **다른 셀의 값을 가져오지 말 것**:
 - 10번째 셀(보도블럭)이 비어있을 때
 - 11번째 셀(모래부설) 값을 가져오면 안 됨!
 - 각 셀은 독립적!

4. **시각적 예시**:
┌──────┬──────┬──────┬──────┬──────┐
│ 셀8 │ 셀9 │ 셀10 │ 셀11 │ 셀12 │
│ ASP │ Con'C│ 보도 │ 모래 │ 보조 │
│ 1.72m│ 0m │(빈칸)│0.33㎡│0.47㎡│
└──────┴──────┴──────┴──────┴──────┘
 ↓ ↓ ↓
 값=0 값=0 값=0.33
 ↑ 빈칸이므로 0!

5. **잘못된 예** (절대 금지):
 - 셀10이 비어있는데 셀11의 "0.33"을 셀10 값으로 사용 ❌

6. **올바른 예**:
 - 셀10 = 빈칸 → "0" ✅
 - 셀11 = "0.33㎡" → "0.33" ✅

═══════════════════════════════════════════════════════════
출력 형식 (JSON):
═══════════════════════════════════════════════════════════

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
    "파취 및 복구 Con'c": "0",
    "파취 및 복구 보도블럭": "0",
    "모래부설": "0.33",
    "보조기층": "0.47",
    "동상방지층": "0.00"
  }
]

중요:
- 띄어쓰기 무시
- OCR 오류 수정: "O" → "0", "l" → "1"
- 단위만 제거 (m, ㎡, ㎥)
- 모든 측점 행 포함
- JSON만 출력 (설명 없이)
"""
        
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