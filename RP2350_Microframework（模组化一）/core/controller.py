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

    def send_move(self, dx, dy):
        """发送鼠标相对移动指令"""
        if dx == 0 and dy == 0: return
        self.ser.write(f"m,{int(dx)},{int(dy)}\n".encode('utf-8'))

    def send_double_click(self):
        """发送双击指令"""
        self.ser.write(b"c\n")
        time.sleep(random.uniform(0.08, 0.15))
        self.ser.write(b"c\n")

    def send_key(self, key_name):
        """发送功能键"""
        self.ser.write(f"k,{key_name}\n".encode('utf-8'))
        time.sleep(0.05)

    def send_text(self, text):
        """发送纯英文/数字文本"""
        if not text: return
        self.ser.write(f"w,{text}\n".encode('utf-8'))
        time.sleep(0.05 * len(text)) 

    def send_combo(self, mod, key):
        """发送组合键"""
        self.ser.write(f"combo,{mod},{key}\n".encode('utf-8'))
        time.sleep(0.1)

    def close(self):
        """关闭串口连接"""
        if self.ser and self.ser.is_open:
            self.ser.close()
