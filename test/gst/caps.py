
#!/usr/bin/env python

import os
import gi
gi.require_version("Gst", "1.0")
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, Gtk


class GTK_Main_1:

    def __init__(self):
        window = Gtk.Window()
        window.set_title("Videotestsrc-Player")
        window.set_default_size(300, -1)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        vbox = Gtk.VBox()
        window.add(vbox)
        self.button = Gtk.Button(label = "Start")
        self.button.connect("clicked", self.start_stop)
        self.btn_reset_resolution = Gtk.Button(label = "Reset Resolution")
        self.btn_reset_resolution.connect("clicked", self.reset_resolution)
        vbox.add(self.button)
        vbox.add(self.btn_reset_resolution)
        window.show_all()

        self.player = Gst.Pipeline.new("player")
        source = Gst.ElementFactory.make("videotestsrc", "video-source")
        sink = Gst.ElementFactory.make("xvimagesink", "video-output")
        caps = Gst.Caps.from_string("video/x-raw, width=320, height=230")
        filter = Gst.ElementFactory.make("capsfilter", "filter")
        filter.set_property("caps", caps)
        self.player.add(source)
        self.player.add(filter)
        self.player.add(sink)
        source.link(filter)
        filter.link(sink)

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

        bus.enable_sync_message_emission()
        bus.connect("sync-message::element", self.on_sync_message)

    def reset_resolution(self, w):
        print(w, self.btn_reset_resolution)
        self.player.set_state(Gst.State.NULL)

        filter = self.player.get_by_name("filter")
        print(filter)
        # ------------- not work --------------
        caps = filter.get_property("caps")
        print('caps:', dir(caps))
        # print(caps.to_string())
        # print('-'*100)
        # structure = caps.steal_structure(0)
        structure = caps.get_structure(0)
        print('structure:', structure, structure.get_name())
        # print("1:", structure, structure.name)
        print('structure:', dir(structure))
        # if structure.has_field('width'):
        #     print(structure.get_value('width'))
        #     structure.set_value('width', 640)
        #     structure.set_value('height', 320)
        #     print(structure.get_value('width'))
        #     # caps.merge_structure(structure)
        #     print(caps.to_string())
        # ------------- not work --------------

        new_caps = Gst.Caps.from_string("video/x-raw, width=640, height=460")
        filter.set_property('caps', new_caps)
        self.player.set_state(Gst.State.PLAYING)

    def start_stop(self, w):
        if self.button.get_label() == "Start":
            self.button.set_label("Stop")
            self.player.set_state(Gst.State.PLAYING)
        else:
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print("on message error: %s" % err, debug)
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")

    def on_sync_message(self, bus, message):
        print("on sync message:", message.get_structure().get_name())
        if message.get_structure().get_name() == 'prepare-window-handle':
            message.src.set_property('force-aspect-ratio', True)

class GTK_Main_2:
    def __init__(self):
        # initialization windows
        Gtk.Window()
        window = Gtk.Window()
        window.set_title("Resolutionchecker")
        window.set_default_size(300, -1)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        vbox = Gtk.VBox()
        window.add(vbox)
        self.entry = Gtk.Entry()
        vbox.pack_start(child = self.entry, expand = False, fill = True, padding = 0)
        self.button = Gtk.Button(label = "Check")
        self.button.connect("clicked", self.start_stop)
        vbox.add(self.button)
        window.show_all()

        self.player = Gst.Pipeline.new("player")
        source = Gst.ElementFactory.make("filesrc", "file-source")
        decoder = Gst.ElementFactory.make("decodebin", "decoder")
        decoder.connect("pad-added", self.decoder_callback)
        self.fakea = Gst.ElementFactory.make("fakesink", "fakea")
        self.fakev = Gst.ElementFactory.make("fakesink", "fakev")
        self.player.add(source)
        self.player.add(decoder)
        self.player.add(self.fakea)
        self.player.add(self.fakev)
        source.link(decoder)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

    def start_stop(self, w):
        filepath = self.entry.get_text().strip()
        if os.path.isfile(filepath):
            filepath = os.path.realpath(filepath)
            self.player.set_state(Gst.State.NULL)
            self.player.get_by_name("file-source").set_property("location", filepath)
            self.player.set_state(Gst.State.PAUSED)

    def on_message(self, bus, message):
        print(message)
        typ = message.type
        if typ == Gst.MessageType.STATE_CHANGED:
            if message.parse_state_changed()[1] == Gst.State.PAUSED:
                decoder = self.player.get_by_name("decoder")
                for pad in decoder.srcpads:
                    caps = pad.query_caps(None)
                    structure_name = caps.to_string()
                    width = caps.get_structure(0).get_int('width')
                    height = caps.get_structure(0).get_int('height')
                    if structure_name.startswith("video") and len(str(width)) < 6:
                        print("Width:%d, Height:%d" %(width, height))
                        self.player.set_state(Gst.State.NULL)
                        break
        elif typ == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print("Error: %s" % err, debug)
            self.player.set_state(Gst.State.NULL)

    def decoder_callback(self, decoder, pad):
        caps = pad.query_caps(None)
        structure_name = caps.to_string()
        print("structure_name = ", structure_name)
        if structure_name.startswith("video"):
            fv_pad = self.fakev.get_static_pad("sink")
            pad.link(fv_pad)
        elif structure_name.startswith("audio"):
            fa_pad = self.fakea.get_static_pad("sink")
            pad.link(fa_pad)

Gst.init(None)        
GTK_Main_1()
Gtk.main()
