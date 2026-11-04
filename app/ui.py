# AIOT-T1 / ESP32-S3  LVGL 9 展示型 Demo
# 同一份 UI 程式碼可跑在：
#   1) PC 瀏覽器模擬器 sim.lvgl.io（import display_driver 之後呼叫 start()）
#   2) ESP32-S3 實機（由 main.py 初始化面板與觸控後呼叫 start()）
# 只用到 LVGL 9.x API，不依賴 9.6 專屬功能，方便在 9.0 模擬器驗證。

import lvgl as lv

# ---------------- 主題色 ----------------
BG = 0x0E1116
CARD = 0x1A1F27
CARD2 = 0x242B36
TXT = 0xE8EDF4
MUTED = 0x7C889A
ACCENT = 0x22D3EE
ACCENT2 = 0xF59E0B
OK = 0x34D399

# 避免 MicroPython GC 回收 LVGL 物件
KEEP = []


def col(h):
    return lv.color_hex(h)


# ---------------- 共用 style ----------------
def _style():
    s = lv.style_t()
    s.init()
    return s


def build_styles():
    st = {}

    s = _style()
    s.set_bg_color(col(CARD))
    s.set_bg_opa(lv.OPA.COVER)
    s.set_radius(14)
    s.set_border_width(0)
    s.set_pad_all(10)
    st["card"] = s

    s = _style()
    s.set_bg_opa(lv.OPA.TRANSP)
    s.set_border_width(0)
    s.set_pad_all(0)
    st["plain"] = s

    s = _style()
    s.set_text_color(col(TXT))
    st["text"] = s

    s = _style()
    s.set_text_color(col(MUTED))
    st["muted"] = s

    s = _style()
    s.set_text_color(col(ACCENT))
    st["accent"] = s

    s = _style()
    s.set_text_color(col(ACCENT2))
    st["accent2"] = s

    s = _style()
    s.set_text_color(col(0x06171B))
    st["on_accent"] = s

    s = _style()
    s.set_bg_color(col(CARD2))
    s.set_bg_opa(lv.OPA.COVER)
    s.set_radius(6)
    s.set_border_width(0)
    st["track"] = s

    s = _style()
    s.set_bg_color(col(ACCENT))
    s.set_bg_opa(lv.OPA.COVER)
    s.set_radius(6)
    s.set_border_width(0)
    st["indic"] = s

    s = _style()
    s.set_bg_opa(lv.OPA.TRANSP)
    s.set_border_width(0)
    s.set_shadow_width(18)
    s.set_shadow_color(col(ACCENT))
    s.set_shadow_opa(lv.OPA._40)
    st["glow"] = s

    for k in list(st):
        KEEP.append(st[k])
    return st


def font(name):
    return getattr(lv, name, None)


# ---------------- 小工具 ----------------
def label(parent, text, st, f=None, color_style=None):
    lb = lv.label(parent)
    lb.set_text(text)
    if f is not None:
        lb.set_style_text_font(f, 0)
    lb.add_style(color_style or st["text"], 0)
    KEEP.append(lb)
    return lb


def base_screen(st):
    scr = lv.obj()
    scr.set_style_bg_color(col(BG), 0)
    scr.set_style_bg_opa(lv.OPA.COVER, 0)
    scr.remove_flag(lv.obj.FLAG.SCROLLABLE)
    KEEP.append(scr)
    return scr


def header(scr, st, title, sub=""):
    h = lv.obj(scr)
    h.set_size(lv.pct(100), 44)
    h.align(lv.ALIGN.TOP_MID, 0, 0)
    h.add_style(st["plain"], 0)
    h.remove_flag(lv.obj.FLAG.SCROLLABLE)

    t = label(h, title, st, font("font_montserrat_20"))
    t.align(lv.ALIGN.LEFT_MID, 10, -5)

    if sub:
        s = label(h, sub, st, font("font_montserrat_12"), st["muted"])
        s.align(lv.ALIGN.LEFT_MID, 10, 11)

    dot = lv.obj(h)
    dot.set_size(8, 8)
    dot.set_style_radius(4, 0)
    dot.set_style_bg_color(col(OK), 0)
    dot.set_style_bg_opa(lv.OPA.COVER, 0)
    dot.set_style_border_width(0, 0)
    dot.align(lv.ALIGN.RIGHT_MID, -12, 0)
    KEEP.append(dot)
    return h


