# LVGL 9 展示型 Demo（ESP32-S3 + MicroPython）

目標：復刻影片（MicroPython + LVGL 9.6 + ESP32-S3）的展示型 GUI，
按鈕 / 滑桿 / 開關 / 弧形儀表 / 頁面轉場動畫。

## 目前狀態

| 項目 | 狀態 |
|---|---|
| `lv_micropython` 原始碼 | ✅ 已 clone 到 `lv_micropython/`（MicroPython 44aa2b1） |
| LVGL 綁定子模組 | ✅ `user_modules/lv_binding_micropython` @032dda4 |
| LVGL 版本 | ⚠️ 綁定目前指向 **v9.3.0**（`c033a98`），要跑 9.6.0 需手動切換（見下） |
| 對應 ESP-IDF | **v5.2.2**（`tools/ci.sh` 指定） |
| 本機 ESP-IDF | ⚠️ 只有 `C:\esp\v6.1`，**不相容**，需另裝 v5.2.2 |
| 韌體編譯 | ❌ 未完成 — Windows 沒有 WSL，MicroPython ESP32 port 不支援原生 Windows 建置 |
| Demo 程式 | ✅ `app/ui.py`（3 頁 + 動畫），語法檢查通過 |
| 畫面驗證 | ❌ 未完成 — 需要硬體或瀏覽器模擬器 |

## 檔案

```
app/
  ui.py        # 全部 UI：首頁儀表板 / 控制項 / 清單，含動畫
  main.py      # 實機入口：ST7789 + CST816T 觸控 + LVGL 主迴圈（腳位需依板子調整）
  sim_run.py   # 瀏覽器模擬器入口（sim.lvgl.io 用）
```

## 硬體建議

| 用途 | 型號 | 重點 |
|---|---|---|
| 首選 | Waveshare ESP32-S3-Touch-LCD-1.69 | ST7789V2 240×280 SPI、CST816T 電容觸控、N16R8 |
| 預算 | Waveshare ESP32-S3-Touch-LCD-1.28 | GC9A01 240×240 圓屏、CST816S |
| 避免 | 2.1" / 4.3" 等 RGB 並排面板 | MicroPython 下難以推到可用 FPS |

## 建置步驟（需要 Linux / WSL2）

```bash
# 1) ESP-IDF 5.2.2（MicroPython 指定的版本）
git clone -b v5.2.2 --recursive https://github.com/espressif/esp-idf.git ~/esp-idf-5.2.2
cd ~/esp-idf-5.2.2 && ./install.sh esp32s3 && . ./export.sh

# 2) 把 LVGL 綁定升到 9.6.0（配合影片）
cd lv_micropython/user_modules/lv_binding_micropython/lvgl
git fetch --depth 1 origin tag v9.6.0 && git checkout v9.6.0
cd -

# 3) 編輯 lv_conf.h：改成 16 位色，並開啟要用的字型
#    LV_COLOR_DEPTH            16
#    LV_FONT_MONTSERRAT_12/14/16/20/24/28  1
sed -i 's/#define LV_COLOR_DEPTH 32/#define LV_COLOR_DEPTH 16/' \
  user_modules/lv_binding_micropython/lv_conf.h

# 4) 編譯
make -C mpy-cross
cd ports/esp32
make BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM_OCT -j4
# 產物：build-ESP32_GENERIC_S3-SPIRAM_OCT/micropython.bin
```

燒錄（Windows 端可用 esptool）：

```powershell
python -m esptool --chip esp32s3 -p COMx -b 460800 write_flash 0 micropython.bin
```

再把 `app/*.py` 用 mpremote 或 Thonny 丟到裝置上，執行 `main.py`。

## 為什麼不用原生 Windows 編譯

- MicroPython `ports/esp32/README.md` 明確建議 Windows 使用者走 WSL。
- 建置需要 host 端 `gcc` 編譯 `mpy-cross`，以及 GNU `make`；本機兩者都沒有。
- 現有 ESP-IDF v6.1 與 MicroPython 期望的 v5.2.2 不相容。

替代方案：用 GitHub Actions（Ubuntu runner）雲端編譯，產物用 `gh run download` 取回。
