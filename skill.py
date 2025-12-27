import pyperclip, datetime, json, os, sys, winsound, ctypes
import tkinter as tk
from tkinter import messagebox

# [1] 설정 파일 경로
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
nt_times = {}
res_alive = {}
ov_elements = {}
guest_beep_flag = False
u_names = {}

# [2] 메인 타이머 로직
def start_logic(names):
    global nt_times, res_alive, ov_elements, u_names
    keys = ['F1', 'F2', 'F3', 'F4', 'F5']
    u_names = {keys[i]: names[i] for i in range(4)}
    u_names['F5'] = "손님"
    
    nt_times = {k: None for k in keys}
    res_alive = {k: True for k in keys[:4]}

    def update_clipboard():
        now = datetime.datetime.now()
        cur_time = now.strftime('%H%M')
        o_p = []
        for rk in keys[:4]:
            if nt_times[rk] and nt_times[rk] > now:
                o_p.append(f"{u_names[rk]} {nt_times[rk].strftime('%M')}")
            else:
                o_p.append(u_names[rk])
        g_str = f"손님 {nt_times['F5'].strftime('%M')}" if nt_times['F5'] and nt_times['F5'] > now else "손님"
        pyperclip.copy(f"현재 {cur_time} | {' '.join(o_p)} | {g_str}")

    def on_click(k):
        now = datetime.datetime.now()
        if k in keys[:4]:
            if res_alive[k]:
                nt_times[k] = now + datetime.timedelta(minutes=30)
        else: # F5 (손님)
            nt_times['F5'] = now + datetime.timedelta(minutes=13)
            global guest_beep_flag
            guest_beep_flag = False
        update_display()
        update_clipboard()

    def toggle_status(k):
        res_alive[k] = not res_alive[k]
        update_display()

    def update_display():
        now = datetime.datetime.now()
        for k in keys[:4]:
            c, nl, tl = ov_elements[k]
            if not res_alive[k]:
                c.config(bg="#2A0A0A", highlightbackground="#441111")
                nl.config(bg="#2A0A0A", fg="#666")
                tl.config(bg="#2A0A0A", text="D.O", fg="#552222")
            elif nt_times[k] and nt_times[k] > now:
                c.config(bg="#1A1A1A", highlightbackground="#333")
                nl.config(bg="#1A1A1A", fg="white")
                tl.config(bg="#1A1A1A", text=nt_times[k].strftime('%M:%S'), fg="#FF5252")
            else:
                c.config(bg="#1E1E1E", highlightbackground="#4CAF50")
                nl.config(bg="#1E1E1E", fg="white")
                tl.config(bg="#1E1E1E", text="READY", fg="#4CAF50")

        # 손님 섹션
        c_g, nl_g, tl_g = ov_elements['F5']
        if nt_times['F5'] and nt_times['F5'] > now:
            diff = (nt_times['F5'] - now).total_seconds()
            tl_g.config(text=nt_times['F5'].strftime('%M:%S'), fg="#FF5252")
            global guest_beep_flag
            if 58 <= diff <= 61 and not guest_beep_flag:
                winsound.Beep(1000, 500); guest_beep_flag = True
        else:
            tl_g.config(text="READY", fg="#03DAC6")

    # --- 오버레이 생성 ---
    ov_root = tk.Tk()
    ov_root.title("Res_Clicker")
    ov_root.attributes("-topmost", True, "-alpha", 0.85)
    ov_root.overrideredirect(True)
    ov_root.configure(bg="#0F0F0F")
    
    # 창 위치: 화면 오른쪽 하단 적절한 곳
    w, h = 220, 360
    screen_w = ov_root.winfo_screenwidth()
    screen_h = ov_root.winfo_screenheight()
    ov_root.geometry(f"{w}x{h}+{screen_w - w - 50}+{screen_h - h - 100}")

    # 드래그 이동
    def sm(e): ov_root.x, ov_root.y = e.x, e.y
    def dm(e): ov_root.geometry(f"+{ov_root.winfo_x()+(e.x-ov_root.x)}+{ov_root.winfo_y()+(e.y-ov_root.y)}")
    ov_root.bind("<Button-1>", sm); ov_root.bind("<B1-Motion>", dm)

    header = tk.Frame(ov_root, bg="#1A1A1A", height=30)
    header.pack(fill="x")
    tk.Label(header, text="RES TIMER", fg="#BB86FC", bg="#1A1A1A", font=("Segoe UI", 8, "bold")).pack(side="left", padx=10)
    tk.Button(header, text="✕", bg="#1A1A1A", fg="#555", bd=0, command=lambda: os._exit(0)).pack(side="right", padx=5)

    main = tk.Frame(ov_root, bg="#0F0F0F", padx=5, pady=5)
    main.pack(fill="both", expand=True)

    for k in keys:
        is_guest = (k == 'F5')
        c = tk.Frame(main, bg="#1E1E1E", bd=0, highlightthickness=1, highlightbackground="#333")
        c.pack(fill="x", pady=2)
        
        nl = tk.Label(c, text=u_names[k], fg="white", bg="#1E1E1E", font=("Malgun Gothic", 9, "bold"))
        nl.pack(pady=(5,0))
        
        tl = tk.Label(c, text="READY", fg="#4CAF50" if not is_guest else "#03DAC6", bg="#1E1E1E", font=("Segoe UI", 14, "bold"))
        tl.pack(pady=(0,5))
        
        ov_elements[k] = (c, nl, tl)
        
        # 클릭 이벤트 바인딩 (컴포넌트 전체)
        for w_ in [c, nl, tl]:
            w_.bind("<Button-1>", lambda e, x=k: on_click(x))
            if not is_guest:
                w_.bind("<Button-3>", lambda e, x=k: toggle_status(x))

    def auto_tick():
        if ov_root.winfo_exists(): update_display(); ov_root.after(1000, auto_tick)
    
    auto_tick()
    ov_root.mainloop()

# [3] 설정 UI
def show_setup_ui():
    root = tk.Tk()
    root.title("Setup")
    root.geometry("350x450")
    root.configure(bg="#121212")
    
    config = load_config()

    tk.Label(root, text="BISHOP ROTATION", font=("Segoe UI", 16, "bold"), bg="#121212", fg="#BB86FC").pack(pady=20)

    ents = []
    for i in range(4):
        f = tk.Frame(root, bg="#121212")
        f.pack(fill="x", padx=40, pady=5)
        tk.Label(f, text=f"B{i+1}", fg="#777", bg="#121212", width=3).pack(side="left")
        e = tk.Entry(f, bg="#1E1E1E", fg="white", bd=0, highlightthickness=1, highlightbackground="#333")
        e.insert(0, config["n"][i])
        e.pack(side="left", fill="x", expand=True, ipady=5)
        ents.append(e)

    def start():
        nv = [e.get() for e in ents]
        save_config(nv)
        root.destroy()
        start_logic(nv)

    tk.Button(root, text="START MISSION", command=start, bg="#BB86FC", fg="black", font=("Segoe UI", 10, "bold"), pady=10).pack(pady=30, padx=40, fill="x")
    
    root.mainloop()

if __name__ == "__main__":
    show_setup_ui()
