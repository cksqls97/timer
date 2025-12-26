import keyboard
import pyperclip
import datetime
import sys

def main():
    print("="*30)
    print("   클립보드 스킬 타이머 v1.0")
    print("="*30)
    
    try:
        # 1. 이름 입력 받기
        names = []
        for i in range(4):
            names.append(input(f"{i+1}번 사용자 이름 (30분): "))
        extra_name = input("5번 특별 사용자 이름 (13분): ")
        
        users = {
            '1': [names[0], 30, None],
            '2': [names[1], 30, None],
            '3': [names[2], 30, None],
            '4': [names[3], 30, None],
            '5': [extra_name, 13, None]
        }
        
        print("\n" + "-"*30)
        print("설정 완료! 이제 창을 내려놓으셔도 됩니다.")
        print("NUMPAD 1~5를 누르면 클립보드에 복사됩니다.")
        print("종료: Ctrl + C")
        print("-"*30)

        def update_clipboard():
            now = datetime.datetime.now()
            output = []
            for i in range(1, 5):
                name_val, cool, next_t = users[str(i)]
                if next_t and now < next_t:
                    output.append(f"{name_val} {next_t.strftime('%H:%M')}")
                else:
                    output.append(name_val)
            
            e_name_val, e_cool, e_next_t = users['5']
            extra_part = f"{e_name_val} {e_next_t.strftime('%H:%M')}" if e_next_t and now < e_next_t else e_name_val
            
            final_text = f"{' '.join(output)} / {extra_part}"
            pyperclip.copy(final_text)
            print(f"\r[복사됨]: {final_text}", end="", flush=True)

        def on_press(key):
            users[key][2] = datetime.datetime.now() + datetime.timedelta(minutes=users[key][1])
            update_clipboard()

        # 키 등록
        keyboard.add_hotkey('num 1', lambda: on_press('1'))
        keyboard.add_hotkey('num 2', lambda: on_press('2'))
        keyboard.add_hotkey('num 3', lambda: on_press('3'))
        keyboard.add_hotkey('num 4', lambda: on_press('4'))
        keyboard.add_hotkey('num 5', lambda: on_press('5'))

        keyboard.wait()

    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
    except Exception as e:
        print(f"\n에러 발생: {e}")
        input("\n엔터를 눌러 종료하세요...")

if __name__ == "__main__":
    main()
