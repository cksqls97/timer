import keyboard, pyperclip, datetime, tkinter as tk, json, os, sys, winsound, ctypes
from tkinter import messagebox

# [1] 관리자 권한 체크
def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

CFG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "timer_config.json")

def load_config():
    if os.path.exists(CFG_FILE):
        try:
            with open(CFG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("n"): return data
        except: pass
    return {"n": ["비숍1", "비숍2", "비숍3", "비숍4"]}

def save_config(names):
    try:
        with open(CFG_FILE, "w", encoding="utf-8") as f:
            json.dump({"n": names}, f, ensure_ascii=False, indent=4)
    except: pass

# 전역 상태 변수
ov_root = None
ov_elements = {}
resurrection_alive = {'f1': True, 'f2': True, 'f3': True, 'f4': True}
ready_notified = {'f1': True, 'f2': True, 'f3': True, 'f4': True}
guest_notified = True # 손님 1분 알림 상태 추적용 추가
last_clip_minute = -1 
usage_logs = {'f1': [], 'f2': [], 'f3': [], 'f4': [], 'f5': []}

def show_manual():
    manual_text = "[ Resurrection_Timer ]\n- 좌클릭: 타이머 시작\n- 우클릭: 생존상태 토글(D.O)\n- 매 분 00초 클립보드 자동복사\n- 비숍 READY 및 손님 1분 전 사운드 알림"
    messagebox.showinfo("Manual", manual_text)

def create_exit_log(names):
    try:
        now = datetime.datetime.now()
        filename = now.strftime("%Y-%m-%d_%H시%M분%S초_미션리포트.txt")
        with open(filename, "w", encoding="utf-8") as f: f.write(f"Mission End: {now}")
    except: pass

def start_logic(names):
    global guest_notified
    u = {'f1': names[0], 'f2': names[1], 'f3': names[2], 'f4': names[3], 'f5': "손님"}
    nt_times = {k: None for k in u.keys()}

    def safe_exit():
        create_exit_log(names)
        os._exit(0)

    def update_clipboard():
        now = datetime.datetime.now()
        o_p = []
        for rk in ['f1','f2','f3','f4']:
            if nt_times[rk] and nt_times[rk] > now: o_p.append(f"{u[rk]} {nt_times[rk].strftime('%M')}")
            else: o_p.append(u[rk])
        g_str = f"손님 {nt_times['f5'].strftime('%M')}" if nt_times['f5'] and nt_times['f5'] > now else "손님"
        pyperclip.copy(f"현재 {now.strftime('%H%M')} | {' '.join(o_p)} | {g_str}")

    def update_display():
        global guest_notified
        now = datetime.datetime.now()
        for rk in ['f1','f2','f3','f4','f5']:
            c, nl, tl, rl, msg = ov_elements[rk]
            nl.config(text=u[rk])
            
            if rk != 'f5' and not resurrection_alive[rk]:
                c.config(bg="#150A0A")
                tl.config(text="D.O", fg="#552222")
                rl.config(text="")
            else:
                c.config(bg="#1E1E1E")
                if nt_times[rk] and nt_times[rk] > now:
                    diff = nt_times[rk] - now
                    total_sec = int(diff.total_seconds())
                    m, s = divmod(total_sec, 60)
                    
                    # [손님 1분 전 알림 로직]
                    if rk == 'f5' and not guest_notified and 59 <= total_sec <= 60:
                        winsound.Beep(800, 600) # 조금 더 낮은 음으로 길게 알림
                        guest_notified = True
                    
                    tl.config(text=nt_times[rk].strftime('%H시 %M분'), fg="#FFD1D1", font=("Malgun Gothic", 12, "bold"))
                    rl.config(text=f"남은 시간: {m}분 {s}초", fg="#FF5252", font=("Malgun Gothic", 9, "bold"))
                else:
                    # [비숍 READY 알림 로직]
                    if rk in ready_notified and not ready_notified[rk]:
                        winsound.Beep(1000, 400)
                        ready_notified[rk] = True
                    
                    ready_color = "#03DAC6" if rk == 'f5' else "#4CAF50"
                    tl.config(text="READY", fg=ready_color, font=("Segoe UI", 15, "bold"))
                    rl.config(text="")
        ov_elements['now'].config(text=now.strftime('%H:%M:%S'))

    def on_click_event(k):
        global guest_notified
        now = datetime.datetime.now()
        if k in ['f1','f2','f3','f4']: 
            nt_times[k] = now + datetime.timedelta(minutes=30)
            ready_notified[k] = False
        elif k == 'f5': 
            nt_times['f5'] = now + datetime.timedelta(minutes=13)
            guest_notified = False # 손님 타이머 시작 시 알림 대기 상태로 변경
        update_display(); update_clipboard()

    def toggle_status(k):
        resurrection_alive[k] = not resurrection_alive[k]
        update_display()

    def create_overlay():
        global ov_root, ov_elements
        ov_root = tk.Tk()
        ov_root.attributes("-topmost", True, "-alpha", 0.95); ov_root.overrideredirect(True)
        ov_root.configure(bg="#0F0F0F")
        w, h = 320, 520
        ov_root.geometry(f"{w}x{h}+{ov_root.winfo_screenwidth()-w-30}+{ov_root.winfo_screenheight()-h-120}")
        
        header = tk.Frame(ov_root, bg="#1A1A1A", height=35); header.pack(fill="x")
        def sm(e): ov_root.x, ov_root.y = e.x, e.y
        def dm(e): ov_root.geometry(f"+{ov_root.winfo_x()+(e.x-ov_root.x)}+{ov_root.winfo_y()+(e.y-ov_root.y)}")
        header.bind("<Button-1>", sm); header.bind("<B1-Motion>", dm)
        
        ov_elements['now'] = tk.Label(header, text="00:00:00", fg="#00FF7F", bg="#1A1A1A", font=("Segoe UI", 10, "bold"))
        ov_elements['now'].pack(side=tk.LEFT, padx=15)
        tk.Button(header, text="✕", bg="#1A1A1A", fg="#888", bd=0, command=safe_exit).pack(side=tk.RIGHT, padx=10)

        main = tk.Frame(ov_root, bg="#0F0F0F", padx=10, pady=10); main.pack(fill="both", expand=True)

        def make_card(parent, k, is_guest=False):
            c = tk.Frame(parent, bg="#1E1E1E", highlightthickness=1, highlightbackground="#333")
            nl = tk.Label(c, text=u[k], fg="#AAAAAA", bg="#1E1E1E", font=("Malgun Gothic", 9))
            tl = tk.Label(c, text="READY", fg="#BB86FC" if not is_guest else "#03DAC6", bg="#1E1E1E", font=("Segoe UI", 15, "bold"))
            rl = tk.Label(c, text="", fg="#FF5252", bg="#1E1E1E", font=("Malgun Gothic", 9, "bold"))
            msg = tk.Label(c, text="", fg="#FF5252", bg="#1E1E1E", font=("Malgun Gothic", 8, "bold"), height=2)
            nl.pack(pady=(5,0)); tl.pack(pady=2); rl.pack(pady=2); msg.pack(pady=(0,5))
            for w_ in [c, nl, tl, rl, msg]:
                w_.bind("<Button-1>", lambda e, x=k: on_click_event(x))
                if not is_guest: w_.bind("<Button-3>", lambda e, x=k: toggle_status(x))
            return c, nl, tl, rl, msg

        for i, k in enumerate(['f1','f2','f3','f4']):
            c, nl, tl, rl, m = make_card(main, k)
            c.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="nsew")
            ov_elements[k] = (c, nl, tl, rl, m)

        c, nl, tl, rl, m = make_card(main, 'f5', is_guest=True)
        c.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        ov_elements['f5'] = (c, nl, tl, rl, m)
        main.grid_columnconfigure(0, weight=1); main.grid_columnconfigure(1, weight=1)

        def auto_tick():
            global last_clip_minute
            if ov_root.winfo_exists():
                now = datetime.datetime.now()
                update_display()
                if now.second == 0 and now.minute != last_clip_minute:
                    update_clipboard(); last_clip_minute = now.minute
                ov_root.after(1000, auto_tick)
        auto_tick(); ov_root.mainloop()

    create_overlay()

