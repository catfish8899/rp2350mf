import os
import sys
import time
import json
import random
import pandas as pd
from pathlib import Path

# 核心模组导入
from core.controller import RP2350Controller
from core.vision import wait_and_find_image_with_retry
from core.action import smooth_move_to
from core.input_engine import set_clipboard_text, hardware_type_from_clipboard

# 强制重定向标准输出流为 UTF-8 编码，避免控制台路径打印出现乱码
if sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def get_external_path(relative_path):
    """
    获取外部资源的绝对路径。
    兼容 PyInstaller 打包环境，确保在 frozen 状态下仍能准确定位到可执行文件同级目录。
    """
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).resolve().parent
    return str(base_path / relative_path)

def load_config():
    """
    动态加载并解析外部 config.json 配置文件。
    若文件不存在则抛出致命错误并终止进程，不执行自动创建以精简代码体积。
    """
    config_path = get_external_path('config.json')
    if not os.path.exists(config_path):
        print(f"[致命错误] 配置文件缺失: {config_path}")
        print("请确保 config.json 与主程序处于同一目录层级。")
        input("按 Enter 键退出...")
        sys.exit(1)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            
        # 提取配置项并执行严格的类型转换
        app_config = {
            'EXCEL_PATH': str(config_data['Settings']['EXCEL_PATH']).strip(),
            'MATCH_THRESHOLD': float(config_data['Settings']['MATCH_THRESHOLD']),
            'TIMEOUT_SECONDS': int(config_data['Settings']['TIMEOUT_SECONDS']),
            'COM_PORT': str(config_data['Settings']['COM_PORT']).strip(),
            'BAUD_RATE': int(config_data['Settings']['BAUD_RATE']),
            'IMAGE_PATHS': config_data['Images']['IMAGE_PATHS']
        }
        return app_config
    except Exception as e:
        print(f"[配置解析异常] config.json 格式错误或缺少必要字段: {e}")
        input("按 Enter 键退出...")
        sys.exit(1)

def read_excel_data(file_path):
    """
    解析 Excel 或 CSV 数据源。
    返回格式化后的键值对列表，用于后续的自动化输入任务。
    """
    try:
        df = pd.read_excel(file_path, header=None)
    except Exception:
        try:
            df = pd.read_csv(file_path, header=None)
        except Exception as e:
            print(f"[数据读取异常] 无法解析数据源文件: {e}")
            return []
    
    data = []
    for index, row in df.iterrows():
        key = str(row[0]).strip('：,: ')
        value = str(row[1]).strip()
        data.append((key, value))
    return data

def main_loop():
    """
    主控循环：负责配置加载、数据读取、硬件初始化及自动化任务的调度执行。
    """
    # 1. 加载系统配置
    print("[系统初始化] 正在加载外部配置文件 config.json ...")
    app_config = load_config()

    # 2. 读取业务数据
    print("[系统初始化] 正在解析数据源...")
    excel_abs_path = get_external_path(app_config['EXCEL_PATH'])
    data_items = read_excel_data(excel_abs_path)
    
    if not data_items:
        print("[执行异常] 数据源为空或读取失败，进程即将终止。")
        input("按 Enter 键退出...")
        return
        
    print(f"[系统初始化] 数据源解析完毕，共计 {len(data_items)} 条有效记录。")

    # 3. 初始化底层硬件控制器
    hw_controller = RP2350Controller(app_config['COM_PORT'], app_config['BAUD_RATE'])
    print(f"\n[任务调度] 自动化序列开始执行...")
    
    try:
        for i, (key, value) in enumerate(data_items):
            # 校验当前步骤是否具备对应的视觉模板
            if i < len(app_config['IMAGE_PATHS']):
                image_abs_path = get_external_path(app_config['IMAGE_PATHS'][i])
            else:
                print(f"[调度警告] 索引 {i+1} 缺失视觉模板配置，已跳过该节点。")
                continue
                
            print(f"\n==========================================")
            print(f"[执行节点 {i+1}] 目标键值: {key} -> {value}")
            
            # 4. 视觉定位与重试机制
            coords = wait_and_find_image_with_retry(
                image_abs_path, 
                app_config['TIMEOUT_SECONDS'], 
                app_config['MATCH_THRESHOLD']
            )
            
            if not coords:
                print(f"[调度跳过] 节点 {i+1} 视觉匹配超时，已放弃执行。")
                continue
                
            print(f"[视觉引擎] 目标已锁定，屏幕坐标: {coords}")
            target_x, target_y = coords
            
            # 5. 轨迹规划与硬件级鼠标移动 (引入随机偏移以模拟真实操作)
            offset_x = 60
            smooth_move_to(
                hw_controller, 
                target_x + offset_x + random.randint(-3, 3), 
                target_y + random.randint(-3, 3)
            )
            
            print(f"[硬件指令] 触发鼠标左键单击事件...")
            hw_controller.left_click()
            time.sleep(0.5)
            
            # 6. 剪贴板数据注入与硬件级键盘敲击
            set_clipboard_text(value)
            print(f"[硬件指令] 激活底层输入引擎，执行物理级键入序列...")
            hardware_type_from_clipboard(hw_controller)
            time.sleep(0.5)

        print("\n[任务完结] 所有自动化节点均已执行完毕。")

    except KeyboardInterrupt as e:
        print(f"\n[进程中断] 接收到用户中断信号: {e}")
    except Exception as e:
        print(f"\n[致命异常] 运行时发生未捕获错误: {e}")
    finally:
        # 确保硬件资源被正确释放
        if 'hw_controller' in locals():
            hw_controller.close()
        input("\n[系统提示] 任务生命周期结束，按 Enter 键关闭控制台...")

if __name__ == "__main__":
    main_loop()
