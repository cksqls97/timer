import keyboard
import pyperclip
import datetime
import tkinter as tk
from tkinter import messagebox
import json
import os

# 설정 파일 경로
CONFIG_FILE = "timer_config.json"

def save_config(names, specials):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"names": names, "specials": specials}, f, ensure_ascii=False)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    return None

def start_timer(names, specials):
    # 타이머 데이터 초기화 (1~4번: 30분, 5~6번: 13분)
    users = {str(i+1): [names[i], 30, None] for i in range(4)}
    users['5'] = [specials[0], 13, None]
    users['6'] = [specials[1] if specials[1].strip() else "", 13, None]

    def update_clipboard():
        now = datetime.datetime.now()
        # 일반 인원 (1~4)
        out = []
        for i in range(1, 5):
            name, cool, next_t = users[str(i)]
            out.append(f"{name} {next_t.strftime('%H:%M')}" if next_t and now < next_t else name)
        
        # 특별 인원 (5~6)
        spec_out = []
        for i in range(5, 7):
            name, cool, next_t = users[str(i)]
            if name.strip(): # 이름이 있을 때만 표시
                spec_out.append(f"{name} {next_t.strftime('%H:%M')}" if next_t and now < next_t else name)
        
        final_text = f"{' '.join(out)} / {' '.join(spec_out)}"
        pyperclip.copy(final_text)

    # 시작 버튼 누르자마자 클립보드 초기화 (AAA BBB CCC DDD / EEE FFF 형식)
    update_clipboard()

    # 키 등록
    for i in range(1, 7):
        keyboard.add_hotkey(f'num {i}', lambda k=str(i): (
            users[k].__setitem__(2, datetime.datetime.now() + datetime.timedelta(minutes=users[k][1])),
            update_clipboard()
        ) if users[k][0].strip() else None)

    keyboard.wait()

def create_ui():
    root = tk.Tk()
    root.title("스킬 타이머 Pro")
    root.geometry("320x480")
    root.configure(bg="#f5f5f5")

    config = load_config() or {"names": ["AAA", "BBB", "CCC", "DDD"], "specials": ["EEE", "FFF"]}

    tk.Label(root, text="인원 이름 설정", font=("Malgun Gothic", 12, "bold"), bg="#f5f5f5", pady=15).pack()

    entries = []
    for i in range(4):
        f = tk.Frame(root, bg="#f5f5f5")
        f.pack(pady=3)
        tk.Label(f, text=f"{i+1}번 (30m):", bg="#f5f5f5", width=10).pack(side=tk.LEFT)
        e = tk.Entry(f, width=15)
        e.insert(0, config["names"][i])
        e.pack(side=tk.LEFT)
        entries.append(e)

    tk.Label(root, text="특별 인원 (13m)", font=("Malgun Gothic", 10, "bold"), bg="#f5f5f5", pady=10).pack()
    
    spec_entries = []
    for i in range(2):
        f = tk.Frame(root, bg="#f5f5f5")
        f.pack(pady=3)
        tk.Label(f, text=f"특{i+1} (NUM{i+5}):", bg="#f5f5f5", width=10).pack(side=tk.LEFT)
        e = tk.Entry(f, width=15)
        e.insert(0, config["specials"][i])
        e.pack(side=tk.LEFT)
        spec_entries.append(e)

    def on_start():
        names = [e.get() for e in entries]
        specials = [e.get() for e in spec_entries]
        save_config(names, specials) # 이름 저장
        root.destroy()
        start_timer(names, specials)

    tk.Button(root, text="저장 및 타이머 시작", command=on_start, width=20, bg="#2196F3", fg="white", font=("Malgun Gothic", 10, "bold"), pady=10).pack(pady=20)
    tk.Label(root, text="특2가 공란이면 기존과 동일하게 작동합니다.", font=("Malgun Gothic", 8), fg="#888", bg="#f5f5f5").pack()

    root.mainloop()

if __name__ == "__main__":
    create_ui()
