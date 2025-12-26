import keyboard, pyperclip, datetime, tkinter as tk, json, os, threading, sys
from tkinter import messagebox
import time

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
            '1': [names[0], 30], '2': [names[1], 30], '3': [names[2], 30], '4': [names[3], 30],
            '7': [specs[0], 13], '8': [specs[1] if specs[1].strip() else "", 13]
        }
        nt_times = {k: None for k in u.keys()}

        def create_overlay():
            global ov_root, ov_elements
            ov_root = tk.Tk()
            ov_root.attributes("-topmost", True); ov_root.overrideredirect(True)
            ov_root.configure(bg="#121212")
            
            def sm(e): ov_root.x, ov_root.y = e.x, e.y
            def dm(e): ov_root.geometry(f"+{ov_root.winfo_x()+(e.x-ov_root.x)}+{ov_root.winfo_y()+(e.y-ov_root.y)}")
            ov_root.bind("<Button-1>", sm); ov_root.bind("<B1-Motion>", dm)

            header = tk.Frame(ov_root, bg="#3d5afe"); header.pack(fill="x")
            ov_elements['now'] = tk.Label(header, text="READY", fg="white", bg="#3d5afe", font=("Malgun Gothic", 10, "bold"))
            ov_elements['now'].pack(pady=5)

            main_cont = tk.Frame(ov_root, bg="#121212", padx=10, pady=10); main_cont.pack()

            def create_card(parent, title_color):
                card = tk.Frame(parent, bg="#262626", bd=1, relief="ridge", padx=5, pady=5)
                name_lbl = tk.Label(card, text="-", fg="white", bg="#262626", font=("Malgun Gothic", 9, "bold"))
                time_lbl = tk.Label(card, text="READY", fg=title_color, bg="#262626", font=("Malgun Gothic", 8))
                name_lbl.pack(); time_lbl.pack()
                return card, name_lbl, time_lbl

            for i, k in enumerate(['1', '2', '3', '4']):
                card, nl, tl = create_card(main_cont, "#BB86FC")
                card.grid(row=(i//2)+1, column=i%2, padx=3, pady=3, sticky="nsew")
                ov_elements[k] = (nl, tl)

            for i, k in enumerate(['7', '8']):
                card, nl, tl = create_card(main_cont, "#03DAC6")
                card.grid(row=4, column=i, padx=3, pady=3, sticky="nsew")
                ov_elements[k] = (nl, tl)

            # --- 보안 강화형 키 모니터링 (후킹X, 폴링O) ---
            def key_monitor():
                # 97=Num1, 98=Num2, 99=Num3, 100=Num4, 103=Num7, 104=Num8
                key_map = {97: '1', 98: '2', 99: '3', 100: '4', 103: '7', 104: '8'}
                pressed_state = {k: False for k in key_map.keys()}
                
                while True:
                    # 프로그램이 종료되면 쓰레드도 종료
                    if not ov_root or not tk.Toplevel.winfo_exists(ov_root): break
                    
                    for vk, k_id in key_map.items():
                        if keyboard.is_pressed(vk):
                            if not pressed_state[vk]: # 처음 눌린 순간만 실행
                                if u[k_id][0].strip():
                                    ov_root.after(0, lambda x=k_id: p(x))
                                pressed_state[vk] = True
                        else:
                            pressed_state[vk] = False
                    
                    # 종료 단축키 체크 (Ctrl + Alt + Num1)
                    if keyboard.is_pressed('ctrl') and keyboard.is_pressed('alt') and keyboard.is_pressed(97):
                        os._exit(0)
                        
                    time.sleep(0.05) # CPU 점유율 방지

            threading.Thread(target=key_monitor, daemon=True).start()
            
            up()
            ov_root.mainloop()

        def up():
            now = datetime.datetime.now()
            cur_time_clip = now.strftime('%H%M')
            o_clip, s_clip = [], []
            for k in u.keys():
                nm = u[k][0].strip()
                if not nm: continue
                nl, tl = ov_elements[k]
                nl.config(text=nm)
                if nt_times[k] and now < nt_times[k]:
                    tl.config(text=nt_times[k].strftime('%H:%M'), fg="#ff5252")
                    target = o_clip if k in '1234' else s_clip
                    target.append(f"{nm} {nt_times[k].strftime('%M')}")
                else:
                    tl.config(text="READY", fg="#4caf50")
                    target = o_clip if k in '1234' else s_clip
                    target.append(nm)
            pyperclip.copy(f"현재시간 {cur_time_clip} / {' '.join(o_clip)} / {' '.join(s_clip)}")
            if ov_root: ov_elements['now'].config(text=f"🕒 {now.strftime('%H:%M')}")

        def p(k):
            now = datetime.datetime.now()
            if k in '1234' and nt_times[k] and now < nt_times[k]:
                custom_notify("Cooldown", f"{u[k][0]}: On cooldown!", "#d32f2f")
                return
            nt_times[k] = now + datetime.timedelta(minutes=u[k][1])
            up()
            custom_notify("Timer Update", f"{u[k][0]} ({nt_times[k].strftime('%H:%M')})", "#2e7d32")

        create_overlay()
    except Exception as e:
        messagebox.showerror("Error", str(e)); os._exit(1)

def ui():
    root = tk.Tk(); root.title("Skill Timer"); root.geometry("320x550"); root.configure(bg="#f8f9fa")
    c = load()
    tk.Label(root, text="TIMER SETUP", font=("Malgun Gothic", 16, "bold"), bg="#f8f9fa").pack(pady=20)
    ents, s_ents = [], []
    for i in range(4):
        f = tk.Frame(root, bg="#f8f9fa"); f.pack(pady=4, padx=25, fill="x")
        tk.Label(f, text=f"리저 {i+1}", width=8, bg="#f8f9fa").pack(side=tk.LEFT)
        e = tk.Entry(f, bd=1, relief="solid"); e.insert(0, c["n"][i]); e.pack(side=tk.LEFT, expand=True, fill="x", padx=10); ents.append(e)
    for i in range(2):
        f = tk.Frame(root, bg="#f8f9fa"); f.pack(pady=4, padx=25, fill="x")
        tk.Label(f, text=f"손님 {i+1}", width=8, bg="#f8f9fa").pack(side=tk.LEFT)
        e = tk.Entry(f, bd=1, relief="solid"); e.insert(0, c["s"][i]); e.pack(side=tk.LEFT, expand=True, fill="x", padx=10); s_ents.append(e)
    def go():
        n, s = [e.get() for e in ents], [e.get() for e in s_ents]
        save(n, s); root.destroy(); start_logic(n, s)
    tk.Button(root, text="START TIMER", command=go, bg="#6200EE", fg="white", font=("Malgun Gothic", 11, "bold"), pady=12).pack(pady=30, padx=25, fill="x")
    root.mainloop()

if __name__ == "__main__": ui()
