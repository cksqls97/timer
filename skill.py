import keyboard, pyperclip, datetime, tkinter as tk, json, os

CFG = "timer_config.json"

def save(n, s):
    with open(CFG, "w", encoding="utf-8") as f:
        json.dump({"n": n, "s": s}, f, ensure_ascii=False)

def load():
    if os.path.exists(CFG):
        try:
            with open(CFG, "r", encoding="utf-8") as f: return json.load(f)
        except: return None
    return None

def start(names, specs):
    u = {str(i+1): [names[i], 30, None] for i in range(4)}
    u['5'] = [specs[0], 13, None]
    u['6'] = [specs[1] if specs[1].strip() else "", 13, None]

    def up():
        now = datetime.datetime.now()
        o = []
        for i in range(1, 5):
            nm, cl, nt = u[str(i)]
            if nm.strip(): o.append(f"{nm} {nt.strftime('%H:%M')}" if nt and now < nt else nm)
        s_o = []
        for i in range(5, 7):
            nm, cl, nt = u[str(i)]
            if nm.strip(): s_o.append(f"{nm} {nt.strftime('%H:%M')}" if nt and now < nt else nm)
        res = f"{' '.join(o)} / {' '.join(s_o)}"
        pyperclip.copy(res)

    up() # 시작 시 클립보드 초기화

    for i in range(1, 7):
        keyboard.add_hotkey(f'num {i}', lambda k=str(i): (
            u[k].__setitem__(2, datetime.datetime.now() + datetime.timedelta(minutes=u[k][1])),
            up()
        ) if u[k][0].strip() else None)
    keyboard.wait()

def ui():
    root = tk.Tk()
    root.title("타이머")
    root.geometry("300x450")
    c = load() or {"n": ["", "", "", ""], "s": ["", ""]}
    tk.Label(root, text="이름 설정", font=("Arial", 12, "bold")).pack(pady=10)
    
    ents, s_ents = [], []
    for i in range(4):
        f = tk.Frame(root); f.pack(pady=2)
        tk.Label(f, text=f"리저{i+1}:", width=8).pack(side=tk.LEFT)
        e = tk.Entry(f, width=15); e.insert(0, c["n"][i]); e.pack(side=tk.LEFT)
        ents.append(e)

    for i in range(2):
        f = tk.Frame(root); f.pack(pady=2)
        tk.Label(f, text=f"손님{i+1}:", width=8).pack(side=tk.LEFT)
        e = tk.Entry(f, width=15); e.insert(0, c["s"][i]); e.pack(side=tk.LEFT)
        s_ents.append(e)

    def go():
        n, s = [e.get() for e in ents], [e.get() for e in s_ents]
        save(n, s); root.destroy(); start(n, s)

    tk.Button(root, text="시작", command=go, width=15, bg="blue", fg="white").pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    ui()
