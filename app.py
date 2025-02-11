"""Gemini의 API를 이용하여 입력한 내용을 3출 요약하는 단측어.
에모업에 다음과 같은 제목 형식(예시)으로 새로운 메모가 생성이 되며, 해당 메모에 3줄 요약 결과
가 출력됩니다.
• 메모 제목 : Gemini 3줄요약 2025-02-11.화 1553.18
• 메모 내용 :
# Gemini 3줄요약
딥시크가 API 사용료를 대폭 인상하여 가격 경쟁력을 상실하고, 모텔 성능 또한 경쟁사에게 추격
당하고 있음.
4 구글 제미나이 2.0과 오픈A|의 GPT-40 미니 등 경쟁 모텔들이 더 저렴하거나 비슷한 가격에
더 나은 성능을 제공하며 시장 경쟁이 심화됨.
중국 서버 데이터 전송 및 보안 문제로 인해 딥시크 API 사용이 제한될 뿐만 아니라, 오픈소스 진
영의 빠른 추격으로 딥시크의 입지가 약화될 가능성이 큼.

RUN:

    프로그램과 같은 폴더에 gemini api key를 작성한 `GEMINI_API_KEY.txt` 파일을 만드세요.
    그리고 실행하세요.


"""

import json
import requests
import pyperclip
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import os, sys

class GeminiSummarizer:
    def __init__(self):
        self.GEMINI_API_KEY = self.load_api_key()
        self.SYSTEM_PROMPT = """다음 내용을 한국어로 3줄로 요약해취. 어미는 ~임, ~함과 같이 간결하게 할 것. 각 문장의 앞에는 그에 어울리는 이모지를 하나 넣을 것.
# Example Output
커서의 새로운 기능인 컴포저 에이전트는 사용자 명령에 따라 코드를 생성하고 실행 여부를 사용자가 결정함.
- AI EXE는 사용자 명령으로 코드 생성 후 사용자 실행, 시 EXE Auto는 모든 과정 자동으로 처리함.
컴포저 에이전트는 사용자에게 실행 권한을 부여하여 안전성을 확보했지만, 코드 이해도가 낮은사용자는 주의가 필요함."""
        self.API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    # def load_api_key(self):
    #     try:
    #         key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'GEMINI_API_KEY.txt')
    #         with open(key_file, 'r') as f:
    #             return f.read().strip()
    #     except Exception as e:
    #         messagebox.showerror("오류", "API 키 파일(GEMINI_API_KEY.txt)을 찾을 수 없거나 읽을 수 없습니다.")
    #         return None
    
    def load_api_key(self):
        try:
            # PyInstaller 번들 실행 여부 확인
            if getattr(sys, 'frozen', False):
                # PyInstaller로 실행된 경우
                application_path = os.path.dirname(sys.executable)
            else:
                # 일반 Python으로 실행된 경우
                application_path = os.path.dirname(os.path.abspath(__file__))
                
            key_file = os.path.join(application_path, 'GEMINI_API_KEY.txt')
            with open(key_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            messagebox.showerror("오류", f"API 키 파일(GEMINI_API_KEY.txt)을 찾을 수 없거나 읽을 수 없습니다.\n경로: {key_file}")
            return None
        
    def get_current_time(self):
        return datetime.now().strftime("%Y-%m-%d.%a %H%M.%S")
        
    def make_request(self, text):
        if not self.GEMINI_API_KEY:
            messagebox.showerror("오류", "유효한 API 키가 없습니다.")
            return None

        try:
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [{
                    "parts": [{"text": f"{self.SYSTEM_PROMPT}\n\n{text}"}]
                }]
            }
            
            url = f"{self.API_URL}?key={self.GEMINI_API_KEY}"
            response = requests.post(url, headers=headers, json=data)
            return response.json()
        except Exception as e:
            messagebox.showerror("오류", f"API 요청 중 오류가 발생했습니다: {str(e)}")
            return None
        
    def extract_summary(self, response):
        try:
            return response['candidates'][0]['content']['parts'][0]['text']
        except:
            return "요약 실패" + str(response)

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.summarizer = GeminiSummarizer()
        if not self.summarizer.GEMINI_API_KEY:  # 추가된 검증
            self.quit()
        self.setup_ui()
        
    def setup_ui(self):
        self.title("Gemini 3줄 요약")
        
        # 입력 텍스트
        input_frame = ttk.LabelFrame(self, text="요약할 텍스트를 입력하세요")
        input_frame.pack(padx=5, pady=5, fill="both", expand=True)
        self.input_text = tk.Text(input_frame, height=10)
        self.input_text.pack(padx=5, pady=5, fill="both", expand=True)
        
        # 실행 버튼
        self.submit_btn = ttk.Button(self, text="요약하기", command=self.process_text)
        self.submit_btn.pack(padx=5, pady=5)
        
    def process_text(self):
        input_text = self.input_text.get("1.0", "end-1c")
        
        if not input_text.strip():
            messagebox.showerror("오류", "텍스트를 입력해주세요.")
            return
            
        response = self.summarizer.make_request(input_text)
        if response:
            summary = self.summarizer.extract_summary(response)
            memo_time = self.summarizer.get_current_time()
            full_text = f"• 메모 제목 : Gemini 3줄요약 {memo_time}\n• 메모 내용 :\n# Gemini 3줄요약\n{summary}"
            
            try:
                pyperclip.copy(full_text)
                messagebox.showinfo("완료", "요약 결과가 클립보드에 복사되었습니다.")
                self.quit()  # 프로그램 종료
            except Exception as e:
                messagebox.showerror("오류", f"클립보드 복사 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    try:
        app = Application()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("오류", f"프로그램 실행 중 오류가 발생했습니다: {str(e)}")