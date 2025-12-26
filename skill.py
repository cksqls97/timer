import keyboard, pyperclip, datetime, sys

def main():
    try:
        names = [input(f"{i+1}번 이름: ") for i in range(4)]
        e_name = input("5번(13분) 이름: ")
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
            
            e_name_p, e_cool, e_next_t = u['5']
            ex = f"{e_name_p} {e_next_t.strftime('%H:%M')}" if e_next_t and n < e_next_t else e_name_p
            res = f"{' '.join(o)} / {ex}"
            pyperclip.copy(res)
            print(f"\r[복사됨]: {res}", end="", flush=True)

        def p(k):
            u[k][2] = datetime.datetime.now() + datetime.timedelta(minutes=u[k][1])
            up()

        for i in range(1, 6):
            keyboard.add_hotkey(f'num {i}', lambda k=str(i): p(k))

        print("\n작동 시작 (NUMPAD 1~5) / 종료하려면 Ctrl+C")
        keyboard.wait()
    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    main()
