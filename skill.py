import keyboard, pyperclip, datetime, tkinter as tk, json, os, sys, winsound, ctypes

# [1] 관리자 권한 및 JSON 로드 (생략/유지)
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
                data = json.load(f); return data if data.get("n") else {"n": ["비숍1", "비숍2", "비숍3", "비숍4"]}
        except: pass
    return {"n": ["비숍1", "비숍2", "비숍3", "비숍4"]}

ov_root = None
ov_elements = {}
res_alive = {'f1': True, 'f2': True, 'f3': True, 'f4': True}

def start_logic(names):
    u = {'f1': names[0], 'f2': names[1], 'f3': names[2], 'f4': names[3], 'f5': "손님"}
    nt_times = {k: None for k in u.keys()}

    def update_display():
        now = datetime.datetime.now()
        # 생존 비숍들의 가용 시각 리스트 (준비 완료면 now)
        alive_times = sorted([nt_times[rk] if nt_times[rk] and nt_times[rk] > now else now 
                             for rk in ['f1','f2','f3','f4'] if res_alive[rk]])

        for rk in ['f1', 'f2', 'f3', 'f4']:
            c, nl, tl, msg = ov_elements[rk]
            nl.config(text=u[rk], fg="white")
            
            if not res_alive[rk]:
                c.config(highlightbackground="#441111", bg="#150A0A")
                tl.config(text="DEATH", fg="#552222"); msg.config(text=""); continue
            
            if nt_times[rk] and nt_times[rk] > now:
                tl.config(text=nt_times[rk].strftime('%H:%M'), fg="#FF5252")
                msg.config(text=""); c.config(highlightbackground="#333", highlightthickness=1)
            else:
                tl.config(text="READY", fg="#4CAF50")
                
                warns = []
                # --- [로직 핵심: 연속 사망 가정 시뮬레이션] ---
                
                # 1. 내가 사용했을 때 (Use)
                # 내가 쓰고(30분 뒤), 그다음 사람도 썼을 때(손님 즉시 재사망 대비), 세 번째 리저가 13분 이내인가?
                tmp_u = sorted(alive_times)
                try: 
                    idx = tmp_u.index(now)
                    tmp_u[idx] = now + datetime.timedelta(minutes=30) # 내가 씀
                    tmp_u = sorted(tmp_u)
                    if len(tmp_u) >= 2:
                        tmp_u[0] = tmp_u[0] + datetime.timedelta(minutes=30) # 그다음 사람이 즉시 살림
                    next_res_after_use = min(tmp_u)
                    if (next_res_after_use - now).total_seconds() > 13 * 60:
                        warns.append("사용 시 불가")
                except: pass

                # 2. 내가 죽었을 때 (Death)
                # 내가 죽고(리스트 제외), 남은 사람 중 한 명이 살렸을 때, 그다음 리저가 13분 이내인가?
                tmp_d = sorted(alive_times)
                try: 
                    tmp_d.remove(now) # 내가 죽음
                    if tmp_d:
                        tmp_d[0] = tmp_d[0] + datetime.timedelta(minutes=30) # 남은 첫 사람이 살림
                        next_res_after_death = min(tmp_d)
                        if (next_res_after_death - now).total_seconds() > 13 * 60:
                            warns.append("사망 시 불가")
                    else: # 남은 비숍이 없음
                        warns.append("사망 시 불가")
                except: pass

                # 표시 업데이트
                if "사망 시 불가" in warns:
                    msg.config(text="\n".join(warns), fg="#FF5252")
                    c.config(highlightbackground="#FF1744", highlightthickness=2)
                elif "사용 시 불가" in warns:
                    msg.config(text="\n".join(warns), fg="#FFD600")
                    c.config(highlightbackground="#FFD600", highlightthickness=2)
                else:
                    msg.config(text=""); c.config(highlightbackground="#333", highlightthickness=1)

        # 손님 정보 (단순 마지노선 표시)
        c, nl, tl, msg = ov_elements['f5']
        if nt_times['f5'] and now < nt_times['f5']:
            tl.config(text=nt_times['f5'].strftime('%H:%M'), fg="#FF5252")
            m_sec = (nt_times['f5'] - (min(alive_times) if alive_times else now)).total_seconds()
            msg.config(text="⚠️ 리저 부족" if m_sec < 0 else f"{int(m_sec//60)}m 여유", fg="#FF1744" if m_sec < 0 else "#FFAB00")
        else: tl.config(text="READY", fg="#03DAC6"); msg.config(text="")
        ov_elements['now'].config(text=now.strftime('%H:%M:%S'))

    def on_key(k):
        now = datetime.datetime.now()
        if k in ['f1','f2','f3','f4']:
            if res_alive[k] and (not nt_times[k] or now >= nt_times[k]):
                nt_times[k] = now + datetime.timedelta(minutes=30)
        elif k == 'f5':
            nt_times['f5'] = now + datetime.timedelta(minutes=13)
        update_display()
        # 클립보드 생략

    def create_overlay():
        global ov_root, ov_elements
        ov_root = tk.Tk()
        ov_root.attributes("-topmost", True, "-alpha", 0.95); ov_root.overrideredirect(True)
        ov_root.configure(bg="#0F0F0F")
        w, h = 300, 420; ov_root.geometry(f"{w}x{h}+{ov_root.winfo_screenwidth()-w-30}+{ov_root.winfo_screenheight()-h-120}")
        
        header = tk.Frame(ov_root, bg="#1A1A1A", height=35); header.pack(fill="x")
        ov_elements['now'] = tk.Label(header, text="00:00:00", fg="#00FF7F", bg="#1A1A1A", font=("Segoe UI", 10, "bold"))
        ov_elements['now'].pack(side=tk.LEFT, padx=15)
        tk.Button(header, text="✕", bg="#1A1A1A", fg="#888", bd=0, command=lambda: os._exit(0)).pack(side=tk.RIGHT, padx=10)
        
        main = tk.Frame(ov_root, bg="#0F0F0F", padx=10, pady=10); main.pack(fill="both", expand=True)
        def make_card(parent, k, is_guest=False):
            c = tk.Frame(parent, bg="#1E1E1E", bd=0, highlightthickness=1, highlightbackground="#333")
            nl = tk.Label(c, text=u[k], fg="white", bg="#1E1E1E", font=("Malgun Gothic", 9, "bold"))
            tl = tk.Label(c, text="READY", fg="#BB86FC" if not is_guest else "#03DAC6", bg="#1E1E1E", font=("Segoe UI", 15, "bold"))
            msg = tk.Label(c, text="", fg="#FF5252", bg="#1E1E1E", font=("Malgun Gothic", 8, "bold"), height=2)
            nl.pack(pady=(5,0)); tl.pack(); msg.pack(pady=(0,5))
            if not is_guest:
                for w_ in [c, nl, tl, msg]: w_.bind("<Button-3>", lambda e, x=k: (res_alive.update({x: not res_alive[x]}), update_display()))
            return c, nl, tl, msg

        for i, k in enumerate(['f1','f2','f3','f4']):
            c, nl, tl, m = make_card(main, k)
            c.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="nsew")
            ov_elements[k] = (c, nl, tl, m)
        c, nl, tl, m = make_card(main, 'f5', is_guest=True)
        c.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        ov_elements['f5'] = (c, nl, tl, m)

        main.grid_columnconfigure(0, weight=1); main.grid_columnconfigure(1, weight=1)
        for k in ['f1','f2','f3','f4','f5']: keyboard.add_hotkey(k, lambda x=k: on_key(x), suppress=False)
        def auto_tick():
            if ov_root.winfo_exists(): update_display(); ov_root.after(1000, auto_tick)
        auto_tick(); ov_root.mainloop()

    create_overlay()

# 설정 UI 생략 (기존 동일)
def show_setup_ui():
    root = tk.Tk(); root.title("Setup"); root.geometry("400x500")
    config = load_config()
    ents = []
    for i in range(4):
        r = tk.Frame(root); r.pack(pady=5)
        tk.Label(r, text=f"비숍 {i+1}").pack(side=tk.LEFT)
        e = tk.Entry(r); e.insert(0, config["n"][i]); e.pack(side=tk.LEFT); ents.append(e)
    tk.Button(root, text="START", command=lambda: (save_config([e.get() for e in ents]), root.destroy(), start_logic([e.get() for e in ents]))).pack(pady=20)
    root.mainloop()

if __name__ == "__main__": show_setup_ui()
