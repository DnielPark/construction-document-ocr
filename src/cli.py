#!/usr/bin/env python3
"""
CM 현장 문서 OCR - CLI 버전 (배치 처리)

실무 사용법:
 python src/cli.py sample_data/

테스트 사용법 (단일 파일):
 python src/cli.py -f sample_data/sample_001.png
"""

import argparse
import os
import sys
from pathlib import Path
import cv2

from ocr.ocr_engine import OCREngine
from utils.table_parser import TableParser
from config import OCR_LANGUAGES, OCR_GPU, TABLE_COLUMNS, TABLE_HEADERS


def process_image(image_path, output_dir, ocr_engine, parser):
    """단일 이미지 처리"""
    print(f"처리 중: {image_path}")
    
    # 이미지 로드
    image = cv2.imread(str(image_path))
    if image is None:
        print(f" ❌ 오류: 이미지를 읽을 수 없습니다.")
        return False
    
    # OCR 실행
    print(f" 🔍 OCR 실행 중...")
    results = ocr_engine.recognize_with_coordinates(image)
    print(f" ✅ {len(results)}개 텍스트 인식됨")
    
    # 테이블 파싱
    table_rows = parser.parse_ocr_results(results)
    aligned_rows = parser.align_to_columns(table_rows, TABLE_COLUMNS)
    print(f" 📊 {len(aligned_rows)}개 행 파싱됨")
    
    # CSV 저장
    output_path = Path(output_dir) / f"{Path(image_path).stem}.csv"
    save_to_csv(aligned_rows, output_path)
    print(f" 💾 저장: {output_path}\n")
    
    return True


def save_to_csv(rows, output_path):
    """CSV 파일로 저장"""
    import csv
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(TABLE_HEADERS)  # 헤더
        writer.writerows(rows)          # 데이터


def main():
    parser = argparse.ArgumentParser(
        description='CM 현장 문서 OCR - 수량표 배치 추출',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
 # 폴더 전체 처리 (실무용)
 python src/cli.py sample_data/
 
 # 출력 폴더 지정
 python src/cli.py sample_data/ -o results/
 
 # 단일 파일 (테스트용)
 python src/cli.py -f sample_data/sample_001.png
 """
    )
    
    # 위치 인자: 폴더 경로 (기본)
    parser.add_argument(
        'directory',
        nargs='?',
        help='처리할 이미지 폴더 경로'
    )
    
    # 옵션 인자
    parser.add_argument(
        '-f', '--file',
        help='[테스트용] 단일 이미지 파일 경로'
    )
    parser.add_argument(
        '-o', '--output',
        default='output',
        help='출력 폴더 (기본값: output/)'
    )
    
    args = parser.parse_args()
    
    # 입력 확인
    if not args.file and not args.directory:
        parser.print_help()
        print("\n❌ 오류: 처리할 폴더 또는 파일을 지정하세요.")
        sys.exit(1)
    
    # OCR 엔진 초기화
    print("=" * 60)
    print("CM 현장 문서 OCR - 배치 처리")
    print("=" * 60)
    print("\n🔧 OCR 엔진 초기화 중... (최초 1-2분 소요)")
    ocr_engine = OCREngine(OCR_LANGUAGES, OCR_GPU)
    table_parser = TableParser()
    print("✅ 초기화 완료!\n")
    
    # 처리할 파일 목록
    if args.file:
        # 테스트용: 단일 파일
        print("ℹ️ 테스트 모드: 단일 파일 처리\n")
        files = [Path(args.file)]
    else:
        # 실무용: 폴더 전체
        folder = Path(args.directory)
        files = sorted(
            list(folder.glob('*.png')) + 
            list(folder.glob('*.jpg')) + 
            list(folder.glob('*.jpeg'))
        )
        print(f"📁 폴더: {folder}")
        print(f"📄 발견된 이미지: {len(files)}개\n")
    
    if not files:
        print("❌ 처리할 이미지가 없습니다.")
        sys.exit(1)
    
    # 파일 처리
    print("-" * 60)
    success_count = 0
    for img_path in files:
        if process_image(img_path, args.output, ocr_engine, table_parser):
            success_count += 1
    
    # 결과 요약
    print("=" * 60)
    print(f"✅ 완료! {success_count}/{len(files)} 파일 처리 성공")
    print(f"📂 결과 폴더: {args.output}/")
    print("=" * 60)


if __name__ == '__main__':
    main()