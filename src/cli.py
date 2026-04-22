#!/usr/bin/env python3
"""
CM 현장 문서 OCR - CLI 버전 (DeepSeek Vision)

실무 사용법:
 python src/cli.py sample_data/

테스트 사용법 (단일 파일):
 python src/cli.py -f sample_data/sample_001.png
"""

import argparse
import os
import sys
from pathlib import Path
import csv
import json

from ocr.claude_engine import ClaudeEngine
from config import CLAUDE_API_KEY, TABLE_HEADERS


def process_image(image_path, claude_engine):
    """단일 이미지 처리 (Claude Vision)"""
    print(f"처리 중: {Path(image_path).name}")
    
    # Claude Vision으로 표 추출
    try:
        print(f" 🔍 Claude Vision으로 표 추출 중...")
        table_data = claude_engine.extract_table(image_path)
        
        # JSON 데이터를 CSV 행으로 변환 (13개 항목)
        rows = []
        for item in table_data:
            row = []
            for header in TABLE_HEADERS:
                # 헤더와 정확히 일치하는 키 찾기
                if header in item:
                    row.append(item[header])
                else:
                    # 기본값 (빈 셀)
                    row.append("0.00")
            
            # 정확히 13개 값인지 확인
            if len(row) != 13:
                print(f"⚠️  경고: 측점 {item.get('측점', '알수없음')}의 값이 13개가 아닙니다: {len(row)}개")
                # 부족한 값 채우기
                while len(row) < 13:
                    row.append("0.00")
                # 초과한 값 자르기
                row = row[:13]
            
            rows.append(row)
        
        print(f" ✅ {len(rows)}개 측점 추출 완료\n")
        return rows
        
    except Exception as e:
        print(f" ❌ 오류: {str(e)}\n")
        return []


def save_to_csv(rows, output_path):
    """CSV 파일로 저장"""
    import os
    import time
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 파일이 열려있으면 새 파일명 생성
    original_path = output_path
    counter = 1
    
    while True:
        try:
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(TABLE_HEADERS)  # 헤더
                writer.writerows(rows)          # 데이터
            break  # 성공하면 루프 탈출
        
        except PermissionError:
            # 파일이 열려있으면 번호 붙여서 재시도
            base = original_path.rsplit('.', 1)[0]
            ext = original_path.rsplit('.', 1)[1] if '.' in original_path else 'csv'
            output_path = f"{base}_{counter}.{ext}"
            counter += 1
            
            if counter > 5:
                # 5번 시도 후 포기
                print(f"\n❌ 오류: CSV 파일 저장 실패")
                print(f" {original_path} 파일이 다른 프로그램에서 열려있습니다.")
                print(f" 파일을 닫고 다시 시도하세요.")
                raise
            
            print(f"⚠️ {original_path} 파일이 사용 중입니다.")
            print(f" 대신 {output_path}에 저장합니다...")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='CM 현장 문서 OCR - 수량표 배치 추출 (DeepSeek Vision)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
 # 폴더 전체 처리 (실무용)
 python src/cli.py sample_data/
 
 # 출력 폴더 지정
 python src/cli.py sample_data/ -o results/
 
 # 단일 파일 (테스트용)
 python src/cli.py -f sample_data/sample_001.png
 
 💰 비용 정보:
 - DeepSeek-V3: $0.27/1M tokens
 - 이미지 1장 ≈ 1,000 tokens = $0.0003 (약 0.4원)
 - CLOVA OCR 대비 60배 저렴!
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
    
    # Claude Vision 엔진 초기화
    print("=" * 60)
    print("CM 현장 문서 OCR - Claude Vision 배치 처리")
    print("=" * 60)
    print("\n🔧 Claude Vision 엔진 초기화 중...")
    claude_engine = ClaudeEngine(CLAUDE_API_KEY)
    print("✅ 초기화 완료!\n")
    
    # 처리할 파일 목록
    if args.file:
        # 테스트용: 단일 파일
        print("ℹ️ 테스트 모드: 단일 파일 처리\n")
        files = [Path(args.file)]
        output_name = Path(args.file).stem
    else:
        # 실무용: 폴더 전체
        folder = Path(args.directory)
        files = sorted(
            list(folder.glob('*.png')) + 
            list(folder.glob('*.jpg')) + 
            list(folder.glob('*.jpeg'))
        )
        output_name = folder.name  # 폴더명을 CSV 파일명으로
        print(f"📁 폴더: {folder}")
        print(f"📄 발견된 이미지: {len(files)}개\n")
    
    if not files:
        print("❌ 처리할 이미지가 없습니다.")
        sys.exit(1)
    
    # 전체 데이터를 담을 리스트
    all_rows = []
    
    # 파일 처리
    print("-" * 60)
    success_count = 0
    for img_path in files:
        rows = process_image(img_path, claude_engine)
        if rows:
            all_rows.extend(rows)
            success_count += 1
    
    # 통합 CSV 저장
    if all_rows:
        output_path = Path(args.output) / f"{output_name}.csv"
        saved_path = save_to_csv(all_rows, output_path)
        
        print("=" * 60)
        print(f"✅ 완료! {success_count}/{len(files)} 파일 처리 성공")
        print(f"📊 총 {len(all_rows)}개 측점 추출")
        print(f"💰 예상 비용: 약 {len(files) * 1.5:.1f}원 (Haiku 4.5)")
        print(f"💾 저장: {saved_path}")
        print("=" * 60)
    else:
        print("❌ 추출된 데이터가 없습니다.")


if __name__ == '__main__':
    main()