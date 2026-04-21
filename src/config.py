"""
프로그램 설정 파일
"""

import re

# OCR 설정
OCR_LANGUAGES = ["ko", "en"]  # 한국어, 영어
OCR_GPU = False  # GPU 사용 여부 (True로 설정하면 빠르지만 CUDA 필요)

# UI 설정
WINDOW_TITLE = "CM 현장 문서 OCR 프로그램"
WINDOW_SIZE = (1200, 800)  # 너비, 높이

# 테이블 설정
TABLE_COLUMNS = 20  # 기본 컬럼 수
TABLE_HEADERS = [
    "측점", "누가거리", "구간거리",
    "터파기_A(㎡)", "터파기_V(㎥)",
    "되메우기_A(㎡)", "되메우기_V(㎥)",
    "모래부설_A(㎡)", "모래부설_V(㎥)",
    "ASP파취복구_L(m)", "ASP파취복구_A(㎡)",
    "Conc파취복구_L(m)", "Conc파취복구_A(㎡)",
    "ASC파취복구_L(m)", "ASC파취복구_A(㎡)",
    "ASP포장절단_L(m)", "ASP포장절단_A(㎡)",
    "Conc포장절단_L(m)", "Conc포장절단_A(㎡)",
    "노면파쇄_L(m)", "노면파쇄_A(㎡)"
]

# 정규식 패턴
STATION_PATTERN = re.compile(r'^\d+\+\d+\.\d+(\(.*\))?$')

# 파일 설정
SUPPORTED_IMAGE_FORMATS = [
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.bmp",
    "*.tiff",
    "*.tif",
    "*.gif",
]

# 경로 설정
DEFAULT_OUTPUT_DIR = "output"
EXCEL_FILENAME_PREFIX = "ocr_result_"