# ESP32-S3 實機入口：初始化面板 + 觸控，然後啟動 UI
# 目標板：Waveshare ESP32-S3-Touch-LCD-1.69（ST7789V2 240x280 + CST816T 電容觸控）
# 注意：腳位請對照你買的板子 wiki 修改 CONFIG；不同批次可能不同。

import time
import machine
import lvgl as lv

import ui

# ---------------- 腳位設定（依實際板子修改） ----------------
CONFIG = {
    "spi_id": 1,
    "sck": 12,
    "mosi": 11,
    "cs": 10,
    "dc": 9,
    "rst": 8,
    "bl": 46,
    # CST816T（I2C）
    "i2c_id": 0,
    "scl": 7,
    "sda": 6,
    "touch_int": 5,
    "touch_rst": 4,
    "width": 240,
    "height": 280,
}

TOUCH_ADDR = 0x15  # CST816T 預設位址（部分模組為 0x15 / 0x5D）


class St7789_240x280:
    """借用 lv_binding 內建的純 Python ST7789 驅動，只放寬解析度限制。"""

    def __init__(self, cfg, st7789_classes):
        St77xx_hw, St77xx_lvgl = st7789_classes
        spi = machine.SPI(
            cfg["spi_id"],
            baudrate=40_000_000,
            polarity=0,
            phase=0,
            sck=machine.Pin(cfg["sck"]),
            mosi=machine.Pin(cfg["mosi"]),
        )
        res = (cfg["width"], cfg["height"])

        class _Panel(St77xx_hw, St77xx_lvgl):
            def __init__(self):
                St77xx_hw.__init__(
                    self,
                    cs=machine.Pin(cfg["cs"]),
                    dc=machine.Pin(cfg["dc"]),
                    spi=spi,
                    res=res,
                    suppRes=[res],
                    model=None,
                    suppModel=None,
                    rst=machine.Pin(cfg["rst"]),
                    bl=machine.Pin(cfg["bl"]),
                    rot=1,
                )
                St77xx_lvgl.__init__(self, doublebuffer=True, factor=4)

        self.panel = _Panel()


def init_touch(cfg, disp):
    i2c = machine.I2C(
        cfg["i2c_id"],
        scl=machine.Pin(cfg["scl"]),
        sda=machine.Pin(cfg["sda"]),
        freq=400_000,
    )
    if not 0 <= TOUCH_ADDR <= 0x7F:
        return None
    reg = bytearray(6)

    indev = lv.indev_create()
    indev.set_type(lv.INDEV_TYPE.POINTER)
    indev.set_display(disp)

    state = {"last": (0, 0)}

    def read_cb(drv, data):
        try:
            i2c.readfrom_mem_into(TOUCH_ADDR, 0x02, reg)
        except OSError:
            data.continue_reading = False
            return
        fingers = reg[1] & 0x0F
        x = ((reg[2] & 0x0F) << 8) | reg[3]
        y = ((reg[4] & 0x0F) << 8) | reg[5]
        if fingers:
            state["last"] = (x, y)
            data.point.x = x
            data.point.y = y
            data.state = lv.INDEV_STATE.PRESSED
        else:
            data.point.x = state["last"][0]
            data.point.y = state["last"][1]
            data.state = lv.INDEV_STATE.RELEASED
        data.continue_reading = True

    indev.set_read_cb(read_cb)
    return indev


def main():
    lv.init()

    from st77xx import St77xx_hw, St77xx_lvgl

    drv = St7789_240x280(CONFIG, (St77xx_hw, St77xx_lvgl))
    disp = lv.display_get_default()
    init_touch(CONFIG, disp)

    ui.start()

    while True:
        lv.timer_handler()
        time.sleep_ms(5)


main()
