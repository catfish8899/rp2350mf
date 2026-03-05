import time

def hardware_type_complex_string(controller, content):
    """混合内容输入逻辑 (利用小狼毫+雾凇拼音 U模式)"""
    print(f" -> [输入系统] 开始处理字符串: {content}")
    i = 0
    while i < len(content):
        char = content[i]
        
        if '\u4e00' <= char <= '\u9fff': 
            hex_code = hex(ord(char))[2:]
            print(f"    [中文] '{char}' -> Unicode: {hex_code}")
            controller.send_combo('shift', 'u')
            time.sleep(0.1)
            controller.send_text(hex_code)
            time.sleep(0.1)
            controller.send_key('space')
            time.sleep(0.2)
            i += 1
            
        elif ('a' <= char <= 'z') or ('A' <= char <= 'Z'):
            temp_str = ""
            while i < len(content) and (('a' <= content[i] <= 'z') or ('A' <= content[i] <= 'Z')):
                temp_str += content[i]
                i += 1
            print(f"    [英文] '{temp_str}'")
            controller.send_text(temp_str)
            time.sleep(0.1)
            controller.send_key('enter')
            time.sleep(0.1)
            
        else:
            temp_str = ""
            while i < len(content) and not ('\u4e00' <= content[i] <= '\u9fff') and not (('a' <= content[i] <= 'z') or ('A' <= content[i] <= 'Z')):
                temp_str += content[i]
                i += 1
            print(f"    [符号] '{temp_str}'")
            controller.send_text(temp_str)
            time.sleep(0.1)
