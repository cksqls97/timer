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
beep_flags = {'f5': False, 'f6': False} # 중복 알림 방지용

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
    try:
        u = {
            'f1': [names[0], 30], 'f2': [names[1], 30], 'f3': [names[2], 30], 'f4': [names[3], 30],
            'f5': [specs[0], 13], 'f6': [specs[1] if specs[1].strip() else "", 13]
        }
        nt_times = {k: None for k in u.keys()}

        def go_to_setup():
            keyboard.unhook_all()
            ov_root.destroy()
            ui()

        def create_overlay():
            global ov_root, ov_elements
            ov_root = tk.Tk()
            ov_root.attributes("-topmost", True); ov_root.overrideredirect(True)
            ov_root.configure(bg="#121212")
            
            # 아래쪽이 잘리지 않도록 높이를 320 -> 360으로 상향 조정
            w, h = 360, 360
            sx, sy = ov_root.winfo_screenwidth() - w - 20, ov_root.winfo_screenheight() - h - 180
            ov_root.geometry(f"{w}x{h}+{sx}+{sy}")
            
            def sm(e): ov_root.x, ov_root.y = e.x, e.y
            def dm(e): ov_root.geometry(f"+{ov_root.winfo_x()+(e.x-ov_root.x)}+{ov_root.winfo_y()+(e.y-ov_root.y)}")
            ov_root.bind("<Button-1>", sm); ov_root.bind("<B1-Motion>", dm)

            header = tk.Frame(ov_root, bg="#3d5afe", height=45)
            header.pack(fill="x")
            ov_elements['now'] = tk.Label(header, text="READY", fg="white", bg="#3d5afe", font=("Malgun Gothic", 11, "bold"))
            ov_elements['now'].pack(side=tk.LEFT, padx=15, pady=8)

            btn_exit = tk.Button(header, text="✕", bg="#3d5afe", fg="white", bd=0, font=("Arial", 12, "bold"), 
                                 activebackground="#ff1744", command=lambda: os._exit(0))
            btn_exit.pack(side=tk.RIGHT, padx=5)
            btn_setup = tk.Button(header, text="⚙", bg="#3d5afe", fg="white", bd=0, font=("Arial", 14), 
                                  activebackground="#7986cb", command=go_to_setup)
            btn_setup.pack(side=tk.RIGHT, padx=5)

            main_cont = tk.Frame(ov_root, bg="#121212", padx=15, pady=10)
            main_cont.pack(fill="both", expand=True)

            def create_card(parent, title_color):
                card = tk.Frame(parent, bg="#262626", bd=2, relief="ridge", padx=10, pady=10) # 패딩 증가
                name_lbl = tk.Label(card, text="-", fg="white", bg="#262626", font=("Malgun Gothic", 10, "bold"))
                time_lbl = tk.Label(card, text="READY", fg=title_color, bg="#262626", font=("Malgun Gothic", 9))
                name_lbl.pack(); time_lbl.pack()
                return card, name_lbl, time_lbl

            tk.Label(main_cont, text="RESURRECTION (F1-F4)", fg="#BB86FC", bg="#121212", font=("Malgun Gothic", 9, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,8))
            for i, k in enumerate(['f1', 'f2', 'f3', 'f4']):
                card, nl, tl = create_card(main_cont, "#BB86FC")
                card.grid(row=(i//2)+1, column=i%2, padx=5, pady=5, sticky="nsew")
                ov_elements[k] = (nl, tl)

            tk.Label(main_cont, text="GUEST (F5-F6)", fg="#03DAC6", bg="#121212", font=("Malgun Gothic", 9, "bold")).grid(row=3, column=0, columnspan=2, sticky="w", pady=(12,8))
            for i, k in enumerate(['f5', 'f6']):
                card, nl, tl = create_card(main_cont, "#03DAC6")
                card.grid(row=4, column=i, padx=5, pady=5, sticky="nsew")
                ov_elements[k] = (nl, tl)

            main_cont.grid_columnconfigure(0, weight=1); main_cont.grid_columnconfigure(1, weight=1)

            for k in u.keys():
                keyboard.add_hotkey(k, lambda x=k: p(x) if u[x][0].strip() else None, suppress=False)
            
            # 실시간 업데이트 루프 (알림음 체크 포함)
            def auto_update():
                if ov_root and ov_root.winfo_exists():
                    up()
                    ov_root.after(1000, auto_update)
            
            auto_update()
            ov_root.mainloop()

        def up():
            now = datetime.datetime.now()
            cur_time_clip = now.strftime('%H%M')
            o_clip, s_clip = [], []
            
            # 손님 알림음 조건용 리스트
            guest_times = []

            for k in u.keys():
                nm = u[k][0].strip()
                if not nm: continue
                nl, tl = ov_elements[k]
                nl.config(text=nm)
                
                if nt_times[k] and now < nt_times[k]:
                    diff = (nt_times[k] - now).total_seconds()
                    tl.config(text=nt_times[k].strftime('%H:%M'), fg="#ff5252")
                    target = o_clip if k in ['f1', 'f2', 'f3', 'f4'] else s_clip
                    target.append(f"{nm} {nt_times[k].strftime('%M')}")
                    
                    if k in ['f5', 'f6']:
                        guest_times.append((k, nt_times[k]))
                else:
                    tl.config(text="READY", fg="#4caf50")
                    target = o_clip if k in ['f1', 'f2', 'f3', 'f4'] else s_clip
                    target.append(nm)
                    if k in ['f5', 'f6']: beep_flags[k] = False

            # 알림음 로직: 입력이 더 빨랐던(남은 시간이 더 적은) 손님 우선
            if guest_times:
                guest_times.sort(key=lambda x: x[1]) # 시간순 정렬
                first_k, first_time = guest_times[0]
                diff = (first_time - now).total_seconds()
                # 1분(60초) 전이고 아직 알림을 울리지 않은 경우
                if 58 <= diff <= 61 and not beep_flags[first_k]:
                    winsound.Beep(1000, 500) # 1000Hz로 0.5초간 비프음
                    beep_flags[first_k] = True

            pyperclip.copy(f"현재시간 {cur_time_clip} / {' '.join(o_clip)} / {' '.join(s_clip)}")
            if ov_root: ov_elements['now'].config(text=f"🕒 {now.strftime('%H:%M')}")

        def p(k):
            now = datetime.datetime.now()
            if k in ['f1', 'f2', 'f3', 'f4'] and nt_times[k] and now < nt_times[k]:
                custom_notify("Cooldown", f"{u[k][0]}: On cooldown!", "#d32f2f")
                return
            nt_times[k] = now + datetime.timedelta(minutes=u[k][1])
            if k in ['f5', 'f6']: beep_flags[k] = False # 타이머 갱신 시 플래그 초기화
            up()
            custom_notify("Timer Update", f"{u[k][0]} ({nt_times[k].strftime('%H:%M')})", "#2e7d32")

        create_overlay()
    except Exception as e:
        messagebox.showerror("Error", str(e)); os._exit(1)

def ui():
    root = tk.Tk(); root.title("Skill Timer"); root.geometry("360x620"); root.configure(bg="#f8f9fa")
    root.eval('tk::PlaceWindow . center')
    
    c = load()
    # 여백 조절 및 폰트 개선
    tk.Label(root, text="TIMER SETUP", font=("Malgun Gothic", 18, "bold"), bg="#f8f9fa", fg="#333").pack(pady=(30, 20))
    
    container = tk.Frame(root, bg="#f8f9fa")
    container.pack(padx=30, fill="x")

    def create_input_row(parent, label_text, default_val):
        row = tk.Frame(parent, bg="#f8f9fa")
        row.pack(fill="x", pady=6)
        tk.Label(row, text=label_text, width=10, anchor="w", bg="#f8f9fa", font=("Malgun Gothic", 10)).pack(side=tk.LEFT)
        e = tk.Entry(row, bd=1, relief="solid", font=("Malgun Gothic", 10), highlightthickness=1, highlightcolor="#6200EE")
        e.insert(0, default_val)
        e.pack(side=tk.LEFT, expand=True, fill="x", padx=(10, 0))
        return e

    ents = []
    tk.Label(container, text="[ Resurrection Members ]", bg="#f8f9fa", fg="#6200EE", font=("Malgun Gothic", 9, "bold")).pack(anchor="w", pady=(10, 5))
    for i in range(4):
        ents.append(create_input_row(container, f"Member {i+1}", c["n"][i]))
        
    tk.Frame(container, height=1, bg="#dee2e6").pack(fill="x", pady=20)
    
    s_ents = []
    tk.Label(container, text="[ Guest Members ]", bg="#f8f9fa", fg="#03DAC6", font=("Malgun Gothic", 9, "bold")).pack(anchor="w", pady=(0, 5))
    for i in range(2):
        s_ents.append(create_input_row(container, f"Guest {i+1}", c["s"][i]))
    
    def go():
        n, s = [e.get() for e in ents], [e.get() for e in s_ents]
        save(n, s); root.destroy(); start_logic(n, s)
    
    tk.Button(root, text="START TIMER", command=go, bg="#6200EE", fg="white", font=("Malgun Gothic", 12, "bold"), 
              pady=15, relief="flat", cursor="hand2").pack(pady=40, padx=30, fill="x")
    root.mainloop()

if __name__ == "__main__": 
    ui()
