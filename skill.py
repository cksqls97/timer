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

def notify(title, msg):
    # threaded=True를 사용해야 알림 창 때문에 프로그램이 멈추지 않습니다.
    toaster.show_toast(title, msg, duration=2, threaded=True)

def start(names, specs):
    # 단축키 매핑: 리저(1,2,3,4), 손님(7,8)
    u = {
        '1': [names[0], 30], '2': [names[1], 30], '3': [names[2], 30], '4': [names[3], 30],
        '7': [specs[0], 13], '8': [specs[1] if specs[1].strip() else "", 13]
    }
    # 쿨타임 종료 시간 저장
    nt = {k: None for k in u.keys()}

    def up():
        now = datetime.datetime.now()
        o = []
        for i in ['1','2','3','4']:
            nm = u[i][0]
            if nm.strip(): o.append(f"{nm} {nt[i].strftime('%H:%M')}" if nt[i] and now < nt[i] else nm)
        s_o = []
        for i in ['7','8']:
            nm = u[i][0]
            if nm.strip(): s_o.append(f"{nm} {nt[i].strftime('%H:%M')}" if nt[i] and now < nt[i] else nm)
        res = f"{' '.join(o)} / {' '.join(s_o)}"
        pyperclip.copy(res)

    up() # 시작 시 즉시 클립보드 세팅

    def p(k):
        now = datetime.datetime.now()
        nm = u[k][0]
        
        # 1. 중복 클릭(쿨타임 중) 체크
        if nt[k] and now < nt[k]:
            notify("쿨타임 경고
