import serial
import time
import random
import sys

class RP2350Controller:
    def __init__(self, port, baud_rate=115200):
        try:
            self.ser = serial.Serial(port, baud_rate, timeout=0.1)
            print(f"[硬件连接] 成功连接至 {port}。RP2350 已就绪。")
        except Exception as e:
            print(f"[连接失败] 无法找到 RP2350，请检查设备管理器中的 COM 号: {e}")
            sys.exit(1)

    # ==========================================
    # 鼠标移动指令
    # ==========================================
    def send_move(self, dx, dy):
        """发送鼠标相对移动指令"""
        if dx == 0 and dy == 0: return
        self.ser.write(f"m,{int(dx)},{int(dy)}\n".encode('utf-8'))

    # ==========================================
    # 鼠标按键指令 (左键、右键、中键、侧键)
    # ==========================================
    def _mouse_action(self, action_type, button):
        """底层鼠标动作发送器 (mc=点击, mp=按下, mr=松开)"""
        valid_buttons = ['left', 'right', 'middle', 'forward', 'back']
        if button not in valid_buttons:
            raise ValueError(f"不支持的鼠标按键: {button}")
        self.ser.write(f"{action_type},{button}\n".encode('utf-8'))
        time.sleep(0.05)

    # --- 左键操作 ---
    def left_click(self):
        """左键点击"""
        self._mouse_action('mc', 'left')

    def left_press(self):
        """左键按住 (用于拖拽)"""
        self._mouse_action('mp', 'left')

    def left_release(self):
        """左键松开 (用于结束拖拽)"""
        self._mouse_action('mr', 'left')

    def left_double_click(self):
        """左键双击"""
        self.left_click()
        time.sleep(random.uniform(0.08, 0.15)) # 模拟人类双击间隔
        self.left_click()

    # --- 右键操作 ---
    def right_click(self):
        """右键点击 (呼出菜单)"""
        self._mouse_action('mc', 'right')

    def right_press(self):
        """右键按住"""
        self._mouse_action('mp', 'right')

    def right_release(self):
        """右键松开"""
        self._mouse_action('mr', 'right')

    # --- 滚轮按键操作 ---
    def middle_click(self):
        """滚轮点击"""
        self._mouse_action('mc', 'middle')

    def middle_press(self):
        """滚轮按住"""
        self._mouse_action('mp', 'middle')

    def middle_release(self):
        """滚轮松开"""
        self._mouse_action('mr', 'middle')

    # --- 侧键操作 (翻页) ---
    def page_forward(self):
        """向前翻页 (鼠标侧键-前)"""
        self._mouse_action('mc', 'forward')

    def page_backward(self):
        """向后翻页 (鼠标侧键-后)"""
        self._mouse_action('mc', 'back')

    # ==========================================
    # 鼠标滚轮滚动指令
    # ==========================================
    def scroll_up(self, lines=1):
        """滚轮上滚固定行程"""
        self.ser.write(f"ms,{int(lines)}\n".encode('utf-8'))
        time.sleep(0.05)

    def scroll_down(self, lines=1):
        """滚轮下滚固定行程"""
        self.ser.write(f"ms,{-int(lines)}\n".encode('utf-8'))
        time.sleep(0.05)

    # ==========================================
    # 键盘指令 (保持不变)
    # ==========================================
    def send_key(self, key_name):
        self.ser.write(f"k,{key_name}\n".encode('utf-8'))
        time.sleep(0.05)

    def send_text(self, text):
        if not text: return
        self.ser.write(f"w,{text}\n".encode('utf-8'))
        time.sleep(0.05 * len(text)) 

    def send_combo(self, mod, key):
        self.ser.write(f"combo,{mod},{key}\n".encode('utf-8'))
        time.sleep(0.1)

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
