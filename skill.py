import keyboard
import pyperclip
import datetime
import tkinter as tk
from tkinter import messagebox

def start_timer(names, extra_name):
    # 타이머 로직 시작
    users = {
        '1': [names[0], 30, None],
        '2': [names[1], 30, None],
        '3': [names[2], 30, None],
        '4': [names[3], 30, None],
        '5': [extra_name, 13, None]
    }

    def update_clipboard():
        now = datetime.datetime.now()
        output = []
        for i in range(1, 5):
            name_val, cool, next_t = users[str(i)]
            if next_t and now < next_t:
                output.append(f"{name_val} {next_t.strftime('%H:%M')}")
            else:
                output.append(name_val)
        
        e_name_val, e_cool, e_next_t = users['5']
        extra_part = f"{e_name_val} {e_next_t.strftime('%H:%M')}" if e_next_t and now < e_next_t else e_name_val
        
        final_text = f"{' '.join(output)} / {extra_part}"
        pyperclip.copy(final_text)

    def on_press(key):
        users[key][2] = datetime.datetime.now() + datetime.timedelta(minutes=users[key][1])
        update_clipboard()

    # 키 등록
    for i in range(1, 6):
        keyboard.add_hotkey(f'num {i}', lambda k=str(i): on_press(k))

    # 백그라운드 대기
    keyboard.wait()

def create_ui():
    # GUI 설정
    root = tk.Tk()
    root.title("스킬 타이머 설정")
    root.geometry("300x400")
    root.configure(bg="#f0f0f0")

    # 폰트 및 스타일
    title_font = ("Malgun Gothic", 14, "bold")
    label_font = ("Malgun Gothic", 10)

    tk.Label(root, text="사용자 이름 설정", font=title_font, bg="#f0f0f0", pady=20).pack()

    entries = []
    for i in range(4):
        frame = tk.Frame(root, bg="#f0f0f0")
        frame.pack(pady=5)
        tk.Label(frame, text=f"{i+1}번 (30분):", font=label_font, bg="#f0f0f0", width=10).pack(side=tk.LEFT)
        entry = tk.Entry(frame, width=15)
        entry.insert(0, f"User{i+1}")
        entry.pack(side=tk.LEFT)
        entries.append(entry)

    # 5번 특별 사용자
    frame_e = tk.Frame(root, bg="#f0f0f0")
    frame_e.pack(pady=5)
    tk.Label(frame_e, text="5번 (13분):", font=label_font, bg="#f0f0f0", width=10).pack(side=tk.LEFT)
    entry_e = tk.Entry(frame_e, width=15)
    entry_e.insert(0, "Special")
    entry_e.pack(side=tk.LEFT)

    def on_submit():
        names = [e.get() for e in entries]
        extra_name = entry_e.get()
        root.destroy()  # 설정창 닫기
        start_timer(names, extra_name)

    # 시작 버튼
    btn = tk.Button(root, text="타이머 시작", command=on_submit, width=20, bg="#4CAF50", fg="white", font=("Malgun Gothic", 10, "bold"), pady=10)
    btn.pack(pady=30)

    # 안내 문구
    tk.Label(root, text="시작 후 창이 사라지면\n넘패드 1~5를 사용하세요.", font=("Malgun Gothic", 8), fg="#666", bg="#f0f0f0").pack()

    root.mainloop()

if __name__ == "__main__":
    create_ui()
