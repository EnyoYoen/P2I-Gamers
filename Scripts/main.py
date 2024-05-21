"""
Main
"""
from mainwin import MainWin
from loginwin import LoginWin
from registerwin import RegisterWin


if __name__ == "__main__":
    
    queue = []
    while not queue[0] or queue[0] == 'register':
        win = LoginWin(queue)
        win.mainloop()
        if queue[0] == 'register':
            win = RegisterWin(queue) 
            win.mainloop()
    if queue[0] == 'connected':
        win = MainWin()
        win.mainloop()
    

