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
last_clip_minute = -1  # 마지막으로 자동 복사한 '분'을 기록
usage_logs = {'f1': [], 'f2': [], 'f3': [], 'f4': [], 'f5': []}
status_logs = {'f1': [], 'f2': [], 'f3': [], 'f4': []}

def show_manual():
    manual_text = (
        "[ Resurrection_Timer 사용 설명서 ]\n\n"
        "1. 조작 안내\n"
        " - 상단 바 드래그: 오버레이 위치 이동\n"
        " - 마우스 좌클릭: 타이머 시작 (30분/13분)\n"
        " - 마우스 우클릭: 비숍 사망/생존(D.O) 토글\n\n"
        "2. 주요 기능\n"
        " - 매 분 00초: 클립보드 자동 갱신\n"
        " - 노란색: 사용 시 손님 연속 사망 대응 불가\n"
        " - 빨간색: 사망 시 로테이션 붕괴 위험\n\n"
        "3. 로그 저장\n"
        " - 종료 시 상세 타임라인 리포트 생성"
    )
    messagebox.showinfo("Resurrection_Timer Manual", manual_text)

def create_exit_log(names):
    try:
        now = datetime.datetime.now()
        filename = now.strftime("%Y-%m-%d_%H시%M분%S초_미션리포트.txt")
        u_dict = {'f1': names[0], 'f2': names[1], 'f3': names[2], 'f4': names[3], 'f5': "손님"}
        log_content = [f"=== Mission Report ===\nEnd: {now}\n"]
        for k in ['f1', 'f2', 'f3', 'f4', 'f5']:
            log_content.append(f"[{u_dict[k]}] Events: {len(usage_logs[k])}")
        with open(filename, "w", encoding="utf-8") as f: f.write("\n".join(log_content))
    except: pass

def start_logic(names):
    u = {'f1': names[0], 'f2': names[1], 'f3': names[2], 'f4': names[3], 'f5': "손님"}
    nt_times = {k: None for k in u.keys()}

    def safe_exit():
        create_exit_log(names)
        os._exit(0)

    def go_to_setup():
        if ov_root: ov_root.destroy()
        show_setup_ui()

    def update_clipboard():
        now = datetime.datetime.now()
        cur_time = now.strftime('%H%M')
        o_p = []
        for rk in ['f1','f2','f3','f4']:
            if nt_times[rk] and nt_times[rk] > now:
                o_p.append(f"{u[rk]} {nt_times[rk].strftime('%M')}")
            else: o_p.append(u[rk])
        g_str = f"손님 {nt_times['f5'].strftime('%M')}" if nt_times['f5'] and nt_times['f5'] > now else "손님"
        pyperclip.copy(f"현재 {cur_time} | {' '.join(o_p)} | {g_str}")

    def update_display():
        now = datetime.datetime.now()
        current_alives = []
        for rk in ['f1','f2','f3','f4']:
            if resurrection_alive[rk]:
                t = nt_times[rk]
                current_alives.append(t if (t and t > now) else now)
        current_alives.sort()
        guest_deadline = nt_times['f5'] if nt_times['f5'] else now

        for rk in ['f1', 'f2', 'f3', 'f4']:
            c, nl, tl, rl, msg = ov_elements[rk]
            nl.config(text=u[rk], fg="white")
            if not resurrection_alive[rk]:
                c.config(highlightbackground="#441111", bg="#150A0A")
                for w in [nl, tl, rl, msg]: w.config(bg="#150A0A")
                tl.config(text="D.O", fg="#552222"); rl.config(text=""); msg.config(text=""); continue
            c.config(bg="#1E1E1E"); nl.config(bg="#1E1E1E"); tl.config(bg="#1E1E1E"); rl.config(bg="#1E1E1E"); msg.config(bg="#1E1E1E")
            if nt_times[rk] and nt_times[rk] > now:
                diff = nt_times[rk] - now
                m, s = divmod(int(diff.total_seconds()), 60)
                tl.config(text=nt_times[rk].strftime('%H시 %M분'), fg="#FFD1D1", font=("Malgun Gothic", 12, "bold"))
                rl.config(text=f"남은 시간: {m}분 {s}초", fg="#FF5252", font=("Malgun Gothic", 9, "bold"))
                msg.config(text=""); c.config(highlightbackground="#333", highlightthickness=1)
            else:
                tl.config(text="READY", fg="#4CAF50", font=("Segoe UI", 15, "bold"))
                rl.config(text=""); msg.config(text=""); c.config(highlightbackground="#333", highlightthickness=1)

        c, nl, tl, rl, msg = ov_elements['f5']
        if nt_times['f5'] and now < nt_times['f5']:
            diff = nt_times['f5'] - now
            m, s = divmod(int(diff.total_seconds()), 60)
            tl.config(text=nt_times['f5'].strftime('%H시 %M분'), fg="#FFD1D1", font=("Malgun Gothic", 12, "bold"))
            rl.config(text=f"남은 시간: {m}분 {s}초", fg="#FF5252", font=("Malgun Gothic", 9, "bold"))
        else:
            tl.config(text="READY", fg="#03DAC6", font=("Segoe UI", 15, "bold")); rl.config(text=""); msg.config(text="")
        ov_elements['now'].config(text=now.strftime('%H:%M:%S'))

    def on_click_event(k):
        now = datetime.datetime.now()
        if k in ['f1','f2','f3','f4']:
            if not nt_times[k] or now >= nt_times[k]:
                nt_times[k] = now + datetime.timedelta(minutes=30)
                usage_logs[k].append(now)
        elif k == 'f5':
            nt_times['f5'] = now + datetime.timedelta(minutes=13)
            usage_logs['f5'].append(now)
        update_display()
        update_clipboard()

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
        tk.Button(header, text="⚙", bg="#1A1A1A", fg="#888", bd=0, command=go_to_setup).pack(side=tk.RIGHT)

        main = tk.Frame(ov_root, bg="#0F0F0F", padx=10, pady=10); main.pack(fill="both", expand=True)

        def make_card(parent, k, is_guest=False):
            c = tk.Frame(parent, bg="#1E1E1E", bd=0, highlightthickness=1, highlightbackground="#333")
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
                
                # 매 분 00초가 되었을 때 한 번만 실행
                if now.second == 0 and now.minute != last_clip_minute:
                    update_clipboard()
                    last_clip_minute = now.minute
                    
                ov_root.after(1000, auto_tick)
        
        auto_tick(); ov_root.mainloop()

    create_overlay()

def show_setup_ui():
    root = tk.Tk(); root.title("Setup"); root.geometry("420x580"); root.configure(bg="#121212")
    config = load_config()
    tk.Label(root, text="Resurrection_Timer", font=("Segoe UI", 20, "bold"), bg="#121212", fg="#BB86FC").pack(pady=20)
    ents = []
    for i in range(4):
        e = tk.Entry(root, font=("Segoe UI", 12), bg="#1E1E1E", fg="white", bd=0, highlightthickness=1)
        e.insert(0, config["n"][i]); e.pack(pady=10, padx=50, fill="x", ipady=8); ents.append(e)
    def start():
        nv = [e.get() for e in ents]; save_config(nv); root.destroy(); start_logic(nv)
    tk.Button(root, text="START MISSION", command=start, bg="#BB86FC", fg="#000", font=("Segoe UI", 13, "bold"), pady=15).pack(pady=30, padx=50, fill="x")
    root.mainloop()

if __name__ == "__main__":
    show_setup_ui()
