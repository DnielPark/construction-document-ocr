"""
프로그램 설정 파일
"""

import os
import re
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# DeepSeek Vision API 설정 (필수)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# API 키 검증
if not DEEPSEEK_API_KEY:
    error_message = """
    ============================================================
    ❌ DeepSeek Vision API 키가 설정되지 않았습니다.
    
    📌 API 키 발급 방법:
    1. DeepSeek 플랫폼 가입: https://platform.deepseek.com
    2. API Keys 메뉴에서 새 키 생성
    3. API 키 복사
    
    📝 설정 방법:
    .env 파일을 생성하고 다음 내용 입력:
    
    DEEPSEEK_API_KEY=여기에_DeepSeek_API_키_입력
    
    💰 비용 정보:
    - DeepSeek-V3: $0.27/1M tokens
    - 이미지 1장 ≈ 1,000 tokens = $0.0003 (약 0.4원)
    - CLOVA OCR 대비 60배 저렴!
    
    자세한 내용: README.md 참고
    ============================================================
    """
    raise ValueError(error_message)

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