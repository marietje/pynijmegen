from pprint import pformat
from mirte.core import Module
from joyce.base import JoyceChannel

import gtk
import cairo
import random
import gobject
import subprocess
import gtk.gdk as gdk


# TODO We want to merge this with pymarietje, when it has been converted to
#      the new protocol.
class MarietjeClientChannel(JoyceChannel):
    def __init__(self, server, *args, **kwargs):
        super(MarietjeClientChannel, self).__init__(*args, **kwargs)
        self.s = server
        self.l = self.s.l
        self.msg_map = {
                'welcome': self.msg_welcome,
                'requests': self.msg_requests,
                'playing': self.msg_playing,
                }
    def handle_message(self, data):
        typ = data.get('type')
        if typ in self.msg_map:
            self.msg_map[typ](data)
        else:
            self.l.warn('Unknown message type: %s' % repr(typ))
    def msg_welcome(self, data):
        self.l.info('Welcome %s' % pformat(data))
        self.send_message({'type': 'follow',
                           'which': ['playing', 'requests']})
    def msg_playing(self, data):
        self.s.sw.set_text('Marietje' if not data['playing']['byKey']
                                    else data['playing']['byKey'],
                data['playing']['media']['artist'] if data['playing']['media']
                        else '(nothing playing)',
                data['playing']['media']['title'] if data['playing']['media']
                        else '')
    def msg_requests(self, data):
        pass

class ScrollWidget(gtk.DrawingArea):
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK |
                        gtk.gdk.EXPOSURE_MASK)
        self.connect('expose_event', self.on_expose)
        self.connect('button_press_event', self.on_button_press)
        self.connect('scroll_event', self.on_scroll)
	
    def on_scroll(self, widget, event):
        if event.direction == gdk.SCROLL_UP:
            subprocess.call(['amixer', 'set', 'Master', '1%+'],
                    stdout=subprocess.PIPE)
        elif event.direction == gdk.SCROLL_DOWN:
            subprocess.call(['amixer', 'set', 'Master', '1%-'],
                    stdout=subprocess.PIPE)

    def on_button_press(self, widget, event):
        if event.button == 1:
            subprocess.call(['amixer', 'set', 'Master', '1%+'],
                    stdout=subprocess.PIPE)
        elif event.button == 2:
            subprocess.call(['amixer', 'set', 'Master', 'toggle'],
                    stdout=subprocess.PIPE)
            subprocess.call(['amixer', 'set', 'PCM', 'unmute'],
                    stdout=subprocess.PIPE)
            subprocess.call(['amixer', 'set', 'Headphone','unmute'],
                   stdout=subprocess.PIPE)
        elif event.button == 3:
            subprocess.call(['amixer', 'set', 'Master', '1%-'],
                    stdout=subprocess.PIPE)
    
    def on_expose(self, widget, event):
        c = widget.window.cairo_create()
        c.rectangle(event.area.x, event.area.y,
                    event.area.width, event.area.height)
        c.clip()
        self.draw(c)
        return False

    def set_text(self, by, artist, title):
        self.text = (by, artist, title)
        print self.text
        self.update()

    def draw(self, c):
        SIZES = (64, 96, 64)
        rect = self.get_allocation()
        c.rectangle(rect.x, rect.y, rect.width, rect.height)
        c.set_source_rgb(0xbe/255.0,0x31/255.0,0x1a/255.0)
        c.fill()
        c.set_source_rgb(1,1,1)
        heights = list()
        bearings = list()
        corrected_text = []
        for i, bit in enumerate(self.text):
            c.set_font_size(SIZES[i])
            first_try = True
            ellipsis = u'\u2026'
            while True:
                if first_try:
                    exts = c.text_extents(bit)
                else:
                    exts = c.text_extents(bit + ellipsis)
                if exts[2] < rect.width - 40 or not bit:
                    break
                first_try = False
                bit = bit[:-1]
            if i == 0:
                heights.append(-exts[1] + 45)
            else:
                heights.append(-exts[1] + 50)
            bearings.append(exts[1])
            if first_try:
                corrected_text.append(bit)
            else:
                corrected_text.append(bit + ellipsis)
        off = (rect.height - sum(heights)) / 2
        for i, bit in enumerate(corrected_text):
            c.set_font_size(SIZES[i])
            c.move_to(40, off - bearings[i])
            c.show_text(bit)
            c.stroke()
            off += heights[i]
        c.stroke()

    
    def update(self):
        if self.window is None:
            return 
        alloc = self.get_allocation()
        rect = gdk.Rectangle(alloc.x, alloc.y,
                             alloc.width, alloc.height)
        self.window.invalidate_rect(rect, True)
        self.window.process_updates(True)

class PyNijmegen(Module):
    def __init__(self, settings, l):
        super(PyNijmegen, self).__init__(settings, l)
        def _channel_class(*args, **kwargs):
            return MarietjeClientChannel(self, *args, **kwargs)
        self.channel = self.joyceClient.create_channel(
                        channel_class=_channel_class)
        w = self.w = gtk.Window()
        sw = self.sw = ScrollWidget()
        sw.set_text('?', '?', '?')
        w.add(sw)
        w.connect("destroy", gtk.main_quit)
    
    def run(self):
        # TODO Use the GtkMainLoop of maried.gstreamer
        self.w.show_all()
        self.w.fullscreen()
        gobject.threads_init()
        self.loop = gobject.MainLoop()
        self.loop.run()

    def update_it(self):
        self.sw.set_text(by, artist, title)
        return True

# vim: et:sta:bs=2:sw=4:
