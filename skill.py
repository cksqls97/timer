import keyboard, pyperclip, datetime, tkinter as tk, json, os, threading, sys, winsound, ctypes
from tkinter import messagebox

# [1] 관리자 권한 체크
def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

CFG_FILE = "timer_config.json"

def save_config(names, guests):
    with open(CFG_FILE, "w", encoding="utf-8") as f:
        json.dump({"n": names, "s": guests}, f, ensure_ascii=False, indent=4)

def load_config():
    if os.path.exists(CFG_FILE):
        try:
            with open(CFG_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"n": ["Bishop 1", "Bishop 2", "Bishop 3", "Bishop 4"], "s": ["Guest 1", "Guest 2"]}

ov_root = None
ov_elements = {}
resurrection_alive = {'f1': True, 'f2': True, 'f3': True, 'f4': True}
beep_flags = {'f5': False, 'f6': False}

def start_logic(names, specs):
    u = {'f1': [names[0], 30], 'f2': [names[1], 30], 'f3': [names[2], 30], 'f4': [names[3], 30],
         'f5': [specs[0], 13], 'f6': [specs[1] if specs[1].strip() else "", 13]}
    nt_times = {k: None for k in u.keys()}

    def go_to_setup():
        keyboard.unhook_all()
        if ov_root: ov_root.destroy()
        show_setup_ui()

    def toggle_resurrection(k):
        resurrection_alive[k] = not resurrection_alive[k]
        update_display()

    def update_clipboard():
        now = datetime.datetime.now()
        cur_time = now.strftime('%H%M')
        o_p, s_p = [], []
        for rk in ['f1','f2','f3','f4']:
            if nt_times[rk] and nt_times[rk] > now: o_p.append(f"{u[rk][0]} {nt_times[rk].strftime('%M')}")
            else: o_p.append(u[rk][0])
        for sk in ['f5', 'f6']:
            if u[sk][0].strip():
                if nt_times[sk] and nt_times[sk] > now: s_p.append(f"{u[sk][0]} {nt_times[sk].strftime('%M')}")
                else: s_p.append(u[sk][0])
        pyperclip.copy(f"현재시간 {cur_time} / {' '.join(o_p)} / {' '.join(s_p)}")

    def create_overlay():
        global ov_root, ov_elements
        ov_root = tk.Tk()
        ov_root.attributes("-topmost", True, "-alpha", 0.9) # 90% 투명도로 세련되게
        ov_root.overrideredirect(True)
        ov_root.configure(bg="#0F0F0F")
        w, h = 320, 440 
        ov_root.geometry(f"{w}x{h}+{ov_root.winfo_screenwidth()-w-30}+{ov_root.winfo_screenheight()-h-120}")
        
        def sm(e): ov_root.x, ov_root.y = e.x, e.y
        def dm(e): ov_root.geometry(f"+{ov_root.winfo_x()+(e.x-ov_root.x)}+{ov_root.winfo_y()+(e.y-ov_root.y)}")
        ov_root.bind("<Button-1>", sm); ov_root.bind("<B1-Motion>", dm)

        header = tk.Frame(ov_root, bg="#1A1A1A", height=30); header.pack(fill="x")
        ov_elements['now'] = tk.Label(header, text="00:00", fg="#888", bg="#1A1A1A", font=("Segoe UI", 10, "bold"))
        ov_elements['now'].pack(side=tk.LEFT, padx=10)
        tk.Button(header, text="✕", bg="#1A1A1A", fg="#555", bd=0, command=lambda: os._exit(0)).pack(side=tk.RIGHT, padx=5)
        tk.Button(header, text="⚙", bg="#1A1A1A", fg="#555", bd=0, command=go_to_setup).pack(side=tk.RIGHT)

        main = tk.Frame(ov_root, bg="#0F0F0F", padx=5, pady=5); main.pack(fill="both", expand=True)

        def make_card(parent, k, is_guest=False):
            # 카드 디자인: 다크 그레이 배경 + 라운드 느낌 (bd=0)
            c = tk.Frame(parent, bg="#1E1E1E", bd=2, highlightthickness=1, highlightbackground="#333")
            nl = tk.Label(c, text="-", fg="#AAA", bg="#1E1E1E", font=("Malgun Gothic", 9))
            tl = tk.Label(c, text="READY", fg="#BB86FC" if not is_guest else "#03DAC6", bg="#1E1E1E", font=("Segoe UI", 14, "bold"))
            msg = tk.Label(c, text="", fg="#FF5252", bg="#1E1E1E", font=("Malgun Gothic", 8, "bold"))
            nl.pack(pady=(5,0)); tl.pack(); msg.pack(pady=(0,5))
            if not is_guest:
                for w_ in [c, nl, tl, msg]: w_.bind("<Button-3>", lambda e, x=k: toggle_resurrection(x))
            return c, nl, tl, msg

        # Resurrection 영역
        for i, k in enumerate(['f1','f2','f3','f4']):
            c, nl, tl, m = make_card(main, k)
            c.grid(row=i//2, column=i%2, padx=4, pady=4, sticky="nsew")
            ov_elements[k] = (c, nl, tl, m)

        # Guest 영역
        guest_label = tk.Label(main, text="GUEST LIMIT (13M)", fg="#555", bg="#0F0F0F", font=("Segoe UI", 8, "bold"))
        guest_label.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        for i, k in enumerate(['f5','f6']):
            c, nl, tl, m = make_card(main, k, is_guest=True)
            c.grid(row=3, column=i, padx=4, pady=4, sticky="nsew")
            ov_elements[k] = (c, nl, tl, m)

        main.grid_columnconfigure(0, weight=1); main.grid_columnconfigure(1, weight=1)

        for k in u.keys():
            keyboard.add_hotkey(k, lambda x=k: on_key(x) if u[x][0].strip() else None, suppress=False)
        
        def auto_tick():
            if ov_root.winfo_exists(): update_display(); ov_root.after(1000, auto_tick)
        auto_tick(); ov_root.mainloop()

    def update_display():
        now = datetime.datetime.now()
        alive_times = [nt_times[rk] if nt_times[rk] and nt_times[rk] > now else now 
                       for rk in ['f1','f2','f3','f4'] if resurrection_alive[rk]]
        
        for rk in ['f1','f2','f3','f4']:
            c, nl, tl, msg = ov_elements[rk]
            nl.config(text=u[rk][0])
            if not resurrection_alive[rk]:
                c.config(highlightbackground="#441111", bg="#150A0A") # 사망 시 어둡게
                for w in [nl, tl, msg]: w.config(bg="#150A0A")
                tl.config(text="DEATH", fg="#552222"); msg.config(text="")
                continue
            
            c.config(bg="#1E1E1E"); nl.config(bg="#1E1E1E"); tl.config(bg="#1E1E1E"); msg.config(bg="#1E1E1E")
            if nt_times[rk] and nt_times[rk] > now:
                tl.config(text=nt_times[rk].strftime('%H:%M'), fg="#FF5252")
                msg.config(text=""); c.config(highlightbackground="#333", highlightthickness=1)
            else:
                tl.config(text="READY", fg="#4CAF50")
                tmp_d = list(alive_times)
                try: tmp_d.remove(now)
                except: pass
                next_if_d = min(tmp_d) if tmp_d else now + datetime.timedelta(minutes=99)
                tmp_u = list(alive_times)
                try: idx = tmp_u.index(now); tmp_u[idx] = now + datetime.timedelta(minutes=30)
                except: pass
                next_if_u = min(tmp_u) if tmp_u else now + datetime.timedelta(minutes=99)

                if (next_if_d - now).total_seconds() > 14 * 60:
                    msg.config(text="사망 시 손님 불가", fg="#FF5252")
                    c.config(highlightbackground="#FF1744", highlightthickness=2)
                elif (next_if_u - now).total_seconds() > 14 * 60:
                    msg.config(text="사용 시 손님 불가", fg="#FFD600")
                    c.config(highlightbackground="#FFD600", highlightthickness=2)
                else: msg.config(text=""); c.config(highlightbackground="#333", highlightthickness=1)

        min_res = min(alive_times) if alive_times else now + datetime.timedelta(minutes=99)
        for k in ['f5','f6']:
            c, nl, tl, msg = ov_elements[k]
            if not u[k][0].strip(): 
                c.grid_remove(); continue
            c.grid_show() if hasattr(c, 'grid_show') else None # 필요시
            nl.config(text=u[k][0])
            if nt_times[k] and now < nt_times[k]:
                tl.config(text=nt_times[k].strftime('%H:%M'), fg="#FF5252")
                diff = (nt_times[k] - now).total_seconds()
                m_sec = diff - (min_res - now).total_seconds()
                msg.config(text="⚠️ 부활 불가" if m_sec < 0 else f"{int(m_sec//60)}m 전", fg="#FF1744" if m_sec < 0 else "#FFAB00")
                if 58 <= diff <= 61 and not beep_flags[k]:
                    winsound.Beep(1000, 500); beep_flags[k] = True
            else: tl.config(text="READY", fg="#03DAC6"); msg.config(text=""); beep_flags[k] = False
        ov_elements['now'].config(text=now.strftime('%H:%M:%S'))

    def on_key(k):
        now = datetime.datetime.now()
        if k in ['f1','f2','f3','f4']:
            if resurrection_alive[k] and (not nt_times[k] or now >= nt_times[k]):
                nt_times[k] = now + datetime.timedelta(minutes=30)
        else:
            nt_times[k] = now + datetime.timedelta(minutes=13); beep_flags[k] = False
        update_display(); update_clipboard()

    create_overlay()

def show_setup_ui():
    root = tk.Tk(); root.title("Raid Timer Setup"); root.geometry("400x680"); root.configure(bg="#F0F0F0")
    root.eval('tk::PlaceWindow . center')
    config = load_config()
    
    tk.Label(root, text="TIMER SETUP", font=("Segoe UI", 20, "bold"), bg="#F0F0F0", fg="#222").pack(pady=20)
    frame = tk.Frame(root, bg="#F0F0F0"); frame.pack(padx=40, fill="x")
    
    def add_e(parent, txt, d):
        r = tk.Frame(parent, bg="#F0F0F0"); r.pack(fill="x", pady=5)
        tk.Label(r, text=txt, width=12, anchor="w", bg="#F0F0F0", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        e = tk.Entry(r, font=("Segoe UI", 10), bd=1, relief="solid"); e.insert(0, d); e.pack(side=tk.LEFT, expand=True, fill="x")
        return e

    tk.Label(frame, text="RESURRECTION MEMBERS", fg="#6200EE", font=("Segoe UI", 9, "bold"), bg="#F0F0F0").pack(anchor="w")
    n_ents = [add_e(frame, f"Member {i+1}", config["n"][i]) for i in range(4)]
    tk.Label(frame, text="GUEST MEMBERS", fg="#009688", font=("Segoe UI", 9, "bold"), bg="#F0F0F0").pack(anchor="w", pady=(20, 0))
    s_ents = [add_e(frame, f"Guest {i+1}", config["s"][i]) for i in range(2)]

    def start():
        nv, sv = [e.get() for e in n_ents], [e.get() for e in s_ents]
        save_config(nv, sv); root.destroy(); start_logic(nv, sv)

    tk.Button(root, text="START MISSION", command=start, bg="#222", fg="white", font=("Segoe UI", 12, "bold"), pady=12, bd=0).pack(pady=40, padx=40, fill="x")
    root.mainloop()

if __name__ == "__main__":
    show_setup_ui()
