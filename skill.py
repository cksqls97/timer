import keyboard, pyperclip, datetime, tkinter as tk, json, os, threading, sys
from tkinter import messagebox

def resource_path(relative_path):
    """ PyInstaller 빌드 환경에서도 파일을 찾을 수 있게 경로 설정 """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

CFG = resource_path("timer_config.json")

def save(n, s):
    """ 설정 저장 """
    try:
        with open("timer_config.json", "w", encoding="utf-8") as f:
            json.dump({"n": n, "s": s}, f, ensure_ascii=False)
    except:
        pass

def load():
    """ 설정 불러오기 """
    target = "timer_config.json" if os.path.exists("timer_config.json") else CFG
    if os.path.exists(target):
        try:
            with open(target, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"n": ["안녕동주야", "브레멘비숍", "외화유출비숍", "돼승끼"], "s": ["손님1", "손님2"]}

ov_root = None
ov_labels = {}

def custom_notify(title, message, color="#333"):
    """ 우측 하단 팝업 알림 """
    def run():
        nt = tk.Toplevel()
        nt.overrideredirect(True)
        nt.attributes("-topmost", True)
        w, h = 280, 80
        sx, sy = nt.winfo_screenwidth() - w - 20, nt.winfo_screenheight() - h - 50
        nt.geometry(f"{w}x{h}+{sx}+{sy}")
        nt.configure(bg=color)
        tk.Label(nt, text=title, fg="white", bg=color, font=("Malgun Gothic", 10, "bold")).pack(pady=(10, 0))
        tk.Label(nt, text=message, fg="white", bg=color, font=("Malgun Gothic", 9), wraplength=250).pack(pady=5)
        nt.after(3000, nt.destroy)
        nt.mainloop()
    threading.Thread(target=run, daemon=True).start()

def start_logic(names, specs):
    """ 메인 타이머 및 GUI 구획화 로직 """
    try:
        u = {
            '1': [names[0], 30], '2': [names[1], 30], '3': [names[2], 30], '4': [names[3], 30],
            '7': [specs[0], 13], '8': [specs[1] if specs[1].strip() else "", 13]
        }
        nt_times = {k: None for k in u.keys()}

        def create_overlay():
            global ov_root, ov_labels
            ov_root = tk.Tk()
            ov_root.title("Overlay")
            ov_root.attributes("-topmost", True)
            ov_root.overrideredirect(True)
            
            # 오버레이 창 크기 및 기본 배경
            w, h = 320, 260
            sx, sy = ov_root.winfo_screenwidth() - w - 20, ov_root.winfo_screenheight() - h - 140
            ov_root.geometry(f"{w}x{h}+{sx}+{sy}")
            ov_root.configure(bg="#1a1a1a") # 다크 그레이 배경
            
            # 드래그 기능
            def sm(e): ov_root.x, ov_root.y = e.x, e.y
            def dm(e): ov_root.geometry(f"+{ov_root.winfo_x() + (e.x - ov_root.x)}+{ov_root.winfo_y() + (e.y - ov_root.y)}")
            ov_root.bind("<Button-1>", sm)
            ov_root.bind("<B1-Motion>", dm)

            # 1. 상단 현재 시간 구획 (Header Box)
            header_frame = tk.Frame(ov_root, bg="#3d5afe", height=40)
            header_frame.pack(fill="x")
            ov_labels['now'] = tk.Label(header_frame, text="READY", fg="white", bg="#3d5afe", font=("Malgun Gothic", 11, "bold"))
            ov_labels['now'].pack(pady=7)

            # 본문 컨테이너 (여백용)
            content = tk.Frame(ov_root, bg="#1a1a1a", padx=10, pady=10)
            content.pack(fill="both", expand=True)

            # 2. 리저 구획 박스 (Card 스타일)
            rez_frame = tk.Frame(content, bg="#2d2d2d", bd=1, relief="solid")
            rez_frame.pack(fill="x", pady=(0, 10))
            tk.Label(rez_frame, text=" REZ STATUS ", fg="#b39ddb", bg="#2d2d2d", font=("Malgun Gothic", 8, "bold")).pack(anchor="w", padx=5, pady=(2, 0))
            ov_labels['rez'] = tk.Label(rez_box_inner := tk.Frame(rez_frame, bg="#2d2d2d", padx=5, pady=5), 
                                        text="-", fg="white", bg="#2d2d2d", font=("Malgun Gothic", 9), justify=tk.LEFT, anchor="nw", wraplength=280)
            rez_box_inner.pack(fill="x")
            ov_labels['rez'].pack(fill="x")

            # 3. 손님 구획 박스 (Card 스타일)
            gst_frame = tk.Frame(content, bg="#2d2d2d", bd=1, relief="solid")
            gst_frame.pack(fill="x")
            tk.Label(gst_frame, text=" GUEST STATUS ", fg="#80cbc4", bg="#2d2d2d", font=("Malgun Gothic", 8, "bold")).pack(anchor="w", padx=5, pady=(2, 0))
            ov_labels['gst'] = tk.Label(gst_box_inner := tk.Frame(gst_frame, bg="#2d2d2d", padx=5, pady=5), 
                                        text="-", fg="white", bg="#2d2d2d", font=("Malgun Gothic", 9), justify=tk.LEFT, anchor="nw", wraplength=280)
            gst_box_inner.pack(fill="x")
            ov_labels['gst'].pack(fill="x")
            
            # 핫키 스캔코드 등록 (방향키 간섭 방지)
            scan_codes = {'1': 79, '2': 80, '3': 81, '4': 75, '7': 71, '8': 72}
            def handle_press(k):
                if u[k][0].strip(): p(k)

            for k, code in scan_codes.items():
                keyboard.on_press_key(code, lambda e, x=k: handle_press(x), suppress=False)
            
            keyboard.add_hotkey('ctrl+alt+num 1', lambda: os._exit(0))
            ov_root.mainloop()

        def up():
            now = datetime.datetime.now()
            cur_time_clip = now.strftime('%H%M')
            cur_time_ov = now.strftime('%H:%M')
            o_clip, s_clip, o_ov, s_ov = [], [], [], []

            for i in '1234':
                nm = u[i][0].strip()
                if nm:
                    if nt_times[i] and now < nt_times[i]:
                        o_clip.append(f"{nm} {nt_times[i].strftime('%M')}")
                        o_ov.append(f"{nm} [{nt_times[i].strftime('%H:%M')}]")
                    else:
                        o_clip.append(nm)
                        o_ov.append(f"{nm} [READY]")
            
            for i in '78':
                nm = u[i][0].strip()
                if nm:
                    if nt_times[i] and now < nt_times[i]:
                        s_clip.append(f"{nm} {nt_times[i].strftime('%M')}")
                        s_ov.append(f"{nm} [{nt_times[i].strftime('%H:%M')}]")
                    else:
                        s_clip.append(nm)
                        s_ov.append(f"{nm} [READY]")

            # 클립보드: 현재시간 0548 / 이름 17 / 손님 01
            clip_text = f"현재시간 {cur_time_clip} / {' '.join(o_clip)} / {' '.join(s_clip)}"
            pyperclip.copy(clip_text)
            
            if ov_root:
                ov_labels['now'].config(text=f"🕒 CURRENT: {cur_time_ov}")
                ov_labels['rez'].config(text=' | '.join(o_ov) if o_ov else "No Data")
                ov_labels['gst'].config(text=' | '.join(s_ov) if s_ov else "No Data")

        def p(k):
            now = datetime.datetime.now()
            nm = u[k][0]
            if k in '1234' and nt_times[k] and now < nt_times[k]:
                custom_notify("Cooldown", f"{nm}: Still on cooldown!", "#d32f2f")
                return
            nt_times[k] = now + datetime.timedelta(minutes=u[k][1])
            up()
            custom_notify("Timer Update", f"{nm} ({nt_times[k].strftime('%H:%M')})", "#2e7d32")

        create_overlay()
    except Exception as e:
        messagebox.showerror("Error", f"로직 오류: {str(e)}")
        os._exit(1)

