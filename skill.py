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
            
            w, h = 360, 400 # 마지노선 표시를 위해 높이 약간 추가
            sx, sy = ov_root.winfo_screenwidth() - w - 20, ov_root.winfo_screenheight() - h - 180
            ov_root.geometry(f"{w}x{h}+{sx}+{sy}")
            
            def sm(e): ov_root.x, ov_root.y = e.x, e.y
            def dm(e): ov_root.geometry(f"+{ov_root.winfo_x()+(e.x-ov_root.x)}+{ov_root.winfo_y()+(e.y-ov_root.y)}")
            ov_root.bind("<Button-1>", sm); ov_root.bind("<B1-Motion>", dm)

            header = tk.Frame(ov_root, bg="#3d5afe", height=45); header.pack(fill="x")
            ov_elements['now'] = tk.Label(header, text="READY", fg="white", bg="#3d5afe", font=("Malgun Gothic", 11, "bold"))
            ov_elements['now'].pack(side=tk.LEFT, padx=15, pady=8)

            tk.Button(header, text="✕", bg="#3d5afe", fg="white", bd=0, font=("Arial", 12, "bold"), command=lambda: os._exit(0)).pack(side=tk.RIGHT, padx=5)
            tk.Button(header, text="⚙", bg="#3d5afe", fg="white", bd=0, font=("Arial", 14), command=go_to_setup).pack(side=tk.RIGHT, padx=5)

            main_cont = tk.Frame(ov_root, bg="#121212", padx=15, pady=10); main_cont.pack(fill="both", expand=True)

            def create_card(parent, title_color, is_guest=False):
                card = tk.Frame(parent, bg="#262626", bd=2, relief="ridge", padx=10, pady=8)
                name_lbl = tk.Label(card, text="-", fg="white", bg="#262626", font=("Malgun Gothic", 10, "bold"))
                time_lbl = tk.Label(card, text="READY", fg=title_color, bg="#262626", font=("Malgun Gothic", 9))
                name_lbl.pack(); time_lbl.pack()
                
                margin_lbl = None
                if is_guest:
                    margin_lbl = tk.Label(card, text="", fg="#ffab00", bg="#262626", font=("Malgun Gothic", 8, "italic"))
                    margin_lbl.pack()
                
                return card, name_lbl, time_lbl, margin_lbl

            # 리저 섹션
            tk.Label(main_cont, text="RESURRECTION (F1-F4)", fg="#BB86FC", bg="#121212", font=("Malgun Gothic", 9, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,8))
            for i, k in enumerate(['f1', 'f2', 'f3', 'f4']):
                card, nl, tl, _ = create_card(main_cont, "#BB86FC")
                card.grid(row=(i//2)+1, column=i%2, padx=5, pady=5, sticky="nsew")
                ov_elements[k] = (nl, tl)

            # 손님 섹션
            tk.Label(main_cont, text="GUEST (F5-F6)", fg="#03DAC6", bg="#121212", font=("Malgun Gothic", 9, "bold")).grid(row=3, column=0, columnspan=2, sticky="w", pady=(12,8))
            for i, k in enumerate(['f5', 'f6']):
                card, nl, tl, ml = create_card(main_cont, "#03DAC6", is_guest=True)
                card.grid(row=4, column=i, padx=5, pady=5, sticky="nsew")
                ov_elements[k] = (nl, tl, ml)

            main_cont.grid_columnconfigure(0, weight=1); main_cont.grid_columnconfigure(1, weight=1)

            for k in u.keys():
                keyboard.add_hotkey(k, lambda x=k: p(x) if u[x][0].strip() else None, suppress=False)
            
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
            
            # 리저들의 남은 쿨타임 중 가장 빠른 시간 찾기
            rez_cools = []
            for rk in ['f1', 'f2', 'f3', 'f4']:
                if nt_times[rk] and nt_times[rk] > now:
                    rez_cools.append(nt_times[rk])
                elif u[rk][0].strip(): # 이름은 있는데 쿨타임이 없으면 즉시 가능
                    rez_cools.append(now)
            
            min_rez_ready = min(rez_cools) if rez_cools else now

            guest_times = []
            for k in u.keys():
                nm = u[k][0].strip()
                if not nm: continue
                
                if k in ['f5', 'f6']:
                    nl, tl, ml = ov_elements[k]
                    if nt_times[k] and now < nt_times[k]:
                        tl.config(text=nt_times[k].strftime('%H:%M'), fg="#ff5252")
                        s_clip.append(f"{nm} {nt_times[k].strftime('%M')}")
                        guest_times.append((k, nt_times[k]))
                        
                        # 마지노선 로직: (손님 부활제한 시간) - (가장 빠른 리저가 돌아오는 시간)
                        # 손님 제한시간은 u[k][1]분(13분)으로 설정되어 있음
                        time_to_death = (nt_times[k] - now).total_seconds()
                        time_to_rez = (min_rez_ready - now).total_seconds()
                        
                        margin = time_to_death - time_to_rez
                        if margin < 0:
                            ml.config(text="⚠️ 부활 불가", fg="#ff1744")
                        else:
                            mins = int(margin // 60)
                            ml.config(text=f"여유: {mins}분", fg="#ffab00")
                    else:
                        tl.config(text="READY", fg="#4caf50")
                        ml.config(text="")
                        s_clip.append(nm); beep_flags[k] = False
                else:
                    nl, tl = ov_elements[k]
                    if nt_times[k] and now < nt_times[k]:
                        tl.config(text=nt_times[k].strftime('%H:%M'), fg="#ff5252")
                        o_clip.append(f"{nm} {nt_times[k].strftime('%M')}")
                    else:
                        tl.config(text="READY", fg="#4caf50")
                        o_clip.append(nm)

            # 알림음 로직 (생략 없음)
            if guest_times:
                guest_times.sort(key=lambda x: x[1])
                first_k, first_time = guest_times[0]
                diff = (first_time - now).total_seconds()
                if 58 <= diff <= 61 and not beep_flags[first_k]:
                    winsound.Beep(1000, 500); beep_flags[first_k] = True

            pyperclip.copy(f"현재시간 {cur_time_clip} / {' '.join(o_clip)} / {' '.join(s_clip)}")
            if ov_root: ov_elements['now'].config(text=f"🕒 {now.strftime('%H:%M')}")

        def p(k):
            now = datetime.datetime.now()
            if k in ['f1', 'f2', 'f3', 'f4'] and nt_times[k] and now < nt_times[k]:
                custom_notify("Cooldown", f"{u[k][0]}: On cooldown!", "#d32f2f")
                return
            nt_times[k] = now + datetime.timedelta(minutes=u[k][1])
            if k in ['f5', 'f6']: beep_flags[k] = False
            up()
            custom_notify("Timer Update", f"{u[k][0]} ({nt_times[k].strftime('%H:%M')})", "#2e7d32")

        create_overlay()
    except Exception as e:
        messagebox.showerror("Error", str(e)); os._exit(1)

def ui():
    root = tk.Tk(); root.title("Skill Timer"); root.geometry("360x640"); root.configure(bg="#f8f9fa")
    root.eval('tk::PlaceWindow . center')
    c = load()
    tk.Label(root, text="TIMER SETUP", font=("Malgun Gothic", 18, "bold"), bg="#f8f9fa", fg="#333").pack(pady=(30, 20))
    container = tk.Frame(root, bg="#f8f9fa"); container.pack(padx=30, fill="x")
    def create_row(parent, txt, d_val):
        row = tk.Frame(parent, bg="#f8f9fa"); row.pack(fill="x", pady=6)
        tk.Label(row, text=txt, width=10, anchor="w", bg="#f8f9fa", font=("Malgun Gothic", 10)).pack(side=tk.LEFT)
        e = tk.Entry(row, bd=1, relief="solid", font=("Malgun Gothic", 10)); e.insert(0, d_val); e.pack(side=tk.LEFT, expand=True, fill="x", padx=(10, 0))
        return e
    ents = []
    tk.Label(container, text="[ Resurrection Members ]", bg="#f8f9fa", fg="#6200EE", font=("Malgun Gothic", 9, "bold")).pack(anchor="w", pady=(10, 5))
    for i in range(4): ents.append(create_row(container, f"Member {i+1}", c["n"][i]))
    tk.Frame(container, height=1, bg="#dee2e6").pack(fill="x", pady=20)
    s_ents = []
    tk.Label(container, text="[ Guest Members ]", bg="#f8f9fa", fg="#03DAC6", font=("Malgun Gothic", 9, "bold")).pack(anchor="w", pady=(0, 5))
    for i in range(2): s_ents.append(create_row(container, f"Guest {i+1}", c["s"][i]))
    def go():
        n, s = [e.get() for e in ents], [e.get() for e in s_ents]
        save(n, s); root.destroy(); start_logic(n, s)
    tk.Button(root, text="START TIMER", command=go, bg="#6200EE", fg="white", font=("Malgun Gothic", 12, "bold"), pady=15).pack(pady=40, padx=30, fill="x")
    root.mainloop()

if __name__ == "__main__": ui()
