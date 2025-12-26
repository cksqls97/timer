import keyboard, pyperclip, datetime, tkinter as tk, json, os, subprocess

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

def notify(t, m):
    # PowerShell 기반 시스템 알림
    cmd = f"PowerShell -Command \"$ErrorActionPreference='SilentlyContinue'; [reflection.assembly]::loadwithpartialname('System.Windows.Forms'); $bal=New-Object System.Windows.Forms.NotifyIcon; $bal.Icon=[System.Drawing.Icon]::ExtractAssociatedIcon((Get-Process -id $pid).Path); $bal.BalloonTipIcon='Info'; $bal.BalloonTipText='{m}'; $bal.BalloonTipTitle='{t}'; $bal.Visible=$true; $bal.ShowBalloonTip(3000)\""
    try: subprocess.Popen(cmd, shell=True)
    except: pass

def start(names, specs):
    u = {
        '1':[names[0],30], '2':[names[1],30], '3':[names[2],30], '4':[names[3],30], 
        '7':[specs[0],13], '8':[specs[1] if specs[1].strip() else "",13]
    }
    nt = {k: None for k in u.keys()}

    def up():
        now = datetime.datetime.now()
        o, s_o = [], []
        for i in '1234':
            nm = u[i][0]
            if nm.strip():
                if nt[i] and now < nt[i]: o.append(f"{nm} {nt[i].strftime('%H:%M')}")
                else: o.append(nm)
        for i in '78':
            nm = u[i][0]
            if nm.strip():
                if nt[i] and now < nt[i]: s_o.append(f"{nm} {nt[i].strftime('%H:%M')}")
                else: s_o.append(nm)
        res = f"{' '.join(o)} / {' '.join(s_o)}"
        pyperclip.copy(res)

    up()

    def p(k):
        now = datetime.datetime.now()
        nm = u[k][0]
        if nt[k] and now < nt[k]:
            notify("쿨타임 알림", f"{nm}: 아직 쿨타임 중입니다!")
            return
        nt[k] = now + datetime.timedelta(minutes=u[k][1])
        up()
        tm = nt[k].strftime('%H:%M')
        msg = f"{nm} 사용됨. 다음: {tm}" if k in '1234' else f"{nm} 사망함. 부활: {tm}"
        notify("타이머 갱신", msg)

    # 핫키 등록
    for k in u.keys():
        keyboard.add_hotkey(f'num {k}', lambda x=k: p(x) if u[x][0].strip() else None)
    
    # 긴급 종료 단축키 (Ctrl+Alt+Num 1)
    keyboard.add_hotkey('ctrl+alt+num 1', lambda: os._exit(0))
    
    keyboard.wait()

def ui():
    root = tk.Tk()
    root.title("Resurrection Timer Pro")
    root.geometry("320x520")
    root.configure(bg="#f0f0f0") # 배경색 설정
    
    c = load() or {"n": ["","","",""], "s": ["",""]}
    
    # 헤더
    tk.Label(root, text="🛡️ 타이머 설정", font=("Malgun Gothic", 16, "bold"), bg="#f0f0f0", fg="#333").pack(pady=20)
    
    # 입력 그룹 스타일링
    def create_input(parent, label_text, default_val):
        frame = tk.Frame(parent, bg="#f0f0f0")
        frame.pack(pady=5, padx=20, fill="x")
