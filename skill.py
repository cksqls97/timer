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
    # PowerShell을 이용한 시스템 알림 (한글 깨짐 방지 처리)
    toast_script = f"""
    $ErrorActionPreference = 'SilentlyContinue'
    [reflection.assembly]::loadwithpartialname('System.Windows.Forms')
    $bal = New-Object System.Windows.Forms.NotifyIcon
    $bal.Icon = [System.Drawing.Icon]::ExtractAssociatedIcon((Get-Process -id $pid).Path)
    $bal.BalloonTipIcon = 'Info'
    $bal.BalloonTipText = '{m}'
    $bal.BalloonTipTitle = '{t}'
    $bal.Visible = $true
    $bal.ShowBalloonTip(3000)
    """
    encoded_script = subprocess.list2cmdline(["PowerShell", "-Command", toast_script])
    subprocess.Popen(encoded_script, shell=True)

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
            if nm.strip(): o.append(f"{nm} {nt[i].strftime('%H:%M')}" if nt[i] and now < nt[i] else nm)
        for i in '78':
            nm = u[i][0]
            if nm.strip(): s_o.append(f"{nm} {nt[i].strftime('%H:%M')}" if nt[i] and now < nt[i] else nm)
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
        msg = f"{nm} 사용됨. 다음: {tm}" if k in '1234'
