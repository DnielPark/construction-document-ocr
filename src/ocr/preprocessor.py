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
        """이미지 전처리 파이프라인"""
        # 1. 그레이스케일 변환
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 2. 노이즈 제거 (Gaussian Blur)
        denoised = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # 3. 적응형 이진화 (표 구조에 효과적)
        binary = cv2.adaptiveThreshold(
            denoised, 
            255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 
            2
        )
        
        # 4. 모폴로지 연산 (선명도 향상)
        kernel = np.ones((2, 2), np.uint8)
        processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return processed
        
    def enhance_contrast(self, image):
        """대비 향상 (CLAHE)"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray)
        
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