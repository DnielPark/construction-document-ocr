# CM 현장 문서 OCR 프로그램

하수관로 공사 수량표를 자동으로 인식하여 Excel 데이터로 변환하는 CLI 프로그램입니다.

## 🔑 API 키 발급 (필수)

### 1. 네이버 클라우드 플랫폼 가입
https://www.ncloud.com

### 2. CLOVA OCR 신청
1. 콘솔 로그인
2. Services → AI·NAVER API → CLOVA OCR
3. "이용 신청하기" 클릭
4. 약관 동의 후 신청

### 3. API 인증키 발급
1. CLOVA OCR 콘솔 접속
2. "Domain" 생성
3. "Secret Key" 복사

### 4. 비용
- 월 1,000건 무료
- 이후 1.1원/건
- 현장 문서 처리 기준: 월 수백원 수준

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
CLOVA_API_URL=https://naveropenapi.apigw.ntruss.com/ocr/v1/general
CLOVA_SECRET_KEY=여기에_발급받은_시크릿_키_입력
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

### 인식률 낮음
- 이미지 해상도 확인 (300dpi 이상 권장)
- 스캔 품질 향상
- CLOVA OCR은 한글 문서에 최적화되어 있음

### 네트워크 오류
- 인터넷 연결 확인
- 방화벽 설정 확인 (CLOVA API 접근 허용)

## 📊 기술 스택
- **OCR 엔진**: 네이버 CLOVA OCR (한글 최적화)
- **이미지 처리**: OpenCV, Pillow
- **데이터 처리**: Pandas, Openpyxl
- **GUI 프레임워크**: PyQt5

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
- Week 2: CLOVA OCR 엔진 통합 ✅
- Week 3: 테이블 파싱 알고리즘 ✅
- Week 4: Excel 내보내기 및 최적화 ⏳

## 📄 라이선스
MIT License