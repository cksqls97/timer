import keyboard, pyperclip, datetime, tkinter as tk, json, os, threading, sys

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

CFG, ICON_NAME = "timer_config.json", "icon.png"

def save(n, s):
    with open(CFG, "w", encoding="utf-8") as f: json.dump({"n": n, "s": s}, f, ensure_ascii=False)

def load():
    if os.path.exists(CFG) and os.path.getsize(CFG) > 0:
        try:
            with open(CFG, "r", encoding="utf-8") as f: return json.load(f)
        except: return None
    return None

status_label = None

def custom_notify(title, message, color="#333"):
    def run():
        nt = tk.Toplevel()
        nt.overrideredirect(True)
        nt.attributes("-topmost", True)
        w, h = 280, 80
        sx, sy = nt.winfo_screenwidth() - w - 20, nt.winfo_screenheight() - h - 50
        nt.geometry(f"{w}x{h}+{sx}+{sy}")
        nt.configure(bg=color)
        tk.Label(nt, text=title, fg="white", bg=color, font=("Malgun Gothic", 10, "bold")).pack(pady=(10, 0))
        tk.Label(nt, text=message, fg="white", bg=color, font=("Malgun Gothic", 9), wraplength=250).pack(pady=5)
        nt.after(3000, nt.destroy)
        nt.mainloop()
    threading.Thread(target=run, daemon=True).start()

def start(names, specs):
    u = {'1':[names[0],30],'2':[names[1],30],'3':[names[2],30],'4':[names[3],30],'7':[specs[0],13],'8':[specs[1] if specs[1].strip() else "",13]}
    nt_times = {k: None for k in u.keys()}

    def create_status_window():
        global status_label
        sw = tk.Tk()
        sw.attributes("-topmost", True)
        sw.overrideredirect(True)
        w, h = 280, 160
        sx, sy = sw.winfo_screenwidth()-w-20, sw.winfo_screenheight()-h-140
        sw.geometry(f"{w}x{h}+{sx}+{sy}")
        sw.configure(bg="#1a1a1a")
        def sm(e): sw.x, sw.y = e.x, e.y
        def dm(e): sw.geometry(f"+{sw.winfo_x()+(e.x-sw.x)}+{sw.winfo_y()+(e.y-sw.y)}")
        sw.bind("<Button-1>", sm); sw.bind("<B1-Motion>", dm)
        status_label = tk.Label(sw, text="Ready", fg="#00FF00", bg="#1a1a1a", font=("Malgun Gothic", 9, "bold"), justify=tk.LEFT, padx=15, pady=15, anchor="nw", wraplength=250)
        status_label.pack(fill="both", expand=True)
        sw.mainloop()

    def up():
        now = datetime.datetime.now()
        cur = now.strftime('%H%M')
        o, s_o = [], []
        for i in '1234':
            nm = u[i][0].strip()
            if nm:
                t = f": {nt_times[i].strftime('%H:%M')}" if nt_times[i] and now < nt_times[i] else ""
                o.append(f"{nm}{t}")
        for i in '78':
            nm = u[i][0].strip()
            if nm:
                t = f": {nt_times[i].strftime('%H:%M')}" if nt_times[i] and now < nt_times[i] else ""
                s_o.append(f"{nm}{t}")
        pyperclip.copy(f"현재시간: {cur} / {' '.join(o)} / {' '.join(s_o)}")
        if status_label:
            txt = f"🕒 현재시간: {cur}\n--------------------------\n✨ 리저: {' , '.join(o) if o else '-'}\n\n👤 손님: {' , '.join(s_o) if s_o else '-'}"
            status_label.config(text=txt)

    def p(k):
        now = datetime.datetime.now()
        nm = u[k][0]
        if k in '1234' and nt_times[k] and now < nt_times[k]:
            custom_notify("Cooldown", f"{nm}: Still on cooldown!", "#d32f2f")
            return
        nt_times[k] = now + datetime.timedelta(minutes=u[k][1])
        up()
        tm = nt_times[k].strftime('%H:%M')
        custom_notify("Timer Update", f"{nm} ({tm})", "#2e7d32")

    threading.Thread(target=create_status_window, daemon=True).start()
    for k in u.keys(): keyboard.add_hotkey(f'num {k}', lambda x=k: p(x) if u[x][0].strip() else None)
    keyboard.add_hotkey('ctrl+alt+num 1', lambda: os._exit(0))
    keyboard.wait()

def ui():
    root = tk.Tk()
    root.title("Skill Timer")
    root.geometry("320x600")
    root.configure(bg="#f8f9fa")
    ip = ICON_NAME if os.path.exists(ICON_NAME) else resource_path(ICON_NAME)
    try:
        img = tk.PhotoImage(file=ip)
        l_img = tk.Label(root, image=img, bg="#f8f9fa")
        l_img.image = img
        l_img.pack(pady=15)
    except:
        tk.Label(root, text="🛡️", font=("Arial", 40), bg="#f8f9fa", fg="#007bff").pack(pady=15)
    
    c = load() or {"n": ["","","",""], "s": ["",""]}
    tk.Label(root, text="Setting", font=("Malgun Gothic", 14, "bold"), bg="#f8f9fa").pack(pady=5)
    
    ents, s_ents = [], []
    for i in range(4):
        f = tk.Frame(root, bg="#f8f9fa"); f.pack(pady=4, padx=25, fill="x")
        tk.Label(f, text=f"Rez {i+1}", width=8, anchor="w", bg="#f8f9fa").pack(side=tk.LEFT)
        e = tk.Entry(f, bd=1, relief="solid"); e.insert(0, c["n"][i]); e.pack(side=tk.LEFT, expand=True, fill="x", padx=10); ents.append(e)
    tk.Frame(root, height=1, bg="#dee2e6").pack(fill="x", padx=25, pady=15)
    for i in range(2):
        f = tk.Frame(root, bg="#f8f9fa"); f.pack(pady=4, padx=25, fill="x")
        tk.Label(f, text=f"Guest {i+1}", width=8, anchor="w", bg="#f8f9fa").pack(side=tk.LEFT)
        e = tk.Entry(f, bd=1, relief="solid"); e.insert(0, c["s"][i]); e.pack(side=tk.LEFT, expand=True, fill="x", padx=10); s_ents.append(e)

    def go():
        n, s = [e.get() for e in ents], [e.get() for e in s_ents]
        save(n, s); root.destroy(); start(n, s)
    tk.Button(root, text="Start Timer", command=go, bg="#007bff", fg="white", font=("Malgun Gothic", 11, "bold"), pady=12).pack(pady=25, padx=25, fill="x")
    root.mainloop()

if __name__ == "__main__":
    ui()
