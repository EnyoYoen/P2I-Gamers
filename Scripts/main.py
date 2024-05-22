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
<<<<<<< HEAD
        print(win.user)
        win = MainWin(win.user)
=======
        win = MainWin(user_id)
>>>>>>> 8f98c3419b3c3a8051de840bc93a5c6cc3295f6b
        win.mainloop()



