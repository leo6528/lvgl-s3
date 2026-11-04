# 供 LVGL MicroPython WASM 模擬器（127.0.0.1 本機版 sim.lvgl.io）使用的顯示驅動。
# 只有 PC 模擬器會 import 這個檔案；實機請用 main.py（SPI ST7789 + I2C 觸控）。
#
# 原理：WASM 版的 LVGL 內建 SDL 驅動，會把畫面直接畫到網頁的 <canvas>，
# 所以這裡只要 lv.init() + lv.sdl_window_create()。
#
# 模擬器沒有 machine.Timer，因此用 micropython.schedule() 自我重排程，
# 讓瀏覽器既有的 handle_pending 迴圈每 5ms 幫我們跑一次 lv.timer_handler()。

import micropython

import lvgl as lv

# 與實際面板相同解析度，模擬器看到的排版就等於實機排版
WIDTH, HEIGHT = 240, 280

TICK_MS = 20

_state = {"running": False}


def init_display():
    if not lv.is_initialized():
        lv.init()

    disp = lv.sdl_window_create(WIDTH, HEIGHT)

    # 滑鼠當觸控用，方便在模擬器上點按鈕、拉滑桿
    try:
        lv.sdl_mouse_create()
    except AttributeError:
        pass

    return disp


def _tick(_arg):
    try:
        lv.tick_inc(TICK_MS)
        lv.timer_handler()
    except Exception:
        pass
    if _state["running"]:
        try:
            micropython.schedule(_tick, 0)
        except Exception:
            pass


def run_event_loop():
    """啟動刷新迴圈（模擬器用）。實機由 main.py 的 while 迴圈負責。"""
    _state["running"] = True
    micropython.schedule(_tick, 0)


def stop_event_loop():
    _state["running"] = False


init_display()
