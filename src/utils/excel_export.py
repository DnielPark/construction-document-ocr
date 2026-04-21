"""
Excel 내보내기 유틸리티
"""

import pandas as pd
from datetime import datetime


class ExcelExporter:
    """Excel 내보내기 클래스"""
    
    def __init__(self):
        pass
        
    def export_table(self, data, headers, filename=None):
        """테이블 데이터를 Excel로 내보내기"""
        # TODO: Week 4에서 구현
        print(f"Excel 내보내기: {len(data)}행 (구현 중)")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ocr_result_{timestamp}.xlsx"
            
        return filename
        
    def create_dataframe(self, data, headers):
        """데이터프레임 생성"""
        # TODO: Week 4에서 구현
        print(f"데이터프레임 생성: {len(headers)}컬럼 (구현 중)")
        return pd.DataFrame()
        
    def save_to_excel(self, df, filename):
        """Excel 파일로 저장"""
        # TODO: Week 4에서 구현
        print(f"Excel 저장: {filename} (구현 중)")
        return True