def show_setup_ui():
    root = tk.Tk()
    root.title("Timer Setup")
    root.geometry("400x600")
    root.configure(bg="#121212")
    
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"+{(sw-400)//2}+{(sh-600)//2}")

    config = load_config()

    header = tk.Frame(root, bg="#121212", pady=20)
    header.pack(fill="x")
    tk.Label(header, text="Timer Configuration", font=("Segoe UI", 18, "bold"), bg="#121212", fg="#BB86FC").pack()
    tk.Button(header, text="[ 도움말 보기 ]", font=("Malgun Gothic", 9), bg="#121212", fg="#03DAC6", bd=0, command=show_manual, cursor="hand2").pack(pady=5)

    input_frame = tk.Frame(root, bg="#121212")
    input_frame.pack(padx=40, fill="x")

    ents = []
    for i in range(4):
        lbl = tk.Label(input_frame, text=f"BISHOP {i+1}", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#888")
        lbl.pack(anchor="w", pady=(10, 0))
        e = tk.Entry(input_frame, font=("Malgun Gothic", 12), bg="#1E1E1E", fg="white", 
                     insertbackground="white", bd=0, highlightthickness=1, highlightbackground="#333",
                     highlightcolor="#BB86FC")
        e.insert(0, config["n"][i])
        e.pack(fill="x", ipady=8)
        ents.append(e)

    def start():
        nv = [e.get().strip() or f"비숍{i+1}" for i, e in enumerate(ents)]
        save_config(nv); root.destroy(); start_logic(nv)

    btn_start = tk.Button(root, text="START MISSION", command=start, bg="#BB86FC", fg="#000", 
                          font=("Segoe UI", 14, "bold"), activebackground="#A370F7", bd=0, cursor="hand2")
    btn_start.pack(side="bottom", fill="x", padx=40, pady=40, ipady=20)

    root.mainloop()

if __name__ == "__main__":
    show_setup_ui()
