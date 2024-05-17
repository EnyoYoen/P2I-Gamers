"""
Main
"""
from mainwin import MainWin
from loginwin import LoginWin


if __name__ == "__main__":
    win = LoginWin()
    win.mainloop()
    if win:
        win = MainWin()
        win.mainloop()
    

