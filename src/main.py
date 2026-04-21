#!/usr/bin/env python3
"""
CM 현장 문서 OCR 프로그램 메인 진입점
"""

import sys
from PyQt5.QtWidgets import QApplication

from ui.main_window import MainWindow
from config import WINDOW_TITLE


def main():
    """프로그램 메인 함수"""
    app = QApplication(sys.argv)
    app.setApplicationName(WINDOW_TITLE)
    
    # 메인 윈도우 생성
    window = MainWindow()
    window.show()
    
    # 이벤트 루프 실행
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()