import keyboard
import pyperclip
import datetime
import tkinter as tk
import json
import os
import threading
import sys
import winsound
import ctypes
from tkinter import messagebox

# [관리자 권한 자동 요청 로직]
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        # 관리자 권한으로 자기 자신을 다시 실행
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

# 실행 시 즉시 관리자 권한 체크
run_as_admin()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

CFG_FILE = "timer_config.json"

def save_cfg(n, s):
    try:
        with open(CFG_FILE, "w", encoding="utf-8") as f:
            json.dump({"n": n, "s": s}, f, ensure_ascii=False)
    except Exception as e:
        print(f"Save error: {e}")

def load_cfg():
    if os.path.exists(CFG_FILE):
        try:
            with open(CFG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"n": ["안녕동주야", "브레멘비숍", "외화유출비숍", "돼승끼"], "s": ["손님1", "손님2"]}

class SkillTimerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Skill Timer v1.0")
        self.u = {}
        self.nt_times = {}
        self.rezzer_alive = {'f1': True, 'f2': True, 'f3': True, 'f4': True}
        self.beep_flags = {'f5': False, 'f6': False}
        self.ov_elements = {}
        self.setup_ui()

    def setup_ui(self):
        self.root.geometry("360x640")
        self.root.configure(bg="#f8f9fa")
        self.root.eval('tk::PlaceWindow . center')
        
        c = load_cfg()
        tk.Label(self.root, text="TIMER SETUP", font=("Malgun Gothic", 18, "bold"), bg="#f8f9fa", fg="#333").pack(pady=(30, 20))
        
        container = tk.Frame(self.root, bg="#f8f9fa")
        container.pack(padx=30, fill="x")

        # 리저 인원 입력
        tk.Label(container, text="[ Resurrection Members ]", fg="#6200EE", bg="#f8f9fa", font=("Malgun Gothic", 9, "bold")).pack(anchor="w", pady=(10, 5))
        self.ents = []
        for i in range(4):
            f = tk.Frame(container, bg="#f8f9fa")
            f.pack(fill="x", pady=4)
            tk.Label(f, text=f"F{i+1}", bg="#f8f9fa", width=4, font=("Malgun Gothic", 10)).pack(side=tk.LEFT)
            e = tk.Entry(f, bd=1, relief="solid", font=("Malgun Gothic", 10))
            e.insert(0, c["n"][i])
            e.pack(side=tk.LEFT, expand=True, fill="x", padx=(10, 0))
            self.ents.append(e)

        tk.Frame(container, height=1, bg="#dee2e6").pack(fill="x", pady=20)

        # 손님 인원 입력
        tk.Label(container, text="[ Guest Members ]", fg="#03DAC6", bg="#f8f9fa", font=("Malgun Gothic", 9, "bold")).pack(anchor="w", pady=(0, 5))
        self.s_ents = []
        for i in range(2):
            f = tk.Frame(container, bg="#f8f9fa")
            f.pack(fill="x", pady=4)
            tk.Label(f, text=f"F{i+5}", bg="#f8f9fa", width=4, font=("Malgun Gothic", 10)).pack(side=tk.LEFT)
            e = tk.Entry(f, bd=1, relief="solid", font=("Malgun Gothic", 10))
            e.insert(0, c["s"][i])
            e.pack(side=tk.LEFT, expand=True, fill="x", padx=(10, 0))
            self.s_ents.append(e)

        tk.Button(self.root, text="START TIMER", command=self.start_timer, bg="#6200EE", fg="white", font=("Malgun Gothic", 12, "bold"), pady=15, relief="flat").pack(pady=40, padx=30, fill="x")

    def start_timer(self):
        names = [e.get() for e in self.ents]
        specs = [e.get() for e in self.s_ents]
        save_cfg(names, specs)
        
        self.u = {
            'f1': [names[0], 30], 'f2': [names[1], 30], 'f3': [names[2], 30], 'f4': [names[3], 30],
            'f5': [specs[0], 13], 'f6': [specs[1] if specs[1].strip() else "", 13]
        }
        self.nt_times = {k: None for k in self.u.keys()}
        self.root.withdraw()
        self.show_overlay()

    def show_overlay(self):
        self.ov = tk.Toplevel(self.root)
        self.ov.attributes("-topmost", True)
        self.ov.overrideredirect(True)
        self.ov.configure(bg="#121212")
        
        w, h = 360, 420
        sx = self.ov.winfo_screenwidth() - w - 20
        sy = self.ov.winfo_screenheight() - h - 180
        self.ov.geometry(f"{w}x{h}+{sx}+{sy}")

        def sm(e): self.ov.x, self.ov.y = e.x, e.y
        def dm(e): self.ov.geometry(f"+{self.ov.winfo_x()+(e.x-self.ov.x)}+{self.ov.winfo_y()+(e.y-self.ov.y)}")
        self.ov.bind("<Button-1>", sm)
        self.ov.bind("<B1-Motion>", dm)

        header = tk.Frame(self.ov, bg="#3d5afe", height=45)
        header.pack(fill="x")
        self.ov_elements['now'] = tk.Label(header, text="READY", fg="white", bg="#3d5afe", font=("Malgun Gothic", 11, "bold"))
        self.ov_elements['now'].pack(side=tk.LEFT, padx=15, pady=8)

        tk.Button(header, text="✕", bg="#3d5afe", fg="white", bd=0, font=("Arial", 12, "bold"), command=lambda: os._exit(0)).pack(side=tk.RIGHT, padx=5)
        tk.Button(header, text="⚙", bg="#3d5afe", fg="white", bd=0, font=("Arial", 14), command=self.back_to_setup).pack(side=tk.RIGHT, padx=5)

        main_cont = tk.Frame(self.ov, bg="#121212", padx=15, pady=10)
        main_cont.pack(fill="both", expand=True)

        def create_card(parent, title_color, k, is_guest=False):
            card = tk.Frame(parent, bg="#262626", bd=2, relief="ridge", padx=10, pady=8)
            nl = tk.Label(card, text="-", fg="white", bg="#262626", font=("Malgun Gothic", 10, "bold"))
            tl = tk.Label(card, text="READY", fg=title_color, bg="#262626", font=("Malgun Gothic", 9))
            nl.pack(); tl.pack()
            ml = None
            if is_guest:
                ml = tk.Label(card, text="", fg="#ffab00", bg="#262626", font=("Malgun Gothic", 8, "italic"))
                ml.pack()
            else:
                card.bind("<Button-3>", lambda e, x=k: self.toggle_rezzer(x))
                nl.bind("<Button-3>", lambda e, x=k: self.toggle_rezzer(x))
            return card, nl, tl, ml

        for i, k in enumerate(['f1', 'f2', 'f3', 'f4']):
            card, nl, tl, _ = create_card(main_cont, "#BB86FC", k)
            card.grid(row=(i//2)+1, column=i%2, padx=5, pady=5, sticky="nsew")
            self.ov_elements[k] = (card, nl, tl)

        for i, k in enumerate(['f5', 'f6']):
            card, nl, tl, ml = create_card(main_cont, "#03DAC6", k, is_guest=True)
            card.grid(row=4, column=i, padx=5, pady=5, sticky="nsew")
            self.ov_elements[k] = (card, nl, tl, ml)

        main_cont.grid_columnconfigure(0, weight=1)
        main_cont.grid_columnconfigure(1, weight=1)

        # 핫키 등록
        try:
            keyboard.unhook_all()
            for k in self.u.keys():
                keyboard.add_hotkey(k, lambda x=k: self.press_key(x), suppress=False)
        except:
            messagebox.showwarning("Warning", "Hotkey registration failed. Try running as admin.")

        self.update_loop()

    def toggle_rezzer(self, k):
        self.rezzer_alive[k] = not self.rezzer_alive[k]
        self.refresh_ui()

    def press_key(self, k):
        now = datetime.datetime.now()
        if k in ['f1', 'f2', 'f3', 'f4']:
            if self.nt_times[k] and now < self.nt_times[k]: return
            if not self.rezzer_alive[k]: return
            self.nt_times[k] = now + datetime.timedelta(minutes=self.u[k][1])
            for gk in ['f5', 'f6']:
                self.nt_times[gk] = None
                self.beep_flags[gk] = False
        else:
            self.nt_times[k] = now + datetime.timedelta(minutes=self.u[k][1])
            self.beep_flags[k] = False
        self.refresh_ui()

    def update_loop(self):
        if hasattr(self, 'ov') and self.ov.winfo_exists():
            self.refresh_ui()
            self.root.after(1000, self.update_loop)

    def refresh_ui(self):
        now = datetime.datetime.now()
        rez_cools = []
        for rk in ['f1', 'f2', 'f3', 'f4']:
            if not self.u[rk][0].strip(): continue
            card, nl, tl = self.ov_elements[rk]
            if not self.rezzer_alive[rk]:
                card.config(highlightbackground="red", highlightthickness=2)
                tl.config(text="PLAYER DEAD", fg="red")
            else:
                card.config(highlightthickness=0)
                nl.config(fg="white")
                if self.nt_times[rk] and self.nt_times[rk] > now:
                    tl.config(text=self.nt_times[rk].strftime('%H:%M'), fg="#ff5252")
                    rez_cools.append(self.nt_times[rk])
                else:
                    tl.config(text="READY", fg="#4caf50")
                    rez_cools.append(now)

        min_rez = min(rez_cools) if rez_cools else None
        
        o_clip, s_clip = [], []
        for k in ['f1', 'f2', 'f3', 'f4']:
            nm = self.u[k][0].strip()
            if not nm: continue
            if self.nt_times[k] and now < self.nt_times[k]:
                o_clip.append(f"{nm} {self.nt_times[k].strftime('%M')}")
            else:
                o_clip.append(nm)

        for k in ['f5', 'f6']:
            nm = self.u[k][0].strip()
            if not nm: continue
            card, nl, tl, ml = self.ov_elements[k]
            if self.nt_times[k] and now < self.nt_times[k]:
                tl.config(text=self.nt_times[k].strftime('%H:%M'), fg="#ff5252")
                s_clip.append(f"{nm} {self.nt_times[k].strftime('%M')}")
                diff = (self.nt_times[k] - now).total_seconds()
                if 58 <= diff <= 61 and not self.beep_flags[k]:
                    winsound.Beep(1000, 500)
                    self.beep_flags[k] = True
                
                if min_rez is None:
                    ml.config(text="⚠️ 리저 부재", fg="#ff1744")
                else:
                    margin = (self.nt_times[k]-now).total_seconds() - (min_rez-now).total_seconds()
                    if margin < 0: ml.config(text="⚠️ 부활 불가", fg="#ff1744")
                    else: ml.config(text=f"여유: {int(margin//60)}분", fg="#ffab00")
            else:
                tl.config(text="READY", fg="#4caf50")
                ml.config(text="")
                s_clip.append(nm)

        pyperclip.copy(f"현재시간 {now.strftime('%H%M')} / {' '.join(o_clip)} / {' '.join(s_clip)}")
        self.ov_elements['now'].config(text=f"🕒 {now.strftime('%H:%M')}")

    def back_to_setup(self):
        keyboard.unhook_all()
        self.ov.destroy()
        self.root.deiconify()

if __name__ == "__main__":
    app = SkillTimerApp()
    app.root.mainloop()
