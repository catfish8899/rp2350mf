import time
import sys
import random
import config
from core.controller import RP2350Controller
from core.vision import find_image_on_screen
from core.action import smooth_move_to
from core.input_engine import set_clipboard_text, hardware_type_from_clipboard

def wait_and_find_image(image_path, timeout):
    """辅助函数：在规定时间内循环寻找图片"""
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        coords = find_image_on_screen(image_path, config.MATCH_THRESHOLD)
        if coords:
            return coords
        time.sleep(0.5)
        sys.stdout.write(".")
        sys.stdout.flush()
    return None

def main_loop():
    # 1. 初始化硬件控制器
    hw_controller = RP2350Controller(config.COM_PORT, config.BAUD_RATE)
    print(f"\n[系统启动] 自动化任务开始执行...")
    
    try:
        # ==========================================
        # 步骤 1：找图1 -> 单击 -> 剪贴板 + Ctrl+V 粘贴
        # ==========================================
        print(f"\n[步骤 1] 正在寻找图片 1: '{config.IMAGE_1_PATH}' ...")
        coords_1 = wait_and_find_image(config.IMAGE_1_PATH, config.TIMEOUT_SECONDS)
        
        if not coords_1:
            print(f"\n[失败] 步骤 1 超时，未找到图片 '{config.IMAGE_1_PATH}'，任务终止。")
            return

        print(f"\n[视觉] 发现图片 1! 坐标: {coords_1}")
        target_x, target_y = coords_1
        
        # 移动并单击激活输入框
        smooth_move_to(hw_controller, target_x + random.randint(-3, 3), target_y + random.randint(-3, 3))
        print(f"[动作] 执行左键单击...")
        hw_controller.left_click()
        time.sleep(0.5) # 等待光标闪烁
        
        # Python 写入系统剪贴板
        text_1 = "1#Aa甘蓝"
        set_clipboard_text(text_1)
        
        # 硬件键盘发送 Ctrl + V 快捷键
        print(f"[动作] 发送快捷键 Ctrl + V 进行粘贴...")
        hw_controller.shortcut('ctrl', 'v')
        time.sleep(1.0) 

        # ==========================================
        # 步骤 2：找图2 -> 单击 -> 剪贴板 + 特殊模式逐字输入
        # ==========================================
        print(f"\n[步骤 2] 正在寻找图片 2: '{config.IMAGE_2_PATH}' ...")
        coords_2 = wait_and_find_image(config.IMAGE_2_PATH, config.TIMEOUT_SECONDS)
        
        if not coords_2:
            print(f"\n[失败] 步骤 2 超时，未找到图片 '{config.IMAGE_2_PATH}'，任务终止。")
            return

        print(f"\n[视觉] 发现图片 2! 坐标: {coords_2}")
        target_x, target_y = coords_2
        
        # 移动并单击激活输入框
        smooth_move_to(hw_controller, target_x + random.randint(-3, 3), target_y + random.randint(-3, 3))
        print(f"[动作] 执行左键单击...")
        hw_controller.left_click()
        time.sleep(0.5) # 等待光标闪烁
        
        # Python 写入系统剪贴板
        text_2 = "3#Cc海苔"
        set_clipboard_text(text_2)
        
        # 调用特殊输入引擎，读取剪贴板并转化为硬件级逐字敲击
        print(f"[动作] 启动特殊输入模式，将剪贴板内容转化为物理按键敲击...")
        hardware_type_from_clipboard(hw_controller)

        print("\n[完成] 所有自动化步骤执行完毕！")

    except KeyboardInterrupt:
        print("\n[中断] 用户手动停止了脚本。")
    finally:
        # 确保退出时释放串口资源
        hw_controller.close()

if __name__ == "__main__":
    main_loop()
