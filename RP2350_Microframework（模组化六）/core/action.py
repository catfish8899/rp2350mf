# ===================================================================================
# 模块名称：拟人化动作引擎 (action.py)
# 模块功能：提供基于 Windows API 的屏幕坐标获取，以及规避软件检测的平滑鼠标轨迹规划算法。
# ===================================================================================
import ctypes
from ctypes import wintypes
import math
import time

def get_current_mouse_pos():
    """
    调用 Windows 底层 API 获取当前鼠标指针的绝对物理坐标。
    返回: (x, y) 坐标元组
    """
    point = wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
    return point.x, point.y

def smooth_move_to(controller, target_x, target_y):
    """
    拟人化平滑移动算法。
    通过动态计算距离与速度因子，将绝对坐标位移转化为一系列相对位移指令，
    模拟人类操作鼠标时的加减速特征，有效降低被目标软件判定为自动化脚本的风险。
    
    参数:
        controller: RP2350Controller 硬件控制器实例
        target_x (int): 目标屏幕 X 坐标
        target_y (int): 目标屏幕 Y 坐标
    """
    max_loops = 300 
    loop_count = 0
    
    while loop_count < max_loops:
        cur_x, cur_y = get_current_mouse_pos()
        diff_x = target_x - cur_x
        diff_y = target_y - cur_y
        
        # 抵达目标容差范围内，终止轨迹规划
        if abs(diff_x) <= 3 and abs(diff_y) <= 3: 
            break
        
        # 动态速度因子计算：距离越近，步长越小（模拟减速对准）
        distance = math.sqrt(diff_x**2 + diff_y**2)
        if distance > 100: 
            speed_factor = 0.15 
        elif distance > 20: 
            speed_factor = 0.3
        else: 
            speed_factor = 0.6
            
        move_x = int(diff_x * speed_factor)
        move_y = int(diff_y * speed_factor)
        
        # 限制单次最大步长，防止移动过于突兀
        max_step = 15
        move_x = max(-max_step, min(max_step, move_x))
        move_y = max(-max_step, min(max_step, move_y))
        
        # 确保在微小位移时不会因取整导致停滞
        if move_x == 0 and abs(diff_x) > 0: move_x = 1 if diff_x > 0 else -1
        if move_y == 0 and abs(diff_y) > 0: move_y = 1 if diff_y > 0 else -1
        
        # 下发相对位移指令至硬件端
        controller.send_move(move_x, move_y)
        time.sleep(0.015) 
        loop_count += 1
        
    # 最终坐标微调，确保精准落点
    cur_x, cur_y = get_current_mouse_pos()
    final_dx = target_x - cur_x
    final_dy = target_y - cur_y
    if abs(final_dx) > 0 or abs(final_dy) > 0:
        controller.send_move(final_dx, final_dy)
