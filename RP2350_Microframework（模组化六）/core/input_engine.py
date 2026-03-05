# ===================================================================================
# 模块名称：复杂输入引擎 (input_engine.py)
# 模块功能：处理系统剪贴板交互，并提供针对反自动化软件的“硬件级混合输入”策略。
# ===================================================================================
import time
import pyperclip

def set_clipboard_text(text):
    """
    将指定文本注入 Windows 系统剪贴板。
    """
    pyperclip.copy(text)
    print(f"[输入引擎] 数据已写入系统剪贴板: {text}")

def get_clipboard_text():
    """
    读取当前 Windows 系统剪贴板中的文本数据。
    """
    return pyperclip.paste()

def hardware_type_from_clipboard(controller):
    """
    硬件级输入调度器。
    读取剪贴板内容，并调用底层分词策略将其转化为物理键盘敲击序列。
    专为绕过目标软件禁用 Ctrl+V 粘贴权限的边缘场景设计。
    """
    content = get_clipboard_text()
    if not content:
        print("[输入引擎] 剪贴板数据为空，已跳过输入序列。")
        return
    
    print(f"[输入引擎] 捕获剪贴板数据，正在初始化硬件级键入序列...")
    hardware_type_complex_string(controller, content)

def hardware_type_complex_string(controller, content):
    """
    核心分词与混合输入算法。
    将混合字符串拆分为中文、英文、符号等区块，并针对不同字符集采用特定的物理输入策略
    （例如：利用输入法的 Unicode 模式输入中文字符，以彻底规避软件层的输入拦截）。
    """
    print(f"[输入引擎] 开始解析并执行字符串流: {content}")
    i = 0
    while i < len(content):
        char = content[i]
        
        # --- 中文字符处理策略 (依赖特定输入法的 U 模式，如雾凇拼音) ---
        if '\u4e00' <= char <= '\u9fff': 
            hex_code = hex(ord(char))[2:]
            controller.shortcut('shift', 'u') # 触发输入法 Unicode 编码输入模式
            time.sleep(0.1)
            controller.send_text(hex_code)
            time.sleep(0.1)
            controller.key_click('space')     # 确认上屏
            time.sleep(0.2)
            i += 1
            
        # --- 英文字符处理策略 (连续键入) ---
        elif ('a' <= char <= 'z') or ('A' <= char <= 'Z'):
            temp_str = ""
            while i < len(content) and (('a' <= content[i] <= 'z') or ('A' <= content[i] <= 'Z')):
                temp_str += content[i]
                i += 1
            controller.send_text(temp_str)
            time.sleep(0.1)
            controller.key_click('enter')     # 触发回车以防止输入法拼音粘连
            time.sleep(0.1)
            
        # --- 数字与特殊符号处理策略 ---
        else:
            temp_str = ""
            while i < len(content) and not ('\u4e00' <= content[i] <= '\u9fff') and not (('a' <= content[i] <= 'z') or ('A' <= content[i] <= 'Z')):
                temp_str += content[i]
                i += 1
            controller.send_text(temp_str)
            time.sleep(0.1)
