import pyperclip, datetime, tkinter as tk, json, os, sys, winsound, ctypes
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
usage_logs = {'f1': [], 'f2': [], 'f3': [], 'f4': [], 'f5': []}
status_logs = {'f1': [], 'f2': [], 'f3': [], 'f4': []}

def show_manual():
    manual_text = (
        "[ Resurrection_Timer 사용 설명서 ]\n\n"
        "1. 조작 안내\n"
        " - 상단 바 드래그: 오버레이 위치 이동\n"
        " - 마우스 좌클릭: 타이머 시작 (30분/13분)\n"
        " - 마우스 우클릭: 비숍 사망/생존(사망) 토글\n\n"
        "2. 주요 기능\n"
        " - 타이머 기반 실시간 로테이션 관리\n"
        " - 1분 간격 클립보드 자동 업데이트\n\n"
        "3. 로그 저장\n"
        " - 종료 시 상세 타임라인 리포트 생성"
    )
    messagebox.showinfo("Manual", manual_text)

def create_exit_log(names):
    try:
        now = datetime.datetime.now()
        filename = now.strftime("%Y-%m-%d_%H시%M분%S초_미션리포트.txt")
        u_dict = {'f1': names[0], 'f2': names[1], 'f3': names[2], 'f4': names[3], 'f5': "손님"}
        log_content = [f"=== Resurrection Timer 미션 상세 리포트 ===", f"종료 시각: {now.strftime('%Y-%m-%d %H:%M:%S')}", "-"*40]
        for k in ['f1', 'f2', 'f3', 'f4', 'f5']:
            log_content.append(f"[{u_dict[k]}]")
            events = [(t, "리저 사용" if k!='f5' else "사망 기록") for t in usage_logs[k]]
            if k != 'f5': events += status_logs[k]
            events.sort(key=lambda x: x[0])
            for idx, (t, act) in enumerate(events, 1): log_content.append(f"  {idx}. [{t.strftime('%H:%M:%S')}] {act}")
            if not events: log_content.append("  - 기록 없음")
            log_content.append("")
        with open(filename, "w", encoding="utf-8") as f: f.write("\n".join(log_content))
    except: pass

