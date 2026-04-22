"""
프로그램 설정 파일
"""

import os
import re
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# CLOVA OCR 설정 (필수)
CLOVA_API_URL = os.getenv("CLOVA_API_URL")
CLOVA_SECRET_KEY = os.getenv("CLOVA_SECRET_KEY")

# API 키 검증
if not CLOVA_API_URL or not CLOVA_SECRET_KEY:
    error_message = """
    ============================================================
    ❌ CLOVA OCR API 키가 설정되지 않았습니다.
    
    📌 API 키 발급 방법:
    1. 네이버 클라우드 가입: https://www.ncloud.com
    2. CLOVA OCR 서비스 신청
    3. API 키 발급 (월 1,000건 무료)
    
    📝 설정 방법:
    .env 파일을 생성하고 다음 내용 입력:
    
    CLOVA_API_URL=https://naveropenapi.apigw.ntruss.com/ocr/v1/general
    CLOVA_SECRET_KEY=여기에_발급받은_키_입력
    
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