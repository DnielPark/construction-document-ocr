"""
OCR 엔진 모듈
"""

import easyocr
import numpy as np
from .preprocessor import ImagePreprocessor


class OCREngine:
    """OCR 엔진 클래스"""
    
    def __init__(self, languages=["ko", "en"], gpu=False):
        self.languages = languages
        self.gpu = gpu
        self.reader = None
        self.preprocessor = ImagePreprocessor()
        self.initialize()
        
    def initialize(self):
        """OCR 리더 초기화"""
        print(f"OCR 엔진 초기화 중... (언어: {self.languages}, GPU: {self.gpu})")
        self.reader = easyocr.Reader(self.languages, gpu=self.gpu)
        print("OCR 엔진 초기화 완료!")
        
    def recognize(self, image):
        """이미지에서 텍스트 인식"""
        if self.reader is None:
            raise RuntimeError("OCR 엔진이 초기화되지 않았습니다.")
        
        # 전처리
        processed = self.preprocessor.preprocess(image)
        
        # OCR 실행
        results = self.reader.readtext(processed)
        
        # 결과 파싱: (bbox, text, confidence)
        parsed_results = []
        for bbox, text, conf in results:
            parsed_results.append({
                'bbox': bbox,
                'text': text,
                'confidence': conf
            })
        
        return parsed_results
        
    def recognize_with_coordinates(self, image):
        """좌표 정보 포함하여 텍스트 인식"""
        results = self.recognize(image)
        
        # 좌표 정보 추가 (중심점 계산)
        for item in results:
            bbox = item['bbox']
            x_coords = [point[0] for point in bbox]
            y_coords = [point[1] for point in bbox]
            
            item['center_x'] = sum(x_coords) / 4
            item['center_y'] = sum(y_coords) / 4
            item['left'] = min(x_coords)
            item['top'] = min(y_coords)
            item['right'] = max(x_coords)
            item['bottom'] = max(y_coords)
        
        return results
        
    def recognize_region(self, image, rect):
        """지정된 영역에서 텍스트 인식"""
        # 영역 크롭
        x, y, w, h = rect
        cropped = image[y:y+h, x:x+w]
        
        if cropped.size == 0:
            return ""
        
        # 해당 영역 OCR 실행
        results = self.recognize(cropped)
        
        # 텍스트 결합
        texts = [item['text'] for item in results]
        return " ".join(texts) if texts else ""