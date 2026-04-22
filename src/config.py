"""
프로그램 설정 파일
"""

import os
import re
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Claude Vision API 설정 (필수)
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# API 키 검증
if not CLAUDE_API_KEY:
    error_message = """
    ============================================================
    ❌ Claude Vision API 키가 설정되지 않았습니다.
    
    📌 API 키 발급 방법:
    1. Anthropic 콘솔 가입: https://console.anthropic.com
    2. API Keys 메뉴에서 새 키 생성
    3. API 키 복사 (sk-ant-... 형식)
    
    📝 설정 방법:
    .env 파일을 생성하고 다음 내용 입력:
    
    CLAUDE_API_KEY=여기에_Claude_API_키_입력
    
    💰 비용 정보:
    - Claude 3.5 Sonnet: $3/1M input tokens
    - 이미지 1장 ≈ 1,000 tokens = $0.003 (약 4원)
    - CLOVA OCR 대비 6배 저렴!
    - Vision 지원 완벽, 표 인식 정확도 최고
    
    자세한 내용: README.md 참고
    ============================================================
    """
    raise ValueError(error_message)

# UI 설정
WINDOW_TITLE = "CM 현장 문서 OCR 프로그램"
WINDOW_SIZE = (1200, 800)  # 너비, 높이

# 테이블 설정 - 실제 표 구조 (13개 항목)
TABLE_HEADERS = [
    "측점",
    "지반고",
    "관저고",
    "터파기 육상",
    "터파기 수중",
    "되메우기 관주위",
    "되메우기 관상단",
    "파취 및 복구 ASP",
    "파취 및 복구 Con'c",
    "파취 및 복구 보도블럭",
    "모래부설",
    "보조기층",
    "동상방지층"
]

TABLE_COLUMNS = len(TABLE_HEADERS)  # 13개

# 정규식 패턴
STATION_PATTERN = re.compile(r'^\d+\+\d+\.\d+$')

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