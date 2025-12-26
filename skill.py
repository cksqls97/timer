import keyboard, pyperclip, datetime, tkinter as tk, json, os, threading, sys
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
ov_labels = {}

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
        u = {'1':[names[0],30],'2':[names[1],30],'3':[names[2],30],'4':[names[3],30],'7':[specs[0],13],'8':[specs[1] if specs[1].strip() else "",13]}
        nt_times = {k: None for k in u.keys()}

        def create_overlay():
            global ov_root, ov_labels
            ov_root = tk.Tk()
            ov_root.title("Overlay")
            ov_root.attributes("-topmost", True); ov_root.overrideredirect(True)
            w, h = 300, 240
            sx, sy = ov_root.winfo_screenwidth()-w-20, ov_root.winfo_screenheight()-h-140
            ov_root.geometry(f"{w}x{h}+{sx}+{sy}"); ov_root.configure(bg="#121212")
            
            def sm(e): ov_root.x, ov_root.y = e.x, e.y
            def dm(e): ov_root.geometry(f"+{ov_root.winfo_x()+(e.x-ov_root.x)}+{ov_root.winfo_y()+(e.y-ov_root.y)}")
            ov_root.bind("<Button-1>", sm); ov_root.bind("<B1-Motion>", dm)

            header = tk.Frame(ov_root, bg="#3700B3", height=35); header.pack(fill="x")
            ov_labels['now'] = tk.Label(header, text="READY", fg="white", bg="#3700B3", font=("Malgun Gothic", 10, "bold"))
            ov_labels['now'].pack(pady=5)

            container = tk.Frame(ov_root, bg="#121212", padx=10, pady=10); container.pack(fill="both", expand=True)
            rez_box = tk.LabelFrame(container, text=" RESURRECTION ", fg="#BB86FC", bg="#121212", font=("Malgun Gothic", 8, "bold"), padx=8, pady=8, relief="solid", bd=1)
            rez_box.pack(fill="x", pady=(0, 10))
            ov_labels['rez'] = tk.Label(rez_box, text="-", fg="white", bg="#121212", font=("Malgun Gothic", 9), justify=tk.LEFT, anchor="nw", wraplength=250)
            ov_labels['rez'].pack(fill="x")
            gst_box = tk.LabelFrame(container, text=" GUEST ", fg="#03DAC6", bg="#121212", font=("Malgun Gothic", 8, "bold"), padx=8, pady=8, relief="solid", bd=1)
            gst_box.pack(fill="x")
            ov_labels['gst'] = tk.Label(gst_box, text="-", fg="white", bg="#121212", font=("Malgun Gothic", 9), justify=tk.LEFT, anchor="nw", wraplength=250)
            ov_labels['gst'].pack(fill="x")
            
            # 핫키 등록 (오버레이 루프 안에서 수행)
            for k in u.keys():
                keyboard.add_hotkey(f'num {k}', lambda x=k: p(x) if u[x][0].strip() else None, suppress=False)
            
            keyboard.add_hotkey('ctrl+alt+num 1', lambda: os._exit(0))
            
            ov_root.mainloop()

        def up():
            now = datetime.datetime.now()
            cur_time = now.strftime('%H%M')
            o_clip, s_clip, o_ov, s_ov = [], [], [], []
            for i in '1234':
                nm = u[i][0].strip()
                if nm:
                    if nt_times[i] and now < nt_times[i]:
                        o_clip.append(f"{nm} {nt_times[i].strftime('%M')}")
                        o_ov.append(f"• {nm}: {nt_times[i].strftime('%H:%M')}")
                    else: o_clip.append(nm); o_ov.append(f"• {nm}")
            for i in '78':
                nm = u[i][0].strip()
                if nm:
                    if nt_times[i] and now < nt_times[i]:
                        s_clip.append(f"{nm} {nt_times[i].strftime('%M')}")
                        s_ov.append(f"• {nm}: {nt_times[i].strftime('%H:%M')}")
                    else: s_clip.append(nm); s_ov.append(f"• {nm}")

            pyperclip.copy(f"현재시간 {cur_time} / {' '.join(o_clip)} / {' '.join(s_clip)}")
            if ov_root:
                ov_labels['now'].config(text=f"🕒 CURRENT: {now.strftime('%H:%M')}")
                ov_labels['rez'].config(text='\n'.join(o_ov) if o_ov else "No Data")
                ov_labels['gst'].config(text='\n'.join(s_ov) if s_ov else "No Data")

        def p(k):
            now = datetime.datetime.now()
            nm = u[k][0]
            if k in '1234' and nt_times[k] and now < nt_times[k]:
                custom_notify("Cooldown", f"{nm}: Still on cooldown!", "#d32f2f")
                return
            nt_times[k] = now + datetime.timedelta(minutes=u[k][1])
            up()
            custom_notify("Timer Update", f"{nm} ({nt_times[k].strftime('%H:%M')})", "#2e7d32")

        create_overlay()
    except Exception as e:
        messagebox.showerror("Error", f"오류 발생: {str(e)}")
        os._exit(1)

def ui():
    root = tk.Tk()
    root.title("Skill Timer")
    root.geometry("320x550"); root.configure(bg="#f8f9fa")
    
    config_data = load()
    tk.Label(root, text="TIMER SETUP", font=("Malgun Gothic", 16, "bold"), bg="#f8f9fa", fg="#333").pack(pady=20)
    ents, s_ents = [], []
    for i in range(4):
        f = tk.Frame(root, bg="#f8f9fa"); f.pack(pady=4, padx=25, fill="x")
        tk.Label(f, text=f"리저 {i+1}", width=8, anchor="w", bg="#f8f9fa").pack(side=tk.LEFT)
        e = tk.Entry(f, bd=1, relief="solid"); e.insert(0, config_data["n"][i]); e.pack(side=tk.LEFT, expand=True, fill="x", padx=10); ents.append(e)
    tk.Frame(root, height=1, bg="#dee2e6").pack(fill="x", padx=25, pady=15)
    for i in range(2):
        f = tk.Frame(root, bg="#f8f9fa"); f.pack(pady=4, padx=25, fill="x")
        tk.Label(f, text=f"손님 {i+1}", width=8, anchor="w", bg="#f8f9fa").pack(side=tk.LEFT)
        e = tk.Entry(f, bd=1, relief="solid"); e.insert(0, config_data["s"][i]); e.pack(side=tk.LEFT, expand=True, fill="x", padx=10); s_ents.append(e)

    def go():
        n, s = [e.get() for e in ents], [e.get() for e in s_ents]
        save(n, s); root.destroy()
        # 프로세스 종료 방지를 위해 메인 스레드에서 로직 실행
        start_logic(n, s)

    tk.Button(root, text="START TIMER", command=go, bg="#6200EE", fg="white", font=("Malgun Gothic", 11, "bold"), pady=12).pack(pady=30, padx=25, fill="x")
    root.mainloop()

if __name__ == "__main__":
    ui()
