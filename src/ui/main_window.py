"""
메인 윈도우 클래스
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QToolBar, QAction, QStatusBar, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap

from config import WINDOW_TITLE, WINDOW_SIZE, TABLE_COLUMNS, TABLE_HEADERS
from ui.image_viewer import ImageViewer
from ui.data_table import DataTable


class MainWindow(QMainWindow):
    """메인 윈도우 클래스"""
    
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, *WINDOW_SIZE)
        
        # 중앙 위젯 생성
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        
        # 툴바 생성
        self.create_toolbar()
        
        # 스플리터 생성 (좌우 40:60 비율)
        splitter = QSplitter(Qt.Horizontal)
        
        # 좌측: 이미지 뷰어 (40%)
        self.image_viewer = ImageViewer()
        splitter.addWidget(self.image_viewer)
        
        # 우측: 데이터 테이블 (60%)
        self.data_table = DataTable(TABLE_COLUMNS, TABLE_HEADERS)
        splitter.addWidget(self.data_table)
        
        # 스플리터 비율 설정
        splitter.setSizes([int(WINDOW_SIZE[0] * 0.4), int(WINDOW_SIZE[0] * 0.6)])
        
        main_layout.addWidget(splitter)
        
        # 상태바 생성
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("준비됨")
        
    def create_toolbar(self):
        """툴바 생성"""
        toolbar = QToolBar("메인 툴바")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # 파일 선택 액션
        file_action = QAction(QIcon(), "파일 선택", self)
        file_action.setStatusTip("이미지 파일 선택")
        file_action.triggered.connect(self.open_file)
        toolbar.addAction(file_action)
        
        # 클립보드 붙여넣기 액션
        paste_action = QAction(QIcon(), "클립보드 붙여넣기", self)
        paste_action.setStatusTip("클립보드에서 이미지 붙여넣기")
        paste_action.triggered.connect(self.paste_from_clipboard)
        toolbar.addAction(paste_action)
        
        toolbar.addSeparator()
        
        # OCR 실행 액션
        ocr_action = QAction(QIcon(), "OCR 실행", self)
        ocr_action.setStatusTip("선택 영역 OCR 실행")
        ocr_action.triggered.connect(self.run_ocr)
        toolbar.addAction(ocr_action)
        
        # Excel 저장 액션
        save_action = QAction(QIcon(), "Excel 저장", self)
        save_action.setStatusTip("테이블 데이터를 Excel로 저장")
        save_action.triggered.connect(self.save_to_excel)
        toolbar.addAction(save_action)
        
    def open_file(self):
        """파일 선택 다이얼로그"""
        from PyQt5.QtWidgets import QFileDialog
        from config import SUPPORTED_IMAGE_FORMATS
        
        file_filter = "이미지 파일 (" + " ".join(SUPPORTED_IMAGE_FORMATS) + ")"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "이미지 파일 선택", "", file_filter
        )
        
        if file_path:
            self.current_image_path = file_path
            if self.image_viewer.load_image(file_path):
                self.status_bar.showMessage(f"파일 로드됨: {file_path}")
            else:
                QMessageBox.warning(self, "오류", "이미지 파일을 로드할 수 없습니다.")
                
    def paste_from_clipboard(self):
        """클립보드에서 이미지 붙여넣기"""
        clipboard = QApplication.clipboard()
        pixmap = clipboard.pixmap()
        
        if not pixmap.isNull():
            self.image_viewer.set_pixmap(pixmap)
            self.current_image_path = None
            self.status_bar.showMessage("클립보드 이미지 붙여넣기 완료")
        else:
            QMessageBox.warning(self, "오류", "클립보드에 이미지가 없습니다.")
            
    def run_ocr(self):
        """OCR 실행"""
        # TODO: OCR 엔진 연동
        self.status_bar.showMessage("OCR 실행 (구현 중)")
        QMessageBox.information(self, "알림", "OCR 기능은 Week 2에서 구현됩니다.")
        
    def save_to_excel(self):
        """Excel로 저장"""
        # TODO: Excel 내보내기 연동
        self.status_bar.showMessage("Excel 저장 (구현 중)")
        QMessageBox.information(self, "알림", "Excel 저장 기능은 Week 4에서 구현됩니다.")


# PyQt5.QtWidgets 모듈 임포트
from PyQt5.QtWidgets import QApplication