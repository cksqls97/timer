import keyboard, pyperclip, datetime, tkinter as tk, json, os, sys, winsound, ctypes
from tkinter import messagebox

# [1] 관리자 권한 체크
def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

CFG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "timer_config.json")

def load_config():
    if os.path.exists(CFG_FILE):
        try:
            with open(CFG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("n"): return data
        except: pass
    return {"n": ["비숍1", "비숍2", "비숍3", "비숍4"]}

def save_config(names):
    try:
        with open(CFG_FILE, "w", encoding="utf-8") as f:
            json.dump({"n": names}, f, ensure_ascii=False, indent=4)
    except: pass

# 전역 상태 변수
ov_root = None
ov_elements = {}
resurrection_alive = {'f1': True, 'f2': True, 'f3': True, 'f4': True}
guest_beep_flag = False
usage_logs = {'f1': [], 'f2': [], 'f3': [], 'f4': [], 'f5': []}
status_logs = {'f1': [], 'f2': [], 'f3': [], 'f4': []}

def show_manual():
    manual_text = (
        "[ Resurrection_Timer 사용 설명서 ]\n\n"
        "1. 조작 안내\n"
        " - 상단 바 드래그: 오버레이 위치 이동\n"
        " - 마우스 좌클릭: 타이머 시작 (30분/13분)\n"
        " - 마우스 우클릭: 비숍 사망/생존(D.O) 토글\n\n"
        "2. 주요 기능\n"
        " - 노란색: 사용 시 손님 연속 사망 대응 불가\n"
        " - 빨간색: 사망 시 로테이션 붕괴 위험\n\n"
        "3. 로그 저장\n"
        " - 종료 시 상세 타임라인 리포트 생성 (사망/부활 포함)"
    )
    messagebox.showinfo("Resurrection_Timer Manual", manual_text)

def create_exit_log(names):
    try:
        now = datetime.datetime.now()
        filename = now.strftime("%Y-%m-%d_%H시%M분%S초_미션리포트.txt")
        u_dict = {'f1': names[0], 'f2': names[1], 'f3': names[2], 'f4': names[3], 'f5': "손님"}
        
        log_content = [
            f"=== Resurrection Timer 미션 상세 리포트 ===",
            f"미션 종료 시각: {now.strftime('%Y-%m-%d %H:%M:%S')}",
            f"-------------------------------------------",
            f"1. 대상별 상세 기록",
            f"-------------------------------------------"
        ]
        
        for k in ['f1', 'f2', 'f3', 'f4', 'f5']:
            log_content.append(f"[{u_dict[k]}]")
            personal_events = []
            for t in usage_logs[k]:
                action = "사망 기록" if k == 'f5' else "리저 사용"
                personal_events.append((t, action))
            if k != 'f5':
                for t, s in status_logs[k]:
                    personal_events.append((t, s))
            personal_events.sort(key=lambda x: x[0])
            if personal_events:
                for idx, (t, act) in enumerate(personal_events, 1):
                    log_content.append(f"  {idx}. [{t.strftime('%H:%M:%S')}] {act}")
            else:
                log_content.append("  - 기록 없음")
            log_content.append("")
            
        log_content.append(f"-------------------------------------------")
        log_content.append(f"2. 미션 통합 타임라인 (시간순)")
        log_content.append(f"-------------------------------------------")
        
        all_events = []
        for k, times in usage_logs.items():
            for t in times:
                action = "사망 기록" if k == 'f5' else "리저 사용"
                all_events.append((t, u_dict[k], action))
        for k, states in status_logs.items():
            for t, s in states:
                all_events.append((t, u_dict[k], s))
        
        all_events.sort(key=lambda x: x[0])
        if all_events:
            for t, name, act in all_events:
                log_content.append(f"[{t.strftime('%H:%M:%S')}] {name: <6} | {act}")
        else:
            log_content.append("- 기록된 내역이 없습니다.")
            
        log_content.append(f"-------------------------------------------")
        log_content.append(f"리포트 생성 완료.")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(log_content))
    except: pass

def start_logic(names):
    u = {'f1': names[0], 'f2': names[1], 'f3': names[2], 'f4': names[3], 'f5': "손님"}
    nt_times = {k: None for k in u.keys()}

    def safe_exit():
        create_exit_log(names)
        os._exit(0)

    def go_to_setup():
        if ov_root: ov_root.destroy()
        show_setup_ui()

    def update_clipboard():
        now = datetime.datetime.now()
        cur_time = now.strftime('%H%M')
        o_p = []
        for rk in ['f1','f2','f3','f4']:
            if nt_times[rk] and nt_times[rk] > now:
                o_p.append(f"{u[rk]} {nt_times[rk].strftime('%M')}")
            else: o_p.append(u[rk])
        g_str = f"손님 {nt_times['f5'].strftime('%M')}" if nt_times['f5'] and nt_times['f5'] > now else "손님"
        pyperclip.copy(f"현재 {cur_time} | {' '.join(o_p)} | {g_str}")

    def update_display():
        now = datetime.datetime.now()
        
        current_alives = []
        for rk in ['f1','f2','f3','f4']:
            if resurrection_alive[rk]:
                t = nt_times[rk]
                current_alives.append(t if (t and t > now) else now)
        current_alives.sort()
        
        guest_deadline = nt_times['f5'] if nt_times['f5'] else now

        for rk in ['f1','f2','f3','f4']:
            c, nl, tl, rl, msg = ov_elements[rk]
            nl.config(text=u[rk], fg="white")
            
            if not resurrection_alive[rk]:
                c.config(highlightbackground="#441111", bg="#150A0A")
                for w in [nl, tl, rl, msg]: w.config(bg="#150A0A")
                tl.config(text="D.O", fg="#552222"); rl.config(text=""); msg.config(text=""); continue
            
            c.config(bg="#1E1E1E"); nl.config(bg="#1E1E1E"); tl.config(bg="#1E1E1E"); rl.config(bg="#1E1E1E"); msg.config(bg="#1E1E1E")
            
            if nt_times[rk] and nt_times[rk] > now:
                diff = nt_times[rk] - now
                m, s = divmod(int(diff.total_seconds()), 60)
                tl.config(text=nt_times[rk].strftime('%H:%M'), fg="#FF5252")
                rl.config(text=f"{m:02d}:{s:02d}", fg="#FFA0A0") # 남은 시간 표시
                msg.config(text=""); c.config(highlightbackground="#333", highlightthickness=1)
            else:
                tl.config(text="READY", fg="#4CAF50")
                rl.config(text="") # READY일 때는 남은 시간 숨김
                
                warn_texts = []
                tmp_u = sorted(current_alives)
                for i, t in enumerate(tmp_u):
                    if t <= now: 
                        tmp_u[i] = now + datetime.timedelta(minutes=30)
                        break
                tmp_u.sort()
                if tmp_u[0] > guest_deadline:
                    warn_texts.append("사용 시 불가")

                tmp_d = sorted(current_alives)
                found = False
                for i, t in enumerate(tmp_d):
                    if t <= now:
                        tmp_d.pop(i)
                        found = True
                        break
                if not found or not tmp_d or sorted(tmp_d)[0] > guest_deadline:
                    warn_texts.append("사망 시 불가")

                if "사망 시 불가" in warn_texts:
                    msg.config(text="\n".join(warn_texts), fg="#FF5252"); c.config(highlightbackground="#FF1744", highlightthickness=2)
                elif "사용 시 불가" in warn_texts:
                    msg.config(text="\n".join(warn_texts), fg="#FFD60
