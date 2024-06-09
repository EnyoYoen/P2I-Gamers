import time
import tkinter as tk

class calibration_popup(tk.Toplevel) :
    def __init__(self) :
        super().__init__()
        self.geometry('600x100')
        self.start_time_calib = time.time()
        self.text = tk.Label(self, text='')
        self.text.pack(anchor=tk.CENTER)
        self.update()
        self.center_window()
    def update(self) :
        self.remaining_time = int(6 - time.time() + self.start_time_calib)
        if self.remaining_time > 0:
            self.text.config(text=f'Calibration commencée... \nVeuillez bouger tous les doigts de la position maximale à minimale pendant 5 secondes\n{self.remaining_time}s')
            self.after(100, self.update)
        elif self.remaining_time > -1 and self.remaining_time <= 0 :
            self.text.config(text='Calibration complète!')
            self.after(100, self.update)
        else :
            self.destroy()
    def center_window(self):
        #self.update_idletasks()
        width = 600
        height = 100
        x = (self.winfo_screenwidth() // 2)
        y = (self.winfo_screenheight() // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
