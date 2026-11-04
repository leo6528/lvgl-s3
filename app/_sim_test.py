import micropython
import lvgl as lv

lv.init()
lv.sdl_window_create(240, 280)

scr = lv.obj()
scr.set_style_bg_color(lv.color_hex(0x101820), 0)

arc = lv.arc(scr)
arc.set_size(140, 140)
arc.center()
arc.set_bg_angles(135, 405)
arc.set_range(0, 100)
arc.set_value(40)
arc.set_style_arc_width(10, lv.PART.MAIN)
arc.set_style_arc_width(10, lv.PART.INDICATOR)
arc.set_style_arc_color(lv.color_hex(0x242B36), lv.PART.MAIN)
arc.set_style_arc_color(lv.color_hex(0x22D3EE), lv.PART.INDICATOR)

lbl = lv.label(scr)
lbl.set_text("SCHED")
lbl.set_style_text_color(lv.color_hex(0xE8EDF4), 0)
lbl.align_to(arc, lv.ALIGN.CENTER, 0, 0)

lv.screen_load(scr)

STATE = {"n": 0}


def tick(_arg):
    try:
        STATE["n"] += 1
        arc.set_value(STATE["n"] % 100)
        lbl.set_text("TICK %d" % STATE["n"])
        lv.tick_inc(20)
        lv.timer_handler()
    except Exception as e:
        pass
    try:
        micropython.schedule(tick, 0)
    except Exception:
        pass


micropython.schedule(tick, 0)
