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
import time
from pathlib import Path
from PIL import Image, ImageGrab, ImageTk
from ocr.claude_engine import ClaudeEngine
from config import TABLE_HEADERS
import csv


class OCRGui:
    def __init__(self, root):
        self.root = root
        self.root.title("CM 현장 문서 OCR 프로그램")
        self.root.geometry("900x600")
        
        # API 키 (메모리에만 저장)
        self.api_key = None
        self.claude_engine = None
        
        # 선택된 폴더
        self.selected_folder = None
        
        # 캡쳐 관련
        self.capture_folder = None
        self.capture_count = 0
        
        # 다중 선택
        self.selected_thumbnails = set()
        
        self.create_widgets()
        
    def create_widgets(self):
        # 메인 프레임 (좌우 분할)
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 왼쪽 프레임 (컨트롤)
        left_frame = tk.Frame(main_container, padx=10, pady=10, width=350)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        left_frame.pack_propagate(False)
        
        # 오른쪽 프레임 (캡쳐 썸네일)
        right_frame = tk.Frame(main_container, padx=10, pady=10, bg="#f0f0f0")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # === 왼쪽: 기존 컨트롤 ===
        
        # API 키
        tk.Label(left_frame, text="Claude API 키:", font=("Arial", 10)).pack(anchor=tk.W)
        self.api_entry = tk.Entry(left_frame, width=40, show="*")
        self.api_entry.pack(fill=tk.X, pady=5)
        
        warning_text = "⚠️ API 키는 임시 저장 (종료 시 삭제)"
        tk.Label(left_frame, text=warning_text, fg="red", wraplength=330).pack(anchor=tk.W, pady=(0, 10))
        
        # 구분선
        tk.Frame(left_frame, height=2, bg="gray").pack(fill=tk.X, pady=10)
        
        # OCR 폴더 선택
        tk.Label(left_frame, text="OCR 처리 폴더:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        ocr_folder_frame = tk.Frame(left_frame)
        ocr_folder_frame.pack(fill=tk.X, pady=5)
        
        self.folder_label = tk.Label(ocr_folder_frame, text="(폴더 선택)", fg="gray", anchor=tk.W)
        self.folder_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(ocr_folder_frame, text="폴더 선택", command=self.select_folder).pack(side=tk.RIGHT)
        
        # 버튼들
        tk.Frame(left_frame, height=10).pack()
        
        self.run_button = tk.Button(left_frame, text="OCR 실행", command=self.run_ocr,
                                     bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), height=2)
        self.run_button.pack(fill=tk.X, pady=2)
        
        self.open_folder_button = tk.Button(left_frame, text="📁 출력 폴더 열기",
                                             command=self.open_output_folder,
                                             bg="#2196F3", fg="white", font=("Arial", 11, "bold"), height=2)
        self.open_folder_button.pack(fill=tk.X, pady=2)
        
        # 구분선
        tk.Frame(left_frame, height=2, bg="gray").pack(fill=tk.X, pady=10)
        
        # 캡쳐 모드
        tk.Label(left_frame, text="화면 캡쳐:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.capture_button = tk.Button(left_frame, text="📸 캡쳐 모드", command=self.start_capture_mode,
                                         bg="#FF9800", fg="white", font=("Arial", 11, "bold"), height=2)
        self.capture_button.pack(fill=tk.X, pady=5)
        
        # 진행 상황
        tk.Frame(left_frame, height=10).pack()
        tk.Label(left_frame, text="📊 진행 상황:", font=("Arial", 10)).pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(left_frame, height=12, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # === 오른쪽: 캡쳐 썸네일 ===
        
        # 상단 정보 바
        info_bar = tk.Frame(right_frame, bg="#f0f0f0")
        info_bar.pack(fill=tk.X)
        
        tk.Label(info_bar, text="저장 폴더:", font=("Arial", 10), bg="#f0f0f0").pack(side=tk.LEFT)
        
        self.capture_folder_label = tk.Label(info_bar, text="(미선택)",
                                              fg="gray", bg="#f0f0f0", anchor=tk.W)
        self.capture_folder_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        tk.Button(info_bar, text="폴더 변경", command=self.select_capture_folder,
                  font=("Arial", 9)).pack(side=tk.RIGHT)
        
        self.capture_count_label = tk.Label(info_bar, text="총 0개",
                                             font=("Arial", 10, "bold"), bg="#f0f0f0")
        self.capture_count_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # 스크롤 가능한 캔버스
        canvas_frame = tk.Frame(right_frame, bg="white", relief=tk.SUNKEN, bd=1)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.thumbnail_canvas = tk.Canvas(canvas_frame, bg="white")
        scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.thumbnail_canvas.yview)
        
        self.thumbnail_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.thumbnail_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 썸네일을 담을 프레임
        self.thumbnail_frame = tk.Frame(self.thumbnail_canvas, bg="white")
        self.thumbnail_canvas.create_window((0, 0), window=self.thumbnail_frame, anchor=tk.NW)
        
        self.thumbnail_frame.bind("<Configure>", 
            lambda e: self.thumbnail_canvas.configure(scrollregion=self.thumbnail_canvas.bbox("all")))
        
    def log(self, message):
        """로그 메시지 추가"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def select_folder(self):
        """OCR 폴더 선택 다이얼로그"""
        folder = filedialog.askdirectory(title="이미지 폴더를 선택하세요")
        if folder:
            self.selected_folder = folder
            self.folder_label.config(text=folder, fg="black")
            self.log(f"📁 OCR 폴더 선택됨: {folder}")
    
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
    
    def select_capture_folder(self):
        """캡쳐 저장 폴더 선택 (폴더 변경 버튼)"""
        folder = filedialog.askdirectory(title="캡쳐 이미지를 저장할 폴더를 선택하세요")
        if folder:
            self.capture_folder = folder
            self.capture_folder_label.config(text=folder, fg="black")
            self.log(f"📁 캡쳐 저장 폴더 변경: {folder}")
            self.refresh_thumbnails()
    
    def start_capture_mode(self):
        """캡쳐 모드 시작 - 즉시 화면 캡쳐"""
        # 폴더 미선택 시 경고
        if not self.capture_folder:
            messagebox.showwarning("경고", "먼저 저장 폴더를 선택하세요.")
            return
        
        # 화면 캡쳐 시작
        self.do_screen_capture()
    
    def do_screen_capture(self):
        """화면 캡쳐 실행 (듀얼 모니터 지원)"""
        self.log("📸 화면을 드래그하여 영역을 선택하세요... (ESC: 취소)")
        
        # 오버레이 창 생성 - fullscreen=True가 모든 모니터 자동 커버
        capture_window = tk.Toplevel(self.root)
        capture_window.attributes("-fullscreen", True)
        capture_window.attributes("-alpha", 0.3)
        capture_window.attributes("-topmost", True)
        capture_window.configure(bg="black")
        
        canvas = tk.Canvas(capture_window, cursor="cross", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # 드래그 좌표 (화면 절대 좌표 기준)
        coords = {"start_x": None, "start_y": None, "rect": None}
        
        def on_mouse_down(event):
            coords["start_x"] = event.x_root
            coords["start_y"] = event.y_root
        
        def on_mouse_move(event):
            if coords["start_x"] is not None:
                if coords["rect"]:
                    canvas.delete(coords["rect"])
                # 화면 절대 좌표로 직접 사각형 그리기
                coords["rect"] = canvas.create_rectangle(
                    coords["start_x"], coords["start_y"],
                    event.x_root, event.y_root,
                    outline="red", width=3, tags="selection"
                )
        
        def on_mouse_up(event):
            if coords["start_x"] is None:
                return
            
            # 화면 절대 좌표 사용 (듀얼 모니터에서 음수 가능)
            x1 = min(coords["start_x"], event.x_root)
            y1 = min(coords["start_y"], event.y_root)
            x2 = max(coords["start_x"], event.x_root)
            y2 = max(coords["start_y"], event.y_root)
            
            # 최소 크기 체크
            if abs(x2 - x1) < 10 or abs(y2 - y1) < 10:
                capture_window.destroy()
                self.log("❌ 영역이 너무 작습니다.")
                return
            
            # 오버레이 닫기
            capture_window.destroy()
            
            # 잠시 대기 (오버레이가 사라지도록)
            self.root.after(100, lambda: self.capture_area(x1, y1, x2, y2))
        
        def on_escape(event):
            capture_window.destroy()
            self.log("❌ 캡쳐 취소됨")
        
        canvas.bind("<ButtonPress-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_move)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)
        capture_window.bind("<Escape>", on_escape)
    
    def capture_area(self, x1, y1, x2, y2):
        """선택 영역 캡쳐"""
        try:
            # 화면 캡쳐
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            
            # 파일명 생성
            self.capture_count += 1
            filename = f"capture_{self.capture_count:03d}.png"
            filepath = Path(self.capture_folder) / filename
            
            # 저장
            screenshot.save(filepath)
            
            self.log(f"✅ 캡쳐 완료: {filename}")
            
            # 썸네일 새로고침
            self.refresh_thumbnails()
            
            # 계속 캡쳐할지 묻기
            if messagebox.askyesno("캡쳐 완료", "계속 캡쳐하시겠습니까?"):
                self.do_screen_capture()
            
        except Exception as e:
            self.log(f"❌ 캡쳐 오류: {str(e)}")
    
    def refresh_thumbnails(self):
        """썸네일 그리드 갱신"""
        # 기존 썸네일 삭제
        for widget in self.thumbnail_frame.winfo_children():
            widget.destroy()
        
        # 선택 초기화
        self.selected_thumbnails.clear()
        
        if not self.capture_folder:
            return
        
        # 이미지 파일 찾기
        folder = Path(self.capture_folder)
        image_files = sorted(
            list(folder.glob("*.png")) + 
            list(folder.glob("*.jpg")) + 
            list(folder.glob("*.jpeg"))
        )
        
        # 개수 업데이트
        self.capture_count_label.config(text=f"총 {len(image_files)}개")
        
        # 썸네일 생성 (4열 그리드)
        cols = 4
        thumb_size = 120
        
        for idx, img_path in enumerate(image_files):
            try:
                # 썸네일 생성
                img = Image.open(img_path)
                img.thumbnail((thumb_size, thumb_size))
                photo = ImageTk.PhotoImage(img)
                
                # 프레임
                row = idx // cols
                col = idx % cols
                
                item_frame = tk.Frame(self.thumbnail_frame, bg="white", relief=tk.RAISED, bd=1)
                item_frame.grid(row=row, column=col, padx=5, pady=5)
                item_frame.img_path = img_path  # 경로 저장
                item_frame.is_selected = False
                
                # 이미지
                img_label = tk.Label(item_frame, image=photo, bg="white")
                img_label.image = photo  # 참조 유지
                img_label.pack()
                
                # 파일명
                tk.Label(item_frame, text=img_path.name, bg="white", font=("Arial", 8)).pack()
                
                # 우클릭 메뉴
                right_click_menu = tk.Menu(self.root, tearoff=0)
                right_click_menu.add_command(label="삭제", 
                    command=lambda p=img_path, f=item_frame: self.delete_single(p, f))
                
                def show_context_menu(event, menu=right_click_menu):
                    menu.tk_popup(event.x_root, event.y_root)
                
                # Ctrl+클릭 다중 선택
                def on_ctrl_click(event, frame=item_frame, path=img_path):
                    if event.state & 0x0004:  # Ctrl 키 눌림
                        self.toggle_selection(frame, path)
                
                # 일반 클릭 - 선택 해제
                def on_click(event):
                    if self.selected_thumbnails:
                        self.clear_selection()
                
                item_frame.bind("<Button-3>", show_context_menu)
                item_frame.bind("<Control-Button-1>", on_ctrl_click)
                item_frame.bind("<Button-1>", on_click)
                img_label.bind("<Button-3>", show_context_menu)
                img_label.bind("<Control-Button-1>", on_ctrl_click)
                
            except Exception as e:
                print(f"썸네일 생성 실패: {img_path.name} - {e}")
        
        # 선택 삭제 버튼 (우클릭 메뉴 대신 하단에 배치)
        if image_files:
            btn_frame = tk.Frame(self.thumbnail_frame, bg="white")
            row_count = (len(image_files) - 1) // cols + 1
            btn_frame.grid(row=row_count, column=0, columnspan=cols, pady=10)
            
            tk.Button(btn_frame, text="🗑️ 선택 삭제", command=self.delete_selected,
                      bg="#f44336", fg="white", font=("Arial", 10, "bold")).pack()
    
    def toggle_selection(self, frame, path):
        """Ctrl+클릭으로 선택 토글"""
        if frame in self.selected_thumbnails:
            # 선택 해제
            self.selected_thumbnails.discard(frame)
            frame.config(bg="white")
            for child in frame.winfo_children():
                try:
                    child.config(bg="white")
                except:
                    pass
        else:
            # 선택
            self.selected_thumbnails.add(frame)
            frame.config(bg="#b3d9ff")
            for child in frame.winfo_children():
                try:
                    child.config(bg="#b3d9ff")
                except:
                    pass
    
    def clear_selection(self):
        """선택 초기화"""
        for frame in self.selected_thumbnails:
            frame.config(bg="white")
            for child in frame.winfo_children():
                try:
                    child.config(bg="white")
                except:
                    pass
        self.selected_thumbnails.clear()
    
    def delete_single(self, path, frame):
        """단일 이미지 삭제"""
        if messagebox.askyesno("삭제 확인", f"'{path.name}'을(를) 삭제하시겠습니까?"):
            try:
                path.unlink()
                self.log(f"🗑️ 삭제: {path.name}")
                self.refresh_thumbnails()
            except Exception as e:
                self.log(f"❌ 삭제 오류: {str(e)}")
    
    def delete_selected(self):
        """선택된 이미지들 일괄 삭제"""
        if not self.selected_thumbnails:
            messagebox.showinfo("알림", "Ctrl+클릭으로 삭제할 이미지를 선택하세요.")
            return
        
        count = len(self.selected_thumbnails)
        if messagebox.askyesno("삭제 확인", f"선택한 {count}개 이미지를 삭제하시겠습니까?"):
            deleted = 0
            for frame in self.selected_thumbnails:
                try:
                    path = frame.img_path
                    path.unlink()
                    deleted += 1
                except Exception as e:
                    self.log(f"❌ 삭제 오류: {str(e)}")
            
            self.log(f"🗑️ {deleted}개 이미지 삭제 완료")
            self.refresh_thumbnails()
    
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
