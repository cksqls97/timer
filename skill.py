import keyboard, pyperclip, datetime, tkinter as tk, json, os
from plyer import notification

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

def notify(t, m):
    try:
        notification.notify(title=t, message=m, app_name='SkillTimer', timeout=3)
    except: pass

def start(names, specs):
    u = {
        '1': [names[0], 30], '2': [names[1], 30], '3': [names[2], 30], '4': [names[3], 30],
        '7': [specs[0], 13], '8': [specs[1] if specs[1].strip() else "", 13]
    }
    nt = {k: None for k in u.keys()}

    def up():
        now = datetime.datetime.now()
        o, s_o = [], []
        for i in ['1','2','3','4']:
            nm = u[i][0]
            if nm.strip(): o.append(f"{nm} {nt[i].strftime('%H:%M')}" if nt[i] and now < nt[i] else nm)
        for i in ['7','8']:
            nm = u[i][0]
            if nm.strip(): s_o.append(f"{nm} {nt[i].strftime('%H:%M')}" if nt[i] and now < nt[i] else nm)
        res = f"{' '.join(o)} / {' '.join(s_o)}"
        pyperclip.copy(res)

    up()

    def p(k):
        now = datetime.datetime.now()
        nm = u[k][0]
        if nt[k] and now < nt[k]:
            notify("Cooldown", f"{nm}: Still on cooldown!")
            return
        nt[k] = now + datetime.timedelta(minutes=u[k][1])
        up()
        tm = nt[k].strftime('%H:%M')
        if k in ['1','2','3','4']: msg = f"{nm} 사용됨\n다음: {tm}"
        else: msg = f"{nm} 사망\n부활: {tm}"
        notify("Timer", msg)

    for k in u.keys():
        keyboard.add_hotkey(f'num {k}', lambda x=k: p(x) if u[x][0].strip() else None)
    keyboard.wait()

def ui():
    root = tk.Tk()
    root.title("Timer Pro")
    root.geometry("300x450")
    c = load() or {"n": ["", "", "", ""], "s": ["", ""]}
    tk.Label(root, text="Names", font=("Arial", 12, "bold")).pack(pady=10)
    ents, s_ents = [], []
    for i in range(4):
        f = tk.Frame(root); f.pack(pady=2)
        tk.Label(f, text=f"Rez {i+1}:", width=8).pack(side=tk.LEFT)
        e = tk.Entry(f, width=15); e.insert(0, c["n"][i]); e.pack(side=tk.LEFT)
        ents.append(e)
    for i in range(2):
        f = tk.Frame(root); f.pack(pady=2)
        tk.Label(f, text=f"Guest {i+1}:", width=8).pack(side=tk.LEFT)
        e = tk.Entry(f, width=15); e.insert(0, c["s"][i]); e.pack(side=tk.LEFT)
        s_ents.append(e)
    def go():
        n, s = [e.get() for e in ents], [e.get() for e in s_ents]
        save(n, s); root.destroy(); start(n, s)
    tk.Button(root, text="Start", command=go, width=15, bg="blue", fg="white").pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    ui()