def ui():
    root = tk.Tk()
    root.title("Skill Timer")
    root.geometry("320x550")
    root.configure(bg="#f8f9fa")
    
    config_data = load()
    tk.Label(root, text="TIMER SETUP", font=("Malgun Gothic", 16, "bold"), bg="#f8f9fa", fg="#333").pack(pady=20)
    
    ents, s_ents = [], []
    for i in range(4):
        f = tk.Frame(root, bg="#f8f9fa"); f.pack(pady=4, padx=25, fill="x")
        tk.Label(f, text=f"리저 {i+1}", width=8, anchor="w", bg="#f8f9fa").pack(side=tk.LEFT)
        e = tk.Entry(f, bd=1, relief="solid"); e.insert(0, config_data["n"][i])
        e.pack(side=tk.LEFT, expand=True, fill="x", padx=10); ents.append(e)
        
    tk.Frame(root, height=1, bg="#dee2e6").pack(fill="x", padx=25, pady=15)
    
    for i in range(2):
        f = tk.Frame(root, bg="#f8f9fa"); f.pack(pady=4, padx=25, fill="x")
        tk.Label(f, text=f"손님 {i+1}", width=8, anchor="w", bg="#f8f9fa").pack(side=tk.LEFT)
        e = tk.Entry(f, bd=1, relief="solid"); e.insert(0, config_data["s"][i])
        e.pack(side=tk.LEFT, expand=True, fill="x", padx=10); s_ents.append(e)

    def go():
        n, s = [e.get() for e in ents], [e.get() for e in s_ents]
        save(n, s); root.destroy(); start_logic(n, s)

    tk.Button(root, text="START TIMER", command=go, bg="#6200EE", fg="white", font=("Malgun Gothic", 11, "bold"), pady=12).pack(pady=30, padx=25, fill="x")
    root.mainloop()

if __name__ == "__main__":
    ui()
