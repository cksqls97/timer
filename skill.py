import keyboard, pyperclip, datetime, tkinter as tk, json, os, threading, sys, winsound, ctypes
from tkinter import messagebox

# [1] 관리자 권한 자동 실행
def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

CFG = resource_path("timer_config.json")

def save(n, s):
    try:
        with open("timer_config.json", "w", encoding="utf-8") as f:
            json.dump({"n": n, "s": s}, f, ensure_ascii=False)
    except: pass

def load():
    target = "timer_config.json" if os.path.exists("timer_config.json") else CFG
    if os.path.exists(target):
        try:
            with open(target, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"n": ["안녕동주야", "브레멘비숍", "외화유출비숍", "돼승끼"], "s": ["손님1", "손님2"]}

ov_root = None
ov_elements = {}
beep_flags = {'f5': False, 'f6': False}

def custom_notify(title, message, color="#333"):
    def run():
        nt = tk.Toplevel()
        nt.overrideredirect(True); nt.attributes("-topmost", True)
        w, h = 300, 90
        sx, sy = nt.winfo_screenwidth() - w - 20, nt.winfo_screenheight() - h - 50
        nt.geometry(f"{w}x{h}+{sx}+{sy}"); nt.configure(bg=color)
        tk.Label(nt, text=title, fg="white", bg=color, font=("Malgun Gothic", 11, "bold")).pack(pady=(10, 0))
        tk.Label(nt, text=message, fg="white", bg=color, font=("Malgun Gothic", 10), wraplength=280).pack(pady=5)
        nt.after(3000, nt.destroy); nt.mainloop()
    threading.Thread(target=run, daemon=True).start()

