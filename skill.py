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

# 시스템 알림 대신 직접 띄우는 커스텀 알림창
def custom_notify(title, message, color="#333"):
    def run():
        nt = tk.Toplevel()
        nt.overrideredirect(True) # 테두리 없는 창
        nt.attributes("-topmost", True)
        
        # 우측 하단 배치
        w, h = 280, 80
        sx = nt.winfo_screenwidth() - w - 20
        sy = nt.winfo_screenheight() - h - 50
        nt.geometry(f"{w}x{h}+{sx}+{sy}")
        nt.configure(bg=color)
        
        tk.Label(nt, text=title, fg="white", bg=color, font=("Malgun Gothic", 10, "bold")).pack(pady=(10, 0))
        tk.Label(nt, text=message, fg="white", bg=color, font=("Malgun Gothic", 9)).pack(pady=5)
        
        nt.after(3000, nt.destroy) # 3초 후 자동 종료
        nt.mainloop()
    
    # 메인 루프 방해 안 되게 별도 스레드 실행
    threading.Thread(target=run, daemon=True).start()

def start(names, specs):
    u = {
        '1':[names[0],30], '2':[names[1],30], '3':[names[2],30], '4':[names[3],30], 
        '7':[specs[0],13], '8':[specs[1] if specs[1].strip() else "", 13]
    }
    nt_times = {k: None for k in u.keys()}

    def up():
        now = datetime.datetime.now()
        o, s_o = [], []
        for i in '1234':
            nm = u[i][0]
            if nm.strip():
                if nt_times[i] and now < nt_times[i]: o.append(f"{nm} {nt_times[i].strftime('%H:%M')}")
                else: o.append(nm)
        for i in '78':
            nm = u[i][0]
            if nm.strip():
                if nt_times[i] and now < nt_times[i]: s_o.append(f"{nm} {nt_times[i].strftime('%H:%M')}")
                else: s_o.append(nm)
        res = f"{' '.join(o)} / {' '.join(s_o)}"
        pyperclip.copy(res)

    up()

    def p(k):
        now = datetime.datetime.now()
        nm = u[k][0]
        if nt_times[k] and now < nt_times[k]:
            custom_notify("쿨타임 경고", f"{nm}: 아직 쿨타임 중입니다!", "#d32f2f")
            return
        
        nt_times[k] = now + datetime.timedelta(minutes=u[k][1])
        up()
        tm = nt_times[k].strftime('%H:%M')
        msg = f"{nm} 사용됨. 다음: {tm}" if k in '1234' else f"{nm} 사망. 부활: {tm}"
        custom_notify("타이머 갱신", msg, "#2e7d32")

    # 핫키 설정
    for k in u.keys():
        keyboard.add_hotkey(f'num {k}', lambda x=k: p(x) if u[x][0].strip() else None)
    
    keyboard.add_hotkey('ctrl+alt+num 1', lambda: os._exit(0))
    keyboard.wait()

def ui():
    root = tk.Tk()
    root.title("Resurrection Timer")
    root.geometry("320x550")
    root.configure(bg="#ffffff")
    
    c = load() or {"n": ["","","",""], "s": ["",""]}
    
    tk.Label(root, text="🛡️ 타이머 설정", font=("Malgun Gothic", 16, "bold"), bg="white").pack(pady=20)
    
    def create_input(label_text, default_val):
        f = tk.Frame(root, bg="white")
        f.pack(pady=5, padx=25, fill="x")
        tk.Label(f, text=label_text, width=8, anchor="w", bg="white", font=("Malgun Gothic", 10)).pack(side=tk.LEFT)
        e = tk.Entry(f, font=("Malgun Gothic", 10), bd=1, relief="solid")
        e.insert(0, default_val)
        e.pack(side=tk.LEFT, expand=True, fill="x", padx=(10, 0))
        return e

    ents = [create_input(f"리저 {i+1}", c["n"][i]) for i in range(4)]
    tk.Frame(root, height=1, bg="#eeeeee").pack(fill="x", padx=25, pady=15)
    s_ents = [create_input(f"손님 {i+1}", c["s"][i]) for i in range(2)]

    def go():
        n, s = [e.get() for e in ents], [e.get() for e in s_ents]
        if not any(n + s): return # 아무것도 입력 안하면 시작 안함
        save(n, s)
        root.destroy()
        start(n, s)

    btn = tk.Button(root, text="타이머 시작", command=go, bg="#1a73e8", fg="white", 
                   font=("Malgun Gothic", 11, "bold"), relief="flat", pady=12, cursor="hand2")
    btn.pack(pady=30, padx=25, fill="x")
    
    tk.Label(root, text="종료: Ctrl + Alt + Numpad 1", font=("Malgun Gothic", 8), bg="white", fg="#999").pack()
    root.mainloop()

if __name__ == "__main__":
    ui()
