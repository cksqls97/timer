import keyboard, pyperclip, datetime, tkinter as tk, json, os, threading, sys

# 파일 경로 문제 해결 (EXE 실행 시 경로 추적)
def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

CFG = "timer_config.json"
ICON_NAME = "icon.png"

def save(n, s):
    with open(CFG, "w", encoding="utf-8") as f:
        json.dump({"n": n, "s": s}, f, ensure_ascii=False)

def load():
    if os.path.exists(CFG) and os.path.getsize(CFG) > 0:
        try:
            with open(CFG, "r", encoding="utf-8") as f: return json.load(f)
        except: return None
    return None

status_label = None

def custom_notify(title, message, color="#333"):
    def run():
        nt = tk.Toplevel()
        nt.overrideredirect(True)
        nt.attributes("-topmost", True)
        w, h = 280, 80
        # 우측 하단 배치
        sx, sy = nt.winfo_screenwidth() - w - 20, nt.winfo_screenheight() - h - 50
        nt.geometry(f"{w}x{h}+{sx}+{sy}")
        nt.configure(bg=color)
        tk.Label(nt, text=title, fg="white", bg=color, font=("Malgun Gothic", 10, "bold")).pack(pady=(10, 0))
        tk.Label(nt, text=message, fg="white", bg=color, font=("Malgun Gothic", 9), wraplength=250).pack(pady=5)
        nt.after(3000, nt.destroy)
        nt.mainloop()
    threading.Thread(target=run, daemon=True).start()

def start(names, specs):
    u = {
        '1':[names[0],30], '2':[names[1],30], '3':[names[2],30], '4':[names[3],30], 
        '7':[specs[0],13], '8':[specs[1] if specs[1].strip() else "", 13]
    }
    nt_times = {k: None for k in u.keys()}

    def create_status_window():
        global status_label
        sw = tk.Tk()
        sw.attributes("-topmost", True)
        sw.overrideredirect(True)
        
        # 위치 설정: 알림창(높이 80+여백50) 바로 위쪽으로 배치
        w, h = 280, 160
        sx = sw.winfo_screenwidth() - w - 20
        sy = sw.winfo_screenheight() - h - 140 # 알림창보다 살짝 위
        sw.geometry(f"{w}x{h}+{sx}+{sy}")
        sw.configure(bg="#1a1a1a")
        
        def start_move(e): sw.x, sw.y = e.x, e.y
        def do_move(e): sw.geometry(f"+{sw.winfo_x()+(e.x-sw.x)}+{sw.winfo_y()+(e.y-sw.y)}")
        sw.bind("<Button-1>", start_move)
        sw.bind("<B1-Motion>", do_move)

        status_label = tk.Label(sw, text="시스템 준비됨", fg="#00FF00", bg="#1a1a1a", 
                                font=("Malgun Gothic", 9, "bold"), justify=tk.LEFT, 
                                padx=15, pady=15, anchor="nw", wraplength=250)
        status_label.pack(fill="both", expand=True)
        sw.mainloop()

    def up():
        now = datetime.datetime.now()
        cur_time_str = now.strftime('%H%M')
        
        o, s_o = [], []
        # 클립보드용 및 오버레이용 텍스트 생성
        for i in '1234':
            nm = u[i][0].strip()
            if nm:
                time_val = f": {nt_times[i].strftime('%H:%M')}" if nt_times[i] and now < nt_times[i] else ""
                o.append(f"{nm}{time_val}")
        
        for i in '78':
            nm = u[i][0].strip()
            if nm:
                time_val = f": {nt_times[i].strftime('%H:%M')}" if nt_times[i] and now < nt_times[i] else ""
                s_o.append(f"{nm}{time_val}")
        
        # 클립보드 저장
        clip_res = f"현재시간: {cur_time_str} / {' '.join(o)} / {' '.join(s_o)}"
        pyperclip.copy(clip_res)
        
        # 오버레이 업데이트 (깔끔하게 줄바꿈)
        if status_label:
            st_display = f"🕒 현재시간: {cur_time_str}\n"
            st_display += "--------------------------\n"
            st_display += f"✨ 리저: {' , '.join(o) if o else '-'}\n\n"
            st_display += f"👤 손님: {' , '.join(s_o) if s_o else '-'}"
            status_label.config(text=st_display)

    def p(k):
        now = datetime.datetime.now()
        nm = u[k][0]
        if k in '1234' and nt_times[k] and now < nt_times[k]:
            custom_notify("쿨타임 경고", f"{nm}: 아직 쿨타임 중입니다!", "#d32f2f")
            return
        
        nt_times[k] = now + datetime.timedelta(minutes=u[k][1])
        up()
        tm = nt_times[k].strftime('%H:%M')
        msg = f"{nm} 사용됨. 다음: {tm}" if k in '1234' else f"{nm} 갱신됨. 부활: {tm}"
        custom_notify("타이머 갱신", msg, "#2e7d32")

    threading.Thread(target=create_status_window, daemon=True).start()
    
    for k in u.keys():
        keyboard.add_hotkey(f'num {k}', lambda x=k: p(x) if u[x][0].strip() else None)
    
    keyboard.add_hotkey('ctrl+alt+num 1', lambda: os._exit(0))
    keyboard.wait()

def ui():
    root = tk.Tk()
    root.title("Skill Timer Setup")
    root.geometry("320x600")
    root.configure(bg="#f8f9fa")
    
    # 아이콘 로드 (exe 실행 폴더 또는 내부 리소스에서 검색)
    icon_path = ICON_NAME if os.path.exists(ICON_NAME) else resource_path(ICON_NAME)
    try:
        img = tk.PhotoImage(file=icon_path)
        lbl_img = tk.Label(root, image=img, bg="#f8f9fa")
        lbl_img.image = img
        lbl_img.pack(pady=15)
    except:
        tk.Label(root, text="🛡️", font=("Arial", 40), bg="#f8f9fa", fg="#007bff").pack(pady=