def start_logic(names, specs):
    try:
        u = {
            'f1': [names[0], 30], 'f2': [names[1], 30], 'f3': [names[2], 30], 'f4': [names[3], 30],
            'f5': [specs[0], 13], 'f6': [specs[1] if specs[1].strip() else "", 13]
        }
        nt_times = {k: None for k in u.keys()}

        def go_to_setup():
            keyboard.unhook_all(); ov_root.destroy(); ui()

        def create_overlay():
            global ov_root, ov_elements
            ov_root = tk.Tk()
            ov_root.attributes("-topmost", True); ov_root.overrideredirect(True)
            ov_root.configure(bg="#121212")
            
            # 텍스트 가독성을 위해 오버레이 크기 조정
            w, h = 420, 520 
            sx, sy = ov_root.winfo_screenwidth() - w - 20, ov_root.winfo_screenheight() - h - 150
            ov_root.geometry(f"{w}x{h}+{sx}+{sy}")
            
            def sm(e): ov_root.x, ov_root.y = e.x, e.y
            def dm(e): ov_root.geometry(f"+{ov_root.winfo_x()+(e.x-ov_root.x)}+{ov_root.winfo_y()+(e.y-ov_root.y)}")
            ov_root.bind("<Button-1>", sm); ov_root.bind("<B1-Motion>", dm)

            header = tk.Frame(ov_root, bg="#3d5afe", height=50); header.pack(fill="x")
            ov_elements['now'] = tk.Label(header, text="READY", fg="white", bg="#3d5afe", font=("Malgun Gothic", 13, "bold"))
            ov_elements['now'].pack(side=tk.LEFT, padx=20, pady=10)

            tk.Button(header, text="✕", bg="#3d5afe", fg="white", bd=0, font=("Arial", 14, "bold"), command=lambda: os._exit(0)).pack(side=tk.RIGHT, padx=10)
            tk.Button(header, text="⚙", bg="#3d5afe", fg="white", bd=0, font=("Arial", 16), command=go_to_setup).pack(side=tk.RIGHT, padx=5)

            main_cont = tk.Frame(ov_root, bg="#121212", padx=15, pady=15); main_cont.pack(fill="both", expand=True)

            def create_card(parent, title_color):
                card = tk.Frame(parent, bg="#262626", bd=2, relief="ridge", padx=10, pady=12)
                nl = tk.Label(card, text="-", fg="white", bg="#262626", font=("Malgun Gothic", 12, "bold"))
                tl = tk.Label(card, text="READY", fg=title_color, bg="#262626", font=("Malgun Gothic", 11, "bold"))
                msg = tk.Label(card, text="", fg="#ffab00", bg="#262626", font=("Malgun Gothic", 10, "bold"))
                nl.pack(); tl.pack(); msg.pack()
                return card, nl, tl, msg

            # Resurrection 섹션
            tk.Label(main_cont, text="Resurrection Members (F1-F4)", fg="#BB86FC", bg="#121212", font=("Malgun Gothic", 11, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,10))
            for i, k in enumerate(['f1', 'f2', 'f3', 'f4']):
                card, nl, tl, msg = create_card(main_cont, "#BB86FC")
                card.grid(row=(i//2)+1, column=i%2, padx=8, pady=8, sticky="nsew")
                ov_elements[k] = (nl, tl, msg)

            # Guest 섹션
            tk.Label(main_cont, text="Guest Members (F5-F6)", fg="#03DAC6", bg="#121212", font=("Malgun Gothic", 11, "bold")).grid(row=3, column=0, columnspan=2, sticky="w", pady=(15,10))
            for i, k in enumerate(['f5', 'f6']):
                card, nl, tl, msg = create_card(main_cont, "#03DAC6")
                card.grid(row=4, column=i, padx=8, pady=8, sticky="nsew")
                ov_elements[k] = (nl, tl, msg)

            main_cont.grid_columnconfigure(0, weight=1); main_cont.grid_columnconfigure(1, weight=1)

            for k in u.keys():
                keyboard.add_hotkey(k, lambda x=k: p(x) if u[x][0].strip() else None, suppress=False)
            
            def auto_update():
                if ov_root and ov_root.winfo_exists():
                    up()
                    ov_root.after(1000, auto_update)
            auto_update(); ov_root.mainloop()

        def up():
            now = datetime.datetime.now()
            cur_time_clip = now.strftime('%H%M')
            o_clip, s_clip = [], []
            rez_cools = []
            
            # Resurrection 업데이트
            for rk in ['f1', 'f2', 'f3', 'f4']:
                nl, tl, msg = ov_elements[rk]
                nl.config(text=u[rk][0])
                if nt_times[rk] and nt_times[rk] > now:
                    diff_min = (nt_times[rk] - now).total_seconds() / 60
                    tl.config(text=nt_times[rk].strftime('%H:%M'), fg="#ff5252")
                    o_clip.append(f"{u[rk][0]} {nt_times[rk].strftime('%M')}")
                    rez_cools.append(nt_times[rk])
                    # 다음 리저까지 15분 이상 남으면 경고 메시지 변경
                    if diff_min >= 15: msg.config(text="사용시 손님 부활 불가", fg="#ff5252")
                    else: msg.config(text="")
                else:
                    tl.config(text="READY", fg="#4caf50")
                    msg.config(text="")
                    if u[rk][0].strip():
                        rez_cools.append(now)
                        o_clip.append(u[rk][0])

            min_rez_ready = min(rez_cools) if rez_cools else None

            # Guest 업데이트
            for k in ['f5', 'f6']:
                nm = u[k][0].strip()
                if not nm: continue
                nl, tl, msg = ov_elements[k]
                nl.config(text=nm)
                if nt_times[k] and now < nt_times[k]:
                    tl.config(text=nt_times[k].strftime('%H:%M'), fg="#ff5252")
                    s_clip.append(f"{nm} {nt_times[k].strftime('%M')}")
                    
                    if min_rez_ready is None:
                        msg.config(text="⚠️ Resurrection 부재", fg="#ff1744")
                    else:
                        margin = (nt_times[k] - now).total_seconds() - (min_rez_ready - now).total_seconds()
                        if margin < 0: msg.config(text="⚠️ 부활 불가", fg="#ff1744")
                        else: msg.config(text=f"{int(margin // 60)}분 전", fg="#ffab00")
                    
                    diff = (nt_times[k] - now).total_seconds()
                    if 58 <= diff <= 61 and not beep_flags[k]:
                        winsound.Beep(1000, 500); beep_flags[k] = True
                else:
                    tl.config(text="READY", fg="#4caf50"); msg.config(text="")
                    s_clip.append(nm); beep_flags[k] = False

            pyperclip.copy(f"현재시간 {cur_time_clip} / {' '.join(o_clip)} / {' '.join(s_clip)}")
            if ov_root: ov_elements['now'].config(text=f"🕒 {now.strftime('%H:%M')}")

        def p(k):
            now = datetime.datetime.now()
            if k in ['f1', 'f2', 'f3', 'f4']:
                if nt_times[k] and now < nt_times[k]:
                    custom_notify("Cooldown", f"{u[k][0]}: On cooldown!", "#d32f2f")
                    return
                nt_times[k] = now + datetime.timedelta(minutes=u[k][1])
                custom_notify("Used", f"{u[k][0]} Resurrection", "#3d5afe")
            else:
                nt_times[k] = now + datetime.timedelta(minutes=u[k][1])
                beep_flags[k] = False
                custom_notify("Death", f"{u[k][0]} Guest", "#2e7d32")
            up()

        create_overlay()
    except Exception as e:
        messagebox.showerror("Error", str(e)); os._exit(1)

def ui():
    root = tk.Tk(); root.title("Skill Timer Setup"); root.geometry("420x720"); root.configure(bg="#f8f9fa")
    root.eval('tk::PlaceWindow . center')
    c = load()
    tk.Label(root, text="TIMER SETUP", font=("Malgun Gothic", 20, "bold"), bg="#f8f9fa", fg="#333").pack(pady=(30, 20))
    container = tk.Frame(root, bg="#f8f9fa"); container.pack(padx=40, fill="x")
    
    def create_row(parent, txt, d_val):
        row = tk.Frame(parent, bg="#f8f9fa"); row.pack(fill="x", pady=8)
        tk.Label(row, text=txt, width=15, anchor="w", bg="#f8f9fa", font=("Malgun Gothic", 11)).pack(side=tk.LEFT)
        e = tk.Entry(row, bd=1, relief="solid", font=("Malgun Gothic", 11)); e.insert(0, d_val); e.pack(side=tk.LEFT, expand=True, fill="x", padx=(10, 0))
        return e

    ents = []
    tk.Label(container, text="[ Resurrection Members ]", bg="#f8f9fa", fg="#6200EE", font=("Malgun Gothic", 11, "bold")).pack(anchor="w", pady=(10, 5))
    for i in range(4): ents.append(create_row(container, f"Member {i+1}", c["n"][i]))
    
    tk.Frame(container, height=1, bg="#dee2e6").pack(fill="x", pady=25)
    
    s_ents = []
    tk.Label(container, text="[ Guest Members ]", bg="#f8f9fa", fg="#03DAC6", font=("Malgun Gothic", 11, "bold")).pack(anchor="w", pady=(0, 5))
    for i in range(2): s_ents.append(create_row(container, f"Guest {i+1}", c["s"][i]))
    
    def go():
        n, s = [e.get() for e in ents], [e.get() for e in s_ents]
        save(n, s); root.destroy(); start_logic(n, s)
        
    tk.Button(root, text="START TIMER", command=go, bg="#6200EE", fg="white", font=("Malgun Gothic", 15, "bold"), pady=15).pack(pady=40, padx=40, fill="x")
    root.mainloop()

if __name__ == "__main__": ui()
