"""
Main program

This script serves as the entry point for the application. It contains the main logic for handling user authentication and launching the main window.

The script imports the following modules:
- mainwin: Contains the MainWin class for the main application window.
- loginwin: Contains the LoginWin class for the login window.
- registerwin: Contains the RegisterWin class for the registration window.

The script initializes a queue to store user actions and a user_id variable to store the current user's ID.

The main logic of the script is as follows:
1. Enter a loop until the queue is empty or the first item in the queue is 'register'.
2. Create an instance of the LoginWin class and start the main event loop.
3. Retrieve the user_id from the LoginWin instance.
4. If the first item in the queue is 'register', create an instance of the RegisterWin class and start the main event loop.
5. Retrieve the user_id from the RegisterWin instance.
6. If the first item in the queue is 'connected', create an instance of the MainWin class with the user_id and start the main event loop.

Note: The script assumes that the imported modules and classes exist in the specified file paths.
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



