import keyboard, pyperclip, datetime, tkinter as tk, json, os
from win10toast import ToastNotifier

CFG = "timer_config.json"
toaster = ToastNotifier()

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
        toaster.show_toast(t, m, duration=2, threaded=True)
    except: pass

def start(names, specs):
    # 키 설정: 리저(1,2,3,4), 손님(7,8)
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

    up() # 시작 시 클립보드 세팅

    def p(k):
        now = datetime.datetime.now()
        nm = u[k][0]
        if nt[k] and now < nt[k]:
            notify("쿨타임 알림", f"{nm}의 쿨타임이 아직 지나지 않았습니다!")
            return
        
        nt[k] = now + datetime.timedelta(minutes=u[k][1])
        up()
        tm = nt[k].strftime('%H:%M')
        
        if k in ['1','2','3','4']:
            msg = f"{nm}가 리저를 사용했습니다.\n다음 리저 시간: {tm}"
        else:
            msg = f"{nm}가 사망하였습니다.\n다음 부활 시간: {tm}"
        notify("타이머 갱신", msg)

    for k in u.keys():
        keyboard.add_hotkey(f'num {k}', lambda x=k: p(x) if u[x][0].strip() else None)
    
    keyboard.wait()

def ui():
    root = tk.Tk()
    root.title("스킬 타이머 Pro")
    root.geometry("300x480")
    c = load() or {"n": ["", "", "", ""], "s": ["", ""]}
    
    tk.Label(root, text="이름 설정", font=("Malgun Gothic", 12, "bold")).pack(pady=10)
    
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

    tk.Button(root, text="저장 및 시작", command=go, width=15, bg="#2196F3", fg="white", font=("Malgun Gothic", 10, "bold")).pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    ui()
