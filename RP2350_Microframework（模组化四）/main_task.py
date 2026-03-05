import time
import random
import pandas as pd
import config
from core.controller import RP2350Controller
from core.vision import wait_and_find_image_with_retry
from core.action import smooth_move_to
from core.input_engine import set_clipboard_text, hardware_type_from_clipboard

def read_excel_data(file_path):
    """读取Excel数据"""
    try:
        # 尝试作为Excel读取
        df = pd.read_excel(file_path, header=None)
    except Exception:
        try:
            # 兼容处理：如果实际是CSV格式
            df = pd.read_csv(file_path, header=None)
        except Exception as e:
            print(f"读取Excel失败: {e}")
            return []
    
    data = []
    for index, row in df.iterrows():
        # 清理可能存在的冒号和空格
        key = str(row[0]).strip('：,: ')
        value = str(row[1]).strip()
        data.append((key, value))
    return data

def main_loop():
    # 1. 读取数据
    print("[系统] 正在读取Excel数据...")
    data_items = read_excel_data(config.EXCEL_PATH)
    if not data_items:
        print("[错误] 未读取到数据，程序退出。")
        input("按 Enter 键退出...")
        return
        
    print(f"[系统] 成功读取 {len(data_items)} 条数据。")

    # 2. 初始化硬件控制器
    hw_controller = RP2350Controller(config.COM_PORT, config.BAUD_RATE)
    print(f"\n[系统启动] 自动化任务开始执行...")
    
    try:
        for i, (key, value) in enumerate(data_items):
            if i < len(config.IMAGE_PATHS):
                image_path = config.IMAGE_PATHS[i]
            else:
                print(f"[警告] 缺少第 {i+1} 项的截图配置，跳过。")
                continue
                
            print(f"\n==========================================")
            print(f"[步骤 {i+1}] 准备输入: {key} -> {value}")
            
            # 使用封装好的带重试机制的找图函数
            coords = wait_and_find_image_with_retry(image_path, config.TIMEOUT_SECONDS, config.MATCH_THRESHOLD)
            if not coords:
                print(f"[跳过] 步骤 {i+1} 已跳过。")
                continue
                
            print(f"[视觉] 发现图片! 坐标: {coords}")
            target_x, target_y = coords
            
            # 移动到截图偏右一点的位置 (X轴向右偏移 60 像素，可根据实际截图大小微调)
            offset_x = 60
            smooth_move_to(hw_controller, target_x + offset_x + random.randint(-3, 3), target_y + random.randint(-3, 3))
            
            print(f"[动作] 执行左键单击...")
            hw_controller.left_click()
            time.sleep(0.5) # 等待光标闪烁
            
            # 写入剪贴板并使用硬件级输入
            set_clipboard_text(value)
            print(f"[动作] 启动特殊输入模式，将剪贴板内容转化为物理按键敲击...")
            hardware_type_from_clipboard(hw_controller)
            time.sleep(0.5)

        print("\n[完成] 所有自动化步骤执行完毕！")

    except KeyboardInterrupt as e:
        print(f"\n[中断] {e}")
    except Exception as e:
        print(f"\n[错误] 发生未知错误: {e}")
    finally:
        # 确保退出时释放串口资源
        if 'hw_controller' in locals():
            hw_controller.close()
        
        # 任务结束后，按enter键才会关闭程序
        input("\n任务结束，按 Enter 键关闭程序...")

if __name__ == "__main__":
    main_loop()
