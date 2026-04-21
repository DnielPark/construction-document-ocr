"""
이미지 전처리 모듈
"""

import cv2
import numpy as np


class ImagePreprocessor:
    """이미지 전처리 클래스"""
    
    def __init__(self):
        pass
        
    def preprocess(self, image):
        """이미지 전처리"""
        # 그레이스케일 변환
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # 노이즈 제거
        denoised = cv2.medianBlur(gray, 3)
        
        # 이진화 (Otsu 방법)
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
        
    def crop_region(self, image, rect):
        """지정된 영역 크롭"""
        x, y, w, h = rect
        return image[y:y+h, x:x+w]
        
    def resize_image(self, image, scale_factor=2.0):
        """이미지 리사이즈 (OCR 정확도 향상을 위해)"""
        height, width = image.shape[:2]
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)