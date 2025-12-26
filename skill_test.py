import keyboard, pyperclip, datetime, tkinter as tk, json, os, threading, sys, winsound
from tkinter import messagebox

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
rezzer_alive = {'f1': True, 'f2': True, 'f3': True, 'f4': True}
nt_times = {} # 전역 참조를 위해 위치 이동

def custom_notify(title, message, color="#333"):
    def run():
        nt = tk.Toplevel()
        nt.overrideredirect(True); nt.attributes("-topmost", True)
        w, h = 280, 80
        sx, sy = nt.winfo_screenwidth() - w - 20, nt.winfo_screenheight() - h - 50
        nt.geometry(f"{w}x{h}+{sx}+{sy}"); nt.configure(bg=color)
        tk.Label(nt, text=title, fg="white", bg=color, font=("Malgun Gothic", 10, "bold")).pack(pady=(10, 0))
        tk.Label(nt, text=message, fg="white", bg=color, font=("Malgun Gothic", 9), wraplength=250).pack(pady=5)
        nt.after(3000, nt.destroy); nt.mainloop()
    threading.Thread(target=run, daemon=True).start()

def start_logic(names, specs):
    global nt_times
    try:
        u = {
            'f1': [names[0], 30], 'f2': [names[1], 30], 'f3': [names[2], 30], 'f4': [names[3], 30],
            'f5': [specs[0], 13], 'f6': [specs[1] if specs[1].strip() else "", 13]
        }
        nt_times = {k: None for k in u.keys()}

        def test_skip_time():
            """테스트용 로직: 모든 활성 타이머를 1분씩 앞으로 당김"""
            for k in nt_times:
                if nt_times[k]:
                    nt_times[k] = nt_times[k] - datetime.timedelta(minutes=1)
            up()
            custom_notify("TEST", "Time shifted +1 minute", "#444")

        def create_overlay():
            global ov_root, ov_elements
            ov_root = tk.Tk()
            ov_root.attributes("-topmost", True); ov_root.overrideredirect(True)
            ov_root.configure(bg="#121212")
            
            w, h = 360, 420
            sx, sy = ov_root.winfo_screenwidth() - w - 20, ov_root.winfo_screenheight() - h - 180
            ov_root.geometry(f"{w}x{h}+{sx}+{sy}")
            
            def sm(e): ov_root.x, ov_root.y = e.x, e.y
            def dm(e): ov_root.geometry(f"+{ov_root.winfo_x()+(e.x-ov_root.x)}+{ov_root.winfo_y()+(e.y-ov_root.y)}")
            ov_root.bind("<Button-1>", sm); ov_root.bind("<B1-Motion>", dm)

            header = tk.Frame(ov_root, bg="#d32f2f", height=45); header.pack(fill="x") # 테스트용은 헤더 빨간색
            ov_elements['now'] = tk.Label(header, text="TEST MODE", fg="white", bg="#d32f2f", font=("Malgun Gothic", 10, "bold"))
            ov_elements['now'].pack(side=tk.LEFT, padx=10, pady=8)

            # 제어 버튼들
            tk.Button(header, text="✕", bg="#d32f2f", fg="white", bd=0, font=("Arial", 12, "bold"), command=lambda: os._exit(0)).pack(side=tk.RIGHT, padx=5)
            tk.Button(header, text="⚙", bg="#d32f2f", fg="white", bd=0, font=("Arial", 14), command=lambda: [keyboard.unhook_all(), ov_root.destroy(), ui()]).pack(side=tk.RIGHT, padx=5)
            
            # [테스트 버튼] 1분 스킵 버튼 추가
            tk.Button(header, text="+1m", bg="#ffeb3b", fg="black", bd=0, font=("Arial", 10, "bold"), command=test_skip_time).pack(side=tk.RIGHT, padx=10)

            main_cont = tk.Frame(ov_root, bg="#121212", padx=15, pady=10); main_cont.pack(fill="both", expand=True)

            def create_card(parent, title_color, k, is_guest=False):
                card = tk.Frame(parent, bg="#262626", bd=2, relief="ridge", padx=10, pady=8)
                name_lbl = tk.Label(card, text="-", fg="white", bg="#262626", font=("Malgun Gothic", 10, "bold"))
                time_lbl = tk.Label(card, text="READY", fg=title_color, bg="#262626", font=("Malgun Gothic", 9))
                name_lbl.pack(); time_lbl.pack()
                margin_lbl = tk.Label(card, text="", fg="#ffab00", bg="#262626", font=("Malgun Gothic", 8, "italic"))
                if is_guest: margin_lbl.pack()
                else: 
                    card.bind("<Button-3>", lambda e, x=k: [rezzer_alive.__setitem__(x, not rezzer_alive[x]), up()])
                return card, name_lbl, time_lbl, margin_lbl

            for i, k in enumerate(['f1', 'f2', 'f3', 'f4']):
                card, nl, tl, _ = create_card(main_cont, "#BB86FC", k)
                card.grid(row=(i//2)+1, column=i%2, padx=5, pady=5, sticky="nsew")
                ov_elements[k] = (card, nl, tl)

            for i, k in enumerate(['f5', 'f6']):
                card, nl, tl, ml = create_card(main_cont, "#03DAC6", k, is_guest=True)
                card.grid(row=4, column=i, padx=5, pady=5, sticky="nsew")
                ov_elements[k] = (card, nl, tl, ml)

            main_cont.grid_columnconfigure(0, weight=1); main_cont.grid_columnconfigure(1, weight=1)
            for k in u.keys(): keyboard.add_hotkey(k, lambda x=k: p(x) if u[x][0].strip() else None, suppress=False)
            
            def auto_update():
                if ov_root and ov_root.winfo_exists():
                    up()
                    ov_root.after(1000, auto_update)
            auto_update(); ov_root.mainloop()

        def up():
            now = datetime.datetime.now()
            rez_cools = []
            for rk in ['f1', 'f2', 'f3', 'f4']:
                if not u[rk][0].strip(): continue
                card, nl, tl = ov_elements[rk]
                if not rezzer_alive[rk]:
                    card.config(highlightbackground="red", highlightthickness=2); tl.config(text="DEAD", fg="red")
                else:
                    card.config(highlightthickness=0); nl.config(fg="white")
                    if nt_times[rk] and nt_times[rk] > now:
                        tl.config(text=nt_times[rk].strftime('%H:%M'), fg="#ff5252"); rez_cools.append(nt_times[rk])
                    else:
                        tl.config(text="READY", fg="#4caf50"); rez_cools.append(now)
            
            min_rez_ready = min(rez_cools) if rez_cools else None
            guest_times = []
            for k in ['f5', 'f6']:
                if not u[k][0].strip(): continue
                card, nl, tl, ml = ov_elements[k]
                if nt_times[k] and now < nt_times[k]:
                    tl.config(text=nt_times[k].strftime('%H:%M'), fg="#ff5252")
                    guest_times.append((k, nt_times[k]))
                    if min_rez_ready is None: ml.config(text="⚠️ 리저 부재", fg="#ff1744")
                    else:
                        margin = (nt_times[k]-now).total_seconds() - (min_rez_ready-now).total_seconds()
                        if margin < 0: ml.config(text="⚠️ 부활 불가", fg="#ff1744")
                        else: ml.config(text=f"여유: {int(margin//60)}분", fg="#ffab00")
                else:
                    tl.config(text="READY", fg="#4caf50"); ml.config(text=""); beep_flags[k] = False

            if guest_times:
                guest_times.sort(key=lambda x: x[1])
                diff = (guest_times[0][1] - now).total_seconds()
                if 58 <= diff <= 61 and not beep_flags[guest_times[0][0]]:
                    winsound.Beep(1000, 500); beep_flags[guest_times[0][0]] = True
            
            if ov_root: ov_elements['now'].config(text=f"🕒 {now.strftime('%H:%M:%S')}") # 테스트용은 초단위 표시

        def p(k):
            now = datetime.datetime.now()
            if k in ['f1', 'f2', 'f3', 'f4']:
                if nt_times[k] and now < nt_times[k]: return
                if not rezzer_alive[k]: return
                nt_times[k] = now + datetime.timedelta(minutes=u[k][1])
                for gk in ['f5', 'f6']: nt_times[gk] = None
            else:
                nt_times[k] = now + datetime.timedelta(minutes=u[k][1])
            up()

        create_overlay()
    except Exception as e: messagebox.showerror("Error", str(e)); os._exit(1)

def ui():
    root = tk.Tk(); root.title("Skill Timer TEST"); root.geometry("360x640"); root.configure(bg="#f8f9fa")
    root.eval('tk::PlaceWindow . center')
    c = load()
    tk.Label(root, text="TEST MODE SETUP", font=("Malgun Gothic", 18, "bold"), bg="#f8f9fa", fg="#d32f2f").pack(pady=30)
    container = tk.Frame(root, bg="#f8f9fa"); container.pack(padx=30, fill="x")
    def create_row(parent, txt, d_val):
        row = tk.Frame(parent, bg="#f8f9fa"); row.pack(fill="x", pady=5)
        tk.Label(row, text=txt, width=10, bg="#f8f9fa").pack(side=tk.LEFT)
        e = tk.Entry(row, bd=1, relief="solid"); e.insert(0, d_val); e.pack(side=tk.LEFT, expand=True, fill="x", padx=10)
        return e
    ents = [create_row(container, f"M {i+1}", c["n"][i]) for i in range(4)]
    s_ents = [create_row(container, f"G {i+1}", c["s"][i]) for i in range(2)]
    tk.Button(root, text="START TEST", command=lambda: [save([e.get() for e in ents], [e.get() for e in s_ents]), root.destroy(), start_logic([e.get() for e in ents], [e.get() for e in s_ents])], bg="#d32f2f", fg="white", font=("Malgun Gothic", 12, "bold"), pady=15).pack(pady=40, padx=30, fill="x")
    root.mainloop()

if __name__ == "__main__": ui()
