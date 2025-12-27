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

def show_manual():
    manual_text = (
        "[ Resurrection_Timer 사용 설명서 ]\n\n"
        "1. 조작 안내\n"
        " - 마우스 좌클릭: 타이머 시작 (30분/13분)\n"
        " - 마우스 우클릭: 비숍 사망/생존(D.O) 토글\n\n"
        "2. 주요 기능\n"
        " - 노란색: 사용 시 손님 연속 사망 대응 불가\n"
        " - 빨간색: 사망 시 로테이션 붕괴 위험\n\n"
        "3. 자동 클립보드\n"
        " - 클릭 시 현재 상태가 즉시 복사됩니다."
    )
    messagebox.showinfo("Resurrection_Timer Manual", manual_text)

# [3] 메인 로직
def start_logic(names):
    u = {'f1': names[0], 'f2': names[1], 'f3': names[2], 'f4': names[3], 'f5': "손님"}
    nt_times = {k: None for k in u.keys()}

    def go_to_setup():
        # 단축키 해제 로직 제거 (클릭 방식이므로)
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
        alive_times = sorted([nt_times[rk] if nt_times[rk] and nt_times[rk] > now else now 
                             for rk in ['f1','f2','f3','f4'] if resurrection_alive[rk]])
        guest_deadline = nt_times['f5'] if nt_times['f5'] else now

        for rk in ['f1','f2','f3','f4']:
            c, nl, tl, msg = ov_elements[rk]
            nl.config(text=u[rk], fg="white")
            if not resurrection_alive[rk]:
                c.config(highlightbackground="#441111", bg="#150A0A")
                for w in [nl, tl, msg]: w.config(bg="#150A0A")
                tl.config(text="D.O", fg="#552222"); msg.config(text=""); continue
            
            c.config(bg="#1E1E1E"); nl.config(bg="#1E1E1E"); tl.config(bg="#1E1E1E"); msg.config(bg="#1E1E1E")
            if nt_times[rk] and nt_times[rk] > now:
                tl.config(text=nt_times[rk].strftime('%H:%M'), fg="#FF5252")
                msg.config(text=""); c.config(highlightbackground="#333", highlightthickness=1)
            else:
                tl.config(text="READY", fg="#4CAF50")
                warn_texts = []
                tmp_u = sorted(alive_times)
                try:
                    idx = tmp_u.index(now); tmp_u[idx] = now + datetime.timedelta(minutes=30)
                    tmp_u = sorted(tmp_u)
                    if len(tmp_u) >= 2: tmp_u[0] = tmp_u[0] + datetime.timedelta(minutes=30)
                    if min(tmp_u) > guest_deadline: warn_texts.append("사용 시 불가")
                except: pass
                tmp_d = sorted(alive_times)
                try:
                    tmp_d.remove(now)
                    if tmp_d:
                        tmp_d[0] = tmp_d[0] + datetime.timedelta(minutes=30)
                        if min(tmp_d) > guest_deadline: warn_texts.append("사망 시 불가")
                    else: warn_texts.append("사망 시 불가")
                except: pass
                if "사망 시 불가" in warn_texts:
                    msg.config(text="\n".join(warn_texts), fg="#FF5252"); c.config(highlightbackground="#FF1744", highlightthickness=2)
                elif "사용 시 불가" in warn_texts:
                    msg.config(text="\n".join(warn_texts), fg="#FFD600"); c.config(highlightbackground="#FFD600", highlightthickness=2)
                else: msg.config(text=""); c.config(highlightbackground="#333", highlightthickness=1)

        c, nl, tl, msg = ov_elements['f5']
        if nt_times['f5'] and now < nt_times['f5']:
            tl.config(text=nt_times['f5'].strftime('%H:%M'), fg="#FF5252")
            min_r = min(alive_times) if alive_times else now + datetime.timedelta(minutes=99)
            m_sec = (nt_times['f5'] - min_r).total_seconds()
            msg.config(text="⚠️ 리저 부족" if m_sec < 0 else f"{int(m_sec//60)}m 여유", fg="#FF1744" if m_sec < 0 else "#FFAB00")
            global guest_beep_flag
            if 58 <= (nt_times['f5'] - now).total_seconds() <= 61 and not guest_beep_flag:
                winsound.Beep(1000, 500); guest_beep_flag = True
        else: tl.config(text="READY", fg="#03DAC6"); msg.config(text=""); guest_beep_flag = False
        ov_elements['now'].config(text=now.strftime('%H:%M:%S'))

    # [핵심] 클릭 이벤트 처리 함수
    def on_click_event(k):
        now = datetime.datetime.now()
        if k in ['f1','f2','f3','f4']:
            # 현재 쿨타임 중이 아닐 때만 갱신 (리저 사용)
            if not nt_times[k] or now >= nt_times[k]:
                nt_times[k] = now + datetime.timedelta(minutes=30)
        elif k == 'f5':
            # 손님 사망 타이머 갱신
            nt_times['f5'] = now + datetime.timedelta(minutes=13)
            global guest_beep_flag
            guest_beep_flag = False
        update_display()
        update_clipboard()

    def create_overlay():
        global ov_root, ov_elements
        ov_root = tk.Tk(); ov_root.title("Resurrection_Timer")
        ov_root.attributes("-topmost", True, "-alpha", 0.95); ov_root.overrideredirect(True)
        ov_root.configure(bg="#0F0F0F")
        w, h = 300, 420; ov_root.geometry(f"{w}x{h}+{ov_root.winfo_screenwidth()-w-30}+{ov_root.winfo_screenheight()-h-120}")
        
        def sm(e): ov_root.x, ov_root.y = e.x, e.y
        def dm(e): ov_root.geometry(f"+{ov_root.winfo_x()+(e.x-ov_root.x)}+{ov_root.winfo_y()+(e.y-ov_root.y)}")
        ov_root.bind("<Button-1>", sm); ov_root.bind("<B1-Motion>", dm)

        header = tk.Frame(ov_root, bg="#1A1A1A", height=35); header.pack(fill="x")
        ov_elements['now'] = tk.Label(header, text="00:00:00", fg="#00FF7F", bg="#1A1A1A", font=("Segoe UI", 10, "bold"))
        ov_elements['now'].pack(side=tk.LEFT, padx=15)
        tk.Button(header, text="✕", bg="#1A1A1A", fg="#888", bd=0, command=lambda: os._exit(0)).pack(side=tk.RIGHT, padx=10)
        tk.Button(header, text="?", bg="#1A1A1A", fg="#888", bd=0, command=show_manual).pack(side=tk.RIGHT, padx=5)
        tk.Button(header, text="⚙", bg="#1A1A1A", fg="#888", bd=0, command=go_to_setup).pack(side=tk.RIGHT)

        main = tk.Frame(ov_root, bg="#0F0F0F", padx=10, pady=10); main.pack(fill="both", expand=True)

        def make_card(parent, k, is_guest=False):
            c = tk.Frame(parent, bg="#1E1E1E", bd=0, highlightthickness=1, highlightbackground="#333")
            nl = tk.Label(c, text=u[k], fg="#FFFFFF", bg="#1E1E1E", font=("Malgun Gothic", 9, "bold"))
            tl = tk.Label(c, text="READY", fg="#BB86FC" if not is_guest else "#03DAC6", bg="#1E1E1E", font=("Segoe UI", 15, "bold"))
            msg = tk.Label(c, text="", fg="#FF5252", bg="#1E1E1E", font=("Malgun Gothic", 8, "bold"), height=2)
            nl.pack(pady=(5,0)); tl.pack(); msg.pack(pady=(0,5))
            
            # 모든 위젯에 클릭 바인딩 (좌클릭: 실행, 우클릭: 상태 토글)
            widgets = [c, nl, tl, msg]
            for w_ in widgets:
                w_.bind("<Button-1>", lambda e, x=k: on_click_event(x))
                if not is_guest:
                    w_.bind("<Button-3>", lambda e, x=k: (resurrection_alive.update({x: not resurrection_alive[x]}), update_display()))
            return c, nl, tl, msg

        for i, k in enumerate(['f1','f2','f3','f4']):
            c, nl, tl, m = make_card(main, k)
            c.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="nsew")
            ov_elements[k] = (c, nl, tl, m)

        c, nl, tl, m = make_card(main, 'f5', is_guest=True)
        c.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        ov_elements['f5'] = (c, nl, tl, m)

        main.grid_columnconfigure(0, weight=1); main.grid_columnconfigure(1, weight=1)
        
        def auto_tick():
            if ov_root.winfo_exists(): update_display(); ov_root.after(1000, auto_tick)
        auto_tick(); ov_root.mainloop()

    create_overlay()

