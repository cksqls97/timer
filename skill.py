import keyboard, pyperclip, datetime, tkinter as tk, json, os, threading, sys, winsound, ctypes
from tkinter import messagebox

# [1] 관리자 권한 및 리소스 설정
def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

def load():
    if os.path.exists("timer_config.json"):
        with open("timer_config.json", "r", encoding="utf-8") as f: return json.load(f)
    return {"n": ["비숍1", "비숍2", "비숍3", "비숍4"], "s": ["손님1", "손님2"]}

ov_root = None
ov_elements = {}
# rezzer -> resurrection_alive로 변경
resurrection_alive = {'f1': True, 'f2': True, 'f3': True, 'f4': True}
beep_flags = {'f5': False, 'f6': False}

def start_logic(names, specs):
    u = {'f1': [names[0], 30], 'f2': [names[1], 30], 'f3': [names[2], 30], 'f4': [names[3], 30],
         'f5': [specs[0], 13], 'f6': [specs[1] if specs[1].strip() else "", 13]}
    nt_times = {k: None for k in u.keys()}

    def toggle_resurrection(k):
        """리저 보유자 사망 상태 토글"""
        resurrection_alive[k] = not resurrection_alive[k]
        up()

    def update_clipboard():
        now = datetime.datetime.now()
        cur_time_str = now.strftime('%H%M')
        o_clip, s_clip = [], []
        
        for rk in ['f1', 'f2', 'f3', 'f4']:
            if nt_times[rk] and nt_times[rk] > now:
                o_clip.append(f"{u[rk][0]} {nt_times[rk].strftime('%M')}")
            else:
                o_clip.append(u[rk][0])
        
        for sk in ['f5', 'f6']:
            nm = u[sk][0].strip()
            if not nm: continue
            if nt_times[sk] and nt_times[sk] > now:
                s_clip.append(f"{nm} {nt_times[sk].strftime('%M')}")
            else:
                s_clip.append(nm)
                
        text = f"현재시간 {cur_time_str} / {' '.join(o_clip)} / {' '.join(s_clip)}"
        pyperclip.copy(text)

    def create_overlay():
        global ov_root, ov_elements
        ov_root = tk.Tk()
        ov_root.attributes("-topmost", True); ov_root.overrideredirect(True)
        ov_root.configure(bg="#111")
        w, h = 380, 460 
        ov_root.geometry(f"{w}x{h}+{ov_root.winfo_screenwidth()-w-20}+{ov_root.winfo_screenheight()-h-100}")
        
        header = tk.Frame(ov_root, bg="#2D2D2D", height=40); header.pack(fill="x")
        ov_elements['now'] = tk.Label(header, text="READY", fg="#00FF7F", bg="#2D2D2D", font=("Malgun Gothic", 12, "bold"))
        ov_elements['now'].pack(side=tk.LEFT, padx=15)
        tk.Button(header, text="✕", bg="#2D2D2D", fg="white", bd=0, font=("Arial", 12), command=lambda: os._exit(0)).pack(side=tk.RIGHT, padx=10)

        main_cont = tk.Frame(ov_root, bg="#111", padx=10, pady=10); main_cont.pack(fill="both", expand=True)

        def create_card(parent, k, is_guest=False):
            card = tk.Frame(parent, bg="#222", bd=1, relief="flat", padx=5, pady=8)
            nl = tk.Label(card, text="-", fg="white", bg="#222", font=("Malgun Gothic", 12, "bold"))
            tl = tk.Label(card, text="READY", fg="#BB86FC" if not is_guest else "#03DAC6", bg="#222", font=("Malgun Gothic", 11, "bold"))
            msg = tk.Label(card, text="", fg="#FF5252", bg="#222", font=("Malgun Gothic", 10, "bold"))
            nl.pack(); tl.pack(); msg.pack()
            if not is_guest:
                for widget in [card, nl, tl, msg]: widget.bind("<Button-3>", lambda e, x=k: toggle_resurrection(x))
            return card, nl, tl, msg

        for i, k in enumerate(['f1', 'f2', 'f3', 'f4']):
            c_obj, nl, tl, msg = create_card(main_cont, k)
            c_obj.grid(row=(i//2)+1, column=i%2, padx=4, pady=4, sticky="nsew")
            ov_elements[k] = (c_obj, nl, tl, msg)

        for i, k in enumerate(['f5', 'f6']):
            c_obj, nl, tl, msg = create_card(main_cont, k, is_guest=True)
            c_obj.grid(row=4, column=i, padx=4, pady=4, sticky="nsew")
            ov_elements[k] = (c_obj, nl, tl, msg)

        main_cont.grid_columnconfigure(0, weight=1); main_cont.grid_columnconfigure(1, weight=1)

        for k in u.keys():
            keyboard.add_hotkey(k, lambda x=k: p(x) if u[x][0].strip() else None, suppress=False)
        
        def auto_update():
            if ov_root.winfo_exists(): up(); ov_root.after(1000, auto_update)
        auto_update(); ov_root.mainloop()

    def up():
        now = datetime.datetime.now()
        # 생존한 비숍들의 다음 사용 가능 시간 리스트
        alive_resurrection_times = [nt_times[rk] if nt_times[rk] and nt_times[rk] > now else now 
                                    for rk in ['f1','f2','f3','f4'] if resurrection_alive[rk]]
        
        for rk in ['f1','f2','f3','f4']:
            card, nl, tl, msg = ov_elements[rk]
            nl.config(text=u[rk][0])
            if not resurrection_alive[rk]:
                card.config(highlightbackground="#FF1744", highlightthickness=2)
                tl.config(text="DEATH", fg="#FF1744"); msg.config(text="")
                continue
            
            if nt_times[rk] and nt_times[rk] > now:
                tl.config(text=nt_times[rk].strftime('%H:%M'), fg="#FF5252")
                msg.config(text=""); card.config(highlightthickness=0)
            else:
                tl.config(text="READY", fg="#4CAF50")
                
                # 1. 사망 시 시뮬레이션
                temp_death = list(alive_resurrection_times)
                try: temp_death.remove(now)
                except: pass
                next_if_death = min(temp_death) if temp_death else now + datetime.timedelta(minutes=99)
                
                # 2. 사용 시 시뮬레이션
                temp_use = list(alive_resurrection_times)
                try: 
                    idx = temp_use.index(now)
                    temp_use[idx] = now + datetime.timedelta(minutes=30)
                except: pass
                next_if_use = min(temp_use) if temp_use else now + datetime.timedelta(minutes=99)

                # 경고 출력 (사망 시 우선)
                if (next_if_death - now).total_seconds() > 14 * 60:
                    msg.config(text="사망 시 손님 부활 불가", fg="#FF5252")
                    card.config(highlightbackground="#FF1744", highlightthickness=1)
                elif (next_if_use - now).total_seconds() > 14 * 60:
                    msg.config(text="사용 시 손님 부활 불가", fg="#FFD600")
                    card.config(highlightbackground="#FFD600", highlightthickness=1)
                else:
                    msg.config(text=""); card.config(highlightthickness=0)

        # 손님 카드 업데이트
        min_resurrection = min(alive_resurrection_times) if alive_resurrection_times else now + datetime.timedelta(minutes=99)
        for k in ['f5','f6']:
            _, nl, tl, msg = ov_elements[k]
            if not u[k][0].strip(): continue
            nl.config(text=u[k][0])
            if nt_times[k] and now < nt_times[k]:
                tl.config(text=nt_times[k].strftime('%H:%M'), fg="#FF5252")
                diff_sec = (nt_times[k] - now).total_seconds()
                margin = diff_sec - (min_resurrection - now).total_seconds()
                msg.config(text="⚠️ 부활 불가" if margin < 0 else f"{int(margin//60)}분 전", fg="#FF1744" if margin < 0 else "#FFAB00")
                if 58 <= diff_sec <= 61 and not beep_flags[k]:
                    winsound.Beep(1000, 500); beep_flags[k] = True
            else: 
                tl.config(text="READY", fg="#4CAF50"); msg.config(text="")
                beep_flags[k] = False

        if ov_root: ov_elements['now'].config(text=f"🕒 {now.strftime('%H:%M')}")

    def p(k):
        now = datetime.datetime.now()
        if k in ['f1','f2','f3','f4']:
            if resurrection_alive[k] and (not nt_times[k] or now >= nt_times[k]):
                nt_times[k] = now + datetime.timedelta(minutes=30)
        else:
            nt_times[k] = now + datetime.timedelta(minutes=13)
            beep_flags[k] = False
        
        up()
        update_clipboard()

    create_overlay()

def ui():
    c = load()
    start_logic(c["n"], c["s"])

if __name__ == "__main__": ui()
