# CM 현장 문서 OCR 프로그램

건설 현장 문서(도면, 시방서, 검사표 등)의 텍스트를 인식하고 데이터를 추출하는 GUI 프로그램입니다.

## 기능
- 이미지 파일 로드 및 표시
- 드래그 앤 드롭으로 텍스트 영역 선택
- EasyOCR 기반 다국어 텍스트 인식
- 인식된 데이터를 테이블 형식으로 정리
- Excel 파일로 내보내기

## 기술 스택
- **GUI**: PyQt5
- **OCR**: EasyOCR (한국어, 영어, 중국어 지원)
- **이미지 처리**: OpenCV, Pillow
- **데이터 처리**: Pandas, Openpyxl

## 설치

### 환경 요구사항
- Python 3.12+
- Windows 10/11 (64-bit)

### 설치 방법

#### 1. 저장소 클론
```bash
git clone https://github.com/DnielPark/construction-document-ocr.git
cd construction-document-ocr
```

#### 2. 가상환경 생성 (권장)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# 또는 source venv/bin/activate  # Linux/Mac
```

#### 3. PyTorch CPU 버전 설치 (필수 - 먼저!)
```bash
pip install torch==2.11.0 torchvision==0.26.0 torchaudio==2.11.0 --index-url https://download.pytorch.org/whl/cpu
```

#### 4. 나머지 의존성 설치
```bash
pip install -r requirements.txt
```

### 실행
```bash
python src\main.py
```

### 문제 해결

**DLL 오류 발생 시:**
1. Visual C++ Redistributable 설치: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. PC 재부팅

**Pillow 호환성 오류:**
```bash
pip install --upgrade easyocr
```

**메모리 부족 오류:**
- 이미지 크기 줄이기
- 선택 영역 OCR 사용

## 사용법
```bash
python src/main.py
```

1. 파일 선택 또는 클립보드 붙여넣기로 이미지 로드
2. 드래그로 텍스트 영역 선택
3. OCR 실행 버튼 클릭
4. 우측 테이블에서 결과 확인
5. Excel 저장 버튼으로 내보내기

## 프로젝트 구조
```
src/
├── main.py              # 프로그램 진입점
├── ui/                  # GUI 컴포넌트
│   ├── main_window.py   # 메인 윈도우
│   ├── image_viewer.py  # 이미지 뷰어
│   └── data_table.py    # 데이터 테이블
├── ocr/                 # OCR 엔진
│   ├── preprocessor.py  # 이미지 전처리
│   └── ocr_engine.py    # OCR 처리
├── utils/               # 유틸리티
│   ├── table_parser.py  # 테이블 파싱
│   └── excel_export.py  # Excel 내보내기
└── config.py            # 설정 파일
```

## 개발 계획
- Week 1: 기본 구조 및 UI 구현
- Week 2: OCR 엔진 통합
- Week 3: 테이블 파싱 알고리즘
- Week 4: Excel 내보내기 및 최적화

## 라이선스
MIT License