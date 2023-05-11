#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk

import gi

gi.require_version("Gst", "1.0")
gi.require_version('Gtk', '3.0')
# from gi.repository import Gst

gst_pipe_format = "gst-launch-1.0 v4l2src device=/dev/video0 io-mode=4 brightness={brightness} contrast=0 hue=0 saturation=0 ! videoscale ! video/x-raw, width=640, height=480, framerate=15/1 ! videoconvert ! clockoverlay time-format=\"%Y/%m/%d-%H:%M:%S\" halignment=right valignment=top font-desc=\"normal 12\" ! textoverlay text=\"54e1ad3f10d3\" halignment=left valignment=top font-desc=\"normal 12\" ! autovideosink"

master = tk.Tk(className='test')
master.geometry('600x480')

mainW = ttk.Frame(master, width=480, height=480)
mainW.pack()


w_brightness = tk.Scale(mainW, from_=-64, to=64)
w_brightness.pack()

def my_callback():
    print(gst_pipe_format)
    print(w_brightness.get())
    pipeline = gst_pipe_format.format(brightness=w_brightness.get())
    print(pipeline)


w_brightness.bind("<ButtonRelease-1>", lambda event: my_callback())

Gst.init(None)
Gst.from_pipeline()

master.mainloop()

# t1 = tk.Text(mainW, width=211, height=131)
# t1.pack()

# w1 = tk.Scale(mainW, from_=0, to=200)
# w1.pack(ipady=100)

# w2 = tk.Scale(mainW, from_=0, to=200, orient=tk.HORIZONTAL)
# w2.pack()


# Gst.init(None)
# player = Gst.Pipeline.new("player")
# source = Gst.ElementFactory.make("videotestsrc", "video-source")
# sink = Gst.ElementFactory.make("xvimagesink", "video-output")
# caps = Gst.Caps.from_string("video/x-raw, width=320, height=230")
# filter = Gst.ElementFactory.make("capsfilter", "filter")
# filter.set_property("caps", caps)
# player.add(source)
# player.add(filter)
# player.add(sink)
# source.link(filter)
# filter.link(sink)
# player.set_state(Gst.State.PLAYING)


# def my_callback(w1, w2):
    # # print(dir(e.widget))
    # # print(e.widget.get())
    # player.set_state(Gst.State.NULL)
    # new_caps = Gst.Caps.from_string(f"video/x-raw, width={w1.get()}, height={w2.get()}")
    # filter.set_property('caps', new_caps)
    # player.set_state(Gst.State.PLAYING)


# w1.bind("<ButtonRelease-1>", lambda event: my_callback(w1, w2))
# w2.bind("<ButtonRelease-1>", lambda event: my_callback(w1, w2))

# master.mainloop()