def content(scr, st):
    """內容區：自動避開 header / nav，內容過長可垂直捲動。"""
    body = lv.obj(scr)
    body.set_size(lv.pct(100), lv.pct(100))
    body.add_style(st["plain"], 0)
    body.set_style_pad_left(10, 0)
    body.set_style_pad_right(10, 0)
    body.set_style_pad_top(48, 0)
    body.set_style_pad_bottom(48, 0)
    body.set_flex_flow(lv.FLEX_FLOW.COLUMN)
    body.set_style_pad_row(8, 0)
    body.set_scroll_dir(lv.DIR.VER)
    KEEP.append(body)
    return body


TABS = ("HOME", "CTRL", "LIST")
NAV = {"index": 0}


def nav(scr, st, index):
    bar = lv.obj(scr)
    bar.set_size(lv.pct(100), 44)
    bar.align(lv.ALIGN.BOTTOM_MID, 0, 0)
    bar.add_style(st["plain"], 0)
    bar.remove_flag(lv.obj.FLAG.SCROLLABLE)
    bar.set_flex_flow(lv.FLEX_FLOW.ROW)
    bar.set_flex_align(lv.FLEX_ALIGN.SPACE_EVENLY, lv.FLEX_ALIGN.CENTER,
                       lv.FLEX_ALIGN.CENTER)

    for i, name in enumerate(TABS):
        b = lv.button(bar)
        b.set_size(62, 30)
        b.set_style_radius(8, 0)
        b.set_style_border_width(0, 0)
        b.set_style_bg_opa(lv.OPA.TRANSP, 0)
        if i == index:
            b.add_style(st["glow"], 0)
            b.set_style_bg_opa(lv.OPA.COVER, 0)
            b.set_style_bg_color(col(CARD), 0)
        txt = label(b, name, st, font("font_montserrat_12"),
                    st["accent"] if i == index else st["muted"])
        txt.center()
        b.add_event_cb(lambda e, t=i: goto(t), lv.EVENT.CLICKED, None)
        KEEP.append(b)


# ---------------- 數字動畫 ----------------
def ease_path():
    for n in ("path_ease_out", "path_ease_in_out"):
        p = getattr(lv.anim_t, n, None)
        if p is not None:
            return p
    return None


def repeat_infinite():
    for v in (getattr(lv, "ANIM_REPEAT_INFINITE", None),
              getattr(getattr(lv, "ANIM_REPEAT", None), "INFINITE", None)):
        if v is not None:
            return v
    return 1


def animate(label_obj, start, end, ms=900, fmt="%d"):
    a = lv.anim_t()
    a.init()
    a.set_values(start, end)
    a.set_time(ms)
    p = ease_path()
    if p is not None:
        a.set_path_cb(p)

    def cb(anim, v):
        label_obj.set_text(fmt % int(v))

    a.set_custom_exec_cb(cb)
    a.start()
    KEEP.append(a)
    return a


