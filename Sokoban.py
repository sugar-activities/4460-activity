#!/usr/bin/python
# Sokoban.py
"""
    Copyright (C) 2011  Peter Hewitt

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

"""
import g,pygame,utils,sys,buttons,load_save
try:
    import gtk
except:
    pass
import soko

class Sokoban:

    def __init__(self):
        self.journal=True # set to False if we come in via main()
        self.canvas=None # set to the pygame canvas if we come in via activity.py

    def display(self):
        g.screen.blit(g.sky,g.sky_xy)
        self.soko.draw()
        buttons.draw()
        s=str(g.pattern)+' / '+str(g.puzzles_n)
        utils.text_blit1(g.screen,s,g.font2,(g.sx(.5),g.sy(.5)),utils.BLUE,False)
        if not g.demo_mode and self.soko.complete():
            utils.centre_blit(g.screen,g.smiley,g.smiley_c)

    def do_click(self):
        return self.soko.click()

    def do_button(self,bu):
        if bu=='cyan':
            if not g.demo_mode:
                if g.solved>=g.pattern:
                    g.pattern+=1
                    if g.pattern>g.puzzles_n: g.pattern=1; buttons.off('one')
            self.soko.setup()
        elif bu=='red':
            if not self.soko.complete():
                if g.demo_started:
                    g.demo=not g.demo
                    if g.demo==False: buttons.stay_down('red')
        elif bu=='green': self.soko.start_demo();g.demo_mode=True
        elif bu=='one': g.pattern=1; self.soko.setup(); buttons.off('one')
        elif bu=='reset': self.soko.setup()

    def do_key(self,key):
        if key in g.CROSS:
            if self.do_click(): return
            bu=buttons.check()
            if bu!='': self.do_button(bu)
            return
        if key in g.SQUARE: self.do_button('cyan'); return
        if key==pygame.K_v: g.version_display=not g.version_display; return
        if key in g.RIGHT: self.soko.right(); return
        if key in g.LEFT: self.soko.left(); return
        if key in g.UP: self.soko.up(); return
        if key in g.DOWN: self.soko.down(); return
        if key in g.CIRCLE: self.soko.undo(); return
        if key==pygame.K_1: self.do_button('one'); return

    def buttons_setup(self):
        cx=g.sx(29.5); cy=g.sy(5); dy=g.sy(3)
        buttons.Button('cyan',(cx,cy)); cy+=dy
        buttons.Button('green',(cx,cy)); cy+=dy
        buttons.Button('red',(cx,cy)); cy+=dy
        buttons.Button('reset',(cx,cy)); cy+=dy
        buttons.Button('one',(cx,cy)); cy+=dy
        if g.pattern==1: buttons.off('one')

    def flush_queue(self):
        flushing=True
        while flushing:
            flushing=False
            if self.journal:
                while gtk.events_pending(): gtk.main_iteration()
            for event in pygame.event.get(): flushing=True

    def run(self):
        g.init()
        if not self.journal: utils.load()
        self.soko=soko.Soko()
        load_save.retrieve()
        self.soko.setup()
        self.buttons_setup()
        if self.canvas<>None: self.canvas.grab_focus()
        ctrl=False
        pygame.key.set_repeat(600,120); key_ms=pygame.time.get_ticks()
        going=True
        while going:
            if self.journal:
                # Pump GTK messages.
                while gtk.events_pending(): gtk.main_iteration()

            # Pump PyGame messages.
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    if not self.journal: utils.save()
                    going=False
                elif event.type == pygame.MOUSEMOTION:
                    g.pos=event.pos
                    g.redraw=True
                    if self.canvas<>None: self.canvas.grab_focus()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    g.redraw=True
                    if event.button==1:
                        if self.do_click():
                            pass
                        else:
                            bu=buttons.check()
                            if bu!='': self.do_button(bu); self.flush_queue()
                    if event.button==3:
                        self.soko.undo()
                elif event.type == pygame.KEYDOWN:
                    # throttle keyboard repeat
                    if pygame.time.get_ticks()-key_ms>110:
                        key_ms=pygame.time.get_ticks()
                        if ctrl:
                            if event.key==pygame.K_q:
                                if not self.journal: utils.save()
                                going=False; break
                            else:
                                ctrl=False
                        if event.key in (pygame.K_LCTRL,pygame.K_RCTRL):
                            ctrl=True; break
                        self.do_key(event.key); g.redraw=True
                        self.flush_queue()
                elif event.type == pygame.KEYUP:
                    ctrl=False
            if not going: break
            self.soko.update()
            if g.redraw:
                if g.pattern>1: buttons.on('one')
                self.display()
                if g.version_display: utils.version_display()
                g.screen.blit(g.pointer,g.pos)
                pygame.display.flip()
                g.redraw=False
            g.clock.tick(40)

if __name__=="__main__":
    pygame.init()
    pygame.display.set_mode((1024,768),pygame.FULLSCREEN)
    game=Sokoban()
    game.journal=False
    game.run()
    pygame.display.quit()
    pygame.quit()
    sys.exit(0)
