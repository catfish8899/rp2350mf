# ===================================================================================
# 模块名称：硬件通信控制器 (controller.py)
# 模块功能：负责与 RP2350 硬件端建立串行通信，封装并下发标准化的键鼠控制指令。
# ===================================================================================
import serial
import time
import random
import sys

class RP2350Controller:
    """
    RP2350 硬件控制器类。
    提供对底层串口通信的封装，向上层业务逻辑暴露易用的键鼠操作 API。
    """
    def __init__(self, port, baud_rate=115200):
        try:
            self.ser = serial.Serial(port, baud_rate, timeout=0.1)
            print(f"[硬件总线] 成功建立通信链路，端口: {port}。RP2350 节点已就绪。")
        except Exception as e:
            print(f"[致命错误] 无法寻址 RP2350 硬件节点，请核对设备管理器中的 COM 端口分配: {e}")
            sys.exit(1)

    # ==========================================
    # 鼠标位移控制接口
    # ==========================================
    def send_move(self, dx, dy):
        """下发鼠标相对位移指令帧"""
        if dx == 0 and dy == 0: return
        self.ser.write(f"m,{int(dx)},{int(dy)}\n".encode('utf-8'))

    # ==========================================
    # 鼠标按键控制接口
    # ==========================================
    def _mouse_action(self, action_type, button):
        """底层鼠标动作指令封装器 (mc=点击, mp=按下, mr=松开)"""
        valid_buttons = ['left', 'right', 'middle', 'forward', 'back']
        if button not in valid_buttons:
            raise ValueError(f"[参数异常] 不支持的鼠标按键标识: {button}")
        self.ser.write(f"{action_type},{button}\n".encode('utf-8'))
        time.sleep(0.05)

    # --- 左键操作集 ---
    def left_click(self):
        """触发鼠标左键单击事件"""
        self._mouse_action('mc', 'left')

    def left_press(self):
        """触发鼠标左键按下事件 (常用于拖拽起始)"""
        self._mouse_action('mp', 'left')

    def left_release(self):
        """触发鼠标左键释放事件 (常用于拖拽结束)"""
        self._mouse_action('mr', 'left')

    def left_double_click(self):
        """触发鼠标左键双击事件 (包含拟人化随机间隔)"""
        self.left_click()
        time.sleep(random.uniform(0.08, 0.15)) 
        self.left_click()

    # --- 右键操作集 ---
    def right_click(self):
        """触发鼠标右键单击事件 (常用于呼出上下文菜单)"""
        self._mouse_action('mc', 'right')

    def right_press(self):
        self._mouse_action('mp', 'right')

    def right_release(self):
        self._mouse_action('mr', 'right')

    # --- 中键/滚轮操作集 ---
    def middle_click(self):
        self._mouse_action('mc', 'middle')

    def middle_press(self):
        self._mouse_action('mp', 'middle')

    def middle_release(self):
        self._mouse_action('mr', 'middle')

    # --- 侧键操作集 ---
    def page_forward(self):
        """触发鼠标侧键前进事件"""
        self._mouse_action('mc', 'forward')

    def page_backward(self):
        """触发鼠标侧键后退事件"""
        self._mouse_action('mc', 'back')

    # ==========================================
    # 鼠标滚轮控制接口
    # ==========================================
    def scroll_up(self, lines=1):
        """下发滚轮向上滚动指令"""
        self.ser.write(f"ms,{int(lines)}\n".encode('utf-8'))
        time.sleep(0.05)

    def scroll_down(self, lines=1):
        """下发滚轮向下滚动指令"""
        self.ser.write(f"ms,{-int(lines)}\n".encode('utf-8'))
        time.sleep(0.05)

    # ==========================================
    # 键盘控制接口
    # ==========================================
    def key_click(self, key_name):
        """触发单键敲击事件 (按下并迅速释放)"""
        self.ser.write(f"k,{key_name}\n".encode('utf-8'))
        time.sleep(0.05)

    def key_press(self, key_name):
        """触发单键按下事件 (常用于修饰键保持)"""
        self.ser.write(f"kp,{key_name}\n".encode('utf-8'))
        time.sleep(0.05)

    def key_release(self, key_name):
        """触发单键释放事件"""
        self.ser.write(f"kr,{key_name}\n".encode('utf-8'))
        time.sleep(0.05)

    def shortcut(self, *keys):
        """
        触发组合快捷键事件。
        示例: controller.shortcut('ctrl', 'c')
        """
        if len(keys) < 2: return
        keys_str = ",".join(keys)
        self.ser.write(f"combo,{keys_str}\n".encode('utf-8'))
        time.sleep(0.1)
    
    def send_text(self, text):
        """下发纯英文/数字文本流快速输入指令"""
        if not text: return
        self.ser.write(f"w,{text}\n".encode('utf-8'))
        time.sleep(0.05 * len(text)) 

    def close(self):
        """安全释放串口通信资源"""
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
            print("[硬件总线] 串口通信链路已安全断开。")
