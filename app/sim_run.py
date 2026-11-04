# 在瀏覽器模擬器 sim.lvgl.io 直接跑這份 UI
# 用法：把這個檔案的內容（連同 ui.py）貼進模擬器編輯器，按 Run
import display_driver  # 模擬器提供的顯示器/滑鼠驅動，只有 sim.lvgl.io 有
import ui

ui.start()
