"""
Main
"""
from mainwin import MainWin
from loginwin import LoginWin
from registerwin import RegisterWin


if __name__ == "__main__":
    
    queue = []
    user_id = None
    while not queue or queue[0] == 'register':
        win = LoginWin(queue)
        win.mainloop()
        user_id = win.user_id
        if queue[0] == 'register':
            reg_win = RegisterWin(queue) 
            reg_win.mainloop()
            user_id = reg_win.user_id
    if queue[0] == 'connected':
        win = MainWin(user_id)
        win.mainloop()
    

