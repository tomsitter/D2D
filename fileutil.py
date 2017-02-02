# Utility Functions
import os
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import Tk


def getfile(initialdir=None, title=None):
    Tk().withdraw()
    
    filename = askopenfilename(initialdir=initialdir or os.path.expanduser("~"),
                               title=title or 'Select report file')
    
    return filename


def createfile(initialdir=None, title=None):
	Tk().withdraw()

	filename = asksaveasfilename(initialdir=initialdir or os.path.expanduser("~"),
								 title=title or "Save output to file...")

	return filename