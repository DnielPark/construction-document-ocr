"""
데이터 테이블 위젯
"""

from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt


class DataTable(QTableWidget):
    """데이터 테이블 위젯"""
    
    def __init__(self, columns=20, headers=None):
        super().__init__()
        self.columns = columns
        self.headers = headers or [f"컬럼 {i+1}" for i in range(columns)]
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        # 기본 행/열 설정
        self.setColumnCount(self.columns)
        self.setRowCount(0)  # 초기에는 행 없음
        
        # 헤더 설정
        self.setHorizontalHeaderLabels(self.headers)
        
        # 테이블 스타일 설정
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        
        # 편집 가능 설정
        self.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        
    def add_row(self, data):
        """새 행 추가"""
        row_position = self.rowCount()
        self.insertRow(row_position)
        
        for col, value in enumerate(data[:self.columns]):
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row_position, col, item)
            
    def update_cell(self, row, col, value):
        """셀 값 업데이트"""
        if 0 <= row < self.rowCount() and 0 <= col < self.columns:
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, col, item)
            
    def get_row_data(self, row):
        """행 데이터 가져오기"""
        if 0 <= row < self.rowCount():
            return [self.item(row, col).text() if self.item(row, col) else "" 
                    for col in range(self.columns)]
        return []
        
    def get_all_data(self):
        """모든 데이터 가져오기"""
        data = []
        for row in range(self.rowCount()):
            data.append(self.get_row_data(row))
        return data
        
    def clear_table(self):
        """테이블 초기화"""
        self.setRowCount(0)
        
    def set_headers(self, headers):
        """헤더 설정"""
        if len(headers) == self.columns:
            self.headers = headers
            self.setHorizontalHeaderLabels(headers)
            
    def resize_columns(self, columns):
        """컬럼 수 조정"""
        if columns > 0:
            self.columns = columns
            self.setColumnCount(columns)
            
            # 헤더 업데이트
            if len(self.headers) != columns:
                self.headers = [f"컬럼 {i+1}" for i in range(columns)]
            self.setHorizontalHeaderLabels(self.headers)