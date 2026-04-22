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
        # 이미지 확인
        pixmap = self.image_viewer.image_label.pixmap()
        if pixmap is None or pixmap.isNull():
            QMessageBox.warning(self, "오류", "이미지를 먼저 로드해주세요.")
            return
        
        self.status_bar.showMessage("OCR 처리 중...")
        QApplication.processEvents()  # UI 업데이트
        
        try:
            # QPixmap → numpy array 변환
            from PIL import Image
            import numpy as np
            import io
            
            # QPixmap을 바이트로 변환
            buffer = io.BytesIO()
            pixmap.save(buffer, "PNG")
            buffer.seek(0)
            
            # PIL Image로 로드
            pil_image = Image.open(buffer)
            image_array = np.array(pil_image)
            
            # OCR 엔진 초기화 (첫 실행 시)
            if not hasattr(self, 'ocr_engine'):
                from ocr.ocr_engine import OCREngine
                from config import OCR_LANGUAGES, OCR_GPU
                self.ocr_engine = OCREngine(OCR_LANGUAGES, OCR_GPU)
            
            # 선택 영역 확인
            selection_rect = self.image_viewer.get_selection_rect()
            
            if selection_rect:
                # 선택 영역 OCR
                rect = (
                    selection_rect.x(),
                    selection_rect.y(),
                    selection_rect.width(),
                    selection_rect.height()
                )
                text = self.ocr_engine.recognize_region(image_array, rect)
                
                # 테이블에 추가
                if text.strip():
                    self.data_table.add_row([text] + [""] * (self.data_table.columns - 1))
                    self.status_bar.showMessage(f"선택 영역 OCR 완료: {text[:50]}...")
                else:
                    QMessageBox.information(self, "알림", "선택 영역에서 텍스트를 인식하지 못했습니다.")
            else:
                # 전체 이미지 OCR
                results = self.ocr_engine.recognize_with_coordinates(image_array)
                
                # 결과 테이블에 표시
                self.display_ocr_results(results)
                
                self.status_bar.showMessage(f"OCR 완료! {len(results)}개 텍스트 인식됨")
                
        except Exception as e:
            QMessageBox.critical(self, "OCR 오류", f"OCR 처리 중 오류 발생:\n{str(e)}")
            self.status_bar.showMessage("OCR 실패")
            
    def display_ocr_results(self, results):
        """OCR 결과를 테이블에 표시 (임시)"""
        self.data_table.clear_table()
        
        for item in results:
            # 임시로 텍스트와 신뢰도만 표시
            row_data = [
                item['text'],
                f"{item['confidence']:.2f}",
                f"({item['center_x']:.0f}, {item['center_y']:.0f})"
            ] + [""] * (self.data_table.columns - 3)
            
            self.data_table.add_row(row_data)
        
    def save_to_excel(self):
        """Excel로 저장"""
        # TODO: Excel 내보내기 연동
        self.status_bar.showMessage("Excel 저장 (구현 중)")
        QMessageBox.information(self, "알림", "Excel 저장 기능은 Week 4에서 구현됩니다.")


# PyQt5.QtWidgets 모듈 임포트
from PyQt5.QtWidgets import QApplication