# CM 현장 문서 OCR 프로그램

하수관로 공사 수량표를 자동으로 인식하여 Excel 데이터로 변환하는 CLI 프로그램입니다.
**DeepSeek Vision API**를 사용하여 이미지에서 직접 표 데이터를 추출합니다.

## 🔑 API 키 발급 (필수)

### 1. DeepSeek 플랫폼 가입
https://platform.deepseek.com

### 2. API 키 발급
1. 로그인 후 "API Keys" 메뉴
2. "Create new secret key" 클릭
3. 키 이름 입력 (예: "현장문서 OCR")
4. "Create" 클릭 후 키 복사

### 3. 비용 (매우 저렴!)
- **DeepSeek-V3**: $0.27/1M input tokens
- **이미지 1장**: 약 1,000 tokens = **$0.0003 (약 0.4원)**
- **CLOVA OCR 대비**: **60배 저렴!**
- **월 100장 처리**: 약 40원
- **월 1,000장 처리**: 약 400원

## 📥 설치

### 1. 저장소 클론
```bash
git clone https://github.com/DnielPark/construction-document-ocr.git
cd construction-document-ocr
```

### 2. 가상환경 생성 (권장)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# 또는 source venv/bin/activate  # Linux/Mac
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. API 키 설정
`.env` 파일 생성:
```bash
DEEPSEEK_API_KEY=여기에_DeepSeek_API_키_입력
```

## 🚀 사용법

### CLI 버전 (권장 - 배치 처리)

#### 폴더 단위 배치 처리
```bash
# sample_data/ 폴더의 모든 이미지 처리
python src/cli.py sample_data/

# 출력 폴더 지정
python src/cli.py sample_data/ -o results/
```

#### 단일 파일 테스트
```bash
python src/cli.py -f sample_data/sample_001.png
```

#### 출력 구조
```
output/
 └── sample_data.csv  # 모든 측점 통합 파일
```

### GUI 버전 (시각적 편집)
```bash
python src/main.py
```

1. 파일 선택으로 이미지 로드
2. 드래그로 텍스트 영역 선택 (선택적)
3. OCR 실행 버튼 클릭
4. 우측 테이블에서 결과 확인
5. Excel 저장 버튼으로 내보내기 (Week 4 구현)

## ❓ 문제 해결

### API 키 오류
`.env` 파일 확인:
- 파일 위치: 프로젝트 루트
- 키 형식: 공백 없이 정확히 입력
- `.env.example` 파일을 `.env`로 복사 후 키 입력

### 인식률 문제
- 이미지 해상도 확인 (300dpi 이상 권장)
- 스캔 품질 향상 (명암 대비, 선명도)
- DeepSeek Vision은 LLM 기반으로 맥락 이해 가능

### 네트워크 오류
- 인터넷 연결 확인 (DeepSeek API 접속 필요)
- 방화벽 설정 확인
- API 키 만료 확인 (DeepSeek 플랫폼에서 재발급)

### 비용 확인
- DeepSeek 플랫폼에서 사용량 확인 가능
- 예상보다 비용이 높다면 이미지 전처리 고려

## 📊 기술 스택
- **Vision 엔진**: DeepSeek Vision API (LLM 기반 이미지 이해)
- **이미지 처리**: OpenCV, Pillow
- **데이터 처리**: Pandas, Openpyxl
- **GUI 프레임워크**: PyQt5

## 🎯 DeepSeek Vision 장점
1. **통합 처리**: OCR + 테이블 파싱 + 데이터 정제 한 번에
2. **맥락 이해**: "지 반 고" → "지반고" 자동 수정
3. **구조화 출력**: 바로 JSON으로 깔끔한 데이터
4. **비용 효율**: CLOVA의 1/60, EasyOCR보다 똑똑함
5. **오류 보정**: LLM이 오타 자동 수정

## 📁 프로젝트 구조
```
src/
├── main.py              # GUI 프로그램 진입점
├── cli.py               # CLI 배치 처리
├── ui/                  # GUI 컴포넌트
│   ├── main_window.py   # 메인 윈도우
│   ├── image_viewer.py  # 이미지 뷰어
│   └── data_table.py    # 데이터 테이블
├── ocr/                 # OCR 엔진
│   ├── preprocessor.py  # 이미지 전처리
│   └── ocr_engine.py    # CLOVA OCR 처리
├── utils/               # 유틸리티
│   ├── table_parser.py  # 테이블 파싱
│   └── excel_export.py  # Excel 내보내기
└── config.py            # 설정 파일
```

## 📅 개발 계획
- Week 1: 기본 구조 및 UI 구현 ✅
- Week 2: DeepSeek Vision 엔진 통합 ✅
- Week 3: 테이블 파싱 알고리즘 ✅
- Week 4: Excel 내보내기 및 최적화 ⏳

## 🔄 아키텍처 진화
1. **초기**: EasyOCR (로컬 모델, 낮은 정확도)
2. **개선**: CLOVA OCR (API, 높은 정확도, 비용 문제)
3. **최종**: DeepSeek Vision (LLM 기반, 최고 정확도, 최저 비용)

## 📄 라이선스
MIT License