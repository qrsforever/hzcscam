#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter as tk

master = tk.Tk()
w1 = tk.Scale(master, from_=0, to=42)
w1.pack()

w2 = tk.Scale(master, from_=0, to=200, orient=tk.HORIZONTAL)
w2.pack()


def my_callback(e):
    print(dir(e.widget))


w1.bind("<Button-1>", my_callback)
master.mainloop()
