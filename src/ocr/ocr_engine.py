"""
OCR 엔진 모듈
"""

import easyocr


class OCREngine:
    """OCR 엔진 클래스"""
    
    def __init__(self, languages=["ko", "en"], gpu=False):
        self.languages = languages
        self.gpu = gpu
        self.reader = None
        self.initialize()
        
    def initialize(self):
        """OCR 리더 초기화"""
        # TODO: Week 2에서 구현
        print(f"OCR 엔진 초기화 (언어: {self.languages}, GPU: {self.gpu})")
        
    def recognize(self, image):
        """이미지에서 텍스트 인식"""
        # TODO: Week 2에서 구현
        print("OCR 인식 실행 (구현 중)")
        return []
        
    def recognize_region(self, image, rect):
        """지정된 영역에서 텍스트 인식"""
        # TODO: Week 2에서 구현
        print(f"영역 OCR: {rect} (구현 중)")
        return ""