# [4] 설정 UI
def show_setup_ui():
    root = tk.Tk(); root.title("Resurrection_Timer Setup")
    root.geometry("420x580"); root.configure(bg="#121212")
    root.eval('tk::PlaceWindow . center')
    config = load_config()

    header = tk.Frame(root, bg="#1A1A1A", pady=25); header.pack(fill="x")
    tk.Label(header, text="Resurrection_Timer", font=("Segoe UI", 20, "bold"), bg="#1A1A1A", fg="#BB86FC").pack()
    tk.Button(header, text="사용 설명서 보기", font=("Segoe UI", 9), bg="#1A1A1A", fg="#03DAC6", bd=0, command=show_manual).pack(pady=5)

    f = tk.Frame(root, bg="#121212", pady=30); f.pack(padx=50, fill="x")
    ents = []
    for i in range(4):
        r = tk.Frame(f, bg="#121212"); r.pack(fill="x", pady=10)
        tk.Label(r, text=f"BISHOP {i+1}", font=("Segoe UI", 9, "bold"), bg="#121212", fg="#777", width=10, anchor="w").pack(side=tk.LEFT)
        e = tk.Entry(r, font=("Segoe UI", 12), bg="#1E1E1E", fg="white", insertbackground="white", bd=0, highlightthickness=1, highlightbackground="#333")
        e.insert(0, config["n"][i]); e.pack(side=tk.LEFT, expand=True, fill="x", ipady=8, padx=5)
        ents.append(e)

    def start():
        nv = [e.get() for e in ents]
        save_config(nv); root.destroy(); start_logic(nv)

    tk.Button(root, text="START MISSION", command=start, bg="#BB86FC", fg="#000", font=("Segoe UI", 13, "bold"), pady=15, bd=0).pack(pady=30, padx=50, fill="x")
    root.mainloop()

if __name__ == "__main__":
    show_setup_ui()
