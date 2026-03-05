import os
import sys
import time
import random
import pandas as pd
import configparser
from pathlib import Path

# 移除 import config，改为动态加载
from core.controller import RP2350Controller
from core.vision import wait_and_find_image_with_retry
from core.action import smooth_move_to
from core.input_engine import set_clipboard_text, hardware_type_from_clipboard

# 强制控制台使用 UTF-8 编码输出，防止打印中文路径时出现乱码
if sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def get_external_path(relative_path):
    """获取外部资源（与exe同级目录）的绝对路径"""
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).resolve().parent
    return str(base_path / relative_path)

def load_config():
    """动态加载外部 config.txt 配置文件"""
    config_path = get_external_path('config.txt')
    if not os.path.exists(config_path):
        print(f"[致命错误] 找不到配置文件: {config_path}")
        print("请确保 config.txt 与程序在同一目录下！")
        input("按 Enter 键退出...")
        sys.exit(1)

    parser = configparser.ConfigParser()
    # 使用 utf-8 编码读取，防止配置文件中有中文注释报错
    parser.read(config_path, encoding='utf-8')

    try:
        # 解析配置项并做类型转换
        app_config = {
            'EXCEL_PATH': parser.get('Settings', 'EXCEL_PATH').strip(),
            'MATCH_THRESHOLD': parser.getfloat('Settings', 'MATCH_THRESHOLD'),
            'TIMEOUT_SECONDS': parser.getint('Settings', 'TIMEOUT_SECONDS'),
            'COM_PORT': parser.get('Settings', 'COM_PORT').strip(),
            'BAUD_RATE': parser.getint('Settings', 'BAUD_RATE'),
            # 将逗号分隔的字符串转换为列表，并去除空格
            'IMAGE_PATHS': [p.strip() for p in parser.get('Images', 'IMAGE_PATHS').split(',')]
        }
        return app_config
    except Exception as e:
        print(f"[配置错误] config.txt 格式不正确或缺少必要配置项: {e}")
        input("按 Enter 键退出...")
        sys.exit(1)

def read_excel_data(file_path):
    """读取Excel数据"""
    try:
        df = pd.read_excel(file_path, header=None)
    except Exception:
        try:
            df = pd.read_csv(file_path, header=None)
        except Exception as e:
            print(f"读取Excel失败: {e}")
            return []
    
    data = []
    for index, row in df.iterrows():
        key = str(row[0]).strip('：,: ')
        value = str(row[1]).strip()
        data.append((key, value))
    return data

def main_loop():
    # 0. 加载外部配置
    print("[系统] 正在加载外部配置文件 config.txt ...")
    app_config = load_config()

    # 1. 读取数据
    print("[系统] 正在读取Excel数据...")
    excel_abs_path = get_external_path(app_config['EXCEL_PATH'])
    data_items = read_excel_data(excel_abs_path)
    
    if not data_items:
        print("[错误] 未读取到数据，程序退出。")
        input("按 Enter 键退出...")
        return
        
    print(f"[系统] 成功读取 {len(data_items)} 条数据。")

    # 2. 初始化硬件控制器
    hw_controller = RP2350Controller(app_config['COM_PORT'], app_config['BAUD_RATE'])
    print(f"\n[系统启动] 自动化任务开始执行...")
    
    try:
        for i, (key, value) in enumerate(data_items):
            if i < len(app_config['IMAGE_PATHS']):
                image_abs_path = get_external_path(app_config['IMAGE_PATHS'][i])
            else:
                print(f"[警告] 缺少第 {i+1} 项的截图配置，跳过。")
                continue
                
            print(f"\n==========================================")
            print(f"[步骤 {i+1}] 准备输入: {key} -> {value}")
            
            # 使用配置中的参数
            coords = wait_and_find_image_with_retry(
                image_abs_path, 
                app_config['TIMEOUT_SECONDS'], 
                app_config['MATCH_THRESHOLD']
            )
            
            if not coords:
                print(f"[跳过] 步骤 {i+1} 已跳过。")
                continue
                
            print(f"[视觉] 发现图片! 坐标: {coords}")
            target_x, target_y = coords
            
            offset_x = 60
            smooth_move_to(hw_controller, target_x + offset_x + random.randint(-3, 3), target_y + random.randint(-3, 3))
            
            print(f"[动作] 执行左键单击...")
            hw_controller.left_click()
            time.sleep(0.5)
            
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
        if 'hw_controller' in locals():
            hw_controller.close()
        input("\n任务结束，按 Enter 键关闭程序...")

if __name__ == "__main__":
    main_loop()
