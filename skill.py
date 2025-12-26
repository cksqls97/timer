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
        # 리저 인원 (1~4)
        out = []
        for i in range(1, 5):
            name, cool, next_t = users[str(i)]
            if name.strip():
                out.append(f"{name} {next_t.strftime('%H:%M')}" if next_t and now < next_t else name)
        
        # 손님 인원 (5~6)
        spec_out = []
        for i in range(5, 7):
            name, cool, next_t = users[str(i)]
            if name.strip():
                spec_out.append(f"{name} {next_t.strftime('%H:%M')}" if next_t and now < next_t else name)
        
        final_text = f"{' '.join(out)} / {' '.join(spec_out)}"
        pyperclip.copy(final_text)

    # 시작하자마자 클립보드 초기화
    update_clipboard()

    # 키 등록 (Num 1~6)
    for i in range(1, 7):
        keyboard.add_hotkey(f'num {i}', lambda k=str(i): (
            users[k].__setitem__(2, datetime.datetime.now() + datetime.timedelta(minutes=users[k][1])),
            update_clipboard()
        ) if users[k][0].strip() else None)

    keyboard.wait()

def create_ui():
    root = tk.Tk()
    root.title("스킬 타이머 Pro (리저/손님)")
    root.geometry("320x480")
    root.configure(bg="#f5f5f5")

    # 기본값은 공란으로 설정
    config = load_config() or {"names": ["", "", "", ""], "specials": ["", ""]}

    tk.Label(root, text="인원 이름 설정", font=("Malgun Gothic", 12, "bold"), bg="#f5f5f5", pady=15).pack()

    entries = []
    for i in range(4):
        f = tk.Frame(root, bg="#f5f5f5")
        f.pack(pady=3)
        tk.Label(f, text=f"리저{i+1} (30m):", bg="#f5f5f5", width=12).pack(side=tk.LEFT)
        e = tk.Entry(f, width=15)
        e.insert(0, config["names"][i])
        e.pack(side=tk.LEFT)
        entries.append(e)

    tk.Label(root, text="특별 인원 (13m)", font=("Malgun Gothic", 10, "bold"), bg="#f5f5f5", pady=10).pack()
    
    spec_entries = []
    for i in range(2):
        f = tk.Frame(root, bg="#f5f5f5")
        f.pack(pady=3)
        tk.Label(f, text=f"손님{i+1} (Num{i+5}):", bg="#f5f5f5", width=12).pack(side=tk.LEFT)
        e = tk.Entry(f, width=15)
        e.insert(0, config["specials"][i])
        e.pack(side=tk.LEFT)
        spec_entries.append(e)

    def on_start():
        names = [e.get() for e in entries]
        specials = [e.get() for e in spec_entries]
        save_config(names, specials)
        root.destroy()
        start_timer(names, specials)

    tk.Button(root, text="저장 및 타이머 시작", command=on_start, width=20, bg="#2196F3", fg="white", font=("Malgun Gothic", 10, "bold"), pady=10).pack(pady=20)
    tk.Label(root, text="손님2가 공란이면 리스트에 나타나지 않습니다.", font=("Malgun Gothic", 8), fg="#888", bg="#f5f5f5").pack()

    root.mainloop()

if __name__ ==
