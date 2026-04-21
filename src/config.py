"""
프로그램 설정 파일
"""

# OCR 설정
OCR_LANGUAGES = ["ko", "en"]  # 한국어, 영어
OCR_GPU = False  # GPU 사용 여부 (True로 설정하면 빠르지만 CUDA 필요)

# UI 설정
WINDOW_TITLE = "CM 현장 문서 OCR 프로그램"
WINDOW_SIZE = (1200, 800)  # 너비, 높이

# 테이블 설정
TABLE_COLUMNS = 20  # 기본 컬럼 수
TABLE_HEADERS = [f"컬럼 {i+1}" for i in range(TABLE_COLUMNS)]

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