from enum import Flag, auto

class T(Flag):
    ONE = auto()
    TWO = auto()
    THREE = auto()
    FOUR = ONE | TWO | THREE
    FIVE = ONE | TWO | THREE

a = T.ONE
match a:
    case x if x in T.FOUR:
        print("Yes")
    case _:
        print("No")