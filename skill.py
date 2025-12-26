import keyboard, pyperclip, datetime
names = [input(f"{i+1}번 이름: ") for i in range(4)]
e_name = input("5번(13분) 이름: ")
u = {str(i+1): [names[i], 30, None] for i in range(4)}
u['5'] = [e_name, 13, None]
def up():
    n = datetime.datetime.now()
    o = [f"{x[0]} {x[2].strftime('%H:%M')}" if x[2] and n < x[2] else x[0] for x in [u[str(i)] for i in range(1, 5)]]
    ex = f"{u['5'][0]} {u['5'][2].strftime('%H:%M')}" if u['5'][2] and n < u['5'][2] else u['5'][0]
    res = f"{' '.join(o)} / {ex}"
    pyperclip.copy(res)
    print(f"\r[복사됨]: {res}", end="")
def p(k):
    u[k][2] = datetime.datetime.now() + datetime.timedelta(minutes=u[k][1])
    up()
for i in range(1, 6):
    keyboard.add_hotkey(f'num {i}', lambda k=str(i): p(k))
keyboard.wait()