def start_logic(names):
    u = {'f1': names[0], 'f2': names[1], 'f3': names[2], 'f4': names[3], 'f5': "손님"}
    nt_times = {k: None for k in u.keys()}

    def safe_exit():
        create_exit_log(names); os._exit(0)

    def go_to_setup():
        if ov_root: ov_root.destroy()
        show_setup_ui()

    def update_clipboard():
        now = datetime.datetime.now()
        o_p = [f"{u[rk]} {nt_times[rk].strftime('%M')}" if nt_times[rk] and nt_times[rk] > now else u[rk] for rk in ['f1','f2','f3','f4']]
        g_str = f"손님 {nt_times['f5'].strftime('%M')}" if nt_times['f5'] and nt_times['f5'] > now else "손님"
        pyperclip.copy(f"현재 {now.strftime('%H%M')} | {' '.join(o_p)} | {g_str}")

    def auto_clipboard_tick():
        if ov_root.winfo_exists(): update_clipboard(); ov_root.after(60000, auto_clipboard_tick)

    def update_display():
        now = datetime.datetime.now()
        current_alives = sorted([nt_times[rk] if (nt_times[rk] and nt_times[rk] > now) else now for rk in ['f1','f2','f3','f4'] if resurrection_alive[rk]])
        
        for rk in ['f1','f2','f3','f4']:
            c, nl, tl, rl, msg = ov_elements[rk]
            if not resurrection_alive[rk]:
                c.config(highlightbackground="#441111", bg="#150A0A")
                for w in [nl, tl, rl, msg]: w.config(bg="#150A0A")
                tl.config(text="사망", fg="#772222"); rl.config(text=""); msg.config(text=""); continue
            
            c.config(bg="#1E1E1E", highlightbackground="#333")
            for w in [nl, tl, rl, msg]: w.config(bg="#1E1E1E")
            
            if nt_times[rk] and nt_times[rk] > now:
                diff = nt_times[rk] - now
                m, s = divmod(int(diff.total_seconds()), 60)
                tl.config(text=f"{m:02d}:{s:02d}", fg="#FF5252", font=("Segoe UI", 14, "bold"))
                rl.config(text=nt_times[rk].strftime('%H:%M'), fg="#888")
            else:
                tl.config(text="READY", fg="#4CAF50", font=("Segoe UI", 14, "bold")); rl.config(text="")

        c, nl, tl, rl, msg = ov_elements['f5']
        if nt_times['f5'] and now < nt_times['f5']:
            m, s = divmod(int((nt_times['f5']-now).total_seconds()), 60)
            tl.config(text=f"{m:02d}:{s:02d}", fg="#03DAC6"); rl.config(text=nt_times['f5'].strftime('%H:%M'))
            min_r = current_alives[0] if current_alives else now + datetime.timedelta(minutes=99)
            m_sec = (nt_times['f5'] - min_r).total_seconds()
            msg.config(text="⚠️ 부족" if m_sec < 0 else f"{int(m_sec//60)}m 여유", fg="#FF1744" if m_sec < 0 else "#FFAB00")
            global guest_beep_flag
            if 58 <= (nt_times['f5']-now).total_seconds() <= 61 and not guest_beep_flag: winsound.Beep(1000, 500); guest_beep_flag = True
        else:
            tl.config(text="READY", fg="#03DAC6"); rl.config(text=""); msg.config(text=""); guest_beep_flag = False
        ov_elements['now'].config(text=now.strftime('%H:%M:%S'))

    def on_click_event(k):
        now = datetime.datetime.now()
        if k in ['f1','f2','f3','f4'] and (not nt_times[k] or now >= nt_times[k]):
            nt_times[k] = now + datetime.timedelta(minutes=30); usage_logs[k].append(now)
        elif k == 'f5':
            nt_times['f5'] = now + datetime.timedelta(minutes=13); usage_logs['f5'].append(now); global guest_beep_flag; guest_beep_flag = False
        update_clipboard()

    def toggle_status(k):
        resurrection_alive[k] = not resurrection_alive[k]
        status_logs[k].append((datetime.datetime.now(), "생존 합류" if resurrection_alive[k] else "사망 발생"))

    def create_overlay():
        global ov_root, ov_elements
        ov_root = tk.Tk()
        ov_root.attributes("-topmost", True, "-alpha", 0.95); ov_root.overrideredirect(True); ov_root.configure(bg="#0F0F0F")
        w, h = 240, 420  # 오버레이 크기 최적화 (가로폭 축소)
        ov_root.geometry(f"{w}x{h}+{ov_root.winfo_screenwidth()-w-20}+{ov_root.winfo_screenheight()-h-80}")
        
        def sm(e): ov_root.x, ov_root.y = e.x, e.y
        def dm(e): ov_root.geometry(f"+{ov_root.winfo_x()+(e.x-ov_root.x)}+{ov_root.winfo_y()+(e.y-ov_root.y)}")

        header = tk.Frame(ov_root, bg="#1A1A1A", height=30); header.pack(fill="x")
        header.bind("<Button-1>", sm); header.bind("<B1-Motion>", dm)
        ov_elements['now'] = tk.Label(header, text="00:00:00", fg="#00FF7F", bg="#1A1A1A", font=("Consolas", 9, "bold"))
        ov_elements['now'].pack(side=tk.LEFT, padx=10)
        for txt, cmd in [("✕", safe_exit), ("?", show_manual), ("⚙", go_to_setup)]:
            tk.Button(header, text=txt, bg="#1A1A1A", fg="#666", bd=0, command=cmd, activebackground="#333", font=("Arial", 9)).pack(side=tk.RIGHT, padx=5)

        main = tk.Frame(ov_root, bg="#0F0F0F", padx=6, pady=6); main.pack(fill="both", expand=True)

        def make_card(parent, k, is_guest=False):
            c = tk.Frame(parent, bg="#1E1E1E", highlightthickness=1, highlightbackground="#333")
            nl = tk.Label(c, text=u[k], fg="#888", bg="#1E1E1E", font=("Malgun Gothic", 8))
            tl = tk.Label(c, text="READY", fg="#BB86FC" if not is_guest else "#03DAC6", bg="#1E1E1E", font=("Segoe UI", 14, "bold"))
            rl = tk.Label(c, text="", fg="#555", bg="#1E1E1E", font=("Segoe UI", 8))
            msg = tk.Label(c, text="", fg="#FF5252", bg="#1E1E1E", font=("Malgun Gothic", 8, "bold"))
            nl.pack(pady=(4,0)); tl.pack(); rl.pack(); msg.pack(pady=(0,4))
            for w_ in [c, nl, tl, rl, msg]:
                w_.bind("<Button-1>", lambda e, x=k: on_click_event(x))
                if not is_guest: w_.bind("<Button-3>", lambda e, x=k: toggle_status(x))
            return c, nl, tl, rl, msg

        for i, k in enumerate(['f1','f2','f3','f4']):
            c, nl, tl, rl, m = make_card(main, k)
            c.grid(row=i//2, column=i%2, padx=3, pady=3, sticky="nsew")
            ov_elements[k] = (c, nl, tl, rl, m)
        c, nl, tl, rl, m = make_card(main, 'f5', is_guest=True)
        c.grid(row=2, column=0, columnspan=2, padx=3, pady=3, sticky="nsew")
        ov_elements['f5'] = (c, nl, tl, rl, m)
        main.grid_columnconfigure((0,1), weight=1); main.grid_rowconfigure((0,1,2), weight=1)

        def auto_tick():
            if ov_root.winfo_exists(): update_display(); ov_root.after(1000, auto_tick)
        auto_tick(); auto_clipboard_tick(); ov_root.mainloop()

    create_overlay()

# [4] 설정 UI (디자인 및 여백 전면 개편)
def show_setup_ui():
    root = tk.Tk(); root.title("Setup"); root.geometry("360x480"); root.configure(bg="#121212")
    root.eval('tk::PlaceWindow . center'); config = load_config()

    header = tk.Frame(root, bg="#1A1A1A", pady=20); header.pack(fill="x")
    tk.Label(header, text="RE-TIMER", font=("Segoe UI", 16, "bold"), bg="#1A1A1A", fg="#BB86FC").pack()
    tk.Label(header, text="비숍 명단을 입력하세요", font=("Malgun Gothic", 9), bg="#1A1A1A", fg="#666").pack()

    body = tk.Frame(root, bg="#121212", pady=20); body.pack(padx=40, fill="x")
    ents = []
    for i in range(4):
        f = tk.Frame(body, bg="#121212"); f.pack(fill="x", pady=8)
        tk.Label(f, text=f"#{i+1}", font=("Consolas", 10), bg="#121212", fg="#444", width=3).pack(side=tk.LEFT)
        e = tk.Entry(f, font=("Malgun Gothic", 11), bg="#1E1E1E", fg="white", bd=0, highlightthickness=1, highlightbackground="#333", insertbackground="white")
        e.insert(0, config["n"][i]); e.pack(side=tk.LEFT, expand=True, fill="x", ipady=6, padx=(5,0)); ents.append(e)

    def start():
        nv = [e.get().strip() or f"비숍{i+1}" for i, e in enumerate(ents)]
        save_config(nv); root.destroy(); start_logic(nv)

    btn = tk.Button(root, text="START MISSION", command=start, bg="#BB86FC", fg="#000", font=("Segoe UI", 11, "bold"), bd=0, cursor="hand2", activebackground="#D1A3FF")
    btn.pack(pady=30, padx=40, fill="x", ipady=10)
    
    tk.Label(root, text="오른쪽 클릭으로 사망 토글이 가능합니다", font=("Malgun Gothic", 8), bg="#121212", fg="#444").pack(side=tk.BOTTOM, pady=10)
    root.mainloop()

if __name__ == "__main__":
    show_setup_ui()
