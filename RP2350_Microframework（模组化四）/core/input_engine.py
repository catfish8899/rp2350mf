import time
import pyperclip

def set_clipboard_text(text):
    """将内容传入系统剪贴板"""
    pyperclip.copy(text)
    print(f"[剪贴板] 已写入内容: {text}")

def get_clipboard_text():
    """获取系统剪贴板内容"""
    return pyperclip.paste()

def hardware_type_from_clipboard(controller):
    """
    特殊功能：读取剪贴板内容，并使用硬件级分词策略逐字打出。
    适用于目标软件拒绝 Ctrl+V 粘贴的场景。
    """
    content = get_clipboard_text()
    if not content:
        print("[输入系统] 剪贴板为空，跳过输入。")
        return
    
    print(f"[输入系统] 读取到剪贴板内容，准备硬件级输入...")
    hardware_type_complex_string(controller, content)

def hardware_type_complex_string(controller, content):
    """核心分词与混合输入逻辑 (原有的黑科技)"""
    print(f" -> 开始处理字符串: {content}")
    i = 0
    while i < len(content):
        char = content[i]
        
        # --- 中文 (U模式) ---
        if '\u4e00' <= char <= '\u9fff': 
            hex_code = hex(ord(char))[2:]
            controller.shortcut('shift', 'u') # 呼出雾凇拼音 U 模式
            time.sleep(0.1)
            controller.send_text(hex_code)
            time.sleep(0.1)
            controller.key_click('space')
            time.sleep(0.2)
            i += 1
            
        # --- 英文 ---
        elif ('a' <= char <= 'z') or ('A' <= char <= 'Z'):
            temp_str = ""
            while i < len(content) and (('a' <= content[i] <= 'z') or ('A' <= content[i] <= 'Z')):
                temp_str += content[i]
                i += 1
            controller.send_text(temp_str)
            time.sleep(0.1)
            controller.key_click('enter') # 防输入法粘连
            time.sleep(0.1)
            
        # --- 数字与符号 ---
        else:
            temp_str = ""
            while i < len(content) and not ('\u4e00' <= content[i] <= '\u9fff') and not (('a' <= content[i] <= 'z') or ('A' <= content[i] <= 'Z')):
                temp_str += content[i]
                i += 1
            controller.send_text(temp_str)
            time.sleep(0.1)

