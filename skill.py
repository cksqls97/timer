def update_display():
        now = datetime.datetime.now()
        # 생존해 있는 비숍들의 다음 사용 가능 시간(이미 지났으면 현재시간으로 간주) 리스트
        alive_times = sorted([nt_times[rk] if nt_times[rk] and nt_times[rk] > now else now 
                             for rk in ['f1','f2','f3','f4'] if resurrection_alive[rk]])
        guest_deadline = nt_times['f5'] if nt_times['f5'] else now

        for rk in ['f1','f2','f3','f4']:
            c, nl, tl, msg = ov_elements[rk]
            nl.config(text=u[rk], fg="white")
            
            # [1] 사망 상태(D.O)일 때
            if not resurrection_alive[rk]:
                c.config(highlightbackground="#441111", bg="#150A0A")
                for w in [nl, tl, msg]: w.config(bg="#150A0A")
                tl.config(text="D.O", fg="#552222") # 시간 표기 대신 D.O
                msg.config(text="")
                continue
            
            # [2] 정상 상태일 때 배경 초기화
            c.config(bg="#1E1E1E"); nl.config(bg="#1E1E1E"); tl.config(bg="#1E1E1E"); msg.config(bg="#1E1E1E")
            
            # [3] 타이머 작동 중일 때 (미래에 만료될 시간이 있을 때)
            if nt_times[rk] and nt_times[rk] > now:
                tl.config(text=nt_times[rk].strftime('%H:%M'), fg="#FF5252")
                msg.config(text="")
                c.config(highlightbackground="#333", highlightthickness=1)
            
            # [4] 타이머 만료 또는 초기 상태 (READY)
            else:
                tl.config(text="READY", fg="#4CAF50") # 시간 대신 READY 표시
                warn_texts = []
                
                # --- 경고 로직 (기존 유지) ---
                tmp_u = sorted(alive_times)
                try:
                    idx = tmp_u.index(now); tmp_u[idx] = now + datetime.timedelta(minutes=30)
                    tmp_u = sorted(tmp_u)
                    if len(tmp_u) >= 2: tmp_u[0] = tmp_u[0] + datetime.timedelta(minutes=30)
                    if min(tmp_u) > guest_deadline: warn_texts.append("사용 시 불가")
                except: pass
                
                tmp_d = sorted(alive_times)
                try:
                    tmp_d.remove(now)
                    if tmp_d:
                        tmp_d[0] = tmp_d[0] + datetime.timedelta(minutes=30)
                        if min(tmp_d) > guest_deadline: warn_texts.append("사망 시 불가")
                    else: warn_texts.append("사망 시 불가")
                except: pass
                
                # 색상 강조 로직
                if "사망 시 불가" in warn_texts:
                    msg.config(text="\n".join(warn_texts), fg="#FF5252")
                    c.config(highlightbackground="#FF1744", highlightthickness=2)
                elif "사용 시 불가" in warn_texts:
                    msg.config(text="\n".join(warn_texts), fg="#FFD600")
                    c.config(highlightbackground="#FFD600", highlightthickness=2)
                else:
                    msg.config(text="")
                    c.config(highlightbackground="#333", highlightthickness=1)
