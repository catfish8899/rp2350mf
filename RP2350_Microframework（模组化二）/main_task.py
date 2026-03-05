import time
import sys
import random
import config
from core.controller import RP2350Controller
from core.vision import find_image_on_screen
from core.action import smooth_move_to
from core.input_engine import hardware_type_complex_string

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
        # 步骤 1：寻找第一张图片并左键双击
        # ==========================================
        print(f"\n[步骤 1] 正在寻找图片 1: '{config.IMAGE_1_PATH}' ...")
        coords_1 = wait_and_find_image(config.IMAGE_1_PATH, config.TIMEOUT_SECONDS)
        
        if not coords_1:
            print(f"\n[失败] 步骤 1 超时，未找到图片 '{config.IMAGE_1_PATH}'，任务终止。")
            return

        print(f"\n[视觉] 发现图片 1! 坐标: {coords_1}")
        target_x, target_y = coords_1
        
        # 移动并双击
        smooth_move_to(hw_controller, target_x + random.randint(-3, 3), target_y + random.randint(-3, 3))
        print(f"[动作] 执行左键双击...")
        hw_controller.left_double_click()
        
        # 给系统/软件一点反应时间（比如打开新窗口或加载界面）
        time.sleep(1.5) 

        # ==========================================
        # 步骤 2：寻找第二张图片，左键单击并输入文本
        # ==========================================
        print(f"\n[步骤 2] 正在寻找图片 2: '{config.IMAGE_2_PATH}' ...")
        coords_2 = wait_and_find_image(config.IMAGE_2_PATH, config.TIMEOUT_SECONDS)
        
        if not coords_2:
            print(f"\n[失败] 步骤 2 超时，未找到图片 '{config.IMAGE_2_PATH}'，任务终止。")
            return

        print(f"\n[视觉] 发现图片 2! 坐标: {coords_2}")
        target_x, target_y = coords_2
        
        # 移动并单击
        smooth_move_to(hw_controller, target_x + random.randint(-3, 3), target_y + random.randint(-3, 3))
        print(f"[动作] 执行左键单击...")
        hw_controller.left_click()
        
        # 等待输入框激活光标
        time.sleep(0.5)
        
        # 输入文本
        print(f"[动作] 开始输入文本: {config.INPUT_STRING}")
        hardware_type_complex_string(hw_controller, config.INPUT_STRING)

        print("\n[完成] 所有自动化步骤执行完毕！")

    except KeyboardInterrupt:
        print("\n[中断] 用户手动停止了脚本。")
    finally:
        # 确保退出时释放串口资源
        hw_controller.close()

if __name__ == "__main__":
    main_loop()
