import time
import sys
import random
import config
from core.controller import RP2350Controller
from core.vision import find_image_on_screen
from core.action import smooth_move_to
from core.input_engine import hardware_type_complex_string

def main_loop():
    # 1. 初始化硬件控制器
    hw_controller = RP2350Controller(config.COM_PORT, config.BAUD_RATE)
    
    print(f"\n[系统启动] 自动化脚本运行中...")
    print(f"待输入内容: {config.INPUT_STRING}")
    
    try:
        while True:
            print(f"\n[流程] 正在屏幕上寻找目标图片 '{config.TARGET_IMAGE_PATH}' ...")
            start_time = time.time()
            found = False
            
            while (time.time() - start_time) < config.TIMEOUT_SECONDS:
                # 2. 调用视觉模块找图
                coords = find_image_on_screen(config.TARGET_IMAGE_PATH, config.MATCH_THRESHOLD)
                
                if coords:
                    print(f"[视觉] 发现目标! 坐标: {coords}")
                    target_x, target_y = coords
                    offset_x = random.randint(-3, 3)
                    offset_y = random.randint(-3, 3)
                    
                    # 3. 调用动作模块移动鼠标
                    smooth_move_to(hw_controller, target_x + offset_x, target_y + offset_y)
                    
                    # 4. 调用控制器执行双击
                    print(f"[动作] 执行硬件左键双击...")
                    hw_controller.send_double_click()
                    time.sleep(1.0) 
                    
                    # 5. 调用输入引擎输入文本
                    print(f"[动作] 执行硬件文本输入...")
                    hardware_type_complex_string(hw_controller, config.INPUT_STRING)
                    
                    found = True
                    break
                
                time.sleep(0.5)
                sys.stdout.write(".")
                sys.stdout.flush()

            if not found:
                print(f"\n[超时] 未找到目标。请检查屏幕上是否有目标图片。")
                choice = input("输入 'r' 重试, 'c' 退出: ").strip().lower()
                if choice == 'c': break 
            else:
                print("\n[完成] 自动化流程执行完毕。")
                choice = input("按回车再次执行，输入 'c' 退出: ").strip().lower()
                if choice == 'c': break
                
    except KeyboardInterrupt:
        pass
    finally:
        # 确保退出时关闭串口
        hw_controller.close()

if __name__ == "__main__":
    main_loop()
