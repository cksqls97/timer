import keyboard, pyperclip, datetime, sys

# 이름을 입력받는 대신 기본값을 설정합니다. (나중에 실행파일에서 바꾸면 됩니다)
def main():
    print("=== 클립보드 타이머 실행 중 ===")
    print("Numpad 1~4: 사용자 30분 쿨타임")
    print("Numpad 5: 특별 사용자 13분 쿨타임")
    
    # 기본값 설정 (필요시 이 부분을 수정해서 다시 빌드하세요)
    names = ["AAA", "BBB", "CCC", "DDD"]
    e_name = "EEE"
    
    u = {str(i+1): [names[i], 30, None] for i in range(4)}
    u['5'] = [e_name, 13, None]

    def up():
        n = datetime.datetime.now()
        o = []
        for i in range(1, 5):
            name, cool, next_t = u[str(i)]
            if next_t and n < next_t:
                o.append(f"{name} {next_t.strftime('%H:%M')}")
            else:
                o.append(name)
        
        e_data = u['5']
        ex = f"{e_data[0]} {e_data[2].strftime('%H:%M')}" if e_data[2] and n < e_data[2] else e_data[0]
        res = f"{' '.join(o)} / {ex}"
        pyperclip.copy(res)
        print(f"\r[복사됨]: {res}", end="", flush=True)

    def p(k):
        u[k][2] = datetime.datetime.now() + datetime.timedelta(minutes=u[k][1])
        up()

    # 키 등록
    keyboard.add_hotkey('num 1', lambda: p('1'))
    keyboard.add_hotkey('num 2', lambda: p('2'))
    keyboard.add_hotkey('num 3', lambda: p('3'))
    keyboard.add_hotkey('num 4', lambda: p('4'))
    keyboard.add_hotkey('num 5', lambda: p('5'))

    keyboard.wait()

if __name__ == "__main__":
    main()
