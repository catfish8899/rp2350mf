# ===================================================================================
# 模块名称：硬件级自动化执行端固件 (code.py)
# 适用硬件：Raspberry Pi RP2350 (Pico 2)
# 模块功能：基于 USB HID 协议，将 RP2350 模拟为标准鼠标与键盘外设。
#           通过监听 USB CDC 虚拟串口接收上位机指令，并转化为物理级的键鼠动作。
# ===================================================================================
import usb_hid
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
import usb_cdc
import time

# 初始化 HID 设备实例
mouse = Mouse(usb_hid.devices)
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)
serial = usb_cdc.console

print("[系统就绪] RP2350 硬件自动化执行端已启动，正在监听串口指令流...")

buffer = ""

# =========================================================================
# [配置] 物理按键映射字典
# 映射上位机字符串指令至底层 HID Keycode
# =========================================================================
KEY_MAP = {
    'shift': Keycode.SHIFT, 
    'ctrl': Keycode.CONTROL, 
    'alt': Keycode.ALT,
    'enter': Keycode.ENTER, 
    'space': Keycode.SPACE, 
    'backspace': Keycode.BACKSPACE,
    'tab': Keycode.TAB, 
    'esc': Keycode.ESCAPE, 
    
    # 常用快捷键字母映射
    'u': Keycode.U,  # 预留：用于触发特定输入法（如雾凇拼音）的特殊模式
    'v': Keycode.V,  # 预留：Ctrl+V 粘贴
    'c': Keycode.C,  # 预留：Ctrl+C 复制
    'a': Keycode.A,  # 预留：Ctrl+A 全选
    'x': Keycode.X,  # 预留：Ctrl+X 剪切
    'z': Keycode.Z   # 预留：Ctrl+Z 撤销
}

# 鼠标物理按键映射字典 (遵循标准 HID 鼠标按键位掩码)
MOUSE_BUTTON_MAP = {
    'left': Mouse.LEFT_BUTTON,     # 1: 左键
    'right': Mouse.RIGHT_BUTTON,   # 2: 右键
    'middle': Mouse.MIDDLE_BUTTON, # 4: 中键/滚轮点击
    'back': 8,                     # 8: 侧键后退
    'forward': 16                  # 16: 侧键前进
}

# 主事件循环：持续轮询串口缓冲区
while True:
    if serial.in_waiting > 0:
        try:
            # 逐字节读取并解码
            char = serial.read(1).decode("utf-8")
            if char == "\n":
                # 遇到换行符，开始解析完整指令帧
                cmd = buffer.strip()
                buffer = ""
                parts = cmd.split(",") 
                action = parts[0]

                # --- 鼠标相对位移指令 (m, dx, dy) ---
                if action == 'm' and len(parts) == 3:
                    mouse.move(x=int(parts[1]), y=int(parts[2]))
                
                # --- 鼠标按键点击指令 (mc, button_name) ---
                elif action == 'mc' and len(parts) == 2:
                    btn = parts[1].lower()
                    if btn in MOUSE_BUTTON_MAP:
                        mouse.click(MOUSE_BUTTON_MAP[btn])
                
                # --- 鼠标按键按下指令 (mp, button_name) ---
                elif action == 'mp' and len(parts) == 2:
                    btn = parts[1].lower()
                    if btn in MOUSE_BUTTON_MAP:
                        mouse.press(MOUSE_BUTTON_MAP[btn])
                
                # --- 鼠标按键释放指令 (mr, button_name) ---
                elif action == 'mr' and len(parts) == 2:
                    btn = parts[1].lower()
                    if btn in MOUSE_BUTTON_MAP:
                        mouse.release(MOUSE_BUTTON_MAP[btn])
                
                # --- 鼠标滚轮滚动指令 (ms, lines) ---
                elif action == 'ms' and len(parts) == 2:
                    # 正值向上滚动，负值向下滚动
                    mouse.move(wheel=int(parts[1]))

                # --- 键盘文本流输出指令 (w, text) ---
                elif action == 'w' and len(parts) >= 2:
                    text_to_write = ",".join(parts[1:])
                    layout.write(text_to_write)
                
                # --- 键盘单键点击指令 (k, key_name) ---
                elif action == 'k' and len(parts) == 2:
                    key_name = parts[1].lower()
                    if key_name in KEY_MAP:
                        kbd.send(KEY_MAP[key_name])
                
                # --- 键盘单键按下指令 (kp, key_name) ---
                elif action == 'kp' and len(parts) == 2:
                    key_name = parts[1].lower()
                    if key_name in KEY_MAP:
                        kbd.press(KEY_MAP[key_name])
                
                # --- 键盘单键释放指令 (kr, key_name) ---
                elif action == 'kr' and len(parts) == 2:
                    key_name = parts[1].lower()
                    if key_name in KEY_MAP:
                        kbd.release(KEY_MAP[key_name])
                
                # --- 键盘组合键/快捷键指令 (combo, key1, key2, ...) ---
                elif action == 'combo' and len(parts) >= 3:
                    modifiers = []
                    target_key = None
                    valid = True
                    
                    # 解析修饰键 (如 ctrl, shift)
                    for k in parts[1:-1]:
                        if k in KEY_MAP: 
                            modifiers.append(KEY_MAP[k])
                        else: 
                            valid = False
                            
                    # 解析目标键
                    last = parts[-1]
                    if last in KEY_MAP: 
                        target_key = KEY_MAP[last]
                    elif len(last) == 1: 
                        pass # 允许单字符作为目标键，但此处逻辑主要依赖 KEY_MAP
                    else: 
                        valid = False

                    # 执行组合键物理敲击
                    if valid and target_key:
                        kbd.press(*modifiers)
                        kbd.press(target_key)
                        kbd.release_all()
            else:
                buffer += char
        except Exception:
            # 异常发生时清空缓冲区，防止指令粘连
            buffer = ""
