"""
CLOVA OCR 엔진
"""

import requests
import base64
import uuid
from pathlib import Path


class OCREngine:
    """CLOVA OCR 엔진 클래스"""
    
    def __init__(self, api_url, secret_key):
        self.api_url = api_url
        self.secret_key = secret_key
        print("CLOVA OCR 엔진 초기화 완료!")
        
    def recognize_with_coordinates(self, image):
        """이미지에서 텍스트 인식 (좌표 포함)"""
        # OpenCV 이미지를 바이트로 변환
        import cv2
        _, img_encoded = cv2.imencode('.jpg', image)
        img_bytes = img_encoded.tobytes()
        
        # Base64 인코딩
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        # API 요청
        headers = {
            'X-OCR-SECRET': self.secret_key,
            'Content-Type': 'application/json'
        }
        
        data = {
            'images': [{
                'format': 'jpg',
                'name': 'document',
                'data': img_base64
            }],
            'lang': 'ko',
            'requestId': str(uuid.uuid4()),
            'version': 'V2',
            'timestamp': 0
        }
        
        response = requests.post(self.api_url, headers=headers, json=data)
        
        if response.status_code != 200:
            raise Exception(f"CLOVA OCR API 오류: {response.text}")
        
        # 응답 파싱
        result = response.json()
        return self._parse_clova_response(result)
        
    def _parse_clova_response(self, result):
        """CLOVA 응답을 EasyOCR 형식으로 변환"""
        parsed_results = []
        
        for image in result['images']:
            for field in image['fields']:
                bbox = field['boundingPoly']['vertices']
                text = field['inferText']
                confidence = field['inferConfidence']
                
                # 중심점 계산
                x_coords = [v['x'] for v in bbox]
                y_coords = [v['y'] for v in bbox]
                
                parsed_results.append({
                    'bbox': [[v['x'], v['y']] for v in bbox],
                    'text': text,
                    'confidence': confidence,
                    'center_x': sum(x_coords) / 4,
                    'center_y': sum(y_coords) / 4,
                    'left': min(x_coords),
                    'top': min(y_coords),
                    'right': max(x_coords),
                    'bottom': max(y_coords)
                })
        
        return parsed_results
        
    def recognize_region(self, image, rect):
        """지정된 영역에서 텍스트 인식"""
        # 영역 크롭
        x, y, w, h = rect
        cropped = image[y:y+h, x:x+w]
        
        if cropped.size == 0:
            return ""
        
        # 해당 영역 OCR 실행
        results = self.recognize_with_coordinates(cropped)
        
        # 텍스트 결합
        texts = [item['text'] for item in results]
        return " ".join(texts) if texts else ""
        
    def recognize(self, image):
        """이전 버전 호환용 (좌표 정보 제외)"""
        results = self.recognize_with_coordinates(image)
        # 좌표 정보 제거하여 이전 형식 유지
        for item in results:
            item.pop('center_x', None)
            item.pop('center_y', None)
            item.pop('left', None)
            item.pop('top', None)
            item.pop('right', None)
            item.pop('bottom', None)
        return results