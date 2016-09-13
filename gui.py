#! python3

import tkinter as tk
from tkinter.filedialog import askopenfilename

class Application(tk.Frame):
    self.numer = {}
    self.denom = {}
    
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.load_numer = tk.Button(self,
                                    text = "Load Numerator",
                                    command = self.load_file)
        self.load_denom = tk.Button(self,
                                    text = "Load Denominator",
                                    command = self.load_file)
        self.load_denom.pack(side="bottom")

    def load_file(self):
            filename = askopenfilename(title="Select a file")
            return filename

root = tk.Tk()
app = Application(master=root)
app.mainloop()
    
