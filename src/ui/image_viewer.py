"""
이미지 뷰어 위젯
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QMouseEvent, QPaintEvent, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import QMimeData


class ImageViewer(QScrollArea):
    """이미지 뷰어 위젯 (드래그 앤 드롭 영역 선택 지원)"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.selection_rect = None
        self.dragging = False
        self.start_point = QPoint()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWidgetResizable(True)
        
        # 이미지 표시 라벨
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        
        self.setWidget(self.image_label)
        
        # 드래그 앤 드롭 설정
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        
    def load_image(self, file_path):
        """이미지 파일 로드"""
        try:
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                return False
                
            self.set_pixmap(pixmap)
            return True
        except Exception:
            return False
            
    def set_pixmap(self, pixmap):
        """QPixmap 설정"""
        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()
        
    def mousePressEvent(self, event: QMouseEvent):
        """마우스 누름 이벤트"""
        if event.button() == Qt.LeftButton and self.image_label.pixmap():
            self.dragging = True
            self.start_point = event.pos()
            self.selection_rect = QRect(self.start_point, self.start_point)
            self.update()
            
    def mouseMoveEvent(self, event: QMouseEvent):
        """마우스 이동 이벤트"""
        if self.dragging and self.image_label.pixmap():
            self.selection_rect = QRect(self.start_point, event.pos()).normalized()
            self.update()
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        """마우스 놓음 이벤트"""
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            
            # 선택 영역이 유효한지 확인 (최소 크기)
            if self.selection_rect.width() > 10 and self.selection_rect.height() > 10:
                # TODO: 선택 영역 좌표를 메인 윈도우에 전달
                print(f"선택 영역: {self.selection_rect}")
            else:
                self.selection_rect = None
                
            self.update()
            
    def paintEvent(self, event: QPaintEvent):
        """페인트 이벤트 (선택 영역 그리기)"""
        super().paintEvent(event)
        
        if self.selection_rect and self.image_label.pixmap():
            painter = QPainter(self.viewport())
            painter.setPen(QPen(QColor(255, 0, 0, 180), 2, Qt.DashLine))
            painter.setBrush(QColor(255, 255, 0, 30))
            painter.drawRect(self.selection_rect)
            
    def get_selection_rect(self):
        """선택 영역 반환"""
        return self.selection_rect
        
    def clear_selection(self):
        """선택 영역 초기화"""
        self.selection_rect = None
        self.update()
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """드래그 진입 이벤트"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        """드롭 이벤트"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                # 이미지 파일인지 확인
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif')):
                    if self.load_image(file_path):
                        # 메인 윈도우에 파일 경로 알림 (시그널 필요)
                        print(f"드롭된 파일: {file_path}")
                    else:
                        print(f"이미지 로드 실패: {file_path}")
                else:
                    print(f"지원하지 않는 파일 형식: {file_path}")
            event.acceptProposedAction()