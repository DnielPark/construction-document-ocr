#!/usr/bin/env python3
"""
CM 현장 문서 OCR - GUI 버전
API 키를 메모리에만 임시 저장 (파일 저장 안 함)
"""

import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading
import os
import subprocess
import platform
from pathlib import Path
from ocr.claude_engine import ClaudeEngine
from config import TABLE_HEADERS
import csv


class OCRGui:
    def __init__(self, root):
        self.root = root
        self.root.title("CM 현장 문서 OCR 프로그램")
        self.root.geometry("600x500")
        
        # API 키 (메모리에만 저장)
        self.api_key = None
        self.claude_engine = None
        
        # 선택된 폴더
        self.selected_folder = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # 상단: API 키 입력
        api_frame = tk.Frame(self.root, padx=10, pady=10)
        api_frame.pack(fill=tk.X)
        
        tk.Label(api_frame, text="Claude API 키:", font=("Arial", 10)).pack(anchor=tk.W)
        
        self.api_entry = tk.Entry(api_frame, width=50, show="*")
        self.api_entry.pack(fill=tk.X, pady=5)
        
        # 보안 안내
        warning_text = "⚠️ 보안 안내: API 키는 임시로만 사용되며, 파일에 저장되지 않습니다. 프로그램 종료 시 자동 삭제됩니다."
        tk.Label(api_frame, text=warning_text, fg="red", wraplength=550, justify=tk.LEFT).pack(anchor=tk.W)
        
        # 중간: 폴더 선택
        folder_frame = tk.Frame(self.root, padx=10, pady=10)
        folder_frame.pack(fill=tk.X)
        
        tk.Label(folder_frame, text="이미지 폴더:", font=("Arial", 10)).pack(anchor=tk.W)
        
        folder_select_frame = tk.Frame(folder_frame)
        folder_select_frame.pack(fill=tk.X, pady=5)
        
        self.folder_label = tk.Label(folder_select_frame, text="(폴더를 선택하세요)", fg="gray")
        self.folder_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(folder_select_frame, text="폴더 선택", command=self.select_folder).pack(side=tk.RIGHT)
        
        # 실행 버튼
        button_frame = tk.Frame(self.root, padx=10, pady=10)
        button_frame.pack(fill=tk.X)
        
        # OCR 실행 버튼
        self.run_button = tk.Button(button_frame, text="OCR 실행", command=self.run_ocr, 
                                     bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), height=2)
        self.run_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # 출력 폴더 열기 버튼
        self.open_folder_button = tk.Button(button_frame, text="📁 출력 폴더 열기", 
                                             command=self.open_output_folder,
                                             bg="#2196F3", fg="white", font=("Arial", 12, "bold"), height=2)
        self.open_folder_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 하단: 진행 상황 표시
        log_frame = tk.Frame(self.root, padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(log_frame, text="📊 진행 상황:", font=("Arial", 10)).pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def log(self, message):
        """로그 메시지 추가"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def select_folder(self):
        """폴더 선택 다이얼로그"""
        folder = filedialog.askdirectory(title="이미지 폴더를 선택하세요")
        if folder:
            self.selected_folder = folder
            self.folder_label.config(text=folder, fg="black")
            self.log(f"📁 폴더 선택됨: {folder}")
        
    def open_output_folder(self):
        """출력 폴더 열기"""
        output_dir = Path("output")
        
        if not output_dir.exists():
            messagebox.showwarning("경고", "출력 폴더가 아직 생성되지 않았습니다.")
            return
        
        try:
            if platform.system() == "Windows":
                os.startfile(output_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", output_dir])
            else:  # Linux
                subprocess.run(["xdg-open", output_dir])
        except Exception as e:
            messagebox.showerror("오류", f"폴더를 열 수 없습니다: {str(e)}")
        
    def run_ocr(self):
        """OCR 실행 (별도 스레드에서)"""
        # API 키 확인
        api_key = self.api_entry.get().strip()
        if not api_key:
            messagebox.showerror("오류", "Claude API 키를 입력하세요.")
            return
        
        # 폴더 확인
        if not self.selected_folder:
            messagebox.showerror("오류", "이미지 폴더를 선택하세요.")
            return
        
        # 메모리에 API 키 저장
        self.api_key = api_key
        
        # 버튼 비활성화
        self.run_button.config(state=tk.DISABLED, text="처리 중...")
        
        # 별도 스레드에서 실행
        thread = threading.Thread(target=self.process_folder)
        thread.start()
        
    def process_folder(self):
        """폴더 내 이미지 처리"""
        try:
            # Claude 엔진 초기화
            self.log("🔧 Claude Vision 엔진 초기화 중...")
            self.claude_engine = ClaudeEngine(self.api_key)
            self.log("✅ 초기화 완료!\n")
            
            # 이미지 파일 찾기
            folder = Path(self.selected_folder)
            files = sorted(
                list(folder.glob('*.png')) + 
                list(folder.glob('*.jpg')) + 
                list(folder.glob('*.jpeg'))
            )
            
            if not files:
                self.log("❌ 이미지 파일이 없습니다.")
                messagebox.showwarning("경고", "선택한 폴더에 이미지가 없습니다.")
                return
            
            self.log(f"📄 발견된 이미지: {len(files)}개\n")
            self.log("-" * 60)
            
            # 전체 데이터
            all_rows = []
            success_count = 0
            
            # 파일 처리
            for img_path in files:
                self.log(f"처리 중: {img_path.name}")
                
                try:
                    # Claude Vision으로 표 추출
                    table_data = self.claude_engine.extract_table(img_path)
                    
                    # JSON → CSV 행 변환
                    for item in table_data:
                        row = [item.get(header, "0.00") for header in TABLE_HEADERS]
                        all_rows.append(row)
                    
                    self.log(f"✅ {len(table_data)}개 측점 추출 완료\n")
                    success_count += 1
                    
                except Exception as e:
                    self.log(f"❌ 오류: {str(e)}\n")
            
            # CSV 저장
            if all_rows:
                output_dir = Path("output")
                output_dir.mkdir(exist_ok=True)
                output_path = output_dir / f"{folder.name}.csv"
                
                with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(TABLE_HEADERS)
                    writer.writerows(all_rows)
                
                self.log("=" * 60)
                self.log(f"✅ 완료! {success_count}/{len(files)} 파일 처리 성공")
                self.log(f"📊 총 {len(all_rows)}개 측점 추출")
                self.log(f"💾 저장: {output_path}")
                self.log("=" * 60)
                
                messagebox.showinfo("완료", f"처리 완료!\n\n파일: {output_path}\n측점: {len(all_rows)}개")
            else:
                self.log("❌ 추출된 데이터가 없습니다.")
                messagebox.showerror("오류", "추출된 데이터가 없습니다.")
                
        except Exception as e:
            self.log(f"\n❌ 오류 발생: {str(e)}")
            messagebox.showerror("오류", str(e))
            
        finally:
            # 버튼 다시 활성화
            self.run_button.config(state=tk.NORMAL, text="OCR 실행")
            
            # API 키 메모리에서 삭제
            self.api_key = None
            self.claude_engine = None


def main():
    root = tk.Tk()
    app = OCRGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
