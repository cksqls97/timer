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
guest_beep_flag = False
last_clip_update = -1 
usage_logs = {'f1': [], 'f2': [], 'f3': [], 'f4': [], 'f5': []}
status_logs = {'f1': [], 'f2': [], 'f3': [], 'f4': []}

def show_manual():
    manual_text = "[ Resurrection_Timer ]\n- 좌클릭: 타이머\n- 우클릭: 생존상태 토글\n- 매 분 00초 클립보드 자동복사"
    messagebox.showinfo("Manual", manual_text)

def create_exit_log(names):
    try:
        now = datetime.datetime.now()
        filename = now.strftime("%Y-%m-%d_%H시%M분%S초_미션리포트.txt")
        u_dict = {'f1': names[0], 'f2': names[1], 'f3': names[2], 'f4': names[3], 'f5': "손님"}
        log_content = [f"=== Mission Report ===\nEnd: {now}\n"]
        for k in ['f1', 'f2', 'f3', 'f4', 'f5']:
            log_content.append(f"[{u_dict[k]}] - Events: {len(usage_logs[k])}")
        with open(filename, "w", encoding="utf-8") as f: f.write("\n".join(log_content))
    except: pass

def start_logic(names):
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
        now = datetime.datetime.now()
        current_alives = []
        for rk in ['f1','f2','f3','f4']:
            if resurrection_alive[rk]:
                t = nt_times[rk]
                current_alives.append(t if (t and t > now) else now)
        current_alives.sort()
        guest_deadline = nt_times['f5'] if nt_times['f5'] else now

        for rk in ['f1','f2','f3','f4']:
            c, nl, tl, rl, msg = ov_elements[rk]
            if not resurrection_alive[rk]:
                c.config(highlightbackground="#441111", bg="#150A0A")
                for w in [nl, tl, rl, msg]: w.config(bg="#150A0A")
                tl.config(text="D.O", fg="#552222"); rl.config(text=""); msg.config(text=""); continue
            
            c.config(bg="#1E1E1E"); nl.config(bg="#1E1E1E", text=u[rk]); tl.config(bg="#1E1E1E"); rl.config(bg="#1E1E1E"); msg.config(bg="#1E1E1E")
            
            if nt_times[rk] and nt_times[rk] > now:
                diff = nt_times[rk] - now
                m, s = divmod(int(diff.total_seconds()), 60)
                tl.config(text=nt_times[rk].strftime('%H:%M'), fg="#FFD1D1", font=("Segoe UI", 12, "bold"))
                rl.config(text=f"{m:02d}:{s:02d} 남음", fg="#FF5252")
                msg.config(text=""); c.config(highlightbackground="#333", highlightthickness=1)
            else:
                tl.config(text="READY", fg="#4CAF50", font=("Segoe UI", 14, "bold"))
                rl.config(text=""); msg.config(text=""); c.config(highlightbackground="#333", highlightthickness=1)

        c, nl, tl, rl, msg = ov_elements['f5']
        if nt_times['f5'] and now < nt_times['f5']:
            diff = nt_times['f5'] - now
            m, s = divmod(int(diff.total_seconds()), 60)
            tl.config(text=nt_times['f5'].strftime('%H:%M'), fg="#FFD1D1")
            rl.config(text=f"{m:02d}:{s:02d} 남음", fg="#FF5252")
            min_r = current_alives[0] if current_alives else now + datetime.timedelta(minutes=99)
            m_sec = (nt_times['f5'] - min_r).total_seconds()
            msg.config(text="⚠️ 리저 부족" if m_sec < 0 else f"{int(m_sec//60)}m 여유", fg="#FF1744" if m_sec < 0 else "#FFAB00")
        else:
            tl.config(text="READY", fg="#03DAC6"); rl.config(text=""); msg.config(text="")
            
        ov_elements['now'].config(text=now.strftime('%H:%M:%S'))

    def on_click_event(k):
        now = datetime.datetime.now()
        if k in ['f1','f2','f3','f4']:
            if not nt_times[k] or now >= nt_times[k]: nt_times[k] = now + datetime.timedelta(minutes=30)
        elif k == 'f5':
            nt_times['f5'] = now + datetime.timedelta(minutes=13)
        update_display(); update_clipboard()

    def toggle_status(k):
        resurrection_alive[k] = not resurrection_alive[k]
        update_display()

    def create_overlay():
        global ov_root, ov_elements
        ov_root = tk.Tk()
        ov_root.attributes("-topmost", True, "-alpha", 0.95); ov_root.overrideredirect(True)
        ov_root.configure(bg="#0F0F0F")
        
        # 전체 창 사이즈 최적화
        w, h = 300, 420 
        ov_root.geometry(f"{w}x{h}+{ov_root.winfo_screenwidth()-w-30}+{ov_root.winfo_screenheight()-h-120}")
        
        header = tk.Frame(ov_root, bg="#1A1A1A", height=30); header.pack(fill="x")
        def sm(e): ov_root.x, ov_root.y = e.x, e.y
        def dm(e): ov_root.geometry(f"+{ov_root.winfo_x()+(e.x-ov_root.x)}+{ov_root.winfo_y()+(e.y-ov_root.y)}")
        header.bind("<Button-1>", sm); header.bind("<B1-Motion>", dm)
        
        ov_elements['now'] = tk.Label(header, text="00:00:00", fg="#00FF7F", bg="#1A1A1A", font=("Segoe UI", 10, "bold"))
        ov_elements['now'].pack(side=tk.LEFT, padx=10)
        tk.Button(header, text="✕", bg="#1A1A1A", fg="#888", bd=0, command=safe_exit).pack(side=tk.RIGHT, padx=5)

        # 메인 컨테이너
        main = tk.Frame(ov_root, bg="#0F0F0F", padx=5, pady=5); main.pack(fill="both", expand=True)

        def make_card(parent, k, is_guest=False):
            # 외부 프레임: 일정한 간격을 유지하도록 고정 패딩 부여
            out_f = tk.Frame(parent, bg="#0F0F0F")
            c = tk.Frame(out_f, bg="#1E1E1E", highlightthickness=1, highlightbackground="#333")
            c.pack(fill="both", expand=True, padx=2, pady=2)
            
            nl = tk.Label(c, text=u[k], fg="#AAAAAA", bg="#1E1E1E", font=("Malgun Gothic", 9))
            tl = tk.Label(c, text="READY", fg="#BB86FC" if not is_guest else "#03DAC6", bg="#1E1E1E", font=("Segoe UI", 13, "bold"))
            rl = tk.Label(c, text="", fg="#FF5252", bg="#1E1E1E", font=("Malgun Gothic", 9))
            msg = tk.Label(c, text="", fg="#FF5252", bg="#1E1E1E", font=("Malgun Gothic", 8, "bold"))
            
            nl.pack(pady=(2,0)); tl.pack(); rl.pack(); msg.pack(pady=(0,2))
            
            for w_ in [c, nl, tl, rl, msg]:
                w_.bind("<Button-1>", lambda e, x=k: on_click_event(x))
                if not is_guest: w_.bind("<Button-3>", lambda e, x=k: toggle_status(x))
            return out_f, nl, tl, rl, msg

        # 비숍들 배치 (2x2)
        for i, k in enumerate(['f1','f2','f3','f4']):
            card_frame, nl, tl, rl, m = make_card(main, k)
            card_frame.place(x=(i%2)*145, y=(i//2)*110, width=145, height=105)
            ov_elements[k] = (card_frame.winfo_children()[0], nl, tl, rl, m)

        # 손님 배치 (하단)
        c5_f, nl5, tl5, rl5, m5 = make_card(main, 'f5', is_guest=True)
        c5_f.place(x=0, y=220, width=290, height=100)
        ov_elements['f5'] = (c5_f.winfo_children()[0], nl5, tl5, rl5, m5)

        def auto_tick():
            global last_clip_update
            if ov_root.winfo_exists():
                now = datetime.datetime.now()
                update_display()
                if now.second == 0 and now.minute != last_clip_update:
                    update_clipboard()
                    last_clip_update = now.minute
                ov_root.after(1000, auto_tick)
        
        auto_tick(); ov_root.mainloop()

    create_overlay()

def show_setup_ui():
    root = tk.Tk(); root.title("Setup"); root.geometry("350x450"); root.configure(bg="#121212")
    config = load_config()
    tk.Label(root, text="Resurrection Timer", font=("Segoe UI", 16, "bold"), bg="#121212", fg="#BB86FC", pady=20).pack()
    ents = []
    for i in range(4):
        e = tk.Entry(root, font=("Segoe UI", 12), bg="#1E1E1E", fg="white", bd=0, highlightthickness=1)
        e.insert(0, config["n"][i]); e.pack(pady=5, padx=50, fill="x", ipady=5); ents.append(e)
    def start():
        nv = [e.get() for e in ents]; save_config(nv); root.destroy(); start_logic(nv)
    tk.Button(root, text="START MISSION", command=start, bg="#BB86FC", fg="#000", font=("Segoe UI", 12, "bold"), pady=10).pack(pady=30, padx=50, fill="x")
    root.mainloop()

if __name__ == "__main__":
    show_setup_ui()
