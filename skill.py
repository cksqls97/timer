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
    return {"n": ["비숍1", "비숍2", "비숍3", "비숍4"], "s": ["손님1", "손님2"]}

ov_root = None
ov_elements = {}
beep_flags = {'f5': False, 'f6': False}
rezzer_alive = {'f1': True, 'f2': True, 'f3': True, 'f4': True}

def custom_notify(title, message, color="#333"):
    def run():
        nt = tk.Toplevel()
        nt.overrideredirect(True); nt.attributes("-topmost", True)
        nt.geometry(f"280x80+{nt.winfo_screenwidth()-300}+{nt.winfo_screenheight()-150}")
        nt.configure(bg=color)
        tk.Label(nt, text=title, fg="white", bg=color, font=("Malgun Gothic", 11, "bold")).pack(pady=(10, 0))
        tk.Label(nt, text=message, fg="white", bg=color, font=("Malgun Gothic", 10)).pack(pady=5)
        nt.after(2500, nt.destroy); nt.mainloop()
    threading.Thread(target=run, daemon=True).start()

def start_logic(names, specs):
    try:
        u = {'f1': [names[0], 30], 'f2': [names[1], 30], 'f3': [names[2], 30], 'f4': [names[3], 30],
             'f5': [specs[0], 13], 'f6': [specs[1] if specs[1].strip() else "", 13]}
        nt_times = {k: None for k in u.keys()}

        def go_to_setup():
            keyboard.unhook_all(); ov_root.destroy(); ui()

        def toggle_rezzer(k):
            rezzer_alive[k] = not rezzer_alive[k]
            up()

        def create_overlay():
            global ov_root, ov_elements
            ov_root = tk.Tk()
            ov_root.attributes("-topmost", True, "-alpha", 0.95); ov_root.overrideredirect(True)
            ov_root.configure(bg="#1A1A1A")
            
            # 가독성과 콤팩트함 사이의 최적화된 크기
            w, h = 380, 460 
            ov_root.geometry(f"{w}x{h}+{ov_root.winfo_screenwidth()-w-20}+{ov_root.winfo_screenheight()-h-100}")
            
            def sm(e): ov_root.x, ov_root.y = e.x, e.y
            def dm(e): ov_root.geometry(f"+{ov_root.winfo_x()+(e.x-ov_root.x)}+{ov_root.winfo_y()+(e.y-ov_root.y)}")
            ov_root.bind("<Button-1>", sm); ov_root.bind("<B1-Motion>", dm)

            header = tk.Frame(ov_root, bg="#2D2D2D", height=40); header.pack(fill="x")
            ov_elements['now'] = tk.Label(header, text="READY", fg="#00FF7F", bg="#2D2D2D", font=("Malgun Gothic", 12, "bold"))
            ov_elements['now'].pack(side=tk.LEFT, padx=15)
            tk.Button(header, text="✕", bg="#2D2D2D", fg="white", bd=0, font=("Arial", 12), command=lambda: os._exit(0)).pack(side=tk.RIGHT, padx=10)
            tk.Button(header, text="⚙", bg="#2D2D2D", fg="white", bd=0, font=("Arial", 12), command=go_to_setup).pack(side=tk.RIGHT)

            main_cont = tk.Frame(ov_root, bg="#1A1A1A", padx=10, pady=10); main_cont.pack(fill="both", expand=True)

            def create_card(parent, k, is_guest=False):
                card = tk.Frame(parent, bg="#2A2A2A", bd=1, relief="flat", padx=5, pady=8)
                nl = tk.Label(card, text="-", fg="#E0E0E0", bg="#2A2A2A", font=("Malgun Gothic", 12, "bold"))
                tl = tk.Label(card, text="READY", fg="#BB86FC" if not is_guest else "#03DAC6", bg="#2A2A2A", font=("Malgun Gothic", 11, "bold"))
                msg = tk.Label(card, text="", fg="#FF5252", bg="#2A2A2A", font=("Malgun Gothic", 9, "bold"))
                nl.pack(); tl.pack(); msg.pack()
                if not is_guest:
                    for widget in [card, nl, tl, msg]: widget.bind("<Button-3>", lambda e, x=k: toggle_rezzer(x))
                return card, nl, tl, msg

            # Resurrection 섹션 (F1-F4)
            tk.Label(main_cont, text="Resurrection Members", fg="#BB86FC", bg="#1A1A1A", font=("Malgun Gothic", 10, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,5))
            for i, k in enumerate(['f1', 'f2', 'f3', 'f4']):
                card, nl, tl, msg = create_card(main_cont, k)
                card.grid(row=(i//2)+1, column=i%2, padx=4, pady=4, sticky="nsew")
                ov_elements[k] = (card, nl, tl, msg)

            # Guest 섹션 (F5-F6)
            tk.Label(main_cont, text="Guest (13m Limit)", fg="#03DAC6", bg="#1A1A1A", font=("Malgun Gothic", 10, "bold")).grid(row=3, column=0, columnspan=2, sticky="w", pady=(15,5))
            for i, k in enumerate(['f5', 'f6']):
                card, nl, tl, msg = create_card(main_cont, k, is_guest=True)
                card.grid(row=4, column=i, padx=4, pady=4, sticky="nsew")
                ov_elements[k] = (card, nl, tl, msg)

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
            
            # 생존한 멤버들의 리저 가능 시간 리스트
            current_rez_states = []
            for rk in ['f1', 'f2', 'f3', 'f4']:
                if rezzer_alive[rk]:
                    if nt_times[rk] and nt_times[rk] > now: current_rez_states.append(nt_times[rk])
                    else: current_rez_states.append(now)
            
            # Resurrection 업데이트
            for idx, rk in enumerate(['f1', 'f2', 'f3', 'f4']):
                card, nl, tl, msg = ov_elements[rk]
                nl.config(text=u[rk][0])
                
                if not rezzer_alive[rk]:
                    card.config(highlightbackground="#FF1744", highlightthickness=2)
                    tl.config(text="DEATH", fg="#FF1744"); msg.config(text="")
                    continue
                
                card.config(highlightthickness=0)
                if nt_times[rk] and nt_times[rk] > now:
                    tl.config(text=nt_times[rk].strftime('%H:%M'), fg="#FF5252")
                    o_clip.append(f"{u[rk][0]} {nt_times[rk].strftime('%M')}")
                    msg.config(text="")
                else:
                    tl.config(text="READY", fg="#4CAF50")
                    o_clip.append(u[rk][0])
                    
                    # 로직 체크 (내가 썼을 때 파티의 공백 시뮬레이션)
                    if current_rez_states:
                        temp_states = list(current_rez_states)
                        # 현재 준비된 리스트에서 나를 '30분 뒤'로 보내고 최소값 찾기
                        try:
                            my_idx_in_states = temp_states.index(now)
                            temp_states[my_idx_in_states] = now + datetime.timedelta(minutes=30)
                        except ValueError: pass # 이미 쿨타임 중이면 무시
                        
                        next_avail = min(temp_states) if temp_states else now + datetime.timedelta(minutes=30)
                        if (next_avail - now).total_seconds() > 14 * 60:
                            msg.config(text="사용시 손님 부활 불가", fg="#FF5252")
                            card.config(highlightbackground="#FFD600", highlightthickness=1) # 노란색 경고 테두리
                        else:
                            msg.config(text=""); card.config(highlightthickness=0)

            # Guest 업데이트
            min_rez_ready = min(current_rez_states) if current_rez_states else now + datetime.timedelta(minutes=999)
            for k in ['f5', 'f6']:
                card, nl, tl, msg = ov_elements[k]
                nm = u[k][0].strip()
                if not nm: continue
                nl.config(text=nm)
                if nt_times[k] and now < nt_times[k]:
                    tl.config(text=nt_times[k].strftime('%H:%M'), fg="#FF5252")
                    s_clip.append(f"{nm} {nt_times[k].strftime('%M')}")
                    
                    margin_sec = (nt_times[k] - now).total_seconds() - (min_rez_ready - now).total_seconds()
                    if margin_sec < 0: 
                        msg.config(text="⚠️ 부활 불가", fg="#FF1744")
                    else: 
                        msg.config(text=f"{int(margin_sec // 60)}분 전", fg="#FFAB00")
                    
                    if 58 <= (nt_times[k] - now).total_seconds() <= 61 and not beep_flags[k]:
                        winsound.Beep(1000, 500); beep_flags[k] = True
                else:
                    tl.config(text="READY", fg="#4CAF50"); msg.config(text="")
                    s_clip.append(nm); beep_flags[k] = False

            pyperclip.copy(f"현재시간 {cur_time_clip} / {' '.join(o_clip)} / {' '.join(s_clip)}")
            if ov_root: ov_elements['now'].config(text=f"🕒 {now.strftime('%H:%M')}")

        def p(k):
            now = datetime.datetime.now()
            if k in ['f1', 'f2', 'f3', 'f4']:
                if not rezzer_alive[k]: return
                if nt_times[k] and now < nt_times[k]: return
                nt_times[k] = now + datetime.timedelta(minutes=30)
            else:
                nt_times[k] = now + datetime.timedelta(minutes=13)
                beep_flags[k] = False
            up()

        create_overlay()
    except Exception as e:
        messagebox.showerror("Error", str(e)); os._exit(1)

def ui():
    root = tk.Tk(); root.title("Setup"); root.geometry("400x650"); root.configure(bg="#F5F5F5")
    root.eval('tk::PlaceWindow . center')
    c = load()
    tk.Label(root, text="RAID TIMER SETUP", font=("Malgun Gothic", 18, "bold"), bg="#F5F5F5", fg="#333").pack(pady=20)
    container = tk.Frame(root, bg="#F5F5F5"); container.pack(padx=30, fill="x")
    
    def create_row(parent, txt, d_val):
        row = tk.Frame(parent, bg="#F5F5F5"); row.pack(fill="x", pady=6)
        tk.Label(row, text=txt, width=12, anchor="w", bg="#F5F5F5", font=("Malgun Gothic", 10)).pack(side=tk.LEFT)
        e = tk.Entry(row, bd=1, relief="solid", font=("Malgun Gothic", 10)); e.insert(0, d_val); e.pack(side=tk.LEFT, expand=True, fill="x", padx=(5, 0))
        return e

    ents = []
    tk.Label(container, text="Resurrection Members", bg="#F5F5F5", fg="#6200EE", font=("Malgun Gothic", 10, "bold")).pack(anchor="w", pady=(5, 5))
    for i in range(4): ents.append(create_row(container, f"Member {i+1}", c["n"][i]))
    tk.Label(container, text="Guest Members", bg="#F5F5F5", fg="#009688", font=("Malgun Gothic", 10, "bold")).pack(anchor="w", pady=(20, 5))
    s_ents = []
    for i in range(2): s_ents.append(create_row(container, f"Guest {i+1}", c["s"][i]))
    
    def go():
        n, s = [e.get() for e in ents], [e.get() for e in s_ents]
        save(n, s); root.destroy(); start_logic(n, s)
        
    tk.Button(root, text="START TIMER", command=go, bg="#6200EE", fg="white", font=("Malgun Gothic", 14, "bold"), pady=15).pack(pady=30, padx=30, fill="x")
    root.mainloop()

if __name__ == "__main__": ui()
