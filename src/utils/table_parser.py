"""
테이블 파싱 유틸리티
"""

import re
from config import STATION_PATTERN, TABLE_HEADERS


class TableParser:
    """테이블 데이터 파서"""
    
    def __init__(self, y_tolerance=10):
        """
        Args:
            y_tolerance: Y좌표 차이 허용 범위 (같은 행으로 간주)
        """
        self.y_tolerance = y_tolerance
        
    def parse_ocr_results(self, ocr_results):
        """OCR 결과를 테이블 형식으로 파싱
        
        Args:
            ocr_results: OCR 엔진에서 반환된 결과 (좌표 포함)
            
        Returns:
            list: 행별로 정렬된 2D 리스트
        """
        if not ocr_results:
            return []
        
        # 1. Y좌표 기준으로 행 그룹화
        rows = self._group_by_rows(ocr_results)
        
        # 2. 각 행 내에서 X좌표 기준 정렬
        sorted_rows = self._sort_rows_by_x(rows)
        
        # 3. 측점 기준 행 분리
        table_rows = self._separate_by_station(sorted_rows)
        
        return table_rows
        
    def _group_by_rows(self, ocr_results):
        """Y좌표 클러스터링으로 행 그룹화"""
        if not ocr_results:
            return []
        
        # Y좌표 기준 정렬
        sorted_by_y = sorted(ocr_results, key=lambda x: x['center_y'])
        
        rows = []
        current_row = [sorted_by_y[0]]
        
        for item in sorted_by_y[1:]:
            # 이전 항목과 Y좌표 차이 확인
            prev_y = current_row[-1]['center_y']
            curr_y = item['center_y']
            
            if abs(curr_y - prev_y) <= self.y_tolerance:
                # 같은 행
                current_row.append(item)
            else:
                # 새로운 행 시작
                rows.append(current_row)
                current_row = [item]
        
        # 마지막 행 추가
        if current_row:
            rows.append(current_row)
        
        return rows
        
    def _sort_rows_by_x(self, rows):
        """각 행 내에서 X좌표 기준 정렬"""
        sorted_rows = []
        
        for row in rows:
            sorted_row = sorted(row, key=lambda x: x['center_x'])
            sorted_rows.append(sorted_row)
        
        return sorted_rows
        
    def _separate_by_station(self, sorted_rows):
        """측점 패턴으로 행 분리
        
        측점(예: 20+0.000)으로 시작하는 행만 추출
        """
        table_rows = []
        
        for row in sorted_rows:
            # 첫 번째 셀이 측점 패턴인지 확인
            if row and self._is_station(row[0]['text']):
                # 텍스트만 추출
                row_data = [item['text'] for item in row]
                table_rows.append(row_data)
        
        return table_rows
        
    def _is_station(self, text):
        """측점 형식 검증"""
        text = text.strip()
        return bool(STATION_PATTERN.match(text))
        
    def align_to_columns(self, table_rows, column_count=20):
        """행 데이터를 고정 컬럼 수에 맞춰 정렬
        
        Args:
            table_rows: 파싱된 테이블 행 리스트
            column_count: 목표 컬럼 수 (기본 20)
            
        Returns:
            list: 컬럼 수가 맞춰진 2D 리스트
        """
        aligned_rows = []
        
        for row in table_rows:
            if len(row) < column_count:
                # 부족한 컬럼은 빈 문자열로 채움
                row = row + [''] * (column_count - len(row))
            elif len(row) > column_count:
                # 초과 컬럼은 잘라냄
                row = row[:column_count]
            
            aligned_rows.append(row)
        
        return aligned_rows
        
    def detect_table_structure(self, text_blocks):
        """텍스트 블록에서 테이블 구조 감지"""
        # TODO: 향후 확장용
        print("테이블 구조 감지 (구현 중)")
        return {}
        
    def align_columns(self, data, column_count):
        """데이터를 컬럼에 맞춰 정렬 (이전 버전 호환용)"""
        return self.align_to_columns(data, column_count)