# ---------------- 頁 1：儀表板 ----------------
def screen_home(st):
    scr = base_screen(st)
    header(scr, st, "AIOT-T1", "ESP32-S3 / LVGL 9")
    body = content(scr, st)

    row = lv.obj(body)
    row.set_size(lv.pct(100), 56)
    row.add_style(st["plain"], 0)
    row.remove_flag(lv.obj.FLAG.SCROLLABLE)
    row.set_flex_flow(lv.FLEX_FLOW.ROW)
    row.set_style_pad_column(8, 0)

    for name, unit, value, cst in (("TEMP", "C", 27, st["accent"]),
                                   ("HUM", "%", 61, st["accent2"])):
        c = lv.obj(row)
        c.set_size(lv.pct(48), lv.pct(100))
        c.add_style(st["card"], 0)
        c.remove_flag(lv.obj.FLAG.SCROLLABLE)
        c.set_flex_grow(1)

        label(c, name, st, font("font_montserrat_12"), st["muted"]).align(
            lv.ALIGN.TOP_LEFT, 0, 0)
        num = label(c, "0", st, font("font_montserrat_24"), cst)
        num.align(lv.ALIGN.BOTTOM_LEFT, 0, -1)
        label(c, unit, st, font("font_montserrat_12"), st["muted"]).align(
            lv.ALIGN.BOTTOM_LEFT, 34, -3)
        animate(num, 0, value, 1200)

    card = lv.obj(body)
    card.set_size(lv.pct(100), 150)
    card.add_style(st["card"], 0)
    card.remove_flag(lv.obj.FLAG.SCROLLABLE)

    arc = lv.arc(card)
    arc.set_size(106, 106)
    arc.align(lv.ALIGN.LEFT_MID, 0, 0)
    arc.set_bg_angles(135, 405)
    arc.set_range(0, 100)
    arc.set_value(0)
    arc.set_rotation(0)
    arc.set_style_arc_width(9, lv.PART.MAIN)
    arc.set_style_arc_width(9, lv.PART.INDICATOR)
    arc.set_style_arc_color(col(CARD2), lv.PART.MAIN)
    arc.set_style_arc_color(col(ACCENT), lv.PART.INDICATOR)
    arc.remove_flag(lv.obj.FLAG.CLICKABLE)

    pct = label(card, "0%", st, font("font_montserrat_20"))
    pct.align_to(arc, lv.ALIGN.CENTER, 0, 0)

    side = lv.obj(card)
    side.set_size(lv.pct(44), lv.pct(100))
    side.align(lv.ALIGN.RIGHT_MID, 0, 0)
    side.add_style(st["plain"], 0)
    side.remove_flag(lv.obj.FLAG.SCROLLABLE)
    side.set_flex_flow(lv.FLEX_FLOW.COLUMN)
    side.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.START,
                        lv.FLEX_ALIGN.START)
    side.set_style_pad_row(2, 0)

    label(side, "LOAD", st, font("font_montserrat_12"), st["muted"])
    load = label(side, "0%", st, font("font_montserrat_28"), st["accent"])
    label(side, "STATUS", st, font("font_montserrat_12"), st["muted"])
    label(side, "RUNNING", st, font("font_montserrat_12"), st["accent2"])

    a = lv.anim_t()
    a.init()
    a.set_values(0, 87)
    a.set_time(1600)
    a.set_playback_time(1200)
    a.set_repeat_count(repeat_infinite())
    p = ease_path()
    if p is not None:
        a.set_path_cb(p)

    def cb(anim, v):
        iv = int(v)
        arc.set_value(iv)
        pct.set_text("%d%%" % iv)
        load.set_text("%d%%" % iv)

    a.set_custom_exec_cb(cb)
    a.start()

    KEEP.extend([a, arc, pct, load, card, side, row])
    return scr


