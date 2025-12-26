import keyboard, pyperclip, datetime, tkinter as tk, json, os, threading

CFG = "timer_config.json"

def save(n, s):
    with open(CFG, "w", encoding="utf-8") as f:
        json.dump({"n": n, "s": s}, f, ensure_ascii=False)

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
        tk.Label(nt, text=message, fg="white", bg=color, font=("Malgun Gothic", 9)).pack(pady=5)
        nt.after(3000, nt.destroy)
        nt.mainloop()
    threading.Thread(target=run, daemon=True).start()

def start(names, specs):
    u = {
        '1':[names[0],30], '2':[names[1],30], '3':[names[2],30], '4':[names[3],30], 
        '7':[specs[0],13], '8':[specs[1] if specs[1].strip() else "", 13]
    }
    nt_times = {k: None for k in u.keys()}

    def create_status_window():
        global status_label
        sw = tk.Tk()
        sw.title("Status")
        sw.attributes("-topmost", True)
        sw.overrideredirect(True)
        sw.geometry("250x140+20+20")
        sw.configure(bg="#1a1a1a")
        
        def start_move(e): sw.x, sw.y = e.x, e.y
        def do_move(e): sw.geometry(f"+{sw.winfo_x()+(e.x-sw.x)}+{sw.winfo_y()+(e.y-sw.y)}")
        sw.bind("<Button-1>", start_move)
        sw.bind("<B1-Motion>", do_move)

        status_label = tk.Label(sw, text="대기 중...", fg="#00FF00", bg="#1a1a1a", font=("Consolas", 10, "bold"), justify=tk.LEFT, padx=10, pady=10)
        status_label.pack(fill="both", expand=True)
        sw.mainloop()

    def up():
        now = datetime.datetime.now()
        # 현재 시간 HHMM 형식
        cur_time_str = now.strftime('%H%M')
        
        o, s_o = [], []
        # 리저 인원 처리
        for i in '1234':
            nm = u[i][0].strip()
            if nm:
                if nt_times[i] and now < nt_times[i]:
                    o.append(f"{nm}: {nt_times[i].strftime('%H:%M')}")
                else:
                    o.append(nm)
        
        # 손님 인원 처리
        for i in '78':
            nm = u[i][0].strip()
            if nm:
                if nt_times[i] and now < nt_times[i]:
                    s_o.append(f"{nm}: {nt_times[i].strftime('%H:%M')}")
                else:
                    s_o.append(nm)
        
        # 요청하신 형식: 현재시간: hhmm / aaa: 20:00 ...
        res = f"현재시간: {cur_time_str} / {' '.join(o)} / {' '.join(s_o)}"
        pyperclip.copy(res)
        
        if status_label:
            st = f"● 현재: {cur_time_str}\n\n[리저]\n{' / '.join(o) if o else '-'}\n\n[손님]\n{' / '.join(s_o) if s_o else '-'}"
            status_label.config(text=st)

    def p(k):
        now = datetime.datetime.now()
        nm = u[k][0]
        
        if k in '1234' and nt_times[k] and now < nt_times[k]:
            custom_notify("쿨타임 경고", f"{nm}: 아직 쿨타임 중입니다!", "#d32f2f")
            return
        
        nt_times[k] = now + datetime.timedelta(minutes=u[k][1])
        up()
        tm = nt_times[k].strftime('%H:%M')
        msg = f"{nm} 사용됨. 다음: {tm}" if k in '1234' else f"{nm} 갱신됨. 부활: {tm}"
        custom_notify("타이머 갱신", msg, "#2e7d32")

    threading.Thread(target=create_status_window, daemon=True).start()
    
    for k in u.keys():
        keyboard.add_hotkey(f'num {k}', lambda x=k: p(x) if u[x][0].strip() else None)
    
    keyboard.add_hotkey('ctrl+alt+num 1', lambda: os._exit(0))
    keyboard.wait()

def ui():
    root = tk.Tk()
    root.title("Skill Timer Setup")
    root.geometry("320x580")
    root.configure(bg="#f8f9fa")
    
    try:
        img = tk.PhotoImage(file="icon.png")
        lbl_img = tk.Label(root, image=img, bg="#f8f9fa")
        lbl_img.image = img
        lbl_img.pack(pady=10)
    except:
        tk.Label(root, text="🛡️", font=("Arial", 30), bg="#f8f9fa").pack(pady=10)
    
    c = load() or {"n": ["","","",""], "s": ["",""]}
    tk.Label(root, text="타이머 인원 설정", font=("Malgun Gothic", 14, "bold"), bg="#f8f9fa").pack(pady=5)
    
    def create_input(label_text, default_val):
        f = tk.Frame(root, bg="#f8f9fa")
        f.pack(pady=4, padx=25, fill="x")
        tk.Label(f, text=label_text, width=8, anchor="w", bg="#f8f9fa", font=("Malgun Gothic", 10)).pack(side=tk.LEFT)
        e = tk.Entry(f, font=("Malgun Gothic", 10), bd=1, relief="solid")
        e.insert(0, default_val)
        e.pack(side=tk.LEFT, expand=True, fill="x", padx=(10, 0))
        return e

    ents = [create_input(f"리저 {i+1}", c["n"][i]) for i in range(4)]
    tk.Frame(root, height=1, bg="#dee2e6").pack(fill="x", padx=25, pady=15)
    s_ents = [create_input(f"손님 {i+1}", c["s"][i]) for i in range(2)]

    def go():
        n, s = [e.get() for e in ents], [e.get() for e in s_ents]
        save(n, s); root.destroy(); start(n, s)

    tk.Button(root, text="설정 저장 및 시작", command=go, bg="#007bff", fg="white", 
              font=("Malgun Gothic", 11, "bold"), relief="flat", pady=12).pack(pady=25, padx=25, fill="x")
    root.mainloop()

if __name__ == "__main__":
    ui()
