# -----------------------------------------------------------------------------------
# 脚本名称：code.py (更新版：支持全功能鼠标动作)
# 适用硬件：树莓派 RP2350 (Pico 2)
# -----------------------------------------------------------------------------------
import usb_hid
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
import usb_cdc
import time

mouse = Mouse(usb_hid.devices)
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)
serial = usb_cdc.console

print("RP2350 硬件自动化执行端已就绪 - 正在监听串口指令...")

buffer = ""

# =========================================================================
# [2] 按键映射表 (已修复：增加常用快捷键字母映射)
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
    
    # 字母映射
    'u': Keycode.U,  # 用于雾凇拼音特殊输入
    'v': Keycode.V,  # 用于 Ctrl+V 粘贴
    'c': Keycode.C,  # 用于 Ctrl+C 复制
    'a': Keycode.A,  # 用于 Ctrl+A 全选
    'x': Keycode.X,  # 用于 Ctrl+X 剪切
    'z': Keycode.Z   # 用于 Ctrl+Z 撤销
}


# 鼠标按键映射表 (标准HID鼠标按键值)
MOUSE_BUTTON_MAP = {
    'left': Mouse.LEFT_BUTTON,     # 1
    'right': Mouse.RIGHT_BUTTON,   # 2
    'middle': Mouse.MIDDLE_BUTTON, # 4
    'back': 8,                     # 侧键后 (向后翻页)
    'forward': 16                  # 侧键前 (向前翻页)
}

while True:
    if serial.in_waiting > 0:
        try:
            char = serial.read(1).decode("utf-8")
            if char == "\n":
                cmd = buffer.strip()
                buffer = ""
                parts = cmd.split(",") 
                action = parts[0]

                # --- 鼠标移动 ---
                if action == 'm' and len(parts) == 3:
                    mouse.move(x=int(parts[1]), y=int(parts[2]))
                
                # --- 鼠标点击 (mc,按键名) ---
                elif action == 'mc' and len(parts) == 2:
                    btn = parts[1].lower()
                    if btn in MOUSE_BUTTON_MAP:
                        mouse.click(MOUSE_BUTTON_MAP[btn])
                
                # --- 鼠标按下 (mp,按键名) ---
                elif action == 'mp' and len(parts) == 2:
                    btn = parts[1].lower()
                    if btn in MOUSE_BUTTON_MAP:
                        mouse.press(MOUSE_BUTTON_MAP[btn])
                
                # --- 鼠标松开 (mr,按键名) ---
                elif action == 'mr' and len(parts) == 2:
                    btn = parts[1].lower()
                    if btn in MOUSE_BUTTON_MAP:
                        mouse.release(MOUSE_BUTTON_MAP[btn])
                
                # --- 鼠标滚轮 (ms,滚动量) ---
                elif action == 'ms' and len(parts) == 2:
                    # 正数向上滚，负数向下滚
                    mouse.move(wheel=int(parts[1]))

                # --- 键盘文本输出 (w,text) ---
                elif action == 'w' and len(parts) >= 2:
                    text_to_write = ",".join(parts[1:])
                    layout.write(text_to_write)
                
                # --- 单按键输入 (k,key_name) ---
                elif action == 'k' and len(parts) == 2:
                    key_name = parts[1].lower()
                    if key_name in KEY_MAP:
                        kbd.send(KEY_MAP[key_name])
                
                # --- 单按键按住 (kp,key_name) ---
                elif action == 'kp' and len(parts) == 2:
                    key_name = parts[1].lower()
                    if key_name in KEY_MAP:
                        kbd.press(KEY_MAP[key_name])
                
                # --- 单按键松开 (kr,key_name) ---
                elif action == 'kr' and len(parts) == 2:
                    key_name = parts[1].lower()
                    if key_name in KEY_MAP:
                        kbd.release(KEY_MAP[key_name])
                
                # --- 组合键/快捷键操作 (combo,key1,key2...) ---
                elif action == 'combo' and len(parts) >= 3:
                    modifiers = []
                    target_key = None
                    valid = True
                    for k in parts[1:-1]:
                        if k in KEY_MAP: modifiers.append(KEY_MAP[k])
                        else: valid = False
                    last = parts[-1]
                    if last in KEY_MAP: target_key = KEY_MAP[last]
                    elif len(last) == 1: pass 
                    else: valid = False

                    if valid and target_key:
                        kbd.press(*modifiers)
                        kbd.press(target_key)
                        kbd.release_all()
            else:
                buffer += char
        except Exception:
            buffer = ""