# ---------------- 頁 2：控制項 ----------------
def screen_ctrl(st):
    scr = base_screen(st)
    header(scr, st, "CONTROLS", "slider / switch / buttons")
    body = content(scr, st)

    # 滑桿卡
    c1 = lv.obj(body)
    c1.set_size(lv.pct(100), 76)
    c1.add_style(st["card"], 0)
    c1.remove_flag(lv.obj.FLAG.SCROLLABLE)

    label(c1, "BRIGHTNESS", st, font("font_montserrat_12"), st["muted"]).align(
        lv.ALIGN.TOP_LEFT, 0, 0)
    val = label(c1, "50%", st, font("font_montserrat_16"), st["accent"])
    val.align(lv.ALIGN.TOP_RIGHT, 0, -2)

    sl = lv.slider(c1)
    sl.set_size(lv.pct(100), 8)
    sl.align(lv.ALIGN.BOTTOM_MID, 0, -4)
    sl.set_range(0, 100)
    sl.set_value(50, lv.ANIM.OFF)
    sl.set_style_bg_color(col(CARD2), lv.PART.MAIN)
    sl.set_style_radius(4, lv.PART.MAIN)
    sl.set_style_bg_color(col(ACCENT), lv.PART.INDICATOR)
    sl.set_style_radius(4, lv.PART.INDICATOR)
    sl.set_style_bg_color(col(ACCENT), lv.PART.KNOB)
    sl.set_style_radius(lv.RADIUS.CIRCLE, lv.PART.KNOB)
    sl.set_style_pad_all(6, lv.PART.KNOB)

    def on_slide(e):
        val.set_text("%d%%" % sl.get_value())

    sl.add_event_cb(on_slide, lv.EVENT.VALUE_CHANGED, None)

    # 開關列
    c2 = lv.obj(body)
    c2.set_size(lv.pct(100), 44)
    c2.add_style(st["card"], 0)
    c2.remove_flag(lv.obj.FLAG.SCROLLABLE)

    label(c2, "Wi-Fi", st, font("font_montserrat_14")).align(
        lv.ALIGN.LEFT_MID, 0, 0)
    sw = lv.switch(c2)
    sw.align(lv.ALIGN.RIGHT_MID, 0, 0)
    sw.add_state(lv.STATE.CHECKED)
    sw.set_style_bg_color(col(ACCENT), lv.PART.INDICATOR | lv.STATE.CHECKED)

    # 按鈕列
    row = lv.obj(body)
    row.set_size(lv.pct(100), 40)
    row.add_style(st["plain"], 0)
    row.remove_flag(lv.obj.FLAG.SCROLLABLE)
    row.set_flex_flow(lv.FLEX_FLOW.ROW)
    row.set_style_pad_column(8, 0)

    for txt, filled in (("PING", True), ("RESET", False)):
        b = lv.button(row)
        b.set_size(lv.pct(48), lv.pct(100))
        b.set_flex_grow(1)
        b.set_style_radius(10, 0)
        b.set_style_border_width(0, 0)
        if filled:
            b.set_style_bg_color(col(ACCENT), 0)
            b.set_style_bg_opa(lv.OPA.COVER, 0)
        else:
            b.set_style_bg_color(col(CARD2), 0)
            b.set_style_bg_opa(lv.OPA.COVER, 0)
        lb = label(b, txt, st, font("font_montserrat_14"),
                   st["on_accent"] if filled else st["text"])
        lb.center()
        b.add_event_cb(lambda e: None, lv.EVENT.CLICKED, None)

    # 進度條
    bar = lv.bar(body)
    bar.set_size(lv.pct(100), 8)
    bar.set_style_bg_color(col(CARD2), lv.PART.MAIN)
    bar.set_style_radius(4, lv.PART.MAIN)
    bar.set_style_bg_color(col(ACCENT2), lv.PART.INDICATOR)
    bar.set_style_radius(4, lv.PART.INDICATOR)

    ba = lv.anim_t()
    ba.init()
    ba.set_values(0, 100)
    ba.set_time(2600)
    ba.set_repeat_count(repeat_infinite())
    p = ease_path()
    if p is not None:
        ba.set_path_cb(p)
    ba.set_custom_exec_cb(lambda a, v: bar.set_value(int(v), lv.ANIM.OFF))
    ba.start()

    KEEP.extend([c1, c2, row, sl, val, sw, bar, ba])
    return scr


# ---------------- 頁 3：清單 ----------------
ITEMS = ("Sensor A", "Sensor B", "Relay 1", "Relay 2", "MQTT",
         "Wi-Fi", "BLE", "OTA", "Log", "About")


def screen_list(st):
    scr = base_screen(st)
    header(scr, st, "DEVICES", "%d items" % len(ITEMS))
    body = content(scr, st)

    for name in ITEMS:
        r = lv.obj(body)
        r.set_size(lv.pct(100), 38)
        r.add_style(st["card"], 0)
        r.remove_flag(lv.obj.FLAG.SCROLLABLE)

        label(r, name, st, font("font_montserrat_14")).align(
            lv.ALIGN.LEFT_MID, 0, 0)
        cb = lv.checkbox(r)
        cb.align(lv.ALIGN.RIGHT_MID, 0, 0)
        if name in ("MQTT", "Wi-Fi", "BLE"):
            cb.add_state(lv.STATE.CHECKED)
        KEEP.append(cb)

    return scr


# ---------------- 導覽 ----------------
SCREENS = []


def goto(index):
    if index >= len(SCREENS):
        return
    prev = NAV["index"]
    if index == prev:
        return
    anim = (lv.SCREEN_LOAD_ANIM.MOVE_LEFT if index > prev
            else lv.SCREEN_LOAD_ANIM.MOVE_RIGHT)
    NAV["index"] = index
    lv.screen_load_anim(SCREENS[index], anim, 260, 0, False)


def start():
    st = build_styles()

    for i, maker in enumerate((screen_home, screen_ctrl, screen_list)):
        scr = maker(st)
        NAV["index"] = i
        nav(scr, st, i)
        SCREENS.append(scr)

    NAV["index"] = 0
    lv.screen_load(SCREENS[0])
